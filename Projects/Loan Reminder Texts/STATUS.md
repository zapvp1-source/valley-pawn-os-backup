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

## Chekkit evaluation + redundancy check — 2026-11-19 8:30 AM (bin/chekkit_overlap_read.py, GET only, Sept 1 - Nov 19; fleet/state/chekkit_overlap_read.json)
CORRECTION to 11/18 9:25 PM: staff texting did NOT drop in October. The September "staff" numbers were the gold-and-silver blast sent under staff names. Real staff texts are 75-210 a store a month.
How the 2,000 limit is really used: Chekkit counts PARTS (a text over 160 characters counts as 2 or more). Estimated parts: Sept CUL 2,629 / WAY 2,567 / HAR 2,232 / LEX 1,886 / ROA 2,291; Oct 1,535 / 1,294 / 1,533 / 824 / 4,083. Sept excess over 2,000 = 1,719 parts x $0.03 = $52, in line with the overage actually billed.
What is sent (messages): gold-and-silver blast about 4,900 in Sept (about 1,000 a store), and about 4,945 more already scheduled for December; Roanoke "open Wednesdays" 1,032 (Oct); win-back 1,764 (Oct) then under 100 a week; review invites 35-105 a store a month (Roanoke 381 in Oct); missed-call texts 50-95 a store a month; staff 75-210.
Everyday load without blasts (Nov 1-19): 275-625 parts a store. Loan reminders (180-400 single-part texts) fit with room to spare. The blasts are what use the allowance.
Redundant or wasteful:
1. Two review requests to the same customer within 7 days: 222 customers (Culpeper 107, Harrisonburg 115) got both "thanks for choosing ... leave us a quick review" and "thanks again for visiting ... 30 seconds to leave a review". 56 of the Harrisonburg second texts say "Dixie Pawn Inc."
2. Gold: Bravo's recurring "We Buy Gold" app message (Waynesboro) and the Chekkit gold-and-silver blast cover the same ask.
3. Roanoke October: 58 customers got the "open Wednesdays" text and a win-back text within 7 days.
4. Three different automatic "we got your message" replies plus the AI reply plus the missed-call text. Waynesboro versions sent since Sept still list the old hours (closed Wednesday) in at least 20 texts.
5. Long wording: gold blast, review invite and win-back each count as 2 parts. Under 160 characters they would count as 1.
6. Undeliverable: 190 of 4,160 tracked texts failed (landline 57, unknown number 89, unreachable 43).
Not a problem: over-texting. In the last 30 days almost nobody got more than 2 automated texts.
Sending tool confirmed: reminders can go out through Chekkit's API (POST /v1/messages), the same proven path the win-back and review-invite agents use.

## 2026-11-19 10:10-11:00 AM — Joshua: "Lets do it all" (the five fixes). Done in the Chekkit dashboard (signed in as Joshua, owner, all 5 locations in the switcher)
1. Review reminder ("drip campaign": a second review text 3 days after the invite to anyone who has not reviewed) — SWITCHED OFF at Culpeper and Harrisonburg (both showed "enabled"; now "Drip campaign disabled", saved with Chekkit's success notice). Already off at Lexington and Waynesboro. Roanoke not opened (no double-ask pairs in its data). Reviews per 100 invites 2026: CUL 23, HAR 24 (reminder on) vs WAY 27, LEX 32 (off), so no sign the reminder helped. The Harrisonburg "Dixie Pawn Inc." wording had already been corrected in the template.
3. Automatic replies — NO CHANGE NEEDED. Each store has one "we got your text" reply and one closed-hours reply. Hours verified correct at Culpeper, Waynesboro (Mon-Fri 10-6, Sat 10-5) and Lexington (closed Wed and Sun). The stale-hours and older wordings in the data were sent before the hours were updated.
NOT done yet:
2. Shorter wording. Harrisonburg's December gold text is 161 characters, one over the limit (929 customers, counts double). Other stores' lengths not yet read. Editing a scheduled campaign means re-confirming its schedule, so it waits for Joshua's OK on the exact text. Win-back text (in our own code) is about 190 characters.
4. Failed-number suppression: not built.
5. Gold in one place: Bravo's Waynesboro "We Buy Gold" app message still on (Bravo screen stalled twice on 11/18; not touched).
Also seen: the December gold list is an old 2023-24 list (Harrisonburg 929) that includes placeholder numbers (555 555 5555, 0000 000 000) and Joshua's own number. Chekkit meters this period (Nov 10-Dec 10): Lexington 68 / 2,000, Waynesboro 210 / 2,000. A sixth location, "Tax Experts" (Petersburg), exists in the same Chekkit login.

## 2026-11-19 11:00 AM-12:10 PM — rest of the Chekkit read (no changes made in this block)
- Roanoke: review reminder already off. So it is now off at all five stores.
- Auto-replies: Roanoke and Harrisonburg have all three (reply, closed-hours reply, missed-call) switched OFF; Culpeper, Lexington, Waynesboro have them on. Not changed.
- Meters today: CUL 101, HAR 157, LEX 68, WAY 210 of 2,000 (Nov 10-Dec 10); ROA 223 of 2,000 (Oct 27-Nov 27).
- December 1 gold text length (read in each campaign editor, nothing saved): CUL 159, WAY 158, HAR 161, LEX 180, ROA 179. List sizes 1,140 / 1,049 / 929 / 793 / 1,036. As written it counts 7,704; with HAR, LEX, ROA under 160 it counts 4,947.
- Chekkit campaign editor requires the exact words "Text STOP to unsubscribe".
- New read-only script bin/chekkit_len_failed_read.py (host queue, GET only) -> fleet/state/chekkit_len_failed.json and fleet/state/chekkit_failed/<STORE>.txt. Since Sept 1: EVERY review invite (1,048; 169-209 characters, the link is 37-39) and EVERY win-back text (1,851; 215-270) went out over 160, so each counted double. Numbers whose last text failed with a carrier dead/landline code and who never replied: CUL 17, HAR 22, LEX 47, ROA 44, WAY 28 = 158.
- Lexington has an unsent draft campaign "Shop Online 2026-10" (605 customers). Left alone.
Proposed wording (waiting on Joshua's OK, then: edit the 3 gold campaigns + remove the 158 failed numbers and placeholder numbers from the gold lists, edit the review invite text at 5 stores, change MSG in winback_texts.py):
- Gold HAR (154): Valley Pawn Harrisonburg buys gold and silver - jewelry, scrap and bullion. Text us back for a quote or come by 1790 E Market St. Text STOP to unsubscribe
- Gold LEX (158): Valley Pawn Lexington buys gold and silver - jewelry, scrap, bullion. Text us for a quote or come by 125 Walker St by Dollar General. Text STOP to unsubscribe
- Gold ROA (156): Valley Pawn Roanoke buys gold and silver - jewelry, scrap, bullion. Text us for a quote or come by 2362 Peters Creek Rd by Dominos. Text STOP to unsubscribe
- Review invite (<=159 with a 12-letter name): Hi ((first_name)), thanks for choosing Valley Pawn <Town>! Mind leaving us a quick review? ((review_invitation))
- Win-back (153-158): Valley Pawn <Town>: need cash? No credit check. Bring in anything of value - gold & silver get the most. Stop by or text us here. Reply STOP to opt out.

## 2026-11-19 12:15-1:10 PM — Joshua: "go" + "find out why the auto replies are not consistent"
- Auto-replies ARE consistent: Chekkit's Automatic Reply, Out of Office Reply and Missed Call Message are unchecked at all five stores (re-read each store's Auto-Reply & Media page today). My earlier note that CUL/LEX/WAY had them on was wrong. They were switched off on 10/1 on Joshua's instruction so the in-house AI responder (com.valleypawn.chekkit-ai-responder, live since 9/30) is the only automatic reply; keyword Smart Replies deleted 10/1. AI responder last 7 days: 5-15 replies a day, healthy.
- DONE win-back wording: bin/winback_texts.py MSG -> "Valley Pawn {TOWN}: need cash? No credit check. Bring in anything of value - gold & silver get the most. Stop by or text us here. Reply STOP to opt out." (153-158 chars; backup fleet/_backups/winback_texts.py.bak-pre-short-20261119). The four read-only reporting scripts now recognise the new wording as win-back.
- DONE review invite wording at all 5 stores (Settings > Templates > "Review Invitation", the automated review template): "Hi ((first_name)), thanks for choosing Valley Pawn <Town>! Mind leaving us a quick review? ((review_invitation))" (113-118 chars before name and link). Saved and re-read at each store. Reminder template untouched (reminders are off).
- DONE dead numbers: 15 of 15 Roanoke failed numbers tested were NOT on the gold list (campaign sends are not delivery-tracked; the 158 came from win-back, review invites and missed-call texts). So the skip went into our own senders: bin/missed_call_text.py (backup fleet/_backups/missed_call_text.py.bak-pre-deadnumbers-20261119) and bin/winback_texts.py now skip any number in fleet/state/chekkit_failed/*.txt. List is a snapshot from today; rerun bin/chekkit_len_failed_read.py to refresh.
- NOT DONE gold wording at HAR/LEX/ROA: saving a campaign opens "Confirm Campaign Compliance" with three boxes (message identifies the business; I have consent from the recipients; opt-out included). Cancelled at Roanoke without saving; campaign re-checked: still Scheduled Dec 1 1:13 PM, 1,036 customers, old text. Needs Joshua's OK to tick those for him, or he saves it himself. Roanoke gold list also holds two placeholder numbers (000 000 0000, 555 555 5555 "Scrap") to remove in the same save.
- Review invite template has "Include review invitation link and image" on at every store.

## 2026-11-19 11:10-11:30 AM — Joshua: "go" + "we have permission to text people"
- Gold campaigns saved with shorter wording, compliance boxes ticked on Joshua's confirmation, schedule unchanged, all still "Scheduled":
  - Roanoke "Reoccurring Gold" Dec 1 1:13 PM, 156 chars, placeholders 000 000 0000 + 555 555 5555 removed, Chekkit skipped 10 invalid -> 1,024 recipients.
  - Lexington "Reoccurring Gold" Dec 1 1:56 PM, 158 chars, placeholder 540 555 5555 removed -> 793.
  - Harrisonburg "We By Gold Ongoing" Dec 1 1:47 PM, 154 chars, placeholders 0000 000 000 + 555 555 5555 removed, Chekkit skipped 2 invalid -> 925.
- All five December gold texts are now under 160 (CUL 159, WAY 158). Dec 1 counts about 4,940 instead of 7,704.
- Each campaign is "One time" (the name says recurring, the setting does not). Joshua's own number is on the HAR list (his check copy) - left.

## 2026-11-19 11:15 AM-12:05 PM — Joshua: "change it and make sure they are all off at all stores ... look at the mobile pawn push notifications and make sure they are consistent"
- NEW `Bravo Data Extraction/MobileEventsGoldOff.ahk` + `_run_mobileevents_goldoff.ps1` + `Valley Pawn OS/bin/mobile_events_gold_off.sh` (allow-listed). Only clears the enabled box on events whose title contains "gold", presses Ok only if it changed something, then re-reads the screen.
- Waynesboro "We Buy Gold" recurring app message: TURNED OFF 11:18 AM, saved, re-read: off. Roanoke one-time "Gold" message was already off. CUL, HAR, LEX have no gold event. Verified on fresh reads at all five: 0 gold events on.
- App (MobilePawn) push notifications: identical at all five stores (same 15 events, all on, same delivery setting each).
- Differences that remain, all in the regular reminder/text events (not the app pushes):
  - Harrisonburg sends Birthday, Store Anniversary, Loan Courtesy Reminder, Layaway Notice and Loan Past Due on a text-only setting (NTFSMS); the other stores use NTFAUT.
  - Roanoke has no Loan Courtesy Reminder, Layaway Notice or Loan Past Due event.
  - Culpeper's birthday wording has a typo: "15% OFF the in the next 30 days!" (others: "15% OFF during the next 30 days.").
- Channel drop-down choices could not be read (no expand pattern); meanings of NTFAUT/NTFREE/NTFIPN/NTFSMS still inferred.

## 2026-11-19 12:42-1:15 PM — Joshua: "we should make these all consistent across all 5"
- Bravo delivery choices (read from the drop-down at Roanoke): AUTO, SMS, MobilePawn.
- Harrisonburg: Birthday, Store Anniversary, Loan Courtesy Reminder, Layaway Notice, Loan Past Due changed SMS -> AUTO (same as the other four), saved 1:07 PM, re-read: no SMS settings left.
- Culpeper birthday wording fixed to "...15% OFF during the next 30 days." (same as the others), saved 1:11 PM, re-read.
- Fresh reads at all five: every event, setting and wording now matches, except Roanoke has no Loan Courtesy Reminder, Layaway Notice or Loan Past Due. "Add new event" only adds custom messages (probe at Roanoke, nothing saved), so those three cannot be created on this screen. Roanoke gets loan and layaway reminders through the planned Chekkit reminders (Joshua 11/18: Roanoke gets the same reminders).
- Script: MobileEventsGoldOff.ahk modes off / align / probe (align = SMS->AUTO on the five standard events + Culpeper typo; checks every change before Ok, otherwise Cancel).

## 2026-11-19 2:00-2:35 PM — INCIDENT: customers think they have a loan (#general 11:26 AM, Walker HAR / Martin WAY)
- Cause: the monthly "Shop Us Online" Chekkit text (cloud scheduled task, pack 2026-11, wording built 10/24 under config app_sms_own=true) sent 11:13 AM to Waynesboro 1,166 + Harrisonburg 1,115: "Valley Pawn: pay your loan from your phone w/ our free app thevalleypawn.com/app/?utm_source=sms Shop online thevalleypawn.com/shop Text STOP to unsubscribe". CUL/LEX/ROA were held by the opt-out guard. Not caused by today's Bravo or Chekkit edits.
- Chekkit 30-day opt-out rate after the send (Settings > Compliance, 2:30 PM): Harrisonburg 8.16% (was 1.07% at 11:09 AM), Waynesboro 6.62% (was 0.55%). Carrier threshold 2%.
- Wording fixed in `eBay Customer Campaign/build_month.py` (backup fleet/_backups/build_month.py.bak-pre-loanwording-20261119): app-text now "Valley Pawn: shop all 5 stores online thevalleypawn.com/shop Have a loan or layaway with us? Pay by phone: thevalleypawn.com/app Text STOP to unsubscribe" (153). December and later packs on disk already carry shop wording, no "pay your loan" left.
- Exact opt-out count: read-only bin/chekkit_today_stops.py queued (slow: 60 requests/min) -> fleet/state/chekkit_today_stops.json.
- 11/19 3:18 PM: exact opt-outs after the 11:21 AM 'pay your loan' text (reply with stop/unsubscribe etc., counted from Chekkit conversations): Harrisonburg 41 of 1,115 (46 replied), Waynesboro 61 of 1,166 (77 replied) = 102. One HAR conversation unreadable. Earlier 150-200 estimate was too high.
- 11/19 7:15 PM: MobilePawn activation pull: Bravo's month-end report only runs through yesterday (it clamped 11/19 to 11/18), so today's activations cannot be read tonight. Baseline through 11/18 (Customers Active, YTD): WAY 282, HAR 353. Re-pull 11/20 9:15 AM for through-11/19 and compare.

## 2026-11-19 11:05 PM — Joshua: "dec 1 hold" + report may be built by background script, but the nightly info must come from an agent
- Gold campaigns HELD (rescheduled, same text and list, still "Scheduled"): Harrisonburg "We By Gold Ongoing" Dec 1 -> Jan 4, 2027 1:47 PM (925); Waynesboro "Gold Boro" Dec 1 -> Jan 4, 2027 12:01 PM (1,046). Culpeper, Lexington, Roanoke unchanged (Dec 1). Re-check WAY/HAR opt-out rate before Jan 4.
- Design rule from Joshua: the nightly reminder feed is a native agent (launchd + pipeline cell), never a chat session or screen control.

## 2026-11-20 8:20 AM — Joshua: Jan 4 good; add reply-stop to birthday text; "Chekkit already adds this"
- CONFIRMED from yesterday's sends: Chekkit appends " Text STOP to unsubscribe" to some outgoing texts that lack that exact phrase (missed-call: 4 of 9 got "...Reply STOP to opt out. Text STOP to unsubscribe"; review invites 159 of 172 at CUL; win-back too). Not every text gets it (likely first contact / periodic).
- Win-back wording now ends with the exact phrase "Text STOP to unsubscribe" (155-160 chars) so nothing is doubled.
- Rule for every Chekkit text we write (loan/layaway reminders, birthday, anniversary): end with exactly "Text STOP to unsubscribe" and count it inside the 160. reminder_core.py wording still says "Reply STOP to opt out." -> change before the trial.
- Birthday/anniversary: opt-out line goes into the Chekkit version at cutover. Not added in Bravo: it pushes the Bravo text past 160 (2 x $0.07).
- Missed-call text wording (fleet/missed_call_text_config.json) still has "Reply STOP to opt out." and sometimes gets the Chekkit line appended as well. Not changed.
- "hold the oin text also": unclear which text; asked Joshua.
- 11/20 9:25 AM: MobilePawn after the 11/19 text (Bravo month-end report, YTD through 11/18 vs 11/19): active app customers WAY 282 -> 283, HAR 353 -> 353; app loan payments on 11/19: WAY 12 (YTD avg ~6/day), HAR 8 (avg ~8/day). Cost: 102 opt-outs. 'Customers Active' may count only customers who have used the app, so installs without a payment may not show.

## 2026-11-20 7:10-8:10 PM — Bravo list for the reminders BUILT and tested (Joshua "yes" 11/19; background script, no screen control)
- NEW saved report in Bravo: **Claude Loan Reminders** (Loans/Buys > Custom Reports). Ticket Kind = LOAN, Due Date range, layout FDP, Shared Company-Wide. Saved 7:44 PM at Culpeper. Nothing existing was loaded, changed or deleted.
- Built by `MobileEventsGoldOff.ahk` modes crprobe (look only) / crdry (everything except Save, leaves by Cancel) / crbuild (Save only if every check passes; refuses if the name already exists). Backups .bak-pre-crprobe-20261120, .bak-pre-crbuild-20261120.
- Lessons: first list-open after a Tab does nothing (read it twice); a date set by value is text and Save rejects it (red X) - click the box and type, Bravo then holds a real date (it kept today's date; the runner overrides both dates each run anyway).
- NEW pipeline cell `loan-reminders` (`reports/LoanReminders.ahk`, two added lines in bravo_watcher.ahk, backup .bak-pre-loanreminders-20261120, validated + watcher restarted 8:01 PM). Token = a day -> due dates 45 days back to 6 days ahead -> `output/<day>_<STORE>_loan-reminders.csv`. Read only.
- Test 8:01-8:09 PM: CUL 1,085 rows, 533 tickets, 271 on loan (182 past due), due dates 10/6-11/26 exactly as asked, 214 of the 271 have the app activated. HAR 705 rows, 495 tickets, 277 on loan (210 app activated). Harrisonburg seeing the report proves it is shared to all stores. Columns: Ticket Number, Disposition, Due Date, Customer, MobilePawn, SMS, Last Payment.
- reminder_core.py: both loan texts now end "Text STOP to unsubscribe" (backup fleet/_backups/reminder_core.py.bak-pre-stopline-20261120). Ticket numbers print digits only (#4017707); when several tickets would push past 160 it says "your 3 loans". Longest text on real Culpeper data: 152. 11 tests pass. Still no send function.
- NOT built yet: phone numbers for these customers (existing ChekkitInvitesRange handler has phones), Chekkit opt-out list feed, the nightly native agent (launchd, after close, no-send for 7 days), layaway and birthday lists.

## 2026-11-21 8:34 AM — Joshua: hold the weekly win-back; layaway wording good
- Weekly win-back text HELD: hold file `Valley Pawn OS/fleet/state/winback_texts.HOLD` + check at the top of bin/winback_texts.py (backup fleet/_backups/winback_texts.py.bak-pre-hold-20261121). Nothing sends or posts while the file exists; delete it to resume. Next run would have been Thu 11/26 10:33 AM.
- Layaway wording approved and added to reminder_core.py TEMPLATES (layaway_notice / layaway_late), up to 161 chars with a long first name at Harrisonburg - the builder drops the name when a text would pass 160.

## 2026-11-21 9:50 AM-12:00 PM — Joshua "ok lets go": nightly NO-SEND agent built, installed, first run clean
- NEW native agent `com.valleypawn.loan-reminders` (fleet plist, installed via install_agent.sh), 11:15 PM daily -> `Valley Pawn OS/bin/loan_reminders_nightly.sh`: (1) Bravo cell loan-reminders, all 5 stores, retries only the stores that failed, up to 3 passes; (2) `bin/chekkit_optouts_sync.py --days 3` (GET only) -> fleet/state/chekkit_optouts/<STORE>.tsv; (3) `Loan Reminder Texts/loan_reminders_plan.py` (offline, no send function) -> trial/<send date>/plan_<STORE>.csv, skipped_<STORE>.csv, summary.json, trial/SUMMARY.csv, trial/ledger_<STORE>.txt. One-time 120-day opt-out backfill runs after tonight's plan. Both scripts allow-listed. Silent: files + agent log only.
- Phones: from the weekly Bravo customer exports already on disk (forfeiture-winback-comparison-contacts + chekkit-invites-range), newest export per name. Chekkit opt-outs and dead numbers removed. Customers with MobilePawn "Activated" are left to Bravo's app notice.
- First run 10:11-11:06 AM (store hours; Harrisonburg login failed on pass 1, came through on pass 2). Plan for Sun 11/22: CUL 26 reminders due / 17 app / 9 texts; HAR 22 / 18 / 4; LEX 20 / 12 / 6; ROA 30 / 14 / 15; WAY 24 / 13 / 11. Longest text 156. Nothing skipped for a missing phone.
- Friday 11/27 projection from today's lists (past-due repeat day): CUL 54, HAR 60, LEX 47, ROA 128, WAY 76 texts (1 no phone at HAR, 1 Chekkit opt-out at LEX). Without the app split it would be 167-303 a store.
- Chekkit opt-outs known after 3 days read: CUL 0, HAR 52, LEX 6, ROA 2, WAY 74.
- Open: the list is pulled the night before; a loan paid between 11:15 PM and 10 AM would still get its text. Decide at cutover whether to add a 9:30 AM re-pull. Layaway and birthday lists not built. Trial ends after the Sat 11/28 plan (7 nights).

## 2026-11-21 12:09 PM — Joshua: design it so nobody can get a reminder after paying
- RULE (in loan_reminders_plan.py `send_window_ok`, to be enforced by the sender): list pulled after all stores close (6 PM; 11:15 PM agent), texts go out 9:15 AM, before stores open at 10. No store is open in between, so nothing on the list can have been paid at a counter or by phone. App payers are never on the text side. If the night pull is missing or late for a store, that store sends nothing that day (never a stale or late send). No morning re-pull needed (my earlier idea dropped).
- Today's daytime test list correctly reads "not allowed to send" (pulled before close).

## 2026-11-21 2:35 PM — Joshua: fix texting first, fleet improvements after
- Layaway reminders added to the same nightly no-send agent: pulls cell `layaway-detail` (all 5 stores, two triggers), plans with Bravo's schedule (5 and 1 days before next due; every 5 days while late), approved wording, first name only, name dropped if the text would pass 160. One text per customer per kind. App-activated customers left to Bravo. Offline test on the 10/21 Harrisonburg list: 1-4 texts a day, longest 158.
- Agent moved 11:15 PM -> 10:40 PM (loans ~25 min, layaways up to ~65 min, done before the 12:45 AM daily GL). Reinstalled.
- Still to build for texting: birthday + store-anniversary list (no Bravo list yet), the sender (must call send_window_ok; off until Joshua's go), cutover step in Bravo (reminders AUTO -> MobilePawn only).
- 2:55 PM: SENDER built and installed, OFF: `com.valleypawn.loan-reminders-send` 9:15 AM daily -> bin/loan_reminders_send.sh -> loan_reminders_send.py. A store sends only with a LIVE file (fleet/state/loan_reminders_live/<STORE>, none exist), last night's plan, send_window_ok (list pulled after close, before 9:45 AM), every text <=160, plan <=250. Otherwise nothing is sent that day. Dry run today: CUL/HAR "HELD (past 9:45 AM)", others "no plan" - correct. Cutover for a store = create its LIVE file + switch that store's Bravo loan/layaway events AUTO -> MobilePawn. Needs Joshua's go.
- Plan rows now carry the customer name (Chekkit contact name). trial/SUMMARY.csv has repeat rows for 11/22 from test re-runs: use the last row per date/store.

## 2026-11-21 3:14 PM — Joshua: OK on birthday/anniversary; "lets do the culpeper cut over"
- CUTOVER PLAN (Culpeper): Sun 11/22 night, after the 10:40 PM run finishes and the 11/23 plan checks out -> Bravo CUL: Loan Courtesy Reminder, Layaway Notice, Loan Past Due switched AUTO -> MobilePawn (new script mode `apponly`, one store per run, Ok only if all three change; `appauto` reverses) -> then create fleet/state/loan_reminders_live/CUL. First live Chekkit send Mon 11/23 9:15 AM. If the plan is not ready at 11:59 PM, wait for it (layaway pulls can run past midnight); stay clear of the 12:45 AM daily GL.
- Other four stores: Mon 11/30 after five clean Culpeper days. Birthday/anniversary: target Mon 12/7 (needs a new Bravo list). Bravo's app-invite/onboarding messages are not part of this move.
- Layaway text schedule corrected after re-reading Bravo's screen: Bravo TEXTS only 1 day before (its 5-day notice is app-only). Chekkit: 1 day before; past due 1 day after, then Fridays, 30 days max. Tests updated (11 pass).
- Nightly agent: second run 4:40 AM = catch-up (re-pulls only stores missing from last night, still after close/before open, rebuilds today's plan).
- Tonight 7:42 PM: no-op test of `apponly` at Roanoke (has none of the three events) + read-only look for birthday criteria.

## 2026-11-21 3:19 PM — Joshua: speed it up, every day on Bravo costs money -> ACCELERATED SCHEDULE (supersedes the 3:14 PM plan)
- Culpeper: switch tonight after the 10:40 PM run (trigger 12:20 AM Sun), first live send Sun 11/22 9:15 AM, verify 9:50 AM.
- Harrisonburg, Lexington, Waynesboro, Roanoke: switch Mon 11/23 night (trigger 12:20 AM Tue) if Culpeper's Sun + Mon sends were clean; first live send Tue 11/24 9:15 AM; verify 9:50 AM.
- Older triggers (Sun 11:59 PM cutover, Mon 9:50 AM verify, Sat 11/28 trial review) still fire: treat them as re-checks of what is already live.
- Birthday/anniversary: build the Bravo list this week; target moved up to as soon as it is proven (was 12/7).
- Cost context: Bravo billed 4,439 texts in Sept and 4,693 in Oct at $0.07 = about $310-330 a month, about $10-11 a day for all five stores and all text types.

## 2026-11-21 7:42-7:52 PM — cutover prep checks
- `apponly` no-op at Roanoke: PASS ("changed=0 already=0 failed=0 notfound=3 | nothing saved"), script loads and exits clean. Culpeper switch stays scheduled for ~12:20 AM.
- Customers > Custom Reports criteria read at Culpeper (look only, new mode crprobecust): includes **Birthday**, **First Time In**, Mobile, MobilePawn Activation Date, Last Time In, Store. A birthday / store-anniversary list can be built the same way as "Claude Loan Reminders". Not built yet: need the Birthday operator choices (dry run) - scheduled for Sunday afternoon (stores closed).

## 2026-11-22 12:20-12:30 AM — CULPEPER CUT OVER
- 10:40 PM run clean, done 11:49 PM: loan + layaway lists for all 5 stores (first layaway pull at all five: CUL 113 active, HAR 81, LEX 41, ROA 65, WAY 50), all lists pulled after close, every text <=160.
- Bravo Culpeper 12:23 AM: Loan Courtesy Reminder, Layaway Notice, Loan Past Due (Due Date) AUTO -> MobilePawn (NTFAUT -> NTFIPN), saved; re-read 12:24 AM: only those three changed, all 21 events otherwise identical.
- LIVE file created: fleet/state/loan_reminders_live/CUL. First live send 9:15 AM today: 8 texts planned (6 due-tomorrow, 2 past due), 17 more loans covered by the app notice.
- Roll back = delete the LIVE file + `mobile_events_gold_off.sh CUL appauto`.

## 2026-11-22 9:50 AM — Culpeper first live send verified
- 9:15:05-9:15:17 AM: 8 planned, 7 delivered to Chekkit (6 due-tomorrow, 1 past due), 1 refused by Chekkit ("Customer has opted out") - correct behavior; that number added to the Culpeper opt-out list and the sender now records such refusals automatically. No other store sent.

## 2026-11-22 2:30-4:45 PM — birthday / store-anniversary: what Bravo does and what data exists
- Bravo events (both AUTO): Birthday = on the birthday, "Happy Birthday, <name>! In celebration, show this message at any of our ValleyPawn locations to enjoy 15% OFF during the next 30 days."; Store Anniversary = yearly on the first-transaction date, "Happy Anniversary <name>! It's the anniversary of your first visit to ValleyPawn! Show this message at any of our locations to enjoy 15% OFF!"
- Customers > Custom Reports (look-only mode crcustdry at CUL): criteria Birthday (=, range, in, is empty, is not empty) and First Time In; saved reports "Birthday Range" and "Customers First Time In" exist; layouts Demographics Report (Name + Birthday), Customers First Time In (Name + First Time In), Customer Address Check (Name + Phone + MobilePawn + SMS).
- No new saved report needed. On disk already (weekly win-back job): per-store full contacts (phones) and visits (First Time In) for customers seen in the last 760 days (~3,400 a store; about 7 anniversaries a day a store before filters).
- NEW bin/birthday_list_pull.sh (allow-listed, read only): "Claude Forfeiture Winback Comparison" + layout Demographics Report -> output/<D>_<STORE>_forfeiture-winback-comparison-birthdays.csv, reused for 60 days. First CUL pull died at 2:41 PM, 23% through the grid (the Mac/bridge dropped at the same minute). Re-run after the Sunday 4:30 PM monday-pull finishes.

## 2026-11-22 7:50 PM — birthday / anniversary planner built (NOT sending)
- loan_reminders_plan.plan_occasions + reminder_core TEMPLATES birthday/anniversary (not yet approved by Joshua). Output: trial/<date>/occasions_<STORE>.csv, which the sender does not read. Marketing rule applied: Bravo DNT + Chekkit opt-outs + dead numbers excluded; app-activated left to Bravo's app notice; one per customer per kind per year.
- Bravo shows birthdays as "August 9" (no year). Birthday lists pulled 7-7:45 PM: CUL 3,473 customers (3,103 with a birthday), HAR 3,333 (3,184), LEX 2,143 (1,988); ROA and WAY still pulling (pulls took 7-25 min a store; LEX needed a second pass). A stale claimed trigger from the 2:41 PM cut-off had blocked the queue; moved to triggers/claimed/aborted-stale-2026-11-22.
- Next 30 days: CUL 153 birthday + 174 anniversary; HAR 149 + 109; LEX 82 + 103. Longest text 159.

## 2026-11-22 8:35 PM — birthday / anniversary lists complete for all 5 stores (still NOT sending; waiting on Joshua)
- Birthday lists pulled for all five by 8:12 PM (reused for 60 days; bin/birthday_list_pull.sh).
- Next 30 days, birthday + anniversary texts: CUL 153 + 174, HAR 149 + 109, LEX 82 + 103, ROA 156 + 129, WAY 146 + 148. Longest 159.
- Left out over the 30 days (all five): app customers 451 (Bravo app notice), store-marked do-not-text 366, Chekkit opt-outs 22, no phone 27, dead numbers 4.
- Decisions for Joshua: wording OK; scope = customers seen in the last ~2 years (Bravo: everyone ever).
- To build once approved: move occasions into the sender's plan, add the birthday list pull to a monthly slot, switch Bravo Birthday + Store Anniversary events to app-only per store at go-live.
- 11/22 11:59 PM re-check (old trigger): second nightly run clean at all 5 stores, done 11:24 PM. Culpeper already live; plan for Mon 11/23: CUL 3 texts (past due), others planned but not live (HAR 4, LEX 2, ROA 13, WAY 4).
- 11/23 9:50 AM: Culpeper day 2 (first weekday): 3 planned, 3 delivered (all past due), 0 rejected, 9:15:06 AM. No other store sent. Other four switch tonight (~12:20 AM) for Tue 11/24 if nothing changes (supersedes the 11/30 date in the old trigger text).

## 2026-11-24 12:20-12:35 AM — ALL FIVE STORES CUT OVER (loan + layaway reminders)
- Preconditions met: Culpeper live sends clean Sun 11/22 (7 sent, 1 opted-out refusal) and Mon 11/23 (3/3); Slack searched (read only) for complaints since 11/21: none. Nightly run 11/23 clean, done 11:25 PM, all lists after close, every text <=160.
- Bravo, saved and re-read (only these three events changed at each store, AUTO -> MobilePawn): Harrisonburg 12:24 AM, Waynesboro 12:29 AM, Lexington 12:32 AM (first Lexington pass changed 2 of 3 so it saved nothing; second pass clean). Roanoke has no such events.
- LIVE files: CUL, HAR, LEX, ROA, WAY. First all-store send Tue 11/24 9:15 AM: CUL 5, HAR 5, LEX 6, ROA 21 (incl. 1 layaway past due), WAY 2 = 39 texts.
- Bravo text events still on at all stores: Birthday, Store Anniversary (AUTO), app invites/onboarding.
- 11/24 9:50 AM: first all-store live send verified: CUL 5/5, HAR 5/5, LEX 6/6, ROA 21/21, WAY 2/2 = 39 sent, 0 rejected, 9:15:05-9:16:08 AM.

## 2026-11-24 12:17 PM — Joshua: birthday/anniversary wording OK; customers of the past two years only
- Templates marked approved. Scope = customers seen in the last ~760 days (what the exports hold).
- Planner: a store's birthday/anniversary texts join the sendable plan only when fleet/state/loan_reminders_live/<STORE>.occasions exists. CUL.occasions created (first send Wed 11/25). Test plan for 11/25: CUL 5 birthday + 1 anniversary on top of 4 reminders.
- Bravo script: modes apponlyocc / appautoocc (Birthday + Store Anniversary -> app-only / back to AUTO), one store per run. Culpeper switch scheduled 12:20 AM Wed; other four Thu 11/26 if Culpeper is clean.
- NEW agent com.valleypawn.birthday-list, Sundays 2:40 PM: weekly refresh of the birthday lists (bin/birthday_list_pull.sh, reuse window now 6 days). Phones and first-visit dates keep coming from the Sunday 12:30 PM win-back job.

## 2026-11-24 12:21 PM — Joshua: hold the other four stores' birthday texts to Friday; NO communications on Thanksgiving (Thu 11/26)
- NO-SEND DAYS: fleet/state/loan_reminders_no_send_dates.txt (2026-11-26). The sender sends nothing at any store on a listed day. Planner: the "due tomorrow" loan notice that would have gone on the holiday goes out the day before; birthdays/anniversaries that fall on the holiday go out the day after; past-due texts are simply not sent that day (Friday repeats them anyway).
- Revised birthday/anniversary dates: Culpeper Wed 11/25 (unchanged). HAR/LEX/ROA/WAY: Bravo events switch to app-only Wed night (so Bravo sends no birthday texts on Thanksgiving either), Chekkit flags created Wed, first Chekkit birthday/anniversary texts Fri 11/27 (covering Thursday's). The Thu 9:50 AM check must confirm NOTHING was sent Thursday (no sent_*.csv in trial/2026-11-26).
- Other Thursday sends found (read only): Brevo email #65 "Thanksgiving and Small Business Saturday" queued Thu 11/26 10:00 AM (bin/brevo_scheduled_list.py -> fleet/state/brevo_scheduled.json). NOT changed - asked Joshua. Win-back text (Thu 10:33) already held. Still automatic on Thursday: missed-call reply text, AI replies to inbound texts, Bravo app notices.

## 2026-11-25 12:20 AM — Culpeper birthday / anniversary cut over
- Nightly run clean (done 11:26 PM). Plan for Wed 11/25 at CUL: 13 texts = 6 due-soon loan notices (incl. 3 pulled forward for Friday's due dates because Thursday is a no-send day), 1 layaway notice, 5 birthday, 1 anniversary; longest 153.
- Bravo CUL 12:23 AM: Birthday + Store Anniversary AUTO -> MobilePawn (NTFIPN), saved, re-read: only those two changed. Culpeper now sends no Bravo texts except app invites.
- 11/25 9:50 AM: Wed sends verified: CUL 12 of 13 (5 birthday + 1 anniversary delivered; 1 loan notice refused, opted out), HAR 6/6, LEX 5/5, ROA 18/18, WAY 6 of 8 (1 refused opted out; 1 was a second due-notice to the same phone, sender keeps one per phone per kind per day). Flags HAR/LEX/ROA/WAY.occasions created; Bravo switch tonight 12:20 AM; no sends Thu; first four-store birthday texts Fri 11/27.

## 2026-11-26 12:20-12:31 AM — Bravo birthday / anniversary texts OFF at the last four stores
- HAR 12:22, LEX 12:24, ROA 12:27, WAY 12:29 AM: Birthday + Store Anniversary AUTO -> MobilePawn (NTFIPN), each saved first try; re-read: only those two changed per store.
- State now, all five stores: Bravo sends no loan, layaway, birthday or anniversary TEXTS (app notices only; app invites/onboarding unchanged). Chekkit sends them 9:15 AM daily. Thursday 11/26 is a no-send day; Friday 11/27 is the first four-store birthday send and the first big past-due day.
- Still open: Brevo email #65 queued Thu 11/26 10:00 AM - Joshua has not answered; not touched.

## 2026-11-27 9:50 AM — Thanksgiving silent; first big Friday verified
- Thu 11/26: no sent files, nothing went out from Chekkit's reminder sender.
- Fri 11/27 9:15:01-9:22:09 AM, delivered: CUL 41, HAR 56, LEX 32, ROA 85, WAY 45 = 259 (past due 191, due-soon 19, layaway 15, birthday 22, anniversary 12). Refused by Chekkit as opted out: 5 (CUL 2, LEX 1, ROA 2), now on the opt-out lists. Every text <=160. Slack (read only) since 11/25: no customer complaints.
- Finding + fix: the plan listed a customer's past-due loans as separate rows per due date and the sender kept one row per customer, so some customers' single text named only some of their loans. reminder_core.build_plan now puts all of a customer's past-due loans in one text (backup fleet/_backups/reminder_core.py.bak-pre-pastduegroup-20261127; 11 tests pass). trial/2026-11-27/plan_*.csv was regenerated with the new grouping after the send (sent_*.csv is the record of what went out).
- Sent since 11/22: CUL 68, HAR 67, LEX 43, ROA 124, WAY 53.

## 2026-11-27 4:31 PM — Joshua: run the maintenance texts for a week, count per store, then layer marketing back in; ALL texts off Bravo
- Marketing texts stay as they are (win-back held; gold Dec 1 at CUL/LEX/ROA and Jan 4 at HAR/WAY still scheduled - not changed) until the one-week count. Report scheduled Sat 12/5 10 AM (7 days 11/28-12/4).
- Bravo re-read (11/25 captures): three events are still on AUTO at every store - MobilePawn Layaway Notice (5 days before), MobilePawn Loan Past Due Notice (1 day after), MobilePawn Layaway Late Notice (every 5 days). AUTO can text customers without the app. Correction to 11/21: the 5-day layaway notice was NOT app-only. New script mode `noauto` (every AUTO/SMS event -> MobilePawn, one store per run); scheduled 12:20 AM Sat 11/28 for all five. Chekkit layaway schedule now includes the 5-day notice again (tests pass).
- Seven events are on NTFREE, including new-loan / new-layaway app invitations "to all non-activated customers". Whether Bravo bills those as $0.07 texts is unconfirmed; proof = next Bravo invoice or a message-usage report.

## 2026-11-27 4:45 PM — Joshua: are the remaining Bravo texts free? if not why can't we move them
- Bravo invoice INV2597398 (October, read from Gmail): only two metered message lines - "Digital Marketing: SMS 4,693 at $0.07 = $328.51" and "Digital Marketing: MobilePawn Messages 4,165 at $0.02 = $83.30". No free line and no per-event breakdown. So nothing on the invoice shows the NTFREE setting is free; an app message costs $0.02.
- Bravo's delivery drop-down offers AUTO, SMS, MobilePawn only (ROA probe 11/19); NTFREE is a fourth stored value that is not in that list. Public web search: no definition.
- The two NTFREE events that cannot be app messages: "MobilePawn New Loan" and "MobilePawn New Layaway" = app invitation to NON-activated customers at a new loan/layaway (max one per 7 days). These must go by text. Can be moved: nightly loan list has Age + MobilePawn status, layaway list has Age. Needs: wording OK from Joshua, then Bravo's two invite events switched off (unchecked).
- Proof of zero Bravo SMS = the invoice for December usage (early January), or a per-event usage breakdown from Bravo billing (email needs Joshua's OK).

## 2026-11-27 9:48 PM — Joshua: invitation wording must be shopping + paying -> "yes build it"; "ok email them"
- EMAIL SENT 9:50 PM from jdavis@fcfpawn.com to billing@bravostoresystems.com, cc ashleyn@ (Gmail thread 1a2200e25e776fb6, subject "How MobilePawn messages bill - acct VALPAW000"): does the FREE delivery type bill as SMS / MobilePawn Message / nothing; November count by event. Checked first: no prior thread on this (30 days, inbox + sent).
- App invitation built: TEMPLATES["app_invite"] = "Valley Pawn {store}: thanks for coming in! Shop and make payments from your phone with our free app thevalleypawn.com/app Text STOP to unsubscribe" (151 max). plan_invites: loan written / layaway started in the last 7 days, MobilePawn Not Activated, phone on file, not store DNT, not opted out, not dead, one per phone per 7 days (ledger key invite|phone). Sent only where fleet/state/loan_reminders_live/<STORE>.invites exists (CUL created); always recorded in trial/<date>/invites_<STORE>.csv.
- Loan list window widened to +32 days (reports/LoanReminders.ahk) so loans written today are listed; watcher validate+restart queued 9:52 PM (20261127-2152-wvalidate).
- Bravo script mode `invitesoff` (unchecks "MobilePawn New Loan" + "MobilePawn New Layaway", one store per run). Culpeper tonight ~1:05 AM; other four Mon 11/30 if Culpeper is clean Sat + Sun.
