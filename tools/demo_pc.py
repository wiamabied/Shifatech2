"""Lance l'interface sur PC avec un faux boitier : python3 tools/demo_pc.py puis http://localhost:8080
Les donnees sont dans tools/demo_data/ : supprimez ce dossier pour tout remettre a zero."""
import os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "firmware"))
from store import Store
from web import App

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
DATA = os.path.join(HERE, "demo_data")
os.makedirs(DATA, exist_ok=True)
app = App(Store(os.path.join(DATA, "schedule.json")), os.path.join(DATA, "auth.json"),
          clock_setter=lambda e: print("Heure du faux boitier reglee :", e))


class Handler(BaseHTTPRequestHandler):
    def _go(self, method):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else b""
        hdrs = {k.lower(): v for k, v in self.headers.items()}
        status, ctype, out, extra = app.handle(method, self.path, hdrs, body)
        data = out.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._go("GET")

    def do_POST(self):
        self._go("POST")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Interface sur http://localhost:%d  (Ctrl+C pour arreter)" % PORT)
    HTTPServer(("localhost", PORT), Handler).serve_forever()
