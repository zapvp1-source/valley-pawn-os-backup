# Refine Social Media — Folder Index

This folder is the working directory for Valley Pawn's social media stack. Future Claude sessions should read this index first to understand what lives here.

## Purpose
Home of the **Publer-routed publishing pipeline** that replaced the direct Meta Graph API path (2026-06-19). Contains the API client, the manifest executor, account mappings, brand assets, and the registration patch for BUSINESS_OS.md.

## Read-first files
1. `BUSINESS_OS_REGISTRATION_DELTA.md` — additive patch listing all new domains/accounts/platforms/scripts/folders registered in this folder. Master enterprise map reference.
2. `vp-social-publisher_SKILL.md` — describes the publishing-layer skill (currently a stub; install via Settings → Capabilities to make it active).

## Core code
- `publer_client.py` — Publer API client. Bulk/networks payload structure. Methods: `schedule_post`, `job_status`, `wait_for_job`, `post_insights`, `list_accounts`.
- `vp_social_publisher.py` — manifest executor. Reads approved-manifest JSON → routes per `routing_tier` → calls Publer API hands-off.
- `friday_close_engagement_publer.py` — engagement analytics (Friday close report) via Publer.
- `friday_close_engagement.py` — LEGACY direct-Meta version. Preserved as fallback only.
- `publer_weekly_digest.py` — **(2026-07-06 strategic build)** Friday 4 PM analytics loop: top/bottom 20% by engagement via Publer API → `friday_digests/`, `weekly-adjustments.json` (Monday batch reads it), `adjustments_log.jsonl`. Run by scheduled task `vp-publer-analytics-friday`.
- `casual_video_processor.py` — **(2026-07-06 strategic build)** casual phone-video pipeline: Whisper (faster-whisper) captions burned in, lower-third, brand end-card, 9:16 normalize, auto-schedule to Brand FB/IG/TikTok/X via Publer. Inbox: `Valley Pawn Studios/casual-video-inbox/`. Run daily 7 PM by `vp-casual-video-daily`.

## Content strategy (2026-07-06 strategic build)
- `PILLAR_OVERLAY.md` — **authoritative** Community (15-20%) + Humor (≤10%) pillar rules + adjust-loop contract. The vp-content-batch-weekly runner reads this at Step 0.5; it wins over the skill cache.
- `hook-library/community.json` — 15 community hooks (per-region + valley-wide). No-CTA rule, 45-day cooldown.
- `hook-library/humor.json` — 10 dry-humor hooks, STYLE-D, hard boundaries, 60-day cooldown.
- `weekly-adjustments.json` — written each Friday by the digest; consumed each Monday by the batch.

## Config
- `publer_config.json` — `{api_key, api_base, workspace_id}` for Publer Business tier.
- `publer_accounts.json` — store_key → Publer ID mapping for all 9 connected accounts (6 Facebook Pages, 1 IG, 1 TikTok, 1 X).

## Content folder
- `brand_assets/`
  - `valley_pawn_profile_1080.png` — 1080×1080 square for X/IG/TikTok profile pics
  - `valley_pawn_x_header_1500x500.png` — X header banner

## Test artifacts (safe to clean up periodically)
- `_test_twitter_manifest.json` + `_test_twitter_manifest_publish_results_*.json` — leftover from the 2026-06-19 X post test cycle.

## Playbooks / docs (reference)
- `META_TASKS_PLAYBOOK.md` — 2026-05-26 Meta UI tasks playbook (mostly historical now)
- `META_APP_REVIEW_SUBMISSION.md`, `META_SUPPORT_*.md` — Meta App Review and support escalation drafts
- `NEW_ROANOKE_PAGE_SETUP.md` — Roanoke Page creation/conversion history
- `AUDIT_INVENTORY.md` — asset audit + ownership consolidation plan
- `VP_30_DAY_CONTENT_CALENDAR.md` — first-month content calendar
- `friday_close_report.md` — most recent Friday engagement report output

## Manifest format (input to vp_social_publisher.py)
```json
{
  "batch_id": "vp-content-batch-YYYY-MM-DD",
  "items": [
    {
      "id": "item-NNN",
      "routing_tier": "brand" | "store-local" | "fan-out",
      "store_keys": ["Brand", "BrandIG", ...],
      "caption": "...",
      "image_url": "https://...",
      "video_url": null,
      "scheduled_at": "2026-06-22T09:00:00Z",
      "status": "approved"
    }
  ]
}
```

## How to run hands-off
```bash
# Dry-run (validate routing, no publish):
python3 vp_social_publisher.py /path/to/manifest.json --dry-run

# Live publish (returns job_id per item):
python3 vp_social_publisher.py /path/to/manifest.json
```

## Phase 2 (planned, not yet built)
- `follow.thevalleypawn.com` → Publer Linkie page
- Counter QR cards × 5 stores
- $100/month giveaway draw automation (last day of month)
- VA-compliant Official Rules at follow.thevalleypawn.com/rules
- Cross-promo posts from FB/IG → driving X/TikTok adoption
- SMS launch blast via Brevo
- Email launch blast via Brevo

## Related skills (read context)
- `vp-content-batch` — generates the weekly approved-manifest that flows in here
- `vp-brand-studio` — visual identity reference for any image assets
- `valley-pawn-context` — brand voice / rules
- `bravo-context` — POS source data for content (top sellers, new arrivals)
- `expert-review-board` — decision governance (pawn shop operator now permanent seat)
