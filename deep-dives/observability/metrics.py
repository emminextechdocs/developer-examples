"""Synthetic counters for the live Prometheus tutorial; never production SLO data."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

started = time.monotonic()

class Metrics(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/metrics':
            self.send_error(404)
            return
        elapsed = time.monotonic() - started
        count = int(elapsed * 100)
        slow = int(count * .02)
        good = count - slow
        total_seconds = good * .1 + slow * .5
        body = f'''# HELP http_request_duration_seconds Synthetic checkout latency observations.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{{service="checkout",le="0.3"}} {good}
http_request_duration_seconds_bucket{{service="checkout",le="+Inf"}} {count}
http_request_duration_seconds_sum{{service="checkout"}} {total_seconds}
http_request_duration_seconds_count{{service="checkout"}} {count}
'''.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *_):
        pass

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8000), Metrics).serve_forever()
