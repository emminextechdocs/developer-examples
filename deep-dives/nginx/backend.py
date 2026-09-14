from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

name = os.environ["BACKEND_NAME"]
posts = 0

class Handler(BaseHTTPRequestHandler):
    def respond(self, status):
        body = json.dumps({"backend": name, "posts": posts}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.respond(200 if self.path == "/stats" or name == "b" else 503)

    def do_POST(self):
        global posts
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        posts += 1
        self.respond(503 if name == "a" else 200)

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
