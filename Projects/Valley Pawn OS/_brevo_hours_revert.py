#!/usr/bin/env python3
"""REVERSAL 2026-07-24: Waynesboro stays closed Wednesdays.
1. Delete campaign 52 (announcement — suspended, never sent).
2. Restore Template 11 + campaigns 27,28,29,30,43 htmlContent from the pre-change backups."""
import json, urllib.request
from pathlib import Path

KEY = (Path.home() / ".config" / "valley-pawn" / "brevo_api_key").read_text().strip()
BASE = "https://api.brevo.com/v3"
BK = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/brevo_backups_2026-07-23")

def call(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"accept": "application/json", "api-key": KEY, "content-type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = r.read().decode()
            return json.loads(d) if d.strip() else {}
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, path, e.read().decode()[:200])
        return None

# 1. delete campaign 52
r = call("/emailCampaigns/52", "DELETE")
print("delete #52:", "OK" if r is not None else "FAILED")
chk = call("/emailCampaigns/52")
print("verify #52 gone:", "GONE" if chk is None else f"STILL EXISTS status={chk.get('status')}")

# 2. restore originals
orig = (BK / "template_11.html").read_text()
r = call("/smtp/templates/11", "PUT", {"htmlContent": orig})
print("T11 restored:", "OK" if r is not None else "FAILED")

for cid in [27, 28, 29, 30, 43]:
    f = BK / f"campaign_{cid}.html"
    if not f.exists():
        print(f"C{cid}: NO BACKUP FILE"); continue
    c = call(f"/emailCampaigns/{cid}")
    if c and c.get("status") == "sent":
        print(f"C{cid}: SKIP (already sent)"); continue
    r = call(f"/emailCampaigns/{cid}", "PUT", {"htmlContent": f.read_text()})
    print(f"C{cid} restored:", "OK" if r is not None else "FAILED")

# verify: originals contain the old Waynesboro 5-day line
t = call("/smtp/templates/11")
h = t.get("htmlContent", "") if t else ""
print("T11 now has old Waynesboro line:", "Waynesboro &middot; Mon, Tue, Thu, Fri & Sat 10am" in h)
print("DONE")
