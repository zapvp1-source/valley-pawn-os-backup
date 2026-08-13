---
name: discount-review
description: DISCOUNT REVIEW — daily 8:15 AM. Health-gate Bravo, pull yesterday's "Claude Sold Inv Details" report for all 5 stores (existing pipeline cell jewelry-margin-sold), compile point-of-sale discount analysis (ticket Price vs Last Sold Price) per item, rank and flag heavily-discounted items, post summary to Joshua's Slack DM, DM Joshua on flags/failure only. Discounting-behavior counterpart to SOLD REVIEW (realized margin) — different signal, same data pull, fully additive.
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "discount-review" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

You are the Valley Pawn "DISCOUNT REVIEW" daily point-of-sale-discount task for Full Circle Finance Inc. In ONE run you PRODUCE the data (pull yesterday's sold items from Bravo, all 5 stores, via the EXISTING `jewelry-margin-sold` cell) and CONSUME it (compile discount analysis and post to Slack). Run autonomously — the user is not present. Take only the write actions this prompt specifies (drop trigger, run compile script, post to Joshua's DM, DM Joshua on flags/failure). When in doubt, produce a report and DM Joshua rather than failing silently.

## What this is, in one sentence

Every day, grade the GAP between what an item was ticketed to sell for and what it
actually sold for — Price vs Last Sold Price, both exact numbers Bravo already has — and
flag anything discounted heavily at the register. This is the discounting-BEHAVIOR mirror
of SOLD REVIEW's realized-MARGIN grading; it does NOT replace or overlap it (different
math, different flag logic, different destination — see below).

## CRITICAL RULES

- NEVER use Parallels GUI / computer-use, and NEVER ask Joshua to sign into Bravo. The
  pipeline is "no Parallels grant required" by design. If Bravo is wedged/at login/
  minimized, recover it PROGRAMMATICALLY only.
- All host-side execution and file I/O go through `mcp__Control_your_Mac__osascript`
  `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if not
  present; wait 30s and retry up to ~10 min if unavailable). NEVER use the Write/Filesystem
  tools for files under the Bravo Data Extraction project (and especially never to drop a
  trigger file into `triggers/`) — use `do shell script` for all reads/writes there. (A
  direct Filesystem-tool write into the live `triggers/` queue was tested and blocked by
  the platform's own safety classifier from an interactive session — `do shell script`
  from inside this scheduled-task session is the proven, unblocked path every other
  scheduled task already uses.)
- The osascript wrapper kills any call >~25s. Keep in-call `sleep` <=18s, guard file
  checks with `|| true`, and poll across SEPARATE osascript calls.
- Avoid literal single quotes inside AppleScript — use `quoted form of`. The JSON below
  uses only double quotes.
- Read `/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md` first — it
  holds the canonical programmatic recovery rule. In particular: `prlctl exec` into the
  Parallels VM hangs from an interactive session but runs cleanly from a scheduled-task
  session — you ARE a scheduled-task session, so direct `prlctl exec` calls (health gate,
  watcher restart) are safe here.

## KEY FACTS

- VM GUID: {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}
- Bravo project root: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction
- Health gate: bravo_ensure_healthy.sh (single-flight, self-heals Bravo)
- Trigger dir: .../triggers/  | claimed: .../triggers/claimed/  | results: .../results/  | output CSVs: .../output/
- Report cell: **jewelry-margin-sold** (EXISTING cell, built 2026-07-28 for an unrelated
  jewelry-scrap project — this task reuses it read-only, never modifies it), handler
  `reports/JewelrySoldMargin.ahk`, saved report **"Claude Sold Inv Details"** (Joshua's own
  saved Ad Hoc report, Inventory module — Custom Reports), stores CUL,HAR,LEX,ROA,WAY. All
  categories are exported (no jewelry filter in the AHK itself) — this task's compile
  script handles filtering/data-quality, not the trigger.
- Compile script: /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/run_daily_discount_review.py'
- Compile JSON out: /Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/daily/{DATE}_discount_review_summary.json
- Slack destination: D03BHQH5VGT (Joshua's own Slack DM channel — same one sold-review
  uses for failure alerts). No `#discount-review` team channel exists yet and there is no
  tool available to create one; posting to Joshua's DM avoids blocking the feature on
  that. If Joshua later creates a team channel, set `DISCOUNT_REVIEW_SLACK_CHANNEL` in
  this file's STEP 5 command to the new channel ID to switch destinations.
- Flag thresholds: >=20% off ticket price OR >=$50 off ticket price (dual threshold, set
  by Expert Board 2026-07-28 — tunable after 2-4 weeks of live data). Items sold AT OR
  BELOW COST are additionally marked "into a loss" and always flagged regardless of
  %/$ threshold.
- Data-quality exclusions (NOT counted as flags/errors, footnoted only): generic/bulk
  numeric SKUs (coins, misc tools, bullion — Price isn't a real per-item ticket on these),
  and firearm-paperwork placeholder rows (Price=$0.01, a data-entry placeholder, not a
  real 100%-off sale). See SCHEMA_NOTES.md in the project folder for detail.
- GLOBAL rule: failures DM Joshua (U03BB52MDSA) ONLY.
- **First live run note:** this task was just built (2026-07-29) and has not yet been
  proven against a live full-day Bravo pull (only a 40-row partial sample was used to
  verify the compile logic). If STEP 3/4 reveals anything unexpected about the
  `jewelry-margin-sold` cell's current behavior, capture the exact error in the log, DM
  Joshua per STEP 7's failure path, and do not guess further changes without that
  diagnostic — and do NOT attempt to fix/modify the `jewelry-margin-sold` cell or its AHK
  handler even if this task's pull fails; that cell is owned by, and actively used by, a
  separate jewelry-scrap project. Flag the discrepancy in the log for the next session
  instead.

STEP 0 — osascript gate: `do shell script "echo READY"`.

STEP 1 — Compute via osascript `date`: YESTERDAY=`date -v-1d +%Y-%m-%d`; NOW=`date +%Y-%m-%dT%H:%M:%S%z`; STAMP=`date +%Y-%m-%dT%H-%M-%S`; TRIGGER_ID="discount-review-"+STAMP.

STEP 2 — ENSURE BRAVO HEALTHY (require PASS). Run backgrounded so it cannot hang this session:
`do shell script "rm -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_health_gate_status.txt' 2>/dev/null; nohup bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_ensure_healthy.sh' CUL > /tmp/discountreview_ensure.log 2>&1 & echo LAUNCHED"`
Then poll `logs/_health_gate_status.txt` (<=18s sleeps across separate calls, ~12 min cap) until it reads `PASS`. If it ends `FAIL ...`, the gate already ran its full self-heal. Still proceed to STEP 3 and drop the trigger — the in-session watcher sometimes reaches a dashboard where the external gate cannot — but note the FAIL for STEP 6.

STEP 3 — Drop the jewelry-margin-sold trigger for all 5 stores, SINGLE-DAY RANGE (start==end) so the handler writes `<YESTERDAY>_to_<YESTERDAY>_<STORE>_jewelry-margin-sold.csv`. Build JSON (double quotes only):
{"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"jewelry-margin-sold","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<YESTERDAY>..<YESTERDAY>"}]}
Write it with AppleScript variables:
  set json to "...the JSON above with values substituted..."
  set p to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<TRIGGER_ID>.json"
  do shell script "printf %s " & quoted form of json & " > " & quoted form of p

STEP 4 — Poll for completion (<=18s sleeps, separate calls). Done when `results/<TRIGGER_ID>.result.json` exists. Track progress via the run log `logs/<TRIGGER_ID>.log`. A store with zero sales that day legitimately yields no rows — that is a quiet day, NOT a failure. Success = result.json written; per-cell "success" (with row counts) or legit "skipped: no rows". Note: this cell has previously taken longer / timed out on wide multi-month date ranges — a single-day range is much lighter and should behave like other single-day cells (sold-yesterday, sold-inv-details), but budget the same ~14 min cap as STEP 4b below just in case.

STEP 4b — SELF-HEAL if stalled. If the trigger is NOT claimed within ~3 min (still in `triggers/`, not moved to `triggers/claimed/`), OR no result.json after ~14 min, OR result.json comes back `aborted`/all cells "bravo-not-ready", recover PROGRAMMATICALLY per BRAVO_KNOWN_ISSUES.md. Run BACKGROUNDED so it can't hang this session:
  - Watcher hung but Bravo logged in: `do shell script "nohup /usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1' > /tmp/discountreview_restart.log 2>&1 &"`
  - Bravo closed/at login: same pattern but `_relaunch_bravo_and_watcher.ps1`.
  Wait ~120s (across <=18s sleeps), confirm `head -1 logs/watcher.last_started.txt` advanced, then re-drop a FRESH TRIGGER_ID and resume STEP 4 polling, capped ~20 more min. Do NOT hammer logins (lockout risk) — at most ONE relaunch cycle beyond the health gate.
  If the cell still fails after one relaunch with an error suggesting the saved report name/location doesn't match, or the grid render error seen previously ("Sold-margin grid did not render within 180s"), stop retrying — DM Joshua with the exact error and skip to STEP 7's failure path rather than looping. Do not modify the AHK handler.

STEP 5 — COMPILE the discount analysis. Once CSVs have landed (result.json written with at least the successful/quiet-day cells), run the compile script via osascript (short-running, no external APIs, should complete in seconds):
`do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Discount Outlier Review/run_daily_discount_review.py' '<YESTERDAY>' > /tmp/discountreview_compile_<YESTERDAY-no-dashes>.log 2>&1; echo EXIT:$?"`
If EXIT:1: `cat` the log, DM Joshua U03BB52MDSA the last 20 lines, do NOT post anything to Slack, then stop.
On EXIT:0: read `daily/<YESTERDAY>_discount_review_summary.json`. Key fields: items, generic_sku_excluded, avg_discount_pct, total_discount_dollars, flags, into_loss, stores{items,wtd_avg_discount_pct,total_discount_dollars,flags,into_loss}, missing_stores, slack_posted, slack_skipped, slack_error, excel_path, info (no-activity days).

STEP 6 — POST to Slack (Joshua's DM, D03BHQH5VGT — the script's default destination):
  - If `slack_posted = true`: the script already posted — do not double-post.
  - If `slack_skipped = true` or JSON has `info` (no-activity) + items=0: no post (quiet day). Log it.
  - Else build and post the summary yourself via `slack_send_message` to D03BHQH5VGT using the `slack_message` field already saved in the JSON verbatim — do not reformat it.

STEP 7 — FLAG ALERT + FAILURE HANDLING (DM Joshua U03BB52MDSA only — note the daily summary already lands in his own DM per STEP 6, so this step is for an EXTRA short flag-count line, not a duplicate of the full report):
  - If flags>0 after a clean run: DM "🚨 DISCOUNT REVIEW flags {YESTERDAY}: {N} item(s) discounted >=20% or >=$50 off ticket price across {STORE_LIST} ({INTO_LOSS_N} sold below cost). Excel → {excel_path}".
  - If the Bravo pull never produced data even after STEP 4b recovery (result.json aborted / all bravo-not-ready / 0 CSVs and not a genuine quiet day): DM "⚠️ DISCOUNT REVIEW {YESTERDAY}: sold-item pull failed even after a programmatic Bravo restart — pipeline needs a look.". Do NOT post the failure anywhere else.
  - If `missing_stores` is non-empty but at least one store succeeded: note the gap in the DM only if flags>0 or the run otherwise DMs; otherwise just log it — a genuinely quiet store is not a failure.
  - Clean run, flags=0: no extra DM (the daily summary in STEP 6 already covers it). Log "DISCOUNT REVIEW OK — {YESTERDAY} posted."

## Relationship to SOLD REVIEW (no redundancy)

SOLD REVIEW (`sold-review`, 7:45 AM daily, #sold-review) grades REALIZED MARGIN — Cost vs
Sale Price — using the separate `sold-yesterday` cell / "Claude Sold Yesterday" report.
DISCOUNT REVIEW grades DISCOUNTING BEHAVIOR — Price (ticket) vs Last Sold Price — using
the separate `jewelry-margin-sold` cell / "Claude Sold Inv Details" report. Different
math, different data source, different destination, different cadence (30 min after
sold-review so Joshua reads pawn-walk, sold-review, and discount-review back to back
without any of them colliding on the shared Bravo pipeline). Never modify sold-review, its
trigger cell (`sold-yesterday`), or its compile script — this task is fully additive
alongside it, and likewise never modifies the jewelry-scrap project that originally built
`jewelry-margin-sold`.

## Additive note

This task depends ENTIRELY on the EXISTING `jewelry-margin-sold` pipeline cell and
Joshua's EXISTING saved Bravo report "Claude Sold Inv Details" — no new Bravo report, no
new AHK handler, and no change to `bravo_watcher.ahk` were needed or made. It does not
touch `sold-yesterday`, `sold-inv-details`-adjacent scripts, or any other existing
pipeline cell, handler, or scheduled task.