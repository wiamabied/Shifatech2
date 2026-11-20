import os, sys, tempfile, time, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firmware"))
from store import Store
from web import App, unquote, parse_qs
import config


def cookie_of(resp):
    for k, v in resp[3]:
        if k == "Set-Cookie":
            return {"cookie": v.split(";")[0]}
    raise AssertionError("pas de cookie")


class WebTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.clock = []
        self.app = App(Store(self.d + "/s.json"), self.d + "/a.json", clock_setter=self.clock.append)

    def login(self):
        r = self.app.handle("POST", "/setup", {}, b"pwd=secret1&pwd2=secret1")
        self.assertEqual(r[0], 303)
        return cookie_of(r)

    def post(self, h, path, **kw):
        body = "&".join("%s=%s" % (k, v) for k, v in dict(csrf=self.app.csrf, **kw).items())
        return self.app.handle("POST", path, h, body.encode())

    def add_med(self, h, name="Doliprane", slot=1):
        return self.post(h, "/meds", name=name, dose="500mg", color="bleu", slot=slot)

    # --- acces et securite ---
    def test_premier_demarrage_redirige_vers_setup(self):
        r = self.app.handle("GET", "/", {}, b"")
        self.assertEqual((r[0], r[3][0][1]), (303, "/setup"))

    def test_mot_de_passe_trop_court(self):
        r = self.app.handle("POST", "/setup", {}, b"pwd=abc&pwd2=abc")
        self.assertEqual(r[0], 200)
        self.assertIsNone(self.app.auth)

    def test_mot_de_passe_hache_et_sale(self):
        self.login()
        with open(self.d + "/a.json") as f:
            raw = f.read()
        self.assertNotIn("secret1", raw)
        self.assertIn("salt", raw)

    def test_non_connecte_redirige_vers_login(self):
        self.login()
        r = self.app.handle("GET", "/meds", {}, b"")
        self.assertEqual((r[0], r[3][0][1]), (303, "/login"))

    def test_csrf_obligatoire(self):
        h = self.login()
        r = self.app.handle("POST", "/meds", h, b"name=A&slot=1&color=bleu")
        self.assertEqual(r[0], 403)
        self.assertEqual(self.app.s.data["meds"], [])

    def test_blocage_apres_5_essais(self):
        self.login()
        for _ in range(config.MAX_FAILS):
            self.app.handle("POST", "/login", {}, b"pwd=faux")
        r = self.app.handle("POST", "/login", {}, b"pwd=secret1")      # bon mot de passe mais bloque
        self.assertEqual(r[0], 200)
        self.assertIn("Trop d", r[2])
        self.app.locked_until = 0
        self.assertEqual(self.app.handle("POST", "/login", {}, b"pwd=secret1")[0], 303)

    def test_plusieurs_telephones_en_meme_temps(self):
        h1 = self.login()
        h2 = cookie_of(self.app.handle("POST", "/login", {}, b"pwd=secret1"))
        for h in (h1, h2):                                              # les deux restent connectes
            self.assertEqual(self.app.handle("GET", "/", h, b"")[0], 200)
        csrf1 = next(c for s, c in self.app.sessions if s in h1["cookie"])
        r = self.app.handle("POST", "/meds", h1, ("csrf=%s&name=A&color=bleu&slot=1" % csrf1).encode())
        self.assertIn("ok=1", r[3][0][1])                               # chaque telephone a son propre jeton
        self.app.handle("GET", "/logout", h2, b"")                      # la deconnexion de l'un ne touche pas l'autre
        self.assertEqual(self.app.handle("GET", "/", h1, b"")[0], 200)
        self.assertEqual(self.app.handle("GET", "/", h2, b"")[0], 303)

    def test_au_plus_3_telephones(self):
        hs = [self.login()] + [cookie_of(self.app.handle("POST", "/login", {}, b"pwd=secret1")) for _ in range(3)]
        self.assertEqual(self.app.handle("GET", "/", hs[0], b"")[0], 303)   # le plus ancien est deconnecte
        for h in hs[1:]:
            self.assertEqual(self.app.handle("GET", "/", h, b"")[0], 200)

    def test_changement_mot_de_passe_deconnecte_les_autres(self):
        h1 = self.login()
        h2 = cookie_of(self.app.handle("POST", "/login", {}, b"pwd=secret1"))
        self.app.handle("GET", "/", h2, b"")                            # selectionne la session 2
        self.post(h2, "/password", old="secret1", new="nouveau1", new2="nouveau1")
        self.assertEqual(self.app.handle("GET", "/", h1, b"")[0], 303)
        self.assertEqual(self.app.handle("GET", "/", h2, b"")[0], 200)

    def test_changement_mot_de_passe(self):
        h = self.login()
        self.post(h, "/password", old="secret1", new="nouveau1", new2="nouveau1")
        self.assertEqual(self.app.handle("POST", "/login", {}, b"pwd=nouveau1")[0], 303)

    def test_changement_mot_de_passe_refuse(self):
        h = self.login()
        r = self.post(h, "/password", old="faux", new="nouveau1", new2="nouveau1")
        self.assertIn("err=1", r[3][0][1])

    # --- medicaments et horaires ---
    def test_ajout_medicament_incremente_la_version(self):
        h = self.login()
        v = self.app.s.data["version"]
        self.assertIn("ok=1", self.add_med(h)[3][0][1])
        self.assertEqual(self.app.s.data["version"], v + 1)
        self.assertEqual(Store(self.d + "/s.json").data["meds"][0]["name"], "Doliprane")  # ecrit en flash

    def test_compartiment_deja_pris_refuse(self):
        h = self.login()
        self.add_med(h)
        self.assertIn("err=1", self.add_med(h, "Autre", 1)[3][0][1])
        self.assertEqual(len(self.app.s.data["meds"]), 1)

    def test_compartiment_hors_limites(self):
        h = self.login()
        self.assertIn("err=1", self.add_med(h, slot=config.WEB_SLOTS + 1)[3][0][1])

    def test_pas_de_flash_si_rien_ne_change(self):
        h = self.login()
        self.add_med(h)
        v = self.app.s.data["version"]
        self.add_med(h, "X", 1)                        # refuse
        self.assertEqual(self.app.s.data["version"], v)

    def test_horaires_max_et_doublons(self):
        h = self.login()
        self.add_med(h)
        for i in range(config.MAX_DOSES_PER_MED):
            self.assertIn("ok=1", self.post(h, "/doses", slot=1, time="0%d%%3A00" % i)[3][0][1])
        self.assertIn("err=1", self.post(h, "/doses", slot=1, time="09%3A00")[3][0][1])   # trop de prises
        self.assertIn("err=1", self.post(h, "/doses", slot=1, time="00%3A00")[3][0][1])   # doublon

    def test_horaire_invalide(self):
        h = self.login()
        self.add_med(h)
        self.assertIn("err=1", self.post(h, "/doses", slot=1, time="25%3A99")[3][0][1])

    def test_suppression_medicament_supprime_ses_prises(self):
        h = self.login()
        self.add_med(h)
        self.post(h, "/doses", slot=1, time="08%3A00")
        self.post(h, "/meds/del", slot=1)
        self.assertEqual((self.app.s.data["meds"], self.app.s.data["doses"]), ([], []))

    def test_historique_limite_a_40(self):
        h = self.login()
        for i in range(60):
            self.app.s.log("e%d" % i)
        self.assertEqual(len(self.app.s.data["history"]), config.HISTORY_MAX)

    # --- options, heure, urgence ---
    def test_options_ecran_ascii_16(self):
        h = self.login()
        self.post(h, "/options", alarm="fort", brightness=7, lcd_msg="Médicament très long")
        o = self.app.s.data["options"]
        self.assertEqual((o["alarm"], o["brightness"], o["lcd_msg"]), ("fort", 7, "Medicament tres "))

    def test_options_invalides(self):
        h = self.login()
        self.assertIn("err=1", self.post(h, "/options", alarm="x", brightness=5, lcd_msg="")[3][0][1])
        self.assertIn("err=1", self.post(h, "/options", alarm="doux", brightness=99, lcd_msg="")[3][0][1])

    def test_reglage_heure(self):
        h = self.login()
        self.post(h, "/heure", epoch=1790000000)
        self.assertEqual(self.clock, [1790000000])

    def test_deverrouillage_urgence_affiche_heure_de_fin(self):
        h = self.login()
        self.post(h, "/unlock")
        r = self.app.handle("GET", "/", h, b"")
        self.assertRegex(r[2], r"Déverrouillé jusqu&#39;à \d\d:\d\d")

    def test_xss_echappe(self):
        h = self.login()
        self.post(h, "/meds", name="%3Cscript%3Ealert(1)%3C%2Fscript%3E", dose="", color="bleu", slot=1)
        r = self.app.handle("GET", "/meds", h, b"")
        self.assertNotIn("<script>alert", r[2])
        self.assertIn("&lt;script&gt;", r[2])

    def test_toutes_les_pages_ont_la_mention_legale_et_restent_hors_ligne(self):
        h = self.login()
        self.add_med(h)
        self.post(h, "/doses", slot=1, time="08%3A00")
        for path in ("/", "/meds", "/doses?edit=1", "/options", "/heure", "/password", "/info", "/fiche"):
            r = self.app.handle("GET", path, h, b"")
            self.assertEqual(r[0], 200, path)
            self.assertIn("pas un dispositif médical", r[2], path)
            self.assertNotIn("http://", r[2], path)
            self.assertNotIn("https://", r[2], path)

    def test_pire_cas_sous_12_ko(self):
        h = self.login()
        for slot in range(1, config.WEB_SLOTS + 1):
            self.add_med(h, "Medicament %d" % slot, slot)
            for i in range(config.MAX_DOSES_PER_MED):
                self.post(h, "/doses", slot=slot, time="%02d%%3A00" % (slot + i))
        for i in range(60):
            self.app.s.log("Evenement numero %d" % i)
        for path in ("/", "/meds", "/doses?edit=1", "/fiche", "/options"):
            r = self.app.handle("GET", path, h, b"")
            self.assertLess(len(r[2].encode()), 12000, path)

    def test_prochaine_prise(self):
        from web import today_items, next_dose
        meds = [{"name": "A", "dose": "", "color": "bleu", "slot": 1}]
        doses = [{"slot": 1, "time": "08:00"}, {"slot": 1, "time": "12:30"}]
        items = today_items(meds, doses, 600)                         # il est 10:00
        self.assertEqual([i[2] for i in items], [True, False])        # 08:00 est passee
        d, t, m, demain = next_dose(items, 600)
        self.assertEqual((d, t, demain), (150, "12:30", False))
        d, t, m, demain = next_dose(today_items(meds, doses, 1300), 1300)   # il est 21:40
        self.assertEqual((t, demain), ("08:00", True))
        self.assertIsNone(next_dose([], 600))

    def test_accueil_affiche_la_prochaine_prise(self):
        h = self.login()
        self.add_med(h)
        self.post(h, "/doses", slot=1, time="08%3A00")
        r = self.app.handle("GET", "/", h, b"")
        self.assertIn("Prochaine prise", r[2])
        self.assertIn("Doliprane", r[2])

    def test_page_inconnue(self):
        h = self.login()
        self.assertEqual(self.app.handle("GET", "/nimporte", h, b"")[0], 404)

    def test_decodage_formulaire(self):
        self.assertEqual(unquote("caf%C3%A9+noir"), "café noir")
        self.assertEqual(parse_qs("a=1&b=x%26y"), {"a": "1", "b": "x&y"})


if __name__ == "__main__":
    unittest.main()
