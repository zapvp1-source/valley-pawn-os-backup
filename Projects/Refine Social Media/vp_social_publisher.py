#!/usr/bin/env python3
"""
vp-social-publisher — Valley Pawn social publishing executor.

Consolidates the publishing layer previously fragmented across:
  - facebook-post skill (direct Graph API — DEPRECATED 2026-06-19)
  - daily-social-media-content (B)
  - weekly-social-media-content (B)
  - tuesday-facebook-posts, wednesday-facebook-posts, saturday-facebook-posts (all B)
  - thursday-youtube-employee-clips (B)
  - weekly-youtube-shorts (B)
  - monthly-top-sales-review (B)

Single publishing path: Publer API via publer_client.PublerClient.

INPUT: an "approved manifest" JSON, typically produced by vp-content-batch after
Joshua approves items in #vp-studio-queue. Schema:

    {
      "batch_id": "...",
      "items": [
        {
          "id": "...",
          "routing_tier": "brand" | "store-local" | "fan-out",
          "store_keys": ["Brand"] | ["Lexington"] | ["Brand","BrandIG"],
          "caption": "...",
          "image_url": "https://...",   # or video_url
          "scheduled_at": "2026-06-22T09:00:00",  # ISO local
          "status": "approved"
        },
        ...
      ]
    }

OUTPUT: a results JSON with Publer post ids and any failures, plus a Slack-ready
summary (does NOT post to Slack by itself — caller decides).

USAGE:
    python3 vp_social_publisher.py <manifest.json> [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from publer_client import PublerClient, PublerError


# --- AUTHENTICITY / QA GATE (added 2026-07-11 content review) --------------
#
# Root cause of the 2026-07-11 review: a live pull of Publer's own post
# history showed 69% of every post ever published through this workspace
# (55 of 80, going back to 2026-05-26) went out with a COMPLETELY EMPTY
# caption -- just an image, no words, no CTA, nothing. Store-local pages
# (Roanoke/Waynesboro/Culpeper) were hit worst at 90% blank. This script
# already had an empty-caption guard (below), which means those posts did
# NOT go through this script -- they were published some other way
# (ad-hoc/manual Publer calls that bypassed the one hardened path).
#
# Going forward: vp_social_publisher.py via publish_item() is the ONLY
# sanctioned way to schedule a Valley Pawn post. Never call
# PublerClient.schedule_post() directly from a one-off script or inline
# snippet -- doing so is exactly how the blank-caption posts slipped
# through undetected for 6+ weeks with no safety net.
#
# Ground-truth store facts, so AI-drafted captions can be checked against
# reality before they go out (a live post claimed "seven days a week" when
# no Valley Pawn store is open 7 days -- Culpeper is closed Sunday; all
# other stores are closed Wednesday AND Sunday). Keep in sync with
# valley-pawn-context if hours/addresses ever change.
STORE_FACTS = {
    "Culpeper": {"address": "571 James Madison Highway, Culpeper, VA 22701",
                 "hours": "Mon-Sat 10am-6pm, closed Sunday"},
    "Waynesboro": {"address": "1321 West Broad Street, Waynesboro, VA 22980",
                   "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"},
    "Harrisonburg": {"address": "1790 East Market Street, Harrisonburg, VA 22801",
                     "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"},
    "Lexington": {"address": "125 Walker Street, Lexington, VA 24450",
                  "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"},
    "Roanoke": {"address": "2362 Peters Creek Road, Suite C, Roanoke, VA 24017",
                "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"},
}

# Phrases that have actually shipped in live posts and are factually wrong or
# generic-tell-tale. Extend this list whenever a fact-check miss is found.
_FORBIDDEN_CLAIMS = [
    (re.compile(r"seven days a week|7 days a week", re.I),
     "no Valley Pawn store is open 7 days/week (Culpeper closed Sun; others closed Wed+Sun)"),
    (re.compile(r"open until 5\s*pm|closes? at 5\s*pm", re.I),
     "no Valley Pawn store closes at 5pm -- all close at 6pm"),
    (re.compile(r"dixie pawn", re.I),
     "legacy name -- Harrisonburg is Valley Pawn, never Dixie Pawn"),
]


def qa_check_caption(caption: str, store_keys: list[str]) -> list[str]:
    """Return a list of blocking problems with a caption. Empty list = OK to publish."""
    problems = []
    stripped = caption.strip()
    if not stripped:
        problems.append("empty caption")
        return problems  # nothing else to check
    for pattern, reason in _FORBIDDEN_CLAIMS:
        if pattern.search(stripped):
            problems.append(f"factual error: {reason}")
    # GBP-style hard rules apply to any Google account key if ever routed here
    if any(k.lower().startswith("gbp") or k.lower() == "google" for k in store_keys):
        if "#" in stripped:
            problems.append("GBP post contains hashtags (Google policy -- strip them)")
        if re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", stripped):
            problems.append("GBP post contains a phone number in body (Google spam signal)")
    return problems


# --- IMAGE AUTHENTICITY GATE (added 2026-07-11 imagery audit) --------------
#
# A live pull + visual review of Publer's actual post history (not just
# captions) found a second, separate authenticity problem: several generic
# AI-rendered "mood" images -- an antique desk/compass scene, a Shenandoah
# Valley landscape, a pile of gold chains on a scale -- were reused, pixel-
# for-pixel identical, across DIFFERENT physical store locations' Google
# Business Profiles and Brand posts (e.g. the same valley-landscape render
# stamped onto Harrisonburg's GBP one day and Roanoke's GBP the next; the
# same antique-desk render on Waynesboro's GBP and two Brand FB/Twitter
# posts). Every one of those was also a blank-caption post (see Section 6
# above / the QA gate that now blocks empty captions).
#
# This is a distinct failure from the caption problem: a customer in
# Harrisonburg and a customer in Roanoke see the literal same stock photo,
# with nothing tying it to their actual town, store, or inventory. Item-
# specific images (a real photo of a specific guitar or amp posted for the
# store that actually has it) looked fine and are NOT what this blocks --
# the same real item's photo cross-posted to that ONE store's FB/IG/GBP is
# expected and fine. Only reuse of one image across MULTIPLE DIFFERENT
# physical stores is the problem.
STORE_TOWNS = {"Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"}


def _base_stores(store_keys: list[str]) -> set[str]:
    """Collapse GBP/FB/IG channel variants down to the physical store they represent."""
    bases = set()
    for k in store_keys:
        nk = normalize_store_key(k)
        if nk.upper().startswith("GBP_"):
            nk = nk[4:]
        if nk in STORE_TOWNS:
            bases.add(nk)
        elif nk.startswith("Brand"):
            bases.add("Brand")
    return bases


def qa_check_image_diversity(items: list[dict]) -> dict[str, str]:
    """
    Batch-level check (run across a whole manifest, not per-item): the same
    image asset must never be reused across posts for two or more DIFFERENT
    physical store locations. Returns {item_id: reason} for every item that
    must be blocked. Brand-tier reuse (same generic brand image on Brand FB
    + BrandIG + BrandTwitter) is fine -- Brand isn't a physical location.
    """
    by_image: dict[str, list[dict]] = {}
    for item in items:
        img = item.get("image_url")
        if not img:
            continue
        by_image.setdefault(img, []).append(item)

    blocked: dict[str, str] = {}
    for img, group in by_image.items():
        if len(group) < 2:
            continue
        all_bases: set[str] = set()
        for item in group:
            all_bases |= _base_stores(expand_routing(item))
        distinct_stores = all_bases - {"Brand"}
        if len(distinct_stores) > 1:
            ids = ", ".join(str(i.get("id", "?")) for i in group)
            reason = (
                f"image reused across {len(distinct_stores)} different store locations "
                f"({', '.join(sorted(distinct_stores))}) -- items {ids}. Generic imagery "
                f"must not stand in for a specific store; use that store's own real photo "
                f"or a genuinely relevant item shot instead."
            )
            for item in group:
                blocked[item.get("id", "<no-id>")] = reason
    return blocked


# --- store key normalization ----------------------------------------------

# Accept both display names and store keys. Map to Publer accounts.json keys.
_STORE_ALIASES = {
    # Brand FB
    "brand": "Brand",
    "valley pawn": "Brand",
    # Brand IG
    "brand-ig": "BrandIG",
    "brand_ig": "BrandIG",
    "valley_pawn ig": "BrandIG",
    "instagram": "BrandIG",
    "@valley_pawn": "BrandIG",
    # Brand TikTok
    "brand-tiktok": "BrandTikTok",
    "brand_tiktok": "BrandTikTok",
    "tiktok": "BrandTikTok",
    # Brand Twitter / X
    "brand-twitter": "BrandTwitter",
    "brand_twitter": "BrandTwitter",
    "twitter": "BrandTwitter",
    "x": "BrandTwitter",
    "@joshuadavis": "BrandTwitter",
    # Brand Blog (WordPress)
    "brand-blog": "BrandBlog",
    "brand_blog": "BrandBlog",
    "wordpress": "BrandBlog",
    "blog": "BrandBlog",
    "thevalleypawn.com": "BrandBlog",
    # Stores
    "lexington": "Lexington",
    "lex": "Lexington",
    "roanoke": "Roanoke",
    "roa": "Roanoke",
    "harrisonburg": "Harrisonburg",
    "har": "Harrisonburg",
    "harrisonburg va": "Harrisonburg",
    "valley pawn- harrisonburg va": "Harrisonburg",
    "culpeper": "Culpeper",
    "cul": "Culpeper",
    "waynesboro": "Waynesboro",
    "way": "Waynesboro",
}


def normalize_store_key(s: str) -> str:
    return _STORE_ALIASES.get(s.strip().lower(), s)


def expand_routing(item: dict) -> list[str]:
    """
    Resolve the list of store keys for an item, taking routing_tier into account.

    routing_tier values (updated 2026-06-19):
      - "brand"       → Brand FB + BrandIG + BrandTwitter + BrandBlog (WordPress).
                        TikTok intentionally NOT included — video-first, requires
                        vp-reel-pipeline. Add explicitly to store_keys if needed.
      - "store-local" → use store_keys as-is (single store FB)
      - "fan-out"     → all 5 store FB Pages + Brand FB + BrandIG + BrandTwitter.
                        WordPress NOT in fan-out (would be noisy for SEO — quality > quantity).
                        TikTok also excluded — same video-first rule.
    """
    tier = item.get("routing_tier", "store-local").lower()
    keys = item.get("store_keys", [])
    keys = [normalize_store_key(k) for k in keys]

    if tier == "brand":
        # default brand cross-post if store_keys not specified
        return keys or ["Brand", "BrandIG", "BrandTwitter", "BrandBlog"]
    if tier == "fan-out":
        return ["Brand", "BrandIG", "BrandTwitter",
                "Lexington", "Roanoke", "Harrisonburg", "Culpeper", "Waynesboro"]
    if tier == "store-local":
        if not keys:
            raise PublerError(f"store-local item {item.get('id','?')} missing store_keys")
        return keys
    # Unknown tier — pass through with warning
    print(f"[warn] unknown routing_tier '{tier}' for item {item.get('id','?')}", file=sys.stderr)
    return keys


# --- main publisher --------------------------------------------------------

def publish_item(p: PublerClient, item: dict, dry_run: bool = False) -> dict:
    """Publish a single item via Publer. Returns a result dict."""
    item_id = item.get("id", "<no-id>")
    if item.get("status") != "approved":
        return {"id": item_id, "skipped": True, "reason": f"status={item.get('status')}"}

    store_keys = expand_routing(item)

    caption = item.get("caption") or item.get("text") or ""
    problems = qa_check_caption(caption, store_keys)
    if problems:
        return {"id": item_id, "error": "QA gate failed — refusing to publish: " + "; ".join(problems)}

    image_url = item.get("image_url")
    video_url = item.get("video_url")
    scheduled_at = item.get("scheduled_at")
    # Publer wants ISO 8601 with timezone. If naive, treat as UTC.
    if scheduled_at and not (scheduled_at.endswith("Z") or
                              ("+" in scheduled_at[10:]) or
                              ("-" in scheduled_at[10:])):
        scheduled_at = scheduled_at + "Z"
    immediate = bool(item.get("immediate"))

    if dry_run:
        return {
            "id": item_id, "dry_run": True,
            "store_keys": store_keys,
            "scheduled_at": scheduled_at,
            "immediate": immediate,
            "caption_preview": caption[:80],
        }

    try:
        resp = p.schedule_post(
            text=caption,
            store_keys=store_keys,
            scheduled_at=scheduled_at,
            image_urls=[image_url] if image_url else None,
            video_url=video_url,
            immediate=immediate,
        )
        job_id = resp.get("job_id") if isinstance(resp, dict) else None
        return {
            "id": item_id,
            "job_id": job_id,
            "store_keys": store_keys,
            "scheduled_at": scheduled_at,
            "immediate": immediate,
        }
    except PublerError as e:
        return {"id": item_id, "error": str(e)[:200], "store_keys": store_keys}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manifest", type=str, help="Path to approved manifest JSON")
    parser.add_argument("--dry-run", action="store_true", help="Resolve routing + validate without publishing")
    parser.add_argument("--out", type=str, default=None, help="Where to write the results JSON (default: alongside manifest)")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text())
    items = manifest.get("items", [])
    if not items:
        print("[error] manifest has no items", file=sys.stderr)
        sys.exit(2)

    p = PublerClient()
    print(f"[info] workspace: {p.workspace_id}", file=sys.stderr)
    print(f"[info] {len(items)} items in manifest, dry_run={args.dry_run}", file=sys.stderr)

    image_problems = qa_check_image_diversity(items)
    if image_problems:
        print(f"[warn] {len(image_problems)} item(s) blocked by image-diversity gate", file=sys.stderr)

    results = []
    for item in items:
        item_id = item.get("id", "<no-id>")
        img_problem = image_problems.get(item_id)
        if img_problem:
            r = {"id": item_id, "error": "QA gate failed — refusing to publish: " + img_problem}
        else:
            r = publish_item(p, item, dry_run=args.dry_run)
        results.append(r)
        status = "DRY" if r.get("dry_run") else ("ERR" if r.get("error") else ("SKIP" if r.get("skipped") else "OK "))
        print(f"  {status} {r.get('id','?'):30s} → {r.get('store_keys', r.get('reason','?'))}")

    out_path = Path(args.out) if args.out else manifest_path.with_name(
        f"{manifest_path.stem}_publish_results_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    )
    out = {
        "manifest_id": manifest.get("batch_id"),
        "manifest_path": str(manifest_path),
        "ran_at": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "results": results,
        "summary": {
            "total": len(results),
            "ok": sum(1 for r in results if r.get("publer_post_id")),
            "errors": sum(1 for r in results if r.get("error")),
            "skipped": sum(1 for r in results if r.get("skipped")),
            "dry_run": sum(1 for r in results if r.get("dry_run")),
        },
    }
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nResults: {out_path}")
    print(f"Summary: {out['summary']}")


if __name__ == "__main__":
    main()
