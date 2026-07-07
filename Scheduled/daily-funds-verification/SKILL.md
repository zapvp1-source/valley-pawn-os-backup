---
name: daily-funds-verification
description: Daily verification that funds Joshua sent to each store made it into the store Safe via Bravo Safe Register Journal — runs 6 PM ET daily. Connector-warmup-proof (waits for osascript/Slack before failing) with a LOCKED Slack + report format so output is identical every day. Zero computer-use; reads CSVs from the Bravo Data Extraction pipeline via osascript shell.
model: claude-sonnet-5
---


> ⚠️ **FAILURE POLICY — STRICT, SET BY JOSHUA 2026-06-08.**
> 1. **Never DM Joshua. Never DM anyone.** No alerts on failure, no "task could not complete" messages, no escalations.
> 2. **Never post to Slack on failure.** No "Funds verification could not run today," no partial results, no error notices, nothing. The #daily-funds-reconcilation channel only ever sees the SUCCESS markdown table.
> 3. **On failure, silently iterate to fix it.** Retry failed cells, restart the watcher if it hung, re-drop the trigger, AND wait out connectors that are still warming up — as many cycles as the time budget allows. Only stop iterating when the work succeeds OR the time budget is exhausted, in which case **exit silently with no notification of any kind.**
> 4. Save the markdown report file either way. The file is the durable record of what happened, including failure modes — Joshua reads the file when he wants to see it. The file is not a notification.

You are running Joshua Davis's daily funds verification for Valley Pawn / Full Circle Finance Inc. The goal: verify that the cash Joshua sent to each store today was actually entered into Bravo the same day.

**How this task works:** the verification reads CSVs produced by the Bravo Data Extraction pipeline that runs inside a Windows VM. This task drops trigger files (via the Mac shell since the pipeline folder is not in the agent sandbox), waits for the CSVs, then reconciles them against Slack. No Parallels grant required.

**Filesystem rule:** the Bravo Data Extraction folder is OUTSIDE this task's sandbox. ALL filesystem I/O against `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` MUST go through `mcp__Control_your_Mac__osascript do shell script`. Never use the Write tool against that folder. (The Daily Funds Verification report folder is fine to write via osascript too — see Step 5c.)

**Time budget:** ~35 minutes from task start (raised from 25 on 2026-06-08 to absorb a connector-warmup wait). If you can't get a clean 5-store result inside that budget after iterating, exit silently.

---

# Step 0 — Connector readiness gate (DO THIS FIRST — added 2026-06-08)

The single biggest failure mode observed in production was concluding a tool is "unavailable" when it had simply not finished connecting yet. At task start, MCP connectors may still be warming up. **A not-yet-connected connector is NOT a failure — wait for it.**

0a. **osascript gate.** Before any Bravo work, confirm `mcp__Control_your_Mac__osascript` is live with a trivial probe: `do shell script "echo READY"`.
- Returns `READY` → proceed.
- Errors with anything like *"No such tool available"*, *not connected*, or tool-not-found → the connector is still warming up. If `ToolSearch` is available, first load it via `select:mcp__Control_your_Mac__osascript`. Then **wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).** Only if it is STILL unavailable after the full 12-minute wait do you treat it as a genuine environmental failure and take the silent-exit path (no DM, no Slack post; save the report noting the connector never came up).

0b. **Slack gate.** Confirm `slack_read_channel` works (Step 1 proves this). If Slack tools aren't connected yet, apply the same wait-and-retry (30 s × up to 12 min) before giving up.

0c. **osascript wrapper timeout — operational rule.** The osascript MCP wrapper kills any single call that runs longer than ~25 s. **Never put a `sleep` longer than ~18 s inside one `do shell script` call.** When polling, poll in short increments (`sleep 18` then check) across multiple calls — never one long sleep. Guard every `grep`/`ls`/`[ -f ]` that may exit nonzero with `|| true` or `|| echo`, because `do shell script` throws on any nonzero exit.

Treat Step 0 as part of the iterate-to-fix mandate: warming-up connectors are exactly the thing to wait out, not surrender to.

---

# Step 1 — Slack scan

For each of the 5 store funds channels, pull TODAY's messages (oldest = today midnight ET, latest = tomorrow midnight ET). Capture each store's request and Joshua's "Sent X" reply. Track cancellations ("don't need it", "got it covered").

| Channel | Channel ID | Store code | Store name |
|---|---|---|---|
| #pepper-funds | C03BLHFJ3KN | CUL | Culpeper |
| #lex-funds | C03B3K5DL6T | LEX | Lexington |
| #boro-funds | C03BLLRN64U | WAY | Waynesboro |
| #roanoke-funds | C063K8E02TW | ROA | Roanoke |
| #harrisonburg-funds | C03BWRKEDUZ | HAR | Harrisonburg |

Use `slack_read_channel` with `oldest=<today_midnight_unix>`, `latest=<tomorrow_midnight_unix>`, `response_format=concise`. Send all 5 reads in one message for parallelism. Compute the unix bounds with osascript `date` so they are always correct for the run date — never hardcode timestamps. Build a per-store ledger: `amounts_sent`, `cancellations`, `net_expected`. If a single request is re-confirmed/troubleshot in-thread (e.g. "not showing available" → "its in there"), it is ONE transfer, not two — count it once.

---

ENSURE BRAVO HEALTHY FIRST (single-flight self-heal, added 2026-06-19): Before dropping the trigger, run the shared health guard bravo_ensure_healthy.sh (in the Bravo Data Extraction folder) via osascript, BACKGROUNDED with nohup so it cannot hang this session. Then poll logs/_health_gate_status.txt in <=18s sleeps across separate calls (cap ~8 min) until it reads PASS, and only then drop the trigger. The guard makes Bravo healthy AND its lockfile guarantees only ONE recovery runs even if sibling morning tasks fire at the same time (prevents the Bravo-already-running collision). The existing reactive watcher-restart stays as a backstop.

# Step 2 — Drop the Bravo trigger via osascript

The Bravo Data Extraction folder is at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`. Trigger files go in `triggers/` (top level); the watcher moves them to `triggers/claimed/` then `triggers/processed/`. Result JSON lands in `results/<triggerId>.result.json`. Each cell's CSV lands at `output/<YYYY-MM-DD>_<STORE>_safe-register-journal.csv`.

2a. Generate a trigger ID: `daily-funds-verification-YYYY-MM-DDTHH-MM-SS` (derive from osascript `date`).

2b. Write the trigger JSON via osascript into `triggers/`. EXACT body shape (stores in this order: CUL,HAR,LEX,ROA,WAY):
```json
{
  "id": "daily-funds-verification-YYYY-MM-DDTHH-MM-SS",
  "requested_at": "YYYY-MM-DDTHH:MM:SS-04:00",
  "reports": [
    {"name": "safe-register-journal", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD"}
  ]
}
```
This schema is correct and verified. Do NOT alter key names — a malformed trigger gets silently renamed `untitled_*` and never runs.

2c. Poll for the result JSON every ~18 s (short sleeps per 0c) — `[ -f "results/<triggerId>.result.json" ] && echo READY`. Each of the 5 cells takes ~63–85 s and runs serially, so expect ~5–7 min. Timeout 10 minutes. While polling you can also `ls -t output/ | grep "<DATE>_.*safe-register"` to watch cells appear.

2d. If 10-min timeout fires with no result JSON: the watcher may be hung → go to Step 2e (watcher restart) and re-drop the trigger.

2e. **Silent watcher restart** (only when needed — watcher hung, all-cells-error, or trigger unclaimed >2 min): create a one-shot Cowork scheduled task to restart the watcher (canonical pattern from `monday-bravo-combined-run` Check 2 — `prlctl exec` from a scheduled-task session runs `_restart_watcher.ps1` cleanly; from interactive osascript it hangs on terminal-grab). Use `mcp__scheduled-tasks__create_scheduled_task` with `fireAt` ≈ 60 s from now, taskId like `srj-watcher-restart-oneshot-<timestamp>`, and a prompt that:
1. Reads `logs/watcher.last_started.txt` to capture the current timestamp.
2. Runs `osascript do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1'"`.
3. Sleeps 15 s, re-reads `watcher.last_started.txt`, confirms the timestamp advanced (retry once if not).
4. Exits silently — no Slack post, no DM, regardless of outcome.

After scheduling the restart, wait 90 s, then drop a fresh trigger and resume polling. Do not DM. Do not post the failure to Slack.

---

# Step 3 — Parse CSVs

For each `status="success"` cell, `cat` the CSV via osascript. Columns: `Txn Num, Date & Time, Txn Type, Till Number, Associate, Comments, Tender Type, Amt Coll`.

Signature for funds Joshua sent INTO the safe (the only rows that count):
- `Txn Type` = `TENDER TRANSFER`
- `Till Number` = `BANK`
- `Tender Type` = `Cash`
- `Amt Coll` is the negative leg, e.g. `"($2,000.00)"`

Parse by stripping `$`, `(`, `)`, `,` → positive float. Sum per store. IGNORE non-Cash BANK transfers (card deposits at till/safe close) and all positive legs — they are not funds-ins.

If the CSV body is `No data returned for current report configuration`, treat the store's entered total as `$0`.

---

# Step 4 — Iterate-to-fix loop (silent)

If any cell came back `status="error"`, OR any CSV is unreadable/corrupted, OR all-cells-EnsureStore failed, OR a needed connector was still warming (Step 0):
1. Identify the failed stores (or the warming connector).
2. For failed cells: drop a focused retry trigger for ONLY those stores (same date, new trigger ID with `-retry-N` suffix). For a warming connector: keep probing per Step 0.
3. Poll the new result (10-min timeout).
4. If the retry's watcher cycle also times out → run the Step 2e silent watcher restart → drop the trigger again.
5. Repeat until either (a) all 5 stores have clean CSVs OR (b) the ~35-min total budget is exhausted.
6. **If budget is exhausted with stores still failing: exit silently — no DM, no Slack post, just save the markdown report capturing whatever you have.**

The retry/wait loop is the entire failure handling. There is no other notification path.

---

# Step 5 — Reconcile and post (SUCCESS PATH ONLY)

For each store, compute `net_actual` (sum of qualifying TENDER TRANSFER + BANK + Cash + negative-amount rows).

Per-store status:
- ✓ Matched — `|net_expected - net_actual| <= 1` (or both zero)
- ⚠ Discrepancy — differ by more than $1
- ❓ Could not verify — cell failed AFTER all retries (only if Step 4 exhausted budget)

5a. **Post to #daily-funds-reconcilation (C0B3R9B3S8H) ONLY if all 5 stores have a verified result** (Matched or Discrepancy — NOT Could not verify). Use the LOCKED FORMAT below — identical every day. Discrepancies ARE part of the success path and post normally.

5b. **If any store is still Could not verify after the loop: do NOT post to Slack.** Save the report (5c) and stop.

5c. **Always** save the markdown report via osascript at `/Users/joshuadavis/Documents/Claude/Projects/Daily Funds Verification/<YYYY-MM-DD> Funds Verification.md` using the LOCKED REPORT FORMAT below. The file is for Joshua to read; it is not a notification.

---

# OUTPUT FORMAT — LOCKED (must be byte-for-byte structure every day; only the values change)

Store rows ALWAYS appear in this fixed order: Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro. The Total row is ALWAYS included. Currency always `$#,###.00`. Headline = `ALL MATCHED` with ✅ if every store is ✓ Matched; otherwise `DISCREPANCY FOUND` with ⚠️. Status cell uses `✓ Matched` or `⚠ Discrepancy`.

### 5a — Slack message (exact template)
```
<EMOJI> *Daily Funds Verification — <YYYY-MM-DD>: <HEADLINE>*

<BOTTOM_LINE: e.g. "Every dollar sent today is in the Bravo safes." or "One store is off — see below.">  *$<EXPECTED_TOTAL> expected = $<ACTUAL_TOTAL> actual* across all 5 stores.

| Store | Expected | In Bravo | Status |
|---|---|---|---|
| Culpeper | $<CUL_exp> | $<CUL_act> | <CUL_status> |
| Harrisonburg | $<HAR_exp> | $<HAR_act> | <HAR_status> |
| Lexington | $<LEX_exp> | $<LEX_act> | <LEX_status> |
| Roanoke | $<ROA_exp> | $<ROA_act> | <ROA_status> |
| Waynesboro | $<WAY_exp> | $<WAY_act> | <WAY_status> |
| *Total* | *$<EXPECTED_TOTAL>* | *$<ACTUAL_TOTAL>* | *<N>/5 matched* |

<NOTES — optional single line, only when something is genuinely noteworthy (e.g. a split send, a re-confirmed transfer, or a discrepancy's likely cause). Omit entirely if nothing to flag.>
```
Post the Total inside the same message (not as a thread reply). Always include the Total row.

### 5c — Markdown report (exact section order)
```
# Daily Funds Verification — <YYYY-MM-DD>

**Status: <COMPLETE — all 5 verified / INCOMPLETE — see below>. <verdict>.**

## Bottom line
<one or two sentences: $<EXPECTED_TOTAL> expected vs $<ACTUAL_TOTAL> actual; matched/exceptions>

## Step 1 — Slack ledger (today, <YYYY-MM-DD> ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | ... | ... | $... |
| HAR — Harrisonburg | #harrisonburg-funds | ... | ... | $... |
| LEX — Lexington | #lex-funds | ... | ... | $... |
| ROA — Roanoke | #roanoke-funds | ... | ... | $... |
| WAY — Waynesboro | #boro-funds | ... | ... | $... |

Cancellations: <none / list>. **Total expected: $<EXPECTED_TOTAL>.**

## Step 2 — Bravo extraction
Trigger `<triggerId>` → watcher status `<success/...>` on <N>/5 cells.

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| ... one row per qualifying transfer; "(no cash transfer)" / "$0.00" for stores with none ... |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $... | $... | ✓ Matched |
| HAR — Harrisonburg | $... | $... | ✓ Matched |
| LEX — Lexington | $... | $... | ✓ Matched |
| ROA — Roanoke | $... | $... | ✓ Matched |
| WAY — Waynesboro | $... | $... | ✓ Matched |
| **Total** | **$<EXPECTED_TOTAL>** | **$<ACTUAL_TOTAL>** | **<verdict>** |

**Slack post: <made / skipped (reason)>.**

_Report generated <YYYY-MM-DD> ~<HH:MM> ET._
```

---

# Hard rules (recap)

- **No DMs. To anyone. Ever.** Not on failure, partial success, discrepancy, watcher hang, or warming connector.
- **No Slack posts on failure.** Only post when all 5 stores have a verified outcome (Matched or Discrepancy), using the LOCKED FORMAT with the Total row.
- **Wait out warming connectors (Step 0) before ever concluding failure.** Then iterate: failed cells → retry; hung watcher → restart silently → retry. Budget runs out → exit silently.
- **Markdown report always saved**, in the LOCKED REPORT FORMAT.

---

# Background

Rewritten 2026-05-12 to use the Bravo Data Extraction pipeline. 2026-06-08 policy rewrite removed all DM/post-on-failure paths and added the silent iterate-to-fix loop with watcher-restart via one-shot scheduled task (Joshua: "i dont want any DMS, i need it fixed, do not DM on fails or anyone else. Post nothing if it fails and then iterate to fix it.").

**2026-06-08 bulletproofing (this version):** added Step 0 connector-readiness gate (the run had failed once by concluding the osascript connector was "unavailable" when it was merely still connecting — wait-and-retry 30 s × 12 min fixes that); raised the budget to 35 min; documented the ~25 s osascript-wrapper timeout (keep in-call sleeps ≤18 s, guard nonzero exits); and LOCKED the Slack + report output format (fixed store order CUL/HAR/LEX/ROA/WAY, mandatory Total row, fixed headline/status wording) so every day's output is structurally identical.

The watcher-restart pattern uses a sub-scheduled-task because `prlctl exec` hangs from interactive osascript sessions but works cleanly from a scheduled-task session — same path `monday-bravo-combined-run` uses. The SafeRegisterJournal handler was patched 2026-06-08 with the Continuous Scrolling toggle-off; per-cell success is now ~100% first attempt, ~63–85 s each. A separate `funds-verification-watchdog` task at 6:47 PM re-runs this flow if no post appeared by then — second safety net.

<!-- migrated to working model 2026-06-15 -->