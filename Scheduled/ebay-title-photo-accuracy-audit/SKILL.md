---
name: ebay-title-photo-accuracy-audit
description: Weekly: audit every eBay listing's title against its photos; auto-fix clear tool-only/battery-charger errors, flag the rest for Joshua
model: claude-sonnet-5
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


Weekly eBay TITLE-vs-PHOTO accuracy audit across all 5 Valley Pawn stores. Goal: find listings whose TITLE does not match what the PHOTOS actually show, correct ONLY the narrow high-confidence cases, and flag everything else for Joshua/Preston. Use the osascript tool (mcp__Control_your_Mac__osascript) for all local/Mac work.

AUTH: eBay Trading API. Store tokens from ~/ebay_weekly_rankings.py (STORES). App creds from ~/.vp_secrets/ebay_credentials.py (APP_ID, DEV_ID, CERT_ID) — never hardcode. Reuse patterns in ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py, ebay_title_revise.py, ebay_toolfix_apply.py.

STEP 1 — PULL: For each store run /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py <Store> ~/Documents/Claude/Projects/eBay/<Store>_photos.json. If eBay 503/usage-limit, stop gracefully and report it was throttled (retries next week).

STEP 2 — SCREEN (thumbnails): Build review sheets with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/build_audit_sheets.py <Store> (writes audit/<Store>_sheet_NN.png, 6 listings each). You MAY spawn one general-purpose subagent per store (Sonnet) to read that store's sheets and return candidate mismatches: {id, current title, issue, suggested title}. Treat these as CANDIDATES ONLY — thumbnails are unreliable for small text, model numbers, and colors.

STEP 3 — VERIFY EACH CANDIDATE ON FULL-RES (critical, this is the dial-in): For every candidate, download that listing's individual photos at full size and look closely before believing the flag. About 20% of thumbnail flags are wrong (a purple dress read as purple hair, a box back read as a second item, etc.). Only keep a flag if the full-res photo clearly confirms it.

STEP 4 — CLASSIFY the confirmed flags:
  (a) ACCESSORY-INCLUSION ADDS — title omits an accessory that is unmistakably pictured (controller, battery+charger, case/bag, cables). These are safe.
  (b) IDENTITY / SPEC / COLOR / QUANTITY errors — wrong brand, model number, magnification, karat, color, or lot count. NEVER auto-change these.
  (c) PHOTO-CONTENT problems — a wrong or mismatched photo on the listing (e.g., an iPhone photo on an iPad listing, a different item in one photo). NEVER a title fix.

STEP 5 — ACT (narrow):
  - AUTO-FIX only category (a) and the specific "Tool Only/Bare but battery AND charger clearly shown" pattern. Write {id:{store,old,new}} and apply with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_title_revise.py <fixes.json> --apply (reversible; keep titles <=80 chars). 
  - Do NOT change anything in category (b) or (c).

STEP 6 — REPORT: Post to Slack #preston-claude (channel_id C0BGXSTT4TY) AND DM Joshua (U03BB52MDSA): counts audited; the (a) items auto-corrected (list them); then category (b) identity/spec/color errors as "confirmed on full-res — needs OK to correct" with current title + issue + suggested title; and category (c) photo problems as "store needs to fix the image." Skimmable. If nothing found, one line.

HARD RULES: The only mutation allowed is the narrow Step-5 title add (reversible). Never end/relist/delist, never change photos/prices, never auto-change brand/model/color/quantity/identity. Everything uncertain is flag-only. End with <run-summary> of counts.