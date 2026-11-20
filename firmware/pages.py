# Pages HTML. Tout est en ligne : aucun fichier, police ou script externe.
# Design : mobile d'abord, cartes, barre de navigation en bas, mode sombre automatique.
from config import VERSION, WEB_SLOTS, COLORS, ALARMS, MAX_DOSES_PER_MED


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


_MAP = {"é": "e", "è": "e", "ê": "e", "ë": "e", "à": "a", "â": "a",
        "î": "i", "ï": "i", "ô": "o", "ù": "u", "û": "u", "ç": "c"}


def ascii_text(s, n=16):
    """Texte pour l'ecran du boitier : ASCII, sans accent, 16 caracteres maximum."""
    s = "".join((_MAP[c.lower()].upper() if c.isupper() else _MAP[c.lower()]) if c.lower() in _MAP else c
                for c in s)
    return "".join(c if 32 <= ord(c) < 127 else "?" for c in s)[:n]


COLOR_HEX = {"rouge": "#e53935", "vert": "#43a047", "bleu": "#1e88e5",
             "jaune": "#fdd835", "blanc": "#f5f5f5", "violet": "#8e24aa"}
ALARM_ICON = {"doux": "🔈", "normal": "🔉", "fort": "🔊"}

CSS = (
    ":root{--bg:#f1f5f9;--c:#fff;--t:#0f172a;--m:#64748b;--p:#2563eb;--ok:#16a34a;--er:#dc2626;--b:#e2e8f0}"
    "@media(prefers-color-scheme:dark){:root{--bg:#0b1220;--c:#162033;--t:#e8eefc;--m:#94a3b8;--p:#3b82f6;--b:#26354f}}"
    "*{box-sizing:border-box}"
    "body{margin:0;background:var(--bg);color:var(--t);font:18px/1.45 system-ui,sans-serif;padding:0 14px 96px}"
    "main{max-width:560px;margin:0 auto}header{padding:22px 2px 2px}h1{margin:0;font-size:27px}"
    "h2{font-size:14px;color:var(--m);text-transform:uppercase;letter-spacing:.06em;margin:24px 4px 8px}"
    ".c{background:var(--c);border-radius:18px;padding:16px;margin:12px 0;box-shadow:0 2px 10px #0000001a;"
    "animation:f .35s ease both}@keyframes f{from{opacity:0;transform:translateY(10px)}}"
    ".b{display:block;width:100%;min-height:52px;border:0;border-radius:14px;background:var(--p);color:#fff;"
    "font:600 18px system-ui,sans-serif;text-align:center;text-decoration:none;padding:14px;margin:10px 0;"
    "cursor:pointer;transition:transform .1s}.b:active{transform:scale(.97)}.b:disabled{opacity:.6}"
    ".s{background:transparent;color:var(--p);border:2px solid var(--p)}.d{background:var(--er);color:#fff;border:0}"
    ".sm{min-height:44px;padding:8px;font-size:16px}"
    "label{display:block;font-size:15px;color:var(--m);margin:14px 0 4px}"
    "input,select{width:100%;min-height:50px;font:inherit;color:var(--t);background:var(--bg);"
    "border:2px solid var(--b);border-radius:12px;padding:8px 12px}"
    "input:focus,select:focus{outline:0;border-color:var(--p)}"
    "small{color:var(--m);font-size:14px}.er{color:var(--er);font-weight:600}.ok{color:var(--ok);font-weight:600}"
    ".o{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:10px;"
    "border:1px solid #0003;flex:none}.O{width:44px;height:44px}"
    ".r{display:flex;align-items:center;padding:10px 0;border-top:1px solid var(--b)}.r:first-child{border:0}"
    ".r>div{flex:1}.p{opacity:.45}.two{display:flex;gap:10px}.two>*{flex:1}"
    ".h{display:inline-flex;align-items:center;background:var(--bg);border-radius:20px;padding:4px 12px;"
    "margin:3px 6px 3px 0;font-weight:600}.h form{display:inline;margin-left:4px}"
    ".h button{border:0;background:none;color:var(--er);font-size:18px;min-width:36px;min-height:36px;cursor:pointer}"
    ".sw,.pl{position:relative;display:inline-block;margin:4px}"
    ".sw input,.pl input{position:absolute;opacity:0;width:1px;min-height:0;height:1px}"
    ".sw i{display:block;width:46px;height:46px;border-radius:50%;border:1px solid #0003;transition:transform .15s}"
    ".sw input:checked+i{outline:3px solid var(--p);outline-offset:3px;transform:scale(1.1)}"
    ".pl span{display:block;min-width:54px;padding:12px 8px;text-align:center;border:2px solid var(--b);"
    "border-radius:12px;font-weight:600}.pl input:checked+span{background:var(--p);color:#fff;border-color:var(--p)}"
    ".g{display:flex;gap:8px}.g .pl{flex:1;margin:0}"
    ".pg{display:grid;grid-template-columns:repeat(auto-fit,minmax(46px,1fr));gap:8px}.pg .pl{margin:0}"
    ".pg span{min-width:0}"
    ".n{background:linear-gradient(135deg,var(--p),#7c3aed);color:#fff}.n small{color:#ffffffd9}"
    ".tm{font-size:46px;font-weight:700;line-height:1.1}.lg{font-size:56px;text-align:center}"
    "details summary{list-style:none;font-weight:600;color:var(--p);min-height:44px;display:flex;"
    "align-items:center;cursor:pointer}summary::-webkit-details-marker{display:none}"
    ".t{position:fixed;top:12px;left:12px;right:12px;max-width:536px;margin:0 auto;padding:14px;"
    "border-radius:14px;color:#fff;background:var(--ok);font-weight:600;z-index:9;box-shadow:0 4px 14px #0004;"
    "animation:o 4s forwards}.t.e{background:var(--er)}@keyframes o{0%,80%{opacity:1}100%{opacity:0;visibility:hidden}}"
    "nav{position:fixed;left:0;right:0;bottom:0;display:flex;background:var(--c);border-top:1px solid var(--b);"
    "padding-bottom:env(safe-area-inset-bottom)}"
    "nav a{flex:1;text-align:center;padding:8px 0 6px;font-size:12px;color:var(--m);text-decoration:none}"
    "nav b{display:block;font-size:24px}nav .on{color:var(--p);font-weight:700}"
    "table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid var(--b);padding:8px;text-align:left}"
    "footer{font-size:12px;color:var(--m);text-align:center;margin:28px 8px}"
    "@media print{.np{display:none}body{background:#fff;color:#000;padding:0}.c{box-shadow:none}}"
)

# Script commun : evite le double envoi d'un formulaire et recharge la page apres un retour arriere.
JS = ("document.addEventListener('submit',function(e){if(e.defaultPrevented)return;"
      "var b=e.target.querySelector('button');if(b){b.disabled=true;b.textContent='…'}});"
      "addEventListener('pageshow',function(e){if(e.persisted)location.reload()});")

LEGAL = "Prototype d'aide à l'observance, pas un dispositif médical, aucun conseil médical."

NAV = (("/", "🏠", "Accueil"), ("/meds", "💊", "Médicaments"),
       ("/options", "⚙️", "Options"), ("/info", "ℹ️", "Infos"))


def page(title, body, nav=True, active="", js=""):
    n = ""
    if nav:
        n = "<nav class='np'>" + "".join(
            "<a href='%s'%s><b>%s</b>%s</a>" % (u, " class='on'" if u == active else "", i, l)
            for u, i, l in NAV) + "</nav>"
    return ("<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<meta name='theme-color' content='#2563eb'>"
            "<title>" + esc(title) + "</title><style>" + CSS + "</style></head><body><main>"
            "<header><h1>" + esc(title) + "</h1></header>" + body +
            "<footer>" + LEGAL + "</footer></main>" + n + "<script>" + JS + js + "</script></body></html>")


def form(csrf, action, inner, btn="Enregistrer", confirm=None, danger=False, cls=""):
    on = (" onsubmit=\"return confirm('" + esc(confirm) + "')\"") if confirm else ""
    c = "b" + (" d" if danger else "") + ((" " + cls) if cls else "")
    return ("<form method='post' action='" + action + "'" + on + ">"
            "<input type='hidden' name='csrf' value='" + esc(csrf) + "'>"
            + inner + "<button class='" + c + "'>" + btn + "</button></form>")


def msgbar(ok=False, err=False, text=""):
    """Petit message qui apparait puis disparait tout seul (animation CSS, sans script)."""
    if ok:
        return "<div class='t'>✓ " + (esc(text) or "Enregistré") + "</div>"
    if err:
        return "<div class='t e'>⚠ " + (esc(text) or "Vérifiez les champs et réessayez") + "</div>"
    return ""


def dot(color, big=False):
    return "<i class='o%s' style='background:%s'></i>" % (" O" if big else "", COLOR_HEX.get(color, "#999"))


def fmt_delta(m):
    if m <= 0:
        return "maintenant"
    return "dans " + (("%d h %02d" % (m // 60, m % 60)) if m >= 60 else "%d min" % m)


# ---------- connexion ----------
def login_page(first, err=""):
    intro = ("<p>Choisissez un mot de passe pour protéger le pilulier (6 caractères minimum).</p>"
             if first else "<p>Entrez votre mot de passe pour continuer.</p>")
    e = "<p class='er'>" + esc(err) + "</p>" if err else ""
    return page("Bienvenue" if first else "Connexion",
                "<div class='c'><div class='lg'>💊</div>" + intro + e + "<form method='post'>"
                "<label>Mot de passe</label><input type='password' name='pwd' required autofocus>"
                + ("<label>Confirmer le mot de passe</label><input type='password' name='pwd2' required>"
                   if first else "") + "<button class='b'>Valider</button></form></div>", nav=False)


# ---------- accueil ----------
COUNTDOWN = ("var c=document.getElementById('cd');if(c){var m=+c.dataset.m,s=Date.now();function u(){"
             "var r=m-Math.floor((Date.now()-s)/60000);c.textContent=r<=0?'maintenant':'dans '+"
             "(r>=60?Math.floor(r/60)+' h '+('0'+r%60).slice(-2):r+' min')}u();setInterval(u,20000)}")


def home_page(meds, history, unlock_text="", csrf="", nxt=None, hello="Bonjour", today=()):
    body = ""
    if unlock_text:
        body += "<div class='c ok'>🔓 " + esc(unlock_text) + "</div>"
    if not meds:
        body += ("<div class='c'><p><b>Bienvenue !</b> Ajoutez votre premier médicament pour commencer.</p>"
                 "<a class='b' href='/meds'>➕ Ajouter un médicament</a></div>")
    elif nxt is None:
        body += ("<div class='c'><p>Aucun horaire n'est réglé pour l'instant.</p>"
                 "<a class='b' href='/meds'>🕐 Régler les horaires</a></div>")
    else:
        d, t, m, tom = nxt
        body += ("<div class='c n'><small>Prochaine prise</small><div class='tm'>%s</div>"
                 "<div><b>%s</b> %s</div><small>Compartiment %s · <span id='cd' data-m='%d'>%s</span>%s</small></div>"
                 % (esc(t), esc(m["name"]), esc(m["dose"]), m["slot"], d, fmt_delta(d),
                    " · demain" if tom else ""))
    if today:
        rows = "".join("<div class='r%s'>%s<div><b>%s</b> %s</div><small>C%s</small></div>"
                       % (" p" if past else "", dot(m["color"]), esc(t), esc(m["name"]), m["slot"])
                       for t, m, past in today[:12])
        more = ("<small>+%d autres prises : voir la fiche</small>" % (len(today) - 12)) if len(today) > 12 else ""
        body += "<h2>Aujourd'hui</h2><div class='c'>" + rows + more + "</div>"
    if history:
        body += ("<h2>Derniers événements</h2><div class='c'>"
                 + "".join("<div class='r'><small>%s</small></div>" % esc(h) for h in reversed(history[-5:]))
                 + "</div>")
    body += ("<h2>Outils</h2><a class='b s' href='/fiche'>🖨️ Fiche de remplissage</a>"
             "<a class='b s' href='/heure'>🕐 Régler l'heure</a><h2>Urgence</h2>"
             + form(csrf, "/unlock", "", "🔓 Déverrouillage d'urgence",
                    "Déverrouiller le boîtier pour quelques minutes ?", True))
    return page(hello + " 👋", body, active="/", js=COUNTDOWN)


# ---------- medicaments ----------
def meds_page(meds, csrf, msg="", doses=(), open_add=False):
    rows = ""
    for m in sorted(meds, key=lambda x: x["slot"]):
        times = sorted(d["time"] for d in doses if d["slot"] == m["slot"])
        chips = "".join("<span class='h'>%s</span>" % esc(t) for t in times) or "<small>Aucun horaire</small>"
        rows += ("<div class='c'><div class='r'>" + dot(m["color"], True)
                 + "<div><b>%s</b> %s<br><small>Compartiment %s</small></div></div><div>%s</div>"
                 % (esc(m["name"]), esc(m["dose"]), m["slot"], chips)
                 + "<div class='two'><a class='b s sm' href='/doses?edit=%s'>🕐 Horaires</a>" % m["slot"]
                 + form(csrf, "/meds/del", "<input type='hidden' name='slot' value='%s'>" % m["slot"],
                        "🗑️ Supprimer", "Supprimer ce médicament ?", True, "sm") + "</div></div>")
    used = [m["slot"] for m in meds]
    free = [i for i in range(1, WEB_SLOTS + 1) if i not in used]
    if free:
        colors = "".join("<label class='sw' title='%s'><input type='radio' name='color' value='%s'%s>"
                         "<i style='background:%s'></i></label>"
                         % (c, c, " checked" if k == 0 else "", COLOR_HEX.get(c, "#999"))
                         for k, c in enumerate(COLORS))
        slots = "".join("<label class='pl'><input type='radio' name='slot' value='%d'%s><span>%d</span></label>"
                        % (i, " checked" if k == 0 else "", i) for k, i in enumerate(free))
        add = ("<details class='c'%s><summary>➕ Ajouter un médicament</summary>"
               % (" open" if (open_add or not meds) else "")
               + form("%s" % csrf, "/meds",
                      "<label>Nom du médicament</label><input name='name' maxlength='30' required>"
                      "<label>Dose (par exemple : 1 comprimé)</label><input name='dose' maxlength='20'>"
                      "<label>Couleur de la lumière</label><div>" + colors + "</div>"
                      "<label>Compartiment</label><div class='pg'>" + slots + "</div>", "Ajouter") + "</details>")
    else:
        add = "<div class='c'>Tous les compartiments sont utilisés.</div>"
    return page("Médicaments", msg + rows + add, active="/meds")


def doses_page(med, times, csrf, msg=""):
    chips = ""
    for t in sorted(times):
        chips += ("<span class='h'>%s<form method='post' action='/doses/del' "
                  "onsubmit=\"return confirm('Supprimer cette prise ?')\">"
                  "<input type='hidden' name='csrf' value='%s'><input type='hidden' name='slot' value='%s'>"
                  "<input type='hidden' name='time' value='%s'><button aria-label='Supprimer'>✕</button>"
                  "</form></span>" % (esc(t), esc(csrf), med["slot"], esc(t)))
    chips = chips or "<small>Aucune prise pour l'instant.</small>"
    head = ("<div class='c'><div class='r'>" + dot(med["color"], True)
            + "<div><b>%s</b> %s<br><small>Compartiment %s</small></div></div><div>%s</div></div>"
            % (esc(med["name"]), esc(med["dose"]), med["slot"], chips))
    if len(times) < MAX_DOSES_PER_MED:
        add = ("<div class='c'>" + form(
            csrf, "/doses", "<input type='hidden' name='slot' value='%s'>"
            "<label>Nouvelle heure de prise</label><input type='time' name='time' required>" % med["slot"],
            "➕ Ajouter cette heure") + "</div>")
    else:
        add = "<div class='c'>Maximum de %d prises par jour atteint.</div>" % MAX_DOSES_PER_MED
    return page("Horaires", msg + head + add + "<a class='b s' href='/meds'>← Retour</a>", active="/meds")


# ---------- options, heure, mot de passe, infos, fiche ----------
def options_page(opts, csrf, msg=""):
    cur = opts.get("alarm", "normal")
    seg = "".join("<label class='pl'><input type='radio' name='alarm' value='%s'%s><span>%s<br>%s</span></label>"
                  % (a, " checked" if a == cur else "", ALARM_ICON.get(a, ""), a.capitalize()) for a in ALARMS)
    b = esc(opts.get("brightness", 5))
    return page("Options", msg + "<div class='c'>" + form(
        csrf, "/options",
        "<label>Alarme</label><div class='g'>" + seg + "</div>"
        "<label>Luminosité de l'écran : <b>" + b + "</b></label>"
        "<input type='range' name='brightness' min='1' max='10' value='" + b + "' "
        "oninput=\"this.previousElementSibling.lastElementChild.textContent=this.value\">"
        "<label>Message sur l'écran du boîtier (16 lettres, sans accent)</label>"
        "<input name='lcd_msg' maxlength='16' value='" + esc(opts.get("lcd_msg", "")) + "'>") + "</div>",
        active="/options")


CLOCK = ("function u(){var d=new Date(),p=function(n){return('0'+n).slice(-2)};"
         "document.getElementById('h').textContent=p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds());"
         "document.getElementById('e').value=Math.floor(d.getTime()/1000)-d.getTimezoneOffset()*60}"
         "u();setInterval(u,1000);")


def heure_page(csrf, msg="", box=""):
    boxline = ("<p>Heure du boîtier : <b>%s</b></p>" % esc(box)) if box else ""
    return page("Heure", msg + "<div class='c'><small>Heure de votre téléphone</small>"
                "<div class='tm' id='h'>--:--:--</div>" + boxline
                + form(csrf, "/heure", "<input type='hidden' name='epoch' id='e'>",
                       "🕐 Régler le boîtier sur cette heure") + "</div>", active="/", js=CLOCK)


def password_page(csrf, msg=""):
    return page("Mot de passe", msg + "<div class='c'>" + form(
        csrf, "/password",
        "<label>Mot de passe actuel</label><input type='password' name='old' required>"
        "<label>Nouveau mot de passe (6 caractères minimum)</label><input type='password' name='new' required>"
        "<label>Confirmer le nouveau mot de passe</label><input type='password' name='new2' required>")
        + "</div><a class='b s' href='/info'>← Retour</a>", active="/info")


def info_page(ssid):
    return page("Informations",
                "<div class='c'><div class='r'><div>Wi-Fi</div><b>%s</b></div>"
                "<div class='r'><div>Adresse</div><b>192.168.4.1</b></div>"
                "<div class='r'><div>Version</div><b>%s</b></div></div>"
                "<p><small>Astuce : ajoutez cette page à l'écran d'accueil de votre téléphone "
                "pour l'ouvrir en un geste.</small></p>"
                "<a class='b s' href='/password'>🔑 Changer le mot de passe</a>"
                "<a class='b s' href='/logout'>🚪 Quitter</a>" % (esc(ssid), esc(VERSION)), active="/info")


def fiche_page(meds, doses):
    rows = ""
    for m in sorted(meds, key=lambda x: x["slot"]):
        times = ", ".join(sorted(d["time"] for d in doses if d["slot"] == m["slot"]))
        rows += ("<tr><td>%s</td><td><b>%s</b> %s</td><td>%s%s</td><td>%s</td></tr>"
                 % (m["slot"], esc(m["name"]), esc(m["dose"]), dot(m["color"]), esc(m["color"]), esc(times)))
    return page("Fiche de remplissage",
                "<div class='c'><table><tr><th>N°</th><th>Médicament</th><th>Couleur</th><th>Horaires</th></tr>"
                + rows + "</table></div><button class='b np' onclick='window.print()'>🖨️ Imprimer</button>"
                "<a class='b s np' href='/'>← Retour</a>", active="/")
