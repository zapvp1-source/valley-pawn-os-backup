# Valley Pawn Academy — Final Pre-Launch Review (board brief)

You are one seat on a three-person expert board reviewing the Valley Pawn Academy (TalentLMS, 71 SCORM lessons: Levels 1–8 + Manager Track) before launch. The owner, Joshua Davis (CEO, Full Circle Finance Inc DBA Valley Pawn — five Virginia pawn stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke; each a Type 02 FFL), will walk through the course himself right after this review, then launch it to staff. Preston Peters is the Market Manager. He wants a top-notch program: accurate, consistent, pawn-business substance, modern learning design, and a pipeline that just works.

## Files (all under /home/claude/academy_review)
- `ALL_LESSONS_DUMP.txt` — every lesson in plain text, in order (id, title, objectives, sources, slides with narration `say`, key points, every quiz question with options; `*` = correct). ~4,800 lines. This is what the learner sees/hears.
- `lessons/L<n>/*.json` — the lesson sources (same content, JSON per LESSON_SPEC.md).
- `LESSON_SPEC.md` — the format and writing rules every lesson must obey.
- `sources/SOURCES_CURRENT.md` — THE governing policy text: P&P Manual v2026.8 (line 10 onward) and the Employee Handbook v2026.6 (line 1110 onward). This is the source of truth for every company rule. Note: a Handbook v2026.7 exists on disk but this consolidated file was built from v2026.6.
- `sources/*.txt` — HR-2026-10 Sales Training policy, Training At The Store policy, OB-2026-01 Rev2 onboarding checklist.
- `ACADEMY_REVIEW_2026-10-14.md` — the previous full review (6 days ago). Its section 3 has 76 management decisions with defaults already written into the lessons. DO NOT re-litigate those defaults unless the default contradicts the P&P/Handbook/law — then say so with the citation. Section 4 lists cosmetic splits deferred to after Oct 28 — don't repeat those.
- `review_2026-10-14/*_findings.md` and `*_changes.md` — the per-level findings/changes from that review.
- `OPEN_ITEMS.md`, `HUDDLE_INPUTS.md` — accumulated open questions and huddle inputs (context; many already resolved in the lessons).
- `build_scorm.py`, `voice.py`, `check_answer_bias.py`, `render_check.py`, `BUILD_README.md`, `UPLOAD_RUNBOOK.md`, `REPLACE_RUNBOOK.md` — the build pipeline. `ONBOARDING_FLOW.md`, `TRAINING_PROGRAM_MASTER_PLAN.md`, `STATUS.md` — program design and history.

## Known facts to hold in mind
- Loan timeline (company rule, settled): 30-day term; day 1 past due = day after due date; grace through day 15; hold through day 30; pull from day 31, finished by day 61; past 61 needs Joshua. Company no longer holds loans past 75 days; the weekly loan review was retired 10/14.
- Discounts: associates 30% ceiling, 10% normal give; 31–50% needs a manager; nothing past 50% ever.
- Greeting (Joshua 10/13): every customer gets "Have you ever been here before?"; first-timer → what makes us different: 30-day warranty on everything, free layaway, mobile app (pay loans / shop from anywhere).
- The Slack Q&A channel is changing: #ask-handbook is being retired in favour of **#ask-goldilocks** (bot "Goldilocks") at launch. Lessons that say "#ask-handbook" need a decision/flag.
- Store hours changed 10/1: any 6-day store closes 5 PM Saturday; Culpeper & Roanoke Mon–Fri 10–6, Sat 10–5. The P&P §01.01 hours text is known-stale.
- Virginia assault-firearm/magazine ban is enjoined — must NOT be taught as law. Under-21 handgun rule rests on federal law. Polygraph: never taught (EPPA).
- Layaway is free/interest-free; three tiers in P&P §05.05; 60+ days no payment → expired.
- Firearms lessons: no firearm images; procedure only.
- Narration is TTS (ElevenLabs). Level intros (N.0) are ungraded previews in Joshua's cloned voice. Re-recording budget is tight until Oct 28 (~27k characters left), so prefer fixes that change few narration lines; quiz/bullet/key-point/why edits cost nothing.
- TalentLMS: 9 courses (126–134), all 71 units uploaded 10/15 on the current build. Portal is still on the Free plan (10 active-course limit, 10-user limit, no API, no Learning Paths) — Grow plan was chosen but not confirmed purchased.

## Output
Write your findings to the file named in your task prompt, as Markdown. For EVERY finding give:
`| # | Severity | Lesson/File | Where (slide/Q/line) | Finding (quote the exact text) | Correction (exact replacement text or action) | Source/citation |`
Severity scale: **BLOCKER** (wrong rule/law or broken experience — must not launch with it), **MUST-FIX** (inconsistency, misleading, or spec violation a learner would notice), **SHOULD-FIX** (quality improvement, cheap), **NOTE** (observation, no action). Be concrete and exhaustive; a vague finding is useless. Quote exactly. Do not pad with praise. Finish with a short "Verdict" paragraph: launch-ready / launch after fixes / not ready, and why.
