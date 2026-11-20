# Format de schedule.json (à valider avec le responsable du boîtier)

L'interface écrit ce fichier. `version` augmente de 1 à chaque modification réelle. Le boîtier doit ignorer les champs qu'il ne connaît pas. Ne renommez ni ne supprimez aucun champ sans prévenir.

```json
{
  "version": 2,
  "meds":    [{"name": "Doliprane", "dose": "500mg", "color": "bleu", "slot": 1}],
  "doses":   [{"slot": 1, "time": "08:00"}],
  "options": {"alarm": "normal", "brightness": 5, "lcd_msg": ""},
  "history": ["Ajout Doliprane"]
}
```

| Champ | Contenu |
|---|---|
| `meds[].slot` | compartiment, 1 à `WEB_SLOTS` (6) |
| `meds[].color` | rouge, vert, bleu, jaune, blanc ou violet |
| `doses[]` | une prise : compartiment et heure « HH:MM » (5 par médicament au maximum) |
| `options.alarm` | doux, normal ou fort |
| `options.brightness` | 1 à 10 |
| `options.lcd_msg` | ASCII, 16 caractères maximum, déjà prêt pour l'écran |
| `history` | 40 textes au maximum, les plus récents à la fin |

Hypothèse à confirmer : les noms de champs ci-dessus ont été choisis par l'interface car le format du boîtier n'était pas disponible.
