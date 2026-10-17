---
name: daily-clockin-check
description: Check Gusto clock-in status at 10:15 AM Mon-Sat and post summary to Slack #general only (no DMs). MCP-first (Gusto API, headless) with Chrome flow as automatic fallback. Wednesdays: Culpeper and Roanoke only; other days: all stores. 15-min grace after 10 AM open.
model: claude-sonnet-5
---

Read and follow /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/task_prompts/daily-clockin-check.md exactly — it is the complete, authoritative instruction set for this task (Step 0 duplicate guard first, then the Gusto connector path, post to Slack #general C03BETSS669 only, no DMs). If that file cannot be read, post nothing and append one row to /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md saying the clock-in instructions file could not be read. Key rules in case of doubt: store staff only (departments Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro; never anyone named Davis; never Preston Peters or Sandi Cole); Wednesdays Culpeper, Roanoke and Waynesboro are open (Waynesboro open Wednesdays from 2026-10-14); plain language, no system names in the post.