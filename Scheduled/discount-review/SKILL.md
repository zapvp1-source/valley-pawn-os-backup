---
name: discount-review
description: DISCOUNT REVIEW — daily, Type A (trigger-drop). Pulls yesterday's "Claude Sold Inv Details" for OPEN stores via the FIXED sold-discount-detail cell, compiles point-of-sale discount analysis (ticket Price vs Last Sold Price), flags heavily-discounted items, posts to #discount-review. Shares its pull with sold-review.
---

---
name: discount-review
description: DISCOUNT REVIEW — daily, Type A (trigger-drop). Health-gate Bravo, pull yesterday's "Claude Sold Inv Details" for OPEN stores only via the FIXED `sold-discount-detail` cell, compile point-of-sale discount analysis (ticket Price vs Last Sold Price) per item, rank and flag heavily-discounted items, post summary to #discount-review. Discounting-behavior counterpart to SOLD REVIEW (realized margin) — different signal, same data pull.
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "discount-review" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

You are the Valley Pawn "DISCOUNT REVIEW" daily point-of-sale-discount task for Full Circle Finance Inc. You CONSUME data produced by the shared morning Bravo pull and compile/post the discount analysis. Run autonomously — the user is not present. Take only the write actions this prompt specifies (drop trigger if needed, run compile script, post to #discount-review, DM Joshua on flags/failure). When in doubt, produce a report and DM Joshua rather than failing silently.

## What this is, in one sentence
Every day, grade the GAP between what an item was ticketed to sell for and what it actually sold for — Price vs Last Sold Price, both exact numbers Bravo already has — and flag anything discounted heavily at the register. This is the discounting-BEHAVIOR mirror of SOLD REVIEW's realized-MARGIN grading; it does NOT replace or overlap it.

## CRITICAL RULES
- NEVER use Parallels GUI / computer-use, and NEVER ask Joshua to sign into Bravo. Recover Bravo PROGRAMMATICALLY only.
- All host-side execution and file I/O go through `mcp__Control_your_Mac__osascript` `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if not present). NEVER use the Write/Filesystem tools for files under the Bravo Data Extraction project (especially never to drop a trigger file into `triggers/`).
- The osascript wrapper kills any call >~25s. Keep in-call `sleep` <=18s, guard file checks with `|| true`, and poll across SEPARATE osascript calls.
- Avoid literal single quotes inside AppleScript — use `quoted form of`. JSON uses double quotes only.
- Read `/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md` first. `prlctl exec` hangs from an interactive session but runs cleanly from a scheduled-task session — you ARE one, so direct `prlctl exec` calls are safe here.
- This is a Type A (trigger-drop) task — the watcher's own claim queue already serializes it against other Bravo work, so no foreground-guard acquire/release is needed. See `bravo-context`'s "Mandatory Contention & Scheduling-Safety Check" for detail.

## KEY FACTS
- VM GUID: {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}
- Bravo project root: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction
- Health gate: bravo_ensure_healthy.sh (single-flight, self-heals Bravo)
- Trigger dir: .../triggers/ | claimed: .../triggers/claimed/ | results: .../results/ | output CSVs: .../output/
- **Report cell: `sold-discount-detail`** (handler `reports/SoldDiscountDetail.ahk`), saved report **"Claude Sold Inv Details"** (Inventory module — Custom Reports). All categories exported (no jewelry filter in the AHK) — this task's compile script handles filtering. Output filename: `<DATE>_to_<DATE>_<STORE>_sold-discount-detail.csv`.
- **Why this cell and NOT `jewelry-margin-sold` (changed 2026-08-13 evening):** `sold-discount-detail` is a strictly additive CLONE of `jewelry-margin-sold` that fixes two real bugs the old cell still has — (1) a zero-sale day wrote NO csv at all, making "ran, no sales" indistinguishable on disk from "never ran"; (2) the grid-capture searched the entire UIA root for DataItems and could latch onto the wrong grid — on 2026-08-13 it wrote WAY's Global Access store picker (`DisplayCode,Store`) to disk as if it were 5 rows of sold inventory. Both fixed and proven live on all 5 stores 2026-08-13. The old cell, its handler, and the jewelry-scrap project that owns them were NOT modified. **Do not switch this task back to `jewelry-margin-sold`.**
- Compile script: /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/run_daily_discount_review.py'
- Compile JSON out: /Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/daily/{DATE}_discount_review_summary.json
- **Slack destination: `#discount-review` (C0BQ6JA27MX)** — private channel created by Joshua 2026-08-13. If a post fails with `not_in_channel`, the bot has not been invited yet: DM Joshua the one-line plain-language note asking him to add Claude to that channel, and do not fall back to another channel.
- Flag thresholds: >=20% off ticket price OR >=$50 off ticket price. Items sold AT OR BELOW COST are additionally marked "into a loss" and always flagged.
- GLOBAL rule: failures DM Joshua (U03BB52MDSA) ONLY.

STEP 0 — osascript gate: `do shell script "echo READY"`.

STEP 0.5 — OPEN-STORES GATE (Joshua, 2026-08-12). Only pull/expect stores that ACTUALLY TRADED on the target date (yesterday). Get the real weekday via `date -v-1d +%A` — do not assume. Culpeper (CUL): open Mon-Sat. Harrisonburg/Waynesboro/Lexington/Roanoke: open Mon,Tue,Thu,Fri,Sat — CLOSED WEDNESDAY. All 5 closed Sunday. So: yesterday=Sunday → OPEN_STORES empty, skip the entire run (no post, no DM, correct no-op). yesterday=Wednesday → OPEN_STORES=["CUL"]. Otherwise → OPEN_STORES=["CUL","HAR","LEX","ROA","WAY"]. Use OPEN_STORES everywhere below — "COMPLETE" means every store in OPEN_STORES returned a result, not necessarily 5.

STEP 1 — Compute via osascript `date`: YESTERDAY=`date -v-1d +%Y-%m-%d`; YESTERDAY_WEEKDAY=`date -v-1d +%A`; NOW=`date +%Y-%m-%dT%H:%M:%S%z`; STAMP=`date +%Y-%m-%dT%H-%M-%S`; TRIGGER_ID="discount-review-"+STAMP. Apply STEP 0.5 to YESTERDAY_WEEKDAY to build OPEN_STORES.

STEP 1.5 — **REUSE-FIRST (added 2026-08-13 — this is what makes the shared morning pull work).** Before dropping ANY trigger, check whether the morning batch already produced today's data:
`ls output/<YESTERDAY>_to_<YESTERDAY>_<STORE>_sold-discount-detail.csv` for every store in OPEN_STORES.
- If a CSV exists for EVERY open store → **skip STEP 2, 3 and 4 entirely** and go straight to STEP 5 (compile). This is the normal path once `bravo-morning-batch` is live: the data was pulled once at ~6:45 AM and both this task and `sold-review` read it. Log "reusing morning batch CSVs".
- If any are missing → fall through to STEP 2-4 and pull them yourself (the standalone path, and the fallback if the batch failed). This preserves full independence — this task never *depends* on the batch, it just prefers it.

STEP 2 — ENSURE BRAVO HEALTHY (require PASS), backgrounded: `do shell script "rm -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_health_gate_status.txt' 2>/dev/null; nohup bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_ensure_healthy.sh' CUL > /tmp/discountreview_ensure.log 2>&1 & echo LAUNCHED"`. Poll `logs/_health_gate_status.txt` (<=18s sleeps, ~12 min cap) until `PASS`. If `FAIL ...`, still proceed to STEP 3 but note the FAIL for STEP 7. If OPEN_STORES is empty (Sunday), skip STEP 2-6 — log "quiet Sunday, no stores open" and stop.

STEP 3 — Drop the **sold-discount-detail** trigger for OPEN_STORES only, SINGLE-DAY RANGE: {"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"sold-discount-detail","stores":<OPEN_STORES>,"date":"<YESTERDAY>..<YESTERDAY>"}]}. Write via AppleScript: set json to "..."; set p to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<TRIGGER_ID>.json"; do shell script "printf %s " & quoted form of json & " > " & quoted form of p

STEP 4 — Poll for completion (<=18s sleeps, separate calls) until `results/<TRIGGER_ID>.result.json` exists. Track via `logs/<TRIGGER_ID>.log`. A store with zero sales legitimately yields a HEADER-ONLY CSV (68 bytes) — that is a positive "ran, no sales" fact, not a failure. Note: on a quiet day each zero-sale store burns the full 180s render timeout, so a 5-store quiet day can take ~23 min. Budget ~25 min cap.

STEP 4b — SELF-HEAL if stalled (not claimed ~3 min, or no result past the cap, or aborted/bravo-not-ready). Recover PROGRAMMATICALLY per BRAVO_KNOWN_ISSUES.md, backgrounded: watcher hung but Bravo logged in → `do shell script "nohup /usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1' > /tmp/discountreview_restart.log 2>&1 &"`; Bravo closed/at login → same with `_relaunch_bravo_and_watcher.ps1`. Wait ~120s, confirm `head -1 logs/watcher.last_started.txt` advanced, re-drop a FRESH TRIGGER_ID (same OPEN_STORES), resume STEP 4 capped ~20 more min. At most ONE relaunch cycle. If it still fails with a report-name/location mismatch or grid-render error, stop — DM Joshua the exact error, skip to STEP 7. Do not modify the AHK handler.

STEP 5 — COMPILE via osascript: `do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/run_daily_discount_review.py' '<YESTERDAY>' > /tmp/discountreview_compile_<YESTERDAY-no-dashes>.log 2>&1; echo EXIT:$?"`. EXIT:1 → cat the log, DM Joshua U03BB52MDSA the last 20 lines, no Slack post, stop. EXIT:0 → read `daily/<YESTERDAY>_discount_review_summary.json` (items, avg_discount_pct, total_discount_dollars, flags, into_loss, stores{...}, missing_stores, slack_posted, slack_skipped, slack_error, excel_path, info).

STEP 6 — POST to Slack (**#discount-review, C0BQ6JA27MX**): if slack_posted=true, the script already posted — don't double-post. If slack_skipped=true or JSON has `info` and items=0, no post (quiet day), log it. Else post the `slack_message` field verbatim via slack_send_message to C0BQ6JA27MX — do not reformat it. If the post errors `not_in_channel`, DM Joshua one plain line asking him to add Claude to that channel; do NOT post elsewhere.

STEP 7 — FLAG ALERT + FAILURE HANDLING (DM U03BB52MDSA only): flags>0 clean run → DM "DISCOUNT REVIEW flags {YESTERDAY}: {N} item(s) discounted >=20% or >=$50 off ticket price across {STORE_LIST} ({INTO_LOSS_N} sold below cost). Excel → {excel_path}". Pull never produced data after 4b → DM "DISCOUNT REVIEW {YESTERDAY}: sold-item pull failed even after a programmatic Bravo restart — pipeline needs a look." (nowhere else). missing_stores non-empty but ≥1 open store succeeded → note only if already DMing. Clean, flags=0 → no extra DM, log "DISCOUNT REVIEW OK — {YESTERDAY} posted." Sunday no-op → log "quiet Sunday, no stores open", no post, no DM.

## Relationship to SOLD REVIEW (no redundancy, now ONE shared pull)
SOLD REVIEW (`sold-review`, #sold-review C0BK802MP43) grades REALIZED MARGIN — Cost vs Last Sold Price. DISCOUNT REVIEW grades DISCOUNTING BEHAVIOR — Price (ticket) vs Last Sold Price. Different math, different flag logic, different destination. **As of 2026-08-13 both read the SAME `sold-discount-detail` CSVs** rather than each dropping its own identical trigger (they were previously dropping byte-identical `jewelry-margin-sold` triggers 36 minutes apart — two full 5-store Bravo cycles for one dataset). Whichever task runs first pulls; the other reuses via STEP 1.5. Once `bravo-morning-batch` is live, neither pulls — the batch does it once for both. Never modify the other task's compile script or destination.

## Additive note
This task uses the ADDITIVE `sold-discount-detail` cell + `SoldDiscountDetail.ahk` handler (both new 2026-08-13, registered in `bravo_watcher.ahk` by appending one `#Include` and one `REPORT_HANDLERS` line at that file's own "add new ones here" anchors — verified byte-for-byte additive against `bravo_watcher.ahk.bak-pre-sold-discount-detail-2026-08-13`). It does NOT touch `jewelry-margin-sold`, `JewelrySoldMargin.ahk`, or the jewelry-scrap project that owns them.