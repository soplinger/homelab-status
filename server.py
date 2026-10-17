"""Serve the status page and a JSON endpoint on localhost."""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

from status import collect_status

PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Homelab status</title></head>
<body>
<h1>Homelab status</h1>
<pre id="status">loading...</pre>
<script>
fetch("/api/status")
  .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
  .then(s => { document.getElementById("status").textContent = JSON.stringify(s, null, 2); })
  .catch(e => { document.getElementById("status").textContent = "status unavailable: " + e.message; });
</script>
</body>
</html>
"""


def is_allowed_host(host_header: str, port: int) -> bool:
    """Accept only the server's own localhost names, to block DNS rebinding."""
    return host_header in {f"127.0.0.1:{port}", f"localhost:{port}"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not is_allowed_host(self.headers.get("Host", ""), self.server.server_port):
            self._send(403, "text/plain; charset=utf-8", b"forbidden")
            return
        path = urlsplit(self.path).path
        if path == "/api/status":
            try:
                body = json.dumps(collect_status(), indent=2).encode("utf-8")
            except (OSError, ValueError) as e:
                error = json.dumps({"error": f"status unavailable: {e}"}).encode("utf-8")
                self._send(500, "application/json", error)
                return
            self._send(200, "application/json", body)
        elif path == "/":
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        else:
            self._send(404, "text/plain; charset=utf-8", b"not found")

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def parse_port(argv: list) -> int:
    """Return the port from argv, default 8080. Exit with usage on bad input."""
    if len(argv) < 2:
        return 8080
    try:
        port = int(argv[1])
    except ValueError:
        port = -1
    if not 1 <= port <= 65535:
        print("usage: python3 server.py [port]   (port 1-65535, default 8080)", file=sys.stderr)
        sys.exit(2)
    return port


def main():
    port = parse_port(sys.argv)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
