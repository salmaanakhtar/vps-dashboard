#!/usr/bin/env python3
"""vps-dashboard — unified VPS overview server.

Serves a static dashboard page and proxies live metrics from the host metrics
agent (hermes-host-agent) over the internal hermes_routing network.
Stdlib only; no third-party dependencies.
"""

import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AGENT = os.environ.get("AGENT_URL", "http://hermes-host-agent:9101").rstrip("/")
PORT = int(os.environ.get("PORT", "8080"))
CACHE_TTL = float(os.environ.get("CACHE_TTL", "2"))

_cache = {}
_last = {}


def fetch(path: str) -> bytes:
    """Fetch from the agent with a short TTL cache."""
    now = time.monotonic()
    if path in _cache and now - _last.get(path, 0) < CACHE_TTL:
        return _cache[path]
    try:
        with urllib.request.urlopen(f"{AGENT}{path}", timeout=5) as r:
            data = r.read()
        _cache[path] = data
        _last[path] = now
        return data
    except Exception:
        return json.dumps({"error": "agent unavailable"}).encode()


class Handler(BaseHTTPRequestHandler):
    server_version = "vps-dashboard/1.0"

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: C901
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            try:
                with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                self._send(500, b"index.html missing", "text/plain")
        elif path.startswith("/api/"):
            self._send(200, fetch(path), "application/json")
        elif path == "/healthz":
            self._send(200, b"ok", "text/plain")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *args):  # silence access log noise
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
