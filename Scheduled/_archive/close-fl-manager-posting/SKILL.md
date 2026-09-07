---
name: close-fl-manager-posting
description: One-time: close/pause the free St. Augustine, FL Store Manager Indeed posting after its 2-day free run
---

Load the `enterprise-map` skill first (mandatory, Domain 1 - Valley Pawn), then the `indeed-access` skill for login mechanics.

Context: On 2026-08-31, Joshua asked for a free Indeed job posting for a "Store Manager" role in the St. Augustine / Jacksonville, FL area (a new Valley Pawn location currently being developed there), pay range $22.00-$26.00/hr, explicitly to "run free for a couple days" only.

The job was posted as a FREE (non-sponsored) job on Indeed for Employers (account: fullcirclepawn@gmail.com — note this session used fullcirclepawn@gmail.com, not the usual jdavis@fcfpawn.com, both appear to have access to the same Jobs dashboard). Job details:
- Title: Store Manager
- Location: Saint Augustine, FL
- Company: Valley Pawn
- Posted: August 31, 2026
- Direct URL: https://employers.indeed.com/jobs/view?employerJobId=aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iL2E4NzY2OGQ2LWJmNDUtNGI5Yi1iNWZkLTg3ZDM2ZjYyZmI3OQ%3D%3D

Task: Navigate to the Jobs dashboard (https://employers.indeed.com/jobs) using Claude in Chrome, find this specific "Store Manager" / "Saint Augustine, FL" posting (search/filter by title + location, it should be the only Florida listing since all other postings are Virginia stores), open it, and CLOSE (not just pause) the job posting so it stops accepting new views/applications after its ~2-day free run. Verify by confirming the job status shows "Closed" on the Jobs dashboard afterward — don't just trust a confirmation toast.

Do NOT sponsor, boost, or spend any money on this posting. Do NOT touch any other job postings (all 5 VA stores' Sales and Loan Associate / Store Manager postings) — those are established, ongoing, and off-limits per Rule #4 (additive/don't touch other infra).

If the job can't be found (e.g., it was already closed manually, or Indeed auto-expired it), that's fine — just verify its current status and log the outcome. No Slack notification needed for a routine success; if something is genuinely broken (e.g., job still open and won't close), send Joshua one plain-language Slack DM per the Failure Alert Policy.

Log the outcome as a one-line addendum in `~/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` and note in `~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` that this open item (FL manager posting, logged 2026-08-31) is now closed out.