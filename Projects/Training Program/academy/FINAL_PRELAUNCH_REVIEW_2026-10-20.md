# Valley Pawn Academy — Final Pre-Launch Review (expert board), October 20–21, 2026

Prepared for Joshua Davis (CEO). Scope: all 71 lessons (Levels 1–8 + Manager Track), every slide, narration line, key point, quiz question and answer explanation; the build and voice pipeline; and the TalentLMS program structure.

## 1. The board and how it worked

Three seats, five independent reviews, then one decision pass:

| Seat | What it checked | Report |
|---|---|---|
| Pawn operator & regulatory compliance (2 reviewers: L1–L4 + Manager Track, L5–L8) | Every rule against P&P v2026.8 / Handbook v2026.6; every legal claim against the current Code of Virginia and federal rules (ATF, TCPA, FTC, IRS); every worked number recomputed | `review_2026-10-20/A1_*.md`, `A2_*.md` |
| Instructional design / L&D (2 reviewers, same split) | Objective ↔ content ↔ test alignment, question quality, narration load, sequencing, gates, program-level gaps | `review_2026-10-20/B1_*.md`, `B2_*.md` |
| Learning-platform / release engineering | Lesson validator on all 71, builder and player code read end-to-end, SCORM behaviour, voice pipeline, TalentLMS limits, runbooks | `review_2026-10-20/C_pipeline_platform.md` |

Raw findings: about 640 rows (≈150 of them explicit "verified correct" confirmations). After de-duplication: 7 blockers, ~45 must-fix, ~120 should-fix.

**Verdict of all five reviewers: substantively strong; launch after fixes.** The Virginia pawn law (charge caps, 45-day floor, record fields, noon police report, law-enforcement access), the loan timeline, Form 8300, TILA, the 4473/VSP redemption rule, melt math, coin specs, layaway tiers and the TCPA/Virginia telephone rules were all verified correct. What needed fixing was accuracy drift, a handful of legal errors, and the platform.

## 2. Blockers — all fixed

| # | Problem | Fix applied |
|---|---|---|
| 1 | **L6-02 taught that a pawn redemption counts toward the ATF multiple-handgun report (Form 3310.4).** 27 CFR 478.126a(a) exempts handguns "returned to the same person from whom they were received", and P&P §05.02 already says so. Q5 had no correct answer. | Slide, narration, key point and floor check now say sales and transfers only; Q5 rewritten (two sales in a week + CHP). Reverses the 10/14 default D40. |
| 2 | **M-01 told managers to "expire it now" on a first-payment default 5 days past due** with no mention of the 15-day statutory grace (§ 54.1-4005) — the associate lessons teach the opposite. | M-01 now: mark expired at day 1 past due, but nothing is pulled, priced or sold before the 15-day grace. |
| 3 | **Store hours stale** in L1-01, L2-02, L3-03 (all stores 10–6 Mon–Sat). | Six-day stores (Culpeper, Roanoke, Waynesboro) close 5 PM Saturday everywhere it's taught. |
| 4 | **#ask-handbook taught in 23 places** (L1-00, L1-02, L1-04, M-05) for a channel being retired. | Renamed to #ask-goldilocks with Goldilocks as the bot; L1-04 title updated. |
| 5 | **L1-07 said "Goldilocks doesn't answer questions"** — false once #ask-goldilocks is live. | Now: answers rule questions in #ask-goldilocks; in report channels it only posts. |
| 6 | **Internal citations leaked to learners** (L7-08: "CEO greeting script 2026-10-13"; L7-12: "9/28 huddle") — the 10/14 leak fix had gaps. | Text fixed and the builder's filter + validator now catch dated/huddle references. |
| 7 | **The program narrated mechanics the platform can't run** (AI phone "sims" that don't exist, Slack ✅ floor checks). | Phone gate is now: pass lesson 7.3 + five practice calls scored by the manager (a real Floor Check). Floor checks are marked in the New Hire Training Tracker. |

## 3. Must-fix — fixed (highlights)

Legal and policy accuracy: supplemental address documents on a 4473 must be **government-issued** (27 CFR 478.124); under-21 now rests on **federal and Virginia law** (Va. Code § 18.2-308.7(C), HB 1525, in force — the enjoined law is HB 217/SB 749); the **bona fide gift** carve-out added to the straw-purchase rules (L6-02, L7-14); title pawns state the **vehicle stays with us** (what makes it a pawn, not an SCC-licensed title loan); "acid confirms a bar" removed from the coins/bars slide; tungsten tells corrected; counterfeit bills never go back to the passer; police-report failures go to Preston and the manager the same day (one rule everywhere); "service charge" corrected to "finance charge".

One rule, stated one way everywhere: first-timer greeting is "Have you ever been here before?" + three things (warranty, free layaway, app), with clearance before they leave = "the four things"; account details go to the verified account holder only; 31–50% discounts need a manager; comps need at least one bid; aged jewelry scraps after six months in clearance (not two years); Close Till → Close Store; one employee-purchase Bravo note; Google review asked mid-transaction; competitors are never recommended to a buyer.

Assessment quality: every question now tests something taught; the three true/false items became scenarios; duplicated questions replaced; "last year's recert" stems fixed for new hires; correct answer is never the longest option (0 of 508).

Structure: L7-07's stale "final lesson of Level 7" gate rewritten; L1-01 can no longer be silently replaced by a missing welcome video; Sales Training — Week One defined (see §6).

## 4. Pipeline — fixed

The builder now refuses to ship a package with missing narration (the 10/14 silent-intro failure can't recur), runs the lesson validator before every full build, catches dated and huddle references, shows a **transcript** under every slide (sound off, no speakers, or hard of hearing), falls back to speech if audio fails to load, shows a proper "Preview done" screen on ungraded intros, drops the false leaderboard line, and renders floor checks as numbered steps. `voice.py verify` lists any uncached narration without billing; `estimate` shows the ElevenLabs balance. Validator result: **71 lessons, 0 violations** (one known exception: the L7-15 scorecard slide, split in phase 2).

## 5. Voice budget — two phases

Every changed narration line re-records in full. The complete fix set needed 35,351 characters; the account had 26,837 until the October 28 reset.

- **Phase 1 (done 10/21):** every narration change that fixes something wrong or contradictory — 24,928 characters, all 536 lines cached, all 71 packages built and validated ALL GREEN with full voiceover.
- **Phase 2 (after the 10/28 reset, automatic):** narration polish whose old wording isn't wrong (L1-05 phrasing, L1-03 closed-day wording, L7-06 eBay detail, L8-00 January recert window, several key-point lines, the L7-15 scorecard split). The full target text is saved in `lessons_target_20261028/`. Quiz, bullet and explanation fixes for those lessons are already live in phase 1.

## 6. Decisions the board made (defaults applied; tell us only if you disagree)

1. **Redemptions don't count toward 3310.4** — per regulation and your own P&P.
2. **Account details: verified account holder only** (your 9/28 draft policy) taught everywhere. P&P §08.02 still allows spouse/attorney — needs the manual updated to match.
3. **Phone gate:** lesson 7.3 + five manager-scored practice calls before inbound calls; outbound reminder calls allowed after lesson 3.6 with the manager in earshot.
4. **Sales Training — Week One:** lessons 7.2, 7.3, 7.8–7.13 and 7.15 assigned on day 1, due day 7 with the role-play (meets HR-2026-10). 7.14 (firearm selling) stays after Level 6.
5. **Annual recerts** (8.3–8.5) due every January 31 (same window as gun safety) — narration in phase 2.

## 7. What only you can do

1. **Sign in to TalentLMS once** in Chrome (the session expired) so the 71 rebuilt units can be uploaded — that is the only thing between the fixed course and your walkthrough.
2. **Before staff launch (not before your walkthrough): buy the Grow plan.** The Free plan caps at 10 users and 10 courses, has no API and no Learning Paths, so levels don't lock in order and the Monday scorecard, nudges and Gusto sync can't run. Until then, the fallback is manual: enroll each hire only in their current level.
3. Approve the P&P/Handbook alignment (routed through the policy flow, nothing sent): §01.01 hours, §06.01 "day 1 past due", §05.00A government-issued address document, §08.02 account holder only, §12.05 under-21 citation, Handbook hours and the "Human Resources" line.

## 8. Your walkthrough — suggested order (≈3 hours over two sittings)

Sitting 1: Level 1 (all 8), then L3-01, L3-06, L4-03, L4-04. Sitting 2: L6-02, L6-05, L7-08, L7-15, M-01, M-05. These carry nearly every fix above. Use "Show transcript" to read along. Anything that doesn't sound like Valley Pawn — note the lesson number and slide; that list becomes the phase-2 edit set before the 10/28 re-voice.

## 9. Files

`academy/review_2026-10-20/` (five board reports + validator), `academy/lessons/` (phase 1, live build), `academy/lessons_target_20261028/` (full target text), `academy/backups/20261020-board-pre/` (pre-review lessons, builder, voice.py and the 10/15 dist zips), `academy/validate_lessons.py`.
