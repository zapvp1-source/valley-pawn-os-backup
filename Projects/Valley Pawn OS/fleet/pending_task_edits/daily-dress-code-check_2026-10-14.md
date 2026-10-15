# Pending edit — daily-dress-code-check (2026-10-14)

Joshua 10/14: Waynesboro is now open 6 days a week — add it to the dress code task.

Change: in the task's "Locations to Check" section, replace the Wednesday line with:

- **Wednesdays:** Check Culpeper, Roanoke, and Waynesboro (Roanoke open Wednesdays from 9/30/2026; Waynesboro moved to a 6-day week — now open Wednesdays — as of 2026-10-14). Harrisonburg and Lexington remain closed Wednesdays.

And the description to: "... Wednesdays: Culpeper, Roanoke, and Waynesboro only. All other days: all 5 locations."

Why it is pending: update_scheduled_task refuses — "this task's file is hard-linked to another file. Replace it with a plain copy."
Fix: on the Mac, break the hard link (Finder: Duplicate SKILL.md in ~/Documents/Claude/Scheduled/daily-dress-code-check/, move the original to Trash, rename the copy to SKILL.md),
then apply the change with update_scheduled_task (description + prompt). Session file tools cannot write that path; the cloud bash sandbox cannot reach it.
Deadline: before Wed 10/21 10:30 AM run (Thu–Tue runs already check all 5 stores).

**APPLIED 2026-10-14 12:45 ET** via host queue job `20261014-1450-ddc-waynesboro-wed.sh` (install_skill.sh). Verified in Scheduled/daily-dress-code-check/SKILL.md. Source kept at fleet/skill_sources/daily-dress-code-check.SKILL.md.
