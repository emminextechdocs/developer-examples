"""Demonstrate draining existing work; not a production HTTP server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import signal
import threading
import time

lock = threading.Lock()
active = 0
draining = False

def log(event, **fields):
    print(json.dumps({"event": event, **fields}), flush=True)

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        global active, draining
        if self.path == "/drain":
            with lock:
                draining = True
            log("drain_started")
            self.reply(200, {"draining": True})
            return
        if self.path in ("/ready", "/live"):
            self.reply(503 if self.path == "/ready" and draining else 200, {"draining": draining})
            return
        with lock:
            if draining:
                admitted = False
            else:
                active += 1
                admitted = True
        if not admitted:
            self.reply(503, {"reason": "draining"})
            return
        log("work_started")
        try:
            time.sleep(6)
            self.reply(200, {"completed": True})
            log("work_completed")
        finally:
            with lock:
                active -= 1

server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)

def stop(signum, frame):
    global draining
    with lock:
        draining = True
        count = active
    log("sigterm", active=count)
    def finish():
        while True:
            with lock:
                if active == 0:
                    break
            time.sleep(0.05)
        # shutdown must run on a different thread from serve_forever.
        server.shutdown()
    threading.Thread(target=finish).start()

signal.signal(signal.SIGTERM, stop)
server.serve_forever()
server.server_close()
log("shutdown_complete")
