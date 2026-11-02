#!/usr/bin/env python3
"""HTTP ingress nội bộ cho host có callback tin nhắn.

Chỉ bind loopback; nếu cần truy cập từ mạng, đặt sau reverse proxy HTTPS với
kiểm soát truy cập. KHÔNG có ChatGPT webhook mặc định.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from member_capture import ingest

MAX_BODY = 40 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Không log nội dung hay Authorization token.
        return

    def respond(self, status, value):
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/health":
            return self.respond(404, {"status": "not_found"})
        # Có server không đồng nghĩa có upstream ChatGPT callback.
        return self.respond(200, {"status": "listening", "upstream_connected": False})

    def do_POST(self):
        if self.path != "/v1/events":
            return self.respond(404, {"status": "not_found"})
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return self.respond(401, {"status": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > MAX_BODY:
                return self.respond(413, {"status": "too_large"})
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected JSON object")
            result = ingest(payload, auth[7:])
            return self.respond(200, result)
        except PermissionError:
            return self.respond(403, {"status": "forbidden"})
        except (ValueError, KeyError, json.JSONDecodeError):
            return self.respond(400, {"status": "invalid_event"})
        except (RuntimeError, OSError):
            # Cổng không báo lưu thành công khi không có SHA push remote.
            return self.respond(503, {"status": "not_synced"})


def main():
    host = "127.0.0.1"
    port = int(os.environ.get("AI_CAPTURE_PORT", "8765"))
    if not (1024 <= port <= 65535):
        raise ValueError("Port không hợp lệ")
    print(f"Capture gateway listening on http://{host}:{port} (loopback only)", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
