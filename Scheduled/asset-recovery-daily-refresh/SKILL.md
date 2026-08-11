---
name: asset-recovery-daily-refresh
description: Daily 7:15 PM refresh of the Asset Recovery 2025 vs 2026 artifact. Reuse-first: reads the latest complete 5-store Bravo End-of-Month CSV set already in the pipeline output (fresh pull only as fallback); updates the current-month Loans+Inventory point. Silent on failure.
model: claude-haiku-4-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack. Joshua reviews every run inside Claude. Only post to Slack once the task has genuinely completed its work.

Refresh the "Asset Recovery 2025 Vs 2026" artifact with the latest combined Loans Receivable + Inventory balance from the Bravo Data Extraction pipeline (NOT QBO — Bravo is the live source of truth).

CONTEXT
- Artifact id: asset-recovery-2025-vs-2026 (file: /Users/joshuadavis/Documents/Claude/Artifacts/asset-recovery-2025-vs-2026/index.html). Edit/Write/Read CANNOT reach that path from this task — to update, read the current HTML via osascript `cat`, write the full updated HTML to your scratch/outputs dir with the Write tool, then call mcp__cowork__update_artifact with id "asset-recovery-2025-vs-2026" and html_path=<your scratch file>.
- Tracked metric: combined month-to-date balance = Σ(Ending Loan Base) + Σ(Ending Inventory Base) across all 5 stores (CUL, HAR, LEX, ROA, WAY), in $K (cost basis, not retail).
- Canonical source = Bravo End of Month report → CSVs at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/ named YYYY-MM-DD_<STORE>_end-of-month.csv. The pipeline folder is OUTSIDE the sandbox — do ALL of its I/O (ls/cat/grep, dropping triggers) with mcp__Control_your_Mac__osascript, never Read/Write/Edit.

STEP 1 — REUSE FIRST (primary path; a fresh pull is fallback only).
- `ls` the output folder for *_end-of-month.csv. Find the most recent date that has a NON-EMPTY (>1KB) CSV for ALL 5 stores.
- If that complete set is dated within the last 8 days, USE IT — do NOT trigger a new pull. The Monday combined run and other tasks already refresh EOM; re-pulling at task time risks wedging Bravo.
- KNOWN ISSUE: EndOfMonth.ahk is NOT yet patched for the "Enable Continuous Scrolling" hang, so fresh EOM pulls frequently hang CUL ~180s and cascade "EnsureStore failed" on the other stores (worst at/after midnight when Bravo is cold). This is exactly why reuse-first matters — do not burn time re-pulling when a recent complete set exists.

STEP 2 — FALLBACK PULL (only if no complete set within 8 days).
- ENSURE BRAVO HEALTHY FIRST (single-flight self-heal, added 2026-06-19): Before dropping the trigger, run the shared health guard bravo_ensure_healthy.sh (in the Bravo Data Extraction folder) via osascript, BACKGROUNDED with nohup so it cannot hang this session. Then poll logs/_health_gate_status.txt in <=18s sleeps across separate calls (cap ~8 min) until it reads PASS, and only then drop the trigger. The guard makes Bravo healthy AND its lockfile guarantees only ONE recovery runs even if sibling morning tasks fire at the same time (prevents the Bravo-already-running collision). The existing reactive watcher-restart stays as a backstop.

Drop ONE trigger via osascript into .../Bravo Data Extraction/triggers/ :
  {"id":"asset-recovery-eom-YYYY-MM-DD","requested_at":"<ISO-now>","reports":[{"name":"end-of-month","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<YYYY-MM-01>..<today>"}]}
- Poll results/asset-recovery-eom-YYYY-MM-DD.result.json and the per-store CSVs every ~30s, max ~10 min. If it errors or any store CSV is missing/empty, STOP — skip the update and stay silent (guardrails). Never fabricate.

STEP 3 — PARSE. For each store CSV, grep the "Ending Loan Base" line and the "Ending Inventory Base" line; take the first $ amount on each; strip $, commas, parens. Sum loans across the 5 stores, sum inventory across the 5 stores. total = (Σloans + Σinv) / 1000, rounded to the nearest whole $K. Note the CSV date used (data-through date).

STEP 4 — UPDATE THE ARTIFACT (edit DATA ONLY; preserve all structure/styles/chart code). Current calendar month = from today's date.
- timelineData array: if an entry for the current month exists (e.g. {m:'Jun 26', v:...}) update its v; else APPEND {m:'<Mon YY>', v:<total>}.
- cycle2026 array: append/update the matching point {month:<N>, label:'<Mon YY>', value:<total $K, 3dp>} where N = months since the Apr-2026 low (Apr=0, May=1, Jun=2, ...).
- KPI tiles: "Today (<Month YYYY>)" → set month label + value ($X.XXXM) + "% from low" vs 2026 low $1,237K (Apr 2026). "Gap to recover ATH" vs Jan 2026 ATH $1,294K: if total ≥ ATH → label "New ATH set", val "+$<total−1294>K", delta "above Jan '26 peak"; else show remaining gap.
- Sub-headline: set "Snapshot: <Month Day, Year>" to today, with "(data through <CSV M/D>)".
- Source line must read "Source: Bravo Data Extraction pipeline (live)".
- Head-to-head "Months to recover ATH" 2026 cell: once total ≥ ATH, show recovery month (Apr-low + N) and "+$<X>K".

STEP 5 — On genuine success only, post one line: "Asset recovery artifact refreshed (Bravo EOM, data through M/D) — <Month> MTD: $X,XXXK (<gap to ATH $YK | NEW ATH +$YK>)". Per the failure policy, post NOTHING on failure/skip.

GUARDRAILS
- Bravo only, never QBO. Read-only on Bravo — trigger/parse, never push back.
- Pipeline failure or missing/empty CSVs → skip silently, leave the artifact unchanged. Never stale or fabricated numbers.
- NEVER change the Aug 2024 anomaly, the 2025 cycle data, or ANY closed month's value. Only the current (running) month's point may be added/updated.
- Additive only: do NOT edit shared pipeline infra (EndOfMonth.ahk, the watcher, saved Bravo reports). The EOM continuous-scrolling patch is a separate, flagged change requiring Joshua's go-ahead.

<!-- migrated to working model 2026-06-15 -->