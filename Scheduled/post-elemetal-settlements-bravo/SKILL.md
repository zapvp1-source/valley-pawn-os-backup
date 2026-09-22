---
name: post-elemetal-settlements-bravo
description: One-time: close the Aug 2026 (and possibly Sept 2026) Elemetal scrap-gold settlement buckets in Bravo POS, with Joshua present to approve Parallels/Bravo screen access.
---

Domain: Full Circle Finance Inc DBA Valley Pawn (Domain 1). Load `enterprise-map` skill first per standing instructions, then `bravo-context` and `vp-operating-rules`.

CONTEXT: Joshua asked (2026-09-21 chat) to get two received Elemetal precious-metals settlements "posted in Bravo." This is a ONE-TIME task fired at 8pm ET specifically because Joshua wants to be present/available to approve the Parallels Desktop screen-access prompt (an earlier attempt this afternoon at 09:32 ET was denied — likely because he wasn't at his desk to approve it).

BACKGROUND — read the full operating guide first:
`/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/OPERATING_GUIDE.md`

STATE AS OF 2026-09-21 ~09:35 ET (verify current state fresh, this may have changed):
- AUGUST 2026 settlement: ALREADY APPROVED AND ARCHIVED. File renamed to `reviews/2026-08_allocations_CLOSED.csv`, uploaded to Drive folder "Accounting Exports > Precious Metals Settlements > 2026-08" (id 1PEemgZCS7XQpkUKrIkPtVbU18fJ01xQK), state.json archived_months includes "2026-08". The Slack post to #gold-trend- FAILED (channel_not_found on documented ID C0BJ8SYTVBN; slack_search_channels found no matching channel — it may be renamed/archived/deleted). **Ask Joshua for the correct channel (or skip the Slack post) rather than guessing.**
  - The 10 Bravo buckets this August settlement closes (net $66,160.08 across 608.1275 dwt):
    CUL: "JULY 2026 GOLD SCRAP" (no-stones, 108.4576 dwt) + "JULY 2026 GOLD W/STONES SCRAP" (stones, 54.3295 dwt)
    HAR: "GOLD W/O STONES 7/31/26" (no-stones, 75.1400 dwt) + "GOLD W STONES" (stones, 72.7907 dwt)
    LEX: "JULY 2026 GOLD SCRAP" (no-stones, 25.3000 dwt) + "JULY 2026 GOLD-STONE SCRAP" (stones, 25.7206 dwt)
    ROA: "ROANOKE JULY GOLD SCRAP" (no-stones, 63.1000 dwt) + "ROANOKE JULY GOLDW/STONE SCRAP" (stones, 103.3993 dwt)
    WAY: "AUGUST 2026 GOLD SCRAP" (no-stones, 31.7100 dwt) + "AUGUST 2026 GOLD STONE SCRAP" (stones, 48.1798 dwt)
  Full detail (including a full per-store dollar breakdown) is in `reviews/2026-08_allocations_CLOSED.csv`.

- SEPTEMBER 2026 settlement: STILL UNAPPROVED (`reviews/2026-09_allocations_REVIEW.csv`, net $38,963.78). It has a real unresolved data question: Elemetal's pre-melt weight (345.700 dwt) is 22.7% higher than the Bravo no-stones-only total (267.2999 dwt) the default classification assumes — much bigger than the ~2.7% gap seen on a normal/clean settlement. The workbook's own note suggests HAR's stones bucket (56.3518 dwt, opened the same day as HAR's no-stones bucket) may have shipped in the same batch, which would bring the gap to 6.4%, but nothing in Bravo confirms this. **Ask Joshua directly (he should be present) which classification is correct before doing ANYTHING with the September buckets in Bravo** — do not guess, do not default silently. If he confirms, recompute/update the workbook accordingly, rename REVIEW->CLOSED, archive to Drive (folder 1IYyifvqI4jTsm-6nXlNSqf0ecCjg4dMi = "Precious Metals Settlements", create a "2026-09" subfolder same as August's pattern), and post to Slack if the channel is resolved by then.

THE ACTUAL BRAVO WORK (the hard, novel part):
There is NO documented procedure anywhere in `bravo-context` or this project for marking a scrap-refining-gold bucket "closed/settled" in Bravo POS. This has never been done by any automation before — it's uncharted UI territory in a live production financial system across 5 stores, real money, no undo. Do this carefully:
1. Run the Bravo contention check first (translate to this session's actual mount path, mirroring `_bravo_foreground_guard.sh`'s logic — check `Bravo Data Extraction/triggers/claimed` and `results/*.result.json` for recent (last 6 min) activity, and `logs/_bravo_foreground_owner.txt` for a live hold). If busy, stop and tell Joshua what collided.
2. `mcp__computer-use__request_access` for "Parallels Desktop" — Joshua should be at his computer to approve this now.
3. Use the `bravo-store-cycle` skill to log into Culpeper first (or whichever store is already open — check the title bar).
4. Navigate read-only first (screenshot, don't click) to find where scrap/refining buckets live in the UI (likely under Inventory or a dedicated Refining/Scrap module) and what a "close" or "settle" action looks like for a bucket. Zoom in and confirm with Joshua verbally/in the moment if the mechanism isn't obvious — he can literally tell you what to click since this is live and he asked to be present at 8pm for exactly this reason.
5. Once you understand the mechanism, close the 10 August buckets listed above, one at a time, verifying the bucket's status actually changed (read the screen after each change — Rule #12, verify against output not assumption) before moving to the next.
6. Cycle through all 5 stores via `bravo-store-cycle` as needed (CUL, HAR, LEX, ROA, WAY).
7. Add whatever you learn about the actual close/settle mechanism into `bravo-context` (the skill's own "How to Extend This Skill" section) so this is documented for next time — this is genuinely new knowledge worth capturing.
8. Acquire/release the `_bravo_foreground_guard.sh`-equivalent flag around the whole session (translate path as in step 1).

Do NOT touch the September buckets in Bravo until the classification question above is resolved with Joshua.

If Parallels/Bravo access is denied or Joshua isn't actually available at 8pm, do not force it — append a row to `Valley Pawn OS/fleet/FAILURE_LEDGER.md` per the standing failure policy and stop; do not DM about the failure.

End with a plain-language summary of what got closed in Bravo, what's still open, and what you learned about the close procedure (for the skill update).