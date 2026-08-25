#!/usr/bin/env python3
"""Verify attribute fill rates against output, not against the import's own
reported counts (Rule 12). Samples the real file at several offsets."""
import json, urllib.request, os, time

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"


def req(path, tries=7):
    for a in range(tries):
        r = urllib.request.Request(BASE + path, headers={"api-key": KEY,
                                                         "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + a * 4); continue
            return e.code, e.read().decode()
    return 429, "rate limited"


tot = fn = ln = sms = store = 0
for off in (0, 2000, 4000, 6000, 8000, 10000, 12000):
    st, d = req(f"/contacts?limit=500&offset={off}")
    if st != 200:
        print(f"  offset {off}: status {st}"); continue
    for c in d.get("contacts", []):
        if not c.get("email"):
            continue
        a = c.get("attributes", {}) or {}
        tot += 1
        if str(a.get("FIRSTNAME") or "").strip(): fn += 1
        if str(a.get("LASTNAME") or "").strip():  ln += 1
        if str(a.get("SMS") or "").strip():       sms += 1
        if str(a.get("STORE") or "").strip():     store += 1
    time.sleep(0.4)

print(f"sampled {tot} contacts across the file")
if tot:
    print(f"  FIRSTNAME : {fn:5}  {100*fn/tot:5.1f}%   (audit baseline ~0.1%)")
    print(f"  LASTNAME  : {ln:5}  {100*ln/tot:5.1f}%")
    print(f"  SMS/phone : {sms:5}  {100*sms/tot:5.1f}%   (audit baseline 0%)")
    print(f"  STORE     : {store:5}  {100*store/tot:5.1f}%   (audit baseline ~54%)")

# engaged list specifically - this is the audience that actually gets the weekly
st, d = req("/contacts/lists/7/contacts?limit=500")
if st == 200:
    cs = [c for c in d.get("contacts", []) if c.get("email")]
    if cs:
        f2 = sum(1 for c in cs if str((c.get("attributes") or {}).get("FIRSTNAME") or "").strip())
        s2 = sum(1 for c in cs if str((c.get("attributes") or {}).get("STORE") or "").strip())
        p2 = sum(1 for c in cs if str((c.get("attributes") or {}).get("SMS") or "").strip())
        print(f"\nEngaged list (7) - {len(cs)} contacts, the weekly audience:")
        print(f"  FIRSTNAME : {f2:4}  {100*f2/len(cs):5.1f}%   (was 1 of 194)")
        print(f"  STORE     : {s2:4}  {100*s2/len(cs):5.1f}%   (was 95 of 194 - the blank"
              f" personalised block)")
        print(f"  SMS/phone : {p2:4}  {100*p2/len(cs):5.1f}%")
