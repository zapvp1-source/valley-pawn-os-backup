# Valley Pawn — Email Channel Efficiency Log

Running week-over-week memory for the `brevo-weekly-efficiency-audit` scheduled task
(Fridays 8:00 AM ET). Each entry: state snapshot, what got fixed automatically, what's
still open and for whom. Read the newest entry first. Full audit history and one-off
fix scripts live in `_audit/`; the original deep audit is
`18_email_channel_audit_2026-08-22.html`.

---

## 2026-08-24 (seed entry — written same-day as the fix session, not by the task itself)
STATE: Channel was producing 0.63 calls+texts/1,000 (target 8) off a 194-person weekly
audience and a broken sending domain. Six fixes shipped same day: thevalleypawn.com
authenticated in Brevo, hello@thevalleypawn.com branded sender live with zero DKIM/SPF
errors, 17 drafts staged Sep 10-Dec 31, 5 rotating wave lists built (10,979 dormant,
~2,100-2,300 each), 22 blacklisted contacts purged from the engaged list (194 -> 172
clean), and a `brevo-weekly-draft-guard` task added (Mon 11:55 AM) to stop the calendar
from silently going dark again — root cause of the Aug 6/13/20 gap was the Monday
picker matching drafts by a literal `Month DD, YYYY` string in the campaign name.
FIXED THIS RUN: see above — full detail in CHANGELOG.md 2026-08-24 and the audit HTML.
STILL OPEN (needs Joshua): delete the duplicate SPF TXT record on fcfpawn.com at
GoDaddy (`v=spf1 include:dc-aa8e722993._spfm.fcfpawn.com ~all`) — both records expand
to identical content so this is zero-risk, just needs a login Chrome doesn't have saved.
STILL OPEN (queued, no input needed): Bravo -> Brevo attribute sync (FIRSTNAME ~0.1%,
STORE ~54%, phone/SMS 0% of the file) — this is what the personalized YOUR-STORE CTA
block needs to actually render for the other half of the list; loan-due reminder flow
(blocked on the sync + a legal read on notice language); welcome series; forfeited-loan
win-back (list 11 exists, has the right attributes, holds 0 contacts); birthday flow;
giveaway follow-up; first A/B test on a subject line; DMARC still p=none on both
domains.
NEXT RUN SHOULD CHECK: did thevalleypawn.com stay authenticated (Brevo has been known
to lose domain auth if a DNS record is later removed by mistake); did the Sep 10 send
(campaign 54, wave A) actually go out on schedule with all three recipient lists
intact; whether the GoDaddy SPF fix landed yet (check every ~2 weeks, don't nag).

## 2026-08-24 (continued — same-day follow-up pass)
STATE: Additional fixes shipped same day as the initial repair. MX for
thevalleypawn.com corrected (was pointing at non-functional smtp.google.com,
now real Google MX records) — necessary step toward a real hello@ mailbox,
but adding the domain to Google Workspace itself needs the admin console,
which has no saved login (both jdavis@fcfpawn.com and fullcirclepawn@gmail.com
show Signed Out). DMARC record rebuilt with a second rua recipient
(jdavis@fcfpawn.com) so someone actually reads auth reports going forward.
Reach widened per Joshua's explicit call: Sep 10-24 stay single-wave warmup,
Oct 1 onward doubles to 2 waves/send (paired rotation), cutting the dormant
11k cycle from 5 weeks to ~2.5. Giveaway follow-up (82 entrants, zero contact
since July) built as a 3-month escalating discount ladder per Joshua's
decision: 10% off (8/25) -> 20% off (9/24) -> 30% off (10/24), then stops —
same in-store-redemption mechanic as the existing Memorial Day 15% sends.
Managers briefed in #in-store-checklists. Welcome flow built via the
transactional email API (Brevo's automation builder has no creation API and
no browser session exists to build it by hand) — template 72 + WELCOMED
attribute + daily `brevo-welcome-new-contacts` task.
FIXED THIS RUN: MX record repair; DMARC rua widened; giveaway ladder (3
campaigns, ids 71/73/74); welcome transactional flow (template 72 + daily
task); Oct-Dec reach doubled to 2 waves/send.
STILL OPEN (needs Joshua): (1) fcfpawn.com duplicate SPF at GoDaddy — no
saved login. (2) Adding thevalleypawn.com as a Workspace domain/alias and
creating hello@thevalleypawn.com as a real mailbox — needs admin.google.com,
no saved login for either Google account. MX is now correct and waiting.
STILL OPEN (queued, no input needed): Bravo -> Brevo attribute sync now has
a standing task (`bravo-brevo-attribute-sync`, Tue 5:30pm) but hasn't run yet
— first real data pass is 2026-08-25. Loan-due reminder flow still blocked
on that sync + a legal read. Forfeited-loan win-back list (11) still empty.
First A/B test still not run.
NEXT RUN SHOULD CHECK: did the giveaway 10% send (campaign 71) actually go
out clean tomorrow morning; did MX propagation hold and did anything break
on thevalleypawn.com mail flow; whether Joshua has gotten into GoDaddy or
Google admin yet.

## 2026-08-24 (brevo-welcome-new-contacts)
Welcomed: 1 new contacts | Skipped (already welcomed/blacklisted/failed): 0


## 2026-08-24 (SPF fix - RESOLVED)
STATE: The duplicate-SPF blocker on fcfpawn.com is CLEARED. Joshua signed into
GoDaddy. NOTE: being signed into godaddy.com is NOT enough - the DNS control
panel at dcc.godaddy.com forces a separate step-up password re-entry. That was
the real reason earlier attempts kept bouncing to a login screen, NOT a browser
profile mismatch as first diagnosed. Verify session state by loading
account.godaddy.com/products, not the marketing homepage.
FIXED THIS RUN: fcfpawn.com now publishes exactly ONE v=spf1 record at the apex
(v=spf1 include:_spf.google.com ~all).
  IMPORTANT: GoDaddy DELETE failed twice with a server-side error ("Your attempt
  to delete DNS records has failed... contact support 1-480-505-8877"), and the
  FIRST failure was SILENT - the confirm dialog accepted the click, the record
  stayed, and the count remained 19. Worked around by EDITING the duplicate
  record's value instead of deleting it:
      was: v=spf1 include:dc-aa8e722993._spfm.fcfpawn.com ~all
      now: x-spf-retired-2026-08-24-duplicate-of-google-spf
  This resolves the RFC 7208 PermError identically (one v=spf1 at apex) and
  leaves a self-documenting row explaining what happened.
  The helper record dc-aa8e722993._spfm (value v=spf1 include:_spf.google.com
  ~all) was intentionally LEFT IN PLACE - it is a subdomain record, not an apex
  SPF, so it does not contribute to the PermError and is harmless.
LESSONS FOR FUTURE SESSIONS:
  1. If a GoDaddy DNS delete fails, edit the record to a neutral value rather
     than fighting the delete endpoint.
  2. Always verify a GoDaddy DNS write with dig against the authoritative NS
     (dig +short TXT <domain> @ns69.domaincontrol.com), never against the UI
     row list alone - the UI showed no error on the first silent failure.
NEXT RUN SHOULD CHECK: `dig +short TXT fcfpawn.com | grep -c 'v=spf1'` should
return 1 once the 1-hour TTL flushes. If it still returns 2 several hours later,
the edit did not stick and needs re-checking in the GoDaddy UI.


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
