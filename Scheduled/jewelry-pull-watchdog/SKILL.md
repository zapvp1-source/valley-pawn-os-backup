---
name: jewelry-pull-watchdog
model: claude-haiku-4-5-20251001
description: Morning watchdog 9:15 AM (Tue-Sun): verify last night's jewelry-onhand CSVs exist; if missing, DM Joshua one plain-language alert.
---

Watchdog for the jewelry-onhand-nightly-pull task (runs 8:30 PM Mon-Sat). You run the following morning.

1. Get yesterday's date: via mcp__Control_your_Mac__osascript run `date -v-1d '+%Y-%m-%d %A'`.
2. If yesterday was Sunday: stores closed, no pull expected — end silently.
3. Check for last night's output: `ls ~/Documents/Claude/Projects/'Bravo Data Extraction'/output/ | grep '<YESTERDAY>_.*jewelry-case-counts'` via osascript.
4. If at least one store CSV exists for yesterday: healthy — end silently, post nothing.
5. If ZERO CSVs exist for yesterday: send ONE plain-language Slack DM to Joshua (channel_id D03BHQH5VGT) via the Slack connector, e.g.: "Heads up — last night's jewelry count pull didn't run (no data for <date>). Most common cause: the Claude app wasn't open at 8:30 PM. Open the app and I can run it manually, or it'll fire at the next 8:30 PM." Nothing technical, no team channels, no other messages.

Never touch Bravo. Never create triggers. Read-only check + one DM at most.