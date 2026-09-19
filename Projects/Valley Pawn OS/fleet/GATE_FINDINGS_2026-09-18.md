# Fleet gate — what is actually broken

2026-09-18. Produced by `bin/vp_audit.py` (measurement) → `bin/fleet_gate.py` (verdict).
Both are deterministic: same input, same verdict, every time. Full table: `fleet/audit.json`.

---

## The headline

**The fleet is not 26 broken tasks. It is about 6 genuinely unreliable daily tasks, plus a history
of infrastructure outages that took everything down at once.**

**60% of every recorded miss (151 of 250) falls on just 17 dates** where 5 or more unrelated tasks
missed simultaneously. Those are infrastructure events. A task's raw delivery rate is dragged down
by every one of them, which is why the raw numbers made the whole fleet look chronically broken.

Remove the shared-outage dates and **eleven tasks are at 100%**:

| Task | Raw rate | Excluding fleet events |
|---|---:|---:|
| weekly-timekeeping-analysis | 33.3% | **100%** |
| review-obtained-last-week | 57.1% | **100%** |
| weekly-markdown-verification-review | 60.0% | **100%** |
| layaway-yield-weekly | 62.5% | **100%** |
| monday-bravo-combined-compile | 75.0% | **100%** |
| weekly-store-kpis | 75.0% | **100%** |
| nics-weekly-mtd-ranking | 75.0% | **100%** |
| monday-bravo-postcheck | 75.0% | **100%** |
| daily-unopened-email-eval | 76.0% | **100%** |
| weekly-returns-summary | 80.0% | **100%** |
| chekkit-unanswered-alert | 82.1% | **100%** |

Every single miss these tasks have ever recorded happened on a day the infrastructure was down.
**They were never flaky.** Any plan that listed them as 11 separate repairs was 11 units of wasted
work. This is the single most important correction in this review.

---

## The outage dates

| Window | Dates | What it was |
|---|---|---|
| **9/12 – 9/17** | 9/12 (9), 9/13 (9), **9/14 (23)**, 9/15 (14), 9/16 (11), 9/17 (7) | The osascript connector disappearing from scheduled sessions. Root-caused 2026-09-17; fixed by converting 11 tasks to native launchd agents. |
| **8/17 – 8/20** | 8/17 (9), 8/18 (6), 8/19 (11), 8/20 (11) | A second multi-day event. **Cause not yet confirmed** — stated as unknown rather than guessed. |
| Scattered | 7/24 (6), 8/8 (5), 8/10 (8), 8/14 (5), 8/30 (5), 8/31 (5), 9/10 (7) | Single-day events, several of them Mondays — consistent with the Monday Bravo combined run failing and cascading to everything downstream of it. |

9/14 alone took out 23 tasks. That one date does more damage to the fleet's numbers than every
task-specific defect combined.

---

## What is genuinely task-specific

These are still below the 95% floor **after** removing every shared-outage date, so the defect is in
the task or its data path — not the infrastructure. This is the real repair list, worst first.

| Task | Rate excl. events | Non-shared misses | Status |
|---|---:|---:|---|
| daily-cloudcover-check | 48.7% (of 39) | 20 | Needs diagnosis |
| pawn-walk | 50.0% (of 44) | 22 | Intake pipeline was dark 9/12–9/18; recovered 9/18, needs a clean week to confirm |
| jewelry-onhand-nightly-pull | 63.6% (of 22) | 8 | Needs diagnosis |
| daily-items-to-price | 70.8% (of 48) | 14 | Known cause: the "Show More" grid stall (Waynesboro got 241 of 247 rows on 9/18) |
| daily-dress-code-check | 76.5% (of 34) | 8 | Needs diagnosis |
| discount-review | 79.2% (of 24) | 5 | Now native; needs a clean week |
| fleet-guardian | 79.2% / 92.0% | 5 / 2 | Two daily instances, both below floor |
| chekkit-unanswered-eod-followup | 84.0% (of 25) | 4 | Needs diagnosis |
| daily-clockin-check | 86.1% (of 36) | 5 | Needs diagnosis |
| sold-review | 88.0% (of 25) | 3 | Now native; needs a clean week |
| daily-funds-verification | 88.4% (of 43) | 5 | Needs diagnosis |

Note the shape: **every one is a DAILY task.** The weekly tier has no task-specific defects at all.

---

## Retire list: empty

The first run of the gate recommended retiring 4 tasks. **All four were wrong, and the tool was
fixed rather than the verdicts hand-waved:**

- `bonus-month-close-pull` was scored 0/1 and labelled "has never worked." It *had* worked — six
  days late. A task that produces its artifact off-schedule is off-schedule, not absent. Now
  REMEDIATE. **A recommendation to delete something has to clear a higher bar than a recommendation
  to fix it**, and it did not.
- `monthly-gun-audit-report`, `monthly-scrap-rankings`, `vp-new-customer-report` each had 1–2
  expected instances, with some of those landing inside outage windows. Retiring a task on n=1 is
  not a finding. The gate now requires **3+ instances** before it will recommend retirement; below
  that it reports NO EVIDENCE and says to watch it.

---

## Why zero tasks pass the gate today

Not because the fleet is worthless — because **every task's 60-day window contains the 9/12–9/17
outage**, and the gate's ceiling is 1 consecutive miss. Nothing that was running in mid-September
can pass a 60-day gate, no matter how healthy it is now.

**A gate run over a window containing a fleet-wide outage measures the outage, not the fleet.**

## The next action

The fixes that matter already shipped: the osascript root cause (9/17, native conversion), the
intake pipeline recovery (9/18), measurement (9/18), isolation testing (9/18). What the fleet needs
now is **a clean measurement week** — 7 consecutive days with no infrastructure event — and then the
gate re-run over that window. That is the first time a GO verdict can mean anything.

In parallel, the 11 task-specific defects above are real work that does not depend on the clean week.
Start with the four worst: cloudcover, pawn-walk, jewelry-onhand, items-to-price.

**Do not re-litigate the 11 tasks at 100%. They are fine.**
