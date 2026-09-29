# Bravo Monthly Scrap Closeout — Autopost Spec (added 2026-09-28)

Companion to `OPERATING_GUIDE.md` (Phase A: email → allocation workbook) and
`BRAVO_BUCKET_CLOSEOUT.md` / `PRECIOUS_METALS_MONTHLY_POSTING_SPEC.md` (the manual
Bravo procedure the AHK handler automates). This doc is the spec for the NEW
recurring automation that closes the loop end to end with only ONE approval
from Joshua per month.

## Why this exists

Joshua, 2026-09-28: *"Lets fix the automated tool first since that will be the
long standing solution, i dont want to have to sit and watch this in the
future, as long as i approve the numbers split from the elemetal email, we
should just execute."*

Business-process change (also 2026-09-28): scrap settlement payment timing was
accelerated. Elemetal now pays for a month's scrap buckets WITHIN that same
month (previously it lagged a month — e.g. August buckets got paid by
September wires). **Going forward: buckets named for month M are closed using
money received in month M, processed on the 1st of month M+1.**

## Two-task design (additive — neither touches existing hardened infra)

Splitting staging (read-only) from posting (money-moving) means a bad manifest
never reaches Bravo without a live human look at the dollar amounts, while
still requiring only ONE reply from Joshua, not per-bucket clicks.

### Task 1 — `scrap-monthly-bravo-manifest-stage`
Cron: `45 9 1 * *` (9:45 AM local, 1st of every month — 45 min after the
existing daily `precious-metals-settlement-handler` task's 9:00 AM run, so
that task has already found last month's Elemetal settlement email(s) and
written/refreshed `reviews/<prior-month>_allocations_REVIEW.csv` if one is
due).

Steps each run:
1. Determine target month = the previous calendar month (e.g. run on 10/1,
   target month = 2026-09).
2. Look for `Precious Metals Settlements/reviews/<target-month>_allocations_REVIEW.csv`
   (or a `_CLOSED.csv` if somehow already approved — in that case there is
   nothing to stage, exit quietly). If neither exists, there is no settlement
   for that month yet — write one row to the fleet FAILURE_LEDGER per the
   platform failure policy (`NEEDS_HUMAN: no` — this is routine, the daily
   handler will pick it up once Elemetal's email arrives) and stop. Do NOT
   invent numbers.
3. If a REVIEW workbook exists, read its BUCKET DETAIL section (store,
   bucket name, type, amount). Bucket names for ALL 5 stores now follow the
   `<YYYY-MM> GOLD` / `<YYYY-MM> GOLD WITH STONES` convention (confirmed for
   HAR 2026-09-28 — HAR's older manifests used legacy names like
   `GOLD W/O STONES`; those are historical only, never use them for a new
   month). If the workbook's BUCKET DETAIL section uses a different name,
   trust the workbook — it reflects what Bravo actually showed when built —
   but flag the deviation from convention in the Slack notification.
4. **Live-weight-gate the manifest before staging it** — this is the step
   that makes the automation safe to run unattended. For each of the 10
   buckets, get the CURRENT live weight in Bravo:
   - Stage a read-only manifest with `"listOnly": true, "allStatus": true`
     and the 5 stores, drop it in
     `Bravo Data Extraction/triggers-scrap/scrap-monthly-<target-month>-list.json`,
     queue a host-queue job calling
     `Valley Pawn OS/bin/scrap_closeout_run.sh scrap-monthly-<target-month>-list 900`
     (already allow-listed), wait for
     `Bravo Data Extraction/results-scrap/scrap-monthly-<target-month>-list.buckets.csv`.
   - For each of the 10 target buckets, find the row matching the expected
     name (occurrence 0 = the newest/topmost match — same name should only
     appear once per month going forward under the new convention) and read
     its live weight the same way `CloseoutOneBucket`'s weight gate does
     (open the bucket, read `Combined Metal Weight`). If a script needs to do
     this bucket-by-bucket, reuse `Valley Pawn OS/bin/scrap_closeout_run.sh`
     in the same `listOnly`+`allStatus` mode — it is zero-mutation, safe to
     run any time.
   - Build the real manifest: `{"id": "scrap-closeout-<target-month>", "buckets": [{"store", "bucketName", "occurrence": 0, "expectedWeightDwt": "<live weight read just now>", "amountPaid": "<from the REVIEW workbook>", "tenderType": "Cashiers Check"}, ...]}` for all 10 gold buckets (never silver — silver is a separate, still-manual settlement).
   - Save it to `Bravo Data Extraction/triggers-scrap/pending-approval/scrap-closeout-<target-month>.json`
     — the `pending-approval/` subfolder, NOT `triggers-scrap/` directly, so
     nothing executes before Joshua approves (the watcher only watches
     `triggers-scrap/` itself).
5. Post ONE Slack DM to Joshua (channel `D03BHQH5VGT`) with:
   - The store-by-store dollar table from the REVIEW workbook.
   - The live-weight-gate confirmation (all 10 buckets matched within
     tolerance — if any did NOT match / could not be found, say so plainly
     and do NOT ask for approval on that bucket; list it as needing his
     attention separately).
   - One line: *"Reply 'post' in this thread to close these buckets in Bravo
     automatically. Reply 'hold' to pause this month."*
6. Write the pending-approval state to
   `Precious Metals Settlements/logs/monthly_autopost_pending.json`:
   `{"month": "<target-month>", "manifest_id": "scrap-closeout-<target-month>", "slack_channel": "D03BHQH5VGT", "slack_ts": "<the notification message's ts>", "staged_at": "<ISO time>"}`.
   This is what Task 2 polls.
7. Respect the fleet publish guard (`vp_dryrun.py status`) before the Slack
   post, same as every other task in this project.
8. Follow the standard failure policy (`FAILURE_LEDGER.md` row, no direct
   DM) for anything that fails along the way — except the final approval
   request itself, which IS the one Slack post this task is allowed to make.

### Task 2 — `scrap-monthly-bravo-approval-watch`
Cron: `0 */3 * * *` (every 3 hours, all day, every day — cheap no-op when
there's nothing pending).

Steps each run:
1. Read `Precious Metals Settlements/logs/monthly_autopost_pending.json`. If
   it doesn't exist or is empty, exit immediately — no Slack post, no log
   noise, nothing (this must be a silent no-op the vast majority of runs).
2. If a pending entry exists, read the Slack thread at
   `slack_channel`/`slack_ts` for any reply from Joshua since `staged_at`.
3. **No reply yet:** if less than 10 days have passed since `staged_at`, do
   nothing this run. If 10+ days have passed with no reply, this needs a
   human — write a `FAILURE_LEDGER.md` row with `NEEDS_HUMAN: yes, approve or
   hold the pending <target-month> scrap closeout` so `fleet-guardian` rolls
   it into Joshua's daily DM, then leave the pending state in place (don't
   clear it — a late reply should still work).
4. **Reply contains "post" (and not "hold"/"wait"/"no"/"stop"):**
   - Move `Bravo Data Extraction/triggers-scrap/pending-approval/scrap-closeout-<month>.json`
     into `Bravo Data Extraction/triggers-scrap/` (this is what makes it
     live/pickupable).
   - Queue a host-queue job calling
     `Valley Pawn OS/bin/scrap_closeout_run.sh scrap-closeout-<month> 2700`
     and wait for the result file.
   - Read the result JSON. Any bucket with `verified: false` or a
     `WEIGHT MISMATCH`/error: do NOT treat the run as fully done — reply in
     the same Slack thread with exactly which bucket(s) need a human look
     (plain language, per the field-communication rule), and write a
     `FAILURE_LEDGER.md` row `NEEDS_HUMAN: yes`. Buckets that DID close
     successfully are still final — say so.
   - All 10 verified: reply in the Slack thread with the final total and
     confirm it matches the approved split. Rename the workbook
     `reviews/<month>_allocations_REVIEW.csv` → `_CLOSED.csv` (or add a
     `_CLOSED` note the way the 2026-08 workbook does — do not delete the
     REVIEW). Append one line to `Valley Pawn OS/CHANGELOG.md` and update
     `Precious Metals Settlements/logs/state.json`.
   - Clear `monthly_autopost_pending.json` (delete it or empty it) so Task 2
     goes back to being a silent no-op.
5. **Reply contains "hold"/"wait"/"no"/"stop":** clear
   `monthly_autopost_pending.json` without posting the buckets, log one row
   to `Life OS/OPEN_ITEMS_REGISTER.md` noting the month was held and why (if
   Joshua said why), and stop. This mirrors the exact pattern from
   2026-09-28's manual run, where Joshua chose "Hold — don't post yet" before
   later approving after an explanation.

## Bucket naming convention (confirmed live 2026-09-28)

All 5 stores now use `<YYYY-MM> GOLD` (no stones) and
`<YYYY-MM> GOLD WITH STONES` (with stones), created near the 1st of the
bucket's own month. This replaces HAR's older ad-hoc names
(`GOLD W/O STONES`, `GOLD W STONES`, `AUGUST GOLD...`, etc., all still visible
in Bravo's history but never to be used for a NEW month's manifest). Always
prefer what the workbook's own BUCKET DETAIL section says (built from a live
Bravo read) over this convention if they ever disagree — the convention is a
sanity check, not a hard rule.

## Safety properties inherited from the 2026-09-28 hardening of
`Bravo Data Extraction/reports/ScrapBucketCloseout.ahk`

- **Weight gate**: a bucket is never touched unless its live weight matches
  the manifest's `expectedWeightDwt` within 0.05 dwt.
- **Idempotent**: an already-CLOSED bucket is read back and reported, never
  re-posted — safe to re-run a manifest.
- **Numeric-tolerant verification**: field values are compared numerically
  (e.g. `0.44` == `0.440`), not as exact strings.
- **`listOnly`+`allStatus` inventory mode**: zero-mutation, safe to run any
  time to see every bucket regardless of status (OPEN/Shipping/Received/
  Assayed/Closed).
- **Silver is out of scope** for this whole automation — silver settlements
  remain manual until a session builds that out separately.

## Open follow-ups (see `Life OS/OPEN_ITEMS_REGISTER.md` 2026-09-28 row)

- Clean up this session's scratch trigger/manifest/host-queue files under
  `Bravo Data Extraction/triggers-scrap/` and `Valley Pawn OS/fleet/host_queue/`.
- First live run of this two-task automation should be watched loosely (not
  per-bucket, just confirm the Slack approval round-trip works) before
  trusting it fully unattended.
