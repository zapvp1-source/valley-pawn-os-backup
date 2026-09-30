#!/usr/bin/env python3
"""slack_scope_probe.py — which OAuth scopes does the ops bot token have, and can it fetch one file? Read-only."""
import json, os, sys, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
tok = vp_slack.token()
req = urllib.request.Request("https://slack.com/api/auth.test", headers={"Authorization": "Bearer " + tok})
with urllib.request.urlopen(req, timeout=20) as r:
    print("scopes:", r.headers.get("x-oauth-scopes"))
    print("auth:", json.load(r).get("ok"))
h = json.load(urllib.request.urlopen(urllib.request.Request(
    "https://slack.com/api/conversations.history?channel=C03C7HV8L48&limit=40", headers={"Authorization": "Bearer " + tok}), timeout=20))
f = next((f for m in h.get("messages", []) for f in (m.get("files") or []) if str(f.get("mimetype","")).startswith("image/")), None)
if not f: print("no image found"); sys.exit()
print("file", f.get("id"), f.get("filetype"))
fi = json.load(urllib.request.urlopen(urllib.request.Request(
    "https://slack.com/api/files.info?file=" + f["id"], headers={"Authorization": "Bearer " + tok}), timeout=20))
print("files.info:", fi.get("ok"), fi.get("error"))
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
try:
    r = op.open(urllib.request.Request(f["url_private_download"], headers={"Authorization": "Bearer " + tok}), timeout=30)
    print("direct:", r.status, r.headers.get("content-type"), len(r.read()))
except urllib.error.HTTPError as e:
    print("direct:", e.code, "->", e.headers.get("location", "")[:120])
