# B2 — Instructional design review, Levels 5–8 (L5-00 → L8-06)

Seat: Senior instructional designer / L&D lead. Scope: 36 lessons, every slide, bullet, narration line, key point, floor check, gate and all 258 quiz questions (ALL_LESSONS_DUMP.txt lines 1890–4356), checked against LESSON_SPEC.md and the 2026-10-14 review (its §3 defaults and §4 deferred splits are not re-litigated or repeated).

Method notes
- Alignment: every question was traced to the slide that teaches it. Result: 257 of 258 questions test taught content; one (L7-15 Q7) tests a rule that appears only in the gate text and the HR policy, not on a slide.
- Narration cost: findings are marked **(free)** when they touch only bullets, key points, quiz text, `why`, gate or floor-check text, and **(narration)** when a `say` line must be re-synthesised, with an approximate character count.
- The build's `learner_text()` strips KB ids, call numbers, POLICY_GAPS, huddle/zoom references from learner-visible text, so those citations in `why` are not reported as findings. The few that slip past the filter are listed.
- Answer position is shuffled by the player, so position bias is reported once (program level) and not per lesson.
- "#ask-handbook" does not appear anywhere in Levels 5–8 (grep of lines 1890–4356: zero hits). No rename work in this scope.

Severity: BLOCKER / MUST-FIX / SHOULD-FIX / NOTE as defined in the brief.

---

## Level 5 — Gold, jewelry and stones

### L5-00 Welcome to Level 5

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 1 | NOTE | L5-00 | Q3 | "Which of these is NOT covered in Level 5?" — negative-stem recall item; harmless in an ungraded preview but the only question type the brief flags as weak. | Optional (free): "A customer asks you to quote her gold chain on your second day. What has to be true first?" → tests slide 3 instead of a table of contents. | Brief §2; LESSON_SPEC intro rule |
| 2 | NOTE | L5-00 | Slide 3 / Q1 | "Your manager watches you test" is the sign-off described; L5-01 and L5-04 call it a Floor Check tapped by the manager. Same thing, two names. | (free) Slide 3 bullet: "Your manager watches you test and taps your Floor Check". | L5-01 gate, L5-04 gate |

### L5-01 Testing gold and silver

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 3 | MUST-FIX | L5-01 | Slide 5 "Coins and bars: magnet, weight, Sigma", bullet 5 and last two narration sentences | Bullet: "Acid on the slate is the standard confirmation. The Kee is an extra if you have one" sits on the **coins and bars** slide, directly under "Every coin and every bar: magnet, weight AND the Sigma tester". A learner reads it as "acid confirms a bar". L5-05 Q2 then marks "Yes, if you acid it on the slate as well" wrong because "Acid is a surface test. A plated tungsten bar passes it." The two lessons disagree on the slide the learner sees. | (free) Move bullet 5 to Slide 3 (jewelry) as "Acid on the slate is your standard confirmation; the Kee is an extra if your store has one". (narration, ~95 chars) Delete the last two sentences of Slide 5's `say` ("Acid on the slate is your standard confirmation. The Kee is an extra if you have one.") or move them to Slide 3's `say`. | L5-05 Q2 why; KB fraud-detection-bars-kee-unreliable |
| 4 | SHOULD-FIX | L5-01 | Slide 1 | Narration ends "And check whether it's been in the store before, and what we loaned on it last time." No bullet carries it; heading/bullets/narration disagree. | (free) Add bullet 5: "Check Bravo: has it been here before, and what did we loan on it?" | P&P §04.03 |
| 5 | SHOULD-FIX | L5-01 | Objectives vs quiz | Objective promises "confirm coins and bars against spec"; no L5-01 question tests a dimension check (Q3 tests the Kee). The spec check is tested only in L5-05 Q6. | (free) Replace Q3's third distractor or add a 9th item: "A 1-oz Maple weighs 31.1 g on the nose but measures 32 mm across. The spec card says 30 mm. What is it?" → "Fake: right weight, wrong size". Or accept and rely on L5-05 Q6 (spaced). | Slide 5 bullet 3 |
| 6 | NOTE | L5-01 | Slide 3 | Six bullets (spec: ≤5) and 125-word / 10-sentence narration. Already on the deferred-split list (§4 Level 5 "split L5-01 slide 1 and Coins and bars") but Slide 3 is the denser one. | Add Slide 3 to the post-Oct-28 split list: "Read it, sort it" / "Acid: how to read the streak". | Review §4 |
| 7 | NOTE | L5-01 | Header `minutes: 12` | Narration 726 words ≈ 4.8 min + 8 questions ≈ 4 min ≈ 9 min. Stated 12. | (free) Set 10. Same over-statement in L5-02 (12 → 9), L5-04 (12 → 10 incl. clip). | Brief §3 |
| 8 | NOTE | L5-01 | Q3 vs L5-05 Q2 | Near-duplicate items (bar passes the Kee → still need Sigma). Acceptable spaced repetition; flagged so nobody "fixes" one without the other. | None. | — |

### L5-02 Melt math and the spot sheet

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 9 | SHOULD-FIX | L5-02 | Slide 6, bullet 4 | "A guess that's wrong by thousands loses the customer. It happened on Call 204" — a call-library ID in a learner-facing bullet. (The build rewrites "Call NNN" in running text, but confirm it catches "on Call 204" — the CALL_REWRITES list has no pattern for "on Call \d+".) | (free) Bullet: "A guess that's wrong by thousands loses the customer. It has happened on a real call." | LESSON_SPEC (anonymised stories); build_scorm CALL_REWRITES |
| 10 | SHOULD-FIX | L5-02 | Slide 4 bullet 5 and narration | "Call for funds: Joshua, then Hillary, then Preston" — Hillary is never introduced with a role anywhere in Levels 1–8. A day-20 hire does not know who Hillary is or how to reach her. | (free) Bullet: "Joshua, then Hillary (office), then Preston" — or whatever role/contact Joshua wants shown; the contact list belongs on the funds card at the counter. | KB gold-deal-escalation-40514bd1 |
| 11 | SHOULD-FIX | L5-02 | Slide 4 narration + Q5/Q6 | Three names for where the percentage comes from in one slide: "The Bravo estimator and the published tiers set it. The percentage comes from the spot sheet, not from you." Q5's right answer is "The rate on the spot sheet"; Q6's is "Stick to the estimator". A learner cannot tell whether the spot sheet and the estimator are the same artifact (D35 is open on what the spot sheet is). | (free) Until D35 is answered, make the bullets consistent: "What we pay is a percentage of melt. The Bravo estimator sets it for jewelry; the spot sheet carries the bullion, silver and junk-silver rates." Narration can stand. | Review D34/D35 |
| 12 | NOTE | L5-02 | Slide 2 narration | "Say it with a ten pennyweight fourteen karat piece. Ten pennyweight, divide by twenty, times point five eight three three, times spot." The spoken worked example stops before the answer; the on-screen example is a different piece (54.8 dwt). Q1 then uses the 10 dwt case. Worked-example → faded-practice is the right design, but the spoken example should finish. | (narration, ~60 chars, defer) "…times spot. At four thousand dollar gold that's eleven sixty-six." Then Q1 is retrieval of a completed example. | Brief §1 (worked examples then faded practice) |
| 13 | NOTE | L5-02 | Q1–Q3 | Arithmetic is correct ($1,166.60; $3,000; $758.29; distractors $933.28 / $23,332 / $2,333.20 / $60,000 all reproduce the named error). Good error-driven distractors. | None. | — |

### L5-03 Scrap buckets and jewelry categories

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 14 | NOTE | L5-03 | Slide 2 bullets / Q1 stem | "2026-08 GOLD", "For August twenty twenty six", "It's September 1, 2026." Format examples must carry a year; these will read stale from January. | Accept for launch. At the next narration cycle use "YYYY-MM GOLD" on the bullet and keep one dated spoken example. | LESSON_SPEC (no dates) |
| 15 | NOTE | L5-03 | Slide 4 | Six bullets. | Merge "Scrap = only for pieces NOT going out for sale" and "Miscellaneous Jewelry = never" into one bullet (free). | Brief §3 |
| 16 | NOTE | L5-03 | Slide 6 vs L7-13 slide 5 | L5-03: "Aged jewelry: 30% off after 1 year on the floor, 6 months in clearance, then scrapped" (§06.03). L7-13: "Clearance jewelry is already 30% under the Bravo estimator… That price is firm." Both say 30% but off different bases (tag vs estimator). Not contradictory to a learner, but see finding 86 (L7-13 Q7 "scrapped at two years") which is. | Align wording when §06.03 is next revised. | P&P §06.03; KB clearance-aged-item-policy |

### L5-04 Diamond basics at the counter

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 17 | SHOULD-FIX | L5-04 | Slide 4 vs Slide 8 | Slide 4: "No inscription, over half a carat, no paperwork → your manager's call." Slide 8: "A large stone → Preston. Always." Two thresholds, two people, and "large" is undefined (open item). A learner with a 0.7 ct uninscribed stone has two instructions. | (free) Slide 4 bullet 4: "No inscription, over half a carat, no paperwork → your manager's call; a large stone still goes to Preston (next slides)". Better: Market Manager states the carat line and one bullet replaces both. | Review D37; L5-04 OPEN "large stone" |
| 18 | SHOULD-FIX | L5-04 | Slide 8 bullet 4 | "No diamond number over the phone — bring it in and we'll look at it while you wait" is taught and in the gate but never tested in this lesson (L5-02 Q7 covers metal only). | (free) Swap Q1 (pure recall of the Good definition, which Q2 also exercises) for: "A caller says 'I've got a one-carat diamond ring, what will you give me?' What do you say?" → bring it in / name, number, time. | Gate text (POLICY_GAPS #3) |
| 19 | NOTE | L5-04 | Slide 2 | 4Cs vocabulary slide: untested by design (OPEN). Fine as advance organiser; keep under 70 words (it is 65). | None. | — |
| 20 | NOTE | L5-04 | Q3 | Good item: distractor 2 ("it's pretty cloudy, so the stone itself isn't worth much") catches the opposite error. Model for other lessons. | None. | — |

### L5-05 Counterfeit tells

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 21 | SHOULD-FIX | L5-05 | Q4 why (correct option) | "All coins and bullion are tested by magnet, weight and Sigma, and coin buys get audited after the fact." The audit is not taught on any slide; the `why` introduces a new fact at feedback time. | (free) "…magnet, weight and Sigma. One test is one third of the answer." | Slide 3 |
| 22 | NOTE | L5-05 | Slide 2 bullet 1 | "At one of our stores, bars passed the Kee and failed the magnet and the Sigma. Fake" repeats L5-01 Slide 5 verbatim. Useful retrieval, but the same sentence in two lessons two days apart reads as copy-paste. | (narration, defer) Vary: "You heard in lesson one what happened with the Kee on bars. Here's the rest of the story." | — |
| 23 | NOTE | L5-05 | Slide 4 | 122-word, 11-sentence narration with four tells (plated notch, light-for-size, magnet on links, 925 plated). Heaviest slide in the level and not on the deferred list. | Add to the post-Oct-28 split list: "Plated and hollow" / "Magnet and 925". | Review §4 |
| 24 | NOTE | L5-05 | Quiz | 7 scenarios + 1 mc, every item traceable, distractors each name the broken rule. Strongest quiz in Level 5. | None. | — |

---

## Level 6 — Firearms

Sequencing check (brief §4): basics → 4473 → check → transfer → pawns → "won't fire" is coherent; each lesson names its prerequisites ("lessons two and three", "lesson three", "Level one"). One gap: the only safe-handling procedure (ask if loaded, take control muzzle-down, clear it behind the workstation) is taught in L6-05 slide 1, after three lessons and two Floor Checks (L6-02 live 4473, L6-04 opening a shipped box) in which the trainee already has a firearm in hand. See finding 25.

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 25 | SHOULD-FIX | L6-01 (level structure) | Slide 1 | No handling rule appears before L6-05. L6-02's Floor Check ("Manager stands beside the trainee for their first live 4473") and L6-04's ("box opened… serial number on the firearm checked") have the trainee handling guns with no Academy instruction yet on clearing. The Gun Safety 101 certificate is the implicit prerequisite but the level never says so. | (free) L6-01 Slide 1 add bullet: "Handling a gun: your Gun Safety certificate, plus the one clearing sequence in lesson 6.5 — ask if it's loaded, take control muzzle-down, you clear it behind the counter." Or (structural, free in TalentLMS) move L6-05 slide 1 into L6-01 as its slide 2 at the next narration cycle. | P&P §04.02 ONE SEQUENCE; §10.06 |

### L6-00 Welcome to Level 6

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 26 | NOTE | L6-00 | Slide 3 bullet 4 / Q3 why | "Joshua, the owner" here; "Joshua (CEO)" in L8-01; "Joshua, the Owner" in L8-03 Q5; "Joshua Davis (CEO)" in gates. Three titles for one person across the levels. | (free where in bullets/whys) Standardise on "Joshua, the CEO" (what L8-01 and the Manager Track use); narration lines that say "owner" can wait for the next cycle. | Review §2 Manager Track ("Joshua, CEO") |
| 27 | NOTE | L6-00 | Q1 | Correct option "Hand it off to a certified coworker or your manager" — the coworker hand-off is not on a slide (slide 3 says only "you don't touch a firearm transaction"). Reasonable inference; ungraded. | (free) Slide 3 bullet: "Not certified yet? A certified coworker or your manager handles it". | — |

### L6-01 FFL basics and the A&D book

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 28 | SHOULD-FIX | L6-01 | Slide 2 bullet 3 (untested critical rule) | "If anything changes in your status that could make you prohibited, tell Preston immediately" — a legal duty taught and never tested in Level 6. | (free) Replace Q3 (the only non-scenario, and its content — redemption is a disposition — is retested in L6-03/L6-05) with: "You're arrested over the weekend and charged with a felony. You're due at the counter Monday. What do you do before your shift?" → "Tell Preston before you handle any firearm." | P&P §10.06; 18 U.S.C. § 922(g) |
| 29 | SHOULD-FIX | L6-01, L6-04 | Slide 1 bullets 2, 4; Slide 6 bullet 4; L6-04 Slide 4 bullet 2 and Q3 | British spelling "licence" in seven learner-visible strings ("The licence names the building", "can cost the licence", "the licence expiration date", "Create the vendor: business name, FFL number and licence expiration date") while "license" is used in the same slides' narration and elsewhere. | (free) license, throughout. | Voice/consistency |
| 30 | SHOULD-FIX | L6-01 | Slide 1 bullet 1 | "Every Valley Pawn store holds its own federal firearms license (FFL) — not just Roanoke." A new hire has never heard the Roanoke myth; the aside only makes sense to legacy staff. Q7 already handles it as a coworker's belief, which is the right place. | (free) Bullet: "Every Valley Pawn store holds its own federal firearms license (FFL)". Narration ("Not just Roanoke. All five.") can stay for the existing-staff rollout; drop it at the next cycle. | P&P §09.02 revision note |
| 31 | NOTE | L6-01 | Q5 option 3 why | "Repair or disposition needs manager pre-approval (P&P §04.02)" — not taught on slide 3; appears only in feedback. Harmless but new. | (free) Drop the clause or add to Slide 3 bullet 5: "…do-not-sell-as-is tag; repair or sale needs manager approval first". | P&P §04.02 |
| 32 | NOTE | L6-01 | Slide 5 | Five bullets, 126 words, 10 sentences; the ATF-visit and trace-request rules share one slide. | Deferred-split candidate (not on the §4 list): "When ATF or police walk in" / "A trace request is a 24-hour clock". | Review §4 |

### L6-02 The 4473, section by section

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 33 | MUST-FIX | L6-02 | Slide 2 "Who fills what" | Eight bullets (brief limit 5) carrying five form sections, the SP-65, the no-attachment rule, 30-day validity and Section D recertification, over a 146-word narration. This is the highest-stakes slide in the Academy and the most overloaded. | (free) Cut to five: (1) "Staff: Section A (the firearm), Section C (ID and the State Police check), Section E (dealer certification)"; (2) "Customer: Section B — every question, in their own hand. And the SP-65 consent form"; (3) "Section D: the customer recertifies if the gun goes out on a later day"; (4) "Everything on the form itself. Never an attachment"; (5) "A check is good for 30 days. After that: new 4473, new check". (narration, ~900 chars, defer) Split into "Who fills what" / "Thirty days and Section D" at the next cycle. | Brief §3; LESSON_SPEC |
| 34 | SHOULD-FIX | L6-02 | Slide 9 bullet 5 | "Log the form in the Firearm Transactions (4473) Log. It's kept until the business closes" — "closes" reads as end of day. Narration says "for as long as we're in business". | (free) "…It's kept for as long as we're in business, then goes to ATF". | P&P §03.08 |
| 35 | SHOULD-FIX | L6-02 | Slide 1 bullet 5 (untested) | "Your own purchase? Another employee completes the 4473" — taught, never tested in Level 6. Low frequency but an ATF citation risk. | (free) Fold into Q1 as a fourth option or add a 9th item: "You've found a rifle on the rack you want to buy. Who does your 4473?" | P&P §05.10 §7 |
| 36 | SHOULD-FIX | L6-02 | FLOOR_CHECK | One 130-word paragraph with nine checks; rendered by the player as a single paragraph after "Your manager will verify this on the floor:". A manager cannot tick it. | (free) Rewrite as numbered steps separated by ";" and have the build render ";"-separated floor checks as an ordered list (one-line change in rFloor). Same for L6-03, L6-04, L6-05, L7-05, L7-06. This is also the 4473 counter checklist job aid (program finding 101). | build_scorm.py line ~1284 |
| 37 | NOTE | L6-02 | Slide 7 | The "21 for handguns" slide rests on federal law and names no dates. Correct per the brief. Q4's third distractor (coaching a straw purchase) is an excellent catch-all. | None. | 18 U.S.C. § 922(b)(1) |
| 38 | NOTE | L6-02 | Quiz | 8 scenarios, each distractor names the rule it breaks; the 30-day validity / Section D remain untested (already deferred in §4). | None beyond §4. | Review §4 |

### L6-03 The background check

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 39 | SHOULD-FIX | L6-03 vs L8-05 | Slide 6 bullet 4 / Q5 | L6-03: "Voicemail: your first name, the store and a callback number. Nothing else." L8-05 slide 5 / Q7: "No voicemail on reminder calls… Even a bare callback message is a voicemail." Different call types (check-finished callback vs loan reminder), but the learner hears "voicemail allowed" in Level 6 and "never a voicemail" in Level 8 with nothing linking them. | (free) L6-03 Slide 6 add to bullet 4: "(Loan reminder calls are different — those get no voicemail at all, lesson 8.5)". L8-05 Slide 5 bullet 2: "No voicemail on reminder calls. (A callback after a background check is the one voicemail we leave — first name, store, number.)" | P&P §08.01; §03.09 |
| 40 | NOTE | L6-03 | Terminology | "Preston approves it, every single time" (slide 5) vs L6-05 slide 4 "approved by the Market Manager every time" for the same rule. Same person, two labels, adjacent lessons. | (free) Key points/bullets: "Preston, the Market Manager, approves it every time" once in each lesson. | Review §2 Level 6 |
| 41 | NOTE | L6-03 | Slide 2 (untested) | Approval number on the paperwork and the gun lock are untested in the quiz; both are in the Floor Check. Acceptable split (procedural → floor). | None. | — |
| 42 | NOTE | L6-03 | Quiz size | 7 questions; pass_percent 80 → 6 of 7 (86%). See program finding 97 on effective pass marks. | — | — |

### L6-04 Receiving an FFL transfer

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 43 | SHOULD-FIX | L6-04 | Slide 5 narration; Q1, Q8 why | "remember the order Preston set" (narration); "That's Preston's SOP" (Q1 why); "Preston's order is sales, payments…", "Transfers come last in Preston's service order" (Q8 whys). Attribution of a rule to a person, which the spec forbids and the 10-14 review removed everywhere else (L7-01 Q5 says "The order is set"). | (free) Q1/Q8 whys: "That's the receiving procedure", "The service order is sales, payments, loans and buys, then transfers". (narration, ~30 chars) "remember the order we set". | LESSON_SPEC (never "Preston says") |
| 44 | NOTE | L6-04 | Slide 5 | 131 words, 11 sentences, five topics (service order, lessons 2–3, age, Bravo ring-out, phone). | Deferred-split candidate: "Handing it over" / "Ringing it out". | Review §4 |
| 45 | NOTE | L6-04 | Q4 | Fee arithmetic ($25 + $10 + $10 = $45) with both wrong models as distractors ($75 per-gun, $35 per-transaction). Good. | None. | KB ffl-transfer-fee |

### L6-05 Firearm pawns, redemptions and holds

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 46 | SHOULD-FIX | L6-05 | Slide 4 bullet 3 | One bullet, 36 words: "A third party NEVER redeems a firearm — not with the ticket, not with ID, not a spouse. One exception: the denied-pledgor designation (lesson 3), approved by the Market Manager every time". Two rules in one line. | (free) Split: "A third party NEVER redeems a firearm — not with the ticket, not with ID, not a spouse" / "The one exception: the denied-pledgor designation from lesson 6.3, Market Manager approval every time". Slide then has 6 bullets — merge bullets 1 and 2 ("…before it's handed over. No permit exempts anyone"). | Brief §3 |
| 47 | SHOULD-FIX | L6-05 | Q3 correct option | "Don't release it. Only he can redeem it; she can make a payment for him" — the payment right is not taught in this lesson (it is Level 3 content). The `why` cites §05.04 but the slide only says a third party never redeems. | (free) Slide 4 bullet: "…not a spouse. They can make a payment or refinance for the pledgor — they just can't take the gun". | P&P §05.04 |
| 48 | NOTE | L6-05 | Slide 7 | 165 words, 11 sentences, two embedded stories — the longest narration in Levels 5–8 and not on the §4 deferred list (which names slide 4). | Add to the split list: "Officer at the counter" / "Nothing moves on a phone call". | Review §4 |
| 49 | NOTE | L6-05 | Slide 2 bullet 5 | "New customer, no history with us? Don't loan high" — taught, untested, and the amount rule is OPEN. Fine. | None. | KB no-high-loans-to-new-gun-customers |

### L6-06 "My gun won't fire"

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 50 | SHOULD-FIX | L6-06, L7-00, L7-08 | L6-06 Slide 1 bullet 2 / Slide 5 bullet 1 vs L7-00 Slide 2 / L7-08 Slide 2 | Level 7 scripts "A 30-day warranty on everything" to every first-time customer; L6-06 teaches "Firearms can't be returned. Don't promise a refund" and never says whether the warranty applies to a gun. The conflict is an open P&P item (§07.04 vs §05.08), but the learner hits it inside one week: they will be asked by a gun buyer "so the 30-day warranty covers this?" and have no sentence to say. | (free) L6-06 Slide 5 add bullet: "The 30-day warranty still means we look at it — no returns on firearms, but a gun that stops working inside 30 days comes in and your manager and Preston decide." Then the remedy decision (D51/OPEN) fills in the rest. | P&P §05.08; §07.04 |
| 51 | NOTE | L6-06 | Quiz | 6 scenarios, every one traceable; "Don't coach a repair" story anonymised. Clean. 80% of 6 = 5/6. | None. | — |

---

## Level 7 — Sell and Serve

Track coherence (brief §4). Lessons 7.1–7.7 are the original policy-flavoured sales module (framework, layaway/warranty, phone, texting/reviews, eBay ×2, recovery); 7.8–7.15 are the selling-skills track added for HR-2026-10. 7.1 is a compressed preview of 7.8, 7.9, 7.10, 7.11 and 7.12 (greeting, pitch, objections, discount authority, add-on, four things all appear twice). The role-play scorecard in 7.15 covers 7.8–7.12 and 7.2 cleanly. Two structural problems follow: the week-one timing conflict (finding 52) and stale gate text (finding 54).

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 52 | MUST-FIX | Level 7 structure (L7-08 gate, L7-15 gate, L7-15 Q7) | L7-08 GATE: "policy HR-2026-10 expects sales training done within 7 days of starting". L7-15 GATE: "by day 7 the store manager runs a 10-minute sales role-play". L7-15 Q7 stem: "It's day 6…" | HR-2026-10 (signed, effective Oct 1) requires the sales course and role-play by **day 7**. The Academy unlocks levels in order and ONBOARDING_FLOW puts Level 7 in **weeks 5–6** (Level 1 days 1–3, Level 2 week 1 … Levels 5+6 week 4). A new hire cannot reach 7.8–7.15 by day 7; the policy, the gate text and Q7 describe a schedule the course makes impossible, and L7-15 Q7 grades the learner on it. | Decide one of: **(A, recommended)** In TalentLMS create "Sales Training — Week One" = 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.2 (layaway tiers, needed by 7.15 mark 10) and 7.15, assigned on day 1 alongside Level 1, due day 7; keep 7.1, 7.3–7.7 and **7.14 (requires Level 6)** in Level 7. Course count becomes 10 (the Free-plan limit) — confirm the Grow purchase or merge the three annual lessons out of Level 8 first (finding 99). **(B)** Amend HR-2026-10 to "within 7 days of reaching Level 7" and re-sign in Gusto; change L7-15 Q7 to "It's the sixth day since Level 7 unlocked…". Either way, remove the "Final lesson of Level 7" gate on 7.7 (finding 54). | HR-2026-10; ONBOARDING_FLOW.md cadence table; Master Plan "levels unlock in order" |
| 53 | MUST-FIX | L7-00 vs L7-08 | L7-00 Slide 2 + Q2; L7-08 Slide 2 + Q2 + FLOOR_CHECK; L7-15 scorecard mark 1 | Same prompt, two different right answers. L7-00 Q2 "It's their first time. What do you tell them?" → **four** things ("A 30-day warranty on everything, the clearance section, free layaway, and a mobile app"). L7-08 Q2, same situation → **three** ("a 30-day warranty on everything, free layaway, and an app"); L7-08's distractor list omits clearance and its Floor Check scores "the new-customer pitch (30-day warranty on everything, free layaway, the mobile app)". Joshua's 10/13 greeting script is three; the "four things every customer hears before they leave" (D17) adds clearance. The lessons never say these are two different moments. | (free) L7-00 Q2 correct option → "A 30-day warranty on everything, free layaway, and a mobile app to pay and shop from anywhere"; L7-00 Slide 2 bullets → three, and add a fourth bullet "Before they leave, every customer also hears about the clearance section". (narration, Joshua's voice, ~60 chars) Slide 2 `say`: "…a thirty day warranty on everything, free layaway, and a mobile app to pay and shop from anywhere. Before anyone leaves, they also hear about our clearance section." L7-08 Slide 2 add bullet: "Clearance joins the list before they leave — that's the four things from 7.1". Keep L7-15 scorecard as is (it already separates mark 1 and mark 8). | Brief "Known facts" greeting; Review D17 |
| 54 | MUST-FIX | L7-07 | GATE (rendered on the start card as "Deadline: …") | "Final lesson of Level 7. Passing it, with L7-05 and L7-06 Floor Checks and five passed phone sims, completes the Certified Valley Pawn Sales & Loan Associate credential…" — Level 7 has eight more lessons; L7-00 tells the learner the level "ends with a ten-minute role-play". Stale text from before 7.8–7.15 existed, shown to every learner. | (free) "Lessons 7.1–7.7, with the eBay Floor Checks and five passed phone sims, are the service half of Level 7. Lessons 7.8–7.15 and the role-play finish the Certified Valley Pawn Sales & Loan Associate credential (keys eligibility at 90 days)." Adjust after the finding-52 decision. | L7-00 Slide 3; L7-15 gate |
| 55 | MUST-FIX | L7-04 vs L7-12 | L7-04 Slide 5 bullet 1 + narration; L7-12 Slide 5 bullets 2–3, Q4 | L7-04: "Ask every customer… at the end of the visit." L7-12: "Ask for the Google review mid-transaction while they're happy, not at the door"; Q4 marks "As they walk out the door with their bag" wrong. A learner who did what 7.4 said fails 7.12 Q4. The huddles (6/1, 7/6) say mid-transaction, so 7.4 is the one to change. | (free) L7-04 Slide 5 bullet 1: "Ask every customer, the same way, in the middle of the visit while they're happy — not at the door". (narration, ~45 chars) "Ask every customer, the same way, while they're at the counter and happy." Also align the mechanism: 7.4 says "the sign and the review text Chekkit sends", 7.12 says "the QR card on the counter" — bullets in both: "point to the QR sign; Chekkit also texts them the link". | Huddle 2026-06-01, 2026-07-06; L7-12 sources |
| 56 | MUST-FIX | L7-07 vs L7-09 / L7-10 | L7-07 Slide 5 bullet 2 + narration ("pointed him to a music store, lesson programs, Marketplace and eBay"), Q5 correct ("point him to places that might sell them"); L7-09 Slide 5 bullet 4 ("Never send them to a competitor. Not another shop, not Marketplace. If they ask where else, we don't know"), Q4; L7-10 Slide 5 bullet 2 ("Never recommend a competitor. Not another shop, not Marketplace, not eBay"), Q6 | 7.7 praises referring a customer to Marketplace and eBay; 7.9 and 7.10 forbid naming Marketplace or eBay. The intended distinction (someone **selling** what we don't take vs a **buyer**) is never stated, and Preston's newest rule (KB never-recommend-competitors, 2026-10-09, "including Facebook Marketplace") postdates the 7.7 call. | (free) L7-07 Slide 5 bullet 2: "Give a real referral: a music store, a lesson program, a collector — never a place that competes with us"; Q5 correct option: "Say no early with the real reason, suggest who might want them (a music store, a lesson program), and say what we pay most for". (narration, ~40 chars) L7-07 Slide 5: "…then pointed him to a music store and some lesson programs." L7-09 Slide 5 bullet 4: "Never send a buyer to a competitor — not another shop, not Marketplace, not eBay". | KB never-recommend-competitors-9b313c90 |
| 57 | MUST-FIX | L7-15 | Q7 | "It's day 6. You've finished the course but your manager hasn't scheduled the role-play yet. What's expected of you?" → "Tell your manager today so the role-play happens by day 7". The rule "Not done by day 7? Tell your manager the same day" is in the gate text and HR-2026-10 only; no slide teaches it. Question tests untaught content (brief rule 1). | (free) Slide 6 add bullet after the pass line: "Not done by day 7? Tell your manager the same day — that's on you, not just them". Keep Q7. Re-time per finding 52. | HR-2026-10 |

### L7-00 Welcome to Level 7

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 58 | NOTE | L7-00 | Slide 3 | "Finish Level seven and you're a Certified Valley Pawn Sales and Loan Associate." Correct, and the only place the credential's name is spoken to the learner before 7.7's gate. Good. | None (see 53 for Slide 2). | — |

### L7-01 How we sell

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 59 | NOTE | L7-01 | Objectives | "greet every customer, get the item floor-ready, pitch benefits before features, handle a price objection, and discount inside your authority" — five objectives for a nine-minute lesson; the brief's standard is one. It functions as the level's advance organiser for 7.8–7.12, which is a legitimate design if the level says so. | (free) Objectives: "see the whole sale in one pass — greeting, floor-ready item, pitch, objection, discount — before lessons 7.8 to 7.12 go deep on each". | Brief §1 |
| 60 | NOTE | L7-01 | Slide 4 narration; L7-11 Slide 4; L7-12 Slide 1, Q1, Q6 | The speaker-without-a-charger story is told in 7.1, 7.11 and 7.12 (twice tested). Three tellings in one level reads as padding. | (free, L7-11 bullet) "Throw in the add-on they need — a strap, a case — not twenty dollars off". (narration, defer) vary the 7.11 example. | — |
| 61 | NOTE | L7-01 | Slide 2 | "The pricing list (the queue of new items waiting for a price in Bravo)" — jargon defined on first use and again in Q1's stem. Model practice. | None. | — |

### L7-02 Free layaway and the 30-day warranty

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 62 | SHOULD-FIX | L7-02 | Slide 8 bullet 1, key point 6 | "It needs an account with an email. No email, no warranty or return." The source (KB warranty-requires-account-with-email) makes the account a condition of the **warranty**; §05.08 conditions a **return** on the receipt and original condition, not on an email. "or return" extends policy. Q5 tests warranty only. | (free) Bullet: "It needs an account with an email. No email, no warranty"; key point: "Returns need the receipt and original condition; the warranty needs an account with an email". Narration ("To qualify, the customer needs an account with an email on file") can stand. | P&P §05.08; KB 4db3aad0 |
| 63 | NOTE | L7-02 | Slides 8–9 vs L7-10 Slide 4/Q7 and L7-15 Slide 3 | 7.2 separates returns (7 days cash, 8–30 credit) from warranty (stops working → exchange or credit). 7.10 Q7 stem "The 30-day warranty on a sale works like this:" → "Inside 7 days, money back…; days 8 to 30, store credit" and 7.15 narration "Explain the warranty, seven days money back the way they paid, then store credit" describe the **return** rule and call it the warranty. The company's own KB wording conflates them, so this is a terminology choice, not an error — but 7.2 and 7.10 teach it differently. | (free) L7-10 Q7 stem: "Our 30-day return-and-warranty window works like this:"; L7-10 Slide 4 bullet 2: "Every sale carries our 30-day return and warranty window: …". L7-15 key point 3 likewise. | KB refund-and-warranty-policy |
| 64 | NOTE | L7-02 | Slide 4 | Six bullets (tiers + rule of thumb + watches + firearms). | (free) Move "A firearm on layaway isn't transferred until paid in full…" to Slide 5 (it's about the term/pickup). | Brief §3 |
| 65 | NOTE | L7-02 | Quiz | Q2 (63 days), Q3 (34 days), Q8 ($700 generator) are strong faded-practice items on the numbers taught. | None. | — |

### L7-03 The phone standard

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 66 | MUST-FIX | L7-03 | GATE ("No live phone until five AI role-play sims are passed"), Slide 1 bullet 3 and narration ("Before you take a live call, you pass five role-play sims against this standard"), key point 5 | The lesson promises a simulated-customer role-play that, per the lesson's own OPEN items, has no rubric or pass mark written and is not among the nine TalentLMS courses. If it does not exist at launch, the gate blocks every new hire from the phone indefinitely and the learner is told to do something that isn't there — a broken experience. | Confirm the sim exists and is linked from Level 7. If not: (free) GATE → "Before your first live call, your manager runs five practice calls with you against this standard"; key point 5 likewise; (narration, ~70 chars) Slide 1: "Before you take a live call, you'll run five practice calls with your manager, scored against exactly this standard." That also gives the Store Manager a Floor Check to tap (L7-03 currently has none). | L7-03 OPEN items; Master Plan v2 |
| 67 | SHOULD-FIX | L7-03 | Slide 2 bullet 2 | Sample greeting names a store and a person: "'Thank you for calling Valley Pawn in Harrisonburg, this is Sam. How can I help?'" while Q1 uses "[town]" and "[name]". | (free) Bullet: "'Thank you for calling Valley Pawn in [your town], this is [your name]. How can I help?'" Narration ("Harrisonburg… Sam") can stand as an example. | LESSON_SPEC (names) |
| 68 | NOTE | L7-03 | Slide 4 bullet 4 | "The target: a name and number on nine out of ten unfilled requests" — on screen, not spoken; Q3 why repeats the 90%. Fine. | None. | — |

### L7-04 Texting, loyalty and Google reviews

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 69 | NOTE | L7-04 | Slide 2 | Six bullets: two legal rules, transactional carve-out, company 18-month rule, Chekkit-only. Dense but each is one line. | (free) Merge bullets 1 and 6: "Every calling rule applies to texts. Customer texts go through Chekkit only — never your phone". | Brief §3 |
| 70 | NOTE | L7-04 vs L8-05 | Slide 2 bullet 2 vs L8-05 Slide 3 bullet 4 | "written opt-in on file" (7.4) vs "an opt-in recorded in Bravo or Chekkit" (8.5). Same rule, two adjectives. | (free) Both: "a recorded opt-in in Bravo or Chekkit". | P&P §07.06 |
| 71 | NOTE | L7-04 | Q3 stem | Names Harrisonburg and Culpeper — already on the §4 deferred list. | — | Review §4 |

### L7-05 Listing on eBay

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 72 | SHOULD-FIX | L7-05 | Slide 1 bullet 4 vs Slide 5 bullet 3 | Slide 1: "NEVER on eBay: … plain gold and silver sold by weight." Slide 5: "Gold, silver, bullion and coins sold by weight are never repriced online." A learner asks: if by-weight metal is never listed, what is there to not reprice? The answer (bullion and coins can be listed; by-weight **jewelry** cannot) is implicit. | (free) Slide 5 bullet 3: "Bullion and coins — anything sold by weight — are never repriced online. They're already priced at melt". Q4 (silver bar) already matches. | P&P §5A rules 2 and Precious-Metal Jewelry |
| 73 | NOTE | L7-05 | Slide 2 narration | "Something like D C D seven seventy one, or A twenty-four eighty-two" — the second example (an Apple model number) is not on the bullet; fine spoken, but the bullet shows only DeWalt. | (free) Bullet 3: "The manufacturer's model number stays (DCD771, A2482)…". | — |
| 74 | NOTE | L7-05 | Q6 | Pure recall ("What's the photo standard") in an otherwise scenario quiz; acceptable, and the Floor Check verifies it live. | None. | — |

### L7-06 Shipping eBay orders

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 75 | NOTE | L7-06 | Whole lesson | 4 slides, 340 words, 7 questions all traceable, Q1 correctly reasons the Friday/2-business-day case. No findings. 80% of 7 = 6/7. | None. | — |

### L7-07 Service recovery

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 76 | SHOULD-FIX | L7-07 vs Level 3 rule | Slide 4 bullet 3 + narration; Q3 | Example and question are built on a **fee waiver**: "told a customer an extension fee couldn't be waived… your manager tells you it could have been." Level 3 (D4) teaches "you never change a rate or a fee; exceptions only through the Market Manager, entered in Bravo." The learner just learned fees are never changed; now a Store Manager waives one. Fee-waiver authority is an OPEN item nobody has written. | (free) Q3 → a non-fee mistake: "This morning you told a customer a cancelled layaway meant losing what she'd paid, and she left upset. This afternoon your manager reminds you it's store credit. What do you do?" (answer unchanged: call her back). (narration, ~250 chars, or keep until the fee-waiver rule is written) Slide 4: "One of our associates told a customer the wrong rule about a layaway refund. Then he checked, found out he was wrong, and nobody asked him to, but he called the customer back…" Bullet 3 likewise. | Review D4; L7-07 OPEN fee-waiver authority |
| 77 | NOTE | L7-07 | Slide 2 narration | "On one call, a man had been asked at the counter whether an award his mother gave him was really his." Anonymised, specific, and the clip is attached. Good use of a real call. | None. | — |

### L7-08 Your first thirty seconds

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 78 | SHOULD-FIX | L7-08 | Q4 correct option | "'She's off today. I'm Josh. The manager and I work every deal together…'" — "Josh" is the CEO's name in a company of five stores; a new hire reads it as Joshua. | (free) "I'm Alex." | Voice |
| 79 | SHOULD-FIX | L7-08 | Q2 why (correct option) | "(CEO greeting script 2026-10-13; §04.01)" — a dated attribution that the build's filter does **not** strip (three-word, capitalised prefix defeats the date regex), so the learner sees it. | (free) "(§04.01; §07.04)". | LESSON_SPEC (never dates); build INTERNAL_ATOM |
| 80 | SHOULD-FIX | L7-08 | Q2 distractor 3 | 41-word distractor: "Ask the three loan-side questions: loan or sell, how much do you need, and whether she's done business here, so you know what kind of visit this is before you say anything else about the store" against a 25-word right answer. Padding with a justification is a test-wiseness cue (see program finding 96). | (free) "Ask the three loan-side questions first — loan or sell, how much do you need — so you know what kind of visit it is". | Brief §2 |
| 81 | NOTE | L7-08 | Slide 3 bullet 4 / key point 6 | "Tell them we buy gold. Ask if they have other items and say what we pay the most for" — the "what we pay the most for" list differs by lesson: 7.9 "gold, jewelry, coins, firearms and ammo"; 7.13 "Gold, jewelry and coins are at the top"; 7.14 "Guns and ammo are at the top"; 8.2 "High-end brands in any category sit at the top". Each is true; together they are four different "tops". | (free) One canonical bullet in 7.8 Slide 3: "What we pay the most for: guns and ammo, gold and jewelry, coins, high-end brands, new-gen consoles, big toys"; other lessons say "the list from 7.8". | KB what-we-pay-most-for-5be0d81b |

### L7-09 Ask before you pitch

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 82 | SHOULD-FIX | L7-09 | Slide 2 | Six bullets, 138-word narration, five questions plus the say-it-back step — the heaviest selling-skills slide and not on the §4 deferred list. | (free now) Move bullet 6 ("Then say it back…") to Slide 3 as its first bullet. (narration, ~900 chars, defer) Split "The five questions" / "Say it back" at the next cycle. | Brief §3; Review §4 |
| 83 | NOTE | L7-09 | Slide 4 vs L7-13 Slide 2 | Identical jewelry-question content (metal, occasion, stone, budget fourth, two or three pieces, one at a time) in two lessons four lessons apart; Q2 (7.9) ≈ Q1 (7.13). Intentional repetition is fine; verbatim duplication reads as padding. | (narration, defer) 7.9 Slide 4 becomes a one-bullet pointer: "Jewelry has its own three questions — lesson 7.13". | — |
| 84 | NOTE | L7-09 | Q4 why (distractor 1) | "(KB never-recommend-competitors)" — stripped by the build; fine. The item itself is correct once finding 56 is applied. | None. | — |

### L7-10 Show it like you own it

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 85 | NOTE | L7-10 | Q6 vs L7-11 Q7 | Both: customer cites a lower eBay price → "here, tested, warrantied, today; where were you hoping to be?" Same scenario, adjacent lessons. | (free) Change L7-10 Q6 to a demo-focused item: "A customer asks to see a drill run. The battery is dead. What do you do?" → charge it or swap a battery before the demo; never demo a dead tool. | — |

### L7-11 Price talk

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 86 | SHOULD-FIX | L7-11 | Q1 and Q8 | Same question twice in one quiz: Q1 "'Come on, what can you really do on this?'" → "Where were you hoping to be on it?"; Q8 "'What's the best you can do?'" → "Where were you hoping to be?" with the same three distractor types. | (free) Replace Q8 with the untested rule from Slide 1: "A coworker just rang a $200 speaker at $120 to close it. The tag had the normal room in it. What does that tell you?" → "The tag was set with about 10% of room; a 40% cut means the tag was wrong, not the customer — flag it for the manager". | Slide 1 bullet 3 |
| 87 | NOTE | L7-11 | Slide 3 | Six bullets, 134 words, 13 sentences. | Deferred-split candidate: "Your limit" / "Own the deal". | Review §4 |

### L7-12 Finish the sale

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 88 | NOTE | L7-12 | Slide 2 bullet 3 | One bullet holds five category lists ("Consoles: controller, game, headset · Tools: … · Instruments: … · Firearms: case, lock, ammo"). On a slide it is a wall; on a counter card it is useful. | (free) Keep the bullet but add the add-on list to the counter job aid (program finding 101). | Brief §6 |
| 89 | NOTE | L7-12 | Q2 vs L7-02 Q5 | Same scenario (customer refuses email) and answer (explain the warranty). 7.12 adds the D55 fallback ("ring it, and tell them plainly…"), which is the useful increment. | None. | Review D55 |

### L7-13 Selling jewelry from the case

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 90 | MUST-FIX | L7-13 vs L5-03 | Q7 whys | Correct-option why: "…the price is FIRM; scrapped at two years"; distractor why: "jewelry over two years goes to scrap, but until then it's sold as jewelry". L5-03 Slide 6, Q8 and §06.03 teach 30% at one year, six months in clearance, scrap at 1.5 years, and L5-03's sources mark the 2-year KB entry as the superseded half of a KB CONFLICT. The learner is told 1.5 years in Level 5 and 2 years in Level 7. | (free) Q7 correct why: "The clearance policy: marked 30% under the estimator and that price is firm; after six months in clearance it goes to scrap (Level 5)". Distractor why: "Clearance is 30% under the estimator. It is sold as jewelry until the aged schedule sends it to scrap". | P&P §06.03; L5-03 OPEN (KB CONFLICT) |
| 91 | NOTE | L7-13 | Q3 | Arithmetic checks: $520 = 20% off $650; $300 = 54% off. Good numeric distractors. | None. | — |

### L7-14 Selling a firearm

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 92 | NOTE | L7-14 | Q5 | Correct: "'I can't talk inventory by phone, but come in…'" to "Do you have any 9mm pistols in right now?" — stricter than the taught rule (never confirm a **specific** firearm is on the premises). Consistent with POLICY_GAPS #2's proposed wording, but it tells a gun store it cannot say "we carry handguns" on the phone. A policy choice for Preston, not an error. | Preston to confirm whether a category-level answer ("we always have handguns in the case; come see them") is allowed; if so, change the correct option. | POLICY_GAPS #2; L1-05 |
| 93 | NOTE | L7-14 | Slide 5 | Six bullets, 158 words. | (free) Merge bullets 4 and 5 ("Multiple handguns: the §04.02 protocol. After the sale, 'my gun won't fire' goes the way 6.6 teaches"). | Brief §3 |
| 94 | NOTE | L7-14 | GATE | "Level 6 (Firearms) must be complete before this lesson is assigned" — must stay in Level 7, not in any week-one course (see 52A). | — | — |

### L7-15 Ask for the sale, your numbers, the role-play

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 95 | SHOULD-FIX | L7-15 | Slide 6 (12 bullets) | The manager's scorecard is rendered as a 12-bullet slide with a two-sentence narration. It is a job aid, not a lesson slide: the learner can't take it to the floor and the manager has nothing to mark. render_check should confirm 12 bullets even fit. | (free) Keep the slide, and publish the same ten marks as a one-page printable "Role-play scorecard" (date, trainee, manager, pass 8/10 + three starred, initials) linked from the lesson and the New Hire Training Tracker — program finding 101. | HR-2026-10; L7-15 FLOOR_CHECK |
| 96 | NOTE | L7-15 | Slide 4 narration | "You can see where you stand yourself in Bravo, and the key points tell you where to look." Narration defers to text for the Bravo path; Q5 tests the path. Acceptable (a menu path is better read than heard). | None. | — |

---

## Level 8 — Advanced and annual

Annual framing (brief §4): L8-00 says "Everyone repeats the three annual lessons every year" and nothing else — no month, no due date (OPEN in all three lessons), and the three annuals sit inside the same TalentLMS course as three one-time advanced lessons, so "repeat every year" has no mechanism. The three annual lessons also open with retrieval stems written for a second-year learner ("A year since your last recert", "Last year's core rule…") that a 60-day new hire sees first.

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 97 | MUST-FIX | L8-03 Q1, L8-04 Q1, L8-05 Q1 | Stems | "A year since your last recert. A coworker makes a remark…"; "Last year's core rule, one more time. At close you notice…"; "Last year's core rule first. During an outreach call…". Every new hire takes these in their first 90 days with no "last year". The retrieval-practice intent is right; the framing is wrong for half the audience. | (free) "The core rule first." / "Start with the rule you must never get wrong." — or drop the lead-in sentence. | Brief §4 (annual framing); L8-00 Slide 3 |
| 98 | SHOULD-FIX | L8-00 | Slide 3, Objectives | Objective: "say when each one is due." Slides say only "every year" and "first ninety days"; no due date is taught because none is set. | Set one recert window and teach it: (free) Slide 3 bullet: "Annual lessons are reassigned every January, due by January 31 — same day as your gun-safety recert". (narration, Joshua's voice, ~70 chars) "Everyone repeats the three annual lessons every January, due by the thirty-first." | HR-2026-05 §7 (gun safety Jan 31); L8-03/04/05 OPEN due date |
| 99 | SHOULD-FIX | Level 8 structure | Course 134 (Level 8) | Advanced one-time lessons (8.1 title pawns, 8.2 watches, 8.6 handbags) and annual recerts (8.3, 8.4, 8.5) share one course, in an order that puts handbags after the annuals. Re-assigning the course yearly re-assigns title pawns too; not re-assigning it means the annuals never recur. | (free in TalentLMS) Reorder Level 8 as 8.1 title pawns, 8.2 watches, 8.3 handbags, then the three annuals; and create an "Annual Recertification" course containing 8.3–8.5 (and the gun-safety verification task) that is assigned every January with the Jan 31 due date. Course count: see finding 52 (Free-plan limit of 10). No narration changes: L8 narration carries no lesson numbers. | Master Plan v2 annual recerts; ONBOARDING_FLOW "Yearly" row |

### L8-00 Welcome to Level 8

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 100 | NOTE | L8-00 | Q1–Q3 | All three mc recall of the intro's own content (allowed for intros). Q2 distractor "Watches, jewelry and high-end brands" misnames 8.2 ("Watches and high-end brands"). | (free) "Watches and high-end brands". | — |

### L8-01 Title pawns

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 101 | NOTE | L8-01 | Slide 2 narration → Q8 | Worked example in narration ("If they bring home two thousand a month, the renewal shouldn't be over six hundred") then Q8 fades it ($2,000 take-home, $750 payment). Exactly the worked-example → practice pattern the brief asks for. Model lesson for alignment: all 8 items traceable, both thresholds (40/50, 30%) and both approvals (MM on bikes/boats, CEO on all) tested with the inverted-rule distractor each time. | None. | — |
| 102 | NOTE | L8-01 | Slide 4 bullet 4 vs key point 4 | "Get Preston, or expect a no" (bullet) vs "red flags go to the Market Manager" (key point). Same person. | (free) Bullet: "Get the Market Manager, or expect a no". | — |

### L8-02 Watches and high-end brands

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 103 | MUST-FIX | L8-02 vs L4-03 / L7-05 | Slide 2 bullet 1 + narration ("If it was an auction, look for more than one bid"), key point 2 ("auctions with more than one bid"), Q2 distractor why ("on auctions look for more than one bid") | L4-03 and L7-05 teach comps from sold listings "with at least one bid"; L8-02 says "more than one bid". The 10-14 review (D22) recommended bringing L8-02 back to "at least one" and the lesson still carries "more than one" in bullet, key point and why. Learner-visible inconsistency on a pricing rule. | (free) Bullet 1: "Sold listings, not active ones. Auction? At least one bid — in used condition"; key point 2 and Q2 why to match. (narration, ~40 chars, defer) "look for at least one bid, so the price was actually tested". | Review D22; KB comp-methodology-sold-with-bids |
| 104 | NOTE | L8-02 | Q2 | A handbag comp question in the watch lesson, before the handbag lesson (8.6). It tests Slide 2's general comp rule, so it is taught; but the sequence (watches → annuals → handbags) is what makes it feel early. Resolved by the reorder in finding 99. | — | — |
| 105 | NOTE | L8-02 | Terminology | This lesson says "Market Manager" throughout (10×) and never "Preston"; Levels 5–6 say "Preston" ~400 times and "Market Manager" ~110 times. Both are correct; a role title survives a personnel change, a name is faster at the counter. | (free in bullets/whys) Program rule: "Preston, the Market Manager" on first mention in each lesson, then either. Narration untouched. | LESSON_SPEC (names where the person is the one to call) |

### L8-03 Harassment, respect and equal opportunity

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 106 | SHOULD-FIX | L8-03 | Slide 7 bullets vs narration; Q7 | Narration adds "If you're a manager and someone asks you, point them to Joshua. Don't say no yourself." No bullet carries it, and Q7 ("The manager wants to say no…") tests exactly that line. Heading/bullets/narration disagree on a tested point. | (free) Add bullet 5: "Managers: never say no yourself — send the request to Joshua". | Handbook — Religious Accommodation Policy |
| 107 | NOTE | L8-03 | Sources | Cites "Employee Handbook v2026.5"; the governing file is v2026.6 and a v2026.7 exists on disk. Before the first annual assignment, re-verify the reporting chain, accommodation wording and third-party rule (D75) against v2026.7. | Policy seat / next pass. | Brief Files note |
| 108 | NOTE | L8-03 | Q3 | "You're a Store Manager…" asks an associate to take a manager's seat. Legitimate (it tests the witness/supervisor duty) and the only way to test it in a company-wide recert. | None. | — |

### L8-04 Protecting customer information

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 109 | SHOULD-FIX | L8-04 | Slide 6 | Five bullets of statutory clocks (AG no minimum, 1,000 → credit bureaus, FTC 30 days at 500+, lost ID may not trigger, clock at discovery) over 131 words — the legalese the spec says to keep out of narration, and only "same hour" and "clock starts at discovery" are tested. | (free) Three bullets: "A breach starts legal clocks: Virginia requires notice to customers and the Attorney General without unreasonable delay" / "Federal rules add a 30-day clock at 500+ customers" / "The clock starts when we discover it — not when we're sure. Our same-hour rule covers everything". Narration can stand until the next cycle. | LESSON_SPEC voice rule |
| 110 | NOTE | L8-04 | Slide 2 bullet 3 vs L6-05 Q3 / P&P §08.02 | "Account details go to the verified account holder only. Not an ex, a relative or a friend" — the spouse question (§08.02 allows spouse/attorney; the 9/28 draft policy says holder only) is deliberately untested. Consistent with the OPEN; no learner-visible conflict because L6-05 Q3 lets a spouse **pay**, not learn details. | None until Joshua approves the Account Details policy. | L8-04 OPEN |

### L8-05 Calling and texting customers

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 111 | SHOULD-FIX | L8-05 vs L7-04 | Q1, Q3, Q4, Q5, Q6 | Five of eight items are the L7-04 items with the surface changed only slightly: 9:15 PM Friday (L7-04: 9:20 PM); two years inactive (same); receipt phone number vs "never opted in" (same rule); buddy's tools on a referral card vs friend's jewelry (same); "take me off your list" vs "STOP". For the annual cycle that is intended retrieval; for a new hire taking both inside 90 days it is the same quiz twice. | (free) Vary the retrieval cues so the rule, not the stem, is recalled: Q4 → an automated Chekkit campaign scheduled for 7:45 AM; Q5 → a customer who opted in at Culpeper two years ago and hasn't been back; Q6 → a coworker proposes texting a referred person "just the address". | Brief §1 (spaced, interleaved review) |
| 112 | NOTE | L8-05 | Slide 3 | Six bullets, 134 words — already on the §4 deferred split list. | — | Review §4 |
| 113 | NOTE | L8-05 | Slide 1 bullet 4 | "every bad call or text can cost $500 to $1,500" — a statutory figure in narration outside the firearms/records exception. Motivational and accurate (TCPA); keep, but it is the kind of number the spec says to cite in sources. | None. | 47 U.S.C. § 227(b)(3) |

### L8-06 Handbags

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 114 | SHOULD-FIX | L8-06 | Q7 distractor 1 why | "Preston: 'Make sure we are sticking to the name brands for these. The brand is what sells them.'" — a quoted, attributed rule in learner-facing feedback (the quotation is outside the parenthetical, so the build's filter keeps it). | (free) "Name brands only — the brand is what sells them. Unbranded bags sit." | LESSON_SPEC (never attribute) |
| 115 | NOTE | L8-06 | Q1, Q3–Q8 whys | "(our handbag process)" survives the filter and appears to the learner six times. Harmless, slightly odd. | (free) Drop the parenthetical. | build INTERNAL_ATOM |
| 116 | NOTE | L8-06 | Slide 4 narration | "a discount store like Ross" — a named retailer in narration; fine (not a competitor recommendation). | None. | — |
| 117 | NOTE | L8-06 | Quiz | 8 items, all traceable, 6 scenarios; Q2 (creed decoding) and Q5 (no serial → pass) are good discriminating items. | None. | — |

---

## Program-level findings for Levels 5–8

| # | Severity | Lesson/File | Where | Finding (exact text) | Correction | Source |
|---|---|---|---|---|---|---|
| 118 | SHOULD-FIX | All graded lessons L5–L8 (and program-wide) | `pass_percent: 80` with 6–9 questions | 80% is never the real bar: 6 questions → 5/6 (83%); 7 → 6/7 (86%); 8 → 7/8 (87.5%); 9 → 8/9 (89%). In every graded lesson the effective rule is "miss at most one", and the start card says 80%. Learners who miss two of eight (75%) will be told they failed an 80% test. | Either state it honestly on the start card — "You can miss one question" — or set 10 questions where 8/10 = 80% is meant. Recommendation: keep 6–9 items, change the player's pass line to "Pass: miss no more than one", and keep `pass_percent` as the SCORM threshold. Zero narration cost. | Brief §2 passing math |
| 119 | SHOULD-FIX | All quizzes L5–L8 | Option construction | Across 258 items the correct option is **never** the longest (the 10-14 fix worked) but is the strictly shortest in 99 (38%), and in 17 items two or more distractors carry a trailing justification ("…since a two-item buyer has earned the full discount and it's inside your limit", "…so he can see we're fair", "…they're small") while the correct option is a plain instruction. Test-wise learners pick the crisp unjustified option. Examples: L5-03 Q7, L6-02 Q6, L6-04 Q3, L7-01 Q5/Q7, L7-04 Q8, L7-05 Q4/Q5, L7-06 Q5, L7-07 Q5, L7-08 Q2, L7-09 Q4, L7-10 Q4/Q5/Q6, L7-14 Q6, L8-02 Q7. | (free) In those 17 items, move the justification from the distractor text into its `why` and keep options to the action alone, matching the correct option's grammar. Add a "correct is shortest" count to check_answer_bias.py alongside "longest". | Brief §2; check_answer_bias.py |
| 120 | NOTE | All quizzes L5–L8 | Answer position | Correct answer sits in position 2 in 202 of 258 items (78%); in Level 7, 109 of 116 (94%). The player shuffles, so no learner effect; but the JSON pattern means an un-shuffled export (TalentLMS native test, printed quiz) would leak it. | None required; note for anyone exporting questions outside the SCORM player. | Brief §2 |
| 121 | SHOULD-FIX | L5-L8 narration | Every `say` | Spec: "2–4 short spoken sentences". Measured: median slide in L5–L8 is 90 words / 8 sentences; 31 slides exceed 110 words; the longest are L6-05 s7 (165), L7-14 s5 (158), L6-02 s2 (146), L7-09 s2 (138), L7-11 s3 (134), L8-05 s3 (134), L6-04 s5 (131), L8-04 s6 (131), L6-05 s4/s6 (130/129). Most are already in the §4 deferred list; those that are not are flagged in findings 6, 23, 32, 44, 48, 82, 87. Cognitive-load risk is real on L6-02 s2 and L6-05 s7 specifically because they carry the most legally consequential content. | Hold for the post-Oct-28 cycle as planned; prioritise L6-02 s2 and L6-05 s7 in that cycle. Bullet trims now (findings 33, 46) reduce on-screen load at zero cost. | LESSON_SPEC; Review §4 |
| 122 | NOTE | L5-L8 headers | `minutes` | Stated minutes exceed narration + quiz in most Level 5 lessons by 2–3 minutes (finding 7) and match within a minute elsewhere. Level 7 lessons with call clips are accurate. | (free) L5-01 10, L5-02 9, L5-04 10. | — |
| 123 | SHOULD-FIX | Level 6 (program) | Refresher | The highest-risk content in the Academy (A&D deadlines, 4473, VSP check, 3310.4, phone rule) has no annual refresher; the three annuals are HR/privacy/telemarketing and the gun-safety recert is an external certificate, not a procedure test. | Add a fourth annual: a 10-question "Firearms rules refresher" drawn from L6-01–L6-05 (one item per critical rule: A&D clocks, Section B ownership, 30-day validity, VA one-handgun gate, 3310.4 incl. redemption, delayed/denied scripts, third-party redemption, phone/voicemail rule, missing-gun same hour, trace 24 hours). Assign in the January window with the others. Zero new narration (test-only unit). | Brief §6; 27 CFR 478 |
| 124 | SHOULD-FIX | Level 7 (program) | Certification capstone | The credential is earned by passing fifteen lessons one at a time. There is no cumulative check, so nothing measures retention of Level 1–6 rules at certification time (Kirkpatrick L2 is per-lesson only). | Add a 20-item test-only unit "Certified Associate exam" at the end of Level 7: one scenario per level's critical rules (loan timeline, discount authority, phone rule, firearms phone/third-party, melt/stones, 4473 ownership, layaway tiers, texting consent…), reusing existing items with changed surface features; pass "miss no more than two". Cheap (no narration), and it gives the 90-day review a number. | Brief §6; ONBOARDING_FLOW (certificate at Level 7) |
| 125 | SHOULD-FIX | L5, L6, L7-12, L7-15, L8-06 (program) | Job aids | Lessons carry counter reference data that nobody can recall from narration: karat factors and the melt formula (L5-02), stamp table and acid reads (L5-01), coin/bar specs (L5-01/05), mm→carat (L5-04); the 4473 sequence (L6-02 Floor Check); the phone/voicemail rule (L6-03/05, L7-03); the add-on list (L7-12); the role-play scorecard (L7-15); handbag brand → number location → pass rule (L8-06). The 10-14 review already assumes a "spec card" exists (D32). | Publish five one-page laminated/PDF job aids, each built from text already in the lessons (no new content, no narration): (1) **Metal & stone card** — formula, 10K–24K factors, stamps 417/585/750/916/999 + GP/GF/GE/HGE/RGP/"1/20 12K", acid reads, Eagle/Maple/Krugerrand/Buffalo weight+diameter, 4.1/5.2/6.5 mm → ¼/½/1 ct, "no spot sheet, no number"; (2) **4473 counter checklist** — the nine L6-02 Floor Check steps as a numbered list plus 30-day/Section D; (3) **What you can say by phone** — verify first; "your check is finished, you can come in"; never approved/denied/the gun/on premises; voicemail rule by call type; (4) **Finish-the-sale card** — needs-it-to-work vs makes-it-better by category, the four things, email line, review ask; (5) **Role-play scorecard** — ten marks, three starred, pass line, date/initials. Link each from its lesson's Floor Check text. | Brief §6; Review D32 |
| 126 | SHOULD-FIX | Build (player) | Start card label; Floor Check rendering | The start card renders `gate` as **"Deadline: "** + text. For L5-03 that reads "Deadline: … The Gold Scrap Bucket Naming Standard and the Jewelry Category Standard are separately signed through Gusto"; for L7-14 "Deadline: Level 6 (Firearms) must be complete before this lesson is assigned. This lesson is about the selling conversation…"; for L6-01 a 70-word legal paragraph. Most gates are not deadlines. Floor checks render as one paragraph (finding 36). | (free, build) Label "Gate: " (or "Before you start: "); render floor-check text split on ";" as an ordered list. Both are one-line changes in build_scorm.py's start-card and rFloor code and affect no narration. | build_scorm.py lines ~1120, ~1284 |
| 127 | NOTE | L5–L8 | Terminology audit | "Store Manager" 21× vs "your manager" 80× — acceptable (the second is the learner's own manager). "Preston" 399× vs "Market Manager" 110× (see 105). "P&P" is written "P&P" in bullets and spoken "P and P" in narration — correct for TTS. System names consistent: Bravo, Chekkit, Goldilocks, Gusto, VCheck, SP-65; Slack channels named in scope: #voicemails-calls-missed (L7-03), #compliance (sources only). No "#ask-handbook" in Levels 5–8. "Joshua" title drifts owner/CEO (finding 26). | — | Brief §5 |
| 128 | NOTE | L5–L8 | Narration voice | Contractions throughout; no bullets read aloud; "A T F", "I D", "V I N", "forty-four seventy-three" spelled for TTS; "Preston says" absent except L6-04 (finding 43); no dated references in narration found in scope. Legal numbers in narration are confined to firearms/records lessons plus the two noted (L8-04 s6, L8-05 s1). | — | LESSON_SPEC voice rule |

---

## Verdict

**Launch after fixes.** Levels 5–8 are substantively sound: 257 of 258 questions test what the slides teach, every graded lesson has at least six scenario items with rule-naming distractors, the firearms sequence is coherent, and Level 8's title-pawn lesson is a model of worked-example-then-practice. Nothing in this scope teaches a wrong law or P&P rule.

What must be fixed before Joshua's walk-through, all but two at zero narration cost: the Level 7 week-one timing conflict (52) and the stale "final lesson" gate on 7.7 (54); the three learner-visible contradictions inside Level 7 — first-timer pitch three vs four things (53), review ask "end of visit" vs "mid-transaction" (55), referrals to Marketplace/eBay vs "never name Marketplace" (56); L7-15 Q7 testing an untaught rule (57); the 1.5-year vs 2-year scrap clock in L7-13 (90); the "at least one" vs "more than one" bid rule in L8-02 (103); the acid-on-the-bars-slide misplacement in L5-01 (3); the eight-bullet 4473 slide (33); the "last year's recert" stems new hires will see (97); and the phone-sim promise if the sim does not exist (66). Total narration touched by the MUST-FIX set: roughly 300 characters (L7-00 s2, L7-04 s5, L7-07 s5), inside the Oct-28 budget.

The SHOULD-FIX set is mostly free quiz and bullet edits plus four program additions that a professional program would have on day one: honest pass-mark wording, the Annual Recertification course with a January 31 window, a firearms refresher and a certification capstone, and five counter job aids built entirely from text the lessons already contain.
