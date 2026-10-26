# Phase 2 re-voice (after the ElevenLabs reset on 2026-10-28)

Why: the 2026-10-20 board review fixed 64 lessons. Phase 1 (10/21) voiced every narration change that corrected something wrong (24,928 chars). The remaining narration polish (~10.9k chars) waits for the monthly reset. Full target text: `lessons_target_20261028/` (already includes every phase-1 change; M-01 clip = call070 anxious_pastdue).

Step 0 — ON HOLD (CEO 2026-10-25): do NOT apply HARVEST_EDITS_2026-10.md until the CEO approves; skip this step.

Also in the target (2026-10-25): the CEO's 2026-10-25 decisions are already applied to BOTH `lessons/` and `lessons_target_20261028/` (loan timeline wording / no 'grace period', late fee on the 6th day past due, account-holder verification = full name + DOB + phone on file or a signed POA, Gusto titles, no personal names, Market Manager contact via Slack / Zoom line 540-202-4200 and voice-call call-outs, training in store on the clock, weekly Slack huddle, phone gate = 7.3 + five practice calls, returns need an email, discount ladder, phone turn-aways, layaway cancellation, working alone, #deal-of-the-week Monday, #basics checks). Pre-edit copies: `backups/20261025-ceo-decisions-pre/`. Validated: target 0 violations.

Steps (run on the Mac, in this folder):
1. `python3 voice.py estimate` after copying the target into a scratch check is NOT needed — just do:
   - `cp -a lessons backups/20261028-phase2-pre/` (backup)
   - `cp -a lessons_target_20261028/. lessons/`
2. `python3 -I validate_lessons.py` → must be 0 violations (L7-15 scorecard is split in the target).
3. `python3 voice.py estimate` → billable must be ≤ remaining (expect ~83k: ~10.9k phase-2 polish + ~65.7k from the 2026-10-25 CEO decisions, 120 changed narration/objective lines + ~6.7k for the two NEW lessons). If billable exceeds the remaining balance, do not generate partially: stop here and add one line to Life OS/HUMAN_QUEUE.md. Then `python3 voice.py generate --all`, then `python3 voice.py verify` → "All … lines cached".
4. `python3 build_scorm.py --all` (strict; no --skip-validate) → ALL GREEN, every row narration_complete true.
5. Upload the changed units to TalentLMS per REPLACE_RUNBOOK.md (unit ids in talentlms_units.json; 64 units = the original phase-2 list + every lesson changed by the 2026-10-25 CEO decisions): L1-00 L1-01 L1-02 L1-03 L1-04 L1-05 L1-06 L1-07 L2-01 L2-02 L2-03 L2-04 L2-05 L3-00 L3-01 L3-02 L3-03 L3-04 L3-05 L3-06 L4-01 L4-02 L4-03 L4-04 L4-05 L4-06 L5-01 L5-02 L5-03 L5-04 L5-05 L6-00 L6-01 L6-02 L6-03 L6-04 L6-05 L6-06 L7-00 L7-01 L7-02 L7-03 L7-04 L7-05 L7-06 L7-07 L7-08 L7-10 L7-12 L7-15 L8-00 L8-01 L8-02 L8-03 L8-04 L8-05 L8-06 M-00 M-01 M-02 M-03 M-04 M-05 M-06 (flip Joshua to Instructor in the course, Change → upload → Publish changes, flip back to Learner). Also voice, build and upload the NEW lessons in NEW_LESSONS_2026-10-25.json (if present) per UPLOAD_RUNBOOK.md, appended in order in their course.
6. Log in STATUS.md, OPEN_ITEMS.md, Valley Pawn OS/CHANGELOG.md, and close the Open Items Register row.
