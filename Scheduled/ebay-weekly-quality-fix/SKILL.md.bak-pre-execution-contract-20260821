---
name: ebay-weekly-quality-fix
description: Weekly: review new eBay listings across all 5 Valley Pawn stores, auto-fix title/category/photo issues, and DM each manager what was fixed and why.
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


> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. Manager DMs here should describe what was fixed and why in plain terms — no script names, no API/Trading-API references. If anything later in this file conflicts with this standard, this standard wins.


Weekly eBay NEW-LISTING quality review and AUTO-FIX for all 5 Valley Pawn stores (Roanoke, Culpeper, Harrisonburg, Lexington, Waynesboro). Goal: review every listing created in the last 7 days, FIX the quality issues yourself, then DM each store's manager what was wrong, what you fixed, and why. Do NOT ask the team to fix things — you fix them.

ACCESS / TOOLS:
- Run scripts on the Mac with the Control-your-Mac osascript tool: `do shell script "..."`. eBay's API is reachable from the Mac.
- eBay Trading API. Per-store user tokens and app creds live in ~/ebay_weekly_rankings.py (the STORES list of {name, token}; plus APP_ID, DEV_ID, CERT_ID -- see that file; never hardcode credential values in this SKILL.md).
- Helper scripts already built (idempotent, reversible):
  • ~/ebay_title_stripper.py <Store> --apply  → strips internal intake codes like (VA123456) from titles. Only changes titles that still have a code, so re-running fixes new listings. Reversible via ~/ebay_title_state.json.
  • ~/ebay_caps_fixer.py <Store> --apply  → converts ALL-CAPS titles to proper case. Reversible via ~/ebay_caps_state.json.
- eBay Taxonomy API for categories (no per-store auth needed): get an app token via client_credentials — POST https://api.ebay.com/identity/v1/oauth2/token, header Authorization: Basic base64(APP_ID:CERT_ID), body grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope. Then GET https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?q=<title> with Bearer <app_token>.

STEPS each run:
1. For each store, pull listings created in the last 7 days (Trading API GetMyeBaySelling ActiveList; keep items whose ListingDetails/StartTime is within 7 days).
2. Run the mechanical fixes on each store: `/usr/bin/python3 ~/ebay_title_stripper.py <Store> --apply` and `/usr/bin/python3 ~/ebay_caps_fixer.py <Store> --apply` (idempotent — they only touch what still needs it, i.e. this week's new listings).
3. For each NEW listing with a weak or short title, WRITE a strong ~80-character keyword title (brand + model + key specs + condition + searchable keywords) and apply it via Trading API ReviseFixedPriceItem (<Item><ItemID>..</ItemID><Title>..</Title></Item>). For cryptic model-only titles, do a quick web search to identify the product rather than guessing. Never fabricate specs you can't confirm.
4. Check each new listing's category against the Taxonomy suggestion; if clearly wrong, correct it via ReviseFixedPriceItem PrimaryCategory. If eBay rejects the category change on an active listing, note it instead.
5. Review each new listing's PRIMARY photo: fetch photos via GetItem (PictureDetails/PictureURL) and actually look at the primary image. Flag intake/webcam stills, blurry photos, and detail close-ups used as the primary. If a better whole-item photo already exists in the listing, reorder it to be primary via ReviseFixedPriceItem. If new photos are needed (can't fix yourself), note it for the manager.
6. Tally per store: how many new listings, what was wrong, what you fixed.

THEN DM each store's manager on Slack (post to their user_id as the channel_id) a concise, friendly note in plain language: how many new listings you looked at, what was wrong with them in plain terms (weak title, wrong category, bad main photo), what you already fixed, anything only they can do (e.g. re-shoot a photo), and a one-line why (good titles/categories/photos help items sell faster). Do not mention script names, "Trading API," "ReviseFixedPriceItem," or any tool/system name in the DM — describe the fix in plain terms only. Manager Slack IDs:
  Roanoke → Benjie U0631AECK4K | Culpeper → Sandi U04C5DL5EKH | Waynesboro → Chadd U04U136MF6V | Harrisonburg → Walker U09UTFT4P7X | Lexington → Uriah U09H9ES2LKA
Also DM Preston (Operations, U03BWMEM9GR) a short roll-up across all stores, same plain-language rule. If a store had no new listings or nothing to fix, send a quick "all clean this week" note or skip it.

All title changes are reversible via the state files. Consult the ebay-context and valley-pawn-context skills for brand voice. Keep DMs brief and warm.