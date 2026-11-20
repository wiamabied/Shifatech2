# Pico W : cree le Wi-Fi "Aouine" et sert l'interface sur http://192.168.4.1
import network, socket, time, gc
from config import WIFI_SSID, WIFI_PASSWORD, WIFI_IDLE_SECONDS
from store import Store
from web import App

REASON = {200: "OK", 204: "No Content", 303: "See Other", 403: "Forbidden", 404: "Not Found"}

ap = network.WLAN(network.AP_IF)
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)    # WPA2
ap.active(True)                                       # adresse 192.168.4.1

app = App(Store())
srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 80))
srv.listen(2)
srv.settimeout(0)                                     # accept() ne bloque pas la boucle du boitier
last_activity = time.time()


def read_request(cl):
    data = b""
    while b"\r\n\r\n" not in data and len(data) < 4096:
        chunk = cl.recv(1024)
        if not chunk:
            break
        data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode().split("\r\n")
    method, target, _ = lines[0].split(" ", 2)
    hdr = {}
    for l in lines[1:]:
        k, _, v = l.partition(":")
        hdr[k.strip().lower()] = v.strip()
    n = int(hdr.get("content-length", "0"))
    while len(body) < n and n < 2048:
        chunk = cl.recv(512)
        if not chunk:
            break
        body += chunk
    return method, target, hdr, body


def serve_once():
    global last_activity
    try:
        cl, _ = srv.accept()
    except OSError:
        return                                        # personne ne se connecte
    last_activity = time.time()
    cl.settimeout(2)
    try:
        method, target, hdr, body = read_request(cl)
        status, ctype, out, extra = app.handle(method, target, hdr, body)
        out = out.encode()
        head = "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n" % (
            status, REASON.get(status, "OK"), ctype, len(out))
        for k, v in extra:
            head += "%s: %s\r\n" % (k, v)
        cl.send(head.encode() + b"\r\n" + out)
    except Exception as e:
        print("erreur", e)
    finally:
        cl.close()
        gc.collect()


while True:
    serve_once()
    # --- ici : un tour de la boucle du boitier (buzzer, verrou, bouton tactile) ---
    if ap.active() and time.time() - last_activity > WIFI_IDLE_SECONDS:
        ap.active(False)                              # arret du Wi-Fi apres ~10 min d'inactivite
        # le bouton tactile le rallume : ap.active(True); last_activity = time.time()
    time.sleep_ms(20)
