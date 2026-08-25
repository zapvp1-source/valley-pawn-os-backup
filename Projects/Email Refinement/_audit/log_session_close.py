#!/usr/bin/env python3
"""Append the continuation-session entry to EFFICIENCY_LOG.md."""
import os

ENTRY = """

## 2026-08-24 (continuation - DMARC, A/B, experiment framework)
STATE: SPF fix CONFIRMED PROPAGATED - `dig +short TXT fcfpawn.com | grep -c
'v=spf1'` now returns 1. Every send from here carries a clean authentication
result for the first time.
FIXED THIS RUN:
  - fcfpawn.com DMARC widened to `v=DMARC1; p=none;
    rua=mailto:rua@dmarc.brevo.com,mailto:jdavis@fcfpawn.com; fo=1` and verified
    authoritatively. Both domains now send aggregate + forensic reports somewhere
    a human actually reads. Deliberately kept at p=none: nobody has ever read a
    DMARC report for this org, so moving to quarantine before reviewing a few
    weeks of data could start silently blocking legitimate mail.
  - Subject-line experiment framework created:
    "Email Refinement/SUBJECT_LINE_EXPERIMENT.md", owned by the Friday audit.
ATTEMPTED AND DELIBERATELY REVERTED - read this before trying again:
  Enabled a real in-send Brevo A/B test on campaign 54 (Sep 10). `abTesting`,
  `subjectA`, `subjectB` and `splitRule` all persisted fine via PUT. But
  **`winnerCriteria` and `winnerDelay` silently do NOT persist** - the API
  returns 204 and reads back None on both. They appear to be UI-only fields, the
  same limitation as contact segments on this plan.
  Shipping that half-configured was judged unsafe: with a split rule set but no
  winner criteria or delay, it is unclear whether Brevo ever sends the remaining
  50% of the audience. The entire premise of this project is that people are not
  receiving our emails, so a config that might silently drop half a send is not
  acceptable. REVERTED abTesting to false and set campaign 54's single subject to
  the stronger challenger variant ("5 things worth the drive to our Roanoke
  store"). Restructured as a SEQUENTIAL experiment instead - alternating subject
  styles across consecutive weekly sends, which needs no UI and carries zero
  delivery risk.
  If anyone ever has a live Brevo web session, converting this to a true in-send
  split test is a real upgrade - the sequential version is confounded by
  week-to-week variation in content, season and audience wave size.
STILL OPEN (needs Joshua): Google Workspace DKIM for thevalleypawn.com - blocked
by Google's own 24-72h cooldown after adding a domain alias, not by anything on
our side. Retry from ~2026-08-26. MX and SPF for that domain already show
Complete in the Workspace console.
STILL OPEN (queued, no input needed): bravo-brevo-attribute-sync first run
2026-08-25 5:30 PM - note the newest stash in _shared-bravo-data is 2026-07-21,
so that run will likely need a live Bravo pull (contention check first) or will
report a data gap. Loan-due reminders still blocked on that sync plus a legal
read. Forfeited-loan win-back list (11) still holds 0 contacts.
NEXT RUN SHOULD CHECK: whether the giveaway 10% send (campaign 71) went out clean
on 8/25 9am; whether brevo-welcome-new-contacts found anyone to welcome; whether
the Bravo sync got fresh data or hit the stale-stash path; and start filling the
running tally in SUBJECT_LINE_EXPERIMENT.md from the 8/27 send onward.
"""

path = os.path.expanduser(
    "~/Documents/Claude/Projects/Email Refinement/EFFICIENCY_LOG.md")
with open(path, "a", encoding="utf-8") as f:
    f.write(ENTRY)
print("appended", len(ENTRY), "chars")
