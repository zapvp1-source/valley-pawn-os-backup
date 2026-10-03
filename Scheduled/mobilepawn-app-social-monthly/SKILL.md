---
name: mobilepawn-app-social-monthly
description: 20th of each month 9:10 AM — schedules next month's MobilePawn app-download post (Brand FB/IG + 5 store FB + 5 GBP) in Publer for the 2nd Tuesday 11 AM ET.
model: claude-sonnet-5
---

Valley Pawn (Full Circle Finance Inc) — monthly MobilePawn app-download social post. Approved by Joshua 2026-09-29 ("go"). Established automation: do not question it, just run it (Rule 17).

1. Make sure ~/Documents/Claude/Projects is available (request_cowork_directory with that path if needed; if no approver is available, use a Mac shell via osascript instead).
2. Run, from the folder "MobilePawn Participation/app_outreach":
   python3 monthly_post.py
   It targets NEXT month, is idempotent (sent_log.json), schedules via Refine Social Media/vp_social_publisher.py (the only sanctioned Publer path) for the 2nd Tuesday 11:00 AM ET, and verifies every Publer job completed. Exit 0 with "OK <month>" or "already scheduled" = success.
3. If it fails: re-run once. If it still fails, append a plain dated line to fleet/FAILURE_LEDGER.md under Valley Pawn OS (create the line only, do not edit other lines) and send at most ONE plain-language Slack DM to Joshua (D03BHQH5VGT), no technical wording, e.g. "Next month's MobilePawn app post didn't get scheduled — I'll retry." Never post failures to any team channel (Rule 16).
4. On success: say nothing to Slack. Do not edit monthly_post.py captions or graphics.