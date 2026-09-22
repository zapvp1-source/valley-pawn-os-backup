# What's actually working and what isn't

Updated **2026-09-21 13:50**. Read with the posting app's own token, day-by-day — never lifetime
rates, which are dominated by the 9/12–9/17 outage and say nothing about now.

---

## Bottom line

**Daily tier: reliable.** Nine daily publications have posted every open day since the 9/17 native
conversion.

**Weekly tier: half.** 4 of 12 published Monday 9/21 after two Mondays of nothing. The rest have a
named cause and a fix in flight.

**Nothing in the fleet is dead.** Zero tasks have produced nothing in 14 days.

---

## Fixed since this document was first written

| Was | Now |
|---|---|
| `daily-unopened-email-eval` — worst in fleet, 1/7 days | **FIXED.** Native agent `com.valleypawn.mail-brief` (18:00 daily) reads Apple Mail's Envelope Index directly. Verified: 216 unopened, real senders and subjects. Old Cowork task disabled. |
| Unified search stale 9 days, "needs Full Disk Access" | **FIXED and the diagnosis was wrong.** vp-runner always had Full Disk Access (proved by reading Mail *and* Messages). Index is current: 349,437 mail rows, newest message today 12:51. |
| `usearch-verify` demanding FDA every night | **FIXED.** Rewritten to say "do NOT grant Full Disk Access; vp-runner already has it." |
| Monday data "missing" | **FIXED — my bug.** The Sunday 16:30 pull stamped files with SUNDAY's date while Monday tasks look for TODAY's. All 25 CSVs were on disk under the wrong date. Now runs Sunday 16:30 **and** Monday 05:30. |

## Claims withdrawn — these were never broken

| Claim | Reality |
|---|---|
| "`daily-items-to-price` — WAY stalls at 241/247" | All five stores pull daily (WAY 238 today, 226 on 9/20, 229 on 9/19); posted 9/19, 9/20, 9/21. The stall was **one incident on 9/18**. |
| "`jewelry-onhand` — LEX wedges" | 8 rows per store, all five stores, every open day. Blank Sunday (closed) and blank until 20:30 today. |
| "`pawn-walk` posts empty messages" (3 days in the ledger) | Posts are **1,460–2,206 characters** of correct report. A Cowork-connector read cannot see another app's message text. |
| "Chekkit's dashboard won't load" | Loads instantly, full data, first attempt. |
| "cloudcover is broken at 48.7%" | Posting normally. That was a lifetime figure dominated by the outage. |

**Five withdrawn claims, three of them causes a failed run invented about itself** (1Password,
empty messages, Chekkit) **which a session then repeated without testing.** The operating rules
already forbid this. The rule isn't the problem.

---

## Still open, with real causes

| Task | Cause | Fix |
|---|---|---|
| `review-obtained-last-week` | Its own words: *"no live user present to approve site access"* at 03:27. Not Chekkit — a **permission card** in an unattended session. | `chromePermissionMode = "skip_all_permission_checks"` was applied to 27 tasks on 9/09 — **this task was never in the list.** Registry edit, mechanism already proven. |
| `google-reviews-post-watchdog` | Same class, same hour. | Same fix; audit will confirm. |
| `monday-bravo-combined-compile` | **Behaved correctly** — refused to publish Sep 6 sales figures as current (Rule 18). | Needs a fresh month-to-date sales file. `weekly-store-kpis` pulled exactly that at 10:42 today, unprompted, via the host queue. |
| `weekly-loan-review-canvas-refresh` | No current-week Loan/Layaway report to refresh from. | Downstream of `combined-compile`. |
| `nics-weekly-mtd-ranking`, `layaway-yield-weekly` | Not yet diagnosed. | Next. |

---

## The two structural facts that explain most of the history

**1. `Control_your_Mac` is gone from scheduled sessions — permanently.** Proven by a probe run
inside a real scheduled session, *after* Joshua confirmed his connectors show as connected. What the
app's settings show and what a scheduled run receives are different things. Eleven weekly tasks
gated on it. Native agents and the host job queue are the only durable path. **Do not re-test this.**

**2. Scheduled sessions are "unattended" for browser permissions at every hour**, not just
overnight. That is why a browser task can fail at 11:02 AM the same way it fails at 03:27. The
permission-skip flag exists for exactly this and must be set on every browser-driving task.

---

## What would make this provable rather than hopeful

The daily tier already is: native agents, receipts, a nightly self-testing doctor, and a 36-scenario
sandbox with mutation testing behind it.

The weekly tier still depends on Cowork sessions firing correctly. Getting the data on disk removed
the hard blocker; converting each report's *analysis* to a script a native agent can run is the
remaining work, and it is what turns Monday from "should work" into "provably works."
