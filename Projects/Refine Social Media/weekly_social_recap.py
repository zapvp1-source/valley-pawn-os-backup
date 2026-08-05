#!/usr/bin/env python3
"""
Weekly Social Media Recap for Valley Pawn.

NET-NEW script (Rule #4 additive) — does not touch publer_weekly_digest.py,
friday_close_engagement.py, or any existing digest/analytics script.

Purpose: answer \"what actually posted across our socials this week\" as a
team-visible Slack recap (#social-media), separate from:
  - vp-publer-analytics-friday -> engagement digest, DM to Joshua only
  - vp-content-batch-postflight -> publish-verification DM to Joshua only
This script is a pure read of Publer's /posts?state=published (Rule 12 —
verify against actual output, not a manifest or run record).

Usage: python3 weekly_social_recap.py [--days 7]
Prints a Slack mrkdwn-formatted recap to stdout, prefixed with \"RECAP:\"
on its own start marker line so the calling skill can grab everything
after it.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from publer_client import PublerClient, PublerError  # noqa: E402

PLATFORM_LABEL = {
    "facebook": "Facebook",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "twitter": "X/Twitter",
    "gmb": "Google Business Profile",
    "wordpress_oauth": "Blog (WordPress)",
    "wordpress": "Blog (WordPress)",
    "google_business": "Google Business Profile",
}


def load_account_index(client: PublerClient) -> dict[str, dict]:
    """account_id -> {store_key, provider, name}"""
    idx = {}
    for store_key, meta in client.accounts.items():
        pid = meta.get("publer_id")
        if pid:
            idx[pid] = {
                "store_key": store_key,
                "provider": meta.get("provider", "unknown"),
                "name": meta.get("name", store_key),
            }
    return idx


def fetch_recent_published(client: PublerClient, days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_posts: list[dict] = []
    for state in ("published",):
        try:
            posts = client.list_posts(state=state, limit=200)
        except PublerError as e:
            print(f"WARN: list_posts({state}) failed: {e}", file=sys.stderr)
            posts = []
        all_posts.extend(posts)
    recent = []
    for post in all_posts:
        ts = post.get("scheduled_at") or post.get("updated_at")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt >= cutoff:
            post["_dt"] = dt
            recent.append(post)
    return recent


def build_recap(days: int = 7) -> str:
    client = PublerClient()
    acct_idx = load_account_index(client)
    posts = fetch_recent_published(client, days)

    by_store: dict[str, list[dict]] = defaultdict(list)
    by_platform: dict[str, int] = defaultdict(int)
    unmapped = 0

    for post in posts:
        meta = acct_idx.get(post.get("account_id"))
        if not meta:
            unmapped += 1
            continue
        by_store[meta["store_key"]].append(post)
        label = PLATFORM_LABEL.get(meta["provider"], meta["provider"])
        by_platform[label] += 1

    total = len(posts)
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%b %-d")
    end = datetime.now(timezone.utc).strftime("%b %-d")

    lines = []
    lines.append(f"*Weekly Social Recap — {start} to {end}*")
    lines.append(f"{total} posts published across all Valley Pawn channels this week.")
    lines.append("")
    lines.append("*By platform:*")
    if by_platform:
        for label, count in sorted(by_platform.items(), key=lambda kv: -kv[1]):
            lines.append(f"\u2022 {label}: {count}")
    else:
        lines.append("\u2022 No published posts found in this window.")
    lines.append("")
    lines.append("*By store/page:*")
    store_order = ["Brand", "Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke",
                   "BrandIG", "BrandTikTok", "BrandTwitter",
                   "GBP_Culpeper", "GBP_Waynesboro", "GBP_Harrisonburg", "GBP_Lexington", "GBP_Roanoke"]
    seen = set()
    for key in store_order:
        if key in by_store:
            lines.append(f"\u2022 {key}: {len(by_store[key])}")
            seen.add(key)
    for key, items in by_store.items():
        if key not in seen:
            lines.append(f"\u2022 {key}: {len(items)}")
    if unmapped:
        lines.append(f"\u2022 (unmapped account_id, {unmapped} posts — account may be new/renamed)")

    print("RECAP_START")
    print("\n".join(lines))
    print("RECAP_END")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()
    build_recap(days=args.days)
