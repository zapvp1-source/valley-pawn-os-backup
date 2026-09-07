# Refine Social Media — Folder Index
_Rewritten 2026-09-06. The previous version (2026-07-07) described a 9-account Publer setup with
no lanes, no drift engine and no KB — three generations behind the code._

## Read these first, in this order
1. **`SOCIAL_SYSTEM_SPEC.md`** — the canonical spec: publishing reality, routing, cadence targets,
   the Publer landmines, the hard rules, and the engine's command reference. It wins over every
   other document in this folder.
2. `SOCIAL_DEPT_REVIEW_AND_PLAN_2026-09-05.md` — the department audit and the 5-phase plan
   (Phases 0–2 built 2026-09-06; Phase 3 consolidation still pending Joshua's go).
3. `PILLAR_OVERLAY.md` — pillar percentages, community/humor lane rules, the adjust-loop contract.
4. `CALENDAR_AUG_DEC_2026.md` — the seasonal calendar through January.

## The engine — `vp_social/`
One deterministic package. **All publishing, all Publer reads, and every reported number go
through it.** See `SOCIAL_SYSTEM_SPEC.md` §6 for commands.

| Module | Role |
|---|---|
| `config.py` | paths, account map, canonical store facts, cadence rules, DRY_RUN switch |
| `reader.py` | the ONLY Publer reader — always sends `from`/`to`, always paginates |
| `ledger.py` | `state/social_ledger.sqlite` — `posts`, `planned`, `runs`; synced from Publer |
| `plan.py` | weekly planner: fills each account to target, de-duplicates, writes slot contracts |
| `publish.py` | the ONLY Publer writer — QA gates, idempotent by ledger key, DELETE refused |
| `report.py` | deterministic recap / digest / quota / postflight / month formatters (exit 2 = withhold) |
| `cli.py` | `python3 -m vp_social <command>` |
| `_migrations/` | one-off migration scripts + the launchd runner and its bootstrap |

State lives in `state/` (`social_ledger.sqlite`, `plans/`, `logs/`, `DRY_RUN`).

## Still load-bearing outside the engine
- `publer_client.py` / `publer_accounts.json` / `publer_config.json` — the transport the engine
  subclasses. 15 accounts.
- `creative_drift.py` + `creative_state.json` + `CREATIVE_DRIFT.md` + `CREATIVE_LEDGER.md` —
  format selection, cooldowns, quarterly refresh.
- `CITY_COMMUNITY_KB.md` — the community lane's source of real local facts, with `[C26]` /
  `[PATTERN]` / `[VERIFY]` tags.
- `vp_deal_reel.py`, `vp_deal_compilation.py`, `vp_deal_reel_publish.py`, `vp_comedy_reel.py`,
  `casual_video_processor.py` — the renderers (PIL + ffmpeg + whisper).
- `publer_weekly_digest.py` — still writes `weekly-adjustments.json`, `adjustments_log.jsonl`,
  `friday_digests/`, `lessons.md`. Its post COUNTS are superseded by `vp_social digest`.
- `quota_watchdog.py` — correct (it always passed from/to); `vp_social quota` is the newer path.
- `engagement_lane/`, `_lane_c/`, `hook-library/`, `reels/`, `manifests/`, `deal_of_week_uploads/`.

## Superseded — do not build on
- `weekly_social_recap.py` — queried Publer with no date range; reported 15 posts for a week that
  had 88. Replaced by `python3 -m vp_social recap`.
- `publish_batch_2026-08-31.py`, `vp_content_batch_storelocal_2026-08-24.py`,
  `publish_store_deals_2026-08-21.py`, `publish_comedy_reels_2026-08-2*.py` — hand-written
  one-off publishers, each bypassing the QA gates. Use `vp_social publish`.
- `friday_close_engagement.py` / `_publer.py`, `friday_close_report.md` — dead since May.
- `giveaway_monthly_draw.py` — a stub pointing at a "Linkie API" that doesn't exist; entries are
  in Brevo. No drawing has ever run.
- `facebook-post` / `reel-comment-alert` skills — Meta Graph tokens dead since 2026-08-21.
- `VP_30_DAY_CONTENT_CALENDAR.md`, `LAUNCH_CAMPAIGNS.md`, `META_*.md`, `LINKIE_BUILD_SHEET.md`,
  `NEW_ROANOKE_PAGE_SETUP.md`, `vp-social-publisher_SKILL.md` (stub), `acrylic_signs*/`,
  `counter_cards/`, `canva_proofs/`, `_test_twitter_manifest*`, and the dated `_run_*.sh` /
  `_fix_*.py` / `_verify_*.py` / `_probe_*.py` scaffolding — historical only.

## Who does what now
- **Managers:** one deal photo + price in `#deal-of-the-week` by Monday noon; a phone video when asked.
- **Scheduled tasks:** produce creative, call the engine to publish, post the engine's output verbatim.
- **The engine:** decides what may publish, publishes it once, and is the source of every number.
- **Joshua:** nothing weekly. One Monday log card, one Friday digest. Failures never reach Slack
  (Rule 16) — they go to `Valley Pawn Studios/STATUS.md`.
