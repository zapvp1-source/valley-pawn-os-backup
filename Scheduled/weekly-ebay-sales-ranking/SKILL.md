---
name: weekly-ebay-sales-ranking
description: Every Monday at 11:30 AM — verify that the eBay weekly rankings were posted to Slack #ebay-performance by the automated LaunchAgent script. If not, post notice to #ebay-performance (no DM).
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running the weekly eBay sales ranking verification task for Valley Pawn.

A macOS LaunchAgent runs ebay_weekly_rankings.py automatically every Monday at 6:00 AM on Joshua's Mac. The script pulls last week's eBay sales from all 5 stores and posts ranked results directly to Slack #ebay-performance via webhook.

Your job is to VERIFY the post happened:

1. Search Slack #ebay-performance (channel ID: C0ANVN5KX4Y) for a message containing "eBay Weekly Sales Rankings" posted today.
   - Use slack_search_public with query: "eBay Weekly Sales Rankings" in:#ebay-performance
   - Check if any result was posted today (Monday).

2. If found → End task. No action needed.

3. If NOT found → The LaunchAgent didn't fire. Fall back:
   a. Use computer-use write_clipboard to put this command in Joshua's clipboard:
      python3 "/Users/joshuadavis/Desktop/ebay_weekly_rankings.py"
   b. DM Joshua on Slack (user ID: U03BB52MDSA):
      "📦 *eBay Weekly Rankings* — The automated script didn't run this morning (no post found in #ebay-performance). The command is in your clipboard — open Terminal and paste it to run manually. Say *'done'* here when it finishes."
   c. End the task.

NEVER post to #ebay-performance yourself. The script handles that via webhook.