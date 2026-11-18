# Scrap gold — monthly runbook (set by Joshua 2026-11-17). This file is the procedure; scheduled tasks just point here.

Paths are under /Users/joshuadavis/Documents/Claude/Projects ($HOME/mnt/Projects in device_bash). Stores: CUL, HAR, LEX, ROA, WAY.
Host jobs: write `Valley Pawn OS/fleet/host_queue/<YYYYMMDD-HHMM>-<name>.sh` = one comment line + ONE plain command line (no chaining).
The runner picks it up within ~1–3 min (it is serial; other jobs may be ahead) and moves it to `host_queue/done/` with a `.log`.
Bravo is busy 5:30–9:00 AM ET; a run that reports "Bravo busy … giving up" (exit 4) touched nothing — queue it again later.

## Naming and calendar
- Buckets are named for the month the gold SHIPS: `<YYYY-MM> GOLD` and `<YYYY-MM> GOLD WITH STONES`. Gold only (silver/platinum are not part of this).
- 15th of month M: Claude creates month M+1's two buckets at all five stores (Section C). Stores do not create gold buckets.
- Staff scan into month M's buckets until month M's shipment leaves (~25th–end of month), then into M+1's.
- 10th of month M+1: close month M's buckets with the Elemetal money for that shipment (Sections A, B). If anything is missing, retry daily until the month is CLOSED — there is no cutoff.

## A. Build the split (10th onward, until `reviews/<T>_allocations_CLOSED.csv` exists; T = previous calendar month)
0. Stop silently if `Precious Metals Settlements/reviews/<T>_allocations_CLOSED.csv` exists, or `logs/monthly_autopost_pending.json` already names T.
1. Elemetal emails (Gmail jdavis@fcfpawn.com, `from:noreply@elemetal.com subject:"Settlement information" after:<T>/20`): need one "Scrap Gold Karat" and one "Scrap Gold Stone Removal" settlement whose invoice numbers are in no earlier `reviews/*_CLOSED.csv`. Download each PDF (download_gmail_attachment, `pdftotext -layout`) and record invoice, lot, date, pre-melt dwt, post-melt dwt, gross, and the NET wire (Payment amount). If one is missing: stop silently, tomorrow's run retries; from the 20th on add one row to `Life OS/HUMAN_QUEUE.md`.
2. Read weights AND item costs, read-only, in Bravo's OPEN view. Write `Bravo Data Extraction/triggers-scrap-open/scrap-<T>-cost.json`:
   `{"id":"scrap-<T>-cost","readOnly":true,"buckets":[{"store":"CUL","bucketName":"<T> GOLD","occurrence":0,"amountPaid":"0.00","tenderType":"Cashiers Check"}, … 10 total]}`
   Host job: `bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_readopen_run.sh" scrap-<T>-cost 2400`
   Result: `Bravo Data Extraction/results-scrap/scrap-<T>-cost.result.json` — per bucket `liveWeightDwt`, `itemCount`, `itemsExpected`, `itemCost`. Every bucket must be `status: readonly` with itemCount == itemsExpected. A bucket that errors: re-run just that store once. NEVER conclude a bucket "does not exist" from the all-status list, the year CSVs or a `-newest.png` screenshot — only this OPEN-view read counts (October 2026 was blocked 2 weeks by that mistake).
   If the result id already exists the runner refuses — use a new id (`-b`, `-c`).
3. Split: `python3 "Precious Metals Settlements/bin/build_month_split.py" --root <Projects> --month <T> --gold-net <net> --stones-net <net> --gold-premelt <dwt> --stones-premelt <dwt> --readonly-result <result.json> --map "CUL:<T> GOLD:gold" --map "CUL:<T> GOLD WITH STONES:stones" …` (10 maps). Writes `reviews/<T>_allocations_REVIEW.csv` and `Bravo Data Extraction/triggers-scrap/pending-approval/scrap-closeout-<T>.json`.
4. Gross profit by store = store settlement $ − store itemCost (both buckets). Append the settlements, the weight check (Bravo gold vs Karat pre-melt; Bravo stones vs Stone Removal pre-melt; combined) and the GP table to the REVIEW csv.
5. ONE Slack DM to Joshua (D03BHQH5VGT), plain business language, no file names: both payments, a table by store (settlement, item cost, gross profit, margin), the weight check in one line (say so plainly if a lot is more than 10% off), then: "Reply 'post' in this thread to close these in Bravo. Reply 'hold' to pause." Record the ts.
6. Write `Precious Metals Settlements/logs/monthly_autopost_pending.json` = {"month","manifest_id":"scrap-closeout-<T>","slack_channel":"D03BHQH5VGT","slack_ts","staged_at","gold_net","stones_net","total"}.

## B. Post after Joshua says "post" (approval watch; store hours only: Mon–Sat 10:15 AM–5:15 PM ET, not Wednesday)
1. No pending file → silent no-op. Read the thread. "hold/wait/no/stop" → clear pending, log one row in `Life OS/OPEN_ITEMS_REGISTER.md`, stop. No reply → nothing (after 10 days one HUMAN_QUEUE row).
2. "post": copy the pending manifest to `Bravo Data Extraction/triggers-scrap/scrap-closeout-<T>.json`; host job `bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_closeout_run.sh" scrap-closeout-<T> 4500` (≈6–10 min per bucket).
3. Read the result. `closed` or `already-closed` with `verified: true` = done. Anything else: build a retry manifest (new id `-r1`, `-r2`) with ONLY the unfinished buckets and run it — the handler is idempotent (an already-closed bucket is read back, never re-posted; a bucket whose weight differs from the approved split by >0.05 dwt is refused). Up to 3 retries the same day, then next store-hours day. Known, harmless on retry: "SCRAP vendor row not found" (transient), "CRITICAL POST-SAVE MISMATCH posted amount=''" when Bravo auto-locked before the read-back (the retry reads it back).
   WEIGHT MISMATCH is never retried: tell Joshua which store's bucket changed since he approved.
4. All 10 verified: reply in the thread with the total (must equal the two wires), rename REVIEW → `_CLOSED.csv` with a STATUS line, move the pending manifest to `pending-approval/_done/`, delete the pending json, prepend one CHANGELOG entry.

## C. Create next month's buckets (15th; idempotent — an existing name is skipped)
1. N = next calendar month. Write `Bravo Data Extraction/triggers-scrap/scrap-create-<N>.json`:
   `{"id":"scrap-create-<N>","createOnly":true,"buckets":[{"store":"CUL","bucketName":"<N> GOLD","occurrence":0,"amountPaid":"0","tenderType":"Cashiers Check"},{"store":"CUL","bucketName":"<N> GOLD WITH STONES",…}, … 10 total]}`
   Also include the CURRENT month's two names for every store (they are skipped if present; this self-heals a missed month).
   Host job: `bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_closeout_run.sh" scrap-create-<N> 3600`
2. Result statuses: `created` or `exists`, `verified: true`. Anything else: re-run with a new id (`-b`) once the same day; still failing → one HUMAN_QUEUE row. Creation only makes an empty named bucket; it never touches items, weights or money.
3. No Slack unless something could not be created. Prepend one CHANGELOG line.

## Tools (all in Bravo Data Extraction/reports, driven by the two runners above)
- `ScrapBucketReadOpen.ahk` — read-only (weights + item costs), refuses any manifest that is not readOnly.
- `ScrapBucketCloseout.ahk` — posting (`"readOnly"` dry run, `"listOnly"`, `"createOnly"`, `"forceView"` supported). Finds buckets in the default view, then all-status descending, then all-status ascending.
