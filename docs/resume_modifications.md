# Résumé : ce qui a été réalisé et pourquoi

Aucun code de départ n'était disponible : l'interface a été construite de zéro selon le document de référence du 20 novembre 2026, puis son apparence a été refaite pour être plus simple et plus agréable.

## Architecture
- `web.py` ne connaît pas les sockets : `App.handle(méthode, url, en-têtes, corps)` renvoie une réponse. Le même code tourne sur PC (`tools/demo_pc.py`) et sur le Pico W (`main.py`), ce qui permet de tout tester sans matériel.
- `pages.py` : tout le HTML, le CSS et le JavaScript en ligne, aucune ressource externe.
- `store.py` : `schedule.json`, version incrémentée à chaque modification, écriture via fichier temporaire puis renommage, historique de 40 événements.

## Apparence (version 0.1, refonte)
- **Navigation** : barre en bas de l'écran (Accueil, Médicaments, Options, Infos), page active en bleu.
- **Accueil** : salutation selon l'heure, carte « Prochaine prise » (heure, médicament, compartiment, « dans 1 h 30 » qui se met à jour seul, « demain » si besoin), liste « Aujourd'hui » avec les prises passées estompées, derniers événements, outils, bouton d'urgence séparé.
- **Médicaments** : une carte par médicament avec pastille de couleur et heures de prise visibles ; ajout par choix de couleur (pastilles) et de compartiment (boutons), dans un volet qui s'ouvre tout seul quand il n'y a encore rien.
- **Horaires** : heures affichées en pastilles avec ✕ pour supprimer ; **Options** : alarme en 3 boutons, luminosité avec curseur ; **Heure** : horloge du téléphone en direct à côté de celle du boîtier.
- Messages de confirmation ou d'erreur qui apparaissent puis disparaissent tout seuls (animation CSS, sans script) ; bouton désactivé après un clic pour éviter les doubles envois ; mode sombre automatique ; animations légères.
- Poids : 5 à 9 Ko par page dans le pire cas (6 médicaments, 30 prises), limite de 12 Ko.

## Fonctions
Premier mot de passe, connexion, changement de mot de passe, médicaments, horaires (une page par médicament), options, suivi du jour, historique, réglage de l'heure avec l'heure du téléphone, déverrouillage d'urgence avec l'heure de fin, page Informations, fiche imprimable, confirmation après chaque enregistrement, script de QR code (`tools/qr_wifi.py`).

## Changements de comportement à connaître
- **Jusqu'à 3 téléphones connectés en même temps** (`MAX_SESSIONS` dans `config.py`) : auparavant, la connexion d'un deuxième téléphone déconnectait le premier. Un changement de mot de passe déconnecte les autres téléphones.
- Les demandes automatiques d'icône (`/favicon.ico`) reçoivent une réponse vide au lieu d'une page d'erreur complète, ce qui économise une requête au Pico.

## Sécurité conservée
Mot de passe haché et salé (SHA-256), jeton CSRF sur chaque formulaire (un jeton par téléphone), blocage après 5 essais, échappement de tout texte saisi, mention légale sur chaque page, aucun lien externe.

## Vérifié
42 tests automatiques réussis sur PC (sécurité, règles, plusieurs téléphones, prochaine prise, pages de moins de 12 Ko dans le pire cas, aucun lien externe). Parcours complet dans un navigateur au format téléphone (création du mot de passe, ajout de médicaments avec les sélecteurs, horaires, toutes les pages) en mode clair et sombre, sans erreur de console.

## Pas encore fait ou à vérifier
- **Non testé sur le vrai Pico W** : mémoire libre (60 Ko minimum), temps de réponse, affichage sur téléphone réel (les emojis dépendent du téléphone).
- Le lien avec `box.py` (boucle du boîtier, bouton tactile, horloge DS3231) reste à brancher (voir `notice_installation.md`, section 7).
- Format de `schedule.json` à valider avec le responsable du boîtier.
- Non réalisés : alertes marquées comme lues, export CSV, sauvegarde et restauration, page de test du buzzer.
- Le déverrouillage d'urgence est enregistré dans l'historique ; son effet sur le verrou doit être lu par `box.py` (l'interface ne pilote pas le matériel).
