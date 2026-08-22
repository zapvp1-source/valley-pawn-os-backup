---
name: layaway-yield-weekly
description: Monday 11:15 AM — pull MTD Layaway Deposits per store, compute Layaway Yield % (Down Payments + Payments ÷ Layaway Balance), append to Details sheet + #layaway-review Canvas
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **Flagged in the 2026-08-03 comms audit: the channel post used to spell out the yield formula and include a bracketed "[Note any missing stores here.]" placeholder. Step 6 below drops both — the formula stays in this file and the Canvas subsection only; missing stores get a plain dash in the table, no bracket note.** If anything later in this file conflicts with this standard, this standard wins.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
You are the Valley Pawn "Layaway Yield Weekly" task. You compute a NEW metric — **Layaway Yield %** — and append it (never replace) to the existing weekly layaway review surfaces. This is additive-only: you never modify any existing Bravo saved report, AHK handler, pipeline cell, or other scheduled task.

> ⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If any step fails, DM Joshua (Slack user U03BB59EM9GR... wait, use U03BB52MDSA) with what failed. Never post errors/partials to a channel or Canvas. Channels and Canvases only ever show a successful, complete result.

DEFINITION (do not deviate — this exact label, to avoid confusion with the unrelated store "Yield" bonus metric):
**Layaway Yield % = (Down Payments MTD + Payments MTD) ÷ Layaway Balance**, per store and company-wide. Always label it "Layaway Yield %" in every surface — never bare "Yield". The formula spelled out this way belongs in this file and the Canvas subsection (Step 5) only — the channel post (Step 6) shows just the label and numbers, no formula text.

============================================================
DESIGN NOTE — internal reference only, never post any of this to Slack (REV 2, 2026-07-15)
============================================================
The first version of this task pulled a separate "Layaway Deposits" report live every Monday, which proved unreliable across repeated runs. Investigation found the existing weekly "End of Month" data pull (already produced every Monday by `weekly-store-kpis` with zero reliability issues) already contains a full "Layaways" section with Down Payments MTD, Payments MTD, AND Ending Balance in one place. Verified byte-for-byte identical to the live Layaway Deposits pull across all 5 stores on 2026-07-14.

As of REV 2, this task **does not touch Bravo at all**. It only reads the `end-of-month.xlsx` files that `weekly-store-kpis` already produced earlier the same morning. No trigger drop, no health gate, no export, no hang risk. If this ever needs to change back, that's a signal something about the underlying data source broke — check `weekly-store-kpis` health first, don't reintroduce a second live pull.

ALL HOST/FILE I/O under the Bravo Data Extraction folder MUST go through `mcp__Control_your_Mac__osascript` `do shell script` — never the Write tool (Parallels shared-folder path/perf rules). Load that tool via ToolSearch `select:mcp__Control_your_Mac__osascript` if it's deferred.

============================================================
STEP 1 — Dates
============================================================
```
YESTERDAY=`date -v-1d +%Y-%m-%d`
```
ENDDATE = YESTERDAY (MTD figures as of yesterday, computed by the existing report itself).

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

Its stdout starts with `OK enddate=...` (all 5 stores computed) or `PARTIAL enddate=... missing=<list>` (some stores skipped — proceed with what's there, note missing stores in the internal record only, see Step 6). If it prints `ERROR`, DM Joshua and stop — do not publish.

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
STEP 6 — Publish results — REWRITTEN 2026-08-03 per Field Communication Standard
============================================================
Post a summary message to the **#layaway-review channel** (id `C04N24STDP1`). No formula text, no bracket placeholders, no missing-store notes — just the label and the numbers, with a dash for any store not computed this run:

```
:moneybag: *Layaway Yield % (MTD)* — updated <DATE>

| Store | Down Pmts | Payments | Collected | Layaway Bal | Yield % |
|---|---|---|---|---|---|
| Culpeper | ... |
| Harrisonburg | ... |
| Lexington | ... |
| Roanoke | ... |
| Waynesboro | ... |
| *Company* | ... |

See the Canvas above for the running view.
```
Then separately DM Joshua (U03BB52MDSA) a one-line confirmation: `✅ Layaway Yield Weekly <DATE>: Company X.X% MTD, posted to #layaway-review.` — this DM is also where any missing-store note goes, never the channel post. Per the global failure policy, skip the channel post entirely and DM-only on any failure — never post a partial/failed result to the channel.

============================================================
Reference
============================================================
- Compile script (REV 2, EOM-only, no Bravo pull of its own): `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/layaway_yield_compile.py`
- Data source: the `end-of-month` pipeline cell's output, already pulled weekly by `weekly-store-kpis` — this task never pulls its own Bravo data.
- The old `layaway-deposits` pull (reports/LayawayDeposits.ahk, patched 2026-07-15 for Continuous Scrolling) is no longer used by this task but remains patched/available for other purposes if ever needed.
- This task is entirely separate from `weekly-loan-layaway-review` / `monday-bravo-combined-run` / `weekly-store-kpis` — it reads their output but modifies none of them.
- Full build/incident log: `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/LAYAWAY_YIELD_STATUS.md`
- First live 5-store run (2026-07-15, on-demand at Joshua's request): Culpeper 8.48%, Harrisonburg 6.49%, Lexington 15.05%, Roanoke 17.96%, Waynesboro 6.55%, Company 10.13%. Re-verified byte-for-byte identical with the REV 2 EOM-only script the same day.
============================================================
REV 2.1 HARDENING (2026-08-21) — DATA FALLBACK RULE (overrides Step 2's give-up path)
============================================================
If no complete <YESTERDAY> EOM set exists (e.g. the run fires on a non-Monday, or weekly-store-kpis missed), DO NOT fail and DO NOT wait pointlessly: find the FRESHEST date with a complete (or largest available) 5-store `*_end-of-month.xlsx` set, run the compile against THAT date, and publish with the as-of date clearly shown in the Canvas line and channel post header ("updated <as-of date>"). Ignore the undated `_<STORE>_end-of-month.xlsx` files — they are stale leftovers from Jul 30. Publishing accurate, clearly-dated numbers from the freshest data always beats skipping the week. The 2026-08-21 run proved this path: no 08-20 files existed, fell back to 08-16, all surfaces updated. Also: if prior weeks' yield JSONs are missing (task skipped), this run's publish inherently catches up — note the gap in Joshua's DM only.
