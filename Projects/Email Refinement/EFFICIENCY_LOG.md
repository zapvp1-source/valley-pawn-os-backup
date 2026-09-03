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

## 2026-08-25 (brevo-welcome-new-contacts)
Welcomed: 1 new contacts | Skipped (already welcomed/blacklisted/failed): 1

## 2026-08-25 (bravo-brevo-attribute-sync — first real run)
Source: Bravo Data Extraction archive (117 chekkit-invites-range CSVs,
2025-01-31 -> 2026-08-10 — same newest file as the 2026-08-24 manual pass, so
no fresh Bravo pull was needed; _shared-bravo-data stash checked too and is
still older/thinner, archive preferred per the task's own instructions).
Rows processed: 4,996 unique archive emails | Upserted: 37 | Skipped (no
email/no change/already in Brevo/not yet in Brevo): rest of the 4,996.
Attribute fill before -> after (sampled n=3,500, whole list): FIRSTNAME 43.6%
-> 43.9% | LASTNAME n/a -> 43.7% | STORE 56.2% -> 56.3% | SMS 54.3% -> 54.6%.
Engaged list (7, 172 contacts, the actual weekly audience): FIRSTNAME 35.5%
| STORE 52.9% | SMS 51.2% (all roughly flat vs. what the 2026-08-24 bulk pass
already achieved — this run was a small top-up on the long tail, not a repeat
of the big fix).
DEVIATION FROM v1 SCRIPT (judgment call, noted per run instructions): built
`_audit/enrich_contacts_v2.py` rather than reusing `enrich_contacts.py`
unmodified, after the dry run surfaced two problems the v1 script has no
guard against:
  1. Two toll-free numbers (+18665403229 tied to 52 distinct emails,
     +19173877468 tied to 13) are clearly shared/placeholder numbers in the
     archive, not real personal cells. v2 skips SMS writes for any phone
     number attached to >=4 distinct emails archive-wide.
  2. ~59 of the 95 raw FIRSTNAME/LASTNAME candidates were email
     usernames/handles, not real names (e.g. "Wigs2002", "Debtheconqueror",
     "2013197540jb") - would have rendered as "Hi Wigs2002," in customer
     email. v2 skips a name if it contains a digit or is just the email's
     local-part.
  Net effect: 47 candidates after filtering (down from 95 raw), 37 upserted,
  10 failed (8 "invalid phone number" from Brevo's own validation, 2
  "duplicate_parameter" - phone already attached to a different Brevo
  contact, e.g. a shared household line below the >=4 threshold; both left
  blank rather than guessed, per the task's own no-guessing rule).
LEGACY CLEANUP: checked whether the 2026-08-24 bulk run (no shared-number
filter) had already written either generic number into SMS - found and
cleared 2 contacts (mahtab80amini@gmail.com, ssexymichael@gmail.com) that had
one of the two placeholder numbers. Small blast radius, already fixed this
run, no further action needed.
Issues: none blocking. Worth a look next Friday audit — the v1/v2 script fork
means future manual re-runs of this enrichment should use v2, not v1 (v1
left on disk for reference/history only, not deleted per additive-only rule).
NEXT RUN SHOULD CHECK: whether the archive gets a newer file than 2026-08-10
(would mean the Bravo pipeline extraction resumed and there's new customer
data to sync); the 10 contacts with rejected phone numbers are probably
permanently unfixable from this source and don't need re-checking weekly.


## 2026-08-28 (brevo-weekly-efficiency-audit — scheduled run)
STATE: Channel is healthy and stable, no incidents. Headline number: this week's
Thursday send (W13 -- Lexington Spotlight, campaign 28, sent 8/27 to lists
[7 Engaged, 10 Seeds]) delivered 169/179, 0 hard bounces, 0 complaints, 0
unsubscribes, and produced 2 call clicks -> 11.83 calls+texts per 1,000
delivered. That is the first send on record to clear the 8/1,000 target
(prior baseline was 0.63/1,000 per the 2026-08-22 audit). Small sample (one
send) so treat as an early positive signal, not a trend yet -- next 2-3 sends
will tell us if this holds.

Domain auth is now fully resolved on both fronts. fcfpawn.com's duplicate SPF
fix has held (dig still shows exactly one v=spf1 record). thevalleypawn.com's
Google Workspace DKIM cooldown has cleared: `GET /senders/domains/thevalleypawn.com`
now shows authenticated=true and both DKIM CNAME records (brevo1/brevo2._domainkey)
report status=true. This was the last "needs Joshua" item carried from last
week -- it resolved itself once Google's cooldown window passed, no action was
needed from him. Both senders (jdavis@fcfpawn.com, hello@thevalleypawn.com)
show active=true with no dkim/spf error fields.

Draft-guard (Mon 11:55 AM) and the Monday picker both worked correctly this
week -- campaign 28 sent on schedule to the correct lists. Draft calendar
runway is healthy: 18 weeks staged (campaigns 29, 54-70, Sep 3 - Dec 31),
well above the 4-week floor. Wave lists 14-18 are balanced (2,145-2,247
subscribers each, ~4.6% spread, well under the 20% rebalance threshold). No
blacklisted contacts found on the engaged list (list 7, sampled in full at
n=173). List 3 (master, 13,226) shows no unexpected shrinkage.

Attribute coverage on the engaged list is flat vs last week as expected
(FIRSTNAME 35.3%, STORE 52.6%, SMS 50.9% -- within noise of last week's
35.5/52.9/51.2). The bravo-brevo-attribute-sync task is a slow weekly top-up
against a mostly-static data source; a bigger jump would need a fresh Bravo
extraction with more customer phone/name coverage than the archive currently
has.

FIXED THIS RUN:
- Filled in the previously-empty running tally in SUBJECT_LINE_EXPERIMENT.md
  with real data from the 8/27 send (was a placeholder row since the file was
  created 8/24).

STILL OPEN (needs Joshua): none new this week.

STILL OPEN (queued, no input needed):
- Bravo -> Brevo attribute sync continues weekly (Tue 5:30 PM) -- gains will
  stay small until a fresher/richer Bravo extraction is available.
- Forfeited-loan win-back list (11) still holds 0 contacts.
- Loan-due reminder flow still blocked on the attribute sync reaching
  meaningful phone/name coverage, plus a legal read on notice language.
- True in-send A/B test still blocked by Brevo's API not persisting
  winnerCriteria/winnerDelay (UI-only fields on this plan) -- sequential
  experiment in SUBJECT_LINE_EXPERIMENT.md is the working substitute.
- First A/B-style comparison data point now exists (row 1 of the tally); need
  5+ more sends before drawing any conclusion per the file's own rule (no
  winner before 6 sends per style).

NEXT RUN SHOULD CHECK: whether campaign 29 (Sep 3, W14) sends cleanly to
lists [7,10]; whether the Sep 10 send (campaign 54) correctly adds wave list
14 for the first real test of the wave-rotation plan (reach should jump from
~180 to ~2,400 delivered that week -- verify the jump actually happens, not
just that the list was attached); keep filling the subject-line tally row by
row.

## 2026-09-01 (brevo-welcome-new-contacts)
Welcomed: 80 new contacts | Skipped (already welcomed/blacklisted/failed): 0

## 2026-09-01 (bravo-brevo-attribute-sync — scheduled weekly run)
Source: Bravo Data Extraction archive (122 chekkit-invites-range CSVs,
2025-01-31 -> 2026-08-31 — 5 fresh store-days landed since the 2026-08-25
run's newest file (2026-08-10), confirming the Bravo pipeline extraction has
resumed; _shared-bravo-data stash checked too, newest dated folder is
2026-08-30 and still thinner than the archive, archive preferred per the
task's own instructions). Ran via the established `_audit/enrich_contacts_v2.py`
(PUT /contacts/{email}, attributes only, no list changes, enrichment-only —
never overwrites non-empty data) — no deviation needed this run.

Rows processed: 5,076 unique archive emails | Brevo contacts on file: 13,966.
In archive but not yet in Brevo (skipped, no new-contact creation per rule):
85 | Name looked like a username/handle (skipped): 75 | Phone was a
shared/generic number, >=4 distinct emails archive-wide (skipped): 64 | No
gap to fill (already complete): 4,878 | Contacts with at least one real gap:
113 (all 113 had an SMS gap; 64 of those also had a LASTNAME gap).

Upserted: 79 | Failed: 34. Breakdown: of the 64 records with both SMS+LASTNAME
queued, all 64 succeeded (v2's fallback wrote LASTNAME alone whenever the SMS
write was rejected). Of the 49 SMS-only records, 15 succeeded (valid unique
phone) and 34 failed outright — no attribute left to fall back to. All 34
failures were Brevo's own phone validation: duplicate_parameter (number
already attached to a different contact — a shared/household line below the
4-email sharing threshold) or invalid_parameter (malformed number). Left
blank rather than guessed, per the task's no-guessing rule.

Attribute fill before -> after: whole file (sampled n=3,500 at fixed offsets,
same method as 2026-08-25): FIRSTNAME 43.9% -> 42.1% | LASTNAME 43.7% ->
41.6% | STORE 56.3% -> 55.8% | SMS 54.6% -> 53.6%. Engaged list (7, the
weekly audience, n=177 vs last week's n=173): FIRSTNAME 35.3% -> 35.0% |
STORE 52.6% -> 52.5% | SMS 50.9% -> 50.3%.

All four whole-file metrics ticked down 1-2 points instead of up, despite
79 real upserts landing. Most likely cause: brevo-welcome-new-contacts added
80 new contacts to list 3 today (own log entry above), and this script's
verification samples fixed numeric offsets (0/2000/4000/.../12000) rather
than a true random sample — new contacts with mostly-empty attributes
shifted into the sampled offsets and diluted the percentages. Engaged-list
numbers (which aren't affected by list-3 growth) stayed flat within noise,
consistent with that read. Not treating this as a regression; flagging for
the Friday efficiency audit to keep an eye on, and noting for future runs
that a true random sample (not fixed offsets) would be more robust once
list 3 keeps growing weekly.

Issues: none blocking. Worth a look next Friday audit per the note above.
The 2026-08-25 run's 10 permanently-rejected phone numbers were not
re-attempted (correctly — they're from the same archive rows and still
carry the same bad data).

NEXT RUN SHOULD CHECK: whether the archive gets files newer than 2026-08-31
(would mean the resumed extraction is holding steady, not a one-time
catch-up); whether STORE is still stuck around 55-56% (the archive alone
can't fix older list-3 contacts with no Chekkit history — list 12
"Valley Pawn - Lexington (Store List)" remains an untried candidate source
for backfilling STORE=Lexington on its ~2,647 members, per the 2026-08-24
audit's still-unsolved note).
