# Level 1 — findings applied (2026-10-14)

Files edited in place: `scratchpad/edit/lessons/L1/*.json` (backup of the pre-edit files at `scratchpad/review/L1_backup/`). All 8 files validate as JSON, 2-space indent, ensure_ascii=False. Edit script: `scratchpad/review/apply_L1.py`.

Level-wide (every lesson):
- Added top-level `objectives` (one performance sentence, 23–30 words each).
- Stripped every section/document citation (§, Handbook, Master Plan, HR-2026-xx, KB, POLICY_GAPS, Call nn, queue #) from quiz `why` text; whys now name the rule in plain words. Citations stay in `sources`.
- Trimmed correct options that were the longest in their set (finding 20); no question now has a uniquely-longest correct answer.
- No `goldilocks: true` marks existed in L1; none removed.

## (a) Per lesson

**L1-00 Welcome to Level 1** (findings 9, 25)
- Narration moved to third-person trainer voice ("Welcome to Valley Pawn. Level one is your first three days…"); `production_notes` and `sources` updated (no longer "Joshua's Take 1 script").
- "Stuck?" line now "#ask-handbook first, then your Store Manager" in bullet, narration and key points.
- Quiz cut to 3 questions about the intro itself (deadline, 70% score, where to look first); Goldilocks, reporting-line and greeting questions deleted; `pass_percent` = 0.

**L1-01 Welcome to Valley Pawn** (findings 11, 6, 22, 27, 20)
- Slide 1 narration replaced with the five-stores/one-name version; founding-history bullet removed.
- New slide 2 "What a pawn loan is" (30 days, service charge, pick up or extend, or we keep the item and that's the end of it; no balance, nothing on credit). Key point added. Source lines added (§09.03 + L3-01) and an OPEN line.
- "Who you go to": added one sentence + bullet that lawsuit threats and unresolved complaints go to Preston right away (so Q6 is now taught).
- Q7 true/false replaced with the "on your phone behind the counter" scenario.
- Q3 and Q6 correct options shortened.

**L1-02 Handbook and P&P** (findings 16, 19, 23, 20)
- "Your protected rights" slide: added bullet + narration sentence that company information includes what's in the cases, the safe and photos of the store, and none of it goes on personal social media (Q6 now taught). "actually" removed from Q6 prompt.
- Q4 correct option now "Ask your Store Manager, or #ask-handbook if they're not there"; why explains never guess.
- Key point and slide bullet: "HR-2026-04" → "one acknowledgment in Gusto".

**L1-03 Gun Safety 101** (findings 17, 18, 22, 20)
- "On the clock" slide: withdrawn-instruction history replaced with "You never pay for any part of this yourself, and nothing is reimbursed from petty cash. The company buys the certificate." (bullet, narration, Q3 why).
- "The rule" slide: added "If your third day lands on a day the store is closed, it's due the day before." (bullet + narration) with an OPEN source line.
- Q8 true/false replaced with the "do it at home on my laptop" scenario. Q2 and Q5 correct options shortened.

**L1-04 Your tools** (findings 1, 3, 4, 21, 20)
- "A few more texting rules": the 18-month sentence replaced with the calls-vs-texts version (bullet + narration); key point 4 adjusted. TCPA citation added to sources.
- Q4 STOP: distractors are now "add them at close" and "stop from this store only; other stores can still text"; the lawful confirmation-reply distractor is gone.
- Q8 prompt reframed to a loan a week past due; "non recourse" replaced in the why with the plain-words version; "Preston's rule" → "Our rule is".
- Q6 correct option shortened.

**L1-05 Phone rules** (findings 3, 12, 13, 14, 15, 27, 20)
- Slide 1: "one week of our own calls" dating removed; now "Four rules carry this lesson: verify before you disclose, never confirm a firearm, quote or capture, and never explain the store." (bullet + narration).
- Slide 3: Glock example anonymised and undated ("We've listened to calls where an employee told a stranger…").
- Slide 5: big-loan line is now "We do loans that size all the time. Bring it in and we'll look at it together"; the "last month / manager had been fired" passage replaced with an anonymised, undated version; "non recourse" replaced with the plain-words sentence (bullets updated to match).
- Slide 6: police-caller rule added (take name and department, call back through the department's main number) in bullet, narration and key points; OPEN source line added.
- Q5 placeholder "[the rule]" fixed; Q6 correct option updated to the new line; Q4 and Q8 correct options shortened; prompt of Q5 no longer says "Preston set the rule" (now "the Market Manager"); call-number references removed from whys.

**L1-06 Cash and your drawer** (findings 7, 8, 26, 27, 22, 20)
- "Your drawer is yours": "skim it to the safe" → "give the excess to your manager to put in the safe"; Transfer Tender mechanic added (count together, Transfer Tender in Bravo, cash never moves between drawers without one). Bullets and key point 1 updated. OPEN source line on the designee.
- "Company money": "immediate termination territory" → "If you ever use company money for yourself, you're done here." Counterfeit check added (pen/UV on every $50 and $100; a failed bill goes to your manager) with an OPEN source line.
- "Big cash": "terminable offence" → "Help with it and you're done here."
- Q5 reworded to the manager-to-safe mechanic; Q2 and Q6 correct options shortened; Q8 true/false replaced with the slow-day two-counts scenario.

**L1-07 Goldilocks** (findings 2, 10, 28, 20)
- Cut: the "What Goldilocks took off our plate" slide, the VP Ops Engine rename sentence/bullet/key-point and its true/false question, and all clock times (7:15/7:45/8:25/7 PM) from bullets, narration and key points. `minutes` 7 → 6.
- One discount rule taught: ceiling 30% off, never past 50%; the Discount Review flags anything deeper than the age ladder and your manager asks why (slide 2 bullet + narration, slide 3 "this is the ladder you're graded on", new key point). §05.03 added to sources.
- "Find your store's line. That's your scoreboard" moved to slide 1. Text replies: "answer within ten minutes" made explicit. Jewelry mismatch: "tell your manager today, and your manager escalates to Preston the same day".
- Q4 rewritten so the correct answer is "flagged on the Discount Review and your manager asks why". Q5 and Q3 correct options shortened.
- New cumulative scenario (finding 28): missed-call post shows a customer's number; coworker wants to text from a personal phone → call back on the store line, number stays in company systems (retrieves L1-04 personal-phone/Chekkit and L1-05 customer-information rules). Quiz stays at 8.

## (b) OPEN items for management (each also appended to that lesson's `sources` as "OPEN (review 2026-10-14): …")

| Lesson | What to confirm | Recommended default (what the lesson currently says) |
|---|---|---|
| L1-01 | "What a pawn loan is" summary: 30-day term, service charge, redeem or extend, forfeiture ends it | Keep as written; it mirrors L3-01 and §09.03. Confirm the term and the counter wording for the service charge. |
| L1-03 | Day-3 deadline landing on a day the store is closed | "Due the day before." Alternative: managers schedule the paid time on day 1 or 2 so it never comes up. |
| L1-05 | Police-caller verification | "Take their name and department, call back through the department's main number." Add to §01.06 or §07.03. |
| L1-06 | Who takes drawer excess to the safe when the Store Manager is off the floor | "Give the excess to your manager to put in the safe." Name the designee per store. |
| L1-06 | Counterfeit check | "Pen or UV on every $50 and $100; a failed bill goes to your manager." Confirm the tool each store has and what happens to the bill. |

Pre-existing OPEN lines (store-email login map, Slack channel map, Chekkit templates, phone-standard adoption, §08.02 spouse alignment, dress-code send-home, mid-day balance routine, certificate purchase mechanics) were left in place untouched.

## (c) DEFERRED
- Finding 24 (L1-02 / L1-04 cognitive load): noted only, no slide splits made. Both lessons still carry 6 dense slides; candidates for a later split are L1-02 "Time: honest, at the store, on the clock" and L1-04 "Chekkit" + "A few more texting rules".
- L1-01 slide 2 "Be about the customer" and L1-05 slide 5 "What you never say" are long narrations; not split (rule: no splits purely for length).
- L1-07 weekly scoreboards and funds-verification slides were kept (finding 10 did not list them for cutting); they could go if the day-3 trim needs to go further.
- L1-01 production_notes still reference the placeholder `joshua_welcome.mp4`; untouched.

## (d) Narration budget
Counted as the length of every replaced or added string in `say`, `key_points` and `objectives` (so phrase-level replacements that reuse most of the old sentence are over-counted):

| Lesson | chars |
|---|---|
| L1-00 | 294 |
| L1-01 | 1,009 |
| L1-02 | 365 |
| L1-03 | 369 |
| L1-04 | 436 |
| L1-05 | 1,472 |
| L1-06 | 794 |
| L1-07 | 1,246 |
| **Total** | **5,985** (ceiling 6,500) |

Net-new narration (true additions, excluding re-recorded replacements) is roughly 2,900 characters: the pawn-loan slide (~390), objectives (~1,150), police-caller rule, Transfer Tender mechanic, counterfeit check, social-media sentence, closed-day sentence, and the new L1-07 key point. Deletions in L1-07 (one full slide and the rename sentence) are free.
