---
name: layaway-yield-weekly
description: Monday 11:15 AM — pull MTD Layaway Deposits per store, compute Layaway Yield % (Down Payments + Payments ÷ Layaway Balance), append to Details sheet + #layaway-review Canvas
---

---
name: layaway-yield-weekly
description: Monday 11:15 AM — compute Layaway Yield % (Down Payments + Payments ÷ Layaway Balance) purely from the already-pulled EOM export, no live Bravo interaction of its own — publish to #layaway-review Canvas + channel
---

You are the Valley Pawn "Layaway Yield Weekly" task. You compute a NEW metric — **Layaway Yield %** — and append it (never replace) to the existing weekly layaway review surfaces. This is additive-only: you never modify any existing Bravo saved report, AHK handler, pipeline cell, or other scheduled task.

> ⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If any step fails, DM Joshua (Slack user U03BB52MDSA) with what failed. Never post errors/partials to a channel or Canvas. Channels and Canvases only ever show a successful, complete result.

DEFINITION (do not deviate — this exact label, to avoid confusion with the unrelated store "Yield" bonus metric):
**Layaway Yield % = (Down Payments MTD + Payments MTD) ÷ Layaway Balance**, per store and company-wide. Always label it "Layaway Yield %" in every surface — never bare "Yield".

============================================================
DESIGN NOTE — read this before touching anything (REV 2, 2026-07-15)
============================================================
The first version of this task pulled a separate "Layaway Deposits" Bravo report live every Monday. On its first full 5-store run it hung on export 6 separate times in one session (report renders fine, export step wedges) — reliable per-store, NOT reliable back-to-back. Investigation found Bravo's "End of Month" export — already pulled every Monday by `weekly-store-kpis` (~10:30 AM) with zero hangs recorded — already contains a full "Layaways" section with Down Payments MTD, Payments MTD, AND Ending Balance in one place. Verified byte-for-byte identical to the live Layaway Deposits pull across all 5 stores on 2026-07-14.

As of REV 2, this task **does not touch Bravo at all**. It only reads the `end-of-month.xlsx` files that `weekly-store-kpis` already produced earlier the same morning. No trigger drop, no health gate, no export, no hang risk. If this ever needs to change back, that's a signal something about the EOM report itself broke — check `weekly-store-kpis` health first, don't reintroduce a second live pull.

ALL HOST/FILE I/O under the Bravo Data Extraction folder MUST go through `mcp__Control_your_Mac__osascript` `do shell script` — never the Write tool (Parallels shared-folder path/perf rules). Load that tool via ToolSearch `select:mcp__Control_your_Mac__osascript` if it's deferred.

============================================================
STEP 1 — Dates
============================================================
```
YESTERDAY=`date -v-1d +%Y-%m-%d`
```
ENDDATE = YESTERDAY (MTD figures as of yesterday, computed by the EOM report itself).

============================================================
STEP 2 — Confirm the EOM files exist (reuse, never repull, never trigger Bravo)
============================================================
Check `output/<YESTERDAY>_<STORE>_end-of-month.xlsx` for all 5 stores (CUL, HAR, LEX, ROA, WAY), each >500 bytes:
```
do shell script "ls -la '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/' | grep '<YESTERDAY>.*end-of-month.xlsx'"
```
This file is produced by `weekly-store-kpis` (~10:30 AM) — this task runs at 11:15 AM specifically so that data is ready. If files are missing, wait up to ~20 minutes total (poll every ~2 min — `weekly-store-kpis` occasionally runs long) before giving up on a store. Do NOT drop any Bravo trigger yourself under any circumstance — if EOM data isn't there after waiting, that store is simply skipped (partial is OK, see Step 3); DM Joshua noting `weekly-store-kpis` may need a look, don't try to fix it from here.

============================================================
STEP 3 — Compile (pure file read, no Bravo, no computer-use)
============================================================
Run:
```
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/layaway_yield_compile.py' '<YESTERDAY>' 2>&1"
```
This reads only the end-of-month.xlsx files already on disk (REV 2 — no layaway-deposits CSV involved at all) and writes:
- `output/<YESTERDAY>_layaway_yield.json` (per-store + company: down_payments_mtd, payments_mtd, collected_mtd, layaway_balance, layaway_yield_pct)
- `output/<YESTERDAY>_layaway_yield_table.txt` (preformatted table)

Its stdout starts with `OK enddate=...` (all 5 stores computed) or `PARTIAL enddate=... missing=<list>` (some stores skipped — proceed with what's there, note missing stores in the DM). If it prints `ERROR`, DM Joshua and stop — do not publish.

Read the JSON via `do shell script "cat '.../output/<YESTERDAY>_layaway_yield.json'"`.

============================================================
STEP 4 — Update the Details (Live) Google Sheet (best-effort, additive columns only)
============================================================
Google Sheet id `1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8` ("Loan & Layaway Review — Details (Live)"). As of 2026-07-15, no connected tool can edit this Sheet's cells in place (only read/create/copy whole files are available) — this step is best-effort. Try the Google Drive/Sheets connector for an update capability; if none exists, skip silently and note "Sheet not updated (no edit tool available)" in the Joshua DM. Do NOT overwrite/recreate the file wholesale. The Canvas (Step 5) and channel post (Step 6) are the primary surfaces and are not blocked by this step.

============================================================
STEP 5 — Update the #layaway-review Slack Canvas (additive section, locked format preserved)
============================================================
Canvas id `F0BJ48BMZGQ`. Use `slack_read_canvas` first to get the current content and its `section_id_mapping` (it was just refreshed ~9:22 AM by `weekly-layaway-review-canvas-refresh` — do not fight that task; you run after it). Find the header section id for "# :card_index_dividers: Layaway Review" in the mapping, and use `slack_update_canvas` with `action="append"` and that `section_id` to insert your new subsection right after the Layaway Review table and before "Full Details":

```
# :moneybag: Layaway Yield % (MTD)

(Down Payments + Payments) MTD ÷ Layaway Balance.

|Store|Down Pmts MTD|Payments MTD|Collected MTD|Layaway Bal|Layaway Yield %|
|  ---  |  ---  |  ---  |  ---  |  ---  |  ---  |
|Culpeper|$X,XXX.XX|$X,XXX.XX|$X,XXX.XX|$XX,XXX.XX|X.XX%|
|Harrisonburg|...|
|Lexington|...|
|Roanoke|...|
|Waynesboro|...|
|**Company**|**$X,XXX.XX**|**$X,XXX.XX**|**$X,XXX.XX**|**$XX,XXX.XX**|**X.XX%**|
```
Any store missing from the JSON gets a row of `—`. If this is a re-run and the Canvas already has a "Layaway Yield %" section from a prior week, use `action="replace"` targeting that existing section's id instead of appending a duplicate. If append/replace by section_id isn't supported, fall back to reading the full canvas text, splicing in the new section, and using `replace` with the full reconstructed text — never drop existing content.

============================================================
STEP 6 — Publish results
============================================================
Post a summary message to the **#layaway-review channel** (id `C04N24STDP1`):

```
:moneybag: *Layaway Yield % (MTD)* — updated <DATE>

Layaway Yield % = (Down Payments + Payments) MTD ÷ Layaway Balance.

| Store | Down Pmts | Payments | Collected | Layaway Bal | Yield % |
|---|---|---|---|---|---|
| Culpeper | ... |
| Harrisonburg | ... |
| Lexington | ... |
| Roanoke | ... |
| Waynesboro | ... |
| *Company* | ... |

See the Canvas above for the running view. [Note any missing stores here.]
```
Then separately DM Joshua (U03BB52MDSA) a one-line confirmation: `✅ Layaway Yield Weekly <DATE>: Company X.X% MTD, posted to #layaway-review.` Per the global failure policy, skip the channel post entirely and DM-only on any failure — never post a partial/failed result to the channel.

============================================================
Reference
============================================================
- Compile script (REV 2, EOM-only, no Bravo pull of its own): `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/layaway_yield_compile.py`
- Data source: the `end-of-month` pipeline cell's output, already pulled weekly by `weekly-store-kpis` — this task never pulls its own Bravo data.
- The old `layaway-deposits` pull (reports/LayawayDeposits.ahk, patched 2026-07-15 for Continuous Scrolling) is no longer used by this task but remains patched/available for other purposes if ever needed.
- This task is entirely separate from `weekly-loan-layaway-review` / `monday-bravo-combined-run` / `weekly-store-kpis` — it reads their output but modifies none of them.
- Full build/incident log: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/LAYAWAY_YIELD_STATUS.md`
- First live 5-store run (2026-07-15, on-demand at Joshua's request): Culpeper 8.48%, Harrisonburg 6.49%, Lexington 15.05%, Roanoke 17.96%, Waynesboro 6.55%, Company 10.13%. Re-verified byte-for-byte identical with the REV 2 EOM-only script the same day.