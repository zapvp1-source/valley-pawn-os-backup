# Policy Day — plan of attack (built 2026-10-21 with the Compliance, HR, Training and Operations projects)

**Goal (Joshua 10/21):** every new or changed policy, procedure and acknowledgment reaches the field once a month — one update, one signature — never sporadically.

## What was wrong
- 35 staff-facing items were built or approved but never delivered; 30 others went out one at a time over 3 months (Slack posts, Gusto docs, DMs, a #general post), some twice, some contradicting each other (Compliance/FIELD_RELEASE_INVENTORY_2026-10-21.md).
- Every project could send on its own: policy-lifecycle posted and sent per policy, compliance programs planned their own Gusto sends, HR sent acks in Gusto, Preston's assistant sent DocuSign acks, the Academy taught rules staff hadn't signed.
- The signature step depended on a Gusto browser session that keeps signing out, so sends and the weekly chase failed silently.

## The system (now in place)
1. **One intake:** anything staff-facing, from any department, becomes a row in `POLICY_QUEUE.md`. Nothing is sent on approval day. (policy-lifecycle skill update proposed so every future policy follows this automatically.)
2. **One day:** Policy Day = 1st business day. Cutoff the 25th. Preview to Joshua the 26th. One "approve" covers everything.
3. **One signature, in Gusto:** one Gusto Team document (current team + future hires) carrying the whole update + the Handbook/P&P acknowledgment. Gusto sign-in is automatic through Google; the runner reads status from Gusto; unsigned names go to Preston on the 15th.
4. **One post:** one #policy-announcements message on Policy Day. No in-between posts — reminders ride in the next update.
5. **One runner:** the scheduled "Policy Day runner" (daily 8:41 AM) does the sweep, build, preview, send after approval, status, Preston list and close — and logs every step in `docusign/state/<YYYY-MM>.json`, the compliance calendar row `monthly-policy-update`, the CHANGELOG and the Open Items Register.
6. **Training matches policy:** each update's items are checked against the Academy the same month; new hires get the Academy + current manuals + current acknowledgment only.

## Roadmap — what goes out when
| Update | Policy Day | Sign by | Contents | Gate |
|---|---|---|---|---|
| **November 2026** | **Wed 11/4** (Valley Pawn Academy launch day — CEO 2026-10-25) | Wed 11/4 (unsigned list to the Market Manager Fri 11/6) | Handbook v2026.8 + P&P v2026.9 revised in place 10/25 (hours, greeting, account details = name + DOB + phone on file or POA, never confirm a gun by phone, police/background-check calls, discount age ladder + 30/50 bands, returns need an email, counterfeits, late fee day 6 + 15-day legal hold + "Your loan is due on its due date.", under-21, straw purchases/gifts, call-outs by voice call, training at the store, gun-safety certificate 10.06, roles not names) + HR-2026-04 Rev2 ack naming the gun-safety certificate · Stop the Wrong Sale (VP-CP-03 / HB21) · Account Details by Phone & Text · Discounts by age · eBay 90/120/150 · eBay tender · Reloans · Bonuses — Standards First · Training Happens at the Store · Mission & Code · Academy launch · SEPARATE Gusto Team document the same day: Name, Image, Likeness & Voice Release (team, HR-2026-09) | The CEO's one "approve" (preview arrives 10/26). Stop the Wrong Sale rides on the firearms program sign-off. Reloans rides on his yes |
| **December 2026** | Tue 12/1 | Thu 12/10 | Sales Training — Week One rewritten for the Academy (replaces HR-2026-10 NRF version) · New Hire Onboarding Checklist Rev3 · Manager transaction limits written into P&P · For Managers: Monthly Store Compliance Checklist (VP-CP-07, first due 12/15) · Virginia accommodation-rights notice (poster + new-hire notice) · Customer privacy notice handout (VP-CP-05A) if counsel has cleared it · Bravo item-description rule if confirmed | Transaction-limit numbers from the Market Manager |
| **January 2027** | Mon 1/4 | Mon 1/11 | Bonus Program (regenerated from the live rules) · AML red-flag training (Academy lesson) · 4473 / straw-purchase refusal training + store refusal log · MLA covered-borrower check + script · Annual recerts due 1/31 (Academy 8.3–8.5 + gun safety) | Compliance programs signed (AML, Firearms, Lending) |
| **February 2027** | Mon 2/1 | Wed 2/10 | Store internet-outage "Crash Package" · annual compliance training day schedule | Draft not started |
| **Held (not scheduled)** | — | — | Drug-Free Workplace / THC testing (Checkr panel conflict) · Mutual Arbitration Agreement (counsel) | Joshua |

## Decisions made (defaults — tell Claude only if you disagree)
1. **Signatures stay in Gusto** (Joshua 10/21, once Google sign-in fixed the login): everything signed lives in each employee's Gusto file.
2. **November Policy Day is Wed 11/4** (CEO 2026-10-25): the Academy launches that day and every new manual, the acknowledgment and the voice release are signed that day; unsigned names go to the Market Manager Fri 11/6. From December it's the first business day.
3. **Training happens at the store, on the clock** — in the November packet (replaces the at-home wording in HR-2026-10 and OB-2026-01).
4. **THC/drug testing stays held** until you decide the Checkr panel.
5. **Policy reminders count as policy:** "clock in every time", call-out rules and similar reminders go in the update, not ad-hoc posts.
6. **Individual HR documents** (Record of Warning, Action Plan, one person's acknowledgment) keep going out on demand — they're not policy changes.

## Before 11/4 (Claude)
- Add all staff to #ask-goldilocks (the update tells them to ask there) and confirm it answers.
- 10/26 preview to the CEO; apply edits; send on Wed 11/4 after "approve" (update + the separate voice-release Team document).
- Fix any Academy lesson that conflicts with the November update (none known after the 10/21 board review; re-checked at preview).
