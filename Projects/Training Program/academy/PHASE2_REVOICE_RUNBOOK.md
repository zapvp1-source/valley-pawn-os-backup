# Phase 2 re-voice (after the ElevenLabs reset on 2026-10-28)

Why: the 2026-10-20 board review fixed 64 lessons. Phase 1 (10/21) voiced every narration change that corrected something wrong (24,928 chars). The remaining narration polish (~10.9k chars) waits for the monthly reset. Full target text: `lessons_target_20261028/` (already includes every phase-1 change; M-01 clip = call070 anxious_pastdue).

Step 0 (added 2026-10-22): before step 1, apply the items in `HARVEST_EDITS_2026-10.md` (monthly knowledge harvest — what calls, texts and staff questions showed) to `lessons_target_20261028/` — key points, scenario questions and floor checks first; change voiced "say" lines only if `voice.py estimate` stays inside the remaining credits. Skip any item that depends on a decision still open in the Policy Queue HARVEST:2026-10 block (default/pull day, firearm returns/denied trades/police transfers/no-serial, 18-20 long guns, low-cash approvals) — those wait for the Policy Day answer. Validate as usual.

Steps (run on the Mac, in this folder):
1. `python3 voice.py estimate` after copying the target into a scratch check is NOT needed — just do:
   - `cp -a lessons backups/20261028-phase2-pre/` (backup)
   - `cp -a lessons_target_20261028/. lessons/`
2. `python3 -I validate_lessons.py` → must be 0 violations (L7-15 scorecard is split in the target).
3. `python3 voice.py estimate` → billable must be ≤ remaining (expect ~10.9k). Then `python3 voice.py generate --all`, then `python3 voice.py verify` → "All … lines cached".
4. `python3 build_scorm.py --all` (strict; no --skip-validate) → ALL GREEN, every row narration_complete true.
5. Upload the changed units to TalentLMS per REPLACE_RUNBOOK.md: L1-01 L1-03 L1-05 L2-03 L2-04 L3-03 L3-04 L4-04 L5-01 L7-02 L7-06 L7-15 L8-00 M-01 (flip Joshua to Instructor in the course, Change → upload → Publish changes, flip back to Learner).
6. Log in STATUS.md, OPEN_ITEMS.md, Valley Pawn OS/CHANGELOG.md, and close the Open Items Register row.
