# Pilulier : interface web de l'aidant

Interface web d'un pilulier connecté, hébergée **par le boîtier lui-même** (Raspberry Pi Pico W sous MicroPython). L'aidant se connecte avec son téléphone au Wi-Fi du boîtier, ouvre `http://192.168.4.1` et règle tout : médicaments, horaires, options, heure, suivi du jour.

Aucun Internet, aucune box, aucun serveur externe, aucune application mobile.

> **Prototype d'aide à l'observance, pas un dispositif médical, aucun conseil médical.**

## Fonctionnement en bref

- Le Pico W crée son propre Wi-Fi (WPA2, SSID `Aouine` par défaut) et sert les pages sur le port 80.
- Un seul rôle, un seul mot de passe. Jusqu'à 3 téléphones peuvent être connectés en même temps.
- Le planning est stocké dans `schedule.json`. Les changements sont appliqués tout de suite.
- 6 compartiments, 1 médicament par compartiment, 5 prises par jour et par médicament au maximum (modifiable dans `config.py`).
- Tout est en français, sans ressource externe (ni police, ni script, ni image distante).

## Structure du dépôt

```
firmware/        Code copié sur le Pico W
  main.py          Wi-Fi, socket, boucle principale
  web.py           Serveur et règles (routes, sessions, validation)
  pages.py         Pages HTML/CSS/JS en ligne
  store.py         Lecture/écriture de schedule.json
  config.py        Constantes du projet
tests/           Tests automatiques (unittest)
tools/           demo_pc.py (interface sur PC), qr_wifi.py (QR codes et feuille à imprimer)
docs/            Notices et format de schedule.json
```

## Installation sur le Pico W

1. Installez MicroPython « Raspberry Pi Pico W » (fichier `.uf2`, mode BOOTSEL), puis Thonny.
2. **Changez `WIFI_PASSWORD`** dans `firmware/config.py` (8 caractères minimum). La valeur fournie est un exemple.
3. Copiez à la racine du Pico W : `config.py`, `store.py`, `pages.py`, `web.py`, `main.py`. `main.py` se lance au démarrage.
4. Connectez le téléphone au Wi-Fi du boîtier, ouvrez `http://192.168.4.1` et choisissez le mot de passe de l'interface (6 caractères minimum).

Détails : [docs/notice_installation.md](docs/notice_installation.md). Notice pour l'utilisateur : [docs/notice_utilisateur.md](docs/notice_utilisateur.md).

### QR codes à imprimer

```
pip install segno
python3 tools/qr_wifi.py
```

Génère `qr_wifi.png` (connexion au Wi-Fi), `qr_page.png` (ouvre `http://192.168.4.1`) et `feuille_wifi.html` (feuille A4 « 1. Connectez-vous », « 2. Ouvrez la page »). À relancer à chaque changement du mot de passe Wi-Fi.

## Lancer sur PC (sans matériel)

```
python3 tools/demo_pc.py          # puis http://localhost:8080
python3 -m unittest discover -s tests -v
```

Les données du faux boîtier sont dans `tools/demo_data/` : supprimez ce dossier pour tout remettre à zéro, mot de passe compris.

## `main.py`

Tourne sur le Pico W uniquement.

- Crée le point d'accès Wi-Fi (`network.AP_IF`, adresse `192.168.4.1`) avec `WIFI_SSID` et `WIFI_PASSWORD`.
- Ouvre un socket sur le port 80, non bloquant pour `accept()`, afin de ne pas gêner la boucle du boîtier (buzzer, verrou).
- `read_request` lit la requête HTTP (en-têtes limités à 4 Ko, corps à 2 Ko) ; `serve_once` la transmet à `App.handle` et renvoie la réponse (`Connection: close`).
- La boucle principale traite une requête à la fois, puis éteint le Wi-Fi après `WIFI_IDLE_SECONDS` (10 minutes) sans activité.
- Un commentaire marque l'endroit où brancher la logique du boîtier (bouton tactile qui rallume le Wi-Fi, horloge DS3231 via `clock_setter`).

## `web.py`

Ne connaît pas les sockets : `App.handle(méthode, url, en-têtes, corps)` renvoie `(statut, type, corps, en-têtes)`. Le même code tourne sur PC et sur le Pico W.

| Route | Rôle |
|---|---|
| `/setup` | Choix du mot de passe au premier démarrage |
| `/login`, `/logout` | Connexion et déconnexion |
| `/` | Accueil : prochaine prise, prises du jour, derniers événements, déverrouillage d'urgence |
| `/meds`, `/meds/del` | Ajouter ou supprimer un médicament (nom, dose, couleur, compartiment) |
| `/doses?edit=N`, `/doses/del` | Horaires d'un médicament (une page par médicament) |
| `/options` | Alarme (doux, normal, fort), luminosité, message de l'écran |
| `/heure` | Règle l'horloge du boîtier avec l'heure du téléphone |
| `/password` | Changement du mot de passe |
| `/info` | Nom du Wi-Fi, adresse, version |
| `/fiche` | Fiche imprimable pour remplir les compartiments |
| `/unlock` | Déverrouillage d'urgence (`UNLOCK_SECONDS`) |

Sécurité : mot de passe haché et salé (SHA-256), jeton CSRF par session sur les formulaires de l'application, blocage après 5 essais ratés (`MAX_FAILS`), échappement de tout texte saisi, Wi-Fi protégé par mot de passe. **N'exposez jamais le boîtier sur Internet.**

## Configuration (`firmware/config.py`)

| Constante | Défaut | Rôle |
|---|---|---|
| `WIFI_SSID`, `WIFI_PASSWORD` | `Aouine`, exemple | Wi-Fi du boîtier |
| `WEB_SLOTS` | 6 | Compartiments proposés |
| `MAX_DOSES_PER_MED` | 5 | Prises par jour et par médicament |
| `HISTORY_MAX` | 40 | Événements gardés |
| `MAX_SESSIONS` | 3 | Téléphones connectés en même temps |
| `MAX_FAILS`, `LOCK_SECONDS` | 5, 300 | Blocage après essais ratés |
| `UNLOCK_SECONDS` | 300 | Durée du déverrouillage d'urgence |
| `WIFI_IDLE_SECONDS` | 600 | Arrêt du Wi-Fi sans activité |

## Format du planning

`schedule.json` : voir [docs/format_schedule_json.md](docs/format_schedule_json.md). Le numéro de version augmente à chaque modification, les champs inconnus sont ignorés, et l'écriture passe par un fichier temporaire puis un renommage.

## Limites du Pico W

264 Ko de RAM, 2 Mo de flash, un seul client servi à la fois. Pages de moins de 12 Ko, réponse en moins d'une demi-seconde, au moins 60 Ko de RAM libres (à mesurer sur le vrai matériel avec `import gc; gc.collect(); print(gc.mem_free())`).

## État du projet

- 42 tests automatiques réussis sur PC.
- Pas encore testé sur un vrai Pico W (mémoire, temps de réponse, affichage sur téléphone).
- Le lien avec la logique du boîtier (bouton tactile, DS3231, verrou) reste à brancher.
