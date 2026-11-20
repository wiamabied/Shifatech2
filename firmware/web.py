# Serveur et regles. Ne connait pas les sockets : handle() recoit une requete et renvoie une reponse.
# Le meme code tourne sur PC (tools/demo_pc.py) et sur le Pico W (main.py).
import hashlib, os, json, time
from binascii import hexlify
from config import (WEB_SLOTS, MAX_DOSES_PER_MED, MAX_FAILS, LOCK_SECONDS, UNLOCK_SECONDS,
                    HISTORY_MAX, WIFI_SSID, COLORS, ALARMS, MAX_SESSIONS)
import pages as P


def unquote(s):
    parts = s.replace("+", " ").split("%")
    out = bytearray(parts[0].encode())
    for p in parts[1:]:
        try:
            out.append(int(p[:2], 16))
            out.extend(p[2:].encode())
        except ValueError:
            out.extend(b"%" + p.encode())
    try:
        return out.decode()
    except UnicodeError:
        return ""


def parse_qs(s):
    d = {}
    for pair in s.split("&"):
        if pair:
            k, _, v = pair.partition("=")
            d[unquote(k)] = unquote(v)
    return d


def html(body, status=200, extra=()):
    return (status, "text/html; charset=utf-8", body, tuple(extra))


def redirect(to, extra=()):
    return (303, "text/plain", "", (("Location", to),) + tuple(extra))


def _hash(salt, pwd):
    return hexlify(hashlib.sha256(salt + pwd.encode()).digest()).decode()


def valid_time(t):
    return (len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit()
            and int(t[:2]) < 24 and int(t[3:]) < 60)


def _minutes(t):
    return int(t[:2]) * 60 + int(t[3:])


def now_minutes():
    t = time.localtime()
    return t[3] * 60 + t[4]


def hello():
    h = time.localtime()[3]
    return "Bonjour" if h < 12 else ("Bon après-midi" if h < 18 else "Bonsoir")


def today_items(meds, doses, now_min):
    """Prises du jour triees par heure : (heure, medicament, deja_passee)."""
    by = {m["slot"]: m for m in meds}
    out = []
    for d in sorted(doses, key=lambda d: d["time"]):
        m = by.get(d["slot"])
        if m:
            out.append((d["time"], m, _minutes(d["time"]) < now_min))
    return out


def next_dose(items, now_min):
    """Prochaine prise : (minutes_restantes, heure, medicament, c_est_demain) ou None."""
    best = None
    for t, m, past in items:
        delta = (_minutes(t) - now_min) % 1440
        if best is None or delta < best[0]:
            best = (delta, t, m, past)
    return best


class App:
    def __init__(self, store, auth_path="auth.json", clock_setter=None):
        self.s = store
        self.auth_path = auth_path
        self.clock_setter = clock_setter   # fonction(epoch) qui regle le DS3231 (fournie par le boitier)
        self.sessions = []                 # [(sid, csrf)] : plusieurs telephones possibles
        self.csrf = self._cur = None       # session de la requete en cours
        self.fails, self.locked_until = 0, 0
        self.unlock_until = 0
        try:
            with open(auth_path) as f:
                self.auth = json.load(f)
        except (OSError, ValueError):
            self.auth = None

    # ---- mot de passe et session ----
    def _set_password(self, pwd):
        salt = hexlify(os.urandom(8)).decode()
        self.auth = {"salt": salt, "hash": _hash(salt.encode(), pwd)}
        with open(self.auth_path, "w") as f:
            json.dump(self.auth, f)

    def _new_session(self):
        sid = hexlify(os.urandom(12)).decode()
        self.csrf = hexlify(os.urandom(8)).decode()
        self._cur = sid
        self.sessions.append((sid, self.csrf))
        del self.sessions[:-MAX_SESSIONS]
        return (("Set-Cookie", "sid=%s; HttpOnly; Path=/; SameSite=Strict" % sid),)

    def _check(self, pwd):
        return _hash(self.auth["salt"].encode(), pwd) == self.auth["hash"]

    # ---- point d'entree ----
    def handle(self, method, target, headers, body):
        path, _, qs = target.partition("?")
        if path == "/favicon.ico":                              # le navigateur le demande tout seul
            return (204, "text/plain", "", ())
        q = parse_qs(qs)
        form = parse_qs(body.decode("utf-8", "ignore")) if method == "POST" else {}

        if self.auth is None:                                   # premier demarrage
            if path != "/setup":
                return redirect("/setup")
            if method == "POST":
                p, p2 = form.get("pwd", ""), form.get("pwd2", "")
                if len(p) < 6 or p != p2:
                    return html(P.login_page(True, "Mots de passe différents ou trop courts (6 minimum)."))
                self._set_password(p)
                return redirect("/", self._new_session())
            return html(P.login_page(True))

        if path == "/login":
            if method == "POST":
                if time.time() < self.locked_until:
                    return html(P.login_page(False, "Trop d'essais ratés. Réessayez dans quelques minutes."))
                if self._check(form.get("pwd", "")):
                    self.fails = 0
                    return redirect("/", self._new_session())
                self.fails += 1
                if self.fails >= MAX_FAILS:
                    self.locked_until, self.fails = time.time() + LOCK_SECONDS, 0
                return html(P.login_page(False, "Mot de passe incorrect."))
            return html(P.login_page(False))

        cookie = headers.get("cookie", "")
        for sid, csrf in self.sessions:
            if "sid=" + sid in cookie:
                self._cur, self.csrf = sid, csrf
                break
        else:
            return redirect("/login")                           # pas connecte

        if method == "POST" and form.get("csrf") != self.csrf:
            return html(P.page("Erreur", "<p>Formulaire expiré. <a href='/'>Retour</a></p>"), 403)

        return self._route(method, path, q, form)

    # ---- routes ----
    def _route(self, method, path, q, form):
        s = self.s.data
        csrf = self.csrf
        post = method == "POST"
        bar = P.msgbar("ok" in q, "err" in q)

        if path == "/":
            nm = now_minutes()
            items = today_items(s["meds"], s["doses"], nm)
            return html(P.home_page(s["meds"], s["history"], self._unlock_text(), csrf,
                                    next_dose(items, nm), hello(), items))
        if path == "/unlock" and post:
            self.unlock_until = time.time() + UNLOCK_SECONDS
            self.s.log("Deverrouillage urgence")
            self.s.commit()
            return redirect("/")
        if path == "/meds":
            return self._add_med(form) if post else html(
                P.meds_page(s["meds"], csrf, bar, s["doses"], "err" in q))
        if path == "/meds/del" and post:
            slot = form.get("slot", "")
            s["meds"] = [m for m in s["meds"] if str(m["slot"]) != slot]
            s["doses"] = [d for d in s["doses"] if str(d["slot"]) != slot]
            self.s.log("Medicament supprime")
            self.s.commit()
            return redirect("/meds?ok=1")
        if path == "/doses":
            return self._doses(post, q, form, bar)
        if path == "/doses/del" and post:
            slot, t = form.get("slot", ""), form.get("time", "")
            s["doses"] = [d for d in s["doses"] if not (str(d["slot"]) == slot and d["time"] == t)]
            self.s.commit()
            return redirect("/doses?edit=" + P.esc(slot) + "&ok=1")
        if path == "/options":
            return self._options(post, form, bar)
        if path == "/heure":
            return self._heure(post, form, bar)
        if path == "/password":
            return self._password(post, form, bar)
        if path == "/info":
            return html(P.info_page(WIFI_SSID))
        if path == "/fiche":
            return html(P.fiche_page(s["meds"], s["doses"]))
        if path == "/logout":
            self.sessions = [x for x in self.sessions if x[0] != self._cur]
            return redirect("/login")
        return html(P.page("Page introuvable", "<p><a href='/'>Retour</a></p>"), 404)

    def _unlock_text(self):
        if self.unlock_until > time.time():
            t = time.localtime(self.unlock_until)
            return "Déverrouillé jusqu'à %02d:%02d" % (t[3], t[4])
        return ""

    def _add_med(self, f):
        try:
            slot = int(f.get("slot", "0"))
        except ValueError:
            slot = 0
        name = f.get("name", "").strip()[:30]
        meds = self.s.data["meds"]
        color = f.get("color", "")
        if (not name or not 1 <= slot <= WEB_SLOTS or color not in COLORS
                or any(m["slot"] == slot for m in meds)):
            return redirect("/meds?err=1")
        meds.append({"name": name, "dose": f.get("dose", "").strip()[:20], "color": color, "slot": slot})
        self.s.log("Ajout " + P.ascii_text(name))
        self.s.commit()
        return redirect("/meds?ok=1")

    def _doses(self, post, q, form, bar):
        s = self.s.data
        slot = form.get("slot") if post else q.get("edit", "")
        med = next((m for m in s["meds"] if str(m["slot"]) == slot), None)
        if med is None:
            return redirect("/meds?err=1")
        times = [d["time"] for d in s["doses"] if d["slot"] == med["slot"]]
        if post:
            t = form.get("time", "")
            if not valid_time(t) or t in times or len(times) >= MAX_DOSES_PER_MED:
                return redirect("/doses?edit=%s&err=1" % slot)
            s["doses"].append({"slot": med["slot"], "time": t})
            self.s.commit()
            return redirect("/doses?edit=%s&ok=1" % slot)
        return html(P.doses_page(med, times, self.csrf, bar))

    def _options(self, post, form, bar):
        o = self.s.data["options"]
        if post:
            try:
                b = int(form.get("brightness", "5"))
            except ValueError:
                return redirect("/options?err=1")
            if form.get("alarm") not in ALARMS or not 1 <= b <= 10:
                return redirect("/options?err=1")
            o["alarm"], o["brightness"] = form["alarm"], b
            o["lcd_msg"] = P.ascii_text(form.get("lcd_msg", "").strip())
            self.s.commit()
            return redirect("/options?ok=1")
        return html(P.options_page(o, self.csrf, bar))

    def _heure(self, post, form, bar):
        if post:
            try:
                epoch = int(form.get("epoch", ""))
            except ValueError:
                return redirect("/heure?err=1")
            if self.clock_setter:
                self.clock_setter(epoch)
            self.s.log("Heure reglee")
            self.s.commit()
            return redirect("/heure?ok=1")
        t = time.localtime()
        return html(P.heure_page(self.csrf, bar, "%02d:%02d" % (t[3], t[4])))

    def _password(self, post, form, bar):
        if post:
            new = form.get("new", "")
            if not self._check(form.get("old", "")) or len(new) < 6 or new != form.get("new2"):
                return redirect("/password?err=1")
            self._set_password(new)
            self.sessions = [x for x in self.sessions if x[0] == self._cur]   # deconnecte les autres telephones
            return redirect("/password?ok=1")
        return html(P.password_page(self.csrf, bar))
