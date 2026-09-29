---
name: scrap-monthly-bravo-manifest-stage
description: 1st of every month, 9:45 AM — stage last month's Bravo scrap gold bucket closeout manifest (live-weight-gated) and post ONE Slack approval request to Joshua. Read-only until he approves.
---

You are running the monthly Bravo scrap-gold-bucket closeout STAGING task for Valley Pawn (Full Circle Finance Inc). This is Task 1 of a two-task pair — you ONLY stage and request approval, you NEVER post/close a bucket in Bravo yourself. Task 2 (`scrap-monthly-bravo-approval-watch`) handles posting after Joshua approves.

First, load context: read `enterprise-map` skill conventions if available, then read the full spec at `/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/BRAVO_MONTHLY_AUTOPOST.md` and follow it exactly — it has the complete step-by-step procedure (determine target month = previous calendar month; find that month's `_allocations_REVIEW.csv`; live-weight-gate all 10 gold buckets via the `listOnly`+`allStatus` read-only Bravo inventory mode and `Valley Pawn OS/bin/scrap_closeout_run.sh`; build and save the manifest to `Bravo Data Extraction/triggers-scrap/pending-approval/` — NOT directly into `triggers-scrap/`; post ONE Slack DM to Joshua at channel `D03BHQH5VGT` asking for a single "post" or "hold" reply; write `Precious Metals Settlements/logs/monthly_autopost_pending.json`).

Also read for context: `Precious Metals Settlements/OPERATING_GUIDE.md`, `Precious Metals Settlements/PRECIOUS_METALS_MONTHLY_POSTING_SPEC.md`, `Precious Metals Settlements/BRAVO_BUCKET_CLOSEOUT.md`, and `Precious Metals Settlements/logs/state.json` for state/history. The Bravo host-queue mechanism, the AHK handler (`Bravo Data Extraction/reports/ScrapBucketCloseout.ahk`), and `scrap_closeout_run.sh` are all already built and hardened (as of 2026-09-28) — do not modify them, only use them via `listOnly`+`allStatus` manifests (zero-mutation) to read live bucket weights.

Silver buckets are explicitly OUT OF SCOPE — only the 2 gold buckets (no-stones, with-stones) per store, 5 stores, 10 buckets total.

If there is no REVIEW workbook for last month yet (Elemetal's settlement email hasn't arrived/been processed), this is routine — do NOT invent numbers, do NOT chase it further than the spec says. Follow the platform-standard failure policy: append one row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` in the form `| <YYYY-MM-DD HH:MM ET> | scrap-monthly-bravo-manifest-stage | <one plain sentence> | NEEDS_HUMAN: no | OPEN |` and stop quietly. Do NOT DM Joshua directly about failures — only the one approval-request Slack DM described in the spec is authorized from this task, and only when a manifest was actually successfully staged.

Before that Slack post, check the fleet publish guard: `python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status` — exit code 0 means armed (do the whole task for real but write what you WOULD have posted to `Valley Pawn OS/fleet/test_output/scrap-monthly-bravo-manifest-stage-<timestamp>.txt` instead of actually posting); exit code 1 means proceed normally.

This is an automated run of a scheduled task. The user is not present. Execute autonomously — do not ask for confirmation, do not stop early. End with <run-summary>one or two sentences</run-summary>.