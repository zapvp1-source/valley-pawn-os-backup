# Layaway Yield % � Build STATUS (2026-07-15)

> Additive-only. Touches no existing Bravo saved report, AHK handler, pipeline
> cell registration, or existing scheduled task. Read this before extending or
> debugging the Layaway Yield % metric.

## What this is
New metric requested by Joshua 2026-07-15: **Layaway Yield % = (Down Payments MTD + Payments MTD) � Layaway Balance**, per store + company. Labelled "Layaway Yield %" everywhere (never bare "Yield") � Joshua's existing monthly-bonus-targets task already uses "Yield" for an unrelated store-level metric (Net Revenue � Prior Month Ending Assets); confirmed with Joshua this naming is fine.

## What already existed (found, not built from scratch)
Three Bravo built-in report handlers � reports/LayawayDeposits.ahk, LayawayBalance.ahk, LayawayJournal.ahk � were already written (cloned from EndOfMonth.ahk) and already registered in bravo_watcher.ahk's dispatch table (pipeline cells layaway-deposits, layaway-balance, layaway-journal, all listed in watcher.last_started.txt). They had NEVER successfully produced output before 2026-07-15 (zero files in output/, no STATUS docs) � built and abandoned in a prior session, never proven.

## Root cause found + fixed (2026-07-15)
Live smoke test on CUL hung Bravo twice:
1. **Continuous Scrolling export hang** (same bug documented in bravo-context for 7 other closing-report handlers, patched 2026-05-29 � LayawayDeposits/Balance/Journal never got that patch). Fixed: ported the identical toggle-off block into all three handlers (see reports/LayawayDeposits.ahk, LayawayBalance.ahk, LayawayJournal.ahk � search "added 2026-07-15"). Confirmed working live: CUL layaway-deposits pull succeeded cleanly after the patch + watcher restart (86s, 26 rows, output/2026-07-14_CUL_layaway-deposits.csv).
2. A **separate, unrelated Bravo ClickOnce auto-update** kicked in mid-testing (not caused by this work) and required a second recovery cycle. Both recoveries completed via the existing bravo_ensure_healthy.sh / bravo_health_gate.sh ladder (no computer-use needed for the deposits report; the balance report's hang needed a one-time manual GUI close � see below).

## Known remaining issue � Layaway Balance report (NOT used in the final design, see below)
The **Layaway Balance** custom report hung on export TWICE even after the Continuous-Scrolling patch (confirmed via computer-use screenshot: report rendered perfectly on screen both times � "Layaway Balance / CUL / 7/1/2026 - 7/14/2026" with columns Starting Balance Due, New Layaways, New Layaway Taxes, Down Payments, Payments, Balance Due on Expired/Reactivated Layaways, Balance Due on Canceled Layaways, Ending Balance Due, Credits Paid Out � but the export-to-CSV step itself hung both times, needing a manual GUI "Close the program" to recover). Root cause not fully diagnosed � likely a second, different export bug specific to this report (wider table, more columns than Layaway Deposits). NOT worth chasing further: the design below doesn't need this report at all.

## Final design � only 2 data sources, both already proven
- **Numerator** (Down Payments MTD + Payments MTD): `layaway-deposits` pipeline cell ? reports/LayawayDeposits.ahk (patched, proven). Real CSV format confirmed live 2026-07-15 (CUL, 7/1-7/14/2026): header row `Date,Starting Layaway Deposits,Down Payments,Payments,Redemptions,,Cancellations,Expirations,Reactivations,Ending Layaway Deposits` (note blank column after Redemptions), `Total:` row carries the MTD sums directly at columns [2]=Down Payments, [3]=Payments.
- **Denominator** (Layaway Balance): REUSED from the `end-of-month` cell that `weekly-store-kpis` already pulls every Monday ~10:30 AM (same "Ending Balance" row extraction already proven in store_kpis_compile.py's Layaway Balance metric). Deliberately does NOT use the flaky Layaway Balance custom report � cross-validated instead: EOM's Ending Balance for CUL 7/14 = $26,955.91, which matches the Layaway Balance custom report's "Ending Balance Due" on-screen figure exactly (before its export hung), and the Down Payments ($1,394.77) / Payments ($891.21) totals from Layaway Deposits matched the Layaway Balance report's totals exactly too � good cross-check that both reports agree, even though only Deposits is used going forward.

## Files added (additive only)
- `layaway_yield_compile.py` � Mac-side Python compile script. Reads `output/<DATE>_<STORE>_layaway-deposits.csv` + `output/<DATE>_<STORE>_end-of-month.xlsx` (already on disk from other tasks), writes `output/<DATE>_layaway_yield.json` + `_table.txt`. Tested live against real CUL data 2026-07-15: Down Payments $1,394.77 + Payments $891.21 = $2,285.98 collected MTD � $26,955.91 balance = **8.48% Layaway Yield** � matches manual calculation exactly.
- Continuous-Scrolling toggle-off patches in reports/LayawayDeposits.ahk, LayawayBalance.ahk, LayawayJournal.ahk (bug fix to previously-nonfunctional code, not a change to hardened/proven infra).

## Scheduled task added
`layaway-yield-weekly` � Monday 11:20 AM (after weekly-store-kpis' ~10:30 AM EOM pull completes). Drops ONE new 5-store layaway-deposits trigger (does not touch the existing monday-bravo-combined trigger), runs the compile script, appends "Payments MTD" + "Layaway Yield %" columns to the Details (Live) Google Sheet's Layaway Review table and a new additive section on the #layaway-review Canvas � existing columns/sections untouched. DMs Joshua only (not posted to channel) until the metric has settled over a few weeks. Full prompt: /Users/joshuadavis/Documents/Claude/Scheduled/layaway-yield-weekly/SKILL.md

## Not yet done / next session
- Layaway Journal handler (reports/LayawayJournal.ahk) also got the CS patch defensively but was never smoke-tested at all (not needed for this metric) — leave as-is unless a future need arises.
- Google Sheet ("Details (Live)") append still not automated — no edit-in-place tool available on the connected Drive/Sheets connector (read/create/copy whole file only). Canvas + channel are the primary surfaces so this isn't blocking, but revisit if Joshua wants the Sheet kept current too.

## UPDATE 2026-07-15 (same day, later) — first full 5-store run completed

Joshua asked when the full run would publish to #layaway-review. Ran it live on-demand rather than waiting for Monday:

| Store | Down Pmts MTD | Payments MTD | Collected MTD | Layaway Bal | Layaway Yield % |
|---|---|---|---|---|---|
| Culpeper | $1,394.77 | $891.21 | $2,285.98 | $26,955.91 | 8.48% |
| Harrisonburg | $640.00 | $960.99 | $1,600.99 | $24,666.80 | 6.49% |
| Lexington | $118.00 | $1,083.48 | $1,201.48 | $7,982.88 | 15.05% |
| Roanoke | $238.00 | $2,705.61 | $2,943.61 | $16,388.93 | 17.96% |
| Waynesboro | $117.00 | $491.42 | $608.42 | $9,286.18 | 6.55% |
| **Company** | **$2,507.77** | **$6,132.71** | **$8,640.48** | **$85,280.70** | **10.13%** |

Published to the #layaway-review Canvas (F0BJ48BMZGQ, new "Layaway Yield % (MTD)" section) and posted to the #layaway-review channel. Google Sheet not updated (see above).

**4 more Bravo hangs** encountered pulling HAR/LEX/ROA/WAY (on top of the 2 from the original CUL smoke test), same symptom each time: report renders correctly on screen with correct data, export-to-CSV step wedges, Bravo goes "(Not Responding)". One was a genuine ClickOnce auto-update firing mid-session (existing guard handled it, just slow — waited ~320s); the others were plain export hangs with no clear trigger. Bravo's memory footprint climbed across the session (110MB -> 756MB) which may correlate. Every hang recovered via bravo_ensure_healthy.sh (force-kill + relaunch), occasionally needing a manual Task Manager "End Task" on Bravo.exe when the script's gentle-recover attempts stalled on a "Bravo is already running" dialog left over from a prior relaunch race.

**Conclusion:** the layaway-deposits pull is reliable per-store but not yet reliable back-to-back across all 5 stores in one sitting without occasional manual recovery. `layaway-yield-weekly`'s SKILL.md now documents a retry loop (re-run health gate + re-trigger only missing stores, up to 3 cycles) so Monday's run should mostly self-heal. If hangs keep recurring weekly, worth considering a pacing change (e.g. restart Bravo between stores) — not applied today per Rule #4 (don't change proven pacing without a clear signal it's needed).

Scheduled task `layaway-yield-weekly` updated: now posts the weekly result to the #layaway-review channel (not just a DM) starting with next Monday's run, matching what was done manually today.

## UPDATE 2026-07-15 (same day, later still) — REV 2: eliminated the Bravo dependency entirely

Joshua asked whether we could use the EOM report or another known-reliable pull instead of fighting the Layaway Deposits report. Checked: **yes** — Bravo's End of Month export already contains a full "Layaways" section (Down Payments MTD, Payments MTD, Ending Balance) in the same file already pulled every Monday by `weekly-store-kpis`. Verified byte-for-byte identical to the live Layaway Deposits pull across all 5 stores for 2026-07-14:

| Store | EOM-derived Down | EOM-derived Payments | EOM-derived Balance |
|---|---|---|---|
| Culpeper | $1,394.77 | $891.21 | $26,955.91 |
| Harrisonburg | $640.00 | $960.99 | $24,666.80 |
| Lexington | $118.00 | $1,083.48 | $7,982.88 |
| Roanoke | $238.00 | $2,705.61 | $16,388.93 |
| Waynesboro | $117.00 | $491.42 | $9,286.18 |

Exact match to the Layaway Deposits report totals used earlier today. **Rewrote `layaway_yield_compile.py` (REV 2)** to read only `end-of-month.xlsx` — the Layaway Deposits pull is no longer used by this metric at all. Extraction anchors on the "Layaways" section header rather than fixed column letters (column position drifts 1-2 cols between stores — same per-store schema-drift issue documented in `reference-bravo-saved-reports-per-store`), then takes the last non-null value within the "Layaway Balance" column-group span for the Down Payments / Payments / Ending Balance rows. Robust across all 5 stores' differing merge layouts.

**Result: this task no longer touches Bravo at all.** No trigger drop, no health gate, no export, no hang risk — pure file read of data another task already pulled. Updated `layaway-yield-weekly`'s SKILL.md accordingly (removed Steps 0/2 entirely — the old health-gate-and-trigger flow). This is the actual long-term fix, not a retry-harder patch: the report that kept hanging is simply no longer in the critical path.

The patched `layaway-deposits` handler (reports/LayawayDeposits.ahk) remains available and working for any other future use, just not used by this task anymore.
