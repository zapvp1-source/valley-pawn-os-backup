#!/usr/bin/env python3
"""Rule-12 check: what is ACTUALLY scheduled in Publer right now, Aug 31 - Sep 20.

Uses explicit from/to on GET /posts — without them Publer silently caps at ~15.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media")
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient  # noqa: E402

acc = json.loads((ROOT / "publer_accounts.json").read_text())["accounts"]
name_by_id = {v["publer_id"]: k for k, v in acc.items()}

p = PublerClient()
data = p.get("/posts", params={"from": "2026-08-31", "to": "2026-09-20",
                               "state": "scheduled", "limit": "200"})
posts = data.get("posts", data) if isinstance(data, dict) else data
print("TOTAL", len(posts))

by_day = Counter()
for x in posts:
    when = (x.get("scheduled_at") or x.get("scheduledAt") or "")[:10]
    ids = x.get("accounts") or x.get("account_ids") or []
    if isinstance(ids, list):
        ids = [i.get("id", i) if isinstance(i, dict) else i for i in ids]
    who = ",".join(name_by_id.get(i, str(i)[:8]) for i in ids)
    txt = (x.get("text") or x.get("content") or "")[:60].replace("\n", " ")
    by_day[when] += 1
    print(f"{when}  {who:28s} {txt}")

print("\n--- per day ---")
for d in sorted(by_day):
    print(d, by_day[d])
