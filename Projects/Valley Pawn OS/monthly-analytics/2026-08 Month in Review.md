# Month in Review — August 2026 — LIVE TEST of monthly-eom-recap logic (run in-session 2026-09-05 ~15:35 ET)

Source: each channel's own August posts (Slack history 8/1–8/31; pawn-walks from Pawn Walks/daily/*_summary.json). Gate: weekly channels ≥3 complete weekly posts; daily channels ≥60% of days.

| Channel | Result | Note |
|---|---|---|
| #loan-review | POSTED | 5 weekly posts (8/31 partial) |
| #layaway-review | POSTED | 5 weekly posts |
| #aged-inventory-review | POSTED | 3 complete weeks + markdown check |
| #first-payment-default | SKIPPED — gate | every August post was missing stores (Culpeper absent all month); no complete week to summarize |
| #timekeeping-summary | POSTED | 5 weeks incl. the 9/3 catch-up for Aug 24–30 |
| #weekly-returns-summary | POSTED | 5 weekly posts; 22 returns / $2,942.45 |
| #daily-funds-reconcilation | DRAFT (classifier blocked autonomous post) | 23/31 days; 20 matched |
| #pawn-walks | DRAFT (classifier blocked autonomous post) | 16 reporting days; 1,191 items, 91 flags |
| #google-reviews | POSTED | 4 weekly posts (week of Aug 2–8 never posted) |
| #social-media | POSTED | 5 weekly recaps = 66 posts |
| #email-campiagns | POSTED | weekly KPI + efficiency posts |
| #website | DRAFT (classifier blocked autonomous post) | 3 weekly analytics posts (week of Aug 10 missing) |
| #ai-marketing | POSTED | 4 scorecards / 5 health checks |
| #ebay-performance | POSTED | weekly rankings + efficiency + ratings sweep |
| #blog-posts | POSTED | 7 posts |

Posted: 11 · Draft for Joshua: 3 · Skipped by gate: 1.

Findings for the scheduled task: (1) the classifier blocked autonomous posts in 3 channels this session (funds, pawn-walks, website) — when the registered task runs on the 1st it inherits its own approvals, so Joshua should click "Run now" once after registering to pre-approve; (2) #first-payment-default's weekly producer has been posting partial data all month (Culpeper cell failing) — that's a monday-bravo-combined-compile/pipeline issue to fix, not a recap issue; (3) #google-reviews and #website each lost one week in August (8/10 and 8/17 respectively) — now covered by the new expected_outputs entries.

---

# Scheduled run — monthly-eom-recap — 2026-09-05 ~16:30 ET (first registered run / pre-approval pass)

Target month: August 2026. Slack connector only. Duplicate guard read the last 30 messages per channel; 11 channels already carried the August Month in Review from the 15:35 live test and were skipped.

| Channel | Result | Note |
|---|---|---|
| #loan-review | skipped-duplicate | posted 15:37 |
| #layaway-review | skipped-duplicate | posted 15:37 |
| #aged-inventory-review | skipped-duplicate | posted 15:37 |
| #first-payment-default | skipped-gate | 3 August posts (8/3, 8/24, 8/31) but every one missing stores (Culpeper all month; 8/31 only 2 of 5) — no complete week |
| #timekeeping-summary | skipped-duplicate | posted 15:37 |
| #weekly-returns-summary | skipped-duplicate | posted 15:38 |
| #daily-funds-reconcilation | POSTED | https://valleypawnworkspace.slack.com/archives/C0B3R9B3S8H/p1788640289949109 — 23/31 days (74%), 20 matched / 3 flagged, $72,900 sent |
| #pawn-walks | skipped-gate | 14 reporting days in channel (8/1, 8/10, 8/12, 8/13, 8/15, 8/20, 8/21, 8/22, 8/24, 8/25, 8/26, 8/27, 8/28, 8/31) = 54% of 26 Mon–Sat days, under the 60% gate. The live test counted 16 from the daily JSON files; the task spec is channel-posts-only, so the gate is applied to what was actually posted. |
| #google-reviews | skipped-duplicate | posted 15:39 |
| #social-media | skipped-duplicate | posted 15:40 |
| #email-campiagns | skipped-duplicate | posted 15:40 |
| #website | POSTED | https://valleypawnworkspace.slack.com/archives/C0ASE9C0GQ0/p1788640296444319 — 3 weekly analytics posts (Aug 3, 17, 24 weeks; Aug 10 week missing), 2 health audits, daily shop counts |
| #ai-marketing | skipped-duplicate | posted 15:42 |
| #ebay-performance | skipped-duplicate | posted 15:42 |
| #blog-posts | skipped-duplicate | posted 15:42 |

Posted: 2 · Skipped-duplicate: 11 · Skipped-gate: 2.

Notes: the three classifier-blocked drafts from the live test were not sent by Joshua before this run; two of them (funds, website) are now posted by the task itself; pawn-walks fails the channel-only gate (the daily pawn-walk poster missed 12 of 26 expected days in August — 8/3–8/9 and 8/17–8/19 have no post at all; that is a producer gap for fleet-guardian, not a recap issue). Next real run: 2026-10-01 10:30 for September.

---

# Scheduled run — monthly-eom-recap — 2026-09-05 (second invocation, later same day)

Target month: August 2026. Slack connector only. Duplicate guard: a workspace search for "Month in Review" + "August 2026" posted since 9/4 returned all 13 eligible channels already carrying the August post (11 from the 15:35 live test, #daily-funds-reconcilation and #website from the ~16:30 run). Nothing posted.

| Channel | Result |
|---|---|
| #loan-review, #layaway-review, #aged-inventory-review, #timekeeping-summary, #weekly-returns-summary, #google-reviews, #social-media, #email-campiagns, #ai-marketing, #ebay-performance, #blog-posts | skipped-duplicate (15:37–15:42) |
| #daily-funds-reconcilation, #website | skipped-duplicate (16:31) |
| #first-payment-default | skipped-gate (unchanged from the 16:30 run — no complete August week) |
| #pawn-walks | skipped-gate (unchanged — 14/26 days, 54%) |

Posted: 0 · Skipped-duplicate: 13 · Skipped-gate: 2. August history is closed, so the two gate results cannot change; no re-count performed. Next real run: 2026-10-01 10:30 for September.
