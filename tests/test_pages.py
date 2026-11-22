import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firmware"))
import pages as P


class PagesTest(unittest.TestCase):
    def test_esc(self):
        self.assertEqual(P.esc("<a href=\"x\">'&"), "&lt;a href=&quot;x&quot;&gt;&#39;&amp;")

    def test_ascii_text(self):
        self.assertEqual(P.ascii_text("Médicament très long"), "Medicament tres ")
        self.assertEqual(P.ascii_text("Été"), "Ete")
        self.assertLessEqual(len(P.ascii_text("x" * 50)), 16)
        self.assertEqual(P.ascii_text("日本"), "??")

    def test_viewport_et_utf8(self):
        html = P.info_page("Aouine")
        self.assertIn("name='viewport'", html)
        self.assertIn("charset='utf-8'", html)

    def test_info_contient_adresse_ssid_version(self):
        html = P.info_page("Aouine")
        for texte in ("Aouine", "192.168.4.1", P.VERSION):
            self.assertIn(texte, html)

    def test_fiche_trie_par_compartiment(self):
        meds = [{"name": "B", "dose": "", "color": "vert", "slot": 2},
                {"name": "A", "dose": "", "color": "bleu", "slot": 1}]
        doses = [{"slot": 1, "time": "20:00"}, {"slot": 1, "time": "08:00"}]
        html = P.fiche_page(meds, doses)
        self.assertLess(html.index("<b>A</b>"), html.index("<b>B</b>"))
        self.assertIn("08:00, 20:00", html)
        self.assertIn("@media print", html)

    def test_formulaire_contient_csrf(self):
        self.assertIn("name='csrf' value='tok'", P.form("tok", "/x", ""))

    def test_fmt_delta(self):
        self.assertEqual(P.fmt_delta(0), "maintenant")
        self.assertEqual(P.fmt_delta(15), "dans 15 min")
        self.assertEqual(P.fmt_delta(125), "dans 2 h 05")

    def test_accueil_etats(self):
        med = {"name": "Doliprane", "dose": "500mg", "color": "bleu", "slot": 1}
        self.assertIn("Ajoutez votre premier médicament", P.home_page([], [], csrf="t"))
        self.assertIn("Aucun horaire", P.home_page([med], [], csrf="t"))
        html = P.home_page([med], [], "", "t", (125, "12:30", med, False), "Bonjour", [("12:30", med, False)])
        self.assertIn("Prochaine prise", html)
        self.assertIn("data-m='125'", html)
        self.assertIn("dans 2 h 05", html)

    def test_demain_et_prises_passees(self):
        med = {"name": "A", "dose": "", "color": "bleu", "slot": 1}
        html = P.home_page([med], [], "", "t", (620, "08:00", med, True), "Bonsoir", [("08:00", med, True)])
        self.assertIn("demain", html)
        self.assertIn("class='r p'", html)          # prise passee estompee

    def test_compartiments_rouges_et_numerotes(self):
        html = P.meds_page([], "t")
        self.assertIn("<details class='c' open>", html)   # ouvert quand il n'y a encore aucun medicament
        self.assertNotIn("name='color'", html)               # plus de choix de couleur
        self.assertEqual(html.count("name='slot'"), P.WEB_SLOTS)
        for i in range(1, P.WEB_SLOTS + 1):
            self.assertIn("<span>Compartiment %d</span>" % i, html)
        med = {"name": "A", "dose": "", "color": "bleu", "slot": 2}   # ancienne donnee : s'affiche quand meme en rouge
        html = P.meds_page([med], "t")
        self.assertIn("Compartiment 2", html)
        self.assertIn(P.RED, html)
        self.assertNotIn("#1e88e5", html)

    def test_arabe_rtl_et_numeros(self):
        med = {"name": "A", "dose": "", "color": "rouge", "slot": 3}
        try:
            P.set_context("ar", "/meds")
            html = P.meds_page([med], "t")
            self.assertIn("dir='rtl'", html)
            self.assertIn("lang='ar'", html)
            self.assertIn("الحجرة 3", html)
            self.assertIn("الأدوية", html)
            self.assertEqual(P.fmt_delta(125), "خلال 2 س 05")
            self.assertEqual(P.fmt_delta(0), "الآن")
        finally:
            P.set_context("fr")
        self.assertIn("dir='ltr'", P.meds_page([med], "t"))

    def test_selecteur_de_langue(self):
        html = P.info_page("A")
        self.assertIn("/lang?l=fr", html)
        self.assertIn("/lang?l=ar", html)

    def test_chaque_texte_francais_a_une_traduction(self):
        """Toutes les pages, en arabe, ne doivent plus contenir de phrase francaise connue."""
        med = {"name": "A", "dose": "", "color": "rouge", "slot": 1}
        try:
            P.set_context("ar", "/")
            pages = [P.login_page(True), P.login_page(False, "Mot de passe incorrect."),
                     P.home_page([med], ["Deverrouillage urgence"], "", "t", (5, "08:00", med, True), "Bonsoir",
                                 [("08:00", med, False)]),
                     P.home_page([], [], csrf="t"), P.home_page([med], [], csrf="t"),
                     P.meds_page([med], "t", "", [], True), P.doses_page(med, ["08:00"], "t"),
                     P.options_page({}, "t"), P.heure_page("t", "", "10:00"), P.password_page("t"),
                     P.info_page("A"), P.fiche_page([med], [])]
            for html in pages:
                for fr in ("Médicament", "Compartiment", "Retour", "Supprimer", "Ajouter", "Horaires",
                           "Accueil", "Enregistrer", "Prototype", "Valider", "Alarme"):
                    self.assertNotIn(fr, html)
        finally:
            P.set_context("fr")

    def test_navigation_active(self):
        self.assertIn("<a href='/meds' class='on'>", P.meds_page([], "t"))

    def test_aucune_ressource_externe(self):
        meds = [{"name": "A", "dose": "1", "color": "bleu", "slot": 1}]
        pages = [P.login_page(True), P.login_page(False), P.home_page(meds, ["e"], "x", "t"),
                 P.meds_page(meds, "t"), P.doses_page(meds[0], ["08:00"], "t"),
                 P.options_page({}, "t"), P.heure_page("t"), P.password_page("t"),
                 P.info_page("A"), P.fiche_page(meds, [])]
        for html in pages:
            for banni in ("http://", "https://", "src=", "<link", "@import"):
                self.assertNotIn(banni, html)


if __name__ == "__main__":
    unittest.main()
