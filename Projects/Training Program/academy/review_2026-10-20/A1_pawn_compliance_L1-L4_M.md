# A1 — Pawn industry operator & regulatory compliance review: Levels 1–4 and the Manager Track

Scope read in full: `ALL_LESSONS_DUMP.txt` lines 1–2235 (L1-00 → L4-06) and 4300–4819 (M-00 → M-06). Every company rule was checked against `sources/SOURCES_CURRENT.md` (P&P v2026.8 / Handbook v2026.6), `sources/*.txt`, and the brief's Known facts. Every legal claim was checked against the current Code of Virginia (law.lis.virginia.gov, read 2026-10-20) and federal sources noted in the citation column. Severity: BLOCKER / MUST-FIX / SHOULD-FIX / NOTE.

Statutes verified today (so the lesson authors don't have to re-check): Va. Code § 54.1-4004 ($5 lost-ticket fee, only if noticed on ticket); § 54.1-4005 (no sale until term ≥30 days + 15-day grace AND statement of ownership on file); § 54.1-4008 (interest 10%/≤$25, 7%/>$25<$100, 5%/≥$100; no splitting; renewals on original amount; TILA APR not a violation); § 54.1-4009 (record fields; ID unexpired government photo ID with current address or other address proof; military ID not imaged → other ID or photograph the person; (C)(1) service fee lesser of 5%/$3; (C)(2) late fee ≤10% only if on ticket; (D) altered serials barred; natural-person violation = Class 4 misdemeanor; electronic records ≥1 year); § 54.1-4010 (daily report by noon following day; Class 4 misdemeanor); § 54.1-4011 (admit LE, examine records/articles, receipt required when an article is taken); § 54.1-4013(B) (storage ≤5%/month of amount loaned); § 54.1-4014 (Class 4 misdemeanor; VCPA prohibited practice); Va. Code § 59.1-510/-514 (telephone privacy: covers texts; EBR 18 months / inquiry 3 months; internal opt-out honoured ≥10 years). All P&P §05.0 citations check out.

---

## Cross-cutting findings (apply to several lessons)

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| X1 | **BLOCKER** | L1-01, L2-02, L3-03 (and any slide saying "ten to six") | L1-01 slide 5 bullets+say; L1-01 Q2 (all three options and whys); L1-01 KEY_POINTS; L2-02 slide 1 bullets+say ("Stores close at 6:00. Nobody stays past 6:30"); L2-02 KEY_POINTS ("Close at 6"); L2-02 Q1 ("It's 5:58 … At 5:58 you're open"); L2-02 Q2 why ("6:30 is the latest anyone stays"); L3-03 Q4 ("It's Saturday and you close at 6") | "All stores 10 AM to 6 PM" / "Store hours are ten to six" / "'Yes, we're open ten to six, Monday through Saturday.' — why: That's the schedule at Culpeper, Roanoke and Waynesboro" / "Stores close at 6:00" / "It's Saturday and you close at 6" | Brief: hours changed 10/1 — every six-day store closes 5 PM Saturday; Culpeper & Roanoke Mon–Fri 10–6, Sat 10–5. Replace: L1-01 slide 5 bullet 1 → "Weekdays 10 AM to 6 PM; Saturdays 10 AM to 5 PM at the six-day stores; everyone in the store by 9:30"; narration → "Store hours are ten to six on weekdays, and the six-day stores close at five on Saturday." Q2 distractor 1 → "'Yes, ten to six, Monday through Saturday, same as the other stores.'" with why "…and no store is open ten to six on Saturday any more — the six-day stores close at five." L2-02 slide 1 → "Stores close at 6 on weekdays and 5 on Saturday at the six-day stores; nobody stays more than 30 minutes past close unless still helping a customer" (narration + key point to match). L3-03 Q4 → "It's 4:58 PM Saturday and you close at 5." A customer-facing hours error on day 1 is the one thing a new hire will repeat to a customer. | Brief "Known facts" (10/1 hours change); P&P §01.01 and Handbook "Hours of Business" are both stale ("No Valley Pawn store ever closes at 5:00 PM" — now false) and must be corrected in the same pass. |
| X2 | **BLOCKER** | L1-00, L1-02, L1-04, M-05 (+ L1-07 by implication) | L1-00 slide 1 bullet 2; slide 3 bullet 3 + say ("ask in the ask handbook channel"); KEY_POINTS 3; Q3 correct option "Ask in #ask-handbook" and distractor why "#ask-handbook does". L1-02 OBJECTIVES ("use #ask-handbook"); slide 2 heading, bullets 1–4, say ("the ask handbook channel in Slack"); KEY_POINTS 2; Q4 correct option and why; Q5 prompt and all three whys. L1-04 TITLE ("…#ask-handbook"); slide 2 bullet 2 + say ("Ask handbook is where you ask what the rule is"); KEY_POINTS 2. M-05 slide 2 bullet 4 ("Preston sets up Slack, #ask-handbook, Chekkit…") — narration already says "the handbook assistant". | Every "#ask-handbook" / "ask handbook" occurrence in scope (complete list at left; 23 learner-facing hits). | Decide before launch: (a) global rename to "#ask-goldilocks" in bullets/key points/quiz (free) and re-record the five narration lines that say "ask handbook channel" (L1-00 slide 3, L1-02 slide 2, L1-04 slide 2 ≈ 420 characters), or (b) keep the channel name #ask-handbook until the lessons are re-cut. Launching with 23 references to a channel that no longer exists on day 1 is a broken experience. Also update the L1-04 lesson title (it is the unit name in TalentLMS). OB-2026-01 Rev2 line 40 and HR-2026-04 §1 name #ask-handbook too — change in the same pass. | Brief "Known facts" (#ask-handbook retired for #ask-goldilocks at launch); OB-2026-01 Rev2 Day 1 row. |
| X3 | **BLOCKER** | L1-07 (and L2-04 Q6, L1-07 Q1) | L1-07 slide 1 bullet 3 + say; L1-07 Q1 distractor 3 why; L2-04 Q6 correct why and distractor why | "Goldilocks … It posts. It doesn't answer questions — take those to your Store Manager" / "Goldilocks posts; it doesn't read replies." | If the Q&A bot in #ask-goldilocks is also named "Goldilocks", this slide is wrong on day 1 of launch and contradicts L1-00/L1-02 ("ask the bot what the rule is"). Fix (cheapest): L1-07 slide 1 bullet 3 → "In #ask-goldilocks it answers 'what's the rule?' from the Handbook and P&P. Everywhere else it only posts reports — it doesn't read replies to a report"; narration line → "Goldilocks answers rule questions in the ask goldilocks channel. On the report channels it only posts. It doesn't read replies there." Keep the L2-04/L1-07 "doesn't read replies" whys (still true). | Brief "Known facts" (#ask-goldilocks, bot "Goldilocks"); L1-07 sources (rename of VP OPS ENGINE → Goldilocks). |
| X4 | **MUST-FIX** | L1-01 vs L3-04 | L1-01 slide 3 bullet 3 + say ("Every customer, every visit hears three things: 30-day warranty…, the mobile app…, and free layaway"); L1-01 KEY_POINTS 4; L1-01 Q4 (correct option names three). L3-04 FLOOR_CHECK ("The four talking points delivered (30-day warranty, clearance, free layaway, mobile app)"); L3-04 slide 5 bullet 4 + say ("the four things every customer hears… what's on clearance"); L3-04 KEY_POINTS 6; L3-04 Q8 correct option "Warranty, clearance, free layaway, and the app" and both distractor whys. | Level 1 teaches THREE talking points (matches P&P §07.04 and Joshua 10/13); Level 3 teaches FOUR (adds "clearance"). The 10/14 default D17 said "four everywhere" — but it was never applied to L1-01, and it contradicts the governing P&P text and Joshua's 10/13 greeting standard, which both list exactly three. | Revert L3-04 to three: FLOOR_CHECK "…The three talking points delivered (30-day warranty, free layaway, mobile app)"; slide 5 bullet 4 → "Then the three things every customer hears: 30-day warranty, free layaway, the mobile app"; narration → "And before they walk out, the three things every customer hears on every visit: the thirty day warranty on everything we sell, free layaway, and the mobile app to shop and pay." Q8 correct → "Warranty, free layaway, and the app"; whys to match. (Level 7 lessons outside my scope carry the same "four" and need the same decision.) | P&P §07.04 "TELL EVERY CUSTOMER about the three things that set Valley Pawn apart: the 30-day warranty…, the mobile app…, and free layaway"; Brief "Known facts" (Joshua 10/13). |
| X5 | **MUST-FIX** | L1-01 | slide 3 (greeting standard); Q1; Q7 | Slide 3 teaches "stand up, 'Welcome to Valley Pawn!'" and the three talking points, but never teaches the settled greeting question: "Have you ever been here before?" → first-timer gets "what makes us different". The question is a Known fact (Joshua 10/13) and L3-02/L4-01 later open with it ("Have you done business with us before?") with no Level 1 foundation. | Add to slide 3 bullet 1: "…'Welcome to Valley Pawn! Have you ever been here before?'" and one sentence of narration: "Then ask, have you ever been here before? If it's their first time, tell them what makes us different." Key point 3 to match. No quiz change required. (One narration line ≈ 120 characters.) | Brief "Known facts" — Greeting (Joshua 10/13). |
| X6 | **MUST-FIX** | L1-05 vs L3-05 (and L1-05 internal) | L1-05 slide 2 bullet 3 + say ("Account details go to the account holder only… An ex, a cousin or a friend… is not the customer"); L1-05 KEY_POINTS 1; L1-05 Q3 why ("account details go to the account holder only"). BUT L1-05 Q2 correct why: "Account details go only to the verified customer (or spouse or attorney)". L3-05 slide 1 bullet 5 + say and KEY_POINTS: "Account details go only to the customer, their spouse or their attorney". | The same rule is stated three different ways inside Level 1–3: "account holder only" (L1-05 slides), "customer or spouse or attorney" (L1-05 Q2 why, L3-05). A learner who passes L1-05 fails L3-05's wording and vice-versa. | Pick one. The P&P in force (§08.02) says customer, spouse or attorney; the 9/28 huddle draft says account holder only and is "awaiting Joshua". Until Joshua signs the draft, the P&P controls: change L1-05 slide 2 bullet 3 to "Account details go to the verified account holder — or their spouse or attorney, verified the same way. An ex, a cousin or a friend calling 'for' someone is not the customer" and narration to match (≈ 60 characters added); L1-05 Q3 stays correct (an ex is not a spouse). If Joshua signs "account holder only, including spouses", instead change L1-05 Q2 why and L3-05 slide 1/key points. Either way, one sentence, everywhere. | P&P §08.02 "Disinterested Third Parties" ("Anyone other than the debtor, the debtor's spouse, or the debtor's attorney is a disinterested third party"); L1-05 sources OPEN (Account_Details_Phone_Text_Policy_2026-10 awaiting Joshua). |
| X7 | **MUST-FIX** | L1-00 / L1-02 / L1-04 vs L1-02 Q4 | L1-00 slide 1 bullet 2, slide 3 bullet 3, KEY_POINTS 3 ("#ask-handbook first, then your Store Manager"); L1-02 Q4 correct option "Ask your Store Manager, or #ask-handbook if they're not there" + why "With a customer waiting, your manager is the fastest answer" | The order is reversed between the intro and the quiz: bot first vs manager first. | Add the condition to L1-00: "Stuck on a rule? Ask the bot first — unless a customer is waiting, then your Store Manager" (bullet/key point only; narration can stay). | L1-00 vs L1-02 Q4. |
| X8 | **MUST-FIX** | L3-01, L3-06, L4-04 vs M-01 | L3-01 slide 5 bullet 5 + say ("First-payment default … No 30-day hold. Pullable once the 15-day legal grace is up"); L3-06 slide 3; L4-04 slide 1 bullet 4 + say ("Bravo marks the loan expired right away … but it still isn't pulled before the fifteen day grace is up"). M-01 slide 4 bullet 5 + say ("Never made a first payment? No 30-day hold — expire it as soon as it's past due, any amount"); M-01 Q7 prompt "A loan written five weeks ago never got a single payment and is now past due" — correct option "Expire it now — a first-payment default gets no 30-day hold". | Associates are taught "not pulled before day 15 past due"; managers are taught "expire it now" on a loan that is 5 days past due (5 weeks from writing = day 5 past due), with no mention of the 15-day legal floor. "Expire" in Bravo moves the loan out of active status toward PFI; if a manager reads M-01 literally and the item is pulled/priced/sold before day 45 of the loan, that is a § 54.1-4005 violation (Class 4 misdemeanor, VCPA exposure) and the pledgor — who still has a statutory right to redeem through day 45 — is turned away. | M-01 slide 4 bullet 5 → "Never made a first payment? No 30-day hold. Mark it expired in Bravo as soon as it's past due, any amount — but nothing is pulled, priced or sold before the 15-day legal grace is up (day 45 of the loan), and the customer can still redeem until then." Narration: replace "It's expired as soon as it's past due, whatever the amount" with "You mark it expired as soon as it's past due, whatever the amount, but it's still not pulled before the fifteen day legal grace is up." Q7 correct → "Mark it expired now; it can be pulled once the 15-day grace is up"; why → "First-payment defaults get no 30-day hold, but the 15-day statutory floor still applies before anything is pulled or sold." Also reconcile P&P §06.01's bare "expired as soon as they are past due" with the floor it states two paragraphs earlier. | Va. Code § 54.1-4005 (no sale until term + 15 days); P&P §05.01 ("Staff never pull on day 16"), §06.01; L4-04 OPEN (review 2026-10-14). |
| X9 | **MUST-FIX** | L4-04 vs M-03 (discount approver) | L4-04 slide 4 bullet 4 + say ("At the counter your ceiling is 30%… Nothing ever sells at more than 50% off"); L4-04 Q7 why ("Up to 30% is yours, and nothing sells above a 50% discount"); L4-04 KEY_POINTS 5. M-03 slide 2 bullet 1 + say ("Between 30% and 50% needs a manager"); M-03 KEY_POINTS 2; M-03 Q2 distractor why ("Over 30% needs a manager"). | The associate lesson never says who can go 31–50%; the manager lesson says "a manager". A learner at Level 4 who is asked for 40% off does not learn that the answer is "let me get my manager" — only that it is "not yours". | L4-04 slide 4 bullet 4 → "At the counter your ceiling is 30%. 31–50% is a manager's call — get your manager. Nothing ever sells at more than 50% off." Q7 correct why → "Up to 30% is yours; 31–50% needs your manager; nothing sells above 50% off." Key point 5 to match. Bullet/why edits only; narration unchanged. | Brief "Known facts" (31–50% needs a manager); P&P §05.03; M-03 slide 2. |
| X10 | **NOTE** | L3-06, L4-04, M-01 vs P&P §06.01 | L4-04 slide 1 ("Count from the day after the due date. That's day 1 past due"); M-01 slide 4 ("Day 1 = the day after the due date") | The lessons follow the settled rule in the brief. P&P §06.01 still reads "Day 1 is the loan due date." Not a lesson defect; the manual sentence should be changed to match the Academy before the Gusto re-sign, or a trainee reading §06.01 will find a one-day contradiction. | Edit P&P §06.01 first sentence: "Day 1 past due is the day after the loan due date." | P&P §06.01; Brief "Known facts". |

---

## L1-00 — Welcome to Level 1

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 1 | BLOCKER | L1-00 | slide 1 b2, slide 3 b3 + say, KEY_POINTS 3, Q3 (correct option, distractor 3 why) | "#ask-handbook" × 5, "ask handbook channel" × 1 | See X2. | Brief. |
| 2 | MUST-FIX | L1-00 | slide 1 / slide 3 / key point 3 | "Stuck on a rule? #ask-handbook first, then your Store Manager" | See X7 (add "unless a customer is waiting"). | L1-02 Q4. |
| 3 | NOTE | L1-00 | Q2 correct why | "After two misses your manager is nudged to sit down with you" | Consistent with L1-01 slide 6 and Q5. No action. | Master Plan v2. |

## L1-01 — Welcome to Valley Pawn

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 4 | BLOCKER | L1-01 | slide 5 b1 + say; Q2 all options; KEY_POINTS 6 | "All stores 10 AM to 6 PM" / "'Yes, we're open ten to six, Monday through Saturday.'" | See X1. | Brief 10/1 hours change. |
| 5 | MUST-FIX | L1-01 | slide 2 b2 + say; KEY_POINTS 2 | "30 days, with a service charge" / "The loan runs thirty days and carries a service charge." | "Service charge/fee" is a specific statutory line item (lesser of 5% or $3, § 54.1-4009(C)(1)). The monthly cost of the loan is the FINANCE CHARGE (interest + storage + service). L3-01 later corrects a caller for exactly this kind of word slip ("he calls the interest a 'storage fee'… right idea, wrong word"). Replace "service charge" with "monthly finance charge" in bullet 2, bullet 3 ("extend it (finance charge only)") and the two narration sentences (≈ 2 words each). Key point 2 can stay. | P&P §05.0; §11.01 Glossary ("Finance Fee: the cost of borrowing"); L3-01 slide 2. |
| 6 | MUST-FIX | L1-01 | slide 3, KEY_POINTS 4, Q4 | Three talking points, no "Have you ever been here before?" | See X4 (keep three) and X5 (add the question). | P&P §07.04; Joshua 10/13. |
| 7 | SHOULD-FIX | L1-01 | slide 5 b2 + say | "Culpeper, Roanoke and Waynesboro: Monday through Saturday" / "Harrisonburg and Lexington: closed Wednesday" | Matches Joshua's 2026-10-14 note (Waynesboro six days from 10/14) but contradicts BOTH governing documents, which still say only Culpeper opens Wednesday and Waynesboro/Roanoke are closed Wednesday. The lesson is right; the P&P §01.01 and Handbook "Hours of Business" must be corrected before employees re-sign, or the bot in #ask-goldilocks will answer the hours question wrong. | P&P §01.01; Handbook "Hours of Business"; L1-01 sources (Joshua 2026-10-14). |
| 8 | SHOULD-FIX | L1-01 | slide 4 b2 + say | "Start with your immediate supervisor; if it isn't resolved in a reasonable time, go to the next person up" | Accurate to the Handbook, but the Handbook also routes "a complaint or problem [that] involves the employee's immediate supervisor" to "the next person in the chain of command or Human Resources". Valley Pawn has no HR department (P&P changelog v2026.4 removed it); the lesson rightly says Preston. No action on the lesson; the Handbook line should drop "or Human Resources". | Handbook "Communication" ¶ last; P&P changelog "Roles and systems". |
| 9 | NOTE | L1-01 | Q6 correct why | "any threat of a lawsuit goes to Preston immediately" | Correct per §01.07 and §09.07. | P&P §01.07. |

## L1-02 — Your Handbook and the P&P

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 10 | BLOCKER | L1-02 | OBJECTIVES; slide 2 heading/b1–b4/say; KEY_POINTS 2; Q4 correct option + why; Q5 prompt + three whys | "#ask-handbook" × 7, "ask handbook channel" × 1 | See X2. | Brief. |
| 11 | SHOULD-FIX | L1-02 | slide 6 b2 + say | "no hats; no earrings or visible piercings" / "No hats, no earrings, no visible piercings." | The Handbook rule has two legally required exceptions (approved medical accommodation → branded cap; approved religious head covering). Taught as an absolute, a new hire who wears a hijab or yarmulke hears "no hats" on day 1. Add to bullet 2: "(religious or medical head coverings are allowed with an approved accommodation — ask your Store Manager)". Narration can stay. | Handbook "Dress Code — Hats and head coverings" (Title VII / Va. Human Rights Act accommodation). |
| 12 | NOTE | L1-02 | slide 5 say | "If you think you've been underpaid, tell Preston or Joshua and it gets fixed within fourteen days." | Verified: P&P §01.04 "pay any shortfall within fourteen (14) days of receiving notice". Correct. | P&P §01.04. |
| 13 | NOTE | L1-02 | Q1 why | "A missed punch is reported to Preston (or Joshua if he can't be reached)" | Verified §01.04 last paragraph. Correct. Handbook "Time Tracking" says "report the matter to their immediate supervisor" — P&P is the store procedure and controls; no change. | P&P §01.04; Handbook "Time Tracking". |
| 14 | NOTE | L1-02 | Q6 distractor 1 why | "That's protected by federal and Virginia law" | Correct — NLRA §7 and Va. Code § 40.1-28.7:9. | Handbook "Salary / Wage Communication". |

## L1-03 — Gun Safety 101

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 15 | MUST-FIX | L1-03 | slide 1 b3 + say | "Third day lands on a day the store is closed? It's due the day before" / "If your third day lands on a day the store is closed, it's due the day before." | Not in HR-2026-05 (§3 counts calendar days and is silent on closed days — the lesson's own sources say so). This shortens a condition-of-employment deadline below what the signed policy says, which is the one direction an unsourced rule must never go. Spec: "No invented policy… keep the question out." Delete the bullet and the sentence (narration −1 sentence), or have Joshua add the closed-day rule to HR-2026-05 before launch. Q6 (Thursday → Saturday) is unaffected. | HR-2026-05 §3 (per lesson sources); LESSON_SPEC rule 1; L1-03 sources OPEN (review 2026-10-14). |
| 16 | NOTE | L1-03 | slide 2 b1–b2; slide 3 b4 | "free Basic Gun Safety 101 class… $25 Certificate of Completion — the Company pays" / "nothing is reimbursed from petty cash" | Matches P&P §10.06 as rewritten (course free, $25 certificate bought by the Company; petty-cash instruction withdrawn). Correct. | P&P §10.06. |
| 17 | NOTE | L1-03 | Q8 | "do the gun safety class on your own laptop… No. It's paid working time, done on the clock" | Consistent with Training-At-The-Store policy (10/5). Note that OB-2026-01 Rev2 has the NRF RISE Up course done "on own phone/home device" — a source conflict for M-05, not for this lesson. | Training_At_The_Store_Policy_2026-10; OB-2026-01 Rev2 Day 1–7 row. |

## L1-04 — Your tools

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 18 | BLOCKER | L1-04 | TITLE; slide 2 b2 + say; KEY_POINTS 2 | "Your tools: Bravo, Slack, Chekkit, #ask-handbook" / "#ask-handbook: 'what's the rule?'" / "Ask handbook is where you ask what the rule is" | See X2. Title is also the TalentLMS unit name. | Brief. |
| 19 | NOTE | L1-04 | slide 5 b2 + say; KEY_POINTS 4 | "Calls are different from texts: we can call about offers for 18 months after a customer's last transaction. A marketing text always needs recorded opt-in" | Legally imprecise but conservative: Virginia's telephone-privacy EBR exemption (18 months / 3 months) applies to texts as well as calls (§ 59.1-510 defines solicitation to include texts; § 59.1-514(D) exempts EBR). The stricter opt-in rule for texts is justified by the TCPA (prior express written consent for automated marketing texts, 47 CFR 64.1200(a)(2)) and is company policy in §07.06. No change needed; if the "why" is ever rewritten, say "texts sent from a platform like Chekkit need written opt-in under federal law" rather than "the 18-month window doesn't apply to texts". | 47 U.S.C. § 227; 47 CFR 64.1200; Va. Code §§ 59.1-510, 59.1-514; P&P §07.06. |
| 20 | NOTE | L1-04 | slide 4 b4 + say | "STOP… It holds at all five stores, forever" | Stricter than law (Virginia: at least 10 years; federal internal DNC: 5 years). Fine as policy. | Va. Code § 59.1-514(A); 47 CFR 64.1200(d)(6). |
| 21 | NOTE | L1-04 | slide 3; Q2 | Store email password rule | Verified word-for-word against P&P §03.17. Correct. | P&P §03.17. |
| 22 | SHOULD-FIX | L1-04 | Q7 distractor 3 why | "Supplies aren't normally paid by cash disbursement; an emergency purchase needs documented Market Manager approval." | Correct, but P&P §03.01 now says supply requests go to Preston (Amazon Business) and orders ≥$250 need approval; the lesson's channel name #supply-request comes from the Handbook. Both are fine; add "(Preston orders it on Amazon Business)" to the slide 2 bullet so the learner knows what happens after they post. | P&P §03.01; Handbook "Branch-Ordered Supplies". |

## L1-05 — What you never say on the phone

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 23 | MUST-FIX | L1-05 | slide 2 b3 + say vs Q2 why | "Account details go to the account holder only" vs Q2 why "Account details go only to the verified customer (or spouse or attorney)" | Internal contradiction inside one lesson. See X6. | P&P §08.02. |
| 24 | SHOULD-FIX | L1-05 | slide 5 say (last sentence) | "They don't owe us anything, and it never touches their credit. That's the law, not just our policy." | Overstated. No Virginia statute says a pawn is non-recourse; it follows from the nature of a pledge and § 54.1-4005 (the pawnbroker's remedy is sale of the pledge), and it is company policy in §09.03. What IS the law is that telling a customer they owe a balance, will be sued, or will be credit-reported is a false/deceptive statement (VCPA). Rewrite the sentence: "Saying otherwise isn't just against our policy, it's a false statement about a debt, and that's illegal." (one narration sentence, same length). | Va. Code § 54.1-4005; § 54.1-4014 / § 59.1-200 (VCPA); P&P §09.03. |
| 25 | NOTE | L1-05 | slide 6 b2 + say | "officers get access to our records under Virginia law; callers do not" | Verified § 54.1-4011. Correct. | Va. Code § 54.1-4011. |
| 26 | NOTE | L1-05 | slide 6 b3 | "A caller says they're a police officer? Take their name and department, then call back through the department's main number" | Standard industry practice, not in P&P (lesson says so in sources). Keep; Preston should add one line to §01.06 or §07.03. | L1-05 sources OPEN. |
| 27 | NOTE | L1-05 | Q8 distractor 3 why | "Melt math comes from the spot sheet, and the item has to be identified first" | Consistent with L4-03 slide 6 and the Melt Calculation Policy. Correct. | P&P §04.03. |

## L1-06 — Cash and your drawer

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 28 | SHOULD-FIX | L1-06 | slide 4 b5 + say | "Use the pen or the UV light on every $50 and $100 you take in. A bill that fails goes to your manager" | Two experienced-operator points: (1) the iodine pen is defeated by bleached-and-reprinted genuine paper (the most common counterfeit $100 a pawnshop sees); teach "UV strip and watermark, pen is a backup". (2) A suspected counterfeit is never handed back to the passer — the Secret Service procedure is: do not return it, delay the passer if safe, note their description and vehicle, give it only to police/Secret Service, initial and date the note's border. The lesson's "goes to your manager" leaves the learner free to hand it back. Replace bullet: "Check every $50 and $100: UV light for the strip, hold it up for the watermark; the pen is a backup. A bill that fails doesn't go back to the customer — hand it to your manager, who calls the police." Narration: swap one sentence. | U.S. Secret Service "Know Your Money" guidance (18 U.S.C. § 472 — knowingly passing a counterfeit is a federal crime; returning a suspected note to the passer is how stores become the passer); L1-06 sources OPEN (counterfeit check not in P&P). |
| 29 | NOTE | L1-06 | slide 6 b1–b2; Q7 | Form 8300 rule: "More than $10,000 in cash… in one payment, within 24 hours, or in related payments over 12 months… filed within 15 days" | Verified against 26 U.S.C. § 6050I / IRS Form 8300 instructions and P&P §05.02. Q7 correctly uses cash RECEIVED by the store (a coin sale). Correct. Note for managers only: 8300 must be e-filed (FinCEN BSA E-Filing) by businesses required to file 10+ information returns — Bravo generation is fine, submission path is Joshua's. | 26 U.S.C. § 6050I; 26 CFR 1.6050I-1; P&P §05.02, §09.04. |
| 30 | NOTE | L1-06 | slide 1; slide 3; slide 5 | $275 float; $2,000 drawer cap; Transfer Tender; recount→research→Preston→document; 90-day employee-purchase floor; Joshua approves family transactions | All verified against §02.03, §02.05, §02.06, §02.08, §05.10, §01.10. Correct. | P&P §§02.03–02.08, 01.10, 05.10. |
| 31 | NOTE | L1-06 | slide 1 b4 | "give the excess to your manager to put in the safe" | OPEN (who is the designee when the manager is off) — unchanged since 10/14; L2-01 Q6 answers it ("the employee the manager designated"). No action. | P&P §02.02, §02.06. |

## L1-07 — Meet Goldilocks

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 32 | BLOCKER | L1-07 | slide 1 b3 + say; Q1 distractor 3 why | "It posts. It doesn't answer questions" | See X3. | Brief (#ask-goldilocks). |
| 33 | SHOULD-FIX | L1-07 vs M-01 | slide 6 b3 + say; L3-06 slide 7 b1 | "First-payment defaults (#first-payment-default): loans written 60–90 days ago with no payment yet" | Under the policy taught in M-01/L4-04 a first-payment default is marked expired at day 1 past due (day 31 from writing) and pullable from day 45. A ranking of loans "written 60–90 days ago with no payment yet" therefore lists loans that should already be expired and pulled — the report definition and the policy contradict each other, and L3-06 slide 7 tells associates to call those customers to "save a loan". Either the report window should be "due in the last 30 days with no payment" or the lessons should describe the report as "first-payment defaults that are still on the shelf". Reconcile the report with Preston before launch; edit bullet text only (no narration change needed in L1-07 if the bullet is corrected and the narration keeps "loans… with no payment yet"). | P&P §06.01; L1-07 sources (Goldilocks weekly posts); M-01 slide 4. |
| 34 | NOTE | L1-07 | slide 3 (ladder); Q4; Q5; Q6 | Discount Review ladder 10/15/20/30/40/50; Pawn Walk flag <30%; Sold Review flag <25% | Report settings, consistently stated in L1-07, L4-03, L4-04, M-03. Q4 math correct (20-day item, 15% > 10%). | L1-07 sources (live posts 2026-09-30). |

## L2-00 — Welcome to Level 2

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 35 | NOTE | L2-00 | Q1 | "$4 over… Recount, research the cause, then call Preston" | Matches §02.08 (overage handled like a shortage). Correct. | P&P §02.08. |

## L2-01 — Opening the store

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 36 | NOTE | L2-01 | slide 4; Q2 | Open Store → Open Till $0.00 → Transfer Tender BANK→SAFE → SAFE→TILL | Matches §02.13. P&P §02.03 still describes a different till-opening path ("Open Till → Main Drawer → Remove/Add Cash → Add → add cash from bank account") — manual-internal conflict; the lesson picks the right one. Preston to delete the §02.03 sentence. | P&P §02.13 vs §02.03. |
| 37 | NOTE | L2-01 | Q6 distractor 3 why | "Ninety days is the keys rule, not the safe rule" | Verified §10.02. Correct. | P&P §10.02. |
| 38 | NOTE | L2-01 | slide 5 b3 | "Last night's police report: if it didn't transmit, it has to go by noon today and Preston is told" | Verified § 54.1-4010. Correct. | Va. Code § 54.1-4010. |

## L2-02 — Closing the store

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 39 | BLOCKER | L2-02 | slide 1 b1–b2 + say; KEY_POINTS 1; Q1; Q2 why | "Stores close at 6:00. Nobody stays past 6:30…" / "It's 5:58…" | See X1 (Saturday 5 PM at six-day stores). | Brief 10/1. |
| 40 | NOTE | L2-02 | slide 3 b1; Q3 whys | "It's due by noon tomorrow by law… Failing to file is a Class 4 misdemeanor" | Verified § 54.1-4010 (Class 4 misdemeanor). Correct. | Va. Code § 54.1-4010. |
| 41 | SHOULD-FIX | L2-02 | Q7 | "$3,400 cash on hand, and it's pouring rain… Make the deposit tonight; over $3,000 goes to the bank" | Rule is right (§10.04), but the lesson's own sources say the night-deposit procedure (night drop after dark? who carries? two people?) is unwritten. A closer alone at 6:15 PM in the rain walking $3,400 to a night drop is the robbery scenario §10.01 is written to avoid. Keep the question, soften the correct why: "…over $3,000 goes to the bank — by the night-drop procedure your manager sets (two people where possible). If you're alone, call your manager rather than skip it." | P&P §10.04 ("go to the bank when cash on hand exceeds $3,000"); §10.01 (two employees to the bank where possible); L2-02 sources OPEN (night deposit). |
| 42 | NOTE | L2-02 | slide 4; Q4; Q6 | "All jewelry and all handguns are locked in the safe at close. No exceptions" | Verified §12.03. Correct. | P&P §12.03. |

## L2-03 — Balancing your drawer

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 43 | NOTE | L2-03 | slide 3; Q1–Q8 | Four moves; causes list; "never docked"; Q2 ($15/$15) | All verified against §02.08 (causes list matches word for word) and §02.13 (Back before Save). Q4 (tape $20 higher → re-run) is the right practice. No findings. | P&P §02.08, §02.13. |

## L2-04 — The safe, and how money reaches it

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 44 | SHOULD-FIX | L2-04 | slide 2 b5 + say; Q2 why; Q4 distractor why | "If the customer can't wait, take it on a ticket: write a small pawn loan on it today so the gold stays with you and they come back for the full price" | An operator's wince: a "placeholder" pawn loan is a real loan with a real finance charge and a real pawn ticket on the police report. The lesson never says how it converts to the buy when the customer returns (does the customer pay the finance charge to redeem and then sell? does the manager convert it in Bravo?). Taught as is, a day-5 trainee may charge the customer interest on their own gold sale. Add one bullet: "When they come back, your manager converts the loan to the buy — the customer isn't charged for the holding loan." Narration unchanged if management confirms that is the practice; otherwise state what is. | L2-04 sources OPEN (review 2026-10-14: 'take it on a ticket' wording and any minimum/maximum); P&P §05.0 (charges are what the ticket says). |
| 45 | NOTE | L2-04 | slide 2 b5 | "Call Joshua, then Hillary, then Preston" | Names allowed (person to call). Hillary is not defined anywhere in Levels 1–4 (who she is, her number). Add "(Hillary Davis, co-owner)" once in the bullet, or the trainee will not know who to call. | LESSON_SPEC rule on names. |
| 46 | NOTE | L2-04 | slide 1 b4 | "Spare keys… opened only on Preston's instruction with two people present" | Verified §02.04. Correct. | P&P §02.04. |

## L2-05 — The daily jewelry count

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 47 | NOTE | L2-05 | slide 2; Q5; Q6; Q8 | Five buckets; charms→Pendants; chains→Necklaces; Q8 arithmetic 120 − 2 + 1 = 119 | Verified §04.03 Jewelry Category Standard; arithmetic correct. | P&P §04.03. |
| 48 | NOTE | L2-05 | slide 5 b3 | "Store Manager now → Preston same business day → Joshua same business day" | Verified §05.11. Correct. | P&P §05.11. |

## L3-00 — Welcome to Level 3

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 49 | SHOULD-FIX | L3-00 | slide 3 b1 + say; KEY_POINTS 3; Q2 why | "Market Manager for stolen property, a missing statement of ownership, or a Bravo refusal" / Q2 why "Your manager is the first call, and the Market Manager hears about it if it can't be fixed" | P&P §05.00A and §09.07 say "stop and call Preston" directly for a Bravo refusal and a possible stolen item; L3-03 slide 1 and Q2 teach exactly that ("Stop and call Preston before finishing the ticket"). The intro inserts the store manager as a first step that the lesson two units later removes. Align the intro to L3-03/§09.07: "Something's off? Stop. Stolen property, an altered serial, a missing statement of ownership or a Bravo refusal go straight to Preston; everything else, your store manager first." (bullet, key point, Q2 why; narration one sentence). | P&P §05.00A ("stop and call Preston Peters rather than working around it"), §09.07; L3-03 Q2. |
| 50 | NOTE | L3-00 | Q1 | "Rate exceptions exist only through the Market Manager, entered in Bravo" | Verified §07.04. Correct and consistent in L3-01, L3-04, M-03. | P&P §07.04. |

## L3-01 — How a pawn loan works

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 51 | NOTE | L3-01 | slide 3 (all bullets); Q3; Q4; Q8 | Interest 10/7/5 by tier; storage ≤5%; service lesser of 5%/$3; late fee ≤10% only if on ticket; $5 lost ticket only if on ticket; no splitting; renewals on original amount | Every figure and every statutory cite verified today against the Code of Virginia. Q4 tier math correct (5 × $24 → 10% tier; 2 × $60 → 7% tier; $120 → 5%). Q8 correct. No findings. | Va. Code §§ 54.1-4004, -4008, -4009(C), -4013(B). |
| 52 | NOTE | L3-01 | slide 5; Q7 | "nothing is sold before day 45 of the loan… hold through 30 days past due… day 31 pulled… by day 61… past 61 needs CEO approval" | Verified § 54.1-4005 and §06.01; matches Known facts and L3-06, L4-04, M-01. Correct. | Va. Code § 54.1-4005; P&P §06.01. |
| 53 | SHOULD-FIX | L3-01 | slide 6 say (last sentence); Q2 distractor 1 why | "saying them can break federal collection rules and Virginia's consumer protection law" / "can violate federal collection standards and the VCPA" | The FDCPA governs third-party debt collectors, not a creditor collecting its own loans; Valley Pawn's exposure for a false "you'll be sued / credit-reported" statement is the Virginia Consumer Protection Act (and the pawnbroker chapter via § 54.1-4014), plus FTC Act §5. The P&P itself adopts the FDCPA as a policy standard, so the lesson is not wrong to teach it as a rule — but "federal collection rules" implies a statute that does not apply. Cheapest fix: leave narration, change the Q2 why to "…can violate our FDCPA-based policy and the Virginia Consumer Protection Act." | 15 U.S.C. § 1692a(6) (FDCPA "debt collector" excludes creditors); Va. Code § 54.1-4014(B), § 59.1-200; P&P §08.02, §09.03. |
| 54 | NOTE | L3-01 | slide 7 | "A pawn loan is consumer credit, so federal Truth in Lending rules apply… finance charge and APR include storage and the service fee" | Correct (Reg Z § 1026.2(a)(14) credit; § 1026.4 finance charge; the late fee is correctly excluded as a default charge). | 12 CFR 1026.4(a), (c)(2); P&P §05.0. |
| 55 | NOTE | L3-01 | Q6 | "picks up on day 3 past due. Bravo adds a late fee… Show him the notice on his ticket and charge what Bravo shows" | Lawful: § 54.1-4009(C)(2) late fee "for each item not claimed by the pledged date… disclosed on the pawn ticket". Correct. | Va. Code § 54.1-4009(C)(2). |

## L3-02 — Qualifying the customer

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 56 | NOTE | L3-02 | slide 2; Q1; Q2 | Unexpired government photo ID with current address or other address proof; record type/issuer/number; image; military ID → other ID or photograph the customer | Verified word-for-word against § 54.1-4009 (ID paragraph and 18 U.S.C. § 701 carve-out). Correct. | Va. Code § 54.1-4009; 18 U.S.C. § 701. |
| 57 | NOTE | L3-02 | slide 3 | "Nobody under eighteen. Nobody who's intoxicated. Nobody known to be a thief…" | Company rule (§01.10). Not a Virginia pawn-chapter statute — the lesson correctly does not call it law. | P&P §01.10. |
| 58 | SHOULD-FIX | L3-02 | slide 1 b4 + say; Q6/Q1 of L4-01 | "History of forfeits and no redemptions in Bravo? Offer a buy, not a loan" | Sound practice, sourced only to KB default-rate entries; the lesson states it as a rule. Keep, but the slide should say "offer the buy first" rather than implying a loan is refused — L4-01 Q2 why already says "A forfeit history isn't a ban". Change bullet to "…Offer the buy first — explain why." | L3-02 sources OPEN; L4-01 Q2 why. |
| 59 | NOTE | L3-02 | slide 5; Q4; Q5 | "$1,000 or more… includes reloans. No exceptions" | Verified §01.10 (twice stated). Q4 distractor 3 ("split into two $800 loans") is correctly treated as structuring to dodge an internal threshold — good distractor. | P&P §01.10. |

## L3-03 — Writing the ticket in Bravo

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 60 | BLOCKER | L3-03 | Q4 prompt | "It's Saturday and you close at 6." | See X1 → "4:58 PM Saturday and you close at 5". | Brief 10/1. |
| 61 | MUST-FIX | L3-03 vs L2-02/L4-05 | slide 7 b3 + say; KEY_POINTS 6; Q4 correct option + why | "If it fails, tell your manager the same day so it's resent before noon" vs L2-02 Q3 "voicemail and Slack Preston tonight" and L4-05 slide 5/Q6 "tell Preston the same day" | Three lessons, two escalation targets for the same failure. §05.00A names Preston. Change L3-03 slide 7 bullet 3 to "If it fails, tell Preston the same day (and your manager) so it's resent before noon"; Q4 correct option → "Tell Preston and your manager tonight so it's resent before noon tomorrow"; key point 6 to match. Narration: "tell your manager that same day" → "tell Preston that same day" (two words). | P&P §05.00A ("if the transmission fails, report it to Preston Peters the same day"); L3-03 sources OPEN (review 2026-10-14). |
| 62 | NOTE | L3-03 | slide 3 (ten-item checklist); Q3 | Record fields | Verified against § 54.1-4009(A) — all ten groups present; "employer" correctly NOT required. The statute additionally allows "any other relevant circumstances" — Bravo covers it. | Va. Code § 54.1-4009(A). |
| 63 | NOTE | L3-03 | sources | "pawn records kept five years, then shredded" | Lawful (statute minimum one year for electronic records). Not learner-facing. | Va. Code § 54.1-4009(B); P&P §03.08. |
| 64 | NOTE | L3-03 | slide 1 b4 | "Leaving required fields blank is a crime under Virginia law" | Verified: § 54.1-4009 last sentence (natural person — Class 4 misdemeanor). Correct and worth keeping in the trainee's face (spec allows it for records rules). | Va. Code § 54.1-4009. |

## L3-04 — Closing the pawn contract

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 65 | MUST-FIX | L3-04 | FLOOR_CHECK; slide 5 b4 + say; KEY_POINTS 6; Q8 (correct option and both whys) | "four things… 30-day warranty, clearance, free layaway, mobile app" | See X4 — revert to three. | P&P §07.04. |
| 66 | SHOULD-FIX | L3-04 | slide 4 say | "A late fee applies if they don't claim the item by the due date" | Accurate to § 54.1-4009(C)(2) wording, but the Bravo-configured start day is unknown (sources OPEN: calls quote a 5-day window). Telling every customer "a late fee applies if you don't claim it by the due date" when Bravo in fact applies it from day 5 would itself be a cost quote that "differs from the printed ticket" (§05.0). Change narration to "A late fee can apply after the due date — it's printed right there" (neutral on the start day) until Preston states the configured rule. | P&P §05.0 (never quote a cost that differs from the ticket); L3-06 sources OPEN (late-fee start day). |
| 67 | NOTE | L3-04 | Q5 | "$5, since it's disclosed on her ticket. Note the lost ticket in Bravo" (on an extension) | Lawful — § 54.1-4004 lost-ticket fee is not limited to redemption. Correct; §05.04 shows the Renewal screen has a lost-ticket step. | Va. Code § 54.1-4004; P&P §05.04. |
| 68 | NOTE | L3-04 | Q7 | Fingerprint refusal → "we can't write it without one" | P&P §05.01 requires it; the lesson's sources say "if they still refuse, stop and ask (§09.07)" but the quiz does not — acceptable (the right answer is still "no fingerprint, no loan"). Preston should state the refusal path in §05.01. | P&P §05.01; L3-04 sources OPEN. |
| 69 | NOTE | L3-04 | slide 4 b4; L3-05 slide 1 | "Firearms and vehicle titles: never released to a third party, except the Level 6 denied-pledgor designation with Market Manager approval" | Verified §05.01 "IF THE PLEDGOR IS DENIED" and §05.04. Correct and consistent in L3-04, L3-05. | P&P §05.01, §05.04. |

## L3-05 — Payments, extensions and redemptions

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 70 | MUST-FIX | L3-05 | slide 1 b5 + say; KEY_POINTS 1; Q1 distractor 2 why | "Account details go only to the customer, their spouse or their attorney" | See X6 — one wording everywhere. | P&P §08.02. |
| 71 | NOTE | L3-05 | slide 4 b5; Q2 | "Firearm? That's a transfer: 4473, State Police check, gun lock. Level 6 only" | Correct: a pawn redemption is a transfer requiring Form 4473 and the point-of-contact check (27 CFR 478.124 — a pawned firearm returned to the pledgor is a transfer to a non-licensee requiring Form 4473 and a NICS/POC check; Virginia is a point-of-contact state via VSP VCheck, Va. Code § 18.2-308.2:2). Gun lock: federal law requires a secure storage device only with handgun transfers (18 U.S.C. § 922(z)); company rule extends to all firearms — stricter, fine. | 27 CFR 478.124; 18 U.S.C. § 922(t), § 922(z); Va. Code § 18.2-308.2:2; P&P §05.01. |
| 72 | SHOULD-FIX | L3-05 | Q6 correct option + why | "He pays the finance charge plus $50 more… It comes off the principal. Bravo shows the new balance" | The lesson's own sources say the Bravo paydown procedure is not in the P&P and the Floor Check asks the manager to "show them the paydown screen". Testing a Bravo behaviour nobody has confirmed (does the $50 reduce principal immediately, or sit as a credit — distractor 3?) is the one quiz item in this lesson that could be marked wrong by the system itself. Either confirm with Preston that Bravo applies overpayment to principal on a Renewal, or change the correct option to "Ask your manager to take it on the paydown screen — never promise the new balance until Bravo shows it" (which is what slide 3 actually teaches). | L3-05 sources OPEN (paydown procedure); slide 3. |
| 73 | NOTE | L3-05 | Q4 distractor 3 why | "Never name a person as the reason. It's 'our policy is'" | Consistent with L1-05 slide 5 and L3-06. Good retrieval. | L1-05. |

## L3-06 — The past-due call

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 74 | NOTE | L3-06 | slide 3; slide 6; Q3; Q4 | 15-day grace / hold through 30 / 31–61 / CEO past 61; calls from 7 days before due; one a day; no voicemail; Mon–Sat 8–9 | All verified (§06.01, §08.01, §08.02). Consistent with L3-01, L4-04, M-01. | P&P §06.01, §08.01, §08.02. |
| 75 | SHOULD-FIX | L3-06 | slide 7 b1 + say | "Every week Goldilocks ranks first-payment defaults: loans written 60 to 90 days ago with no payment yet" | See finding 33 — the report window contradicts the expire-on-day-1-past-due rule; the slide tells associates to work loans that policy says were expired a month ago. Reword after Preston reconciles the report. | P&P §06.01; L1-07. |
| 76 | NOTE | L3-06 | Q5 correct option | "'Yes, that's an extension. It's [Bravo amount], and your new due date is [Bravo date]'" | Bracketed placeholders will be read aloud by nobody (quiz text), fine on screen. Consider "the amount Bravo shows" to avoid literal brackets on the quiz card. | Cosmetic. |
| 77 | NOTE | L3-06 | Q8 correct option | "'Our hold is thirty days past due. It's a courtesy deadline, not a penalty…'" | Does not mention the retired 75-day rule — complies with the spec (no retired rule in learner text). Good. | LESSON_SPEC. |

## L4-00 — Welcome to Level 4

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 78 | NOTE | L4-00 | KEY_POINTS 3 | "Every offer starts with research, and every deal gets negotiated" | Consistent with L4-03. No findings. | KB negotiate-every-deal. |

## L4-01 — Buy or loan?

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 79 | NOTE | L4-01 | slide 2 b3; Q7 | "We hold it thirty days before it's sold" (buys) | Company rule §05.02 (Virginia's pawnbroker chapter sets no purchase hold; the 15-day precious-metals-dealer hold in § 54.1-4104 is a separate regime). 30 days is the stricter figure; fine. | P&P §05.02. |
| 80 | NOTE | L4-01 | slide 3 b5 + say | "A small loan ties up our cash at least two months" | Arithmetic holds (30-day term + 30 days past due before PFI eligibility = 60 days; 45 days is only the legal floor). Correct. | P&P §06.01. |
| 81 | NOTE | L4-01 | slide 4; Q6 | "On general merchandise the buy is the bigger number… Gold works off the estimator (Level 5)" | Sourced to KB (OPEN: 2025-11-11 Joshua said buy and loan 'can be equal' for GOLD only). The lesson scopes it to general merchandise — correct handling. | L4-01 sources OPEN. |

## L4-02 — What we pay the most for

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 82 | SHOULD-FIX | L4-02 | slide 4 b6 | "New in box only: small appliances, vacuums, printers" | "Printers" is not in any listed source (KB appliances-new-in-box-only, vacuums-new-in-box-only). Either cite a KB entry or delete "printers". Bullet-only edit. | LESSON_SPEC rule 1; L4-02 sources. |
| 83 | NOTE | L4-02 | slide 3; Q6 | "Never, by rule: Cell phones; anything alive; rent-to-own; altered serials; anything leaking; big appliances" | Verified §04.05 (lesson omits pornography/adult toys/paraphernalia/non-functioning firearms — acceptable in a Level 4 steer lesson; "the rest of the list" is referenced). | P&P §04.05. |
| 84 | NOTE | L4-02 | slide 1 b1 "Guns" | Telling a Level 4 trainee to steer customers to bring guns | GATE line correctly says the trainee may *say* it but not transact until Level 6. No conflict. | L4-02 GATE. |

## L4-03 — Making the offer

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 85 | NOTE | L4-03 | slide 3; Q7 | Pressure washer: comps 180/200/210 → $200; target ≈ $100; open buy $80, loan $60. Miter saw: 140/150/160 → $150; target $75; open ≈ $60; "$110 is over 70% of resale, under 30% margin" | Recomputed: mean $196.7 ≈ $200 ✓; $110/$150 = 73% → 27% margin ✓ (flag line). All correct. | Arithmetic. |
| 86 | NOTE | L4-03 | slide 5 b1 + say; M-03 slide 5 | "Thirty dollars overpaid a day at each store is about forty thousand a year" | $30 × 5 stores × ~300 open days ≈ $45k; × 6 days/wk × 52 ≈ $47k. "About forty thousand" is Preston's rounding — acceptable as an order of magnitude; do not tighten (it's narration). | KB overpaying-math. |
| 87 | NOTE | L4-03 | slide 7; Q5; Q6; Q8 | Worksheet $1,000+ incl. reloans; detailed notes + photos + loyalty report; metals need resale and melt; title pawns CEO at any amount | Verified §01.10, §04.04, KB entries. Correct. | P&P §01.10, §04.04. |
| 88 | SHOULD-FIX | L4-03 | slide 4 b5 + say | "Set category percentages: bows and crossbows off-season 25% of resale, muzzleloaders 40%" | The lesson's own sources flag the crossbow figure as Jan-2024 and off-season only, with "in season" unstated — but the slide states it as a standing rule with no season caveat in the narration ("Bows and crossbows off season, twenty five percent"). Fine as narrated; bullet is fine. Just confirm with Preston before launch; if retired, this is a bullet + one narration sentence. | L4-03 sources OPEN (bows-crossbows-25-percent). |

## L4-04 — The pull list, pricing the floor, markdowns

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 89 | MUST-FIX | L4-04 | slide 4 b4; KEY_POINTS 5; Q7 why | 30% ceiling / 50% cap with no 31–50% approver | See X9. | Brief; M-03. |
| 90 | NOTE | L4-04 | slide 1 | "Count from the day after the due date. That's day 1 past due" | See X10 (P&P sentence to fix). | P&P §06.01. |
| 91 | NOTE | L4-04 | slide 4; Q4; Q5; Q6 | eBay 90/120/150, 30% floor; in-store aged = 1 year, GM 25%/month then clearance, jewelry 30% + 6-month clearance then scrap; by the 15th; metal never repriced online | All verified against §5A and §06.03 and consistent with M-02. Q5 (designer 14k on eBay at day 150 → manager's decision, no cut) matches §5A rule 2 as in force; sources correctly note the HUDDLE F5 question is Joshua's to rule. | P&P §5A, §06.03. |
| 92 | NOTE | L4-04 | slide 2 b4 | "The law won't let us sell a pawned item without one [statement of ownership], however long it's been" | Verified § 54.1-4005. Correct. | Va. Code § 54.1-4005. |

## L4-05 — Ownership, red flags, police, the daily report

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 93 | SHOULD-FIX | L4-05 | slide 1 b2 + say | "Unexpired photo ID with their current address. Imaged." / "an unexpired photo I D showing their current address" | L3-02 (and the statute) allow an ID with an old address plus other proof of current address. L4-05 states "current address" as absolute; a trainee who passed L3-02 Q1 ("A second document fixes an out-of-date ADDRESS") now hears the opposite. Bullet 2 → "Unexpired government photo ID. Old address on it? Other proof of the current address too." Narration can stay (it is not wrong, just incomplete). | Va. Code § 54.1-4009; P&P §05.00A; L3-02 slide 2; L4-05 sources OPEN (review 2026-10-14). |
| 94 | NOTE | L4-05 | slide 4; Q5 | LE: credentials → admit immediately → records and item → receipt → notify Preston and Joshua in parallel | Verified § 54.1-4011 (receipt requirement is statutory) and §01.06. Correct. | Va. Code § 54.1-4011; P&P §01.06. |
| 95 | NOTE | L4-05 | Q2 distractor 3 why | "Altering an item to read a serial number isn't allowed" | Verified § 54.1-4012 (property not to be disfigured) and §09.05. Correct. | Va. Code § 54.1-4012. |
| 96 | SHOULD-FIX | L4-05 | Q8 correct option | "Someone who's brought in stolen goods before" | §01.10 says "known to be a thief or convicted of larceny, burglary or robbery". A customer who once unknowingly brought in a stolen item (it happens; the police took it) is not "known to be a thief". The option is defensible as written but a sharp learner can argue it. Change to "Someone known to be a thief, or flagged in Bravo as one" (quiz-only edit). | P&P §01.10. |
| 97 | NOTE | L4-05 | slide 5 b4 | "'Silver bullion, quantity one' fails the report" | Good practice; § 54.1-4010 requires "a description of each item". Correct. | Va. Code § 54.1-4010. |

## L4-06 — Employee purchases and family

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 98 | NOTE | L4-06 | all slides; Q1–Q7 | 90 consecutive days; form fields; Preston AND Joshua; separation of duties; Bravo note; firearms 4473 by another employee; no holds; restricted categories; family approval by Joshua in advance | Verified line-by-line against §05.10 §§1–10 and §01.10. Q1 distractor 1 ("past the 30-day mark") correctly retires the KB 30-day draft. No findings. | P&P §05.10, §01.10. |
| 99 | NOTE | L4-06 | slide 3 b4 | "Your thirty percent counter discount is for customers. It doesn't apply to you" | Consistent with M-03 Q7. Correct. | P&P §05.03 vs §05.10. |

## M-00 — Welcome to the Manager Track

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 100 | NOTE | M-00 | slide 1 b3 | "Weekly layaway review and the loan timeline" | Correctly reflects the retired weekly loan review (10/14). No findings. | Brief. |

## M-01 — Weekly layaway review and the loan timeline

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 101 | **BLOCKER** | M-01 | slide 4 b5 + say; KEY_POINTS 4; Q7 (prompt, correct option, all whys) | "Never made a first payment? No 30-day hold — expire it as soon as it's past due, any amount" / Q7: loan "written five weeks ago… Expire it now" | See X8. A manager acting on "expire it now" at day 5 past due can pull/sell inside the statutory 15-day grace. The associate lessons say the opposite. Blocker because it is a legal line and a manager-vs-associate contradiction on the same rule. | Va. Code § 54.1-4005; P&P §05.01, §06.01. |
| 102 | NOTE | M-01 | slide 2–3; Q1–Q3 | Four layaway numbers; store credit on expiry; tag removed in Bravo; Locate = 0 → Preston same day; Q2 (10-month jewelry layaway, 64 days no payment → expire) | Verified §05.05 (jewelry tier up to 10 months; 60-day rule runs alongside term). Correct. | P&P §05.05. |
| 103 | NOTE | M-01 | slide 4 b6; Q8 | "A renewal payment resets the due date; count from the latest due date in Bravo" | Correct in substance (§05.01: paying the finance charge "enter[s] a new 30-day loan"). OPEN on the Bravo field name stands. | P&P §05.01. |
| 104 | NOTE | M-01 | Q5 | 63 days past due, promise to pay Friday → "Pull it, or get Joshua's approval to hold" | Correct (§06.01). Good distractors. | P&P §06.01. |

## M-02 — Aged inventory and the pricing queue

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 105 | NOTE | M-02 | slide 2; Q1; Q3 | GM 25% then clearance (deeper = manager's call, ≤50%); jewelry 30%/6 months/scrap; markdowns don't stack; done = repriced AND moved | Matches §06.03 and the 10/14 default D24. The "does 25% compound monthly" question is still Preston/Joshua's; §06.03 literally says "25% markdown per month". Not re-litigated. | P&P §06.03; ACADEMY_REVIEW D24. |
| 106 | NOTE | M-02 | slide 4; Q2; Q6 | Metal never repriced online; melt-priced metal never below melt anywhere; reprice UP when spot rises | Verified §5A rule 2 and KB spot-price-rising-action. Correct; consistent with L4-04. | P&P §5A. |
| 107 | NOTE | M-02 | slide 6 b4; Q4 | "Best Offer never gets switched on… Ending a listing? Update the item's status in Bravo" | Verified §5A rules 1 and 4. Correct. | P&P §5A. |
| 108 | NOTE | M-02 | Q7 | Item of the Day approved by Preston (item and price) | Verified §06.02. Correct. | P&P §06.02. |

## M-03 — Discount and margin reviews

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 109 | NOTE | M-03 | slide 2 b1 | "Between 30% and 50% needs a manager" | The only place in Levels 1–4/M where the 31–50% approver is stated — see X9 to copy it into L4-04. Who the "manager" is (Store Manager?) is still OPEN; the 10/14 recommended default (Store Manager on the ticket) is fine. | Brief; M-03 sources OPEN. |
| 110 | NOTE | M-03 | Q2; Q5; Q1 | $200 → $90 = 55% off ✓; $330 buy vs $336 comps: 50% target ≈ $168–170 ✓, 30% flag line = $235 ✓; $55 off ≈ 14% ⇒ ticket ≈ $393 ✓ | All arithmetic recomputed and correct. | Arithmetic. |
| 111 | NOTE | M-03 | Q3; Q6 | Storewide sale excludes clearance jewelry, coins, bullion; sales tax on every deal, no out-the-door pricing | KB-sourced; consistent. Virginia sales tax must be collected on retail sales — "out the door" pricing that absorbs tax is lawful only if tax is still remitted; the KB rule avoids the margin loss and the ambiguity. Fine. | KB bullion-coins-discount-exclusions; Va. Code § 58.1-603. |
| 112 | NOTE | M-03 | slide 6 b3 | "Something that breaks a hard limit (over 50% off, self-rung purchase) goes to Preston" | Consistent with §05.03/§05.10 and §09.07. Correct. | P&P §05.03, §05.10. |

## M-04 — Running the coaching huddle

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 113 | NOTE | M-04 | Q3 | Associate confirms a pistol on loan to an unverified caller → "Call Preston today, then talk to him privately" | Consistent with L1-05 rule 2 and §09.07 ("a firearm transaction raises any doubt at all"). Correct. | P&P §09.07; L1-05. |
| 114 | SHOULD-FIX | M-04 | Q7 prompt | "In the huddle an associate asks, 'Whose call was that bad one?'" | The lesson teaches that bad calls are NOT played in the huddle (Q1, Q2: "teach the rule, no names"). A manager who follows the lesson never plays a "bad one", so the prompt implies a huddle the lesson forbids. Reword: "In the huddle, after you teach a 'do this instead' pattern, an associate asks, 'Whose call was that?'" — quiz-only edit. | M-04 slides 3–5. |
| 115 | NOTE | M-04 | slide 1 b4; Q4 | "Fifteen minutes a week" | Huddle day/slot still OPEN; taught as paid time. No conflict with §12.01 (team meeting is a different event). | P&P §12.01. |

## M-05 — Onboarding a new hire

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 116 | MUST-FIX | M-05 | slide 2 (bullets + say); slide 6 ("first-week rhythm"); KEY_POINTS | Day-1 list: "I-9… acknowledgment… clock-in… Preston sets up Slack, #ask-handbook, Chekkit and their Bravo login… Academy… shirts" | OB-2026-01 Rev 2 (October 1, 2026 — the version in `sources/`) added three NEW rows the lesson does not teach: Day 1 "Enrolled in NRF RISE Up Customer Service & Sales course; login email received (HR-2026-10)"; Day 1–7 "Customer Service & Sales course completed… time reported to manager and added to Gusto hours as paid time"; By day 7 "Training time entered in Gusto… 10-minute sales role-play at the counter passed". A manager lesson titled "run a new hire's first ninety days from the checklist" that omits a third of the checklist's first-week rows will produce managers who skip them. Add one bullet to slide 2 ("Enroll them in the RISE Up sales course — HR-2026-10") and one to slide 6 ("By day 7: RISE Up course done, time in Gusto, ten-minute sales role-play passed"). Narration: one sentence each (≈ 200 characters). | OB-2026-01 Rev2 rows "NEW"; Valley_Pawn_Sales_Training_HR-2026-10.txt. |
| 117 | BLOCKER | M-05 | slide 2 b4 | "Preston sets up Slack, #ask-handbook, Chekkit and their Bravo login" | See X2 (narration already says "the handbook assistant" — bullet only). | Brief. |
| 118 | NOTE | M-05 | slide 4 b4; Q8 | "No firearm transaction until Level 6 + its Floor Checks + certificate verified — and the State Police employee check is done" | Verified Va. Code § 18.2-308.2:3 (dealer employees who transfer firearms must pass a VSP criminal-history check) and §10.06. Correct and important. | Va. Code § 18.2-308.2:3; P&P §10.06. |
| 119 | NOTE | M-05 | slide 2 b1; Q1 | "I-9 Section 2 in person, with the ORIGINAL documents. Deadline: 3rd business day" | Correct (8 CFR 274a.2(b)(1)(ii) — within three business days of the first day of employment; "alternative procedure" remote inspection is available only to E-Verify employers, so "in person, originals" is right for Valley Pawn). | 8 CFR 274a.2. |
| 120 | NOTE | M-05 | slide 1 b3 | "Drug screen passed (includes THC)" | Lawful in Virginia for pre-employment (Va. Code § 40.1-27.4 protects only lawful medical cannabis-oil use with a written certification; the firearms-handling prohibited-person rule in §10.06 independently bars unlawful marijuana users under 18 U.S.C. § 922(g)(3)). No change. | Va. Code § 40.1-27.4; 18 U.S.C. § 922(g)(3); P&P §10.06. |
| 121 | NOTE | M-05 | slide 4 b6; Q6 | "Keys: 90 days AND Certified (Level 7 complete), with Preston's approval" | OPEN keys conflict stands (OB-2026-01 and §10.02 allow pre-90-day keys with MM approval). Lesson teaches the stricter rule — acceptable; not re-litigated. | P&P §10.02; OB-2026-01. |
| 122 | NOTE | M-05 | Q7 prompt | "'I closed with Dana last night…'" | Fictional coworker name in learner text. The spec example itself uses "Mike Davis", so fictional names are tolerated — but "Dana" is a common enough first name that a real employee may share it; "a coworker" costs nothing. | LESSON_SPEC rule on anonymised stories. |

## M-06 — Running a fair Floor Check

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 123 | NOTE | M-06 | slide 4; Q4 | "handing a redeemed firearm back before the State Police check is obtained… Stop it now" | Verified §05.01 (redemption is a transfer; VSP check before release; 18 U.S.C. § 922(t)). Correct and the right example. | P&P §05.01; 18 U.S.C. § 922(t). |
| 124 | NOTE | M-06 | Q6 | "$10 short… handled exactly as the lesson says → Pass" | Consistent with L2-03 FLOOR_CHECK text ("If the drawer is over or short, the manager confirms the trainee recounted, researched, called Preston…"). Correct. Distractor 3 why cites Va. Code § 40.1-29 — correct (no wage deduction for shortages absent a signed authorization; company bars it outright). | L2-03 FLOOR_CHECK; Va. Code § 40.1-29(D). |
| 125 | NOTE | M-06 | slide 2 b4 | "Step not coming up on the real shift? Observe two clean counts, or stage a planted discrepancy" | Unwritten but sensible; a planted discrepancy must be documented so it never reads as a real shortage in Bravo — add "(tell Preston first, and never enter a planted variance in Bravo)" to the bullet. | M-06 sources OPEN; P&P §02.08 (documentation in Bravo). |

---

## Count

- BLOCKER: 4 distinct issues (X1 hours / Saturday 5 PM; X2 #ask-handbook → #ask-goldilocks; X3 "Goldilocks doesn't answer questions"; X8/101 first-payment default "expire it now" inside the statutory grace) — touching 11 lesson locations.
- MUST-FIX: 12 (X4 three-vs-four talking points; X5 "Have you ever been here before?"; X6 spouse/attorney wording; X7 bot-first vs manager-first; X9 31–50% approver in L4-04; 5 "service charge"; 15 closed-day deadline rule; 61 police-report failure routing; 65; 70; 89; 116 NRF RISE Up rows missing from M-05).
- SHOULD-FIX: 21 (7, 8, 11, 22, 24, 28, 33, 41, 44, 49, 53, 58, 66, 72, 75, 82, 88, 93, 96, 114, 125).
- NOTE: 1 cross-cutting (X10) + 61 lesson-level, including ~40 explicit "verified, correct" confirmations so the authors know what was checked.
- Total rows: 135 (10 cross-cutting + 125 lesson-level).

## Verdict

**Launch after fixes — not ready as it stands.** The pawn-law substance in Levels 1–4 and the Manager Track is strong: every Virginia charge cap, the 45-day floor, the record fields, the ID/military-ID rule, the noon police-report deadline, the law-enforcement access/receipt rule, Form 8300, TILA and the 4473/VSP redemption rule all check out against the current Code and P&P, and the loan timeline is stated identically in L3-01, L3-06, L4-04 and M-01. What stops a launch is operational, and all of it is cheap: (1) the store hours and closing time are stale against the 10/1 change in four lessons including a customer-facing quiz; (2) twenty-three learner-facing references to #ask-handbook, a channel being retired the day the course goes live, plus L1-07 teaching that Goldilocks "doesn't answer questions"; (3) one legal contradiction between the associate and manager tracks on first-payment defaults (M-01 tells a manager to "expire it now" at day 5 past due with no mention of the 15-day statutory floor — fix the wording before any manager acts on it); (4) three rules stated two ways across levels (three vs four talking points, account-holder vs spouse/attorney, who approves 31–50% off). None of these needs more than a handful of narration lines (my estimate ≈ 900 characters total if X2, X3, X4, 5 and 116 are all re-recorded; everything else is bullet/quiz text). Fix X1–X9, 5, 15, 61 and 116, then it is launch-ready from a compliance and pawn-practice standpoint.
