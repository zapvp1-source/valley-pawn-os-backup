#!/usr/bin/env python3
"""One-shot local file server for handing policy PDFs to browser pages.
Serves ~/Documents/Claude/Projects/Human Resources on 127.0.0.1:8899 with the
CORS + Private Network Access headers Chrome requires for a page to fetch from
localhost. Auto-exits after 10 minutes. Used by the Gusto e-signature flow
(see gusto-access skill) so file bytes never need manual transcription."""
import http.server, functools, os, threading

DIR = os.path.expanduser("~/Documents/Claude/Projects/Human Resources")
PORT = 8899

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

handler = functools.partial(H, directory=DIR)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
threading.Timer(600, srv.shutdown).start()
srv.serve_forever()
