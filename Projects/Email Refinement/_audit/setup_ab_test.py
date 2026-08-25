#!/usr/bin/env python3
"""First A/B test in the account's history.

The 2026-08-22 audit found abTesting=false and sendAtBestTime=false on all 41
campaigns ever created - not one hypothesis has ever been tested, so we have
zero evidence about what actually moves this audience.

Start with the highest-leverage hypothesis from the audit: subject lines carry
no number, no deadline, and no concrete value proposition ("What's new at Valley
Pawn Roanoke"), while the logo out-clicks every offer on nearly every send -
which is what you'd expect when the offer isn't compelling enough to beat idle
curiosity.

TEST 1 (Sep 10, campaign 54, ~2,300 recipients across engaged + wave A):
  A: generic/current style     -> "What we stock at our Peters Creek Road store"
  B: concrete + numbered       -> "5 things worth the drive to our Roanoke store"

winnerCriteria is CLICK, not open. Per the audit, Apple MPP inflates opens
(481 of 624 "opens" on the Aug blast were MPP prefetches), so optimising on
opens would be optimising on bots.
"""
import json, urllib.request, os, time, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv


def req(method, path, body=None, tries=6):
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


TESTS = [
    {
        "id": 54,
        "subjectA": "What we stock at our Peters Creek Road store",
        "subjectB": "5 things worth the drive to our Roanoke store",
        "hypothesis": "concrete number + benefit beats generic 'what's new'",
    },
]

for t in TESTS:
    cid = t["id"]
    st, cur = req("GET", f"/emailCampaigns/{cid}")
    if st != 200:
        print(f"{cid}: FETCH FAIL {st}"); continue
    print(f"=== {cid} {cur['name']}")
    print(f"    current subject: {cur.get('subject')}")
    print(f"    recipients: {cur['recipients'].get('lists')}")
    print(f"    hypothesis: {t['hypothesis']}")

    payload = {
        "abTesting": True,
        "subjectA": t["subjectA"],
        "subjectB": t["subjectB"],
        "splitRule": 50,          # 50% into the test (25% A / 25% B), rest gets winner
        "winnerCriteria": "click",  # NOT open - MPP makes opens unreliable
        "winnerDelay": 4,           # hours before the remainder goes out
    }
    if DRY:
        print(f"    [dry] would set: {json.dumps(payload)}")
        continue

    st2, res = req("PUT", f"/emailCampaigns/{cid}", payload)
    print(f"    PUT -> {st2} {res if st2 >= 300 else 'OK'}")
    time.sleep(1)

    st3, chk = req("GET", f"/emailCampaigns/{cid}")
    print(f"    VERIFY abTesting={chk.get('abTesting')} "
          f"A={chk.get('subjectA')!r} B={chk.get('subjectB')!r} "
          f"split={chk.get('splitRule')} criteria={chk.get('winnerCriteria')} "
          f"delay={chk.get('winnerDelay')}")

print("\nDRY RUN - pass --apply" if DRY else "\nDONE")
