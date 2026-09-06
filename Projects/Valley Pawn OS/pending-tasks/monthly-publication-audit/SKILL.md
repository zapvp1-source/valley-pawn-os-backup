---
name: monthly-publication-audit
description: 2nd and 4th of month, 10 AM — verifies every MONTHLY publication in Valley Pawn OS/PUBLICATION_CALENDAR.md actually landed for the prior month (reads the channel, not run records), re-runs rerun-safe producers in-session when a post is missing, and DMs Joshua one plain line only if something could not be recovered. The monthly net the fleet-guardian cannot provide (its 48-hour staleness rule hides 1st-of-month misses by the 3rd).
model: claude-sonnet-5
cron: 0 10 2,4 * *
---

<!-- NOT YET REGISTERED. Creating this task from an autonomous session was blocked by the app's
     permission classifier on 2026-09-05. To register: in a Cowork chat say "create the
     monthly-publication-audit scheduled task from Valley Pawn OS/pending-tasks/monthly-publication-audit/SKILL.md,
     cron 0 10 2,4 * *" and approve the prompt. Until then, fleet-guardian covers the same entries
     (fleet/expected_outputs.json) but only within 48 h of each producer's fire time. -->

You verify that every MONTHLY publication for the prior month actually landed, and recover the ones that didn't.

CONTEXT LOAD: invoke `enterprise-map` first (osascript fallback if the Projects folder is not mounted), then `vp-operating-rules`. Read `Valley Pawn OS/PUBLICATION_CALENDAR.md` (MONTHLY table) and `Valley Pawn OS/fleet/expected_outputs.json` (entries whose cadence starts with `monthly-`), plus `Valley Pawn OS/fleet/rerun_manifest.json`.

STEP 1 — Verify against output (Rule 12). For each monthly entry whose cadence day is ≤ today's day-of-month: search the entry's channel (include bot/webhook messages) for the entry's marker since the 1st of THIS month. Present → healthy. Absent → MISSED. Ignore entries whose cadence day is still in the future this month (e.g., day-10 bonus items on the 4th; day-16 gun audit).

STEP 2 — Classify. Task in `rerun_safe` → recoverable in-session. Anything else → verify-only: never execute; record it.

STEP 3 — Recover, one at a time, in this order if several are missing: monthly-analytics-report (check the sidecar first — `Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/` needs 30 files ≥ 2 KB; if not, launch `cd "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin" && nohup /usr/bin/python3 monthly_prestage_runner.py --report-month {YYYY-MM} >> "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/logs/launcher.out" 2>&1 &` and poll until 30/30, up to 90 min, before running the report), then monthly-employee-sales-rankings, monthly-scrap-rankings, nics-monthly-ranking, vp-new-customer-report, monthly-ebay-ratings-sweep. For each: read its SKILL.md at `~/Documents/Claude/Scheduled/<task>/SKILL.md` (osascript) and execute it faithfully for the prior month, honoring its own duplicate guards, completeness gates and failure policy. Before any Bravo-touching rerun, wait until the pipeline queue is idle (no pending `*.json` in `Bravo Data Extraction/triggers/`, nothing in `triggers/claimed/` newer than 2 h). Confirm each recovered post actually landed by reading the channel back. Budget: stop starting new reruns after 3 hours; queue the rest in the log for the next audit day.

STEP 4 — Log. Write `Valley Pawn OS/fleet/publication_audits/{YYYY-MM-DD}.json` via osascript heredoc (mkdir -p): checked, healthy, missed, recovered (permalinks), unrecovered, verify-only misses. Add one dated line under `## {today}` at the top of `Valley Pawn OS/CHANGELOG.md`.

STEP 5 — Alert only if needed. Everything healthy or recovered → completely silent. Something unrecovered → ONE plain-language DM to Joshua (D03BHQH5VGT), e.g. "The {Month} gold scrap rankings still haven't gone out — needs a look." No technical detail, no jargon, no file names (Rule 16). Never post anything to a team channel from this task except the recovered publications themselves.

Hard rules: additive only — never edit a producer's SKILL.md, handler, or the runner; all file I/O via osascript; Rule 18 — never post a partial or caveated publication as a recovery; never post a monthly report to #store-performance.
