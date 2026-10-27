# Valley Pawn Academy: open items

This list merges every `OPEN:` line in the `sources` of all 51 lessons (L1–L8 and M), with duplicates removed. Compiled 2026-09-28. It's meant to be taken to Preston in one pass. Items that need a CEO decision or sign-off are listed separately under Joshua.

Each item gives the lesson ids it affects. When an item is answered, update those lessons and delete the `OPEN:` line from their `sources`. Nothing marked OPEN is tested in the quizzes unless the item says otherwise.

**Also read `HUDDLE_INPUTS.md`** (2026-09-28): lesson additions and 6 hard flags harvested from every Slack huddle. Its F1–F6 flags belong with Part 1/Part 2 below when this file is next regenerated.

Resolved since the last pass: layaway down payment and term. P&P v2026.8 §05.05 states the three tiers, "Confirmed by Joshua Davis (CEO), 2026-09-23". L7-02 now teaches and tests them.

**2026-10-25 — Market Manager 10/23 answers, drafts awaiting his sign-off (not in the live lessons yet):** `drafts_for_preston_20261025/` holds L7-03 (no want-list: take name + number and call when one comes in; police/ATF callback line: name, badge, department, call back on the department's main number, tell the Manager; greeting confirmed), L3-06 (teaching unchanged; stale source notes fixed: grace → 15-day legal hold, late fee 5% of principal from day 6, verification and first-payment default resolved) and L4-02 (source note: no want-list). On sign-off, copy them over `lessons/` and `lessons_target_20261028/` (back up first) before the next voice/upload pass. Paired P&P draft: Human Resources/DRAFT_Phone_Policy_Updates_for_Preston_2026-10-25.docx.

---

## Part 1: Questions for Preston

### Onboarding, HR and systems
- **P1.** Gun-safety certificate: what's the one way it gets paid for (store card, or Preston buys it)? HR-2026-05 §4 says "directly or by reimbursement". P&P §10.06 says the Company buys it directly. *(L1-03)*
- **P2.** Publish the Slack channel map: which channel for deals, store questions, schedule swaps and call-outs. Only #policy-announcements, #supply-request, #ask-handbook and #general are documented. *(L1-04)*
- **P3.** For each platform (Slack, Gusto, the Academy), is the login the store email or a personal one? *(L1-04)*
- **P4.** Dress code: is "may be sent home unpaid to change" applied consistently? *(L1-02)*

### Cash, opening and closing
- **P5.** Mid-day drawer balance: what time, is there a witness, and is it entered in Bravo or kept on paper only (§02.07, §12.04)? *(L1-06, L2-03)*
- **P6.** Alarm: who holds the code, and what are the opening disarm routine and the closing arm routine (exit delay)? What do staff do on an alarm event, a fault, or a panel that won't arm? *(L2-01, L2-02)*
- **P7.** Opening walk: the order for the outside look, back door, lights, HVAC, sign and front door. *(L2-01)*
- **P8.** Which mornings involve a bank run, and who goes (§02.03)? *(L2-01)*
- **P9.** Put the Slack funds-request flow in writing: who may request, the wording, who enters BANK→SAFE in Bravo, and the cut-off time for a same-day transfer. The lesson currently uses "before close, same day" because the automated check runs at 6 PM ET. *(L2-04)*
- **P10.** Long-gun overnight storage at close (rack, cable, back room or safe). §12.03 defers to §04.02 and §10.06, and neither section states it. *(L2-02)*
- **P11.** Night deposit: does it go to the bank the same evening or stay in the safe for the morning run, and who carries it? *(L2-02)*
- **P12.** At each store, who has the safe combination, and who is the "designated employee" on a manager's day off? *(L2-04)*
- **P13.** Daily jewelry count:
  - who is the designated teammate at each store, and who counts when the scheduled person is out;
  - is there a store-level variance tolerance;
  - are watches, loose stones, coins/bullion or the scrap bucket counted? *(L2-05)*

### Pawn loans
- **P14.** What interest and storage percentages is Bravo configured to charge? Should trainees know the numbers? *(L3-01)*
- **P15.** Paydowns and partial payments:
  - how a payment toward principal is taken in Bravo;
  - whether a payment smaller than the finance charge or the extension is ever accepted;
  - whether payments can be taken by phone (Call 127 said no, use the app). *(L3-01, L3-05, L3-06)*
- **P16.** The late-fee rate Bravo actually applies and the day it starts. Calls quote "5% of principal" and a "five-day" window. The P&P says only "up to 10%" and "if disclosed". *(L3-06)*
- **P17.** First-payment defaults. §06.01 says they're "expired as soon as past due", but §05.01 says nothing may be sold before term plus 15 days.
  - What does "expired" mean inside that window?
  - What is the customer told, and may staff say "your stuff is safe"?
  - Is the old KB rule "if it's a good customer, call them and get that payment" still expected? *(L3-01, L3-06, M-01)*
- **P18.** Does an extension ever need approval? The v2026.7 changelog promises "one approver for extensions", but no section names one. *(L3-05)*
- **P19.** Retire the 2025-02-10 KB rule and your Slack rule that the Large Loan/Buy Worksheet isn't needed for reloans. P&P §01.10 includes reloans. *(L3-02, L8-02)*
- **P20.** Large Loan/Buy Worksheet: who confirms or approves it now, who's the backup when you're away, where it's sent, and does any amount also need Joshua? *(L3-02, L4-03)*
- **P21.** A customer photo on every intake is your KB rule. The P&P requires it only for military ID. Should it go into the P&P? *(L3-02)*
- **P22.** Does the Academy's "ten required fields" grouping of §05.00A match what Bravo highlights? Which fields does Bravo fill automatically, and which does the employee enter? *(L3-03)*
- **P23.** What happens when a customer refuses the fingerprint §05.01 requires? *(L3-04)*
- **P24.** Phone verification:
  - which non-public identifiers can actually be checked in Bravo at the counter (ticket number, DOB, last four of the phone);
  - is any voicemail ever left on non-reminder calls (§08.01 bars them on reminder calls);
  - when a delayed firearm check resolves, who calls the customer and by what channel? *(L1-05, L6-03)*

### Buying, pricing and inventory
- **P25.** Does buy-above-loan still stand for general merchandise, given Joshua's 2025-11-11 direction that gold buy and loan "can be equal"? *(L4-01)*
- **P26.** Publish general-merchandise loan and buy percentage bands by category, or confirm that sold comps plus negotiation is the whole method. *(L4-01, L4-03)*
- **P27.** The Bravo "customer loyalty report": its exact name, menu path, what it shows and how to read it. *(L4-01, L7-04)*
- **P28.** Is the 2023-12-18 steer list still current (electric drum sets, lawn equipment)? Name the current new-gen console list (PS5 / Xbox Series / Switch 2?). *(L4-02)*
- **P29.** The want-list: where it lives (a Bravo field, Slack or a sheet) and the store procedure. *(L4-02, L7-03)*
- **P30.** Buying a titled vehicle outright (4-wheelers, dirt bikes, motorcycles): what's the approval path? §04.04 covers title pawns only. *(L4-02)*
- **P31.** Does bows and crossbows at 25% of resale off-season (Jan 2024) still hold? What's the in-season number? *(L4-03)*
- **P32.** How is a general-merchandise retail price set at pricing time: a percentage of sold comps, or Bravo's suggested price? *(L4-04)*
- **P33.** Record the Bravo clicks for moving an expired loan to Pull From Inventory and printing SKU and price tags. *(L4-04)*
- **P34.** Jewelry scrap timing. Retire the conflicting KB entries: 2 years (Jan 2024), 1 year + 6 months (Jul 2024) and 1.5 years (2025–26). P&P §06.03 is what's taught: 30% off at 1 year, 6 months in clearance, then scrap. *(L4-04, L5-03, M-02)*
- **P35.** The statement-of-ownership wording, and where the customer signs it in Bravo. *(L4-05)*
- **P36.** Where the Employee Purchase Request Form lives (Gusto, Drive or paper) and how it's submitted. *(L4-06)*

### Gold, silver and diamonds
- **P37.** Does any store have, or will any store get, an XRF analyzer? *(L5-01)*
- **P38.** The acid set: which acid for which karat, how deep to scratch, and how to read the result. *(L5-01)*
- **P39.** Gold-filled, plated and vermeil stamps (GF, HGE, RGP, 1/20) and the file-a-notch test: confirm before they're taught. *(L5-01)*
- **P40.** The Kee pen replacement: what does each store use today? *(L5-01)*
- **P41.** Current gold buy and loan tiers. The last figures on record are an estimator loan of 50% and buy of 55% (Nov 2025), with Joshua directing the buy down 5–10%. A conflicting note says "no more than 65–70%". *(L5-02; see also P25)*
- **P42.** The karat purity table for 10K, 18K, 22K, 24K, sterling and 90% coin silver. Only 14K = 0.5833 is sourced. *(L5-02)*
- **P43.** Grams or dwt: which unit do the store scales display? What's the conversion? *(L5-02)*
- **P44.** What is the "spot sheet" physically (a printed sheet, Coinapps or the Bravo estimator), and who updates it? *(L5-02)*
- **P45.** Does the gold melt formula structure apply to silver and platinum, with their own purity decimals? *(L5-02)*
- **P46.** The silver and platinum scrap bucket name format (e.g. "2026-08 SILVER"). *(L5-03)*
- **P47.** At intake, who decides whether a sellable piece goes to scrap or into the case? *(L5-03)*
- **P48.** Approve or cut the 4Cs vocabulary slide. *(L5-04)*
- **P49.** Diamond tester: the model at each store, the calibration steps, and what a pass or fail looks like. A bench video or written steps would work. *(L5-04)*
- **P50.** Diamonds beyond the basics (the "diamond ladder" session):
  - the carat threshold for a "large stone" that goes to you;
  - how to detect moissanite and lab-grown stones, and what we pay for them;
  - how to estimate the carat weight of a set stone, and how to enter the stone-weight breakout in Bravo. *(L5-04)*
- **P51.** Watches and designer items:
  - the authentication procedure (tells, box and papers, serial and reference checks, opening the case, third-party authentication) and who approves;
  - the store's dollar approval authority for high-end items below the $1,000 worksheet line. *(L5-05, L8-02)*
- **P52.** Coin counterfeit tells beyond magnet, weight and Sigma (spec weights and diameters, ping test, reeding, known-fake dates). *(L5-05)*
- **P53.** The customer script when an item tests fake. Is the item ever held, or are the police ever called? *(L5-05)*
- **P54.** Non-metal brands with high counterfeit risk (Benchmade, Gibson): confirm them for a Level 4 or Level 8 brand lesson. *(L5-05)*

### Firearms
- **P55.** The A&D record at each store:
  - is it Bravo's electronic book, paper, or both;
  - who may make entries;
  - how an entry is corrected, including fixing a misclassified firearm "in both the system and the gun log". *(L6-01)*
- **P56.** Which supplemental address documents are accepted (they must be government-issued under 27 CFR 478.124)? *(L6-02)*
- **P57.** Which 4473 revision each store stocks, and whether Bravo or an e-4473 tool is used. *(L6-02)*
- **P58.** A handgun buyer whose ID shows an out-of-state residence: decline, or ship to an FFL in their state? *(L6-02)*
- **P59.** The Section D recertification procedure when a delayed check is picked up on a later day. *(L6-02)*
- **P60.** How long a State Police approval or a pending delay stays usable before a new 4473 and check are needed. *(L6-03)*
- **P61.** Terminology. Conform "NICS" in §04.02 and §05.05 to "Virginia State Police check" (§05.01). Is the "NICS fee" in KB transfer-firearm-accounting the same $25/$10 transfer-fee line in Bravo, and should its label change? *(L6-03, L6-04)*
- **P62.** The exact VCheck on-screen response labels, to confirm when you record the walkthrough. *(L6-03)*
- **P63.** A box arrives from a non-dealer, with no FFL copy inside, or addressed to an unexpected name. What's the procedure? *(L6-04)*
- **P64.** May a verified buyer be told by phone that "your transfer has arrived"? *(L6-04)*
- **P65.** Which Bravo step records the transfer OUT to the buyer (a $0.00 sale plus the fee)? *(L6-04)*
- **P66.** Firearm loan-amount guidance beyond "don't loan high to new customers". *(L6-05)*

### Selling, phones and service
- **P67.** One or two real pitch examples (benefits first, then specs) to replace the generic ones. *(L7-01)*
- **P68.** Clearance is the fourth talking point in your daily reminder, but §07.04 lists three. Add it to the P&P or confirm three. *(L7-01)*
- **P69.** Warranty wording:
  - align §07.04's "everything we sell" with §05.08's exclusions (firearms, ammunition, consumables);
  - define "consumables". *(L7-02)*
- **P70.** A defect that existed at sale but was found after day 30 (queue #10). Is there a rule beyond "manager review"? *(L7-02, L7-07)*
- **P71.** Confirm or replace the inbound greeting script ("Thank you for calling Valley Pawn in [town], this is [name]…"). *(L7-03)*
- **P72.** The role-play sim's scoring rubric and pass mark. *(L7-03)*
- **P73.** Who responds to a negative Google review, and what does an associate do when a customer threatens one? *(L7-04)*
- **P74.** Chekkit:
  - the approved transactional templates (§07.06);
  - where in-person opt-ins are recorded, and whether Chekkit's settings capture consent;
  - is texting loan status or due dates to the number on file without verification allowed? *(L1-04, L7-04)*
- **P75.** The eBay listing workflow:
  - whether items are listed from Bravo or from Seller Hub;
  - the Bravo status or location that marks an item "on eBay";
  - photo setup;
  - who sets Promoted Listings rates. *(L7-05)*
- **P76.** eBay shipping:
  - who packs and ships at each store, the carriers, and each store's handling time;
  - the Bravo step that takes a sold item out of availability;
  - the dollar threshold for signature confirmation and extra insurance. *(L7-06)*
- **P77.** Authority to make things right: who may waive which fees (queue #14), and what an associate may offer on their own (comps, credits). *(L7-07)*
- **P78.** Confirm the framing for "protect a vulnerable customer" (Call 88) next to "negotiate every deal". *(L7-07)*
- **P79.** Call 37/39: the audio is tagged WAY, but the employee says Lexington. Confirm the store before the clip is labeled. *(L7-07)*

### Title pawns, privacy and texting
- **P80.** Title pawn value source: confirm the one source, and which Black Book figure the 40% target and the 50% ceiling run off. *(L8-01)*
- **P81.** Title pawn paperwork:
  - is the spare key kept for the life of the loan, and where;
  - who files the DMV lien recordation and releases it at redemption, and are there DMV fees;
  - is the Excel Collections Log (§03.08) still in use? *(L8-01)*
- **P82.** Where a do-not-call request is recorded in Bravo, and how the written internal list is kept. *(L8-05)*

### Manager track
- **P83.** An overdue layaway (past its final payment date) whose customer is still paying monthly: expire it, extend it, and who approves? *(M-01)*
- **P84.** When and where do managers actually receive their store's weekly loan and layaway numbers? *(M-01)*
- **P85.** The §06.03 general-merchandise markdown of 25% per month:
  - does it compound, and is there a floor;
  - how does it square with §05.03's 50% cap and "even if it is a loss"? *(M-02)*
- **P86.** Is the 2024 "Blowout tag, keep the original tag on" clearance procedure still current? *(M-02)*
- **P87.** Daily discount, margin and intake flags:
  - what should the manager do with each one (reply in the channel, note it in Bravo, or only act on request);
  - which intake-margin post do stores see in #pawn-walks, and at what time? *(M-03)*
- **P88.** The weekly huddle: when, where (in store or the §12.01 Zoom), and how long? Who picks the Call of the Week? *(M-04)*
- **P89.** Floor Checks:
  - who may sign one (Store Manager only, or an assistant manager or MIT too);
  - how many redos before it escalates to you;
  - is a failed check logged anywhere? *(M-05, M-06)*
- **P90.** Add an Academy line to OB-2026-01: login on day 1, Level 1 by day 3, and the Level 6 and Certified sign-offs. *(M-05)*

---

## Part 2: Decisions and sign-offs for Joshua

(Where the source says "Preston/Joshua", the item is listed here if it's a policy decision, with Preston's input noted.)

### Policies to adopt in writing
- **J1.** Adopt the proposed phone standards into P&P §07.03 and send them for Gusto e-signature:
  - POLICY_GAPS #1: verify with name plus one non-public identifier;
  - #2: never confirm a firearm by phone, and voicemails say only name, store and callback number;
  - #3: no metal number without the spot sheet and the item identified;
  - #4: every sell-side call ends with a range, a time, or a name and number;
  - queue #6: stolen-property calls.

  The lessons already teach these as the Academy standard. They should be adopted before company-wide assignment. *(L1-05, L3-05, L3-06, L4-03, L4-05, L5-02, L6-03, L6-04, L6-05, L7-03)*
- **J2.** Adopt, or edit, the grace, late-fee and expiration call script (queue #7) as the written script. *(L3-06; with Preston)*
- **J3.** Put the "we're Valley Pawn, never 'Dixie Pawn'" rule in writing, for example a line in §07.03. *(L1-01; with Preston)*
- **J4.** Adopt Google-review rules into §07: ask everyone, no incentive, no reviews by employees or family, never write one for a customer. Note them beside the bonus review goal. *(L7-04; with Preston)*
- **J5.** Adopt the Floor Check standard ("watch, don't coach during" and the pass/redo rule) as a short §12 addition or a Master Plan line. *(M-06; with Preston)*
- **J6.** Write the police-hold procedure: how a hold is placed and flagged in Bravo, how long it lasts, who releases it, and on what paperwork. Firearms included. *(L4-05, L6-05; with Preston)*

### Academy gates and HR
- **J7.** Confirm the Master Plan v2 Academy gates as the standard. If any gate changes, edit M-05 questions 4, 5, 6 and 8. *(M-05)*
- **J8.** HR-2026-05 makes only the gun-safety certificate a day-3 condition, while the Master Plan extends day 3 to all of Level 1. Confirm the wording, then send HR-2026-05, which is built but not sent. *(M-05)*
- **J9.** Keys conflict. OB-2026-01 and §10.02 allow keys before 90 days with Market Manager approval. The Master Plan says 90 days AND Certified. Reconcile them. *(M-05; with Preston)*
- **J10.** Should the Virginia State Police dealer-employee check (§10.06) be an explicit Academy gate for Level 6, and who tracks it? *(L6-01; with Preston)*
- **J11.** Set recert due dates for the annual courses. Only gun safety has one: Jan 31, HR-2026-05 §7. *(L8-03, L8-04, L8-05)*
- **J12.** Re-render HR-2026-04 before the send: §1 still names Handbook v2026.4, and the current Handbook is v2026.5. *(L1-02)*
- **J13.** What does an employee do when a customer or vendor harasses them? The Handbook covers only harassment between employees. *(L8-03; with Preston)*
- **J14.** May a MEDIUM conduct clip with an identifiable coworker be played to the whole team, or only one-on-one? The lesson teaches one-on-one. *(M-04; with Preston)*

### Operating decisions
- **J15.** Title pawns: are they actively offered, and exactly what do staff tell a caller who asks? Call 241 said "we don't do title loans". If they're not offered, retire L8-01. *(L3-04, L8-01; with Preston)*
- **J16.** Delayed firearm transfers: does Valley Pawn ever release on a delay without an approval after the State Police's fifth business day? Who decides, and how is it documented? *(L6-03; with Preston)*
- **J17.** The loan side of the weekly review after 2026-10-01, when §06.01 retires the 75-day / 5% measure. What numbers does it report (e.g. anything past day 61 without CEO approval)? *(M-01; with Preston)*
- **J18.** Who may approve a sale discount between 30% and 50%? §05.03 sets the limits but names no approver. *(L4-04, L7-01, M-03)*
- **J19.** Employee transactions:
  - does §01.10 cover an employee personally buying from a customer outside the store's buy process;
  - on an approved family transaction, may the related employee process it? *(L4-06; with Preston)*
- **J20.** Bullion at 50%: confirm the basis. Your 2026-02-02 reply said "50 percent of current spot". Is that spot or melt? *(L5-02)*
- **J21.** eBay operations:
  - which stores list what, and a higher intake floor for sub-$50 items (L7-05);
  - return shipping (buyer pays today) and whether to ship internationally (L7-06);
  - Top Rated Plus: 1-day handling and free returns over $100 (L7-06).
- **J22.** Automated texts:
  - confirm that the Friday past-due and coming-due reminder texts and the weekly Chekkit review-request campaign to inactive customers each have the consent they need as marketing or transactional messages. *(L8-05; with Preston)*

### Privacy and data security
- **J23.** GLBA. State the Company's obligations:
  - the FTC Safeguards Rule written information security program;
  - the Qualified Individual;
  - the risk assessment;
  - the customer privacy notice. *(L8-04; with Preston)*
- **J24.** Are ID images and Bravo/Chekkit data encrypted at rest? The answer decides whether Va. Code § 18.2-186.6 applies to "unencrypted personal information". *(L8-04)*

---

## Part 3: Notes, not questions

These are recorded so no `OPEN:` line is lost. No decision is needed:
- Firearm-specific pawn fields and A&D steps are deliberately left to Level 6. *(L3-03)*
- The Handbook has no numbered sections, so lessons cite it by heading. *(L8-03)*
- The 20%/$50, 25% and 30% discount-flag lines are report settings, not P&P policy. Only §05.03's 30% and 50% are policy, and the lesson says so. *(M-03)*
- Culpeper and Roanoke get no coaching pack until their Zoom Phone ports land. *(M-04)*
- The Slack ✅ → Academy Floor Check flow is Master Plan build step 8. Until it's live, Floor Checks are tapped in the Academy only. *(M-06)*

---

## Added 2026-09-28 (evening): huddle lesson pass

For Preston:
- **H1.** Current store rule for possible assault firearms and buyers/pledgors/employees under 21. The 2026 ban is enjoined statewide (through Dec 31 or a final order); is the §12.05 under-21 rule inside the enjoined law or separate? Lessons now teach only "stop and get the current rule from the Market Manager." *(L6-01, L6-02, L6-04, L6-05; HUDDLE_INPUTS F1/F2; re-check before Jan 1, 2027)*
- **H2.** A firearm we sold that doesn't work: what's the remedy (gunsmith repair, exchange, credit, nothing) and time limit? §05.08 bars firearm returns; §07.04 promises a warranty on "everything we sell." *(L6-06, L7-02)*
- **H3.** A customer's firearm brought back for inspection: A&D entry if it stays overnight? 4473 and State Police check to hand it back? Who inspects it? *(L6-06)*
- **H4.** Function-complaint customer who wants to trade toward another gun: paperwork and value. *(L6-06)*
- **H5.** Confirm in writing: the three questions (what's it doing, what have you tried, what ammo) and "never coach a repair." *(L6-06)*
- **H6.** Rolex/luxury-watch authentication checklist (serial/reference lookup + your 5–8 checks) to close P51. Nothing taught until it's written. *(L8-02)*
- **H7.** Define "item age" for the discount review (days since intake or since tagged), and confirm the "reply to pawn-walk flags in Slack" procedure from 7/23. *(M-03)*

For Joshua:
- **H8.** Approve the Account Details by Phone & Text policy (account holder only, "including spouses") and align P&P §08.02, which still allows spouse or attorney. Lessons teach account holder only and test only non-spouse third parties. *(L1-05, L8-04)*
- **H9.** Loan-expiration date: Oct 1 or Sat Oct 3? Lessons say "in October" and don't test the date. *(L3-01, L3-06, L4-04, M-01; F6)*
- **H10.** eBay jewelry markdowns (154 items) vs the "never reprice precious metal online" rule. M-02 and L4-04 still teach the rule in force. *(M-02, L4-04; F5)*

## Added 2026-09-29: L8-06 Handbags
- **J-L8-06.** Joshua: adopt a paid authentication service for luxury bags (Authentic Detective recommended, pay per item)? If yes, add it as the step before "pass" in L8-06 and to the P&P. *(L8-06)*
- **P-L8-06.** Preston/Sandi: supply photos (or a short video) of a Coach creed patch, an MK seam tag and a Dooney serial tag for the lesson. *(L8-06)*

---

## Added 2026-10-13: selling-skills track L7-08 to L7-15 (8 lessons, built + validated, voiceover embedded)

Built from Preston's Sales Training Framework, P&P §04.01/§05.03/§06.02/§07.04, the Preston KB selling entries, the 10/08 Preston-to-new-hire calls, the huddle inputs, and the best-calls library. Each lesson's `sources` carries its own OPEN lines; the ones that need Preston or Joshua:

### For Preston
- RESOLVED 2026-10-13 (Joshua): the greeting script is 'Have you ever been here before?' + for a first-timer: 30-day warranty on everything, free layaway, the mobile app (pay your loan / shop from anywhere). Taught in L7-08, scored in the L7-15 role-play. Still open for Preston: a sell-side question list (L7-09 uses five questions; not tested as exact wording).
- L7-08: is "we buy gold" said to every customer, or only when it fits?
- L7-10: one or two real benefits-and-features pitches to replace the drill/PS5 examples.
- L7-11: who approves a discount between 30% and 50% (§05.03 is silent). Is general-merchandise "Blowout" clearance pricing firm like clearance jewelry?
- L7-12: confirm the add-on lists by category; the 90% email-capture target is a huddle goal, not policy.
- L7-13: does the 30-day warranty apply to jewelry, and what does it cover? Ring sizing (who, cost, turnaround)? Is "never sell gold jewelry under melt" a floor rule?
- L7-14: confirm the firearm add-on list and whether ammunition is sold with every firearm; warranty on firearms beyond L6-06.
- L7-15: hold policy for a sale a customer wants to "think about" (taught: layaway or a name + number for Chekkit follow-up).

### For Joshua
- L7-15 role-play scorecard: 10 marks, pass at 8 including the three starred. Confirm or change before HR-2026-10's role-play is scored against it.
- Level 7 now runs 15 lessons (~2 hours). Decide whether the selling track (7.8–7.15) is assignable on its own in week 1 for HR-2026-10, with the rest of the Academy following.
- Retail Brilliance: once 7.8–7.15 are live and assigned, the $239/month Brilliance seats can be cancelled (Manage Subscription).

### Upload status
- DONE 2026-10-13: all 8 zips uploaded to TalentLMS course 132 (Level 7) as units 2119–2126, titled 7.8–7.15; unit list verified in order 7.1–7.15. Course not republished, no enrollments (standing rule). Brilliance can be retired once Joshua decides.

### Voice clone (2026-10-13)
- Joshua's Take 1 (4:31) cloned as an ElevenLabs instant voice "Joshua Davis (Valley Pawn)", voice_id dKbJs6goRG1YRqCqrNO0 (Creator plan, 1 of 30 voice slots). NOT added to the voice rotation and no lesson re-voiced. Test clip: Training Program/Voice_Clone_Test_Joshua.mp3. Awaiting Joshua's approval of how it sounds.
- 2026-10-13: Joshua approved variant A ("natural and loose"): eleven_multilingual_v2, stability 0.35, similarity 0.95, style 0, speaker boost on. Saved under "joshua_voice" in .elevenlabs.json (voice_rotation untouched, no lessons re-voiced). Use for the level intros.

## Level intros uploaded (2026-10-13)
- 9 intro units (L1-00..L8-00, M-00) in Joshua's cloned voice (ElevenLabs voice_id dKbJs6goRG1YRqCqrNO0, variant A) uploaded to TalentLms courses 126-134 as "N.0 Welcome to ...", moved to first position, verified after reload.
- All uploaded as Draft (hidden). NOTHING published. Level 1 intro (unit 2127) is Draft inside the active Level 1 course (126): learners will not see it until Joshua/Preston publishes it.
- Units: L1 2127, L2 2128, L3 2129, L4 2130, L5 2131, L6 2132, L7 2133, L8 2134, M 2135.
- Remaining (need Joshua/Preston): publish decisions, Grow plan purchase, avatar clip (optional).

## Nov 4 launch demo + citation leak fix (2026-10-14)
- Demo deck (Claude Slides artifact "Valley Pawn Academy — Nov 4 Launch Demo", 10 slides, 15-min run of show) and Demo Player artifact (plays 7.0, 7.8, 7.15 standalone, no sign-in; files in demo_player/).
- TalentLMS can't play units for admins without activating courses / learner enrollment, so the player is the demo path. Course activation stays Joshua's call.
- FIXED: quiz feedback in 7.8-7.15 (plus 7.1, 7.4, 5.2) showed internal citations, incl. coaching calls naming employees ("zoom-call ... Preston-to-JoshuaBurnett/Benjie/JacobCox", "Huddle 2026-..", "Joshua Davis, 2026-10-13", "Preston 2025-11-24:"). build_scorm.py learner-text filter + validator extended (backup build_scorm.py.bak-20261014-huddlefilter). 11 lessons rebuilt, all 71 ALL GREEN, and replaced in TalentLMS (units 2119-2126, 2067, 2075, 2086). Lesson JSONs untouched.
- Level 1 intro (unit 2127) is the only intro hidden as a draft; other intros are visible inside their (inactive) courses.

## Sound effects + rollout (2026-10-14, in progress)
- build_scorm.py: synthesized ding (right), buzzer (wrong), applause (passed test); follows the lesson sound toggle. Backup build_scorm.py.bak-20261014-sfx. All 71 rebuilt, ALL GREEN; headless test confirmed all three sounds fire.
- Demo Player artifact updated with the sound versions. Deck: removed mentions of the cloned voice; lesson slide mentions ding/buzzer/applause.
- TalentLMS: Level 1 (course 126, active) all 8 units replaced with sound builds, but "Publish changes" NOT clicked (needs Joshua's OK); learners still see the old versions. Courses 127-134 (63 units) NOT yet replaced. Then: activate courses + enroll Joshua as learner (needs Joshua's OK).
- UPDATE 2026-10-14 (Joshua approved go-live for himself as first learner): all 71 TalentLMS units replaced with the sound builds; Level 1 changes published; Level 1 intro (2127) published; courses 127-134 activated; TalentLMS sample "What is TalentLibrary?" (course 125) deactivated to stay inside the Free plan's active-course limit (10). Joshua's role in all 9 courses changed Instructor -> Learner (0%, not started). Verified learner view: Level 1 opens and 1.0 loads. No other users enrolled. Joshua's account view left on Learner.

## Hillary voice clone (2026-10-14)
- Source: Hillary's 3:52 read of the L1-01 welcome script (Training Program/Hillary_Voice_Sample.mp3). ElevenLabs instant clone "Hillary Davis - VPA", voice_id Uruw1KTSW5RkXaLagJzW, eleven_multilingual_v2.
- Samples sent to Joshua: Voice_Tests/Hillary_A_natural (stab 0.35/sim 0.95), B_steady (0.55/0.9), C_warm (0.25/0.9/style 0.25). ~1k chars billed. Not wired into any lesson yet; waiting on Joshua's pick and where to use it.
- 2026-10-14: Joshua picked Hillary variant A (natural). Saved as hillary_voice in .elevenlabs.json (backup .bak-20261014-hillary). Not yet assigned to lessons.
- 2026-10-14 voice checks: all 9 Joshua intros transcribe to their scripts. Speaker match (resemblyzer cosine; same person real-vs-real 0.985-0.99, different people 0.58-0.70): Joshua clone 0.95, Hillary clone A 0.94 / B 0.94 / C 0.93.
- 2026-10-14 SPEED: joshua_voice + hillary_voice speed 0.92 in .elevenlabs.json (backup .bak-20261014-speed). Samples Voice_Tests/*_slower_92.mp3 sent for approval. WARNING: dist/*-00_*.zip were rebuilt WITHOUT narration (new settings = cache miss; run voice.py for the 9 intros, then rebuild) - do NOT upload them until re-voiced. TalentLMS still has the previous voiced intros.
- 2026-10-14: 9 intros re-voiced at speed 0.92 (~6.8k chars), rebuilt ALL GREEN with voiceover, uploaded + published in TalentLMS (2127-2135); Joshua's course roles flipped to Instructor for the upload and back to Learner in all 9 (TalentLMS limits admin edits in courses where you're a learner). Demo player intro updated.

## Added 2026-10-14: Goldilocks tie-ins (Joshua chose "tie-ins where it matters")
- Built + validated ALL GREEN (voiceover embedded). Facts used are only those taught in L1-07; each addition is marked `"goldilocks": true` in the lesson JSON.
  - L2-04 funds: the 6 PM check is named as Goldilocks; +1 question (a Slack reply doesn't clear the flag; record BANK to SAFE same day).
  - L2-05 jewelry count: the overnight check is named as Goldilocks; +1 question (the post isn't the escalation; Preston tonight).
  - L3-06 past-due call: new slide (weekly past-due review, first-payment default ranking); +1 question.
  - L4-03 making the offer: new slide (7:15 Daily Pawn Walk, flag under 30%); +1 key point, +1 question.
  - L4-04 pricing: new slide (7:45 Sold Review, 8:25 Discount Review age lines; limits unchanged); +1 question.
  - L7-02 layaway: new slide (the weekly layaway review is a Goldilocks post). No new question; Q2 already tests it.
  - L7-03 phone: new slide (#voicemails-calls-missed, auto-text isn't the callback); +1 key point, +1 question.
  - L7-04 texting: new slide (Chekkit inbox replies, 10-minute flag, 7 PM follow-up); +1 key point; replaced the large-deal approval question, which duplicated L4-03 Q8.
  - L7-15 selling: new slide (weekly month-to-date sales rankings, retail without fees, vs. start-date goals); +1 question.
- Spec change: a quiz may hold 9 questions when the 9th is the Goldilocks tie-in (LESSON_SPEC.md, validator). With 9 questions, passing at 80% takes 8 right.
- Distractors balanced so the right answer isn't the longest option.
- RESOLVED 2026-10-14 (Joshua): the weekly loan review "needs to go away, we no longer hold loans past 75 days." L1-07 no longer teaches it (weekly scoreboards = layaways, first-payment defaults, sales rankings); L3-06's Goldilocks slide now points at the first-payment-default ranking. The #loan-review post itself was retired in Valley Pawn OS (see CHANGELOG 2026-10-14). Rebuilt ALL GREEN. Upload list now 11 units: L1-07, L2-04, L2-05, L3-06, L4-03, L4-04, L7-02, L7-03, L7-04, L7-15 (course L1=126 added).
- TalentLMS upload PENDING: the Academy session expired (login page). Zips are in dist/ and staged. Courses affected: L2=127, L3=128, L4=129, L7=132. Steps: flip Joshua to Instructor in those 4, Change → upload → Publish changes per unit, then flip back to Learner.

## Added 2026-10-14 (evening): full program review and revision — ALL 71 lessons rebuilt
- Joshua: "Review the entire Valley Pawn Academy and make sure it feels and looks and sounds like a top notch program written by professionals using the most up to date learning strategies... relevant content for our company not just trivial facts, the pawn business which is the most important."
- Ten independent reviews (one per level, instructional design + pawn operator lens), then ten edit passes. Report for Joshua/Preston: `ACADEMY_REVIEW_2026-10-14.md` (76 numbered decisions, defaults already in the lessons). Per-level findings and change logs: `review_2026-10-14/`. Pre-edit lesson copies: `backups/20261014-review-pre/`.
- Spec/builder changes: `objectives` field on every lesson (spoken on the Start card after "By the end, you'll be able to…" and shown in a box); level intros (N.0) are ungraded previews with 3 questions (`pass_percent: 0`; validator and quiz self-test accept it; Start card shows "Not graded" / "quick questions"); `objectives` added to the learner-field allow-list; LESSON_SPEC.md updated (company voice, no attributions/dates, option-length rule).
- Every lesson re-voiced where lines changed (any edited line re-records in full). ElevenLabs meter ~104k of 131k used; resets 2026-10-28. Deferred length-only slide splits (section 4 of the report) wait for the reset.
- Built `--all`: ALL GREEN, voiceover 100% embedded on all 71. Demo Player artifact updated (7.0, 7.8, 7.15 = v4).
- TalentLMS upload PENDING for ALL 71 units (session expired). After Joshua signs in: for each course 126–134, flip Joshua to Instructor, Change → upload → Publish changes per unit, flip back to Learner. Zips in dist/.
- 2026-10-15: UPLOADED. All 71 revised units replaced in TalentLMS (courses 126-134), each course published ("Content updated successfully" x9). Unit M.1 renamed "M.1 The weekly layaway review and the loan timeline". Joshua flipped to Instructor for the upload and back to Learner in all 9 courses (verified after reload). The Free-plan sample course "[Edit me] Guide for Learners" still lists Joshua as Instructor (untouched).

## 2026-10-20/21: FINAL PRE-LAUNCH REVIEW (3-seat expert board) — read FINAL_PRELAUNCH_REVIEW_2026-10-20.md
- Board: pawn/compliance (2 reviewers), instructional design (2), platform/release (1). Reports in review_2026-10-20/. 7 blockers, ~45 must-fix: all fixed in the lesson JSONs (64 lessons changed). Pre-review copies: backups/20261020-board-pre/ (lessons, build_scorm.py, voice.py, the 10/15 dist zips).
- Key reversals: D40 reversed — pawn redemptions do NOT count toward ATF 3310.4 (27 CFR 478.126a(a)); D17 settled — first-timers hear three things, everyone hears clearance before leaving (= "the four things"); account details = verified account holder only everywhere (P&P §08.02 to align); phone gate = lesson 7.3 + five manager-scored practice calls (the "AI sims" don't exist); Sales Training — Week One (7.2, 7.3, 7.8–7.13, 7.15) due day 7.
- Builder/voice (backups *.bak-20261020-boardreview): narration-complete guard, transcript toggle, decode fallback, intro "Preview done" screen, leak filter (ISO dates/huddles), validator hooked into --all, voice.py verify + balance in estimate.
- Phase 1 voiced 24,928 chars (all 536 lines cached); --all build ALL GREEN (71/71, --skip-validate only for the L7-15 12-bullet slide). Phase 2 (~10.9k chars) after the 10/28 reset: PHASE2_REVOICE_RUNBOOK.md, target text lessons_target_20261028/.
- 2026-10-21: UPLOADED all 71 rebuilt units to TalentLMS (courses 126–134), each course published (0 unpublished after), unit 1.4 renamed "1.4 Your tools: Bravo, Slack, Chekkit, #ask-goldilocks". Joshua flipped to Instructor per course for the upload and back to Learner (verified each). Unit-ID map now in talentlms_units.json.
- Joshua-only: TalentLMS sign-in; Grow plan before staff launch; P&P/Handbook alignment (hours §01.01, §06.01 day-1, §05.00A government-issued doc, §08.02 holder only, §12.05 under-21 cite, Handbook hours + "Human Resources").
- 2026-10-21: P&P Manual v2026.9 FINAL and Employee Handbook v2026.8 FINAL created in Human Resources/ to match the Academy (hours, §06.01 day-1/FPD grace, §05.00A government-issued doc for 4473, §08.02 account holder only, 3310.4 filer + gift carve-out, under-21 § 18.2-308.7(C), §12.06 enjoined ban, greeting/three things, 31–50% Store Manager, warranty vs returns, counterfeit handling, Close Till/Close Store, title-pawn possession, police-caller + background-check phone script). Change table: Human Resources/PP_v2026.9_CHANGES.md. Re-sign acknowledgment HR-2026-04 Rev2 built. NOT sent (Gusto/Slack wait for Joshua's OK). #ask-goldilocks bot sources rebuilt from the new versions.

- 2026-10-22: Preston Peters added to TalentLMS (user 2, Learner-Type, username preston.peters, preston@fcfpawn.com, no password set by Claude) and enrolled as Learner in all 9 courses (L1-L8 + Manager Track). All 9 courses active (plan active-course limit reached). Users: Joshua (SuperAdmin) + Preston. Preston sets his password via "Forgot your password?" on valleypawn.talentlms.com.

- 2026-10-26 Policy Update November (Policy Day runner): checked all lessons against the November items — none teaches an old rule. Preston-draft fixes (L7-03, L3-06 notes, L4-02) still wait on his sign-off.
