#!/usr/bin/env python3
"""read-only: find the non-existent Harrisonburg 'Suite/Ste 22' in upcoming Brevo sends + Master template 11."""
import json, os, re, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
g = lambda p: json.load(urllib.request.urlopen(urllib.request.Request("https://api.brevo.com/v3" + p, headers={"api-key": K}), timeout=60))
pat = re.compile(r"(Suite|Ste\.?)\s*22", re.I)
print("template 11:", len(pat.findall(g("/smtp/templates/11")["htmlContent"])))
for st in ("queued", "draft"):
    for c in g("/emailCampaigns?status=%s&limit=100" % st)["campaigns"]:
        h = g("/emailCampaigns/%d" % c["id"]).get("htmlContent") or ""
        n = len(pat.findall(h))
        if n: print(st, c["id"], c["name"], n)
