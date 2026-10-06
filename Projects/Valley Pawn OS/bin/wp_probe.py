#!/usr/bin/env python3
"""read-only: list WP REST namespaces + find where the spot-price snippet lives."""
import base64, json, os, urllib.request
kv = dict(l.strip().split("=", 1) for l in open(os.path.expanduser("~/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials")) if "=" in l)
A = "Basic " + base64.b64encode(("%s:%s" % (kv["WP_USER"].strip().strip('"'), kv["WP_APP_PASSWORD"].strip().strip('"'))).encode()).decode()
def g(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://thevalleypawn.com/wp-json" + p, headers={"Authorization": A, "User-Agent": "ValleyPawnOps/1.0"}), timeout=60))
print(g("/")["namespaces"])
for t in ("wpcode", "wpcode_snippets", "hfcm", "snippets"):
    try: print(t, str(g("/wp/v2/types"))[:0] or "")
    except Exception as e: pass
ty = g("/wp/v2/types"); print(sorted(ty.keys()))
for ns in ("/code-snippets/v1/snippets",):
    try:
        r = g(ns); print(ns, [(x.get("id"), x.get("name")) for x in r][:40])
    except Exception as e: print(ns, "ERR", e)
html = urllib.request.urlopen(urllib.request.Request("https://thevalleypawn.com/sell-gold-culpeper/", headers={"User-Agent": "Mozilla/5.0"})).read().decode("utf-8", "replace")
import re
print(re.findall(r".{0,120}VP_GOLD_SPOT.{0,160}", html)[:3])
