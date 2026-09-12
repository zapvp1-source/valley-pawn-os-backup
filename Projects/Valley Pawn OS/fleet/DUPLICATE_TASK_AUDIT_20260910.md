# Scheduled-Task Duplicate Audit — 2026-09-10

Full sweep of all enabled Cowork scheduled tasks. Findings only — nothing below was changed
except the two items marked **DONE**.

---

## 1. Preston channel (the one that started this) — **DONE**

| task | was | now |
|---|---|---|
| `preston-interactive-assistant` | every 2 hrs, 7am–6pm | **every 5 min, 7am–10pm** |
| `preston-claude-evening-check` | hourly, 6pm–10pm | **disabled — superseded** (rollback hold) |
| `preston-ebay-feedback-watch` | — | already disabled 2026-08-26 |

Native layer (unchanged, still running): `com.valleypawn.preston-watch` launchd agent, every
120 s, posts the "Got it, Preston — on it" ack. Never does the work by design.

**Open item:** lower that agent's `StartInterval` from 120 → 60 so the ack lands inside a minute.
Blocked — editing `~/Library/LaunchAgents` is refused by the permission classifier. Needs Joshua
to run it (command in chat) or a Bash permission rule.

---

## 2. Real duplicates worth fixing next

**Hiring intake — two tasks routing the same applicants to Preston**
- `indeed-applicant-outreach` (hourly 9am–7pm) — also still carries a hardcoded, now-expired
  interview window "Mon 9/7–Wed 9/9". Should be fixed regardless.
- `hiring-inbox-watch` (5×/day Mon–Sat)

**Manager video — double-post risk on Wednesdays**
- `vp-casual-video-daily` (daily 7pm) and `vp-staff-video-chase` (Wed 11:15am) both collect,
  process AND schedule the same Slack submissions.

**`#store-performance` — ordering bug**
- `weekly-store-perf-canvas-refresh` runs Mon 9:37am from "latest weekly store KPI files"
- `weekly-store-kpis` doesn't produce those files until Mon 10:39am
- → the canvas is refreshed from last week's data every week.

**Three GA4 pulls of the same property**
- `weekly-analytics-summary` (Mon 1am), `vp-website-shop-weekly-report` (Mon 7:48am),
  `vp-website-trend-daily-refresh` (daily 12:55am)

**Three Sunday-evening Bravo sessions against the same POS**
- `monday-bravo-combined-run` 6:08pm, `weekly-markdown-verification-pull` 7pm,
  `monday-bravo-cell-gapfill` 8:39pm

**Four near-identical Slack-Canvas refresh tasks** (loan / layaway / employee-perf / aged-inventory
/ store-perf, all Mon 9:24–9:37) — one parameterized task would replace five.

**Two eBay weekly audits + two eBay listing-quality audits**
- `ebay-weekly-channel-audit` (Mon) vs `weekly-online-store-audit` (Sun)
- `ebay-weekly-quality-fix` (Mon) vs `ebay-title-photo-accuracy-audit` (Sun)

**Tuesday supply order — auto-approve logic duplicated in two tasks**
- `tuesday-supply-summary` and `tuesday-supply-checkout` each independently decide to place
  orders under $500. `tuesday-supply-checkout` also re-fires 32×/Tuesday.

**Four overlapping search indexers** — `unified-search-index-refresh` already covers Drive and
Photos OCR, yet `gdrive-cache-refresh` and `document-photos-index-refresh` index the same sources.

---

## 3. Cleanup backlog (low risk, no urgency)

- **13 dead one-shots** still listed, all disabled and already fired.
- **5 disabled-but-unannotated** tasks with no supersession note: `weekly-social-media-content`,
  `wordpress-token-keepalive`, `store-mail-archive-sweep`, `jewelry-onhand-nightly-compare`,
  `jewelry-count-reconciliation` (this last one has **never run**).
- **2 recurring tasks still titled "⭐ RUN NOW ONCE"** — `monthly-publication-audit`,
  `monday-bravo-cell-gapfill`. Will confuse the next hygiene sweep.
- **`weekly-training-pipeline` is still in TEST WEEK — DM only mode.** The test flag was never
  lifted, so managers/Preston/#call-insights have never received it.
- `task-hygiene-sweep` ran 2026-09-01 and left all of the above in place — its criteria are too
  narrow.

---

## 4. Skill-level duplicate

Two skills, same job: `loan-layaway-review` and `weekly-loan-layaway-review`.
