# Valley Pawn Training Program — Master Plan (v2, 2026-09-28)

**Domain:** 1 — Full Circle Finance Inc DBA Valley Pawn · **Owner:** Joshua · **Operator:** Preston + store managers · **Built/measured by:** automation
**Supersedes:** v1 of this file (same day). Joshua: *"super uninteractive and academic… we want robust engaging content so when a new hire comes on they can be put in front of a screen, take the modules, take the tests so we know they master the material, then have scorecards and accountability."*

---

## The one-sentence version

A new hire sits down at the store computer on day one, logs into **Valley Pawn Academy**, and works through short video-and-scenario lessons in order; every lesson ends in a test they must pass at 80% or better before the next one unlocks; managers verify the hands-on pieces on the floor; every Monday a scorecard shows who is where, and nobody works the counter alone, touches a firearm transaction, or gets keys until the record says they've mastered it.

---

## What the new hire actually experiences

**Day 1, first hour.** Manager logs them into the Academy on the store PC (or their phone — mobile app). The dashboard shows one thing: *Level 1 — Welcome to Valley Pawn*. A 4-minute video from Joshua on who we are and what "be about the customer" means. Then the handbook and P&P acknowledgment (they sign in Gusto — link inside the lesson). Then the Basic Gun Safety 101 class (free, ~40 min) with the certificate number typed into the Academy so we can verify it. Level 1 is done by end of day 3 or employment ends (HR-2026-05).

**Days 2–30.** Levels 2–7 unlock one at a time. Each lesson is 5–10 minutes, built the same way so it's never a wall of text: a narrated video (screen recording of Bravo doing the real thing, or a slide-narrated micro-lesson), a **real recorded call** from our own library ("listen to Logan quote the Xbox without seeing it"), then a **scenario test** — "a caller gives a surname and asks what's in pawn under it; what do you say?" — with wrong answers explained, not just marked wrong. Pass at 80% to unlock the next lesson; fail twice and the manager gets a nudge to sit with them.

**Hands-on checks.** Some things can't be tested on a screen — testing gold, running a 4473, counting the drawer. Those lessons end with a *Floor Check*: the manager watches them do it and taps ✅ in the Academy (or replies ✅ to the Slack nudge). Screen test + floor check = mastered.

**Practice before the phone goes live.** An AI role-play sim: the trainee "answers" a simulated customer call (text or voice), handles it, and gets scored against the phone standard (verify before you disclose, quote or capture, never confirm a firearm on premises). Five passed sims before they take a live call.

**Days 31–90 and after.** Level 8 (advanced: diamonds, title pawns, delayed transfers, service recovery) and a monthly 10-minute module built from that month's best and worst real calls. Annual recerts (gun safety by Jan 31, harassment/EEO, data security) are just Academy courses with due dates. Managers have their own track.

**What they see the whole time:** a progress bar, their score, badges per level, a leaderboard by store (completion and score, positive only), and a certificate at Level 7 — *Certified Valley Pawn Sales & Loan Associate* — which is also the trigger for keys eligibility and the 90-day review.

---

## The curriculum (Preston's 16 checklist items, reorganized into levels)

| Level | Name | Lessons (each = video + call clip + scenario test; ⚙ = also has a Floor Check) | Gate |
|---|---|---|---|
| 1 | **Welcome & Rules of the Road** (day 1–3) | Who we are · Handbook/P&P acknowledgment (Gusto) · Basic Gun Safety 101 certificate · Systems: Bravo, Slack, #ask-handbook, Chekkit · What you never say on the phone · Cash & drawer basics ⚙ | Must complete by day 3 |
| 2 | **Open, Close, Count** | Opening procedure ⚙ · Closing procedure ⚙ · Drawer balancing 2×/day ⚙ · Safe & funds verification · Jewelry daily count ⚙ | Before any opening/closing shift |
| 3 | **The Loan** | How a pawn loan works (interest vs principal, grace vs expiration, the four permitted charges) · Qualifying the customer · Writing the ticket in Bravo — the 10 required fields ⚙ · Pawn contract closing ⚙ · Payments, renewals, redemptions ⚙ · The past-due call | Before writing loans unsupervised |
| 4 | **Buying & Pricing** | Buying vs loaning · What we pay the most for (Preston's steer list) · Pull list / pricing ⚙ · Statement of ownership & stolen-property inquiries · Police report deadline · Employee purchase rules | Before buying unsupervised |
| 5 | **Gold, Jewelry, Stones** | Testing gold & silver ⚙ · Melt math and the spot sheet · Scrap bucket naming · Jewelry category standard · Diamond grading basics ⚙ · Counterfeit tells | Before quoting precious metal |
| 6 | **Firearms** | FFL basics & the A&D book · 4473 walkthrough ⚙ · NICS, delays, denials ⚙ · Receiving an FFL transfer ⚙ · Layaway firearms · Under-21 handgun rule · Never on the phone | **Hard gate**: no firearm transaction until Level 6 + Floor Checks + certificate verified |
| 7 | **Sell & Serve** | Sales framework (merchandising, pitch, objections) · Free layaway & warranty · The phone standard (quote-or-capture) + 5 passed role-play sims · Chekkit & customer loyalty · Google reviews · eBay listing ⚙ · eBay shipping ⚙ · Service recovery | → **Certified Sales & Loan Associate** |
| 8 | **Advanced / ongoing** | Title pawns (CEO approval) · Delayed transfers · Watches & high-end brands · Monthly module from real calls · Annual recerts | Rolling |
| M | **Manager track** | Weekly loan/layaway review · Aged inventory · Discount & sold-margin reviews · Coaching-pack huddles · Hiring pipeline · Bravo user admin · Floor-Check standards | Managers + MITs |

Every lesson cites its P&P section so the Academy and #ask-handbook never disagree. Content sources are all ours: P&P v2026.8, Handbook v2026.5, Preston's knowledge base (219+ verified rules), the teachable-call library (22 clips and growing), Preston's Sales Training Framework, the PawnTrain course lists as an outline check.

---

## Platform decision (expert-board recommendation, not a menu)

**Recommendation: TalentLMS** as the Academy, with Claude producing every piece of content and automation reading its reporting API.

Why this and not the alternatives:
- It is a real LMS off the shelf — learning paths with unlock rules, quizzes with a pass mark and retake limits, certificates, gamification (points, badges, leaderboards), a mobile app, per-user/per-branch reports, a REST API, and an AI course builder we can seed. Pricing is per active user and in the **roughly $70–120/month** band for a team our size (plans and tiers moved in 2026 — confirm at checkout; a free tier exists for a 5-user pilot). [Sources below.]
- **Trainual** is closer to an SOP wiki with quizzes — good for "how we do things," weaker on mastery gating, video-first lessons and reporting; it costs more.
- **A WordPress LMS plugin** on thevalleypawn.com (LearnDash/Tutor) would be fully owned and cheaper, but puts training on the marketing site, adds plugin upkeep and login management to the website audit's plate, and is another thing that can break. Not worth it at 18 people.
- **Building our own** app is the one path that never "just works" for a non-developer owner. No.
- **PawnTrain/PCG "All Aboard"** — no evidence of an active subscription or completions; it's generic pawn-industry content, not ours. Keep the Phase 1–3 course lists as a checklist against our curriculum; don't pay for it.

Store "branches" in TalentLMS = our 5 stores, so leaderboards and reports come out per store for free.

---

## Content production — how it stays engaging without a video crew

| Format | How it's made | Used for |
|---|---|---|
| **Screen-recorded Bravo walkthroughs** (3–6 min) | Preston records once per procedure on the training store; Claude scripts the shot list and writes the on-screen captions and the test | Every ⚙ lesson |
| **Narrated micro-lessons** (2–4 min) | Claude writes script + slides (brand studio look), generates narration, renders video | Concepts: how a loan works, the four charges, melt math |
| **Real call clips** (30–90 s) | Already pulled from the Zoom library; new ones nominated weekly | Phone standard, sales, service recovery, collections |
| **Scenario tests** (5–8 questions) | Written from the P&P and the actual mistakes in the call review; every wrong answer has a one-line "why" | Every lesson, 80% pass |
| **AI role-play sim** | A "customer" the trainee handles; scored against the phone standard | Level 7 phone gate |
| **Joshua on camera** (once) | 4-min welcome; 2-min "why the phone matters" | Level 1 |
| **Floor Checks** | Manager taps ✅ | Anything physical |

Preston's total time: record ~20 walkthroughs (one afternoon), approve each lesson once (10 min each). Joshua: two short videos.

---

## Scorecards & accountability

**Weekly Academy scorecard (Mon 09:30, from the reporting API)** — per store and per person: level reached, days since hire, on-track / behind / overdue, average test score, first-attempt pass rate, Floor Checks pending on the manager, recerts coming due. To Joshua's DM during the pilot; then to a #training channel (positive-only leaderboard) with the per-person detail going to each manager privately.

**Gates that make it real (recommended; written into the lessons unless overruled):**
- Level 1 by day 3 or employment ends (HR-2026-05, already drafted).
- No solo shift until Level 2; no unsupervised loans until Level 3; no buys until 4; no precious-metal quotes until 5; **no firearm transaction until Level 6**; no live phone until the sims are passed.
- Keys at 90 days *and* Certified.
- The 90-day review reminder goes to Preston with the Academy record attached; a manager whose new hire is >7 days behind gets it on their weekly goals.
- Manager accountability: Floor Checks left pending >3 days show on the scorecard by manager name.
- Training stays out of bonus qualifiers (except Level 1, which is already a condition of employment).

**Did it work?** The call-review scoreboard (quote rate, capture rate, verification rate, MEDIUM+ conduct) is the outcome measure. Academy completion is the input; the phones are the output.

---

## Build order

**Week 1 (Sep 28 – Oct 4) — stand it up.**
1. TalentLMS account (money — Joshua's card; the pilot can run on the free tier for 5 users), branded, 5 store branches, 18 users imported from `hr/ROSTER.json`, store-PC and mobile-app logins.
2. Curriculum locked in `CURRICULUM.md` (this file's table, expanded to lesson-level with P&P/KB citations).
3. Level 1 built complete: welcome video script for Joshua, acknowledgment + gun-safety lessons, phone-rules lesson + test, drawer basics.
4. Preston's shot list for the ~20 Bravo walkthroughs; he records at his pace.

**Weeks 2–3 (Oct 5 – Oct 18) — Levels 2–4 live; pilot.**
5. Lessons and tests for Open/Close/Count, The Loan, Buying & Pricing (narrated micro-lessons now, Preston's recordings swapped in as they arrive).
6. Pilot on the newest hires (Jacob Cox, Camden Ahern) + one manager; fix what confuses them.
7. `academy-sync` native agent: new Gusto hire → Academy user + Level 1 assigned + due dates; roster changes mirrored. `academy-scorecard` (Mon) to Joshua's DM. Nudges: day-3 gate escalation to Preston + Joshua only.

**Weeks 4–6 (Oct 19 – Nov 8) — Levels 5–7, the sims, the gates.**
8. Gold/Jewelry, Firearms, Sell & Serve; role-play sim; certificate; Floor Check flow (Slack ✅ → API).
9. Whole team assigned; current staff get Level 1 by 10/24 (cure date) and Levels 2–7 as a 60-day catch-up, tested — this is where we find who actually knows what.
10. Call-review pipeline relaunched (its three blockers fixed) so the monthly module and the outcome scoreboard run.

**Months 2–3 (Nov – Dec) — steady state.**
11. Level 8 + manager track; annual recert courses with due dates; 90-day review hook; leaderboard to #training.
12. Culpeper/Roanoke join the call program when Zoom Phone ports land.

## Decisions that are Joshua's (everything else proceeds)
1. **Platform spend** — TalentLMS at roughly $70–120/month (final tier confirmed at checkout; free 5-user tier for the pilot). Alternative is the WordPress plugin route at ~$200/yr if he'd rather own it and accept the upkeep.
2. **Go** to send HR-2026-05 (Level 1 gate; cure date 10/24 for current staff) and to ask Preston for the certificate list and the recordings.
3. **Confirm the gates** above (solo shift, loans, buys, metals, firearms, phone, keys).

## Blast radius / what this touches
Reads: `hr/ROSTER.json`, Gusto hires/documents, `KB_CURRENT.md`, P&P/Handbook, `Call Analysis/` library and packs, `COMPLIANCE_CALENDAR.md`.
Writes (new only): `Training Program/`, `hr/TRAINING.json` (mirror of Academy state), Drive `03 Human Resources/Training/` (scripts, videos, tests as source), new `com.valleypawn.academy-*` agents, TalentLMS content.
Never modifies: `weekly-training-pipeline` internals (fixed forward alongside), `Ask_Handbook`, the bonus engine, the website, any hardened fleet file.

## Sources (platform research, 2026-09-28)
- [TalentLMS — The 7 Best LMS for Small Businesses in 2026](https://www.talentlms.com/blog/lms-small-business/)
- [GoSkills — 10 Best LMS Options for Small Business in 2026](https://www.goskills.com/resources/best-lms-small-business)
- [Trainual vs TalentLMS comparison](https://trainual.com/compare/talentlms) · [G2 TalentLMS vs Trainual](https://www.g2.com/compare/talentlms-vs-trainual)
- [TalentLMS Pricing 2026 — educate-me](https://www.educate-me.co/blog/talentlms-pricing) · [TalentLMS Pricing — Capterra](https://www.capterra.com/p/132935/TalentLMS/pricing/) · [TalentLMS Pricing Review — Teachfloor](https://www.teachfloor.com/blog/talentlms-pricing)
