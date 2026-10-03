---
name: scrap-bucket-name-check
description: 5th, 15th and 25th of each month, 10:15 AM — read-only check of every store's gold and silver scrap bucket names in Bravo; if a store named one wrong, Slack its manager one reminder with the correct names.
model: claude-sonnet-5
---

Domain 1 (Full Circle Finance Inc DBA Valley Pawn). Load `enterprise-map` conventions first. Paths are relative to `/Users/joshuadavis/Documents/Claude/Projects/`.

PURPOSE (Joshua's standing direction, 2026-10-02): "if you find gold buckets or silver buckets are named improperly, message the manager." Bucket names must be standard so the monthly Elemetal payout closeout (`scrap-monthly-bravo-manifest-stage` / `-approval-watch`) can find them. Example of the problem: Lexington named September's buckets "2026-09 GOLD SCRAP" / "2026-09 GOLD STONE SCRAP".

STANDARD NAMES (M = the bucket's month as YYYY-MM):
- `M GOLD`
- `M GOLD WITH STONES`
- `M SILVER` (a store may also have `M SILVER WITH STONES` — that is acceptable, not a violation)
Platinum or other metals: ignore. Only check buckets that are not CLOSED and whose CreatedOn is in the current or previous calendar month (older legacy names like "GOLD W/O STONES 7/31/26" or "JULY 2026 GOLD SCRAP" are history — ignore anything created before 2026-10-01).

STEPS:
1. Bravo contention: the run script below already waits for the Bravo foreground guard. Do not use screen control.
2. Zero-mutation bucket inventory of all 5 stores: write `Bravo Data Extraction/triggers-scrap/scrap-namecheck-<YYYYMMDD>.json` = `{"id":"scrap-namecheck-<YYYYMMDD>","listOnly":true,"allStatus":true,"buckets":[{"store":"CUL","bucketName":"x","amountPaid":"0","tenderType":"Cashiers Check"},{"store":"HAR",...},{"store":"LEX",...},{"store":"ROA",...},{"store":"WAY",...}]}` (same shape for each store). Queue it with a host-queue job file `Valley Pawn OS/fleet/host_queue/<YYYYMMDD-HHMM>-scrap-namecheck.sh` containing a comment line and `bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_closeout_run.sh" scrap-namecheck-<YYYYMMDD> 1500`. Poll every ~2 min (up to ~30 min) for `Bravo Data Extraction/results-scrap/scrap-namecheck-<YYYYMMDD>.buckets.csv` (columns Store, BucketName, CreatedOn, Status, StatusDate). If it never appears (Bravo down/busy), append one FAILURE_LEDGER row `NEEDS_HUMAN: no` and stop — the next scheduled run retries.
3. For each store, take every bucket in scope (see above) whose name contains GOLD or SILVER. A name is WRONG if it does not exactly equal one of the standard names for its month (case-insensitive, trim spaces). Infer the month from the name's YYYY-MM if present, else from CreatedOn. Also flag a store that has two open buckets for the same month and type.
4. Dedupe: read/write `Precious Metals Settlements/logs/bucket_name_reminders.json` (create if missing) — a list of {store, month, bad_name, sent_at}. Never message the same store twice for the same month + bad name. If a store fixed the name since the last reminder, note it in the file (fixed_at) and send nothing.
5. Who to message: the store's Manager from `Valley Pawn OS/hr/ROSTER.json` (employees where department = store name and title contains "Manager", use slack_id). CUL=Culpeper, HAR=Harrisonburg, LEX=Lexington, ROA=Roanoke, WAY=Waynesboro. If a store has no manager with a slack_id, send the reminder to Preston Peters (U03BWMEM9GR) instead and say which store.
6. Fleet publish guard before any Slack send: `python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status` — exit 0 (armed) → write the would-be messages to `Valley Pawn OS/fleet/test_output/scrap-bucket-name-check-<timestamp>.txt` instead; exit 1 → send.
7. Send ONE Slack DM per store with violations (Slack connector, DM the manager's user id). It goes out as Joshua, so write it in his voice — short, no greeting beyond "Hey <first name>", no sign-off, no bullets beyond the name list. Template:
   "Hey <name> quick one on scrap buckets. <Month word> got named "<bad name 1>"<and "<bad name 2>">. All stores need to use the same names so the payouts post right:

   <M> GOLD
   <M> GOLD WITH STONES
   <M> SILVER

   Same format every month, just change the month. Can you rename those so they match?"
   (For a duplicate-bucket violation, say there are two open <type> buckets for <month> and ask them to combine into one.)
8. Log each send to `bucket_name_reminders.json`. Do NOT DM Joshua about sends or about clean results; if nothing is wrong, the run is silent.

Never rename, create, or change any bucket in Bravo yourself. Never touch the closeout manifests. Failure policy: one row to `Valley Pawn OS/fleet/FAILURE_LEDGER.md` as `| <YYYY-MM-DD HH:MM ET> | scrap-bucket-name-check | <one plain sentence> | NEEDS_HUMAN: ... | OPEN |`.

This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.