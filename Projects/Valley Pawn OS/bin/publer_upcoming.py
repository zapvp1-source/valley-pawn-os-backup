#!/usr/bin/env python3
"""publer_upcoming.py [--hours 48] — READ-ONLY. Prints every SCHEDULED Publer post in the next N hours as JSON lines
(publer_id, account_key, scheduled_at, text). Used by the daily social fact-check (2026-10-21)."""
import argparse, json, os, sys, datetime as dt
RSM = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects")) + "/Refine Social Media"
sys.path.insert(0, RSM); os.chdir(RSM)
os.environ.setdefault("VP_SOCIAL_LEDGER", "/tmp/vp_upcoming_ledger.sqlite")
from vp_social import reader, config  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--hours", type=int, default=48); a = ap.parse_args()
now = dt.datetime.now(config.TZ); end = now + dt.timedelta(hours=a.hours)
for r in reader.fetch_window(now.date().isoformat(), end.date().isoformat(), states=("scheduled",)):
    t = dt.datetime.fromisoformat(r["scheduled_at"]) if r["scheduled_at"] else None
    if t and now <= t <= end:
        print(json.dumps({"publer_id": r["publer_id"], "account_key": r["account_key"], "scheduled_at": r["scheduled_at"], "text": r["text"]}))
