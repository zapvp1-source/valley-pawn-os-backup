#!/usr/bin/env python3
"""Verify the 2026-08-26 comedy-reel posts against Publer's LIVE scheduled list
(Rule 12 — never trust the local manifest). Matches on the exact media IDs uploaded
by publish_comedy_reels_2026-08-26.py, so a same-slot post from another lane can't
be mistaken for ours."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from publer_client import PublerClient

MEDIA = json.loads((ROOT / "manifests" / "comedy_reels_2026-08-26_results.json").read_text())["media"]
WANT = {v["id"]: k for k, v in MEDIA.items()}
WANT_NAMES = {Path(v["path"]).name: k for k, v in MEDIA.items()}

p = PublerClient()
by_id = {v["publer_id"]: k for k, v in p.accounts.items()}
res = p.get("/posts", params={"state": "scheduled", "from": "2026-08-27",
                             "to": "2026-08-30", "limit": "200"})
posts = res.get("posts", res) if isinstance(res, dict) else (res or [])
print("scanned:", len(posts))
hits = []
for post in posts:
    blob = json.dumps(post)
    bit = next((k for mid, k in WANT.items() if mid in blob), None) \
        or next((k for nm, k in WANT_NAMES.items() if nm in blob), None)
    if not bit:
        continue
    acc = post.get("account_id") or (post.get("account") or {}).get("id") or "?"
    hits.append((bit, by_id.get(acc, acc),
                 str(post.get("scheduled_at") or post.get("due_at")),
                 (post.get("text") or "")[:55].replace("\n", " "),
                 post.get("id") or post.get("_id")))
print(f"\nCOMEDY-REEL POSTS LIVE ON PUBLER: {len(hits)}")
for h in sorted(hits, key=lambda x: x[2]):
    print(f"  {h[2][:19]}  {h[1]:<13} {h[0]:<9} {h[4]}  {h[3]}")
