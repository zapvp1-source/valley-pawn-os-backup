---
name: daily-items-to-price
description: Daily 8 AM ET — per-store count + total Cost of unpriced inventory (Bravo "Price Items" worklist) via the Bravo Data Extraction pipeline; posts to Slack #items-to-price. ALL-FIVE-OR-NOTHING: posts only when all 5 stores are present AND clean; a missing/incomplete store triggers a recovery loop, never a partial post.
model: claude-sonnet-5
---

Daily Items-to-Price report for Valley Pawn. Runs 8 AM ET. For each of the 5 stores it pulls the COUNT of inventory items awaiting pricing — Bravo's Dashboard "Price Items" worklist (items pulled from defaulted loans or bought from the public that are available to sell but not yet priced/on the floor; Status = UNPRICED) — and the TOTAL COST of those items. Pipeline cell `items-to-price` (NO computer-use, NO Parallels grant). It posts a per-store summary to Slack #items-to-price.

HOW THE DATA WORKS: the `items-to-price` pipeline handler dumps EVERY unpriced row for a store to `output/<DATE>_<STORE>_items-to-price.csv`. That CSV has a header row `Number,Status,Category,Type,Description,Location,Cost,Date` and one row per unpriced item (Cost looks like `$714.00`; some fields may be quoted because they contain commas). This task computes, per store: COUNT = number of data rows; DOLLAR = sum of the Cost column. Do NOT expect a pre-summarized count/dollar_sum CSV — parse the full dump.

FAILURE POLICY — ALL-FIVE-OR-NOTHING (hardened 2026-06-24 after a MISSING store was posted as "data unavailable"). NEVER post a partial, incomplete, or failed report to #items-to-price. The report posts ONLY when ALL 5 stores have a present CSV AND every one passes the integrity gate — i.e. zero MISSING stores and zero TRUNCATED stores. A single missing or incomplete store blocks the ENTIRE post; you do NOT post the other four with a "data unavailable" line, and you do NOT post a ⚠️ partial. If you do not yet have all 5 clean, you MUST run the STEP 4.5 recovery loop to GO GET the missing/incomplete data, then post the complete report. ONLY if recovery is fully exhausted and a store still cannot be captured: stay completely silent on Slack (post NOTHING) and append a line to `logs/_itp_incomplete_<DATE>.txt` recording which store(s) failed and why, for manual follow-up — the next day's run covers it. Do NOT DM anyone on failure. Posting clean-looking partial/incomplete data is the ONE outcome that is never acceptable — silence is always preferred over a partial.

All filesystem I/O against `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` is OUTSIDE this task's sandbox — it MUST go through `mcp__Control_your_Mac__osascript` `do shell script`. Never use the Write tool there. AVOID literal single quotes in AppleScript source (the osascript wrapper breaks on them) — use `quoted form of` for shell args. The osascript wrapper kills any single call running longer than ~25s, so keep every in-call sleep ≤18s and guard ls/cat/test with `|| true`.

STEP 0 — osascript gate. `do shell script "echo READY"`. If unavailable, load via ToolSearch `select:mcp__Control_your_Mac__osascript`, wait 30s, retry up to ~10 min. If still unavailable, stop silently.

STEP 1 — Compute date + trigger id via osascript `date` (never hardcode):
- DATE = `date +%Y-%m-%d`
- NOW  = `date +%Y-%m-%dT%H:%M:%S%z`
- TRIGGER_ID = "items-to-price-" + `date +%Y-%m-%dT%H-%M-%S`

ENSURE BRAVO HEALTHY FIRST (single-flight self-heal, added 2026-06-19): Before dropping the trigger, run the shared health guard bravo_ensure_healthy.sh (in the Bravo Data Extraction folder) via osascript, BACKGROUNDED with nohup so it cannot hang this session. Then poll logs/_health_gate_status.txt in <=18s sleeps across separate calls (cap ~8 min) until it reads PASS, and only then drop the trigger. The guard makes Bravo healthy AND its lockfile guarantees only ONE recovery runs even if sibling morning tasks fire at the same time (prevents the Bravo-already-running collision). The existing reactive watcher-restart stays as a backstop.

STEP 2 — Drop the pipeline trigger for all 5 stores (order CUL,HAR,LEX,ROA,WAY). JSON (escaped double-quotes in AppleScript):
{"id":"<TRIGGER_ID>","requested_at":"<NOW>","reports":[{"name":"items-to-price","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<DATE>"}]}
Write: `do shell script "printf '%s' " & quoted form of json & " > " & quoted form of ("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & TRIGGER_ID & ".json")`

STEP 3 — Poll for completion. The watcher store-cycles and walks each store's full grid (the walker auto-discovers a UIA ScrollPattern container and scrolls the virtualized grid; PageDown + "Show More" are fallbacks), ~2–3.5 min per store, ~12–18 min total. Done when `results/<TRIGGER_ID>.result.json` exists OR all 5 `output/<DATE>_<STORE>_items-to-price.csv` exist. Poll in ≤18s sleeps across SEPARATE calls; cap total at ~30 minutes. Guard with `|| true`.

STEP 4 — Compute per-store count + Cost-sum with a robust CSV parse. Run this via osascript (set PY to the script text, then `do shell script "/usr/bin/python3 -c " & quoted form of PY`). The script must be exactly:
import csv,os
base="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
DATE=os.environ.get("ITP_DATE","")
tot_c=0; tot_d=0.0
for s in ["CUL","HAR","LEX","ROA","WAY"]:
    f=os.path.join(base, DATE+"_"+s+"_items-to-price.csv")
    if not os.path.exists(f):
        print(s+"\tMISSING"); continue
    cnt=0; dsum=0.0
    with open(f,newline="",encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            cnt+=1
            v=(row.get("Cost") or "").replace("$","").replace(",","").strip()
            try: dsum+=float(v)
            except: pass
    tot_c+=cnt; tot_d+=dsum
    print(s+"\t"+str(cnt)+"\t"+("%0.2f"%dsum))
print("TOTAL\t"+str(tot_c)+"\t"+("%0.2f"%tot_d))
Pass the date by prefixing the shell command with `ITP_DATE=<DATE> ` so the script sees it (e.g. build the command as `"ITP_DATE=" & DATE & " /usr/bin/python3 -c " & quoted form of PY`). Parse the tab-separated output: each line is STORE<TAB>count<TAB>cost (or STORE<TAB>MISSING). Format cost as $X,XXX.XX. A MISSING store does NOT get a "data unavailable" line and does NOT get posted — it is an incomplete report that MUST go through the STEP 4.5 recovery loop. The report is only rendered/posted once all 5 stores are present and clean.

STEP 4.5 — COMPLETENESS + INTEGRITY GATE (completeness half hardened 2026-06-24; integrity half added 2026-06-20). Two failure modes block a post: a store with NO CSV (MISSING / completeness failure) and a store whose grid walk bailed before capturing every row (TRUNCATED / integrity failure). Both must be zero before STEP 5.
  Classify each store:
  • MISSING = no `output/<DATE>_<STORE>_items-to-price.csv`.
  • TRUNCATED = has a CSV but its run-log section contains the string `GAVE UP`, OR (csv_count < maxY − 1, where maxY = the largest Y across that section's `seen=X/Y` lines and maxY > 0). Isolate each store's section of `logs/<TRIGGER_ID>.log` (from its `Running items-to-price for <STORE>` / `ItemsToPrice for <STORE>` line up to the next store's, or EOF) and extract maxY via osascript by grepping the section for `seen=` and taking the max trailing number. Both checks are belt-and-suspenders; either trips TRUNCATED.
  • CLEAN = present and not truncated.

  GATE: if ALL 5 stores are CLEAN → go to STEP 5 and post.

  Otherwise (any MISSING or TRUNCATED) → RECOVERY LOOP. Do NOT post yet. Run up to 3 recovery rounds, each targeting ONLY the not-yet-clean stores:
    Round R (R = 1..3):
    1. Heal Bravo: run bravo_ensure_healthy.sh backgrounded via nohup and poll logs/_health_gate_status.txt until PASS (cap ~8 min). If this is round 2 or 3 (a store failed a prior round — typically a render-timeout where the grid `counter=''` never appears), ALSO force a Bravo watcher restart before re-triggering: run `_restart_watcher.ps1` via osascript (e.g. `do shell script "/usr/bin/pwsh -File ... _restart_watcher.ps1"` or the established powershell invocation) to clear any wedged Bravo UI state, then re-run the health guard to PASS.
    2. Build a NEW TRIGGER_ID and drop a trigger whose reports[0].stores lists ONLY the not-yet-clean stores (same DATE).
    3. Poll as in STEP 3 for just those CSVs/result (cap ~20 min).
    4. Recompute count+cost (STEP 4) for those stores from the fresh CSVs and re-classify (MISSING/TRUNCATED/CLEAN) on the NEW log.
    5. If all 5 are now CLEAN → go to STEP 5. Else continue to the next round with whatever stores remain not-clean.

  AFTER the recovery loop:
  • If ALL 5 stores are CLEAN → STEP 5, post the complete report.
  • If one or more stores are STILL not clean after 3 rounds → DO NOT POST ANYTHING to Slack. Append a line to `logs/_itp_incomplete_<DATE>.txt` via osascript: `<NOW> INCOMPLETE: <STORE>=<MISSING|TRUNCATED maxY=..> ...` for each failed store, plus the clean stores' counts for reference. Then stop. Silence + a local failure record is the correct, mandated outcome — NEVER a partial post.

STEP 5 — POST ONLY WHEN ALL 5 STORES ARE CLEAN. Post to Slack channel #items-to-price, channel_id `C0BA5U0GENL`, via `slack_send_message`. Fixed store order with city names. Every line is a real, clean count — there is no "data unavailable" line and no ⚠️ partial line in a posted message (those states are handled by STEP 4.5 and block the post entirely):

:label: *Items to Price — <Mon DD, YYYY>*
Unpriced inventory awaiting pricing & floor placement, by store:

• *Culpeper (CUL):* <count> items — <$cost>
• *Harrisonburg (HAR):* <count> items — <$cost>
• *Lexington (LEX):* <count> items — <$cost>
• *Roanoke (ROA):* <count> items — <$cost>
• *Waynesboro (WAY):* <count> items — <$cost>

*Total:* <total count> items — <$total cost>

(dollar = total Cost of each store's unpriced items.)

This task is complete EITHER after `slack_send_message` returns success for an all-5-clean report, OR after a fully-exhausted recovery loop has logged the incomplete state to logs/_itp_incomplete_<DATE>.txt and posted NOTHING. Until one of those terminal states is reached, end every turn with a tool call advancing toward it; treat "Tool loaded." / "Continue" as resume signals, not stop signals. Execute autonomously; do not ask for confirmation.

<!-- migrated to working model 2026-06-15 -->
<!-- integrity gate (STEP 4.5) added 2026-06-20 after the 43-row truncation correction -->
<!-- ALL-FIVE-OR-NOTHING completeness gate + recovery loop added 2026-06-24 after a MISSING ROA was posted as "data unavailable" -->
