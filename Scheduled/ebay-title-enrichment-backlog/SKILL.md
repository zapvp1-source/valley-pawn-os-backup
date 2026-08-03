---
name: ebay-title-enrichment-backlog
description: Daily: work through the backlog of cryptic model-only eBay titles across all 5 stores — look up each product, write a proper keyword title, and apply. Runs until the backlog is clear.
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


Continue the eBay TITLE-ENRICHMENT BACKLOG for all 5 Valley Pawn stores until it is clear. Goal: rewrite the remaining genuinely-weak short titles — CRYPTIC brand+model-only tool/electronics listings with no product-type description (e.g. "Ryobi Tools P519VN", "Hitachi Dh 40FB", "Hart Tool HPCS01VN", "Eaton AHCL360C") — into proper ~80-character keyword titles, and apply them. LEAVE already-good titles alone: jewelry with karat/weight/size (e.g. "Gold Earrings 14K Yellow Gold 1dwt"), vinyl records with year+artist+album, and clearly-named games that already have a platform.

TOOLS: Run scripts on the Mac using the Control-your-Mac osascript tool (`do shell script "..."`). eBay tokens/creds live in ~/ebay_weekly_rankings.py. eBay API is reachable from the Mac.

STEPS each run:
1. Refresh the working list: `/usr/bin/python3 ~/ebay_short_titles_pull.py` — writes ~/ebay_short_titles.json (all current active titles under 50 chars, with id/store/title/price).
2. Read ~/ebay_title_enrich_state.json — these item IDs are already enriched; SKIP them.
3. From ~/ebay_short_titles.json, pick up to 20 titles that are CRYPTIC MODEL-ONLY (a brand plus a model number with no product-type word), not already enriched, and not jewelry/records/already-named-games. Prioritize higher-priced items first.
4. For each, WEB SEARCH "<brand> <model>" to identify the real product (type + key spec). Then write a clear ~80-char title: Brand + Product Type + Model + a key spec + condition only if known. NEVER fabricate specs you cannot confirm; if a model can't be identified, skip it (leave it for a human) rather than guess.
5. Save the {ItemID: new_title} pairs to ~/backlog.json (JSON object) and apply: `/usr/bin/python3 ~/ebay_title_apply.py ~/backlog.json --apply`. This records originals in ~/ebay_title_enrich_state.json so every change is reversible.
6. DM Preston on Slack (post to user_id U03BWMEM9GR as the channel_id) a one-line progress note: how many titles you enriched this run and roughly how many cryptic titles remain. When there are no cryptic model-only titles left to fix, DM "eBay title-enrichment backlog is clear ✅" and mention this task can be disabled.

All title changes are reversible via ~/ebay_title_apply.py <file> --revert. Consult the ebay-context and valley-pawn-context skills for brand voice. Keep going a batch per day until the backlog is clear.