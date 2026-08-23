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

# ---------------------------------------------------------------------------
# FIXED 2026-08-22 -- signal threshold is now PER ACCOUNT, not corpus-wide.
# The 8/21 digest emitted "+5% warranty next batch" off n=8 posts total. An
# account contributes to the top/bottom ranking that drives the mix adjustment
# only if it published at least MIN_POSTS_FOR_SIGNAL posts in the window; and
# the winning theme must itself have MIN_THEME_POSTS posts behind it. Posts from
# thin accounts are still REPORTED, they just don't get to steer the batch.
# Override with env VP_MIN_POSTS_FOR_SIGNAL / VP_MIN_THEME_POSTS.
# ---------------------------------------------------------------------------
import os  # noqa: E402
MIN_POSTS_FOR_SIGNAL = int(os.environ.get("VP_MIN_POSTS_FOR_SIGNAL", "10"))
MIN_THEME_POSTS = int(os.environ.get("VP_MIN_THEME_POSTS", "3"))

# ---------------------------------------------------------------------------
# FIXED 2026-08-22 -- BOILERPLATE COLLISION IN THE THEME CLASSIFIER.
#
# The old patterns matched sitewide boilerplate that rides in the footer of
# nearly every post and carries ZERO thematic signal. Measured against the real
# 90-day corpus (audit_2026-08-22/publer_90day_raw.json, 246 posts with text):
#
#   warranty   103 -> 13 posts (8 unique content pieces). The old regex was
#              `warranty|what'?s right is right`. "What's Right Is Right" is the
#              BRAND TAGLINE and "30-day warranty" is the stock product-post
#              adjunct, so 103 posts were labelled `warranty` when only ~8 are
#              actually ABOUT the warranty. This single artifact produced eight
#              consecutive weeks of "+5% warranty next batch" in
#              adjustments_log.jsonl (7/12 -> 8/21). Those entries are VOID --
#              see adjustments_log_README.md.
#   heritage     5 -> 1. `since 20` matched the footer "since 2014"; `five
#              stores` matched "five stores across the Valley"; `shenandoah`
#              matched "five Shenandoah Valley stores". All three are footer
#              boilerplate. Every single old `heritage` hit was an artifact.
#   community   24 -> 10. NEWLY FOUND collision (not in the original bug
#              report): `walker street` and `davis street` are Valley Pawn's OWN
#              store addresses ("125 Walker Street, Lexington"), so every
#              Lexington post carrying its address was labelled `community`.
#              Also dropped bare `trail` and `harvest` (match product copy).
#   value       12 -> 19. `\$\d{2,}` matched ANY price, i.e. every product post.
#              Replaced with explicit price-COMPARISON phrasing.
#   team         0 -> 4.  `meet ` and `our team` matched product copy such as
#              "Our Harrisonburg team has a Godin LGXT ... on the floor".
#   mobile-app  `\bapp\b|download` -> requires an actual app-store reference.
#
# Themes with no pattern at all (hiring, layaway, giveaway, birthstone,
# holiday) were added -- `birthstone` was already referenced by
# build_adjustment()'s cap table, proving it was always meant to exist.
# ---------------------------------------------------------------------------

# Sitewide boilerplate. Stripped BEFORE classification so it can never vote.
BOILERPLATE_RE = [re.compile(p, re.I) for p in (
    r"what'?s right is right",
    r"\b(?:backed by|covered by|comes with|and it'?s covered by|includes?|protected by)\s+(?:our|its|the|a)?\s*(?:standard\s+)?30[-\s]?day warrant(?:y|ies)\b",
    r"\b30[-\s]?day warrant(?:y|ies)\b(?:\s*(?:on |like )?(?:everything|every item)(?: we sell)?|\s*(?:included|incl\.?))?",
    r"\bfree layaway\b",
    r"\bfamily[-\s]?owned\b",
    r"\bsince 20\d{2}\b",
    r"\b(?:five|5)\s+(?:shenandoah valley\s+)?(?:stores|locations)\b",
    r"\ball\s+(?:five|5)\s+(?:valley pawn\s+)?locations\b",
    r"\bshenandoah valley\b",
    r"\bin the (?:shenandoah )?valley\b",
    r"[\U0001F4CD]\s*[^\n]*",                      # trailing map-pin address lines
    r"\b\d{2,5}\s+[A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*)*\s+(?:St|Street|Rd|Road|Hwy|Highway|Blvd|Ave|Avenue)\b[^\n]*",
    r"\b(?:valley pawn[-\s]*)?(?:culpeper|harrisonburg|lexington|roanoke|waynesboro)\b",
    r"\bvalley pawn\b",
)]


def strip_boilerplate(t: str) -> str:
    for rx in BOILERPLATE_RE:
        t = rx.sub(" ", t)
    return re.sub(r"\s+", " ", t)


# "warranty" counts only when it is the SUBJECT of the post, never the adjunct.
WARRANTY_WORD_RE = re.compile(r"\bwarrant(?:y|ies)\b", re.I)
WARRANTY_SUBJECT_RE = re.compile(
    r"(if it doesn'?t work|bring it back|we stand behind what we sell|"
    r"money[-\s]?back guarantee|not a slogan|no fine print|store policy|"
    r"breaks in the first 30 days|buy with a warrant|warrant(?:y|ies) covers|"
    r"no exceptions)", re.I)
# A warranty promise stated without ever using the word "warranty".
WARRANTY_PROMISE_RE = re.compile(r"bring it back", re.I)
WARRANTY_PROMISE2_RE = re.compile(r"(make it right|no exceptions|30 days)", re.I)

TYPE_PATTERNS = [
    ("humor", r"guess the year|bingo|still runs|ask your parents|well[, ]+that's a first|it just needs a battery|drop your guess"),
    ("community", r"parade|farmers market|greenway|skyline drive|blue ridge|mill mountain|\bjmu\b|\bvmi\b|dukes|friendly city|national park|first friday|apple season"),
    ("holiday", r"memorial day|4th of july|fourth of july|independence day|labor day|black friday|christmas|new year|thanksgiving|veterans day"),
    ("hiring", r"we'?re hiring|now hiring|retail sales associate|join our team|apply (?:today|now)|we'?re growing"),
    ("giveaway", r"giveaway|giving away|enter free|drop your email|one customer wins|\$100 (?:each|every) month"),
    ("birthstone", r"birthstone"),
    ("layaway", r"\blayaway\b"),
    ("deal", r"deal of the week|this week'?s deal|blowout|storewide|today only|save up to"),
    ("gold", r"\bgold\b|\bsilver\b|scrap|spot price|karat|\b(?:10|14|18|22|24)k\b"),
    ("loan", r"\bloan\b|collateral|\bborrow|pawn loan"),
    ("how-it-works", r"how (?:pawn|it) works|apprais|our process|transparen|we weigh, we test"),
    ("team", r"years with us|meet (?:our|the) team\b|shoutout to our|team member|employee of the|(?:he|she) (?:manages|runs) the store|ask for (?:him|her)|good person to ask for"),
    ("heritage", r"serving the valley|our (?:story|history)|generation(?:s|al) (?:of )?family|how pawn shops used to work"),
    ("mobile-app", r"\bapp store\b|\bgoogle play\b|download (?:the|our) app|\bour app\b"),
    ("value", r"retail:? \$|new:? \$|ours:? \$|marked down (?:to|from)|\bmsrp\b|\$[\d,]+(?:\.\d+)? (?:off|under)|you save|our price|below what|under the \$|runs \$[\d,]+(?:\.\d+)? new|retail runs"),
    ("find", r"just walked in|walked in|new arrival|on the wall|on the floor(?: right)? now|just landed|just hit the|new in at|brand new to the shelf|crossed our counter|don'?t come up for sale often|doesn'?t come around every day|fresh inventory"),
]


def classify(text: str, post_type: str | None) -> str:
    raw = text or ""
    t = strip_boilerplate(raw).lower()
    rawl = raw.lower()

    has_w = bool(WARRANTY_WORD_RE.search(rawl))
    n_w = len(WARRANTY_WORD_RE.findall(rawl))
    if has_w and (WARRANTY_WORD_RE.search(t) or WARRANTY_SUBJECT_RE.search(rawl) or n_w >= 2):
        return "warranty"
    if not has_w and WARRANTY_PROMISE_RE.search(rawl) and WARRANTY_PROMISE2_RE.search(rawl):
        return "warranty"

    for label, pat in TYPE_PATTERNS:
        if re.search(pat, t):
            return label
    if post_type and "video" in str(post_type).lower():
        return "casual-video"
    return "other"


def metric(post: dict, *keys: str) -> int:
    # FIXED 2026-07-12: live-tested Publer's actual post_insights response --
    # every metric (reach, likes, comments, shares, post_clicks, video_views,
    # reach_rate, engagement_rate) is nested under post["analytics"][field]["value"],
    # NOT top-level and NOT under "insights"/"metrics" as originally assumed. That
    # mismatch meant every reach/engagement number in every digest since this
    # script was built (2026-07-06) silently computed as 0 -- the HTTP call
    # succeeded, so no error surfaced; the adjust loop just never had real signal.
    for k in keys:
        v = post.get(k)
        if isinstance(v, dict):
            v = v.get("value")
        if isinstance(v, (int, float)):
            return int(v)
    for src_key in ("analytics", "insights", "metrics"):
        ins = post.get(src_key)
        if not isinstance(ins, dict):
            continue
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
            # FIXED 2026-07-12: Publer has no single "engagement" field -- it
            # exposes likes, comments, shares, and post_clicks as separate
            # metrics (see metric() note above). Sum them for a real engagement
            # total instead of the previous engagement/engagements/likes lookup,
            # which always returned 0 since none of those keys ever existed.
            likes_n = metric(post, "likes")
            comments_n = metric(post, "comments")
            shares_n = metric(post, "shares", "reposts")
            clicks_n = metric(post, "post_clicks", "link_clicks")
            rows.append({
                "account": key,
                "network": cfg.get("provider", "?"),
                "text": text.strip().split("\n")[0][:90],
                "content_type": ctype,
                "reach": metric(post, "reach", "impressions", "views"),
                "engagement": likes_n + comments_n + shares_n + clicks_n,
                "comments": comments_n,
                "shares": shares_n,
                "eng_rate": None,
                "posted_at": post.get("scheduled_at") or post.get("published_at") or "",
                "url": post.get("url") or post.get("permalink") or "",
            })
    for r in rows:
        r["eng_rate"] = round(r["engagement"] / r["reach"], 4) if r["reach"] else 0.0
        r["score"] = r["engagement"] * 3 + r["reach"] * 0.01
    return rows


def dominant_type(rows: list[dict], min_theme_posts: int = 1) -> str:
    """Most common content_type in `rows`, ignoring the meaningless `other`
    bucket and any theme with fewer than `min_theme_posts` posts behind it."""
    counts: dict[str, int] = {}
    for r in rows:
        if r["content_type"] in ("other", "n/a"):
            continue
        counts[r["content_type"]] = counts.get(r["content_type"], 0) + 1
    counts = {k: v for k, v in counts.items() if v >= min_theme_posts}
    return max(counts, key=counts.get) if counts else "n/a"


def signal_accounts(rows: list[dict]) -> tuple[list[dict], dict[str, int], list[str]]:
    """Split rows into the ones allowed to steer the batch and the ones that
    aren't. An account needs >= MIN_POSTS_FOR_SIGNAL posts in the window."""
    per_account: dict[str, int] = {}
    for r in rows:
        per_account[r["account"]] = per_account.get(r["account"], 0) + 1
    eligible = [a for a, n in per_account.items() if n >= MIN_POSTS_FOR_SIGNAL]
    return [r for r in rows if r["account"] in eligible], per_account, sorted(eligible)


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

    # FIXED 2026-08-22: only accounts with enough volume may steer the mix.
    steer_rows, per_account, eligible = signal_accounts(rows)
    thin = sorted(a for a in per_account if a not in eligible)

    if not steer_rows:
        ranked = sorted(rows, key=lambda r: r["score"], reverse=True)
        n = max(1, round(len(ranked) * 0.2))
        top, bottom = ranked[:n], ranked[-n:]
        top_type = bottom_type = "n/a"
        action = (f"hold current mix — insufficient signal "
                  f"(no account reached {MIN_POSTS_FOR_SIGNAL} posts in {args.days}d)")
    else:
        ranked = sorted(steer_rows, key=lambda r: r["score"], reverse=True)
        n = max(1, round(len(ranked) * 0.2))
        top, bottom = ranked[:n], ranked[-n:]
        top_type = dominant_type(top, MIN_THEME_POSTS)
        bottom_type = dominant_type(bottom, MIN_THEME_POSTS)
        action = build_adjustment(top_type, bottom_type)

    signal_note = (f"**Signal basis:** {len(steer_rows)} posts from "
                   f"{len(eligible)} account(s) at/above the {MIN_POSTS_FOR_SIGNAL}-post "
                   f"threshold ({', '.join(eligible) or 'none'}). "
                   f"Excluded from steering (too thin): {', '.join(thin) or 'none'}.")

    lines = [f"# Valley Pawn — Friday Performance Digest — {today}",
             f"\n{len(rows)} posts across {len(set(r['account'] for r in rows))} accounts, last {args.days} days.\n",
             signal_note + "\n",
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
           "signal_posts": len(steer_rows), "signal_accounts": eligible,
           "excluded_thin_accounts": thin,
           "min_posts_for_signal": MIN_POSTS_FOR_SIGNAL,
           "min_theme_posts": MIN_THEME_POSTS,
           "top_posts": [{k: r[k] for k in ("account", "content_type", "text", "reach", "engagement")} for r in top],
           "bottom_posts": [{k: r[k] for k in ("account", "content_type", "text", "reach", "engagement")} for r in bottom]}
    ADJUSTMENTS.write_text(json.dumps(adj, indent=2))
    with open(ADJ_LOG, "a") as fh:
        fh.write(json.dumps({"week_ending": today, "top": top_type,
                             "bottom": bottom_type, "action": action,
                             "signal_posts": len(steer_rows),
                             "signal_accounts": eligible,
                             "classifier_version": "2026-08-22-boilerplate-fix"}) + "\n")
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
