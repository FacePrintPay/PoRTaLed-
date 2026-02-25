from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

GATEWAY_URL = os.environ["GATEWAY_URL"]        # e.g. https://<your-tunnel>.trycloudflare.com
API_TOKEN   = os.environ["AIKRE8TIVE_TOKEN"]    # shared secret

class handler(BaseHTTPRequestHandler):
    def _deny(self, code=401, msg="unauthorized"):
        self.send_response(code); self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())

    def do_POST(self):
        if self.headers.get("Authorization") != f"Bearer {API_TOKEN}":
            return self._deny()
        try:
            length = int(self.headers.get("content-length", "0"))
            body = self.rfile.read(length)
            req  = urllib.request.Request(
                f"{GATEWAY_URL}/task",
                data=body,
                headers={"Content-Type":"application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type","application/json")
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self._deny(502, str(e))
