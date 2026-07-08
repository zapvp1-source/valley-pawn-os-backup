#!/usr/bin/env python3
"""
Valley Pawn — Friday Close Engagement Pull

Reads engagement metrics for the past 7 days across all 6 Valley Pawn Facebook
Pages via the Meta Graph API, aggregates per-post and per-Page totals, and
writes a Markdown report.

Uses the same long-lived Page Access Tokens already saved by the facebook-post
skill at:
  ~/Library/.../claude-hostloop-plugins/.../skills/facebook-post/data/tokens.json

REQUIRES these permissions on the app's tokens (App Review must approve before
the deeper insights fields populate; engagement counts work at standard tier):
  - pages_read_engagement      ← post-level reactions/comments/shares
  - read_insights              ← post_impressions, post_reach, engaged_users

USAGE:
  python3 friday_close_engagement.py
  python3 friday_close_engagement.py --days 14
  python3 friday_close_engagement.py --out /path/to/report.md

The script degrades gracefully — if a permission isn't yet granted, the
corresponding column is left blank and a warning is appended to the report.
That way you can run it TODAY against the public-engagement fields and it'll
start surfacing the deeper Insights columns automatically the moment Meta
approves App Review.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# --------- locations ---------
TOKENS_PATH = Path(
    os.path.expanduser(
        "~/Library/Application Support/Claude"
    )
)
# Try the known hostloop-plugins location first; fall back to a copy in workspace
CANDIDATE_TOKEN_PATHS = [
    Path(
        "/var/folders/6k/_z_8cvwd09v5v4cglg57t9_c0000gn/T/"
        "claude-hostloop-plugins/8d3bfa4a5124690e/skills/facebook-post/"
        "data/tokens.json"
    ),
    Path.home() / "Documents/Claude/Projects/Refine Social Media/tokens.json",
]

API_VERSION = "v25.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"

PAGE_KEYS = ["Lexington", "Waynesboro", "Harrisonburg", "Culpeper", "Roanoke", "Brand"]

# Insights metrics we want at the post level (read_insights perm required)
POST_INSIGHTS = ["post_impressions", "post_reach", "post_engaged_users"]


# --------- token loading ---------
def load_tokens():
    for p in CANDIDATE_TOKEN_PATHS:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    print(
        "ERROR: tokens.json not found. Looked in:\n  "
        + "\n  ".join(str(p) for p in CANDIDATE_TOKEN_PATHS),
        file=sys.stderr,
    )
    sys.exit(1)


# --------- Graph API helpers ---------
def gx(url, params=None, retries=3):
    """GET with retry. Returns parsed JSON or {'error': ...}."""
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params or {}, timeout=20)
            if r.status_code == 200:
                return r.json()
            last_err = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
        except requests.RequestException as e:
            last_err = {"exception": str(e)}
        time.sleep(1 + attempt)
    return {"error": last_err}


def fetch_posts(page_id, token, since_unix):
    """Pull all posts published since `since_unix`. Page through if needed."""
    url = f"{BASE}/{page_id}/posts"
    params = {
        "access_token": token,
        "since": since_unix,
        "limit": 100,
        "fields": (
            "id,created_time,message,permalink_url,"
            "reactions.summary(true).limit(0),"
            "comments.summary(true).limit(0),"
            "shares"
        ),
    }
    posts = []
    while True:
        data = gx(url, params=params)
        if "error" in data and "data" not in data:
            return posts, data["error"]
        posts.extend(data.get("data", []))
        next_url = data.get("paging", {}).get("next")
        if not next_url:
            break
        url = next_url
        params = None
    return posts, None


def fetch_post_insights(post_id, token):
    """Pull post-level insights — needs read_insights perm. Returns dict or {}."""
    url = f"{BASE}/{post_id}/insights"
    params = {
        "access_token": token,
        "metric": ",".join(POST_INSIGHTS),
    }
    data = gx(url, params=params)
    out = {}
    if "data" in data:
        for entry in data["data"]:
            name = entry.get("name")
            values = entry.get("values", [])
            if values and name:
                out[name] = values[0].get("value")
    return out


# --------- per-page work ---------
def summarize_page(label, cfg, since_unix, include_insights):
    """Returns {label, page_id, posts: [...post dicts...], page_warnings: [...]}"""
    page_id = cfg["page_id"]
    token = cfg["access_token"]

    posts, err = fetch_posts(page_id, token, since_unix)
    warnings = []
    if err:
        warnings.append(f"posts fetch error: {err}")

    enriched = []
    for p in posts:
        row = {
            "id": p.get("id"),
            "created_time": p.get("created_time"),
            "permalink_url": p.get("permalink_url"),
            "message": (p.get("message") or "").splitlines()[0][:120],
            "reactions": (p.get("reactions") or {}).get("summary", {}).get("total_count", 0),
            "comments": (p.get("comments") or {}).get("summary", {}).get("total_count", 0),
            "shares": (p.get("shares") or {}).get("count", 0),
        }
        if include_insights:
            ins = fetch_post_insights(p["id"], token)
            row["impressions"] = ins.get("post_impressions")
            row["reach"] = ins.get("post_reach")
            row["engaged_users"] = ins.get("post_engaged_users")
            if not ins:
                # If insights returns empty for the first post, warn once and stop trying.
                warnings.append(
                    "insights returned empty — read_insights perm likely not approved yet"
                )
                include_insights = False
        enriched.append(row)

    return {
        "label": label,
        "page_id": page_id,
        "posts": enriched,
        "warnings": warnings,
    }


# --------- report rendering ---------
def render_markdown(page_summaries, since_dt, until_dt):
    lines = []
    lines.append(f"# Valley Pawn — Friday Close Engagement Report")
    lines.append("")
    lines.append(
        f"**Window:** {since_dt.strftime('%Y-%m-%d')} → {until_dt.strftime('%Y-%m-%d')} "
        f"(generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})"
    )
    lines.append("")

    # Per-Page rollup
    lines.append("## Per-Page rollup")
    lines.append("")
    lines.append(
        "| Page | Posts | Reactions | Comments | Shares | Impressions | Reach | Engaged |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    grand = {"posts": 0, "reactions": 0, "comments": 0, "shares": 0,
             "impressions": 0, "reach": 0, "engaged_users": 0}
    for s in page_summaries:
        r = c = sh = imp = rch = eng = 0
        for p in s["posts"]:
            r += p["reactions"]; c += p["comments"]; sh += p["shares"]
            imp += p.get("impressions") or 0
            rch += p.get("reach") or 0
            eng += p.get("engaged_users") or 0
        n = len(s["posts"])
        lines.append(
            f"| {s['label']} | {n} | {r} | {c} | {sh} | {imp or '—'} | {rch or '—'} | {eng or '—'} |"
        )
        grand["posts"] += n; grand["reactions"] += r; grand["comments"] += c
        grand["shares"] += sh; grand["impressions"] += imp
        grand["reach"] += rch; grand["engaged_users"] += eng
    lines.append(
        f"| **TOTAL** | **{grand['posts']}** | **{grand['reactions']}** | **{grand['comments']}** "
        f"| **{grand['shares']}** | **{grand['impressions'] or '—'}** | **{grand['reach'] or '—'}** "
        f"| **{grand['engaged_users'] or '—'}** |"
    )
    lines.append("")

    # Top 5 posts by engagement (reactions + comments + shares)
    all_posts = []
    for s in page_summaries:
        for p in s["posts"]:
            score = (p["reactions"] or 0) + (p["comments"] or 0) + (p["shares"] or 0)
            all_posts.append((score, s["label"], p))
    all_posts.sort(key=lambda x: -x[0])
    lines.append("## Top 5 posts this week")
    lines.append("")
    if not all_posts:
        lines.append("_No posts in the window._")
    else:
        for rank, (score, label, p) in enumerate(all_posts[:5], 1):
            preview = p["message"].replace("|", "\\|")
            url = p.get("permalink_url") or ""
            lines.append(f"{rank}. **{label}** — score {score} "
                         f"(R{p['reactions']}/C{p['comments']}/S{p['shares']}) "
                         f"— [{preview}]({url})")
    lines.append("")

    # Warnings
    warnings_present = any(s["warnings"] for s in page_summaries)
    if warnings_present:
        lines.append("## Notes")
        lines.append("")
        for s in page_summaries:
            for w in s["warnings"]:
                lines.append(f"- **{s['label']}**: {w}")
        lines.append("")

    return "\n".join(lines)


# --------- main ---------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7,
                        help="lookback window in days (default 7)")
    parser.add_argument("--out", type=str,
                        default=str(Path.home() / "Documents/Claude/Projects/"
                                    "Refine Social Media/friday_close_report.md"))
    parser.add_argument("--no-insights", action="store_true",
                        help="skip read_insights calls (faster, no per-post insights)")
    args = parser.parse_args()

    tokens = load_tokens()
    pages = tokens["pages"]

    until_dt = datetime.now(timezone.utc)
    since_dt = until_dt - timedelta(days=args.days)
    since_unix = int(since_dt.timestamp())

    page_summaries = []
    include_insights = not args.no_insights
    for key in PAGE_KEYS:
        if key not in pages:
            print(f"[warn] Page {key} missing from tokens.json — skipping")
            continue
        print(f"[info] Pulling {key}...", file=sys.stderr)
        page_summaries.append(
            summarize_page(key, pages[key], since_unix, include_insights)
        )

    report = render_markdown(page_summaries, since_dt, until_dt)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()
