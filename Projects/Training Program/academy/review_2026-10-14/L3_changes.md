# Level 3 — findings applied (2026-10-14)

Edited in place: `scratchpad/edit/lessons/L3/*.json` (7 files). Pre-edit copies kept at `scratchpad/review/L3_backup_pre_apply/`. All files re-parsed as valid JSON (2-space indent, ensure_ascii=False). Every lesson now has a top-level `objectives` string ("By the end, you'll be able to …", 24–31 words). Section/KB/call citations stripped from every quiz `why`; every wrong option's `why` names the rule it breaks in plain words. No correct option is the longest in its set.

## (a) Per lesson

### L3-00 Welcome
- `objectives` added.
- Narration: slide 2 adds "rates and fees are set in Bravo, you never change one" and "how much to lend is Level 4's job" (gap E). Slide 3 adds the escalation ladder: store manager on duty first; Market Manager for stolen property, a missing statement of ownership, and anything Bravo won't accept after you've tried (finding 7). Key points updated to match.
- Quiz: `pass_percent` 0; cut to 3 questions about the intro (finding 11/19). Q1 rate question rewritten to the single rule (finding 3). Q2 correct → "Get the info from the customer. Still refused? Stop and ask your manager." Q3 new: where the loan-amount decision is taught (Level 4). Dropped "How long is every pawn loan?", the SOO question and the past-due extension question (tested in L3-01/03/05/06).

### L3-01 How a pawn loan works
- `objectives` added.
- "Four charges" narration replaced with the short version (finding 20); tier table stays in bullets.
- "Two rules": 12.5% history cut (finding 9); added the one rate rule ("you never change a rate or a fee … exceptions only through the Market Manager, entered in Bravo") (finding 3).
- "The timeline": "Starting in October" removed → "Nothing is held past that without Joshua's approval"; FPD rewritten per finding 2; SOO sentence moved out (finding 22). Bullets match.
- Key points 3 and 4 updated (no negotiation wording → never change a rate/fee; day 61 added; FPD "no hold").
- Quiz: Q3 distractor "flat 12.5%" → "A late fee the customer was never told about on the ticket" (finding 9). Q5 rebuilt per finding 12 (correct = charge Bravo's number; third option = charge the lower of the two); prompt no longer calls 12.5% "the old rule". Q6 T/F → day-3 late-fee scenario (finding 13). Q7 75-day distractor → "keep it until day 61, that's when the pull has to be finished". Charizard/call references removed from whys. Clip caption anonymised (no store, date or "GM" line).
- Sources: 12.5%/75-day/October lines removed; HUDDLE F6 OPEN removed; 2 OPEN lines appended.

### L3-02 Qualifying the customer
- `objectives` added.
- Slide 1: "Preston's pawnbroker one oh one" → "That's the order"; $10-loan judgment → the rule "if Bravo shows a history of forfeits and no redemptions, offer a buy, not a loan" (finding 25).
- Slide 2: "Preston's rule / in his words" → the rule stated (finding 6).
- Slide 3: family list compressed to "your spouse, anyone you live with, including roommates, and your family by blood or marriage"; known thief → "If Bravo flags the account, you don't write it. Ask your manager." (finding 24, OPEN).
- Slide 4: named the categories: rent-to-own, cell phones, altered serials (finding 26).
- Slide 5: "old message that said reloans were exempt" and "Preston's words" cut (finding 9).
- Quiz: Q5 prompt no longer says "Preston said so"; distractor → "Reloans don't need it. The item was already vetted when the first loan was written." Q4 why de-attributed. Dangling citations repaired. Clip caption anonymised.
- Sources: old customer-photo OPEN replaced; 3 OPEN lines appended.

### L3-03 Writing the ticket
- `objectives` added.
- "The one rule": misdemeanor line → "Leaving required fields blank is a crime under Virginia law, and these records are what the police read" (finding 31).
- "Bravo, start to finish": narration cut to the three decision points (customer / item / payment) (finding 21).
- "Ten-item checklist": narrates the three groups; sub-items stay in bullets (finding 21).
- ID slide: "Preston checks for both" cut.
- "After you hit Save": police report moved to its own new slide "The police report" (finding 23); failure routed "tell your manager that same day so it's resent before noon" (finding 14; OPEN vs P&P's "report to Preston"). Added "tag it and put it where your store keeps pawned items" (gap E, kept generic; OPEN). Floor check adds "trainee tags and shelves the item the way the store does it".
- Key point 6 updated (failure → manager same day).
- Quiz: Q4 rebuilt per finding 14 (correct "Tell your manager tonight so it can be resent before noon tomorrow"; distractor "Say nothing and retry Monday. Weekends don't count"). Q7 military-ID T/F replaced with an item-handling scenario (drill + batteries + charger → shrink-wrap together, tag) (finding 15). Q5 shortened so the correct option isn't longest.
- Sources: 2 OPEN lines appended.

### L3-04 Closing the contract
- `objectives` added.
- "Read the box": rate rule unified to the one sentence (finding 3).
- "Fees": "old two dollar figure" cut (finding 9); third-party firearm line now "never, except the denied pledgor designation taught in Level Six, with Market Manager approval every time" (finding 4).
- "Sign, print, hand over, file": send-off is four things — warranty, clearance, free layaway, app (finding 18). Floor check and key points updated.
- Quiz: Q3 correct aligned to the rate rule. Q5 prompt/distractor per finding 9 ("No fee. She's the customer on the loan and her ID proves it"). Q7 correct → "Explain every contract is fingerprinted and we can't write it without one" (finding 16; §05.01 says every contract is fingerprinted). Q8 → scenario "The loan's signed and the customer is leaving…" with the four things. Clip caption anonymised; title-pawn note now points to the Market Manager.
- Sources: "$2 figure" note removed; 3 OPEN lines appended.

### L3-05 Payments, extensions and redemptions
- `objectives` added.
- "Verify": "narrow exception needs Preston's approval" → Level 6 denied-pledgor designation with Market Manager approval (finding 4).
- "Extra toward principal": "have your manager show you" moved to floor_check ("ask the manager to show you the paydown screen in Bravo") (finding 27).
- "Redemption": "In Preston's words…" cut; bullet de-attributed (finding 6).
- "I can't afford": $12 anecdote removed (kept once in L3-06) (finding 10); "the manual says" → plain rule.
- "Extension" wording: already extension-first with one Renewal mention; unchanged (finding 28).
- Quiz: Q6 redeem-and-rewrite replaced with the paydown scenario ("pays the finance charge plus $50 — what does the $50 do?") (finding 15). Q4 "Preston won't let us" → "My manager won't let us" with the no-blame why. Call 183 references removed.
- Sources: 2 OPEN lines appended.

### L3-06 The past-due call
- `objectives` added.
- Slide 1 "Four versions in one week" → "One script", narration per finding 8 (no call-audit recap).
- "What safe means": day 61 restored, CEO approval past 61, FPD per finding 2, "starting in October" removed (findings 1, 2, 5).
- "Collections without shame": October/"set after payday"/best-call line cut; now "when a long-time customer remembers us holding things longer … our hold is thirty days past due, a courtesy deadline, not a penalty" (findings 5, 10). "not Preston" → "not the Market Manager" in the no-blame line.
- "Outbound rules": open-line anecdote cut (finding 10); added "the same rules cover reminder calls before the due date and past-due calls after it" (finding 29).
- "What Goldilocks will show you": added the FPD shelf-check sentence (finding 30). `goldilocks: true` marks kept.
- Key points 2, 5, 6 updated.
- Quiz: Q3 75-day distractor → day-61 distractor. Q6 prompt/distractor no longer say "start expiring"; "Preston and the owner" → "The Market Manager and the owner". Q8 rebuilt per findings 5/8 (prompt: ten-year customer remembers a longer hold; correct: "Our hold is thirty days past due. It's a courtesy deadline, not a penalty…"; distractor: "Anything over thirty days past due is gone now…"). Q9 prompt → "has the most first-payment defaults"; distractor → "Wait. The automatic Friday text already reminds them." (finding 17). Call 73/130/183/201/249 references removed from whys. Clip caption anonymised.
- Sources: 75-day/October/huddle-October/PHONE_AND_TEXT_REVIEW lines removed; 2 OPEN lines appended.

## (b) OPEN items (appended to `sources` as "OPEN (review 2026-10-14): …") with recommended default

1. **First-payment default** (L3-01, L3-06): taught as "no 30-day company hold; pullable once the 15-day statutory grace is up". Default: keep — it is the only reading consistent with §05.01's statutory floor.
2. **Market Manager rate exceptions** (L3-00, L3-01, L3-04): taught as "you never change a rate or fee; exceptions only through the MM, entered in Bravo". Default: keep (it's §07.04); if Preston says no exceptions exist, delete the last sentence everywhere.
3. **Escalation ladder** (L3-00): store manager first; MM for stolen property, missing SOO, Bravo refusal after trying. Default: keep the ladder; note L3-02/L3-03 still say "stop and call Preston" for stolen/altered-serial/Bravo-refusal because the P&P does. Preston to say whether the store manager is an acceptable first stop for those.
4. **Police report failure routing** (L3-03): taught "tell your manager the same day"; P&P says Preston. Default: manager same day, and the manager tells Preston.
5. **Customer photo every intake** (L3-02): taught as the company standard; P&P requires it only for military ID. Default: keep; add to P&P §05.00A.
6. **"Known thief" — how you'd know** (L3-02): taught "if Bravo flags the account, don't write it; ask your manager". Default: keep if Bravo has such a flag; otherwise change to "if your manager has told you".
7. **Buy-not-loan rule** (L3-02): "history of forfeits and no redemptions in Bravo → offer a buy". Default: keep (KB default-rate entries).
8. **Item handling after Save** (L3-03): tag + shelf stated generically ("where your store keeps pawned items"); procedure is a floor-check item. Default: Preston to add one sentence on tagging and location.
9. **Four send-off talking points incl. clearance** (L3-04): review said four; §07.04 lists three. Default: keep four if clearance is a standing talking point; otherwise revert to three (warranty, app, free layaway) in slide 5, floor_check, key point 6 and Q8.
10. **Third-party firearm pickup exception** (L3-04, L3-05): "never, except the Level 6 denied-pledgor designation, MM approval every time". Default: keep.
11. **Paydown procedure in Bravo** (L3-05): concept taught; steps are a floor-check item. Default: Preston states the screen; then add one bullet.
12. **Long-time-customer wording** (L3-06): "our hold is thirty days past due, a courtesy deadline, not a penalty"; the retired tolerance is never mentioned. Default: keep.
13. Pre-existing OPEN lines (configured rates, title-pawn answer, fingerprint refusal, phone payments, extension approver, grace/late-fee script adoption) left in place.

## (c) DEFERRED

- No slides were split purely for length. The one new slide (L3-03 "The police report") was a content split asked for by finding 23.
- L3-03 "Ten-item checklist" and L3-01 "Four charges" narrations were rewritten rather than split; both are now shorter than before.
- L3-06 "Collections without shame" is still the longest `say` in the level (~720 chars); splitting it would be for length only, so left as is.
- Spouse access to account details (gap E) — not addressed; the lessons already say details go to "the customer, their spouse or their attorney" per §03.09/§08.02 and nothing more is in the sources.
- Quiz rule "right option not the only one quoting the lesson" was checked by eye only; no automated check.

## (d) Estimated changed narration characters

Measured with difflib (inserted + replaced characters in `say` + `key_points` + `objectives`, old vs new):

| Lesson | Changed chars |
|---|---|
| L3-00 | 611 |
| L3-01 | 551 |
| L3-02 | 332 |
| L3-03 | 557 |
| L3-04 | 425 |
| L3-05 | 232 |
| L3-06 | 678 |
| **Total** | **3,386** (budget 6,500) |

Of that, 1,100 is the seven new `objectives` strings. Quiz, bullet, caption, floor_check and sources edits are not counted.
