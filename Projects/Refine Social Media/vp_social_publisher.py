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
import sys
from datetime import datetime
from pathlib import Path

from publer_client import PublerClient, PublerError


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
    if not caption.strip():
        return {"id": item_id, "error": "empty caption — refusing to publish"}

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

    results = []
    for item in items:
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
