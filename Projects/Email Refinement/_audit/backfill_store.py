#!/usr/bin/env python3
"""Backfill the STORE attribute, which is what the weekly email's personalised
"YOUR VALLEY PAWN STORE" block keys off.

The block is `{% if contact.STORE == "Culpeper" %} ... {% elif ... %}` with a
correct {% else %} fallback. The Liquid is fine. It renders blank-ish for anyone
whose STORE is empty — which the audit measured at 99 of 194 on the engaged list.

The Chekkit archive could not fix these: those contacts predate the Chekkit flow
and appear in no per-store source. Two signals remain:

  1. Brevo list 12 "Valley Pawn - Lexington (Store List)" (~2,647 contacts)
     -> STORE = Lexington for any member still missing it.
  2. Per-store SEGMENTS 7-11 ("Store: Culpeper" etc). These were built 2026-07-22
     from click behaviour on store-specific links, so membership is a genuine
     revealed preference for that store. Segments cannot be read back through the
     API on this plan, so this path is only usable from the UI — noted here so a
     future session with a browser session doesn't miss it.

Only (1) is executable headlessly today.
"""
import json, urllib.request, urllib.parse, os, time, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv
LEX_LIST = 12
STORE_VALUE = "Lexington"   # must match the Liquid branch exactly


def req(method, path, body=None, tries=7):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                   headers={"api-key": KEY,
                                            "Content-Type": "application/json",
                                            "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + a * 4); continue
            return e.code, e.read().decode()
    return 429, "rate limited"


print(f"reading list {LEX_LIST} ...")
members, offset = [], 0
while True:
    st, d = req("GET", f"/contacts/lists/{LEX_LIST}/contacts?limit=500&offset={offset}")
    if st != 200:
        print(f"  page fail offset={offset} status={st}"); break
    batch = d.get("contacts", [])
    members.extend(batch)
    if len(batch) < 500:
        break
    offset += 500
    time.sleep(0.4)

print(f"  members: {len(members)}")

todo = []
for c in members:
    if not c.get("email") or c.get("emailBlacklisted"):
        continue
    a = c.get("attributes") or {}
    if not str(a.get("STORE") or "").strip():
        todo.append(c["email"])

print(f"  blacklisted/no-email skipped : {len(members) - sum(1 for c in members if c.get('email') and not c.get('emailBlacklisted'))}")
print(f"  missing STORE, will set to '{STORE_VALUE}': {len(todo)}")

if DRY:
    print("\nDRY RUN - pass --apply. Sample:", todo[:5])
    sys.exit(0)

ok = fail = 0
for n, em in enumerate(todo, 1):
    ident = urllib.parse.quote(em, safe="")
    st, res = req("PUT", f"/contacts/{ident}", {"attributes": {"STORE": STORE_VALUE}})
    if st in (200, 204):
        ok += 1
    else:
        fail += 1
    if n % 250 == 0:
        print(f"  {n}/{len(todo)} ok={ok} fail={fail}", flush=True)
    time.sleep(0.12)

print(f"\nDONE  set STORE on {ok} contacts, {fail} failed")
