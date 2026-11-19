# Loan reminder texts through Chekkit — controlled build (nothing live)

Rule (Joshua 11/18): do not change anything in Bravo or Chekkit until this is proven reliable.

## Is it cheaper? Yes.
- Bravo Oct 2026: 4,693 texts x $0.07 = $328.51 (INV2597398).
- Chekkit: 5 accounts x 2,000 texts included = 10,000/mo; over = $0.03. October use through ~10/22 (bin/chekkit_text_census.py): Culpeper 283, Waynesboro 208, Harrisonburg 259, Lexington 106, Roanoke 1,458.
- About 940 reminders per store fits inside what is already paid for, except Roanoke (about 400 over = $12). Saving about $315/mo, $3,800/yr. Bravo's flat $245.71 Mobile Messenger fee stays unless app pushes can run without it (not known).

## Built 2026-11-18 (offline)
- `reminder_core.py` — plans the day's texts from Bravo's open-loan list (FDP layout: ticket, due date, customer, SMS flag) plus a phone list. No send function exists in the file. Skips: Bravo DNT, Chekkit opt-outs, police/courtesy holds, no phone, a name that matches two phone numbers, anything already sent. One text per customer per day; an extension restarts the cycle.
- `test_reminders.py` — 8 tests pass.

## Not known yet (must be read from Bravo, look only)
1. What Bravo sends today: which messages, which days, wording (Bravo text-message setup screen). The schedule in the code (3 days before, due day, 5 days past) is a placeholder.
2. A daily Bravo export with ticket + due date + phone. The open-loan export has no phone; joining by name is not safe enough (the code refuses ambiguous names). Last full open-loan pull on disk is 10/7.

## Gates (each needs Joshua's OK)
1. Read Bravo's current text settings; add the daily open-loan + phone pull (read-only).
2. 14-day shadow: plan daily, send nothing, compare counts with Bravo's invoice and spot-check 20 customers per store.
3. Culpeper pilot: Chekkit sends, Bravo's reminders off for Culpeper only (first change in either system).
4. All stores; then ask Bravo what the Mobile Messenger fee covers.

## Update 2026-11-18 10:55 AM (Joshua)
- "Chekkit is the source of truth on Do not text, ignore Bravo." Done in code: Bravo's SMS/DNT column is never used; only Chekkit opt-outs block a text (9 tests pass).
- Texts first; eBay Desk parked at gate 1.
- Found in the 9/30 Bravo map screenshot (Customers > Schedule Mobile Event, Waynesboro): enabled events include a recurring "We Buy Gold" blast to all mobile customers and "Birthday", besides the loan/layaway reminder types (Loan Courtesy Reminder, Loan Past Due, Layaway Notice, MobilePawn Layaway Notice). So Bravo's 4,693 texts/mo are not all reminders. The screenshot is cropped: enabled list, schedule and wording per store still need one look-only read of that screen in all 5 stores (close with Cancel, never Save).

## Bravo automatic messages — read from all 5 stores 2026-11-18 ~11:30 AM (look-only, closed with Cancel)
Tool: `Bravo Data Extraction/MobileEventsRead.ahk` via `Valley Pawn OS/bin/mobile_events_read.sh` (host queue). Raw: `Bravo Data Extraction/output/mobile_events/<STORE>.txt/.png`, parsed `_parsed.json`. One UIA timeout at Harrisonburg after the read; health gate PASS; retry added; Lexington/Roanoke clean. Nothing edited.
Channel codes seen: NTFSMS (text), NTFAUT (auto), NTFREE, NTFIPN (app). Meaning of AUT/REE/IPN is inferred, not confirmed with Bravo.

Can go out as a text (SMS or Auto), 10:00 AM:
| Event | When | CUL | HAR | LEX | ROA | WAY |
|---|---|---|---|---|---|---|
| Loan Courtesy Reminder | 1 day before due | Auto | SMS | Auto | NOT SET UP | Auto |
| Loan Past Due | every Friday while past due | Auto | SMS | Auto | NOT SET UP | Auto |
| Layaway Notice | 1 day before due | Auto | SMS | Auto | NOT SET UP | Auto |
| MobilePawn Loan Past Due Notice | 1 day after due | Auto | Auto | Auto | Auto | Auto |
| MobilePawn Layaway Notice | 5 days before next due | Auto | Auto | Auto | Auto | Auto |
| MobilePawn Layaway Late Notice | every 5 days while late | Auto | Auto | Auto | Auto | Auto |
| Birthday (15% off, 30 days) | on birthday | Auto | SMS | Auto | Auto | Auto |
| Store Anniversary (15% off) | first-visit anniversary | Auto | SMS | Auto | Auto | Auto |

App only (NTFREE / NTFIPN), all 5 stores: MobilePawn loan courtesy reminders (5, 3, 1 days before and on the due date), MobilePawn layaway notice 1 day before, new-loan and new-layaway app invites, 5 app onboarding messages. "We Buy Gold" recurring = Waynesboro only, app only. Roanoke has a one-time gold message, switched off.

Wording captured: Birthday, Anniversary, Gold. Loan/layaway reminder wording sits behind template buttons (Single/Multiple ...) that were NOT opened.

Changes this makes to the build: courtesy = 1 day before due (not 3); past due = 1 day after, then every Friday; add layaway notices (1 and 5 days before, every 5 days late); birthday and anniversary texts need date of birth and first-visit date from Bravo.

## 2026-11-18 ~12:10 PM — Joshua: "lets go on all three"
1. Birthday + anniversary 15% texts: carry over unchanged. 2. Roanoke: same reminders as the other four. 3. Read Bravo's reminder wording.
- (3) FAILED TO READ, nothing changed: clicking the template buttons (Waynesboro only) shows no wording on screen, and the last attempt stalled until the automatic recovery ran (health gate PASS 12:02). Verified after: Waynesboro re-read at 12:08, all 21 events, on/off, schedule, channel and wording identical to the 10:59 read (baseline in output/mobile_events/baseline_1100). Template mode is NOT to be run again (MobileEventsRead.ahk "templates").
- Wording therefore = new drafts for Joshua to approve (in reminder_core.py TEMPLATES, marked DRAFT), or one real Bravo text forwarded from a phone.
- reminder_core.py now follows Bravo's schedule: loan courtesy 1 day before; past due 1 day after then every Friday; layaway 5 and 1 days before, every 5 days late. 11 tests pass.
- Still needed (read-only): daily Bravo list with phone + loan due date, layaway next due date, birthday, first-visit date.

## Savings double-check 2026-11-18 1:30 PM (Joshua: "double check the savings")
- Bravo text charge, two invoices: Sept 4,439 x $0.07 = $310.73 (INV2594653); Oct 4,693 x $0.07 = $328.51 (INV2597398). About $3,800/yr. App messages ($74-$83/mo) and the flat $245.71 Mobile Messenger fee do not move.
- Chekkit actual charges, 12 months (Amex 3001): base $546/mo, total $546-$597, so $0-$51/mo of overage already. Limit-reached emails: Roanoke 10/21, Harrisonburg 9/7 and 7/9, Waynesboro 5/10, Culpeper 4/7. The accounts are NOT mostly empty; my 11:00 AM figure (2,300 of 10,000 used) under-counted and is withdrawn.
- Corrected saving: if every moved text is charged Chekkit's $0.03 = about $135-$140/mo, saving about $180-$190/mo = $2,100-$2,300/yr (floor). If some fit under the 2,000 allowance, up to about $3,800/yr (ceiling). Use $2,200.
- Past-due text was 182 characters (two texts' worth); shortened to 156 at the longest store name so it bills as one. Loan-due text is 144.
- Design point found: Bravo "Auto" sends an app notice to app users and a text to everyone else. At go-live the 8 events are switched to app-only in Bravo (not off), and Chekkit texts only customers without the app, so volume stays about what Bravo texts today.

## Direction 2026-11-18 1:23 PM (Joshua)
"Focus on text first. Stay under the Chekkit limits if we can. Evaluate the effectiveness of the sends. I do not want to pay double for texts. All texts should be going off Chekkit by pricing alone."
Facts gathered 1:45 PM:
- Chekkit texts per store per month, Jul-Sep 2026 average (staff + campaigns + review invites; census 10/24): Culpeper 1,610; Waynesboro 2,370; Harrisonburg 1,340; Lexington 1,040; Roanoke 1,360. Allowance 2,000 each. Since October the weekly win-back texts add roughly 200-480 per store per month, and a monthly campaign can add 1,000+ to one store (Roanoke Oct 1,375). "event_other" rows (400-1,400/store) are not yet identified as billable or not.
- Rough check on whether Bravo's loan texts matter: loans 75+ days past due as a share of loan balance (Sept-Nov daily average vs 8/27 balance): Roanoke 1.2% (has NO Bravo loan reminder texts), Lexington 1.2%, Waynesboro 1.0%, Harrisonburg 0.8% (every reminder forced to text), Culpeper ~0%. Not a controlled test; suggests the texts are not doing much on their own.
Plan:
1. One monthly text budget per store (2,000), spent in priority order: staff conversations, missed-call and phone-menu texts, loan/layaway reminders, review invites, marketing. Marketing that does not fit goes by email (Brevo) instead.
2. No text to a customer who has the MobilePawn app; Bravo already sends them app reminders at 5, 3, 1 and 0 days.
3. Measure every send type before it gets budget: reminders = paid within 3 days of the text vs not texted; win-back = came back within 14 days; review invites = review left; campaigns = replies/visits. Reminder holdout (1 in 5 customers not texted for 30 days) once Chekkit is sending.
4. No double pay: at go-live each Bravo event is switched to app-only the same day Chekkit starts for that store; the day's plan refuses to run for a store whose Bravo event is still set to text.

## Win-back texts — result so far (computed 2026-11-18 4:00 PM from Email Refinement/forfeiture_winback/runs)
Audience = customers who forfeited a loan in the last 2 years and have not been back (not "inactive 6 months").
Texted 9/29-11/8: 1,934 people, 2,017 texts (1,692 in the first send 9/29; 20-80 new forfeiters a week since). No longer on the not-back list at the 11/15 run: 112 = 5.8% (CUL 30/403 7.4%, WAY 29/371 7.8%, ROA 30/528 5.7%, HAR 16/415 3.9%, LEX 7/217 3.2%). A handful of the 112 may have left the list by ageing past 2 years rather than visiting. No untexted comparison group exists, so the share who would have returned anyway is unknown. Cost at $0.03 = about $60, about $0.54 per returning customer.
Correction: win-back is NOT a large ongoing user of the Chekkit allowance (one-time 1,692, then under 100 a week across all stores).
Joshua 3:52 PM: no email to Chekkit about pooling; work within the 2,000 per store; do not cut outreach; measure what works; go faster.

## Win-back texts — before/after (2026-11-18 4:25 PM; analysis/winback_before_after.py, Bravo exports on disk)
Joshua: "can't you measure a time period before the win-back texts and compare?" Yes.
A. Same-age comparison (people 49-107 days past their forfeit): BEFORE texts (forfeited 6/14-8/11, checked 9/29) 103 of 360 back = 28.6%. AFTER texts began (forfeited 7/31-9/27, checked 11/15) 90 of 326 back = 27.6%. By store before -> after: CUL 34.4 -> 28.1, HAR 39.1 -> 28.8, LEX 21.4 -> 37.1, ROA 15.0 -> 18.3, WAY 36.1 -> 33.3 (store samples are small).
B. The 1,716 not back on 9/29: 78 came in by 11/15 (4.5%, verified against Bravo visit dates). The return pattern from before any text predicts about 72 (4.2%).
Read: no measurable lift from the win-back texts in the first 7 weeks. Win-back emails were already running from 7/31, so this measures texts on top of email. (The 4:00 PM "112 = 5.8%" counted everyone who left the list; 78 is the verified-visit count.)

## 2026-11-18 5:30 PM — Joshua: "ok lets proceed" (all texting moves to Chekkit; Bravo keeps app notices)
Awaiting his approval: layaway wording (due / past due) and adding "Reply STOP to opt out" to the birthday and anniversary texts.
DRAFT layaway due: "Valley Pawn {store}: your layaway payment is due {due}. Pay in store or in the MobilePawn app: thevalleypawn.com/app Reply STOP to opt out."
DRAFT layaway past due: "Valley Pawn {store}: your layaway payment is past due. Call or text us here, or pay in the MobilePawn app: thevalleypawn.com/app Reply STOP to opt out."
Order: tonight list pull + effectiveness read -> 7-day no-send plan vs Bravo's count -> test Bravo app-only setting at Culpeper -> Culpeper live (ask first) -> other four.

## Overnight job 1 — 2026-11-18 8:15-8:35 PM (scheduled follow-up; nothing sent, Bravo not touched)
- Open-loan pull NOT run. Why it was paused (10/8): the only existing open-loan pull needs 36-40 date windows per store and ran for hours, colliding with the 8:43 PM jewelry count and the morning reports. The switch (pm_loan_growth.PAUSED) was left in place.
- No-send dry plan run instead on data already on disk (analysis/dry_plan_oct.py): open-loan book from 10/7 (3,267 open loans) + customer phone directory from 9/29-9/30.
  - Loans matched to exactly one phone: 3,171 of 3,267 = 97.1% (85 names with two phones, 11 with none; those are skipped, never guessed).
  - Loans whose customer has no app: 1,157 (CUL 227, HAR 278, LEX 118, ROA 312, WAY 222).
  - Estimated loan texts a month to no-app customers (1 day before due, 1 day after, then Fridays): CUL 281, HAR 397, LEX 181, ROA 376, WAY 229 = about 1,460. Layaway, birthday and anniversary texts not yet counted.
- Needed for the daily list: ONE new saved report in Bravo — open loans with a Due Date range (run nightly for due dates 10 days back to 6 days ahead). It is small and takes about a minute per store, instead of 36+ windows. Saving a new report adds to Bravo and changes nothing existing, but it is a Bravo change, so it waits for Joshua's OK. Same for layaways (next due date) and a birthday/first-visit customer list.

## Overnight job 2 — what Chekkit sends and what gets a response (2026-11-18 9:25 PM; bin/chekkit_send_effect.py, GET only; fleet/state/chekkit_send_effect.json; Aug 1 - Nov 18)
"event_other" rows are NOT texts: they are Chekkit log lines ("scheduled message for <date>", "<staff> closed/assigned this conversation"). They do not use the allowance.
Texts sent per store per month (staff + automated + campaigns; inbound and log lines excluded):
| Store | Aug | Sep | Oct |
|---|---|---|---|
| CUL | 1,270 | 1,440 | 818 |
| WAY | 1,512 | 1,429 | 718 |
| HAR | 1,132 | 1,231 | 868 |
| LEX | 1,013 | 977 | 437 |
| ROA | 1,201 | 1,229 | 2,101 |
These are message counts. Chekkit's own meter runs higher (Harrisonburg got a 2,000-limit email on 9/7 with about 1,200 messages counted), most likely because a long text counts as more than one. The meter in each Chekkit account is the number to trust; not yet read.
Staff-sent texts fell sharply in October at four stores (WAY 1,236 -> 218, HAR 1,048 -> 196, LEX 886 -> 98, ROA 1,112 -> 106). Cause not established.
Response within 72 hours, all stores, Aug 1 - Nov 18:
| Send | Sent | Customer wrote back | Opted out (STOP) |
|---|---|---|---|
| Missed-call text | 659 | 163 = 24.7% | 15 = 2.3% |
| AI reply | 263 | 188 = 71% | - |
| Staff texts | 10,258 | 1,828 = 17.8% | 41 |
| Review invite | 1,480 | 52 = 3.5% | 21 = 1.4% |
| Win-back | 1,831 | 53 = 2.9% | 40 = 2.2% |
| Culpeper "buys gold and silver" campaign | 2,373 | 69 = 2.9% | 12 = 0.5% |
| Roanoke October campaign | 1,093 | 46 = 4.2% | 7 = 0.6% |
Already scheduled in Chekkit for December: about 4,800 texts (CUL 1,140, WAY 1,047, HAR 928, LEX 793, ROA 1,036). Which campaign this is has not been identified.
Budget read: in a normal month loan reminders (180-400 a store) fit under 2,000 everywhere. December is tight because of the 800-1,140 already scheduled per store.
