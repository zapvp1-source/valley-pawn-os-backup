#!/usr/bin/env python3
"""Widen reach from Oct 1 onward: 2 waves per send instead of 1.

Decision (Joshua asked for a call on how wide to go, "a lot of people not
getting emails"): thevalleypawn.com / hello@thevalleypawn.com is a brand-new
sending identity as of 2026-08-23. Sending to the full 11k dormant file on
week one of a new domain risks the exact deliverability collapse the audit
just fixed. So:

  - Sep 10, 17, 24 (campaigns 54-56): stay single-wave. Clean warm-up on the
    new sender while we watch bounce/complaint trend on the efficiency log.
  - Oct 1 onward (57-70): double up to 2 waves per send. Every dormant
    contact then hears from us roughly every 2.5 weeks instead of every 5,
    while total per-send volume stays modest (~4,300 vs an 11k spike).

Pairing pattern: each send gets its already-assigned wave plus the next one
in the A-B-C-D-E cycle, so coverage stays even and rolls forward continuously
rather than resetting.
"""
import json, urllib.request, os, time, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv

ENGAGED, SEEDS = 7, 10
WAVE_LIST = {"A": 14, "B": 15, "C": 16, "D": 17, "E": 18}
CYCLE = ["A", "B", "C", "D", "E"]

# campaign id -> (date label, primary wave already assigned)
WIDEN_FROM = [
    (57, "October 1",   "D"), (58, "October 8",    "E"), (59, "October 15",   "A"),
    (60, "October 22",  "B"), (61, "October 29",   "C"), (62, "November 5",   "D"),
    (63, "November 12", "E"), (64, "November 19",  "A"), (65, "November 26",  "B"),
    (66, "December 3",  "C"), (67, "December 10",  "D"), (68, "December 17",  "E"),
    (69, "December 24", "A"), (70, "December 31",  "B"),
]


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


for cid, label, primary in WIDEN_FROM:
    nxt = CYCLE[(CYCLE.index(primary) + 1) % 5]
    lists = [ENGAGED, SEEDS, WAVE_LIST[primary], WAVE_LIST[nxt]]
    if DRY:
        print(f"[dry] {cid}  {label:14} waves {primary}+{nxt} -> lists {lists}")
        continue
    st, res = req("PUT", f"/emailCampaigns/{cid}", {"recipients": {"listIds": lists}})
    time.sleep(0.6)
    st2, chk = req("GET", f"/emailCampaigns/{cid}")
    got = chk.get("recipients", {}).get("lists")
    ok = got == lists
    print(f"{'OK  ' if ok else 'CHECK'} {cid}  {label:14} waves {primary}+{nxt}  PUT {st}  now={got}")
    time.sleep(0.6)

print("\nDRY RUN — pass --apply" if DRY else "\nDONE")
