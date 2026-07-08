#!/usr/bin/env python3
"""
Valley Pawn — Publer Weekly Digest (Part 4 of the 2026-07-06 strategic build)

Replaces the broken Meta-Graph measurement loop with Publer's analytics API.

Every Friday 4 PM (task: vp-publer-analytics-friday):
  1. Pull post-level insights for the last 7 days across ALL connected accounts.
  2. Rank by engagement (fallback: reach). Identify top 20% and bottom 20%.
  3. Classify each post's content type (community / humor / deal / find / value /
     warranty / gold / loan / heritage / team / how-it-works / casual-video / other)
     from caption keywords + the week's batch manifest when present.
  4. Write friday_digests/friday_digest_{date}.md (full report)
     + weekly-adjustments.json (the Monday batch reads this — the adjust loop)
     + append to adjustments_log.jsonl.
  5. Print the ONE-LINE digest for Joshua's DM on the last stdout line:
     DIGEST: Top: {type} / {N reach} · Bottom: {type} / {N reach} · action: {adjustment}

Usage:
  python3 publer_weekly_digest.py            # last 7 days
  python3 publer_weekly_digest.py --days 14
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from publer_client import PublerClient, PublerError  # noqa: E402

ROOT = Path(__file__).parent
DIGEST_DIR = ROOT / "friday_digests"
ADJUSTMENTS = ROOT / "weekly-adjustments.json"
ADJ_LOG = ROOT / "adjustments_log.jsonl"
STUDIO_OUT = Path.home() / "Documents/Claude/Projects/Valley Pawn Studios/output"
LESSONS = Path.home() / ".vp-studio/lessons.md"

TYPE_PATTERNS = [
    ("humor", r"guess the year|bingo|still runs|ask your parents|well[, ]+that's a first|it just needs a battery|generations"),
    ("community", r"parade|farmers market|greenway|trail|skyline drive|blue ridge|mill mountain|jmu|vmi|dukes|friendly city|davis street|walker street|national park|first friday|harvest|apple season"),
    ("deal", r"deal of the week|this week's deal|new:? \$|ours:? \$"),
    ("gold", r"gold|silver|scrap|spot price|karat|14k|10k|18k"),
    ("loan", r"\bloan|collateral|borrow"),
    ("warranty", r"warranty|what'?s right is right"),
    ("how-it-works", r"how (pawn|it) works|apprais|our process|transparen"),
    ("team", r"years with us|our team|meet |shoutout to our"),
    ("heritage", r"since 20|serving the valley|five stores|shenandoah(?! national)"),
    ("mobile-app", r"\bapp\b|download"),
    ("value", r"retail:? \$|new:? \$|ours:? \$|\$\d{2,}"),
    ("find", r"just walked in|walked in|new arrival|on the wall"),
]


def classify(text: str, post_type: str | None) -> str:
    t = (text or "").lower()
    for label, pat in TYPE_PATTERNS:
        if re.search(pat, t):
            return label
    if post_type and "video" in str(post_type).lower():
        return "casual-video"
    return "other"


def metric(post: dict, *keys: str) -> int:
    for k in keys:
        v = post.get(k)
        if isinstance(v, dict):
            v = v.get("value")
        if isinstance(v, (int, float)):
            return int(v)
    ins = post.get("insights") or post.get("metrics") or {}
    if isinstance(ins, dict):
        for k in keys:
            v = ins.get(k)
            if isinstance(v, dict):
                v = v.get("value")
            if isinstance(v, (int, float)):
                return int(v)
    return 0


def load_manifest_types() -> dict[str, str]:
    """Map caption first-lines -> pillar from the most recent batch manifest."""
    out: dict[str, str] = {}
    if not STUDIO_OUT.exists():
        return out
    manifests = sorted(STUDIO_OUT.glob("*/batch_manifest_*.json"), reverse=True)[:2]
    for mf in manifests:
        try:
            data = json.loads(mf.read_text())
        except Exception:
            continue
        for item in data.get("items", []):
            cap = (item.get("caption_fb") or item.get("headline") or "")
            key = cap.strip().split("\n")[0][:60].lower()
            pillar = item.get("sub_pillar") or item.get("pillar")
            if key and pillar:
                out[key] = str(pillar)
    return out


def collect(p: PublerClient, days: int) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    manifest_types = load_manifest_types()
    rows = []
    for key, cfg in p.accounts.items():
        try:
            posts = p.post_insights(cfg["publer_id"], since=since, until=until, limit=200)
        except PublerError as e:
            print(json.dumps({"warn": f"{key}: {str(e)[:120]}"}))
            continue
        for post in posts or []:
            text = post.get("text") or post.get("caption") or post.get("content") or ""
            first = text.strip().split("\n")[0][:60].lower()
            ctype = manifest_types.get(first) or classify(text, post.get("type"))
            rows.append({
                "account": key,
                "network": cfg.get("provider", "?"),
                "text": text.strip().split("\n")[0][:90],
                "content_type": ctype,
                "reach": metric(post, "reach", "impressions", "views"),
                "engagement": metric(post, "engagement", "engagements", "likes"),
                "comments": metric(post, "comments"),
                "shares": metric(post, "shares", "reposts"),
                "eng_rate": None,
                "posted_at": post.get("scheduled_at") or post.get("published_at") or "",
                "url": post.get("url") or post.get("permalink") or "",
            })
    for r in rows:
        r["eng_rate"] = round(r["engagement"] / r["reach"], 4) if r["reach"] else 0.0
        r["score"] = r["engagement"] * 3 + r["reach"] * 0.01
    return rows


def dominant_type(rows: list[dict]) -> str:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["content_type"]] = counts.get(r["content_type"], 0) + 1
    return max(counts, key=counts.get) if counts else "n/a"


def build_adjustment(top_type: str, bottom_type: str) -> str:
    protected_floors = {"community": "Community has a 15% floor — do not cut below it.",
                        "warranty": "Warranty has a 10% floor.", "team": "Team has a 10% floor.",
                        "how-it-works": "How-It-Works has a 10% floor.", "mobile-app": "Mobile app has a 5% floor."}
    capped = {"humor": "Humor is hard-capped at 10% / 1 per week — do NOT increase past cap.",
              "birthstone": "Birthstone capped at 15%."}
    parts = []
    if top_type not in ("other", "n/a"):
        note = f" ({capped[top_type]})" if top_type in capped else ""
        parts.append(f"+5% {top_type} next batch{note}")
    if bottom_type not in ("other", "n/a") and bottom_type != top_type:
        note = f" ({protected_floors[bottom_type]})" if bottom_type in protected_floors else ""
        parts.append(f"-5% {bottom_type}{note}")
    return "; ".join(parts) if parts else "hold current mix"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    p = PublerClient()
    rows = collect(p, args.days)
    today = datetime.now().strftime("%Y-%m-%d")
    DIGEST_DIR.mkdir(exist_ok=True)
    out_md = DIGEST_DIR / f"friday_digest_{today}.md"

    if not rows:
        out_md.write_text(f"# Friday digest {today}\n\nNo posts with insights found "
                          f"in the last {args.days} days (analytics may lag 24-48h).\n")
        print("DIGEST: No post insights available this week — Publer analytics may be lagging; no mix change.")
        return

    ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
    n = max(1, round(len(ranked) * 0.2))
    top, bottom = ranked[:n], ranked[-n:]
    top_type, bottom_type = dominant_type(top), dominant_type(bottom)
    action = build_adjustment(top_type, bottom_type)

    lines = [f"# Valley Pawn — Friday Performance Digest — {today}",
             f"\n{len(rows)} posts across {len(set(r['account'] for r in rows))} accounts, last {args.days} days.\n",
             f"**Top 20% dominant type:** {top_type}  |  **Bottom 20% dominant type:** {bottom_type}",
             f"**Adjustment for Monday's batch:** {action}\n", "## Top performers\n",
             "| Account | Type | Post | Reach | Eng | Rate |", "|---|---|---|---|---|---|"]
    for r in top:
        lines.append(f"| {r['account']} | {r['content_type']} | {r['text'][:60]} | "
                     f"{r['reach']} | {r['engagement']} | {r['eng_rate']:.1%} |")
    lines += ["\n## Bottom performers\n",
              "| Account | Type | Post | Reach | Eng | Rate |", "|---|---|---|---|---|---|"]
    for r in bottom:
        lines.append(f"| {r['account']} | {r['content_type']} | {r['text'][:60]} | "
                     f"{r['reach']} | {r['engagement']} | {r['eng_rate']:.1%} |")
    by_type: dict[str, list] = {}
    for r in rows:
        by_type.setdefault(r["content_type"], []).append(r)
    lines += ["\n## By content type\n", "| Type | Posts | Avg reach | Avg eng |", "|---|---|---|---|"]
    for t, rs in sorted(by_type.items(), key=lambda kv: -sum(x["engagement"] for x in kv[1])):
        lines.append(f"| {t} | {len(rs)} | {sum(x['reach'] for x in rs)//len(rs)} | "
                     f"{sum(x['engagement'] for x in rs)//len(rs)} |")
    out_md.write_text("\n".join(lines) + "\n")

    adj = {"week_ending": today, "generated_at": datetime.now().isoformat(),
           "top_type": top_type, "bottom_type": bottom_type, "action": action,
           "top_posts": [{k: r[k] for k in ("account", "content_type", "text", "reach", "engagement")} for r in top],
           "bottom_posts": [{k: r[k] for k in ("account", "content_type", "text", "reach", "engagement")} for r in bottom]}
    ADJUSTMENTS.write_text(json.dumps(adj, indent=2))
    with open(ADJ_LOG, "a") as fh:
        fh.write(json.dumps({"week_ending": today, "top": top_type,
                             "bottom": bottom_type, "action": action}) + "\n")
    try:
        LESSONS.parent.mkdir(parents=True, exist_ok=True)
        with open(LESSONS, "a") as fh:
            fh.write(f"\n## {today} (Publer digest)\nBottom 20% dominated by "
                     f"{bottom_type}: " + "; ".join(r["text"][:60] for r in bottom) + "\n")
    except OSError:
        pass

    top_r = max(top, key=lambda r: r["reach"])
    bot_r = min(bottom, key=lambda r: r["reach"])
    print(f"DIGEST: Top: {top_type} / {top_r['reach']} reach · Bottom: {bottom_type} / "
          f"{bot_r['reach']} reach · action: {action}")


if __name__ == "__main__":
    main()
