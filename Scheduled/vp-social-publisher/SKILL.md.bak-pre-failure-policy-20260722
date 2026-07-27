---
name: vp-social-publisher
description: Valley Pawn social publishing executor. Takes an approved-manifest JSON from vp-content-batch and pushes posts to Facebook Pages + brand Instagram via Publer's API. Replaces the deprecated facebook-post skill and consolidates 8 disabled scheduled tasks (daily-social-media-content, weekly-social-media-content, tuesday/wednesday/saturday-facebook-posts, thursday-youtube-employee-clips, weekly-youtube-shorts, monthly-top-sales-review) into a single publishing path.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

## What this skill does

Single publishing path for Valley Pawn social content. Reads an approved-manifest JSON (typically produced by vp-content-batch after Joshua approves items in `#vp-studio-queue`), routes each item to the correct Publer accounts based on `routing_tier`, and schedules the post via Publer's API.

**Why it exists:** the 8 disabled scheduled tasks listed in the description were broken by the Meta token wall + Waynesboro/Culpeper sub-portfolio ownership issue. Publer's OAuth bypasses both. `vp-social-publisher` is the additive replacement (Rule #4) — the 8 old tasks remain in `/Scheduled/` as LEGACY (do not reactivate; clone into this skill's flow instead).

## Pre-reads (always)

1. `valley-pawn-context` — brand voice, "Dixie Pawn never" rule, no firearms in social
2. `vp-brand-studio` — visual identity reference
3. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/publer_config.json` — API auth + workspace
4. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/publer_accounts.json` — store-key → Publer account ID map

## Inputs

An approved manifest JSON. Schema:

```json
{
  "batch_id": "vp-content-batch-2026-06-22",
  "items": [
    {
      "id": "item-001",
      "routing_tier": "brand" | "store-local" | "fan-out",
      "store_keys": ["Brand", "BrandIG"],
      "caption": "Final approved caption text",
      "image_url": "https://...",
      "video_url": null,
      "scheduled_at": "2026-06-22T09:00:00",
      "status": "approved"
    }
  ]
}
```

Routing tier rules:
- `brand` → Brand FB Page + @valley_pawn IG (cross-post)
- `store-local` → only the named store's FB Page (single account)
- `fan-out` → Brand FB + Brand IG + all 5 store FB Pages (rare, holiday only)

## How to run

```bash
# Dry-run (validate routing + accounts, do not publish):
python3 /Users/joshuadavis/Documents/Claude/Projects/Refine\ Social\ Media/vp_social_publisher.py \
  /path/to/approved_manifest.json --dry-run

# Live (actually schedule posts via Publer):
python3 /Users/joshuadavis/Documents/Claude/Projects/Refine\ Social\ Media/vp_social_publisher.py \
  /path/to/approved_manifest.json
```

A results JSON is written alongside the manifest with each item's Publer post id + any failures.

## Steps for an autonomous run

1. Receive a path to an approved manifest JSON (provided by caller — typically vp-content-batch).
2. Verify the manifest exists and has at least one approved item. If empty, exit silently — no Slack noise.
3. Run with `--dry-run` first to validate routing maps cleanly. If any item errors at the routing step (e.g. unknown store key), surface the failure to the caller; do NOT skip silently.
4. After dry-run passes, run live without `--dry-run`. Each item that publishes successfully gets a `publer_post_id` in the results JSON.
5. Write a summary back to the caller (vp-content-batch handles the Slack post if appropriate).

## Hard rules

- **Never publish an item with empty caption.** The script enforces this — empty caption returns an error, not a publish.
- **Never publish "Dixie Pawn" anywhere in the caption.** Caller (vp-content-batch) is supposed to check, but if it slips through, fail hard.
- **Never publish firearms-related content to social.** Same — caller's responsibility, but second-line check welcome.
- **No Slack failure noise.** If the API errors, log to results JSON, return non-zero exit, let the caller decide whether to alert.

## Troubleshooting

- **All publishes fail with 401:** check `publer_config.json` has `workspace_id` set (the API rejects requests without it).
- **All publishes fail with 500:** Publer's analytics indexer is warming up after a freshly-connected account. Retry after a few hours.
- **Unknown store key error:** check the store_keys in the manifest against `publer_accounts.json`. Normalizations are in `_STORE_ALIASES` in `vp_social_publisher.py` — extend if a new alias is needed.
- **A specific account fails repeatedly:** confirm in Publer's UI that the social account is still healthy (Publer surfaces "needs reconnect" status). Re-OAuth from Publer's social-accounts page is a Joshua click.

## What this skill does NOT do

- Does NOT generate content (that's vp-content-batch)
- Does NOT generate images (that's vp-hero-image)
- Does NOT compose channel-specific assets (that's vp-asset-compose)
- Does NOT post to Slack (caller's job)
- Does NOT touch direct Meta Graph API (deprecated path; everything routes through Publer)
- Does NOT publish to TikTok / YouTube Shorts / Twitter yet (Phase 2 expansion — when those accounts connect, just add their store keys to `publer_accounts.json` and they become routable)

## Migration / deprecation notes

- This skill is the **2026-06-19 replacement** for the `facebook-post` skill's publishing path.
- The `facebook-post` skill remains in place as LEGACY for reference. Do not call it from new code.
- The 8 disabled scheduled tasks in the description above remain in `/Scheduled/` as LEGACY. Their B-status keeps them from firing. Don't reactivate; their logic is fully subsumed by `vp-content-batch` (orchestration) + this skill (publishing).
