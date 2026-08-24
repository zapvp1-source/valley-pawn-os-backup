#!/usr/bin/env python3
"""Wire the rotating wave lists into the Sep-Dec drafts.

Ramp plan: hello@thevalleypawn.com is a brand-new sending identity, so the first
two sends (Aug 27, Sep 3) stay on the engaged list alone as clean warm-up. From
Sep 10 every weekly send goes to engaged + seeds + ONE wave, rotating A-E, so each
dormant contact hears from us every 5 weeks at roughly today's total volume --
but in 2.4k sends instead of one 11k spike.
"""
import json, urllib.request, os, time, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv

ENGAGED, SEEDS = 7, 10
WAVE_LIST = {"A": 14, "B": 15, "C": 16, "D": 17, "E": 18}

# campaign id -> (date label, wave letter)
PLAN = [
    (54, "September 10", "A"), (55, "September 17", "B"), (56, "September 24", "C"),
    (57, "October 1",    "D"), (58, "October 8",    "E"), (59, "October 15",   "A"),
    (60, "October 22",   "B"), (61, "October 29",   "C"), (62, "November 5",   "D"),
    (63, "November 12",  "E"), (64, "November 19",  "A"), (65, "November 26",  "B"),
    (66, "December 3",   "C"), (67, "December 10",  "D"), (68, "December 17",  "E"),
    (69, "December 24",  "A"), (70, "December 31",  "B"),
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


for cid, label, wave in PLAN:
    lists = [ENGAGED, SEEDS, WAVE_LIST[wave]]
    if DRY:
        print(f"[dry] {cid}  {label:14} wave {wave} -> lists {lists}")
        continue
    st, res = req("PUT", f"/emailCampaigns/{cid}", {"recipients": {"listIds": lists}})
    time.sleep(0.6)
    st2, chk = req("GET", f"/emailCampaigns/{cid}")
    got = chk.get("recipients", {}).get("lists")
    ok = got == lists
    print(f"{'OK  ' if ok else 'CHECK'} {cid}  {label:14} wave {wave}  PUT {st}  now={got}")
    time.sleep(0.6)

print("\nDRY RUN — pass --apply" if DRY else "\nDONE")
