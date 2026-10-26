# -*- coding: utf-8 -*-
"""가짜 서버 v1: 시연값 응답을 localhost에서 돌려준다. 실제 OpenAlex, Crossref의 동작이 아니다.
- 직전 요청과 min_gap 초 안에 다시 오면 429(이 간격은 시험용으로 이 책이 정했고 실제 서비스의 값이 아니다).
- /blocked 는 403."""
import json, os, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import demodata


class Fake:
    def __init__(self, min_gap=0.2):
        self.min_gap = min_gap
        self.last = None
        self.log = []                 # (도착 시각(monotonic), 경로, 응답 코드)
        self.lock = threading.Lock()
        self.srv = ThreadingHTTPServer(('127.0.0.1', 0), self._handler())
        self.port = self.srv.server_address[1]
        self.oa, self.cr = demodata.build(self.port)
        self.pdfs = demodata.pdf_files()
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def start(self):
        self.t.start(); return self

    def stop(self):
        self.srv.shutdown(); self.srv.server_close()

    def _handler(self):
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, body, ctype='application/json'):
                self.send_response(code)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                now = time.monotonic()
                path = self.path.split('?')[0]
                with outer.lock:
                    too_fast = outer.last is not None and now - outer.last < outer.min_gap
                    outer.last = now
                if path == '/blocked':
                    code = 403; self._send(403, b'{}')
                elif too_fast:
                    code = 429; self._send(429, b'{"error":"too many requests"}')
                elif path.startswith('/openalex/works/doi:'):
                    k = path.split('doi:')[1].lower()
                    w = outer.oa.get(k.replace('10.9999/', ''))
                    code = 200 if w else 404
                    self._send(code, json.dumps(w).encode() if w else b'{}')
                elif path.startswith('/crossref/works/'):
                    k = path.split('/works/')[1].lower()
                    w = outer.cr.get(k.replace('10.9999/', ''))
                    code = 200 if w else 404
                    self._send(code, json.dumps(w).encode() if w else b'{}')
                elif path.startswith('/pdf/'):
                    f = outer.pdfs.get(path.split('/pdf/')[1].replace('.pdf', ''))
                    code = 200 if f else 404
                    self._send(code, open(f, 'rb').read() if f else b'', 'application/pdf')
                elif path.startswith('/landing/'):
                    code = 200; self._send(200, b'<html><body>landing page, not a pdf</body></html>', 'text/html')
                else:
                    code = 404; self._send(404, b'{}')
                with outer.lock:
                    outer.log.append((now, path, code))
        return H
