#!/usr/bin/env python3
import json
from publer_client import PublerClient

c = PublerClient()
for state in ["published", "scheduled"]:
    posts = c.list_posts(state=state, limit=100)
    print(state, "count:", len(posts))
    for p in posts:
        sa = str(p.get("scheduled_at") or p.get("published_at") or "")
        blob = json.dumps(p, default=str)
        if "2026-07-23T16" in sa or "six days" in blob or "6 days a week" in blob:
            print(state, "|", p.get("id"), "|", sa[:19])
            print("   full:", blob[:700])
