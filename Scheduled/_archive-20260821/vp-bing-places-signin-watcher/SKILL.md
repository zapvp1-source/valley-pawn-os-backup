---
name: vp-bing-places-signin-watcher
description: COMPLETE 2026-08-03 — Bing Places sign-in achieved and all queued whitelisted fixes applied and verified in the same session. Disabled; no further purpose.
---

LOCAL ACCESS GATE — DO THIS FIRST. This task runs ON Joshua's Mac Studio and DOES have local access. If `mcp__Control_your_Mac__osascript` is not loaded, load it via ToolSearch (`select:mcp__Control_your_Mac__osascript`) and probe it with a trivial `do shell script "echo READY"`. Retry every 30s for up to 12 minutes before treating local access as unavailable. NEVER conclude this is a cloud run or that there is "no Mac bridge" — the tools `mcp__remote-devices__*` and `mcp__claude-code-remote__send_later` DO NOT EXIST and must never be probed for or cited. Browser work uses `mcp__Control_Chrome__*` (load via ToolSearch: `select:mcp__Control_Chrome__open_url,mcp__Control_Chrome__get_page_content,mcp__Control_Chrome__execute_javascript`). All filesystem I/O goes through osascript `do shell script`, never the Write tool.

PURPOSE. Three whitelisted Valley Pawn Bing Places corrections have been blocked since 2026-07-22 by exactly one thing: bingplaces.com has no signed-in Chrome session on this Mac. This task watches for that session and executes the moment it appears, so the fixes land without another week of re-reporting.

STEP 1 — CHECK SIGN-IN. Open https://www.bingplaces.com/DashBoard/Manage in Chrome and read the page.
- If the page shows the anonymous marketing landing ("Connect to millions of customers", "Sign in", "Contoso Cafe"), Joshua is NOT signed in. Do nothing further. Do NOT post to Slack. Do NOT DM Joshua. Exit silently. (Silence here is correct — this is a watcher, not a reporter. Joshua has already been told once.)
- If the page shows an actual business dashboard with Valley Pawn locations, proceed to STEP 2.

STEP 2 — APPLY THE QUEUED FIXES. Working only within Bing Places, correct these three, one at a time, re-reading the page after each save:
  a) ROANOKE — address is missing "Suite C". Canonical: 2362 Peters Creek Rd NW, Suite C, Roanoke, VA 24017.
  b) HARRISONBURG — address must read 1790 E Market St, Ste 22, Harrisonburg, VA 22801. If the listing shown is a legacy "Dixie Pawn" record at "1790 Toni St" that is NOT under this account, do NOT edit it — that is a separate duplicate requiring a claim/merge; log it as needs-joshua and move on.
  c) LEXINGTON — the "About"/business description references a sixth "Salem" location that does not exist. Valley Pawn has exactly five stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. Remove the Salem reference; leave the rest of the description intact.
Confirm canonical NAP against the `valley-pawn-context` skill before typing anything. Never use the name "Dixie Pawn" for any Valley Pawn listing.

STEP 3 — VERIFY. For each store edited, load https://www.bing.com/maps?q=valley+pawn+<city>+va and read it. Bing syndication can lag hours to a day — if the public map has not updated yet, record the item as "submitted, pending Bing review", NOT "fixed".

STEP 4 — LOG. Append one row per item to the "Valley Pawn — AI Search Autofix Log" Google Sheet (ID 1A_gJuj5siq2bEKE7-ZvVyjAs6DNK7rzEaKkBbkBY9yY, tab "Untitled"), columns Date, Source Task, Finding, Category, Action Taken, Verification Result, Status, Notes. Sheets writes DO work — via osascript, `cd ~/Documents/Claude/Scheduled/_shared` and call `sheets_helper.SheetsClient().append(sheet_id, "Untitled!A:H", rows)`. Never report "no Sheets write access"; that claim is false.

STEP 5 — REPORT AND STAND DOWN. Post ONE message to Slack #ai-marketing (C0BCEESUANM): "🔧 Bing Places sign-in detected — applied the queued Valley Pawn corrections. Fixed: <n> · Pending Bing review: <n> · Still needs you: <n>", then one short plain-language line per item. Then append a line to /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md under a "## <today's date> (manual entries)" heading recording what landed. Finally, disable this task via `mcp__scheduled-tasks__update_scheduled_task` with enabled:false — its job is done.

FAILURE POLICY. If the run fails outright, send Joshua ONE plain-language Slack DM (D03BHQH5VGT): '⚠️ Scheduled task "vp-bing-places-signin-watcher" did not complete — <date>.' Nothing technical in the DM. Never send failure notices to any team channel, store manager, or employee.