PAWN WALK STATUS — 2026-07-30 (processing 2026-07-29 data)

RESULT: incomplete. 1/5 stores captured.
- CUL: SUCCESS, 28 rows (07:25 run)
- HAR, LEX, ROA, WAY: FAILED in BOTH the 07:22 primary run and the 09:37 resume
  run — 100% failure rate (12/12 selection attempts across 4 stores x 3 tries
  each), all with identical signature:
  "Claude Pawn Walks did not load after 3 selection attempts (wrong report /
  no item columns)"

ADDITIONAL: mid-primary-run, Bravo.exe crashed outright ("Bravo window not
found" on LEX/ROA/WAY, tasklist confirmed 0 instances running ~07:35). Watcher
self-healed (relaunched Bravo, watcher restart logged 07:33:15 and again
08:13:21). Resume run at 09:37 started clean (fresh login) but still hit the
same "wrong report" failure on all 4 stores.

ROOT CAUSE ASSESSMENT:
This is NOT the old intermittent single-store flakiness seen 7/27-7/29 (where
1 store out of 5 occasionally failed and self-corrected on retry). Today it is
100% reproducible across every store, across two independent runs including
one right after a fresh Bravo relaunch. Reviewed reports/IntakeDetail.ahk:
IntakeSelectSavedReportCommitted() finds the report BY NAME (not position)
and the combo consistently commits to the same Object_Layout GUID
(9311fe9f-55a4-422f-aa1c-dd869548bd95) every time — including on today's
failures — yet the rendered grid lacks the FullDescription/Category columns.
The post-Ok verification window is already generous (~30s render wait + 5s +
up to 16s of column polling) and still fails uniformly. This points away from
a timing race and toward either:
  (a) the "Claude Pawn Walks" saved report definition itself changed/broke
      server-side in Bravo (would explain same GUID, wrong columns, 100%
      reproducible), or
  (b) broader Bravo instability today (the mid-run crash is a second,
      independent bad sign) possibly tied to the VM not having a clean
      reboot since 2026-07-23 12:25 PM and only ~4.3GB/8GB RAM free.
Did NOT attempt a blind fix (e.g., widening timers) because the timing
window was already generous and the failure is deterministic, not marginal —
a code timing tweak is unlikely to fix a server-side report definition
issue. Needs a human/visual check of the "Claude Pawn Walks" saved report in
Bravo (Loans/Buys > Custom Reports) to confirm whether its column layout
still matches what the automation expects.

WHAT'S DONE:
- Slack message format updated per Joshua's request (2026-07-30): overpay
  flags now grouped by store with a header per store, one line per flagged
  item, in the SAME post (run_daily_intake.py build_slack_message()) —
  previously flat-sorted by margin across all stores, capped at 12.
  New cap is 25 total, still grouped by store.

NEXT STEPS FOR NEXT SESSION:
1. Do NOT keep blind-retrying the same trigger — already tried twice at 100%
   failure. Needs eyes-on Bravo (Joshua or a computer-use session) to check
   whether "Claude Pawn Walks" custom report layout still has
   FullDescription/Category columns, or if it got edited/reset.
2. If the report definition is fine, escalate to VM health: consider a full
   Windows reboot (not just Bravo relaunch) — uptime since 7/23, memory
   headroom is tight (4.3GB free of 8GB).
3. Once HAR/LEX/ROA/WAY are recovered, run compile:
   /usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/run_daily_intake.py' '2026-07-29'
4. Do NOT post a partial (CUL-only) summary as if it's the full daily walk —
   held off intentionally, would be misleading with 4/5 stores missing.
