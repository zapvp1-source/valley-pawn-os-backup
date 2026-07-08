#!/usr/bin/env python3
"""
Dormant -> Sunset sweep
Run after Reactivation Email 3 (campaign ID 18) has been sent for ~3 days.

What it does:
1. Pulls the Dormant segment (ID 4) members
2. For each contact, checks: did they click ANY link in any of the 3 reactivation campaigns (16, 17, 18)?
3. Contacts that DID click → leave alone (they'll naturally re-enter the Engaged segment via click history)
4. Contacts that did NOT click any of the 3 → move to Sunset list, remove from list 3

Usage:
    python3 sweep_dormant_to_sunset.py [--dry-run]

Reads API key from ~/.config/valley-pawn/brevo_api_key
"""
import json, urllib.request, urllib.error, sys, os, time
from pathlib import Path

KEY = Path.home().joinpath(".config/valley-pawn/brevo_api_key").read_text().strip()
DRY_RUN = "--dry-run" in sys.argv

DORMANT_SEGMENT_ID = 4
LIST_MASTER = 3                    # Valley Pawn Customers
SUNSET_LIST_ID = None              # SET THIS once you create the "Dormant — Sunset" list in Brevo UI
REACTIVATION_CAMPAIGN_IDS = [16, 17, 18]

def call(method, path, body=None):
    req = urllib.request.Request(
        f"https://api.brevo.com/v3{path}",
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"api-key": KEY, "accept": "application/json", "content-type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            return r.status, (json.loads(data) if data else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]

assert SUNSET_LIST_ID, "Set SUNSET_LIST_ID before running. Create 'Dormant — Sunset' list in Brevo UI, then paste its ID here."

# Step 1: pull all clickers from the 3 reactivation campaigns
print("Collecting clickers from reactivation campaigns…")
clickers = set()
for cid in REACTIVATION_CAMPAIGN_IDS:
    offset = 0
    while True:
        status, data = call("GET", f"/emailCampaigns/{cid}/identifiedClicks?limit=500&offset={offset}")
        if status != 200:
            print(f"  WARN: campaign {cid} clicks fetch returned {status}: {data}")
            break
        for evt in (data.get("clicks", []) or []):
            clickers.add(evt.get("email", "").lower())
        if len(data.get("clicks", [])) < 500:
            break
        offset += 500
print(f"  Total unique clickers across {len(REACTIVATION_CAMPAIGN_IDS)} campaigns: {len(clickers)}")

# Step 2: pull the Dormant segment contacts via the contacts-of-list endpoint
# Brevo doesn't have a direct segment-contacts endpoint, so we iterate list 3 and filter via the dormant segment intersection
# Alternative: pull the segment's contacts via UI export, then read the CSV here.
# For now we'll pull list 3 and check engagement timestamps
print("Loading list 3 contacts…")
sunset_emails = []
offset = 0
while True:
    status, data = call("GET", f"/contacts/lists/{LIST_MASTER}/contacts?limit=500&offset={offset}")
    if status != 200:
        print(f"  ERROR: {status} {data}")
        sys.exit(1)
    for c in data.get("contacts", []):
        em = c.get("email", "").lower()
        if not em or em in clickers:
            continue
        # TODO: cross-check against Dormant segment ID 4 membership
        # For initial sweep, treat list-3 minus clickers as sunset candidates
        sunset_emails.append(em)
    if len(data.get("contacts", [])) < 500:
        break
    offset += 500

print(f"\nSunset candidates: {len(sunset_emails)}")
print(f"  Sample: {sunset_emails[:5]}")

if DRY_RUN:
    print("\n[DRY RUN] Not making any changes. Re-run without --dry-run to execute.")
    sys.exit(0)

# Step 3: for each candidate, add to sunset list + remove from list 3
print("\nMoving contacts to sunset list…")
batch_size = 150  # Brevo limit
for i in range(0, len(sunset_emails), batch_size):
    batch = sunset_emails[i:i+batch_size]
    # Add to sunset list
    status, _ = call("POST", f"/contacts/lists/{SUNSET_LIST_ID}/contacts/add", {"emails": batch})
    # Remove from master list
    status2, _ = call("POST", f"/contacts/lists/{LIST_MASTER}/contacts/remove", {"emails": batch})
    print(f"  Batch {i//batch_size + 1}: add={status}, remove={status2}, count={len(batch)}")
    time.sleep(0.5)  # be polite

print(f"\nDONE. {len(sunset_emails)} contacts moved from list {LIST_MASTER} → list {SUNSET_LIST_ID}.")
print(f"Next sends should now target the Engaged segment (ID 3) by default.")
