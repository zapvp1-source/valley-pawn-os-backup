#!/usr/bin/env python3
"""Check whether the two generic/shared phone numbers found on 2026-08-25
(+18665403229, +19173877468 - each tied to dozens of unrelated emails in the
Bravo archive) already got written into Brevo's SMS attribute by the 2026-08-24
bulk enrichment run, which had no shared-number filter."""
import json, urllib.request, os, time

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
SHARED = {"18665403229", "19173877468"}


def req(path):
    r = urllib.request.Request(BASE + path, headers={"api-key": KEY, "Accept": "application/json"})
    with urllib.request.urlopen(r) as resp:
        return resp.status, json.loads(resp.read())


hits = []
offset = 0
while True:
    st, d = req(f"/contacts?limit=500&offset={offset}")
    if st != 200:
        break
    batch = d.get("contacts", [])
    for c in batch:
        sms = str((c.get("attributes") or {}).get("SMS") or "")
        digits = "".join(ch for ch in sms if ch.isdigit())
        if digits in SHARED:
            hits.append((c.get("email"), sms))
    if len(batch) < 500:
        break
    offset += 500
    time.sleep(0.3)

print(f"contacts with a shared/generic SMS value already in Brevo: {len(hits)}")
for h in hits[:50]:
    print("  ", h)
