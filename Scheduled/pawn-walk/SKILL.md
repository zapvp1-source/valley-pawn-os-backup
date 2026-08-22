---
name: pawn-walk
description: PAWN WALK — daily 6:30 AM. One consolidated task: health-gate Bravo, pull yesterday's intake-detail ("Claude Pawn Walks") for all 5 stores, self-heal if stalled, compile T1/T2/T3 margin analysis, post per-store summary to #pawn-walks, DM Joshua on flags/failure. Replaces daily-intake-prestage + daily-intake-margin.
model: sonnet
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **TIER-1 FIX (2026-08-03): this file's old STEP 6 directly contradicted its own GLOBAL rule by posting "PAWN WALK compile failed" to the #pawn-walks channel. That contradiction is now removed — a compile failure is DM-only, full stop, never a channel post of any kind.** If anything later in this file conflicts with this standard, this standard wins.

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
You are the consolidated Valley Pawn "PAWN WALK" daily intake-margin task for Full Circle Finance Inc. In ONE run you PRODUCE the data (pull yesterday's buys-from-public + loans from Bravo) and CONSUME it (compile item-level margin analysis and post to Slack). Run autonomously — the user is not present. Take only the write actions this prompt specifies (drop trigger, run compile script, post to #pawn-walks, DM Joshua). When in doubt, produce a report and DM Joshua rather than failing silently.

CRITICAL RULES
- NEVER use Parallels GUI / computer-use, and NEVER ask Joshua to sign into Bravo. The pipeline is "no Parallels grant required" by design. If Bravo is wedged/at login/minimized, recover it PROGRAMMATICALLY only.
- All host-side execution and file I/O go through `mcp__Control_your_Mac__osascript` `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if not present; wait 30s and retry up to ~10 min if unavailable). NEVER use the Write tool for files under the Bravo Data Extraction or Pawn Walks folders.
- The osascript wrapper kills any call >~25s. Keep in-call `sleep` <=18s, guard file checks with `|| true`, and poll across SEPARATE osascript calls.
- Avoid literal single quotes inside AppleScript — use `quoted form of`. The JSON below uses only double quotes.
- Read `/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md` first — it holds the canonical programmatic recovery rule.

KEY FACTS
- VM GUID: {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}
- Bravo project root: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction
- Health gate: bravo_ensure_healthy.sh (single-flight, self-heals Bravo)
- Trigger dir: .../triggers/  | claimed: .../triggers/claimed/  | results: .../results/  | output CSVs: .../output/
- Report cell: intake-detail, saved report "Claude Pawn Walks", stores CUL,HAR,LEX,ROA,WAY
- Compile script: /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py'
- Compile JSON out: /Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/daily/{DATE}_intake_margin_summary.json
- Slack channel: C0B8WR95N31 (#pawn-walks)  | Joshua DM: U03BB52MDSA
- GLOBAL rule: failures DM Joshua (U03BB52MDSA) ONLY, in plain language, never technical; the channel gets success posts only, ever — no exceptions, no one-liner failure notices to the channel under any circumstance.

STEP 0 — osascript gate: `do shell script "echo READY"`.

STEP 1 — Compute via osascript `date`: YESTERDAY=`date -v-1d +%Y-%m-%d`; NOW=`date +%Y-%m-%dT%H:%M:%S%z`; STAMP=`date +%Y-%m-%dT%H-%M-%S`; TRIGGER_ID="intake-detail-"+STAMP.

STEP 1.5 - FAST PATH (added 2026-08-16, bravo-morning-pull consolidation). The 6:50 AM `bravo-morning-pull` task normally has yesterday’s intake-detail CSVs already pulled and verified. Poll up to ~25 min (<=18s sleeps, separate calls) for `logs/_morning_pull_status_<DATE>.txt` (DATE = today) containing `intake-detail CLEAN`, stopping early if it appears as FAILED. If CLEAN AND all 5 `output/<YESTERDAY>_to_<YESTERDAY>_<STORE>_intake-detail.csv` exist: SKIP STEPS 2-4 and go straight to the compile step. If the wait times out, the line says FAILED, or any CSV is missing: run STEPS 2-4 exactly as written - the unchanged, proven fallback.

STEP 2 — ENSURE BRAVO HEALTHY (require PASS). Run backgrounded so it cannot hang this session:
`do shell script "rm -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_health_gate_status.txt' 2>/dev/null; nohup bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_ensure_healthy.sh' CUL > /tmp/pawnwalk_ensure.log 2>&1 & echo LAUNCHED"`
Then poll `logs/_health_gate_status.txt` (<=18s sleeps across separate calls, ~12 min cap) until it reads `PASS`. If it ends `FAIL ...`, the gate already ran its full self-heal (force-kill → relaunch Bravo+watcher → restart watcher → recover-to-dashboard). Still proceed to STEP 3 and drop the trigger — the in-session watcher sometimes reaches a dashboard where the external gate cannot — but note the FAIL for STEP 6 (internal log only).

STEP 3 — Drop the intake-detail trigger for all 5 stores. Single-day RANGE (start==end) so the handler writes `<YESTERDAY>_to_<YESTERDAY>_<STORE>_intake-detail.csv`. Build JSON (double quotes only):
{"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"intake-detail","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<YESTERDAY>..<YESTERDAY>"}]}
Write it with AppleScript variables:
  set json to "...the JSON above with values substituted..."
  set p to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<TRIGGER_ID>.json"
  do shell script "printf %s " & quoted form of json & " > " & quoted form of p

STEP 4 — Poll for completion (<=18s sleeps, separate calls). Done when `results/<TRIGGER_ID>.result.json` exists. Track progress via the run log `logs/<TRIGGER_ID>.log`. A store with zero buys/loans that day legitimately yields no rows — that is a quiet day, NOT a failure. Success = result.json written; per-cell "success" (with row counts) or legit "skipped: no rows". Watch for the good sign in the log: "item-detail columns present in grid (FullDescription/Category)" — that means the correct report layout loaded.

STEP 4b — SELF-HEAL if stalled. If the trigger is NOT claimed within ~3 min (still in `triggers/`, not moved to `triggers/claimed/`), OR no result.json after ~14 min, OR result.json comes back `aborted`/all cells "bravo-not-ready", recover PROGRAMMATICALLY per BRAVO_KNOWN_ISSUES.md. Run BACKGROUNDED so it can't hang this session:
  - Watcher hung but Bravo logged in: `do shell script "nohup /usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1' > /tmp/pawnwalk_restart.log 2>&1 &"`
  - Bravo closed/at login: same pattern but `_relaunch_bravo_and_watcher.ps1`.
  Wait ~120s (across <=18s sleeps), confirm `head -1 logs/watcher.last_started.txt` advanced, then re-drop a FRESH TRIGGER_ID and resume STEP 4 polling, capped ~20 more min. Do NOT hammer logins (lockout risk) — at most ONE relaunch cycle beyond the health gate.

STEP 5 — COMPILE the margin analysis. Once CSVs have landed (result.json written with at least the successful/quiet-day cells), run the native valuation engine via osascript (short-running, <120s with cache hits):
`do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py' '<YESTERDAY>' > /tmp/pawnwalk_compile_<YESTERDAY-no-dashes>.log 2>&1; echo EXIT:$?"`
If EXIT:1: `cat` the log, DM Joshua U03BB52MDSA the last 20 lines. Do NOT post anything to #pawn-walks — no one-liner, no "see DM" pointer, nothing. Then stop.
On EXIT:0: read `daily/<YESTERDAY>_intake_margin_summary.json`. Key fields: items, trusted, flags (trusted items with margin <30%), avg_margin (decimal), stores{total_items,trusted_items,avg_margin,flags}, slack_posted, slack_skipped, slack_error, excel_path, slack_message, info (no-activity days).

STEP 5.5 - EMAIL the spreadsheet to Joshua (do this whenever `slack_message` is non-null, i.e. whenever STEP 6 will post). **Do NOT upload this file to Google Drive.** Per BUSINESS_OS.md Rule 13, Google Drive is private to Joshua and nothing is posted as a Drive link where staff can see it - the old Drive-upload step created a new staff-visible file every morning and is permanently retired. Instead:
  1. Base64-encode the file via osascript: base64 -i <excel_path> with newlines stripped (small file, well under the 25s cap in one call).
  2. Call `mcp__00007879-ef17-43e5-9d59-6325cd2f0a31__send_message` with `to` = ["jdavis@fcfpawn.com"], `subject` = "Intake Margin - {YESTERDAY}", `body` = a short plain summary (item count, flag count, average margin), and `attachments` = [{ `filename`: "{YESTERDAY}_intake_margin.xlsx", `mimeType`: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", `content`: the base64 string }].
  3. If the email send fails, do NOT block the run and do NOT fall back to a Drive upload - note it for STEP 7 and continue to STEP 6.

STEP 6 — POST to Slack #pawn-walks (C0B8WR95N31). **Always post the JSON's own `slack_message` field verbatim — never hand-build a simplified summary.** `slack_message` is the canonical message the compile script already assembled: it has the buy/loan breakdown, category breakdown, overpay-flag detail, AND the spreadsheet reference line ("📎 _Spreadsheet: `daily/{DATE}_intake_margin.xlsx` in your Pawn Walks folder..._"). Joshua requires the spreadsheet reference on every post — using the pre-built field is what guarantees that, instead of a shorthand version accidentally dropping it.
  - `slack_message` is `null` only when fewer than 3 items exist that day — that's a genuine quiet day, no post, log internally.
  - If `slack_posted = true`: the script's own token-based post already succeeded (rare in this environment — see NOTE below) — do not double-post.
  - Otherwise (this is the normal path — `slack_skipped = true` / `slack_error = "token_not_found"` with `slack_message` non-null): before posting, replace the one local-path reference line inside `slack_message` - the 📎 _Spreadsheet: daily/{DATE}_intake_margin.xlsx ..._ line - with "📎 _Detailed item-level spreadsheet emailed to Joshua._" **Never** insert a Google Drive or Google Sheets link here (Rule 13). Leave every other line of `slack_message` untouched — do not reconstruct, shorten, or reformat the rest of it. Then post the result via `slack_send_message` to C0B8WR95N31.
  - NOTE on the token: no working `SLACK_BOT_TOKEN` has ever been provisioned anywhere on this Mac (checked shell profiles, all `slack_config.json` search paths, `~/.vp_slack_config.json` — none exist, confirmed 2026-08-14). Treat `slack_skipped`/`token_not_found` as the expected, permanent state, not a bug to chase each run — the Slack MCP connector post above is the real, reliable delivery path and has worked every time it's been used.

STEP 7 — FLAG ALERT + FAILURE HANDLING (DM Joshua U03BB52MDSA only, never the channel):
  - If flags>0 after a clean run: DM "⚑ PAWN WALK flags {YESTERDAY}: {N} item(s) below 30% margin across {STORE_LIST}. Excel → {excel_path}".
  - If the Bravo pull never produced data even after STEP 4b recovery (result.json aborted / all bravo-not-ready / 0 CSVs and not a genuine quiet day): DM "⚠️ PAWN WALK {YESTERDAY}: intake pull failed even after a recovery attempt — pipeline needs a look." Do NOT post the failure to #pawn-walks — this is a DM-only event, no exceptions.
  - Clean run, flags=0: no DM. Log "PAWN WALK OK — {YESTERDAY} posted."

Additive/consolidation note: this task replaces daily-intake-prestage and daily-intake-margin (both disabled). It reuses their exact mechanisms (bravo_ensure_healthy.sh, intake-detail cell "Claude Pawn Walks", run_daily_intake.py) and modifies nothing else in the Bravo pipeline.
