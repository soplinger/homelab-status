"""Serve the status page and a JSON endpoint on localhost."""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from status import collect_status

PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Homelab status</title></head>
<body>
<h1>Homelab status</h1>
<pre id="status">loading...</pre>
<script>
fetch("/api/status").then(r => r.json()).then(s => {
  document.getElementById("status").textContent = JSON.stringify(s, null, 2);
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            body = json.dumps(collect_status(), indent=2).encode("utf-8")
            self._send(200, "application/json", body)
        elif self.path == "/":
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        else:
            self._send(404, "text/plain; charset=utf-8", b"not found")

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
