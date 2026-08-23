#!/usr/bin/env python3
"""Verify comedy-reel posts against Publer's REAL scheduled list (Rule 12 — never a
run record, never our own manifest). Explicit from/to because GET /posts silently
caps at ~15 without it."""
import json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient

p = PublerClient()
id_to_key = {v["publer_id"]: k for k, v in p.accounts.items()}
today = dt.date.today().isoformat()
end = (dt.date.today() + dt.timedelta(days=3)).isoformat()

rows = []
for state in ("scheduled", "published", "failed"):
    data = p.get("/posts", params={"state": state, "from": today, "to": end, "limit": "100"})
    posts = data.get("posts", data) if isinstance(data, dict) else (data or [])
    for post in posts:
        acct = id_to_key.get(str(post.get("account_id", "")), post.get("account_id"))
        rows.append({
            "state": state,
            "account": acct,
            "scheduled_at": post.get("scheduled_at"),
            "type": post.get("type") or post.get("post_type"),
            "text": (post.get("text") or "")[:70].replace("\n", " "),
            "id": post.get("id"),
        })

rows.sort(key=lambda r: str(r["scheduled_at"]))
print(f"TOTAL {len(rows)} posts on Publer {today}..{end}\n")
for r in rows:
    print(f"{r['state']:<10} {str(r['scheduled_at'])[:19]:<20} {str(r['account']):<14} "
          f"{str(r['type']):<8} {r['text']}")
Path(ROOT / "manifests" / "comedy_reels_2026-08-22_publer_verify.json").write_text(
    json.dumps(rows, indent=2))
