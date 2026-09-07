---
name: monthly-publication-audit
description: 2nd and 4th of month, 10 AM — verifies every monthly publication in PUBLICATION_CALENDAR.md actually landed for the prior month (reads the channel, not run records), re-runs rerun-safe producers when a post is missing, and DMs Joshua one plain line only if something could not be recovered.
---

Invoke the `enterprise-map` skill first. Then read `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/pending-tasks/monthly-publication-audit/SKILL.md` (via osascript `cat` if the Projects folder is not mounted) and follow its instructions exactly — it is the full specification for this task: what to verify, how to classify rerun-safe vs verify-only, the recovery order, the logging, and the single-plain-DM-only alert rule.