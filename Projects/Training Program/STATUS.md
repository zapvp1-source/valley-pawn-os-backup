# Training Program — STATUS

**Read `TRAINING_PROGRAM_MASTER_PLAN.md` first.** Resume from the build order there; never restart.

## 2026-09-28 (late night) — plan + onboarding flow
- Joshua chose the **Grow** plan (he purchases). He wants to test Level 1 as an employee: test learner to be created by Joshua (Claude is blocked from creating accounts) using jdavis+academy@fcfpawn.com, enrolled in course 126 as learner.
- Onboarding flow proposed in `ONBOARDING_FLOW.md`: Gusto hire → academy-sync (TalentLMS API) creates learner + New Hire learning path + store group → Slack welcome DM + manager DM → daily nudges, day-3 escalation, Monday scorecard. Cadence: L1 by day 3, one level/week, Certified by day 45, L8 by day 90.

## 2026-09-28 (night) — voiceover live
- ElevenLabs (Creator plan, key in academy/.elevenlabs.json, TTS-only scope) — model eleven_turbo_v2_5; 5-voice rotation per lesson (Eric, Sarah, Brian, Jessica, Chris; voice = rotation[(level+order) % 5], so adding lessons never re-bills others). All 390 lines / 183,313 chars generated and cached in academy/media/voice/.
- Huddle edits applied first (9/28 items + hard flags: under-21 assault-firearm rule no longer taught as law; October date untested); new L6-06 "My gun won't fire". 52 lessons, 52/52 green.
- All 52 uploaded (6.6 = unit 2116, course 131). Verified live on 1.1: voiceover plays in TalentLMS.
- Courses 127–134 still INACTIVE (their "Publish" = activation); content is loaded and goes live when activated at launch.

## 2026-09-28 (late PM) — huddle input
- **2026-09-28 (evening) — 9/28 huddle edits APPLIED to the lesson JSONs** (the earlier attempt had changed no lesson file). 17 lessons edited + NEW L6-06 'My gun won't fire' (52 lessons). Hard flags: L6-01/02/04 no longer teach the under-21 assault-firearm rule as law; every 'October 1' is now 'in October' and untested. L8-02 (Rolex) and M-02 (F5) got source notes only. Answer bias 19.3% → 17.5%. build --all + --validate-only: ALL GREEN (52/52). Voice estimate 183,313 chars (was 178,318). Pre-edit copy: academy/lessons_backup_2026-09-28_pre-huddle/. New OPEN items H1–H10 in academy/OPEN_ITEMS.md. NOT done: TalentLMS re-upload (changed zips + new L6-06 unit in course 131), voice generate.
- **SYNC FOR THE ACADEMY BUILD SESSION: read `academy/HUDDLE_INPUTS.md` before the next lesson pass.** All 11 Slack huddles with AI notes (Feb–Sep 2026) harvested: 43 lesson additions mapped to lesson ids, 6 hard flags (assault-firearm ban is enjoined statewide — don't teach the 6/15 July-1 ban; polygraph = do not teach; hold periods, under-21 rule, eBay jewelry markdowns, Oct-1 date need confirmation). Lesson JSONs were NOT edited by the huddle session to avoid colliding with the build session.
- 9/28 Joshua–Preston huddle mapped to 13 Academy items (doc: https://claude.ai/code/artifact/e85d2848-52d6-438b-a893-ff54de1fcd22). Lesson edits pending: L1-05 (no cash-process talk; account holder only), L8-04, L7-03 (hold/callback), L3-06 (no past-due voicemail; Oct deadline framing), NEW L6-06 'my gun won't fire', L7-02, L7-01 (charger add-on), L8-02 (Rolex, waits on Preston/P51), L4-04, M-03, M-02 (blocked on eBay precious-metal ruling), M-05. Joshua plans 2 paid hours of at-home Academy time.

## 2026-09-28 (evening) — Academy built and loaded (NOT launched)
- TalentLMS portal valleypawn.talentlms.com branded "Valley Pawn Academy" (logo, favicon, purple/blue theme, US date/time, Eastern TZ, lockout 5/15 min, 9 categories). Free plan in 14-day trial.
- 51 lessons written (lessons/L1–L8, M), quizzes de-biased (correct answer longest 87% → 19%), 114 open questions consolidated in academy/OPEN_ITEMS.md (90 Preston, 24 Joshua).
- build_scorm.py turns each lesson into a SCORM 1.2 package: slides with icons, narration, real call clip (exemplars only — 4 conduct/customer-name clips pulled), key points, scenario test (80% pass, retake, manager nudge after 2), result screen. 51/51 validated.
- LEARNED LIVE: TalentLMS's SCORM frame won't load <audio> media and doesn't scroll → audio is embedded base64 + Web Audio; lesson scrolls its own #stage. Verified in TalentLMS: plays, audio works, 8/8 recorded, unit completes, next unit unlocks.
- 9 courses (IDs 126–134), all 51 units uploaded in order, all on the final build. Level 1 (126) is ACTIVE for testing (Joshua is enrolled as instructor); 127–134 inactive. No other users. NO invites (Joshua's rule until the program is complete).
- Voiceover pipeline (voice.py, ElevenLabs, cached per line) built and tested; ~178k billable characters for everything. BLOCKED on Joshua's ElevenLabs key.
- Known platform limits on the free plan: notifications can't be disabled (adding users would email them), no API (scorecard automation needs Core $119/mo+), no Learning Paths (level-to-level prerequisites need Grow $229/mo+), max 10 users.

## 2026-09-28 (PM) — plan v2
- Joshua rejected v1 as "uninteractive and academic." Wants: new hire in front of a screen, engaging modules, tests proving mastery, scorecards and accountability.
- v2 written: Valley Pawn Academy on TalentLMS (recommended), 8 levels + manager track from Preston's 16 items, video + real-call clip + scenario test per lesson (80% pass, unlock order), Floor Checks by manager, AI phone role-play sim, hard gates (day-3 firearm cert, no firearm transaction before Level 6, etc.), Monday scorecard from the API.
- Awaiting Joshua on: platform spend, HR-2026-05 send + Preston asks, gate confirmation. Week 1 items 2–4 (curriculum, Level 1 content, shot list) can start without him.

## 2026-09-28 — project opened
- Joshua asked for the plan to get a robust training program off the ground.
- Inventory done (CHANGELOG, BUSINESS_OS HR section, Human Resources/, Call Analysis/, Preston Knowledge Base/, Drive, Slack, Gmail). Nine existing assets, one missing spine (per-employee tracker). Details in the plan.
- Nothing built yet beyond the plan. Nothing sent to anyone.
- Next: Week 1 items 1–3 (curriculum map, TRAINING.json + tracker sheet, evidence backfill). Item 4 and the Preston certificate request wait on Joshua's go (outbound to people).

## Open questions for Joshua (only these)
1. DECIDED: Grow plan — Joshua to purchase in TalentLMS → Subscription. Then enable API key (Account & Settings → Integrations → API) so academy-sync can be built.
2. Go to send HR-2026-05 + ask Preston for the certificate list and Bravo walkthrough recordings.
3. Confirm the gates (Level 1 by day 3; no firearm transaction before Level 6; keys at 90 days + Certified).

## Related open register rows
- 2026-09-23 firearm cert policy (built, not sent; audit incomplete)
- 2026-09-23 P&P v2026.5+ layaway figure → acknowledgment send
- 2026-09-08 weekly-training-pipeline double-fire / rubric definitions
