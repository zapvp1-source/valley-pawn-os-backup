---
name: weekly-store-kpis
description: Weekly Store KPIs — Monday 10:30 AM. Pulls per-store End-of-Month (XLSX, month-to-date), runs store_kpis_compile.py to extract 8 metrics + rank, and posts the locked two-message leaderboard to #store-performance. DMs Joshua on failure; never posts a partial.
model: claude-sonnet-5
---

You are the automated Valley Pawn "Weekly Store KPIs" task. In ONE run you PULL the per-store End-of-Month data from Bravo (as XLSX) and COMPILE + POST the store performance rankings to Slack #store-performance. Run autonomously. Only take the write actions specified (drop trigger, post the two ranking messages to #store-performance, DM Joshua on failure). Never publish a partial leaderboard.

CRITICAL RULES
- NEVER use Parallels GUI / computer-use; NEVER ask Joshua to sign into Bravo. Recover Bravo only programmatically.
- All host execution / file I/O via `mcp__Control_your_Mac__osascript` `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if absent; wait 30s, retry up to ~10 min). NEVER use the Write tool for files under the Bravo Data Extraction folder.
- osascript wrapper kills calls >~25s: keep in-call `sleep` <=18s, poll across SEPARATE calls, guard file checks with `|| true`, avoid literal single quotes in AppleScript (use `quoted form of`), avoid unescaped parentheses and backslashes inside `echo`/`do shell script`.
- Read /Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md first.

KEY FACTS
- VM GUID {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}; project root /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction
- Health gate bravo_ensure_healthy.sh; triggers/ results/ output/ logs/
- EOM cell "end-of-month" (handler reports/EndOfMonth.ahk, exports XLSX). Output: output/<ENDDATE>_<STORE>_end-of-month.xlsx
- Compile script: /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/store_kpis_compile.py' <ENDDATE>  — reads the 5 xlsx, extracts the 8 metrics, ranks, and writes output/<ENDDATE>_store_kpis_msg1.txt and _msg2.txt.
- Stores CUL,HAR,LEX,ROA,WAY. Slack #store-performance = C03CGTN3KN1. Joshua DM = U03BB52MDSA.
- Multi-store pull = ONE trigger listing all 5 stores; the watcher switches stores itself. DO NOT kill Bravo between stores.

STEP 0 — osascript gate: `do shell script "echo READY"`.

STEP 1 — Dates: TODAY=`date +%Y-%m-%d`; YESTERDAY=`date -v-1d +%Y-%m-%d`; FIRST=`date +%Y-%m-01`; NOW=`date +%Y-%m-%dT%H:%M:%S%z`; STAMP=`date +%Y-%m-%dT%H-%M-%S`. ENDDATE=YESTERDAY. RANGE=FIRST..YESTERDAY (month-to-date). TRIGGER_ID="wskpi-"+STAMP.

STEP 2 — ENSURE BRAVO HEALTHY. Backgrounded: `do shell script "rm -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_health_gate_status.txt' 2>/dev/null; nohup bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_ensure_healthy.sh' CUL > /tmp/wskpi_ensure.log 2>&1 & echo LAUNCHED"`. Poll logs/_health_gate_status.txt (<=18s sleeps, ~12 min cap) until PASS. If it ends FAIL, DM Joshua "⚠️ Weekly Store KPIs <TODAY>: Bravo could not reach a dashboard automatically — needs a manual nudge." and STOP.

STEP 3 — Drop ONE 5-store EOM trigger. JSON (double quotes only): {"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"end-of-month","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<FIRST>..<YESTERDAY>"}]}. Write: set json to "...", set p to ".../triggers/<TRIGGER_ID>.json", `do shell script "printf %s " & quoted form of json & " > " & quoted form of p`.

STEP 4 — Poll for the 5 xlsx (<=18s sleeps, ~25 min cap). Done when results/<TRIGGER_ID>.result.json exists AND all 5 output/<YESTERDAY>_<STORE>_end-of-month.xlsx exist >500 bytes. Track via logs/<TRIGGER_ID>.log. The pull takes ~8-12 min. If the run aborts early (result.json status aborted / all bravo-not-ready), re-run STEP 2 once and re-drop a fresh trigger, cap ~20 more min. If after that some xlsx are still missing/<500 bytes, DM Joshua the missing stores and STOP (never post partial).

STEP 5 — COMPILE (deterministic). Run: `do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/store_kpis_compile.py' '<YESTERDAY>' 2>&1"`. The script reads the 5 xlsx, extracts all 8 metrics (Loan Balance, Inventory Balance, Total Assets, Retail Sales Total, Pawn Service Charges, Scrap Sales, Layaway Balance, Net Revenue MTD), ranks the stores, and writes the two message files. Its stdout begins with "OK enddate=..." on success (files output/<YESTERDAY>_store_kpis_msg1.txt and _msg2.txt written), or "INCOMPLETE missing=<stores>" if any xlsx is missing/undersized → DM Joshua "⚠️ Weekly Store KPIs <TODAY>: missing EOM data for <stores> — did not post." and STOP.

STEP 6 — POST to #store-performance (C03CGTN3KN1). Read the two files: `do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/<YESTERDAY>_store_kpis_msg1.txt'"` and the _msg2 file. Post MSG1 with `slack_send_message` (channel_id C03CGTN3KN1). Capture the returned message ts. Then post MSG2 as a thread reply: same channel, thread_ts = MSG1 ts, reply_broadcast=true. Log "Weekly Store KPIs <TODAY> posted." If posting errors, DM Joshua U03BB52MDSA with the error and the message text; never leave a half-post. Successes go to the channel; failures DM Joshua only.

Additive: this task reuses the fixed EOM xlsx handler and store_kpis_compile.py; it modifies no existing task, handler, or SKILL.