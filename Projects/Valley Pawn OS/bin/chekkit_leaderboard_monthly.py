#!/usr/bin/env python3
"""chekkit_leaderboard_monthly.py — READ-ONLY (2026-10-24). GET /v1/leaderboard per store per calendar month from
2025-01 to now: invitationsSent, reviews.total, averageRating. Prints a table + writes fleet/state/chekkit_leaderboard_monthly.json."""
import sys, os, json, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "state", "chekkit_leaderboard_monthly.json")
today = dt.date.today(); res = {}
for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
    y, m = 2025, 1
    while (y, m) <= (today.year, today.month):
        a = dt.date(y, m, 1); b = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)); b = min(b, today)
        try:
            loc = (ck.get(code, "/v1/leaderboard?from=%s&to=%s" % (a, b)) or {}).get("location") or {}
            r = loc.get("reviews") or {}
            res.setdefault(code, {})["%d-%02d" % (y, m)] = {"inv": loc.get("invitationsSent"), "rev": r.get("total"), "avg": r.get("averageRating"), "conv": loc.get("conversations") if not isinstance(loc.get("conversations"), (list, dict)) else None}
        except Exception as e:
            res.setdefault(code, {})["%d-%02d" % (y, m)] = {"err": str(e)[:60]}
        time.sleep(0.4); m += 1
        if m == 13: y, m = y + 1, 1
json.dump(res, open(OUT, "w"), indent=1)
months = sorted({k for v in res.values() for k in v})
for mo in months:
    inv = sum((res[c].get(mo, {}).get("inv") or 0) for c in res); rev = sum((res[c].get(mo, {}).get("rev") or 0) for c in res)
    print(mo, "invites", inv, "reviews", rev)
