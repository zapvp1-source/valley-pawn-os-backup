#!/usr/bin/env python3
"""chekkit_leaderboard_ytd.py — READ-ONLY (2026-10-23). GET /v1/leaderboard per store for 2026-01-01..today and prints
the location-level totals (reviews, invitations, clicks). For the November team deck."""
import sys, os, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck
for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
    try:
        b = ck.get(code, "/v1/leaderboard?from=2026-01-01&to=%s" % dt.date.today().isoformat())
        loc = b.get("location") or {}
        print(code, json.dumps({k: v for k, v in loc.items() if not isinstance(v, (list, dict)) or k in ("reviews", "invitations", "totals")})[:700])
        print(code, "KEYS", list(b.keys()), list(loc.keys()))
    except Exception as e:
        print(code, "ERR", e)
