#!/usr/bin/env python3
"""Rule 12 verification: diff the 2026-08-31 deal-reel plan against Publer's ACTUAL
scheduled list (explicit from/to via live_scheduled). A manifest is not evidence."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from vp_deal_reel_publish import ReelPublisher, _text_of  # noqa: E402

ACC = {v["publer_id"]: k
       for k, v in json.loads((ROOT / "publer_accounts.json").read_text())["accounts"].items()}

plan = json.loads((ROOT / "manifests" / "deal_reels_2026-08-31.json").read_text())
p = ReelPublisher()
live = p.live_scheduled(days_ahead=14)
print(f"live scheduled posts pulled: {len(live)}\n")

found = missing = 0
rows = []
for it in plan["items"]:
    for t in it["targets"]:
        marker = t["caption"][:45]
        hit = [x for x in live
               if _text_of(x).startswith(marker)
               and ACC.get(str(x.get("account_id"))) == t["account"]]
        ok = bool(hit)
        found += ok
        missing += (not ok)
        rows.append((it["id"], t["account"], t["scheduled_at"][:16],
                     "YES" if ok else "*** NOT FOUND ***"))

for r in rows:
    print("%-38s %-13s %-17s %s" % r)
print()
print("LIVE-VERIFIED %d/%d   missing=%d" % (found, found + missing, missing))
