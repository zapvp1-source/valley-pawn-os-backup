#!/usr/bin/env python3
"""Rule 12 verification for the 2026-09-09 comedy/story lane run.

Diffs the plan against Publer's ACTUAL scheduled list (explicit from/to via
live_scheduled). A manifest is not evidence.

ALSO CHECKS FOR DUPLICATES. During this run two vp_deal_reel_publish processes
were briefly alive at the same time (the first osascript invocation timed out at
the MCP layer but its child kept running, then a second was started). The extra
process was killed ~25s in, but a race window existed, so every target is counted
rather than just presence-checked: count != 1 is a failure here.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from vp_deal_reel_publish import ReelPublisher, _text_of  # noqa: E402

ACC = {v["publer_id"]: k
       for k, v in json.loads((ROOT / "publer_accounts.json").read_text())["accounts"].items()}

plan = json.loads((ROOT / "manifests" / "comedy_reels_2026-09-09.json").read_text())
p = ReelPublisher()
live = p.live_scheduled(days_ahead=14)
print(f"live scheduled posts pulled: {len(live)}\n")

rows = []
found = missing = dupes = 0
for it in plan["items"]:
    for t in it["targets"]:
        marker = t["caption"][:45]
        hits = [x for x in live
                if _text_of(x).startswith(marker)
                and ACC.get(str(x.get("account_id"))) == t["account"]]
        n = len(hits)
        if n == 1:
            found += 1
            verdict = "YES"
        elif n == 0:
            missing += 1
            verdict = "*** NOT FOUND ***"
        else:
            dupes += 1
            verdict = f"*** DUPLICATE x{n} ***"
        rows.append((it["id"][:36], t["account"], t["scheduled_at"][:16], verdict))

for r in rows:
    print("%-36s %-13s %-17s %s" % r)

# Belt and braces: any of OUR video captions appearing more than once anywhere.
own = [_text_of(x)[:45] for x in live
       for it in plan["items"] for t in it["targets"]
       if _text_of(x).startswith(t["caption"][:45])]
extra = {k: v for k, v in Counter(own).items() if v > 1}

print()
print("LIVE-VERIFIED %d/%d   missing=%d   duplicates=%d"
      % (found, len(rows), missing, dupes))
if extra:
    print("DUPLICATE CAPTION MARKERS:", json.dumps(extra, indent=1))
sys.exit(0 if (missing == 0 and dupes == 0) else 1)
