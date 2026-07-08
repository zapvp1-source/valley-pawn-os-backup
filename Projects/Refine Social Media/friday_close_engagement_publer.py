#!/usr/bin/env python3
"""
Valley Pawn — Friday Close Engagement Report (Publer-routed)

Replaces the direct Meta Graph API analytics path with Publer's analytics endpoint.

Why: the direct Meta Graph API path required permanent Page Access Tokens that
Meta kept invalidating, and was blocked from Waynesboro/Culpeper Pages by the
sub-portfolio ownership wall. Publer's analytics endpoint exposes the same
metrics (reactions / comments / shares / reach / impressions) without any of
that token nonsense.

Original direct-Meta version preserved at: friday_close_engagement.py
(kept for reference + fallback if Publer's analytics ever returns stale data)

Runs:
    python3 friday_close_engagement_publer.py
    python3 friday_close_engagement_publer.py --days 14
    python3 friday_close_engagement_publer.py --out /tmp/report.md
"""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from publer_client import PublerClient, PublerError

DEFAULT_OUT = Path.home() / "Documents/Claude/Projects/Refine Social Media/friday_close_report.md"


def _safe_get(metrics: dict, *keys: str) -> int | None:
    """Walk a metrics dict to find a key — Publer's analytics shape varies a bit by provider."""
    if not isinstance(metrics, dict):
        return None
    for k in keys:
        if k in metrics:
            v = metrics[k]
            if isinstance(v, (int, float)):
                return int(v)
            if isinstance(v, dict) and "value" in v:
                return int(v["value"])
    return None


def collect(p: PublerClient, days: int) -> list[dict]:
    """Pull per-account post-level insights for the past N days, aggregate per account."""
    until_dt = datetime.now(timezone.utc)
    since_dt = until_dt - timedelta(days=days)
    since = since_dt.strftime("%Y-%m-%d")
    until = until_dt.strftime("%Y-%m-%d")

    rows = []
    for key, cfg in p.accounts.items():
        try:
            posts = p.post_insights(cfg["publer_id"], since=since, until=until, limit=200)
        except PublerError as e:
            rows.append({
                "key": key, "name": cfg.get("name", key),
                "error": str(e)[:100], "post_count": 0,
                "reactions": 0, "comments": 0, "shares": 0,
                "reach": 0, "impressions": 0, "top": None,
            })
            continue

        # Aggregate per account
        agg = dict(reactions=0, comments=0, shares=0, reach=0, impressions=0,
                   saves=0, video_views=0, link_clicks=0)
        top_post = None
        top_score = -1
        for post in posts:
            for k in agg:
                v = _safe_get(post, k, f"total_{k}", k.rstrip('s'))
                if v:
                    agg[k] += v
            # score = likes + comments + shares for "top post" pick
            score = (_safe_get(post, "likes", "reactions") or 0) + \
                    (_safe_get(post, "comments") or 0) + \
                    (_safe_get(post, "shares") or 0)
            if score > top_score:
                top_score = score
                top_post = post

        rows.append({
            "key": key,
            "name": cfg.get("name", key),
            "error": None,
            "post_count": len(posts),
            "reactions": agg["reactions"],
            "comments": agg["comments"],
            "shares": agg["shares"],
            "reach": agg["reach"] or None,
            "impressions": agg["impressions"] or None,
            "saves": agg["saves"],
            "video_views": agg["video_views"],
            "link_clicks": agg["link_clicks"],
            "top": (top_post if top_score > 0 else None),
        })
    return rows


def render(rows: list[dict], days: int, since_dt: datetime, until_dt: datetime) -> str:
    out = []
    out.append("# Valley Pawn — Friday Close Engagement Report (Publer-routed)")
    out.append("")
    out.append(
        f"**Window:** {since_dt.strftime('%Y-%m-%d')} → {until_dt.strftime('%Y-%m-%d')} "
        f"({days} days)  ·  Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ·  Source: Publer analytics"
    )
    out.append("")

    # Roll-up table
    out.append("## Per-account roll-up")
    out.append("")
    out.append("| Account | Posts | Reactions | Comments | Shares | Reach | Impressions |")
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    total = dict(post_count=0, reactions=0, comments=0, shares=0, reach=0, impressions=0)
    for r in rows:
        if r["error"]:
            out.append(f"| {r['name']} | — | — | — | — | — | — |")
            continue
        total["post_count"] += r.get("post_count") or 0
        total["reactions"] += r.get("reactions") or 0
        total["comments"] += r.get("comments") or 0
        total["shares"] += r.get("shares") or 0
        total["reach"] += r.get("reach") or 0
        total["impressions"] += r.get("impressions") or 0
        out.append(
            f"| {r['name']} | {r['post_count']} | {r['reactions']} | {r['comments']} "
            f"| {r['shares']} | {r['reach'] or '—'} | {r['impressions'] or '—'} |"
        )
    out.append(
        f"| **TOTAL** | **{total['post_count']}** | **{total['reactions']}** | **{total['comments']}** "
        f"| **{total['shares']}** | **{total['reach'] or '—'}** | **{total['impressions'] or '—'}** |"
    )
    out.append("")

    # Errors / notes
    errs = [r for r in rows if r["error"]]
    if errs:
        out.append("## Accounts with errors")
        out.append("")
        for r in errs:
            out.append(f"- **{r['name']}**: {r['error']}")
        out.append("")

    out.append("## Notes")
    out.append("")
    out.append(
        "- Source: Publer analytics endpoint (`/accounts/{id}/analytics`). Replaces the direct "
        "Meta Graph API path. The original `friday_close_engagement.py` is preserved as a fallback."
    )
    out.append(
        "- If a metric shows `—`, Publer's analytics returned no value for it on this account. "
        "Some providers (notably IG) report a different subset than FB Pages."
    )
    out.append(
        "- This report should be cross-referenced with `weekly-analytics-summary` (Google Analytics) "
        "for website-side conversion data not visible in social analytics."
    )
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7, help="lookback window in days (default 7)")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    args = parser.parse_args()

    until_dt = datetime.now(timezone.utc)
    since_dt = until_dt - timedelta(days=args.days)

    p = PublerClient()
    print(f"[info] workspace: {p.workspace_id}", file=sys.stderr)
    print(f"[info] window: {since_dt.strftime('%Y-%m-%d')} → {until_dt.strftime('%Y-%m-%d')}", file=sys.stderr)

    rows = collect(p, args.days)
    print(f"[info] {len(rows)} accounts queried", file=sys.stderr)

    report = render(rows, args.days, since_dt, until_dt)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print(f"Report written: {out}")


if __name__ == "__main__":
    main()
