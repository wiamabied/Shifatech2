# Notice d'installation sur le Pico W

## 1. Préparer le Pico W (une seule fois)
1. Téléchargez le fichier MicroPython « Raspberry Pi Pico W » (.uf2) sur le site officiel de MicroPython.
2. Maintenez le bouton BOOTSEL, branchez le Pico W en USB, puis déposez le fichier .uf2 sur le disque qui apparaît.
3. Installez Thonny et choisissez l'interpréteur « MicroPython (Raspberry Pi Pico) ».

## 2. Choisir le mot de passe du Wi-Fi (avant tout usage réel)
Ouvrez `firmware/config.py` et changez `WIFI_PASSWORD` (8 caractères minimum). Le mot de passe actuel est un exemple.
Puis régénérez le QR code : `pip install segno` puis `python3 tools/qr_wifi.py` (fichier `qr_wifi.png`, à imprimer sur le boîtier ou la notice). Testez-le avec un téléphone.

## 3. Copier les fichiers
Dans Thonny, copiez ces 5 fichiers de `firmware/` à la racine du Pico W (clic droit, « Upload to / ») :
`config.py`, `store.py`, `pages.py`, `web.py`, `main.py`.
`main.py` se lance tout seul au démarrage. Ne copiez ni `tests/` ni `tools/`.

## 4. Première connexion
1. Branchez le boîtier. Le Wi-Fi « Aouine » apparaît (ou, une fois l'intégration faite, appui court sur le bouton tactile).
2. Sur le téléphone, scannez le QR code ou choisissez « Aouine » et entrez le mot de passe Wi-Fi.
3. Ouvrez http://192.168.4.1.
4. À la première visite, l'interface demande de **choisir le mot de passe de l'interface** (6 caractères minimum). Il est ensuite demandé à chaque connexion.
5. Ajoutez un raccourci sur l'écran d'accueil du téléphone (menu du navigateur).

## 5. Vérifications sur le vrai Pico W
Dans le terminal de Thonny :
```python
import gc; gc.collect(); print(gc.mem_free())
```
Il doit rester **au moins 60 Ko** libres. Parcourez toutes les pages avec un vrai téléphone et vérifiez qu'aucune ne met plus d'une demi-seconde à s'afficher.

## 6. Mot de passe oublié
Supprimez le fichier `auth.json` du Pico W avec Thonny, puis redémarrez : l'interface redemande un nouveau mot de passe. Le planning n'est pas touché.

## 7. Intégration avec le boîtier (à faire avec le responsable du boîtier)
`main.py` contient un commentaire « tour de la boucle du boîtier » : c'est là que `box.py` doit être appelé. Le bouton tactile doit rallumer le Wi-Fi (`ap.active(True)` et `last_activity = time.time()`). Pour régler l'horloge DS3231 depuis la page « Heure », passez une fonction à `App(..., clock_setter=ma_fonction)`.
Le format de `schedule.json` est décrit dans `docs/format_schedule_json.md`.

## Travailler sur PC (sans le matériel)
```
python3 tools/demo_pc.py          # puis http://localhost:8080
python3 -m unittest discover -s tests -v
```
Supprimez `tools/demo_data/` pour tout remettre à zéro (mot de passe compris).
