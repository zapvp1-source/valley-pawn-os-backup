#!/usr/bin/env python3
"""Remove the two DIAGNOSTIC posts from the Brand FB page before they can publish.
DELETE /posts/{id} 404'd on the id returned by GET /posts, so this dumps the full
post object to find the field the delete endpoint actually wants."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient, PublerError  # noqa: E402

p = PublerClient()
data = p.get("/posts", params={"state": "scheduled", "from": "2026-08-24",
                               "to": "2026-08-25", "limit": "100"})
posts = data.get("posts", data) if isinstance(data, dict) else (data or [])
targets = [x for x in posts if "DIAGNOSTIC" in (x.get("text") or "")]
print(f"{len(targets)} diagnostic posts found")
for t in targets:
    print(json.dumps(t, indent=2)[:1800])
    print("-" * 60)

for t in targets:
    for field in ("id", "_id", "post_id", "group_id"):
        val = t.get(field)
        if not val:
            continue
        if isinstance(val, dict):
            val = val.get("$oid") or val.get("id")
        for ep in (f"/posts/{val}", f"/posts/{val}/delete"):
            try:
                p.delete(ep)
                print(f"DELETED via {ep}")
                break
            except PublerError as e:
                print(f"  {ep} -> {str(e)[:90]}")
        else:
            continue
        break
