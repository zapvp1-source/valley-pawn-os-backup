# Preston Time Review — STATUS (2026-10-01)

Doc: https://claude.ai/code/artifact/6e7cf7ad-5c1e-428e-b882-9827d9d1db37
- transcripts/ — the 5 recorded store<->Preston Zoom calls (8/21–10/1), local Whisper.
- slack_data/ — Preston's Sept Slack in/outbound (as visible to Joshua's account).
- T-Mobile detail lives in the TFB portal (acct 960053854, Billing → Usage → (540) 836-4200).
Zoom line staged: (540) 202-4200 + 6th calling plan, UNASSIGNED until Joshua talks to Preston Mon 10/5.
Next: assign line → add to internal_roster.json → weekly call-reason report from out/employee.

## 2026-10-15 — Limit-raise effect check (interim)
Task: `preston-call-load-after-limit-change-20261015`, read-only, Slack DM output only.

Confirmed via Joshua↔Preston DM: manager transaction limits raised + communicated 10/8 ~2:31pm
(Joshua asked 2:27pm, Preston "Yes"/"Yes" to raised + told everyone). BEFORE=10/1-10/7,
AFTER=10/8-10/14, no shift needed.

Findings:
- Slack: Chadd's "$750 limit" complaint (#boro-funds, 10/3) is the only dollar-limit friction
  message found all month. Zero recurrence in any of the 5 funds channels 10/8-10/14.
- #mobile-approvals (device-login push approvals, NOT money) flat at 7 requests both weeks —
  not a signal for the dollar-limit change.
- Zoom call-log counts (5 before vs 39 after on 540-202-4200) are NOT a valid before/after
  comparator — the Zoom line itself only started real adoption ~10/6-10/7 (per the note above),
  so the jump is line adoption, not call-volume change. Flagging so nobody downstream
  mis-reads "39 calls" as "8x more calls."
- Transcribed 11 of the AFTER-week recorded calls (7 already done from an earlier 10/8 pass:
  Sandi x2, Jacob Cox x2, staff/x3983, Joshua Burnett; 4 new this run: Walker 10/12, Benjie
  10/8, Chadd 10/12, Uriah 10/13). Reasons: coaching/30-60-90 (3), scheduling/policy (1), bank
  admin (2), deal/procedure question (1), IT/equipment (1), one legitimate compliance escalation
  (Uriah — denied firearm transfer, needed Preston's judgment on the trade-in refund). **Zero of
  11 were a transaction blocked by a dollar limit.**
- T-Mobile cell (540-836-4200) — the real before/after baseline — NOT pulled. tfb.t-mobile.com
  was not already signed in; that login needs Joshua's Face ID on his phone, which this
  unattended run can't trigger. Per the task's own instruction, skipped rather than waited on.

Verdict sent to Joshua in Slack DM: the specific limit friction is gone, but no clean overall
call-minutes number without the T-Mobile pull. Re-run after the 10/16 bill close (see row in
Open Items Register) once Joshua has signed into T-Mobile for Business at least once.

New transcripts: `transcripts/2026-10-08_1312_benjie-moore_0424.txt`,
`transcripts/2026-10-12_0956_walker-tapley_0302.txt`,
`transcripts/2026-10-12_0959_chadd-mcclintic_0857.txt`,
`transcripts/2026-10-13_1126_uriah-tiglao_0435.txt`.

## 2026-10-23 — T-Mobile cell pulled (bill _111 Sep17–Oct16 + current cycle)
Week Mon 10/12–Sat 10/17, cell (540) 836-4200: 81 calls / 487 min. Staff+stores only 6 calls / 6 min
(was 17–51 calls/wk Sep 21–Oct 10) → managers moved to the Zoom line. Hiring candidates 43 calls / 252 min
(Indeed interviews still placed from his cell — hiring confirmation template still says "from (540) 836-4200").
Fortis (card processor) 1 call / 28 min. Unidentified 28 calls / 198 min (incl. recurring x9687, likely personal).
Zoom line same week: 49 calls / 132 min (Walker 17, Chadd 10, Sandi 8). Combined ≈ 619 min ≈ 103 min/workday.
Weekly cell calls: 9/21 100c/559m · 9/28 49c/276m · 10/5 56c/372m · 10/12 81c/487m.
