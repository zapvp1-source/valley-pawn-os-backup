---
name: weekly-loan-portfolio-refresh
description: Weekly refresh of the Loan Portfolio Optimization analysis — runs Mondays at 7am
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Run the weekly Loan Portfolio Optimization refresh for Valley Pawn.

CONTEXT:
- Project STATUS.md: /Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/STATUS.md (read FIRST)
- Bravo Data Extraction pipeline: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/
- Analysis script: /Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/local_7d4c218c-06bf-4a4e-8925-62088f81f954/outputs/run_analysis.py (may move to project folder over time)
- Output dir: /Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/

STEPS (zero-computer-use until step 3):
1. Read STATUS.md to understand current state of the project + known pipeline gaps (AHK enumerator cap, LEX dropdown bug).
2. Drop a trigger via osascript at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/. The trigger ID format: weekly-loan-portfolio-YYYY-MM-DD. JSON shape:
{
  "id": "weekly-loan-portfolio-<date>",
  "requested_at": "<ISO>",
  "reports": [
    {"name": "loan-portfolio-2026", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "2025-<thisweek - 365>..<yesterday>"}
  ]
}
3. Poll for the result JSON at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/<id>.result.json (every 60s, timeout 20 min). DO NOT drive Bravo's UI — the watcher in the Parallels VM handles it.
4. When done, run the analysis script (use osascript to run python3 from /Users/joshuadavis/Library/Application Support/.../run_analysis.py).
5. Verify Excel + JSON + dashboard HTML refreshed in /Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/.
6. Post a 3-bullet summary to Slack channel #optimize-loan-portfolio (if it exists, else DM Joshua at U03BB52MDSA) with:
   - Which stores got fresh data this week
   - Top headline finding (e.g., "HAR redemption still trailing at X%")
   - Any pipeline failures that need attention
7. Update STATUS.md session log with date + what changed.

KNOWN ISSUES (don't try to fix in this scheduled task, just note in the Slack post):
- AHK enumerator caps at ~200 rows per pull — most stores return truncated data
- LEX dropdown discovery fails consistently
- CUL & WAY inventory-details not yet in pipeline

This is an additive refresh task — do NOT modify the saved Bravo report or any existing AHK handler.