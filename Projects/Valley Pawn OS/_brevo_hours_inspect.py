#!/usr/bin/env python3
"""Inspect Brevo Template 11 + staged campaigns for hours strings (read-only)."""
import json, re, urllib.request
from pathlib import Path

KEY = (Path.home() / ".config" / "valley-pawn" / "brevo_api_key").read_text().strip()
BASE = "https://api.brevo.com/v3"

def get(path):
    req = urllib.request.Request(BASE + path, headers={"accept": "application/json", "api-key": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def hours_contexts(html, label):
    print(f"\n===== {label} (len {len(html)}) =====")
    pats = [r"Mon[^<]{0,80}Sat", r"[Cc]losed[^<]{0,60}", r"Waynesboro[^<]{0,100}", r"All other stores[^<]{0,120}", r"10am[^<]{0,40}", r"10:00[^<]{0,60}"]
    seen = set()
    for p in pats:
        for m in re.finditer(p, html):
            s = m.group(0)[:150]
            if s not in seen:
                seen.add(s)
                print(f"  [{m.start()}] {s!r}")

t = get("/smtp/templates/11")
hours_contexts(t.get("htmlContent", ""), f"TEMPLATE 11: {t.get('name')}")

for cid in [26, 27, 28, 29, 30, 43]:
    try:
        c = get(f"/emailCampaigns/{cid}")
        hours_contexts(c.get("htmlContent", ""), f"CAMPAIGN {cid}: {c.get('name')} [{c.get('status')}]")
    except Exception as e:
        print(f"CAMPAIGN {cid}: ERROR {e}")

print("\n===== LISTS =====")
ls = get("/contacts/lists?limit=50")
for l in ls.get("lists", []):
    print(f"  id={l['id']} name={l['name']!r} subscribers={l.get('totalSubscribers')}")
