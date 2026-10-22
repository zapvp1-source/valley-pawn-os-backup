# A2 — Pawn industry operator & regulatory compliance review: Levels 5–8

Reviewer seat: pawn operator / FFL & Virginia pawnbroker compliance. Scope read in full: `ALL_LESSONS_DUMP.txt` lines 1890–4356 (L5-00 through L8-06, 37 lessons). Every company rule was checked against `sources/SOURCES_CURRENT.md` (P&P v2026.8 / Handbook v2026.6); legal statements were verified against the statute/regulation text or current reporting (citations in the last column). Worked numbers were recomputed.

Severity: **BLOCKER** / **MUST-FIX** / **SHOULD-FIX** / **NOTE**.

**#ask-handbook sweep (item 7):** no lesson, slide, bullet, key point or quiz question in L5-00 … L8-06 says "#ask-handbook" or "ask handbook". All Slack-bot references in scope already say "Goldilocks" (L7-02 S7, L7-03 S6/Q8, L7-04 S4/Q7, L7-15 S5/Q8). Nothing to change in this scope.

---

## Level 5 — Gold, Jewelry and Stones

### L5-00 Welcome to Level 5
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 1 | NOTE | L5-00 | S3, KEY_POINTS, Q1 | "No metal quote until Level 5 is passed; your manager watches you test" | Consistent with L5-01 Floor Check and Master Plan gate. No change. | Master Plan v2 |

### L5-01 Testing gold and silver
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 2 | MUST-FIX | L5-01 | S5 (coins & bars) bullet 5 and `say` last two sentences | "Acid on the slate is the standard confirmation. The Kee is an extra if you have one." sits on the COINS AND BARS slide, right after "Every coin and every bar: magnet, weight AND the Sigma tester". | Move the sentence to S3 (jewelry) or reword on S5: "For coins and bars the Sigma is the confirmation — acid is a surface test and a plated tungsten bar passes it." L5-05 Q2 `why` already says exactly that ("Acid is a surface test. A plated tungsten bar passes it"), so as written the two lessons contradict each other. One short narration line. | KB 6f888d88 (coins/bullion = magnet, weight, Sigma); L5-05 Q2 why |
| 3 | SHOULD-FIX | L5-01 | S3 bullet 3 / `say` | "Scratch deep enough to get under any plating, or file a small notch on the inside of the shank" | Add "with the customer's OK" — on a PAWN the piece is the customer's property and Va. Code § 54.1-4012 bars disfiguring property in pawn; a notch filed without consent is a complaint waiting to happen. Also applies to L5-05 S4 "file a notch inside the clasp or shank". | Va. Code § 54.1-4012; P&P §09.05 |
| 4 | SHOULD-FIX | L5-01 | S2 bullet 2 / `say` | "If it's attracted, it's not real gold" | Acceptable shorthand, but add "strongly" — a faint pull from a steel spring inside a clasp or a white-gold piece with nickel alloy can show slight attraction; the rule is "grabs the magnet = not gold". Keeps new hires from passing on real white gold. | Industry practice |
| 5 | NOTE | L5-01 | S5 | Coin specs "1-oz American Eagle: 33.93 g, 32.7 mm. 1-oz Maple: 31.1 g" | Correct (AGE 33.931 g / 32.70 mm; Maple 31.103 g / 30.00 mm). Add Maple diameter 30 mm to the bullet since the lesson says "right weight but wrong size = fake". | US Mint / RCM specs |
| 6 | NOTE | L5-01 | Q2 option 3 `why` | "You still read the markings and confirm with Kee or acid" | Fine; consistent. | — |

### L5-02 Melt math and the spot sheet
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 7 | NOTE | L5-02 | S2 worked example; Q1–Q3 | All numbers recomputed: 54.8/20 × 0.5833 × 4,000 = $6,392.97 ≈ $6,393 ✓; Q1 $1,166.60 ✓, distractors $23,332 (no ÷20) and $2,000 (no purity) ✓; Q2 $3,000 ✓, $2,333.20 ✓, $60,000 ✓; Q3 6.5/20 × 0.5833 × 4,000 = $758.29 ✓, $933.28 ✓. Purity table 0.4167/0.5833/0.75/0.9167/1.0 ✓. | No change. | Arithmetic |
| 8 | NOTE | L5-02 | Q2 | Four options where every other question in L5–L8 has three. | Harmless; drop "$4,000.00" if the team wants uniform three-option quizzes (the $23,332-style "no purity" distractor is already covered in Q1). | LESSON_SPEC (3-option example) |
| 9 | NOTE | L5-02 | Q8 | "melt works out to about $2,600 and the estimator offer is $1,300" (50%). | Consistent with the loan estimator rate; a BUY would be ~55% ($1,430) per KB 46a31d72, but since the percentage is explicitly "not yours to set" and untested, no change. | KB pay-percentage-estimator-set-46a31d72 |
| 10 | SHOULD-FIX | L5-02 | S6 `say` | "On a real call, an employee guessed … and came in thousands low. The customer said so, and he's gone." | Fine as anonymised story, but "Call 204" appears in the BULLET ("It happened on Call 204"). A call number means nothing to a trainee; replace with "It happened on a real call." | LESSON_SPEC §50 (anonymise) |

### L5-03 Scrap buckets and jewelry categories
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 11 | NOTE | L5-03 | S5 bullet 1 / `say` | "Virginia doesn't tax bullion and coins" | Correct today: Va. Code § 58.1-609.1(19) exemption (gold, silver, platinum bullion and legal-tender coins, no $ threshold) was extended by the 2026 budget act to **June 30, 2028**. Add a re-check date (mid-2028) to the lesson's sources; nothing learner-facing changes. | Va. Code § 58.1-609.1(19); 2026 Appropriation Act item 3-5.25 |
| 12 | NOTE | L5-03 | S6, Q8 | "30% off after 1 year on the floor, 6 months in clearance, then scrapped" | Matches P&P §06.03 exactly. **But see L7-13 #49** — that lesson still says "scrapped at two years". | P&P §06.03 |
| 13 | NOTE | L5-03 | S2 `say` | "For August twenty twenty six that's twenty twenty six dash oh eight GOLD" | A dated example is fine (it's the format, not a rule date). | — |

### L5-04 Diamond basics at the counter
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 14 | NOTE | L5-04 | S5, Q8 | "4.1 mm ≈ ¼ ct · 5.2 mm ≈ ½ ct · 6.5 mm ≈ 1 ct; 1 carat = 0.2 g" | Correct for round brilliants (standard chart 4.1/5.1–5.2/6.4–6.5 mm). | GIA size-to-weight chart |
| 15 | SHOULD-FIX | L5-04 | S4 bullet 3 / `say`; Q4 | "'LG' or 'Lab Grown' in front of the number = lab-grown" | Add "LGDR" and "LABORATORY-GROWN": IGI inscribes "LG", GIA inscribes "LGDR"/"LABORATORY-GROWN". A trainee reading "LGDR" against this list could treat it as a mined-stone report number. Bullet/why edit only. | GIA Laboratory-Grown Diamond Report inscription practice; IGI |
| 16 | SHOULD-FIX | L5-04 | S4 bullet 1 | "The diamond tester says 'diamond' for mined, lab-grown and, on a thermal-only unit, moissanite" | Correct and appropriately conservative. Add the one counter tell that costs nothing: "doubly-refractive/rainbow fire and a very light stone for its size = moissanite — loupe it". Optional. | Industry practice |
| 17 | NOTE | L5-04 | Q6 `why` | "Outside tools that value colored-stone jewelry off total weight overstate value" | The scenario is a ring with stones generally, not a colored-stone piece; change to "stone-set jewelry". Cosmetic. | KB fab0f465 |

### L5-05 Counterfeit tells
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 18 | SHOULD-FIX | L5-05 | S2 bullets 3–4 / `say` | "Tungsten is almost as dense as gold, so a plated tungsten bar weighs right. Measure it against spec: too thick or too wide is a fake" | Misleading: tungsten (19.25 g/cc) is within 0.4% of gold (19.32), so a tungsten-core bar also measures within mint tolerance. Dimensions catch lead/brass/copper cores; tungsten is caught by the Sigma (conductivity) and the ring/tap test. Reword: "Measuring against spec catches the cheap cores (lead, brass). Tungsten weighs AND measures right — only the Sigma and the tap test catch it. That's why the Sigma is never skipped on a bar." Q6 (34.5 mm Eagle) is still right because that is a light-metal fake. | Densities: Au 19.32, W 19.25 g/cc |
| 19 | SHOULD-FIX | L5-05 | S4 bullet 1 | "file a notch inside the clasp or shank" | Same consent point as #3. | Va. Code § 54.1-4012 |
| 20 | NOTE | L5-05 | Q5 marked answer | "Plated. Acid it, and if it fails, no deal" | The option states the conclusion before the test; acceptable because the `why` carries the reasoning ("The acid settles it"). Consider "Probably plated — acid it; fails, no deal." | — |
| 21 | NOTE | L5-05 | S3 / Q3 | "Sigma-test it through the holder" | Correct — the Sigma PMV reads through standard PCGS/NGC slabs. | Sigma Metalytics PMV documentation |

---

## Level 6 — Firearms

### L6-00 Welcome to Level 6
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 22 | NOTE | L6-00 | S3, Q3 | "Preston … is the call for every firearms question … Joshua … makes the ATF reports" | Consistent with L6-01 S6 and P&P §10.04/§09.07. | P&P §09.07 |

### L6-01 FFL basics and the A&D book
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 23 | NOTE | L6-01 | S3, Q2, Q3 | Acquisition "by close of the NEXT business day"; disposition "within SEVEN days"; pawns logged day of | Correct. 27 CFR 478.125(e). | 27 CFR 478.125(e) |
| 24 | NOTE | L6-01 | S4, Q1 | "4473s and the A and D record are kept until the business is discontinued … '20 years' is NOT a destruction date" | Correct **today** (27 CFR 478.129(b) as amended by RIN 2021R-05F, eff. 8/24/2022). **Heads-up:** ATF published an NPRM (Doc. 2026-08929, spring 2026; comments closed 8/4/2026) to restore a fixed 20- (or 30-) year retention; `regulations.atf.gov` shows the revised §478.129 as "Effective Date – Pending". Nothing changes for staff (company rule: nothing destroyed without Joshua), but add a re-check note to sources and keep the "never destroy on a calendar rule" framing. | 27 CFR 478.129(b); regulations.atf.gov/upcoming-regulation-page/478-129 |
| 25 | NOTE | L6-01 | S5, Q8 | "ATF trace request … answered within 24 hours" | Correct. | 27 CFR 478.25a |
| 26 | NOTE | L6-01 | S6, Q6 | "48 hours from discovery to report to ATF and the police … Form 3310.11" | Correct. | 18 U.S.C. § 923(g)(6); 27 CFR 478.39a |
| 27 | SHOULD-FIX | L6-01 | S1 bullet 1 / `say`; Q7 all three options | "not just Roanoke" / "Send the customer over to Roanoke" / "That's the old error the P&P corrected" | Teaches a retired rule by name and names two stores, which the spec forbids. Cheapest fix (no narration): rewrite Q7 stem as "A coworker says 'We can't — only one of our stores has the license'", drop "Roanoke"/"Waynesboro" from options and whys, and delete "That's the old error the P&P corrected". Leave the S1 narration if re-recording budget is tight (it is a one-off myth-bust). | LESSON_SPEC §50 |
| 28 | NOTE | L6-01 | S5 | "They're entitled to see our records and inventory during business hours" | Correct for Virginia pawn records (Va. Code § 54.1-4011) and ATF (18 U.S.C. § 923(g)(1)(B) — one warrantless compliance inspection per 12 months plus trace/criminal-investigation inspections). Company policy of immediate cooperation is the right teaching. | Va. Code § 54.1-4011; 18 U.S.C. § 923(g)(1)(B) |

### L6-02 The 4473, section by section
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 29 | **BLOCKER** | L6-02 | S6 bullet 1 and `say` ("a redemption counts the same as a sale"); KEY_POINTS bullet 5 ("Two handguns inside five business days, redemptions included: Form 3310.4"); FLOOR_CHECK; Q5 (marked answer + all three `why`s); SOURCES line "ATF treats a pawn redemption as a disposition that counts" and OPEN "ATF's published position is that pawn redemptions are dispositions that count" | **This is the wrong legal rule.** 27 CFR 478.126a(a) states expressly: "a report need not be made where pistols or revolvers, or any combination thereof, are returned to the same person from whom they were received." Returning a pawned handgun to the pledgor is exactly that. P&P §05.02 already has it right ("It is not required for a customer redeeming multiple pawned firearms — sales and transfers only"). The lesson contradicts both the regulation and the manual, and the 10/14 "conservative default" rests on a mistaken premise, so it should be reversed. Over-filing is not harmless: each 3310.4 sends a named customer's handgun data to ATF and the local police. **Fix:** S6 bullet 1 → "Same person, two or more handguns SOLD or TRANSFERRED by us within five business days. A customer getting their own pawned handgun back does not count." Narration: replace "and a redemption counts the same as a sale" with "a customer redeeming their own pawned handgun doesn't count — that's a return, not a sale". KEY_POINTS: "redemptions included" → "redemptions excluded". FLOOR_CHECK: unchanged wording is fine (it says "for a second handgun"). **Q5 must be rewritten:** the Tuesday redemption is neither a Virginia "purchase" nor a reportable disposition, so the Thursday pistol is ONE handgun — no 3310.4, and the CHP is irrelevant. Suggested replacement Q5: "A customer bought a pistol from you Monday. Thursday he's back for a second pistol and shows a valid Virginia concealed handgun permit. What else has to happen?" → correct: "Record the permit number for the Virginia gate, then flag it to your manager so the 3310.4 goes out today"; distractors: "Nothing extra — the permit covers everything" (why: permit clears the Virginia gate only; the federal report is still due) / "Refuse — two handguns in a week is never allowed" (why: with a verified exception the sale is lawful; the report is a filing, not a refusal). Also fix the OPEN line in SOURCES so Preston/Joshua are not asked to "reconcile" a correct P&P to a wrong lesson. | 27 CFR 478.126a(a); P&P §05.02 |
| 30 | MUST-FIX | L6-02 | S3 bullet 2 / `say`; Q3 marked answer and `why`s | "Old address on the ID? A second document that verifies the current address — recorded" / "the customer needs a second document that verifies where they live now" | Federal rule requires the supplemental document be **government-issued** (vehicle registration, vehicle title, tax bill, voter card, hunting licence, etc.). A lease, utility bill, bank statement or phone bill does NOT qualify. As written a new hire will accept a Dominion bill. Add "government-issued" to the bullet, the narration sentence and Q3's correct option/why ("a second government-issued document — vehicle registration, tax bill, voter card"). The P&P §05.00A says "other documentation" — flag for the P&P fix too. | 27 CFR 478.124(c)(3)(i); ATF 4473 instructions; ATF FFL Newsletter Nov 2012 |
| 31 | MUST-FIX | L6-02 | S7 bullets 2–4, `say`; Q4 marked `why` | "Federal law sets 21 for a dealer handgun sale … 'The age for a handgun is 21.'" cites federal law only (18 U.S.C. § 922(b)(1)). | The P&P script (§05.02) is "tell them **Virginia law** sets the age at 21", and that is the stronger ground: Va. Code § 18.2-308.7(C) (HB 1525, 2026) makes it a Class 1 misdemeanor for anyone under 21 to purchase a handgun (or assault firearm) in Virginia, is in force, and was not enjoined as of 10/6/2026 (challenged in *Boyer v. Katz*, Lynchburg Cir. Ct., filed 10/6/2026, no injunction reported). Federal § 922(b)(1) also still binds Virginia dealers (*McCoy v. ATF*, 4th Cir. 2025; cert. denied 6/30/2026) despite the 9/17/2026 DOJ OLC non-enforcement opinion. Change bullet 2 to "Federal AND Virginia law set 21 for a handgun sale"; Q4 `why` add "Va. Code § 18.2-308.7(C)". Narration line can stay if budget is tight (it is not wrong, just incomplete). | Va. Code § 18.2-308.7(C); 18 U.S.C. § 922(b)(1); McCoy v. ATF (4th Cir. 2025); DOJ OLC op. 9/17/2026; P&P §05.02 |
| 32 | MUST-FIX | L6-02 / L6-04 / L6-05 / L7-14 | all "under 21 and it might be an assault firearm → ask the Market Manager" slides; SOURCES OPEN F1/F2 ("Whether the under-21 assault-firearm rule in P&P §12.05 (HB 1525) sits inside the enjoined law … is NOT confirmed") | The open question has an answer: the enjoined 2026 sales/possession ban is **HB 217/SB 749**; the under-21 purchase rule is **HB 1525 → § 18.2-308.7(C)**, a separate statute that is in force. The "ask the Market Manager" procedure is a safe floor and can stay, but the lessons should not keep saying the under-21 rule is unconfirmed, and the "re-check before Jan 1, 2027" note is tied to the wrong case. Action for Joshua/counsel: confirm § 18.2-308.7(C) status, then (cheap) update the SOURCES/OPEN text in L6-01, L6-02, L6-04, L6-05, L7-14 and P&P §12.05, and add one bullet to L6-02 S4: "Under 21: no handgun, and no assault firearm — Virginia law." Pawn redemption by an under-21 pledgor (§12.05) is still "stop and call the Market Manager". | Va. Code § 18.2-308.7(C) (HB 1525, Ch. 1102, 2026); HB 217/SB 749 (enjoined per brief); P&P §12.05 |
| 33 | SHOULD-FIX | L6-02 | S8 bullet 1 / `say`; (and L7-14 S2 bullet 4, see #58) | "The person filling out the form must be the actual buyer. Buying for someone else is a straw purchase — a federal crime" | True, but the 4473 itself says a **bona fide gift** bought with the buyer's own money is lawful (the giver IS the actual transferee). Without that sentence staff will refuse a father buying a Christmas shotgun for his adult son, or treat every "it's for my wife" as a straw sale. Add one bullet: "A genuine gift, paid for with their own money, is fine — they're the buyer. Someone else picking it, paying, or getting reimbursed is not." No narration change needed. | ATF Form 4473 instructions (Question 21.a / 'actual transferee' and gift language); 18 U.S.C. § 922(a)(6) |
| 34 | NOTE | L6-02 | S2 | Sections A/B/C/D/E roles; "A check is good for 30 days … recertify in Section D" | Correct for the Aug 2023 4473 revision; 27 CFR 478.102(c) 30 calendar days; Section D recertification when transfer is on a later day than Section B signature. | 27 CFR 478.102(c), 478.124 |
| 35 | NOTE | L6-02 | S5, Q8 | Virginia one-handgun-per-30-days gate; CHP exception | Correct. Statutory exceptions (§ 18.2-308.2:2(R)) include CHP holders, same-time trade-in, stolen/lost replacement with police report, law enforcement, antiques, C&R private sales, and the VSP multiple-handgun certificate (valid 7 days). P&P §04.02 lists them correctly. | Va. Code § 18.2-308.2:2(R) |
| 36 | NOTE | L6-02 | S9, Q2 | "ATF allows a single lined-through correction … Our rule is stricter: photocopy-only" | Accurate description of both. | ATF 4473 instructions; P&P §05.02 |

### L6-03 The background check
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 37 | NOTE | L6-03 | S3, Q2 | "until the end of the store's fifth business day … December 25 doesn't count" | Correct. § 18.2-308.2:2(B)(2) and (B)(6). | Va. Code § 18.2-308.2:2(B) |
| 38 | NOTE | L6-03 | S4, Q3 | "they can contest the denial with the State Police within 30 days" | Close enough: § 18.2-308.2:2(D) gives access/review/correction under § 9.1-132 and a civil action that must be brought within 30 days of denial; VSP's FTC also runs an appeal process. Keep as is. | Va. Code § 18.2-308.2:2(D), § 9.1-132, § 9.1-135 |
| 39 | NOTE | L6-03 | S1, Q6 | "No permit exempts anyone. A Virginia concealed handgun permit does NOT skip the check" | Correct — Virginia CHP is not a Brady-alternative permit and VSP requires the check on every dealer transfer. | Va. Code § 18.2-308.2:2(B)(1); ATF Permanent Brady Permit Chart (VA: none) |
| 40 | NOTE | L6-03 | S2 | "Supply a gun lock with the firearm — every sale, every redemption" | Federal law requires a secure storage device only with handguns (18 U.S.C. § 922(z)); company rule extends to all. Fine. | 18 U.S.C. § 922(z); P&P §05.01/§05.02 |

### L6-04 Receiving an FFL transfer
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 41 | SHOULD-FIX | L6-04 | S5 `say` | "remember the order Preston set. Sales first, then payments…" | Spec: narration never attributes a rule to a person. Change to "remember the line order" (one narration line). Bullet is already un-attributed. | LESSON_SPEC §50 |
| 42 | NOTE | L6-04 | S2 | "A private person can lawfully ship a gun to a dealer, but it's recorded under their name and address" | Correct (27 CFR 478.125(e); 18 U.S.C. § 922(a)(2)(A)). Note handguns from a non-licensee must come by common carrier, not USPS — not needed in the slide. | 27 CFR 478.125(e) |
| 43 | NOTE | L6-04 | Q4 | $25 + $10 + $10 = $45 | Correct. | KB ffl-transfer-fee |
| 44 | NOTE | L6-04 | S1/S5 | Transfer out = "full 4473 and State Police check"; age rules apply | Correct; the Virginia one-handgun gate also applies to a handgun transfer (the online purchase is the "purchase") — consider one line in S5 so staff run the §04.02 gate on transfers too. | Va. Code § 18.2-308.2:2(R) |

### L6-05 Firearm pawns, redemptions and holds
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 45 | NOTE | L6-05 | S4, Q3, S6 | Third party never redeems a firearm; verified buyer "check is finished, come in" | Identical to L6-03 S6 and P&P §05.04 — no drift. | P&P §05.04 |
| 46 | SHOULD-FIX | L6-05 | Q5 stem | "'This is Dave Carter. I've got a Glock on pawn…'" | Fictional customer names are tolerable, but the spec prefers anonymised stories; "a caller gives a name" works. Low priority. Same for L7-03 Q4 "Jessica", L8-04 Q8 "Kayla", L8-01 Q2 "MARIA LOPEZ AND JUAN LOPEZ" (the title example genuinely needs names — keep that one). | LESSON_SPEC §50 |
| 47 | NOTE | L6-05 | S7, Q6 | Officer takes a firearm: receipt, photograph, A&D disposition within 7 days with agency/officer | Correct. | Va. Code § 54.1-4011; 27 CFR 478.125(e) |

### L6-06 "My gun won't fire"
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 48 | SHOULD-FIX | L6-06 | S1, S5, Q1, Q4 vs L7-00 S2 / L7-08 S2 / L7-02 S1 | "Firearms can't be returned" vs the first-timer pitch "A 30-day warranty on everything" | A trainee will hit this inside a week: the pitch says everything, §05.08 excludes firearms, ammunition and consumables. The P&P §07.04/§05.08 conflict is already OPEN; until Preston states the firearm remedy, add one clause to L7-02 S9 and L7-14 S4: "Firearms: no returns; a function problem goes to your manager and Preston (lesson 6.6)". Do not change the Joshua-voice L7-00 narration. | P&P §05.08, §07.04 |

---

## Level 7 — Sell and Serve

### L7-00 Welcome to Level 7
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 49 | MUST-FIX | L7-00 | S2 bullets/`say`, KEY_POINTS 2, Q2 marked option ("A 30-day warranty on everything, the clearance section, free layaway, and a mobile app") | Drift on the first-timer line. Brief/Joshua 10/13 and L7-08 S2 + L7-15 role-play mark 1: first-timer hears THREE things (warranty, free layaway, mobile app). L7-00 says the first-timer hears FOUR (adds clearance). Meanwhile "every customer hears four things" (Preston KB, incl. clearance) is taught in L7-01/02/08/12 and role-play mark 8 — so L7-08 and L7-15 each carry two different lists. | Decide once. Option A (matches Joshua's script, costs L7-00 Joshua-voice narration + Q2): first-timer = 3; "four things to every customer" stays as the send-off list. Option B (no narration cost): make the first-timer line the same four and change L7-08 S2 bullet 3 + FLOOR_CHECK + Q2 and L7-15 mark 1 to add clearance. Either way, L7-08 and L7-15 must stop presenting two lists without saying why. Recommend A with an explicit bridge sentence in L7-08 S5: "The first-timer line is three things; before anyone leaves they've also heard clearance — that's the four." | Brief "Known facts"; KB wclm-four-pitch-points; P&P §07.04 (three: warranty, app, layaway) |

### L7-01 How we sell
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 50 | NOTE | L7-01 | S6, Q3, Q7 | 30% associate limit, 10% normal give, 31–50% manager, never past 50%; no discounts on coins/bullion/clearance jewelry; tax on every deal | Matches P&P §05.03 and the shared Level-7 standard; identical in L7-11, L7-13, L7-14. No drift. | P&P §05.03 |
| 51 | NOTE | L7-01 | S1, Q5 | Line order sales → payments → loans/buys → transfers | Identical in L6-04, L7-08, L7-14. No drift. | KB customer-priority-order |

### L7-02 Free layaway and the 30-day warranty
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 52 | SHOULD-FIX | L7-02 | S8 bullet 1 / `say`; Q5 | "It needs an account with an email. No email, no warranty **or return**" | P&P §05.08 conditions a return on the receipt, original condition and accessories — not on an account/email. The KB rule (4db3aad0) ties the WARRANTY to the account. Teaching "no return without email" denies a lawful-under-policy change-of-mind return and invites a complaint. Change to "No email, no warranty" and keep returns on the §05.08 terms. Q5 is about the warranty and is fine. | P&P §05.08; KB warranty-requires-account-with-email |
| 53 | NOTE | L7-02 | S4, Q8; L8-02 S7/Q6 | Tiers: jewelry 10%/10 mo; <$500 20%/3 mo; ≥$500 10%/6 mo; $499.99 is under; watch/coin/bullion = price tiers | Exact match to P&P §05.05 in both lessons. | P&P §05.05 |
| 54 | NOTE | L7-02 | S8 | "Days 1–7 refund in original form; 8–30 store credit; >30 manager review; cash refund >$50 manager approval" | Matches §05.08. §05.08 also allows an exchange for equal-or-greater value within 14 days with manager approval — not taught; optional. | P&P §05.08 |

### L7-03 The phone standard
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 55 | NOTE | L7-03 | S5, Q4 | "Name plus one non-public identifier" | Proposed standard (POLICY_GAPS #1) adopted by the Academy; stricter than §08.02 (spouse/attorney may receive details). Consistent with L8-04. See #67. | P&P §03.09, §08.02 |
| 56 | NOTE | L7-03 | S2 | "Thank you for calling Valley Pawn in Harrisonburg, this is Sam" | Store and first name in a greeting template are appropriate; not a spec violation. | — |

### L7-04 Texting, loyalty and Google reviews
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 57 | NOTE | L7-04 | S2, S3, Q1–Q4 | Written opt-in before marketing texts; 8 AM–9 PM customer local time; STOP honoured, internal DNC company-wide and permanent; 18-month EBR | All correct and consistent with L8-05 and P&P §07.06. Prior express written consent for marketing texts: 47 CFR 64.1200(a)(2)/(f)(9); hours 64.1200(c)(1) and Va. Code § 59.1-513; internal DNC 64.1200(d) (federal minimum 5 years — company "permanent" is stricter, fine); EBR 64.1200(f)(5). | 47 CFR 64.1200; Va. Code § 59.1-510 et seq. |
| 58 | NOTE | L7-04 | S6 `say` | "We never offer anything for a review … Google bans it and so does federal law" | Slight overstatement in narration: federal rule (16 CFR 465.4) bans incentives conditioned on sentiment and fake/insider reviews; an unconditioned incentive is a Google-policy violation, not a federal one. Q5's `why` states it correctly. Leave narration (cost) — Q5 carries the nuance. | 16 CFR Part 465; Google Maps UGC policy |
| 59 | SHOULD-FIX | L7-04 | Q3 stem/options | "Harrisonburg gold-buying text … Culpeper runs its own text campaign" | Two stores named in a scenario; spec says anonymise ("one store … another store"). Cheap edit. | LESSON_SPEC §50 |

### L7-05 Listing on eBay
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 60 | MUST-FIX | L7-05 vs L8-02 | L7-05 S4 bullet 4, Q5 why ("at least one bid"); L8-02 S2 bullet 1, `say`, Q2 why, KEY_POINTS ("more than one bid") | Same comp rule, two thresholds. KB says "at least one bid". | Pick one (recommend the KB's "at least one bid" — a single-bid sale is still a tested price) and change L8-02 S2 bullet, Q2 why, KEY_POINTS; the L8-02 narration says "look for more than one bid" — one short line, or leave narration and fix text only if Joshua accepts the stricter wording for watches specifically. | KB comp-methodology-sold-with-bids |
| 61 | NOTE | L7-05 | S5, Q2–Q4, Q7 | Four binding rules; 90-day hands-off; by-weight metal never repriced; delist through Bravo | Exact match to P&P 5A. | P&P 5A |
| 62 | NOTE | L7-05 | S1 | "Fees take roughly a fifth of the sale price" | eBay FVF ~13–15% + promoted-listing ad fee → ~20% all-in. Fine. | KB ebay-costs-20-percent |

### L7-06 Shipping eBay orders
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 63 | SHOULD-FIX | L7-06 | S1 bullet 2 / `say`; Q2 marked option/why | "More than 3% late and the store loses Top Rated status: no fee discount, pushed down in search" | Two inaccuracies: (a) the 10% final-value-fee discount attaches only to **Top Rated Plus listings** (1-day handling + 30-day free returns) — the stores run 2–3-day handling, so there is no discount to lose today; (b) search demotion comes from falling to **Below Standard** (defect rate >2% or cases closed without resolution >0.3%), not from losing Top Rated. Late shipment >3% does cost Top Rated status. Reword: "More than 3% late and the store loses Top Rated. Keep piling up defects and cases and the store goes Below Standard, which buries every listing in search." Q2 option: drop "no fee discount". | eBay Seller Performance Standards (US): Top Rated late-shipment ≤3%; Below Standard defect >2% / cases >0.3%; Top Rated Plus 10% FVF discount |
| 64 | NOTE | L7-06 | Q1 | Friday order, 2-business-day handling | Ship-by is Tuesday; "next Wednesday" is late — correct. | eBay handling-time rules |
| 65 | NOTE | L7-06 | S2/Q7 | "Carrier coverage on metal is limited … insurance method your manager sets" | Correct and appropriately open (USPS Registered Mail or third-party insurance are the usual answers for $1k+ jewelry); no figure taught. | KB shipping-scrap-insurance |

### L7-07 Service recovery
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 66 | NOTE | L7-07 | Q2 | PlayStation at 40 days → "Past 30 days a manager reviews it" | Matches §05.08. | P&P §05.08 |
| 67 | NOTE | L7-07 | S2 | "Never 'the manager's not here' and never 'that wasn't me'" | Good practice; consistent with POLICY_GAPS #5. | — |

### L7-08 Your first thirty seconds
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 68 | MUST-FIX | L7-08 | S2 (three things to first-timers) vs S5 bullet 4 / KEY_POINTS 6 / Q8 ("Every customer hears … four things … clearance") | Two lists in one lesson with no bridge (see #49). | Per #49 — add the bridge sentence or unify. Q8 is fine once the bridge exists. | Brief; KB wclm-four-pitch-points |
| 69 | SHOULD-FIX | L7-08 | Q4 marked option | "'She's off today. I'm Josh. The manager and I work every deal together…'" | The associate in the example is "Josh" — the owner is Joshua. Trainees will read it as Joshua Davis. Use any other name ("I'm Sam"). | LESSON_SPEC §50 |
| 70 | NOTE | L7-08 | S3 | "the three loan-side questions: been here before, loan or sell, how much do you need" | Consistent with L7-09 Q6. | KB qualify-before-you-look-anything-up |

### L7-09 Ask before you pitch
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 71 | NOTE | L7-09 | S5 | "what we pay the most for: gold, jewelry, coins, firearms and ammo" | Subset of the KB list (adds big toys, new-gen consoles, high-end brands); L7-08 Q5 why notes consoles are worth taking. Fine. | KB what-we-pay-most-for |
| 72 | NOTE | L7-09 | S5 bullet 4 vs L7-07 S5 | "Never send them to a competitor … If they ask where else, we don't know" vs L7-07 "Give a real referral: who might buy it, where it might sell" (drumsticks → music store, Marketplace, eBay) | Apparent conflict. L7-07 is for items we never take (no sale lost); L7-09/L7-10 is for items we stock. L7-07 S5 should say so in one clause: "For something we don't deal in at all, a real referral…". Bullet edit only. | KB never-recommend-competitors; TRAINING_PROGRAM_PLAN library |

### L7-10 Show it like you own it
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 73 | NOTE | L7-10 | S4, Q7 | "inside 7 days money back the way they paid, then store credit through day 30" | Matches §05.08 / L7-02. Terminology mixes "warranty" and "return" but consistently across L7-02/10/15. | P&P §05.08 |
| 74 | NOTE | L7-10 | Q3 | Disclosed dent, day 4, change of mind → money back | Defensible under §05.08 (7-day original-form refund; item in original condition). Marked answer is the only right one. | P&P §05.08 |

### L7-11 Price talk
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 75 | NOTE | L7-11 | Q2, Q5, Q3 | $110/$180 = 38.9% ("39%") ✓; $150 = 16.7% ✓; 30% off $95/$85 = $66.50/$59.50 ("$66 and $60") ✓; $225 on $250 = 10% ✓ | Arithmetic correct. | — |
| 76 | NOTE | L7-11 | S5, Q6 | "A pawn redemption amount is never negotiated" | Correct and legally sound — charges are statutory caps computed by Bravo (P&P §05.0); a "goodwill discount" on a redemption would also be an unrecorded charge change. | P&P §05.0; KB pawn-redemption-not-negotiable |

### L7-12 Finish the sale
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 77 | NOTE | L7-12 | S4, Q2 | "No email, no warranty"; refuse → ring it and say so | Matches KB and the 10/14 default. Consistent with #52 once L7-02 drops "or return". | KB warranty-requires-account-with-email |
| 78 | NOTE | L7-12 | S2 | "Firearms: case, lock, ammo" add-ons | Fine; the gun lock is supplied free by rule (§05.02) — don't let staff read "lock" as an upsell. Add "(the lock comes with it)" to the bullet. | P&P §05.02 |

### L7-13 Selling jewelry from the case
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 79 | MUST-FIX | L7-13 | Q7 marked `why` ("scrapped at two years") and option 3 `why` ("jewelry over two years goes to scrap") | Contradicts L5-03 S6/Q8 and P&P §06.03 (30% at 1 year, 6 months clearance, scrap at ~18 months). L5-03's sources already mark the 2-year KB entry as superseded. | Change both `why`s to "…then scrapped after the six-month clearance period (§06.03)". Text-only. | P&P §06.03 |
| 80 | NOTE | L7-13 | Q3 | $650 ring, offer $250; counter $520 (20% off); "$300 is 54% off" (53.8%) | Correct. | — |
| 81 | NOTE | L7-13 | S4 | "we don't sell gold under melt, so any discount that would get there is the manager's call" | Consistent with 5A rule 2 note ("metal priced at melt is never marked down below melt anywhere"). | P&P 5A |

### L7-14 Selling a firearm
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 82 | MUST-FIX | L7-14 | S2 bullet 4 / `say` ("Who's it for? If it isn't for them, stop … That's not a sales question anymore"); KEY_POINTS 2 ("If it's not for them, stop and follow Level 6") | As a blanket rule this is wrong and will cost lawful sales: a bona fide gift purchased with the buyer's own money is lawful and the 4473 says so. Q2's scenario (brother "just working today") is a genuine red flag and the answer "stop, follow Level 6" is right for THAT case. | Bullet: "Who's it for? A gift they're paying for themselves is fine — they're the buyer. If the other person picked it, is paying, or will pay them back, stop: that's Level 6, not a sales question." Narration: optional. See #33 for the matching L6-02 bullet. | ATF Form 4473 instructions (actual transferee / gift); 18 U.S.C. § 922(a)(6) |
| 83 | SHOULD-FIX | L7-14 | S4 bullet 3 / `say` ("Account with an email, so the record and the warranty are on file") | Firearms are excluded from returns and the firearm warranty remedy is OPEN (L6-06). Saying "warranty" at the gun counter sets up the L6-06 refund argument. | "Account with an email, so the record is on file" — drop "warranty" on this slide until Preston states the firearm remedy. | P&P §05.08; L6-06 OPEN |
| 84 | NOTE | L7-14 | S3 | "Never confirm a firearm is on the premises by phone … In person you can show what's on the rack" | Consistent with L6-05/L1-05. | POLICY_GAPS #2 |

### L7-15 Ask for the sale / role-play
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 85 | MUST-FIX | L7-15 | S6 mark 1 ("a first-timer gets the what-makes-us-different line") vs mark 8 ("the four things (warranty, clearance, free layaway, the app)") | Two lists in the scorecard; a manager scoring mark 1 against mark 8 will dock a trainee for omitting clearance from the first-timer line or vice versa. | Resolve with #49; then state in mark 1 exactly which items are required. | Brief; KB wclm-four-pitch-points |
| 86 | NOTE | L7-15 | S4, Q4, Q8 | $7K/$9K/$12K in 30-day periods from start date; ranking is month-to-date retail without fees | Consistent, clearly distinguished. | KB new-hire-sales-goals-30-60-90 |

---

## Level 8 — Advanced

### L8-00 Welcome to Level 8
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 87 | NOTE | L8-00 | S3 | "New hires finish Level 8 in their first ninety days" | Matches Master Plan rolling gate. Recert due dates remain OPEN in L8-03/04/05 (only gun safety has Jan 31). | Master Plan v2 |

### L8-01 Title pawns
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 88 | MUST-FIX | L8-01 | S1 `say` ("The title and the lien are what secure the loan"), whole lesson | Nowhere does the lesson say the **vehicle is held by the store**. Virginia's pawnbroker chapter only permits a vehicle pawn where the vehicle is pledged and "in the pawnbroker's possession" (§ 54.1-4005 — the sale clock runs on possession; P&P §06.02 even has the store starting pawned vehicles every two days). A loan where the customer keeps driving is a **motor vehicle title loan** under Va. Code § 6.2-2200 et seq., which needs a separate SCC licence, bars rollovers/renewals and caps rates — a different product. A trainee reading "title pawn", "renewal payment", "spare key" and "lien" with no mention of possession could write exactly that. | Add one bullet/line to S1: "The vehicle stays with us for the life of the loan — that's what makes it a pawn and not a title loan." (and keep the existing OPEN for Joshua/counsel on structure). Text edit; narration optional. | Va. Code § 54.1-4005; § 6.2-2200 et seq.; P&P §06.02 (Vehicles) |
| 89 | NOTE | L8-01 | Q3, Q8 | $10,000 × 50% = $5,000; 40% = $4,000 ✓; 30% × $2,000 = $600 ✓ | Correct. | P&P §04.04/§04.06 |
| 90 | NOTE | L8-01 | S3, Q2 | "'and' = both owners present, 'or' = one" | Correct Virginia DMV practice and P&P §04.04. | P&P §04.04 |
| 91 | NOTE | L8-01 | S6, Q7 | "If our lien isn't properly recorded, we can't lawfully sell the vehicle on default" | Matches §04.04 / § 54.1-4005 → § 46.2-637, § 46.2-633. | Va. Code § 54.1-4005 |

### L8-02 Watches and high-end brands
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 92 | MUST-FIX | L8-02 | S2, Q2, KEY_POINTS ("more than one bid") | See #60 — drift from L7-05/KB "at least one bid". | Unify. | KB comp-methodology |
| 93 | SHOULD-FIX | L8-02 | S5 bullet 1 | "Reference number and serial number: engraved between the lugs or on the caseback" | Add "or on the inner bezel ring (rehaut) at 6 o'clock" — Rolex moved the serial to the rehaut after 2005–08; a trainee told "between the lugs" will find nothing on a modern Rolex and flag a real watch. Bullet edit. | Rolex serial placement (post-2008 rehaut engraving) |
| 94 | SHOULD-FIX | L8-02 | S5 bullet 3 / `say` | "Mechanical movement: the second hand sweeps smoothly. A tick-tick on a watch that should sweep is a red flag" | Correctly caveated ("on a mechanical watch"), but add: "many luxury brands also make quartz models (Cartier, Omega, TAG Heuer, Rolex Oysterquartz) — look up the reference first." Otherwise step 2 (reference lookup) is undercut by step 1. | Industry practice |
| 95 | NOTE | L8-02 | S7, Q6 | $450 watch → 20% down / 3 months | Correct per §05.05. | P&P §05.05 |
| 96 | NOTE | L8-02 | S8, Q5 | Altered serial = cannot take; Va. Code § 54.1-4009(D) | Correct. | Va. Code § 54.1-4009(D) |
| 97 | NOTE | L8-02 | S3/Q1 | Worksheet at $1,000+ "reloans included" | Matches §01.10 (P&P supersedes the Slack exemption). | P&P §01.10 |

### L8-03 Harassment, respect and EEO
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 98 | NOTE | L8-03 | S1 | Protected list incl. "marital status … lactation … veteran or military status" | Matches the Virginia Human Rights Act (§ 2.2-3900 et seq., as amended 2020–2021) and Handbook EEO. | Va. Code § 2.2-3900 et seq. |
| 99 | NOTE | L8-03 | S4–S7, Q1–Q8 | Report to Store Manager/Market Manager/Owner; involves Preston → Joshua; managers report immediately; no confidentiality promise; no retaliation; religious request in writing 30 days ahead | Matches Handbook "Reporting Harassment", "Religious Accommodation Policy", "Who to Contact" (HR = Joshua). All quiz answers singular. | Handbook v2026.6 |
| 100 | NOTE | L8-03 | S5, Q8 | Customer/vendor harassment — "Management decides whether that person is welcome back" | Correct statement of the employer duty for non-employee harassment. | 29 C.F.R. § 1604.11(e) |
| 101 | SHOULD-FIX | L8-03 | SOURCES | Cites "Employee Handbook v2026.5" throughout | Consolidated source file is v2026.6 (and v2026.7 exists on disk). Update the citation strings so the lesson's provenance matches the current Handbook; verify v2026.7 did not change the reporting chain. Same in L7-03, L7-07, L8-04, L8-05 sources. | sources/SOURCES_CURRENT.md header |

### L8-04 Protecting customer information
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 102 | NOTE | L8-04 | S6, KEY_POINTS 6 | "Virginia requires notice to affected customers AND the Attorney General without unreasonable delay … no minimum … over 1,000: credit bureaus … FTC 30 days at 500+" | All correct. § 18.2-186.6(B), (E) (no 2025/2026 amendment); 16 CFR 314.4(j) (FTC notice ≤30 days, ≥500 consumers, eff. 5/13/2024). | Va. Code § 18.2-186.6; 16 CFR 314.4(j) |
| 103 | SHOULD-FIX | L8-04 | S2 bullet 3 / `say` ("Account details go to the verified account holder only. Not an ex, a relative or a friend"); Q8 | P&P §08.02 still allows the debtor's **spouse** (and attorney) to receive account details; the stricter "account holder only" rule is a draft policy awaiting Joshua. "Not … a relative" as written contradicts §08.02 on spouses. | Either Joshua approves the draft and §08.02 is amended before launch, or the bullet says "Not an ex, a friend, or anyone but the account holder (and spouse, per the manual)". Flagged OPEN already — needs a decision, not another note. | P&P §08.02; Account_Details_Phone_Text_Policy_2026-10 (draft) |
| 104 | NOTE | L8-04 | S1 | "Federal law treats a pawnbroker as a financial institution for customer privacy" | Correct — the FTC treats pawnbrokers as "financial institutions" under GLBA (FTC Privacy Rule definition of financial institution, 16 CFR 313.3(k), includes businesses significantly engaged in lending), so the Privacy and Safeguards Rules apply. The GLBA program itself is OPEN (Qualified Individual, WISP) — outside the lesson. | 16 CFR Parts 313–314 |
| 105 | NOTE | L8-04 | Q6 | "shred all but firearm records" with Joshua's OK | Correct; pawn transaction records 5 years (company) vs. Va. § 54.1-4009(B) 1-year minimum. | P&P §03.08 |

### L8-05 Calling and texting customers
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 106 | NOTE | L8-05 | S1 | "every bad call or text can cost $500 to $1,500" | Correct: TCPA 47 U.S.C. § 227(b)(3)/(c)(5) $500, treble to $1,500 if willful; Va. Code § 59.1-515 same figures. | 47 U.S.C. § 227; Va. Code § 59.1-515 |
| 107 | NOTE | L8-05 | S3, Q2 | "18 months … lets us call a customer who's on the National Do Not Call list. It never covers marketing texts" | Correct: EBR exemption 47 CFR 64.1200(f)(5) and Va. § 59.1-514(D); autodialed marketing texts need prior express **written** consent regardless of EBR. The National DNC scrubbing procedure is OPEN — without a registry subscription, calling non-EBR numbers is itself unlawful; keep that OPEN visible to Preston. | 47 CFR 64.1200(c)(2), (f)(5), (a)(2) |
| 108 | NOTE | L8-05 | S4, Q8 | "first and last name and 'Valley Pawn' … never block caller ID" | Correct — Va. Code § 59.1-512 (identify promptly; no caller-ID blocking). | Va. Code § 59.1-512 |
| 109 | SHOULD-FIX | L8-05 | S5 bullet 2 / Q7 option 3 `why` ("Even a bare callback message is a voicemail, and no message is left on reminder calls") vs L6-03 S6 ("Voicemail: your first name, the store and a callback number. Nothing else") | Two voicemail rules in two lessons. They are for different calls (loan reminders §08.01 vs. a finished background check) but a trainee will not see the seam. | Add to L8-05 S5 bullet 2: "(that's reminder and past-due calls — a callback on a finished background check is lesson 6.3: first name, store, number)". Bullet edit. | P&P §08.01; L6-03 S6 |
| 110 | NOTE | L8-05 | S6 | "Virginia only needs one party's consent" to record | Correct. | Va. Code § 19.2-62 |
| 111 | NOTE | L8-05 | S5 | "Collection contact: Monday–Saturday, 8 AM–9 PM" | FDCPA itself has no day-of-week rule and technically governs third-party collectors, not a creditor on a non-recourse pawn; the Mon–Sat limit is company policy (§08.02). Teaching it as "our rule" is fine. | 15 U.S.C. § 1692c; P&P §08.02 |

### L8-06 Handbags
| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 112 | NOTE | L8-06 | S3, Q2 | Coach creed "first set is a date code, second is the model; F = factory outlet" | Correct for Coach creed patches (F-prefix = Factory). | Coach creed format |
| 113 | SHOULD-FIX | L8-06 | S6 bullet 3 | "Photograph the stamps, stitching, date code and hardware" | Louis Vuitton stopped date codes in March 2021 (replaced by an NFC microchip) — a 2021+ LV with no date code is not a red flag. Add "(LV made after 2021 has a chip, not a date code)". Bullet edit. | LV public statements, 2021 |
| 114 | NOTE | L8-06 | S7 | "Selling counterfeit goods is a crime, and it gets our online store shut down" | Correct in substance (18 U.S.C. § 2320 requires knowing trafficking; eBay VeRO). Sources cite Va. Code § 59.1-92.12 as "Virginia trademark counterfeiting"; that section is the civil infringement provision of the Trademark and Service Mark Act — have counsel confirm the Virginia criminal citation before it is quoted anywhere learner-facing. Source-line only. | 18 U.S.C. § 2320; Va. Code § 59.1-92.12 et seq. |
| 115 | NOTE | L8-06 | S5 | "every real Dooney has a serial number on a tag inside" | True for Dooney & Bourke bags since the 1990s (red/white "serial" fob or tag); vintage AWL bags carry a leather fob — fine for the counter. | Industry practice |

---

## Cross-cutting

| # | Severity | Lesson/File | Where | Finding (quote) | Correction | Source/citation |
|---|---|---|---|---|---|---|
| 116 | NOTE | L5–L8 | all | "#ask-handbook" / "ask handbook": **zero occurrences** in scope. | None. | grep |
| 117 | NOTE | L5–L8 | all | Known-fact drift check: loan timeline (not restated in scope — no drift), discount rule (L7-01/11/13/14 identical), third-party pickup (L6-05 Q3, L8-01 Q5 match §05.04), phone rule for firearm checks (L6-03 S6 = L6-05 S6 word for word), under-21 handgun (federal + Virginia, see #31). | Only the first-timer/four-things list drifts (#49/#68/#85) and the two comp-bid thresholds (#60/#92) and the jewelry scrap age (#79). | — |
| 118 | NOTE | L6 | all | No firearm images referenced in any L6 asset (VIDEO null, no image fields). Polygraph not mentioned anywhere in scope. | None. | Brief |

---

## Verdict

**Launch after fixes.** Levels 5–8 are substantively strong — the melt math, coin specs, Virginia layaway/return tiers, 4473 section roles, A&D deadlines, 48-hour loss report, 24-hour trace rule, VCheck five-business-day rule, TCPA/VTPPA hours and consent rules, and the Virginia breach-notice duties are all stated correctly and consistently with P&P v2026.8. But Level 6 carries one genuine legal error that must not go live: **L6-02 teaches that a pawn redemption counts toward the ATF multiple-handgun report (Form 3310.4), when 27 CFR 478.126a(a) expressly exempts handguns "returned to the same person from whom they were received" — and the P&P already says so.** Q5 of that lesson is built on the error and has no correct option as written. Three further MUST-FIX items touch federal/Virginia firearms practice (government-issued supplemental ID only; the under-21 rule now rests on Virginia § 18.2-308.7(C) as well as federal law and the "is HB 1525 enjoined?" OPEN has an answer; the blanket "if it isn't for them, stop" needs the bona-fide-gift carve-out). The remaining MUST-FIXes are internal drift a learner would notice (first-timer three vs. four things across L7-00/L7-08/L7-15; comp bids "at least one" vs. "more than one"; jewelry scrapped at 1.5 vs. 2 years; the title-pawn lesson never saying the vehicle stays with us). All of these are quiz/bullet/key-point edits except roughly four short narration lines (L5-01 S5, L6-02 S6, L6-04 S5, L7-00 or L7-08 depending on the greeting decision). Fix those, re-upload L6-02 first, and Level 6 is safe to gate on.
