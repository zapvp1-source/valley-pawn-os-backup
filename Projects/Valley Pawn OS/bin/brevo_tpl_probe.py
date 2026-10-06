#!/usr/bin/env python3
"""read-only: print the context around every [[MARKER]] in a Brevo template (default 11)."""
import json, os, re, sys, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
tid = sys.argv[1] if len(sys.argv) > 1 else "11"
h = json.load(urllib.request.urlopen(urllib.request.Request("https://api.brevo.com/v3/smtp/templates/" + tid, headers={"api-key": K})))["htmlContent"]
for m in re.finditer(r"\[\[[A-Z_]+\]\]", h):
    print(m.group(0), "::", repr(h[max(0, m.start() - 90):m.end() + 20]))
