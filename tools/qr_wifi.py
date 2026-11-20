"""Genere le QR code de connexion au Wi-Fi du boitier : qr_wifi.png (a imprimer).
Installation : pip install segno   puis   python3 tools/qr_wifi.py
Regenerez-le chaque fois que le mot de passe Wi-Fi change (firmware/config.py)."""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firmware"))
from config import WIFI_SSID, WIFI_PASSWORD

try:
    import segno
except ImportError:
    sys.exit("Installez d'abord segno : pip install segno")


def esc(s):  # echappement du format WIFI:
    for c in '\\;,:"':
        s = s.replace(c, "\\" + c)
    return s


text = "WIFI:T:WPA;S:%s;P:%s;;" % (esc(WIFI_SSID), esc(WIFI_PASSWORD))
segno.make(text, error="m").save("qr_wifi.png", scale=10, border=4)
print("QR code enregistre : qr_wifi.png  (testez-le avec un telephone avant d'imprimer)")
