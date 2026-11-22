# Constantes du projet. Modifiables par l'equipe du projet.

WIFI_SSID = "Aouine"
WIFI_PASSWORD = "ChangezMoi2026"   # 8 caracteres minimum (WPA2). A CHANGER avant l'usage reel.
WEB_SLOTS = 6                      # compartiments proposes dans l'interface
MAX_DOSES_PER_MED = 5              # prises par jour et par medicament
HISTORY_MAX = 40                   # evenements gardes dans l'historique
MAX_SESSIONS = 3                   # telephones connectes en meme temps (le plus ancien est deconnecte)
MAX_FAILS = 5                     # essais de connexion rates avant blocage
LOCK_SECONDS = 300                 # duree du blocage (5 minutes)
UNLOCK_SECONDS = 300               # duree du deverrouillage d'urgence
WIFI_IDLE_SECONDS = 600            # arret du Wi-Fi apres 10 minutes d'inactivite
VERSION = "0.1"
COLORS = ("rouge",)                # tous les compartiments sont rouges
LANGS = ("fr", "ar")               # langues de l'interface
DEFAULT_LANG = "fr"
ALARMS = ("doux", "normal", "fort")
