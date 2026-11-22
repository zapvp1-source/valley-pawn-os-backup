# Fleet schedule audit — Bravo-touching agents (2026-11-21)

Why: Joshua 11/21 — "look at the entire agent fleet and schedule all these things so they just work."
Source: every `fleet/com.valleypawn.*.plist` (192) + Bravo's own result files (`Bravo Data Extraction/results`, 11/7–11/21). Read only. Nothing rescheduled yet.

## 1. What the results say (last 15 days, a day counts only if every store came back)
| Job | Days complete | Note |
|---|---|---|
| Monday reports (aged inventory, layaways, 75-day, employee activity, Chekkit inactives, EOM) | 4 of 4 | solid |
| Items to price | 14 of 15 | |
| Daily GL posting | 12 of 15 | |
| Sold / discount detail, intake detail | 12 of 15 | |
| Funds verification (safe journal) | 10 of 13 | |
| Daily GL export | 8 of 15 | 466 failed store attempts ("Could not select store"), carried by retries |
| Jewelry nightly counts | 0 of 13 (24 of 61 store-nights) | "Charms"/"Brooches" category returns no count and the run refuses |
| NICS month-to-date | 0 successes, 280 failed attempts | "Could not locate the report Start/End date" at every store |
| Morning pawn-walk / sold / discount reviews | 78 runs skipped "Bravo not ready" | see 2 |

## 2. Schedule collisions (one shared Bravo login; a 5-store pull takes 25–40 minutes)
Morning, every day: 6:30 relaunch → 6:50 morning-pull (median 25 min, worst 40) → 7:15 pawn → 7:45 sold + jewelry catch-up → 7:50 daily GL → 8:00 items to price → 8:25 discount → 9:15 jewelry watchdog. Six jobs are spaced 5–30 minutes apart behind a pull that needs up to 40. They queue, time out, and report "Bravo not ready".
Evening: 6:30 funds → 7:00 markdown → 7:15 asset recovery → 8:00 monthly prestage → 8:30 jewelry (9–27 min per store) → 9:10 ceo-week (Sun) → 10:30 map → 11:15 loan reminders → 12:45 daily GL.
Night: 2:00–4:30 monthly jobs, 3:15 daily GL, 3:35 intake backfill, 4:00 relaunch.

## 3. Bravo-touching agents and their times
asset-recovery 19:15 · bonus-close-pull d1 11:30 · bravo-daily-gl 00:45 03:15 07:50 13:10 · bravo-health-watchdog 05:00 17:00 · bravo-map-oneshot 22:30, Sun 07:00 · bravo-relaunch 04:00 06:30 · ceo-week-pull Sun 21:10, Mon 07:40 · chekkit-review-invites Tue 16:40 · daily-report-pawn 07:15 · daily-report-sold 07:45 · daily-report-discount 08:25 · eom-gl-export d1 06:00 · forfeiture-winback Sun 12:30 · funds-verification 18:30 · gift-credit d2 02:30 · intake-backfill 03:35 · items-to-price 08:00 · jewelry-catchup 07:45 (6 days) · jewelry-nightly 20:30 (6 days) · loan-reminders 23:15 · mobilepawn-participation d1–3 09:15 · monday-pull Sun 16:30, Mon 05:30 · monthly-employee-rankings d1 02:00 · morning-pull 06:50 · new-customer-report d3 07:00 · nics-monthly d1 09:30 · nics-weekly-mtd Mon 09:30 · sales-tax-monthly d1 08:00 · scrap-rankings-monthly d1 04:30 · store-kpis-weekly Mon 10:30 · markdown-verification-pull 19:00 · monthly-prestage 20:00 · storetraffic-nightly 21:35

## 4. Fix order (proposed)
1. Morning: one sequenced chain instead of six clocks — each job starts when the one before it finishes (single runner, fixed order, one health check at the top). Removes the "Bravo not ready" skips.
2. NICS month-to-date handler (date boxes changed in Bravo 2026.10).
3. Jewelry nightly: treat an empty Charms/Brooches category as zero when the prior day was zero, instead of failing the store.
4. Daily GL export store-select failures.
5. Evening and night: same chain pattern; fixed slots with 45–60 minute gaps for anything that cannot chain.
Rule for all: additive, one change at a time, each proven for a week before the next.
