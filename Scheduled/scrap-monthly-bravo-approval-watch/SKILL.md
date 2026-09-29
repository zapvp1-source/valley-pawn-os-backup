---
name: scrap-monthly-bravo-approval-watch
description: Every 3 hours — silent no-op unless a monthly Bravo scrap closeout manifest is pending Joshua's approval. On his "post" reply, closes all 10 buckets unattended via the hardened AHK handler; on "hold", pauses the month.
---

You are running the monthly Bravo scrap-gold-bucket closeout APPROVAL-WATCH task for Valley Pawn (Full Circle Finance Inc). This is Task 2 of a two-task pair — Task 1 (`scrap-monthly-bravo-manifest-stage`, runs 1st of month) stages a manifest and asks Joshua for ONE approval; THIS task watches for his reply and, only on approval, actually posts the buckets in Bravo.

Read the full spec at `/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/BRAVO_MONTHLY_AUTOPOST.md` and follow "Task 2" exactly, step by step.

FIRST ACTION, ALWAYS: read `/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/logs/monthly_autopost_pending.json`. If it does not exist or is empty, this run is a silent no-op — do NOT post to Slack, do NOT write to any log, do NOT call any tool beyond checking that file. Just end immediately with a one-line run-summary saying nothing was pending. This must be cheap and quiet on the vast majority of the ~240 runs/month this task fires.

If a pending entry EXISTS: read the Slack thread named in it (channel `D03BHQH5VGT`, the message at `slack_ts`) for any reply from Joshua since `staged_at`. Follow the spec's exact branches: no reply yet (and under 10 days) → do nothing; no reply after 10+ days → one FAILURE_LEDGER row with NEEDS_HUMAN: yes; reply contains "post" (and not hold/wait/no/stop) → move the staged manifest from `Bravo Data Extraction/triggers-scrap/pending-approval/` into `Bravo Data Extraction/triggers-scrap/`, queue a host-queue job calling `Valley Pawn OS/bin/scrap_closeout_run.sh scrap-closeout-<month> 2700`, wait for the result, verify every bucket shows `verified: true`, reply in the Slack thread with the outcome (plain language — no bucket names/codes/file paths in anything customer- or field-facing, though this is an internal thread to Joshua so plain business language about dollar totals is fine), rename the workbook REVIEW→CLOSED, update `Valley Pawn OS/CHANGELOG.md` and `Precious Metals Settlements/logs/state.json`, then clear `monthly_autopost_pending.json`; reply contains "hold"/"wait"/"no"/"stop" → clear the pending state, log one row to `Life OS/OPEN_ITEMS_REGISTER.md`, stop.

Do not modify `Bravo Data Extraction/reports/ScrapBucketCloseout.ahk` or `scrap_closeout_run.sh` — they are already hardened (2026-09-28) and proven. Use them exactly as documented in the spec and in `Precious Metals Settlements/PRECIOUS_METALS_MONTHLY_POSTING_SPEC.md` / `BRAVO_BUCKET_CLOSEOUT.md`.

Follow the platform-standard failure policy for anything unexpected: append one row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` in the form `| <YYYY-MM-DD HH:MM ET> | scrap-monthly-bravo-approval-watch | <one plain sentence> | <NEEDS_HUMAN: no|yes, ...> | OPEN |` — never DM Joshua directly except the one outcome reply in the existing approval thread described above.

Before any Slack post, check the fleet publish guard: `python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status` — exit 0 (armed) means do the real work but write what you would have posted to `Valley Pawn OS/fleet/test_output/scrap-monthly-bravo-approval-watch-<timestamp>.txt` instead; exit 1 means post normally.

This is an automated run of a scheduled task. The user is not present. Execute autonomously — do not ask for confirmation, do not stop early. End with <run-summary>one or two sentences</run-summary>.