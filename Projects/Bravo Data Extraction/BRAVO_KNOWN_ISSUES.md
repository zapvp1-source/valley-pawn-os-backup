
---
## RUN -- 2026-07-27 (PAWN WALK)
intake-detail (Claude Pawn Walks) for 2026-07-26: FAILED, 0 CSVs, no result.json.

Timeline:
- Health gate (bravo_ensure_healthy.sh CUL) PASSED instantly (Bravo already healthy/running).
- Trigger intake-detail-2026-07-27T09-10-06 dropped 09:10:06. NOT claimed by watcher for ~29 min even though Bravo/watcher were alive -- root cause was a legitimate backlog: watcher was mid-processing an unrelated Monday job (vpops-trigger-dropper-2026-07-27T09-06-58, multi-cell employee-activity + loans-75-days-past-due + layaways across all 5 stores), which didn't finish until 09:38. NOT a hang, just Monday-morning queue contention -- worth considering a later fire time or queue priority for PAWN WALK on Mondays.
- Did ONE watcher restart (_restart_watcher.ps1) at ~09:12 while diagnosing the claim delay, before realizing it was legitimate backlog. watcher.last_started.txt did NOT advance after the restart (confirms prior memory note this file is stale/unreliable -- verify by claim/output instead).
- Trigger finally claimed ~09:39. CUL: 3/3 attempts "Claude Pawn Walks did not load (wrong report / no item columns, loads with Age=1 criteria instead of Transaction Date/Category/FullDescription/LoanAmount)" -- same recurring regression documented 2026-06-16, 2026-06-20, 2026-07-10, 2026-07-11. Still unresolved.
- HAR: same wrong-report signature attempts 1-2. Attempt 3 hit a NEW failure: "GetBravoRoot: Bravo window not found" -- Bravo actually crashed/closed mid-run (PID changed 13272->13048, mem ~1.2GB->428MB, CPU reset, window title lost store suffix). Different from the wrong-report issue -- a genuine crash.
- LEX: EnsureStore failed -- could not reach Dashboard post-crash, "Lock Session" element not found. Correctly flagged cause=nav (not lockout), breaker not incremented -- no login-hammering occurred.
- A second trigger (re-dropped as intake-detail-2026-07-27T09-20-00 during the earlier claim-delay diagnosis) got picked up by an apparently-fresh watcher process (bravo_watcher.ahk PID 5084->9288, CPU reset to 0 -- possible auto-restart after the Bravo crash, cause not confirmed) at 09:46:42. Found Bravo at a "Select a store" screen (confirms the crash), self-recovered login to CUL, reached Dashboard 09:47:09, logged "settling 90s before report" -- then went SILENT. No further log lines through 09:53:27+ (6.5+ min past the expected 90s settle). No result.json, no CSVs from either trigger.
- Per policy (max ONE relaunch cycle beyond the health gate, no login-hammering), did not attempt a second watcher/Bravo restart. Stopped and reported failure per the v2 failure policy: DM to Joshua only, no post to #pawn-walks.

NEXT SESSION should investigate, in priority order:
1. The settling-90s-then-silent hang on the 09-20-00 run -- check for a screenshot/crash artifact, confirm whether Bravo.exe (was PID 13048) and bravo_watcher.ahk (was PID 9288) are still alive/responsive.
2. The recurring "Claude Pawn Walks wrong report / Age=1 criteria" regression -- 5th occurrence now (6/16, 6/20, 7/10, 7/11, 7/27). Needs the permanent Bravo-side fix (re-save/re-verify the saved report + list-view layout per store), not another automation retry-count bump.
3. Whether the mid-run Bravo crash (GetBravoRoot: Bravo window not found on HAR) is a new failure mode or related to resource pressure from the Monday backlog job that ran immediately before.
