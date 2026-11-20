"""Genere les QR codes du boitier et une feuille prete a imprimer :
  - qr_wifi.png         : connexion au Wi-Fi du boitier
  - qr_page.png         : ouvre http://192.168.4.1
  - feuille_wifi.html   : feuille A4 avec les deux (1. Connectez-vous, 2. Ouvrez la page)
Installation : pip install segno   puis   python3 tools/qr_wifi.py
Pour imprimer : ouvrez feuille_wifi.html dans un navigateur, puis Ctrl+P (ou Imprimer en PDF).
Regenerez tout chaque fois que le mot de passe Wi-Fi change (firmware/config.py)."""
import html
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firmware"))
from config import WIFI_SSID, WIFI_PASSWORD

try:
    import segno
except ImportError:
    sys.exit("Installez d'abord segno : pip install segno")

URL = "http://192.168.4.1"


def esc(s):  # echappement du format WIFI:
    for c in '\\;,:"':
        s = s.replace(c, "\\" + c)
    return s


wifi_text = "WIFI:T:WPA;S:%s;P:%s;;" % (esc(WIFI_SSID), esc(WIFI_PASSWORD))
qr_wifi = segno.make(wifi_text, error="m")
qr_page = segno.make(URL, error="m")

qr_wifi.save("qr_wifi.png", scale=10, border=4)
qr_page.save("qr_page.png", scale=10, border=4)

img_wifi = qr_wifi.svg_data_uri(scale=10, border=4)
img_page = qr_page.svg_data_uri(scale=10, border=4)

feuille = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Connexion au boitier</title>
<style>
  @page {{ size: A4; margin: 15mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: Arial, Helvetica, sans-serif; color: #111; margin: 0; text-align: center; }}
  h1 {{ font-size: 28pt; margin: 0 0 4mm; }}
  .reseau {{ font-size: 14pt; color: #444; margin-bottom: 10mm; }}
  .etapes {{ display: flex; gap: 10mm; justify-content: center; }}
  .etape {{ flex: 1; border: 2px solid #111; border-radius: 6mm; padding: 8mm 6mm; }}
  .num {{ font-size: 22pt; font-weight: bold; margin-bottom: 4mm; }}
  .etape img {{ width: 100%; max-width: 70mm; height: auto; }}
  .aide {{ font-size: 12pt; color: #333; margin-top: 4mm; }}
  .url {{ font-family: monospace; font-size: 14pt; margin-top: 2mm; }}
</style>
</head>
<body>
  <h1>Acc&egrave;s au bo&icirc;tier</h1>
  <div class="reseau">R&eacute;seau Wi-Fi : <strong>{ssid}</strong></div>
  <div class="etapes">
    <div class="etape">
      <div class="num">1. Connectez-vous</div>
      <img src="{img_wifi}" alt="QR code Wi-Fi">
      <div class="aide">Scannez avec l'appareil photo du t&eacute;l&eacute;phone pour rejoindre le Wi-Fi.</div>
    </div>
    <div class="etape">
      <div class="num">2. Ouvrez la page</div>
      <img src="{img_page}" alt="QR code page">
      <div class="aide">Puis scannez celui-ci pour ouvrir la page.</div>
      <div class="url">{url}</div>
    </div>
  </div>
</body>
</html>
""".format(ssid=html.escape(WIFI_SSID), img_wifi=img_wifi, img_page=img_page, url=html.escape(URL))

with open("feuille_wifi.html", "w", encoding="utf-8") as f:
    f.write(feuille)

print("Fichiers enregistres : qr_wifi.png, qr_page.png, feuille_wifi.html")
print("Ouvrez feuille_wifi.html dans un navigateur et imprimez-la (testez les 2 QR avec un telephone avant).")
