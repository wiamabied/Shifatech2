import json, os

_replace = getattr(os, "replace", os.rename)


class Store:
    """Planning (schedule.json). Ecriture dans la flash uniquement lors d'un vrai changement."""

    def __init__(self, path="schedule.json", history_max=40):
        self.path = path
        self.history_max = history_max
        self.data = {
            "version": 0,
            "meds": [],       # {"name","dose","color","slot"}
            "doses": [],      # {"slot","time"}  time = "HH:MM"
            "options": {"alarm": "normal", "brightness": 5, "lcd_msg": ""},
            "history": [],    # textes courts (derniers evenements)
        }
        try:
            with open(path) as f:
                self.data.update(json.load(f))
        except (OSError, ValueError):
            pass

    def commit(self):
        """Augmente la version, puis ecrit via un fichier temporaire et un renommage."""
        self.data["version"] += 1
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f)
        _replace(tmp, self.path)

    def log(self, text):
        h = self.data["history"]
        h.append(text)
        del h[:-self.history_max]
