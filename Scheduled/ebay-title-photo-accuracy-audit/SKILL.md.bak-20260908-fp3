---
name: ebay-title-photo-accuracy-audit
description: Weekly: audit every eBay listing's title against its photos; auto-fix confirmed title-text errors (accessory adds + full-res-confirmed identity/spec/color errors), DM the store manager directly for photo-content problems, and DM Joshua a summary — no longer a "flag and wait forever" design
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


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


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
Weekly eBay TITLE-vs-PHOTO accuracy audit across all 5 Valley Pawn stores. Goal: find listings whose TITLE does not match what the PHOTOS actually show, correct the confirmed cases, get photo-content problems in front of the store manager who can actually fix them, and stop letting confirmed issues rot unresolved across multiple runs. Use the osascript tool (mcp__Control_your_Mac__osascript) for all local/Mac work.

AUTH: eBay Trading API. Store tokens from ~/ebay_weekly_rankings.py (STORES). App creds from ~/.vp_secrets/ebay_credentials.py (APP_ID, DEV_ID, CERT_ID) — never hardcode. Reuse patterns in ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py, ebay_title_revise.py, ebay_toolfix_apply.py, getitem_detail.py.

STEP 1 — PULL: For each store run /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_photos_pull.py <Store> ~/Documents/Claude/Projects/eBay/<Store>_photos.json. If eBay 503/usage-limit, stop gracefully and report it was throttled (retries next week).

STEP 2 — SCREEN (thumbnails): Build review sheets with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/build_audit_sheets.py <Store> (writes audit/<Store>_sheet_NN.png, 6 listings each). You MAY spawn one general-purpose subagent per store (Sonnet) to read that store's sheets and return candidate mismatches: {id, current title, issue, suggested title}. Treat these as CANDIDATES ONLY — thumbnails are unreliable for small text, model numbers, and colors.

STEP 3 — VERIFY EACH CANDIDATE ON FULL-RES (critical, this is the dial-in): For every candidate, download that listing's individual photos at full size and look closely before believing the flag. About 20% of thumbnail flags are wrong (a purple dress read as purple hair, a box back read as a second item, etc.). Only keep a flag if the full-res photo clearly confirms it. Before touching anything, also run getitem_detail.py on the item to confirm it's still active and see its current live title (titles can have changed since the photo pull).

STEP 4 — CLASSIFY the confirmed flags:
  (a) ACCESSORY-INCLUSION ADDS — title omits an accessory that is unmistakably pictured (controller, battery+charger, case/bag, cables). Safe, title-text only.
  (b) IDENTITY / SPEC / COLOR / QUANTITY-WORDING errors — wrong brand, model number, magnification, karat, color, or lot count, where STEP 3's full-res check plainly and unambiguously shows the true value (e.g. the box/label itself reads a different brand than the title). Title-text-only fix — never touches price, photo, or the Quantity field itself.
  (c) PHOTO-CONTENT problems — a wrong or mismatched photo on the listing (e.g., an iPhone photo on an iPad listing, a different item in one photo). Never a title fix — this needs a physical photo swap by the store.
  (d) GENUINELY AMBIGUOUS — full-res doesn't clearly settle it either way. Flag-only, explain the ambiguity. Don't force these into (b).

STEP 5 — ACT:
  - AUTO-FIX category (a) and the "Tool Only/Bare but battery AND charger clearly shown" pattern, as before.
  - AUTO-FIX category (b) too (changed 2026-08-21). Write {id:{store,old,new}} and apply with /usr/bin/python3 ~/Documents/Claude/Projects/eBay/ebay_title_revise.py <fixes.json> --apply (reversible via the same script's --revert; keep titles <=80 chars).
  - Category (c): never a title fix, never auto-touch photos/price/quantity. Instead, identify the store and DM that store's manager directly — search Slack via slack_search_users for the manager name (Sandi/Culpeper, Chadd/Waynesboro, Walker/Harrisonburg, Uriah/Lexington, Benjie/Roanoke — cross-check against ~/Documents/Claude/Projects/eBay/WEEKLY_QUALITY_FIX_LOG.md if a name doesn't match) with a plain-language note: item title, item number, which photo(s) are wrong and what they actually show, and ask them to swap in correct photos. This DM is what actually gets it fixed — don't just log it and move on.
  - Category (d): flag-only in the Joshua DM, with the specific reason it's ambiguous.
  - Why (b)/(c) changed: the old "flag and wait" design let the exact same confirmed items (e.g. Harrisonburg 800406852492 Kindle mislabeled as Fire tablet, Roanoke 298226614316 mirror mislabeled as Wheel Masters) sit unfixed and get re-flagged run after run (confirmed both 2026-08-02 and 2026-08-16, still wrong on 2026-08-21 when checked) with nobody ever closing the loop, and left (c) photo problems live for 3+ weeks with no manager ever told. Both changes are reversible/non-destructive so they don't need a human approval gate the way a price or listing-ending action would.

STEP 6 — REPORT: DM Joshua ONLY (U03BB52MDSA) — never post to #preston-claude (C0BGXSTT4TY) or any other Slack channel: counts audited; every (a)/(b) item auto-corrected this run (old title -> new title); every (d) ambiguous item and why; and for (c), which item + which store manager was DM'd. Skimmable. If nothing found, one line.

HARD RULES: Mutations allowed are Step-5 title changes (both reversible via ebay_title_revise.py --revert) plus the category-(c) store-manager DM. Never end/relist/delist, never change photos/price/quantity directly, never touch anything genuinely ambiguous on full-res (downgrade to (d), flag-only). Never post any output from this task to Slack channel #preston-claude or C0BGXSTT4TY — Joshua DM only (the one exception is the category-(c) store-manager DM, which must stay plain-language, no jargon, no file paths, no item-internals beyond the item number). End with <run-summary> of counts.