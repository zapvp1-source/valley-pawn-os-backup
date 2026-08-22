---
name: sold-review
model: claude-sonnet-5
description: SOLD REVIEW — daily, Type A (trigger-drop). Pulls yesterday's "Claude Sold Inv Details" for OPEN stores via the FIXED sold-discount-detail cell, compiles realized-margin analysis (Cost vs Last Sold Price), flags items sold too cheap, posts to #sold-review. Shares its pull with discount-review.
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (Joshua 2026-07-22, v2):** If this run fails or cannot complete its core work, send Joshua ONE plain-language Slack DM line (D03BHQH5VGT): ⚠️ Scheduled task "sold-review" did not complete — <date>. Nothing technical in the DM. Technical detail goes in the run log/STATUS file. Joshua's DM is the ONLY place a failure may ever be mentioned — never a team channel, store manager, or employee, including Preston, in any medium. Anything sent to the field must be plain everyday language: no jargon, no error codes, no system names, no file paths.

> 🛑 **COMPLETENESS RULE (Joshua 2026-08-14, binding, supersedes anything below that conflicts):** **NEVER post a partial report.** If even ONE store in OPEN_STORES has no usable data, do NOT post — go get it (STEP 4c); if you still can't, post NOTHING and DM Joshua. A late complete report is correct. An on-time report missing a store is a FAILURE that looks like success: store totals AND the company average are both wrong and no reader can tell. Do not "note the gap" and publish. `missing_stores` must be EMPTY before anything reaches Slack.

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
You are the Valley Pawn "SOLD REVIEW" daily task for Full Circle Finance Inc. Run autonomously. Take only the write actions specified. When in doubt, produce a COMPLETE report or none at all.

## What this is

Two different questions about yesterday's sales:
1. **Did we make money?** — realized margin, Cost vs Last Sold Price. Flags below 25%.
2. **Did we sell it too cheap?** — sale vs what the item is worth, benchmarked against our own realized history AND real eBay SOLD comps.

Q2 exists because Q1 is blind to the case that matters most: an item bought for $10, worth $200, sold for $60 posts an 83% margin and looks like a win. Per Joshua (2026-08-14), an internal-only benchmark is self-serving — if we systematically underprice, our own history certifies that underpricing as normal. Hence real eBay sold data.

## Bugs already found and fixed — do not reintroduce

- **2026-08-13:** source moved `sold-yesterday` → `jewelry-margin-sold` → **`sold-discount-detail`** (current). Old cells wrote no CSV on zero-sale days and could capture the wrong grid entirely. **Do not switch back.**
- **2026-08-14a:** a partial report (4/5 stores) was published with a caveat. Joshua: that's a failure, not degraded success. → COMPLETENESS RULE.
- **2026-08-14b:** STEP 6 swallowed a real report because the compile script's own Slack post has no `SLACK_BOT_TOKEN` on this host, so `slack_skipped=true` ALWAYS. That flag is NOT a skip signal. → STEP 6.
- **2026-08-14c:** a redundant re-pull DESTROYED data — the handler resets the output file at START of run. → STEP 1.5 is data-safety, not optimization.
- **2026-08-14d:** eBay's API cannot supply sold data — proven on our own creds (`buy.marketplace.insights` → `invalid_scope`; item_sales → 403; `findCompletedItems` dead since Feb 2025). Probe: `Pawn Walks/ebay_scope_probe.py`. **Don't retry the API.** Terapeak (STEP 6b) is the route.
- **2026-08-14e:** firearms must NEVER go to Terapeak — eBay bans gun sales, so "GLOCK 19" returns holsters and magazines; a $500 pistol would benchmark against $30 of accessories and every gun sale would flag. Handled in code (`FIREARM_RE`); don't work around it.
- **2026-08-15:** a finished, complete report NEVER POSTED because the Terapeak browser step ran BEFORE the post and got manually interrupted (Chrome moving on Joshua's screen). The post is the deliverable; browser enrichment is optional. → STEP 6b now runs LAST, after the post, and interrupting it is harmless.

## CRITICAL RULES

- NEVER use Parallels GUI/computer-use for Bravo; NEVER ask Joshua to log in anywhere. Recover Bravo PROGRAMMATICALLY. (Chrome with saved credentials for Terapeak is expected and fine.)
- Bravo file I/O + host execution via `mcp__Control_your_Mac__osascript` `do shell script` (ToolSearch `select:mcp__Control_your_Mac__osascript`). NEVER use Write/Filesystem tools under **Bravo Data Extraction**, especially `triggers/`. (**Sold Margin Review** is NOT Bravo — Write there is fine and STEP 6b needs it.)
- **NEVER drop a trigger for a store whose CSV already exists** — a pull resets the output file. Check STEP 1.5 before every trigger.
- osascript kills calls >~25s: `sleep` <=18s, guard checks with `|| true`, poll across separate calls.
- Avoid literal single quotes in AppleScript — use `quoted form of`. JSON uses double quotes.
- Read `/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md` first. `prlctl exec` works from a scheduled session — you ARE one.
- Type A: watcher queue serializes it, no foreground guard. Trigger IDs prefixed `sold-review-`.
- Never modify `SoldDiscountDetail.ahk`, `jewelry-margin-sold`, or `discount-review` — shared read-only.

## KEY FACTS

- VM GUID {7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a} · Bravo root `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction`
- Health gate `bravo_ensure_healthy.sh` · triggers/ · results/ · output/
- Cell **`sold-discount-detail`** → `<DATE>_to_<DATE>_<STORE>_sold-discount-detail.csv`
- **Known intermittent:** CUL can fail all 3 UIA select-strategies while other stores succeed. Confirmed intermittent (failed 07:50, succeeded 11:06 same day). A retry clears it → STEP 4c.
- Project: `/Users/joshuadavis/Documents/Claude/Projects/Sold Margin Review`
- Compile: `/usr/bin/python3 '<project>/run_daily_sold_review.py' <DATE>` → `daily/{DATE}_sold_review_summary.json`
- Slack **#sold-review C0BK802MP43**; DMs → U03BB52MDSA / D03BHQH5VGT
- Margin: target 50%, flag <25%, CRITICAL at/below cost, "(aged clearance)" note at 90+ days.

STEP 0 — `do shell script "echo READY"`.

STEP 0.5 — OPEN-STORES GATE. Get weekday via `date -v-1d +%A`, do not assume. CUL open Mon-Sat. HAR/WAY/LEX/ROA Mon,Tue,Thu,Fri,Sat — CLOSED WEDNESDAY. All closed Sunday. Sunday → OPEN_STORES empty, skip everything (no post, no DM — correct). Wednesday → ["CUL"]. Else all 5. COMPLETE means every open store, not necessarily 5.

STEP 1 — YESTERDAY=`date -v-1d +%Y-%m-%d`; NOW=`date +%Y-%m-%dT%H:%M:%S%z`; STAMP=`date +%Y-%m-%dT%H-%M-%S`; TRIGGER_ID="sold-review-"+STAMP.

STEP 1.5 — **REUSE-FIRST (mandatory).** `ls output/<YESTERDAY>_to_<YESTERDAY>_<STORE>_sold-discount-detail.csv` per open store. All present → skip STEP 2-4, go to STEP 4.8, log "reusing existing CSVs". Some missing → pull ONLY those. All missing → pull all.

STEP 2 — Health-gate, backgrounded: `do shell script "rm -f '<bravo>/logs/_health_gate_status.txt' 2>/dev/null; nohup bash '<bravo>/bravo_ensure_healthy.sh' CUL > /tmp/soldreview_ensure.log 2>&1 & echo LAUNCHED"`. Poll `logs/_health_gate_status.txt` (<=18s sleeps, ~12 min) until PASS. On FAIL proceed but note for STEP 7.

STEP 3 — Drop trigger for MISSING stores only: {"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"sold-discount-detail","stores":<MISSING>,"date":"<YESTERDAY>..<YESTERDAY>"}]} via `do shell script "printf %s " & quoted form of json & " > " & quoted form of p`.

STEP 4 — Poll until `results/<TRIGGER_ID>.result.json` exists. A zero-sale store yields a HEADER-ONLY CSV (~68 bytes) — that is "ran, no sales", counts as PRESENT, not missing. Quiet 5-store day ~23 min; budget ~25 min before self-healing.

STEP 4b — SELF-HEAL only if the WHOLE trigger stalled (unclaimed ~3 min / no result past cap / bravo-not-ready). Backgrounded `prlctl exec ... _restart_watcher.ps1` (or `_relaunch_bravo_and_watcher.ps1` if Bravo closed). Wait ~120s, confirm `head -1 logs/watcher.last_started.txt` advanced, re-drop FRESH TRIGGER_ID for still-missing stores, resume capped ~30 min. ONE relaunch cycle max.

STEP 4c — **PER-STORE RETRY (what makes COMPLETENESS achievable).** Read result `cells`, find stores with status `error` (single-store failure is NOT a stall). For each: re-check disk first (sibling task may have produced it — if so it's not missing, do NOT re-pull), then drop `sold-review-retry-<STAMP>` for still-missing stores. Up to TWO rounds. Still missing after both → continue to STEP 5 so Excel/JSON exist; STEP 6 will correctly refuse to post.

STEP 4.8 — **FAIR-VALUE COMPS via SoldComps API (BLEND_V2, added 2026-08-14 — no browser, cheap).** Skip if any open store's CSV is still missing (report won't post — save the quota). Otherwise — **BACKGROUND it; a direct do-shell-script call OUTRUNS the ~2-min AppleScript timeout on big days, and re-invoking after the 'error' double-burns quota (happened live 2026-08-14, caught at 56/60):**
1. `do shell script "cd '<project>' && rm -f /tmp/fv_lookup.log && nohup /usr/bin/python3 fair_value.py --lookup-all '<YESTERDAY>' > /tmp/fv_lookup.log 2>&1 & echo LAUNCHED"`
2. Poll every ~30s (≤8 min budget): `do shell script "pgrep -f 'fair_value.py --lookup-all' >/dev/null && echo RUNNING || echo DONE"`. **NEVER launch a second sweep** — if unsure whether one is running, that same pgrep is the check.
3. When DONE: `do shell script "cat /tmp/fv_lookup.log"` → JSON stats. If the log is empty/unparseable, treat as degraded (comps come from cache) and continue — do NOT retry the sweep.
This sweeps EVERY eligible sold item (no 8-item cap), highest sale value first: precious metals → melt (never comped), firearms → internal-only (never eBay), everything else → SoldComps sold-comps API, condition=used, model-key query then brand+category fallback. Quota guard lives inside the client (60/day hard ceiling, shared by all callers); `quota_stopped:true` in the stats → note it for STEP 7. If the API key is missing (`.soldcomps_key`), every lookup degrades to cache/Terapeak — normal until Joshua supplies the key, do not DM about it more than once ever.

STEP 5 — COMPILE: `do shell script "/usr/bin/python3 '<project>/run_daily_sold_review.py' '<YESTERDAY>' > /tmp/soldreview_compile.log 2>&1; echo EXIT:$?"`. EXIT:1 → cat log, DM last 20 lines, no post, stop. EXIT:0 → read the summary JSON.

STEP 6 — POST to #sold-review (C0BK802MP43). IN ORDER:
1. `slack_posted`=true → already posted, stop.
2. JSON has `info`, OR `slack_message` is null → nothing to report (Sunday / no files / under 3-item minimum). Log quiet day. No post, no DM. Stop.
3. **`missing_stores` NON-EMPTY → DO NOT POST.** COMPLETENESS RULE, absolute. DM Joshua ONE line: "Sold review for {YESTERDAY} is on hold — one of the stores didn't report its sales and I didn't want to send you half a picture. Detail is saved for the next look." Stop.
4. Otherwise → **POST `slack_message` verbatim** to C0BK802MP43, do not reformat. REGARDLESS of `slack_skipped`/`slack_error` — those only describe the compile script's own attempt, which has no bot token here (`token_not_found` is routine, NOT a reason to skip).

STEP 7 (runs right after STEP 6 — never wait on 6b for this) — DMs to U03BB52MDSA only (the summary already went to the channel; these are short extra lines, not duplicates).
- **Flags:** count BOTH `flags` (margin <25%) and items with `market_flag` true. If either >0 after a clean COMPLETE run → DM: "SOLD REVIEW {YESTERDAY}: {N} sold below 25% margin ({CRITICAL_N} at/below cost); {M} sold below market. Detail → #sold-review."
- **Market-feed health (added 2026-08-14 — this is the daily canary, do not skip it):** if `market_feed_ok` is `false`, DM ONE plain line: "Heads up — the market price check on the sold review stopped working, so today's report only compares against our own past sales. The rest of the report is fine." Then put `market_feed_note` in the run log for the next session. **Why this exists:** the eBay market data comes from a web page we don't control, so it will eventually break. The danger is that it breaks QUIETLY — the market column just goes blank and the report keeps publishing looking healthy for weeks. `market_feed_ok=false` means the daily canary caught it. The report is still VALID (margin grading is unaffected, benchmarks fall back to our own history); it is just no longer market-informed. Never suppress the report over this.
- **SoldComps quota (BLEND_V2):** if STEP 4.8 reported `quota_stopped:true` OR the summary JSON's `soldcomps_used_today` ≥ 60 → DM ONE plain line: "Heads up — the sold review hit its daily limit for market lookups today, so the cheapest items ran without a fresh market check. Highest-value items were done first, and it resets tomorrow." Once per day max.
- **Fair-value coverage:** if `fair_value_coverage` is 0 while `items` > 0 → DM ONE plain line: "The 'what should it have sold for' number is missing from today's sold review — margin grading and flags are unaffected. I'll look at it." Log detail for the next session.
- **Pull failed after 4b/4c** → send the STEP 6 gate-3 line only (one DM total).
- Clean run, no flags of either type, feed healthy → no DM, log "SOLD REVIEW OK — {YESTERDAY} posted."
- Sunday no-op → log it, no post, no DM.

STEP 6b — **MARKET COMPS via Terapeak (real eBay SOLD data). OPTIONAL, runs LAST — after STEP 6's post and STEP 7's DMs (moved 2026-08-15: an interrupted browser step killed a finished report's post that morning; never again). These comps land in the cache and improve TOMORROW's report. If this step gets interrupted (someone using the Mac), that is harmless — nothing depends on it.** Skip entirely if `missing_stores` was non-empty.
1. `do shell script "cd '<project>' && /usr/bin/python3 market_benchmark.py --candidates '<YESTERDAY>'"` → `<keyword>\t<url>` lines, max 8, prioritised by sale value, already excluding precious metals, firearms and anything cached fresh. Empty output → done. **(With STEP 4.8's API sweep, most keywords are already cached — 6b finding few or zero candidates is the system working, not a failure.)**
2. For EACH line (max 8 — one browser round-trip each):
   - `mcp__claude-in-chrome__navigate` to the URL. Chrome has saved eBay credentials (seller `valley_pawn_lexington`). **If it lands on a login page, STOP all of 6b and note it — never attempt to log in.**
   - Wait ~4s for the JS grid. Reading earlier returns an empty page.
   - `mcp__claude-in-chrome__get_page_text`
   - Save that text with the **Write** tool to `<project>/.terapeak_tmp.txt`, then `do shell script "cd '<project>' && /usr/bin/python3 terapeak.py --ingest '<KEYWORD>' .terapeak_tmp.txt"`. Prints `OK ... -> $X` or `MISS`. A MISS is normal and is cached so we don't retry tomorrow.
3. **NEVER read Terapeak's headline "Avg sold price" yourself, and never hand-enter a number.** It is contaminated by parts — proven: STIHL BG 50 headline $61.84 vs true filtered median $195.00, because 8 of 14 rows were gas caps, carburetors and primer bulbs. Let `terapeak.py` filter.
4. Close any tabs you opened.
5. Do NOT re-run the compile or re-post — the report already went out in STEP 6.

## Relationship to DISCOUNT REVIEW / PAWN WALK

`discount-review` (#discount-review C0BQ6JA27MX, ~40 min later) grades DISCOUNTING — ticket Price vs Last Sold Price. This task grades MARGIN + MARKET. **Both read the SAME CSVs** — whichever runs first pulls, the other reuses via STEP 1.5, so always re-check disk before re-pulling. `pawn-walk` grades INTAKE against an external estimate — unrelated source. Never modify either task's compile script or destination.

## Files this task owns (Sold Margin Review)

- `run_daily_sold_review.py` — compile, Slack message, embedded daily canary
- `market_benchmark.py` — internal comp index (~29k of our own sold rows), blend logic, `--candidates`
- `fair_value.py` — Fair Value v2 engine (precision blend, `--lookup-all`, `--validate`, `--health`)
- `soldcomps.py` — SoldComps API client, quota guard (60/day), `--test`
- `calibrate_fees.py` — measures real eBay fee rate from our own orders → `.channel_calibration.json`
- `terapeak.py` — eBay sold-comp parser, 30-day cache, `--ingest` / `--stats` / `--selfcheck`
- `test_fixtures/terapeak_stihl_bg50.txt` — regression fixture; `parse_page` on it must return ~$195
- `STATUS.md` — read before changing anything here
