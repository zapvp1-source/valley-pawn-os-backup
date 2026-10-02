# Scheduled run — monthly-eom-recap — 2026-10-01 10:30 ET

Target month: September 2026 (2026-09-01 00:00 ET – 2026-09-30 23:59 ET). Slack connector only; source
is each channel's own posts during the month. Dry-run guard checked first (`vp_dryrun.py status` →
exit 1, not armed) — publications below are live, not test.

Duplicate guard: searched workspace for "Month in Review" + "September" (after:2026-09-28) and read
each target channel's own September history directly — no September Month in Review existed in any
of the 15 channels before this run (only each channel's August MIR, posted 2026-09-05, was present).

| Channel | Result | Note |
|---|---|---|
| #loan-review | POSTED | 3 weekly posts (9/7, 9/21, 9/28) |
| #layaway-review | POSTED | 3 weekly posts (9/7, 9/21, 9/28) |
| #aged-inventory-review | POSTED | 3 weekly posts (9/7, 9/21, 9/28) |
| #first-payment-default | skipped-gate | only 1 September post found (9/7) — gate needs ≥3 weekly |
| #timekeeping-summary | POSTED | 4 weekly posts (wk Aug31, Sep7, Sep14, Sep21) |
| #weekly-returns-summary | POSTED | 3 weekly posts (wk Aug31, Sep14, Sep21); week of Sep7-14 missing |
| #daily-funds-reconcilation | POSTED | 24/30 days (80%) — 23 matched clean, 1 confirmation-only flag |
| #pawn-walks | skipped-gate | only 9 of ~26 expected days had real data (9/1-9/11); 9/16 onward is blank placeholder posts with no content — 35%, under the 60% gate |
| #google-reviews | POSTED | 3 weekly ranked counts (wk Aug30, Sep6, Sep20); week of Sep13-19 missing |
| #social-media | skipped-gate | only 1 "Weekly Social Recap" found (9/7); other weeks only had lane-update posts, not the recap format |
| #email-campiagns | POSTED | 3 "Email — Week of" posts (wk Sep3, Sep10, Sep21) plus uploads/health checks |
| #website | POSTED | 3+ Weekly Website Analytics posts (9/7, 9/22, 9/26-recovered) plus health audit + daily shop refreshes |
| #ai-marketing | POSTED | multiple weekly producers, each ≥3 (health check, visibility scorecard, presence audit) |
| #ebay-performance | POSTED | multiple weekly producers, each ≥4 (sales rankings, efficiency, store audit, ratings sweep) |
| #blog-posts | POSTED | 3 posts published in September (9/3, 9/7, 9/10) — full count, no completeness gate applicable (not a weekly check-in producer) |

Posted: 12 · Skipped-gate: 3 (#first-payment-default, #pawn-walks, #social-media).

Notes for next run:
- #first-payment-default's weekly producer appears to have mostly stopped posting in September (only
  one post all month) — a producer gap, not a recap issue. Worth a look by whoever owns that task.
- #pawn-walks: the daily pawn-walk post stopped carrying real content around 9/12 and has been posting
  empty placeholder messages (blank text, timestamp only) through month end — a producer gap, not a
  recap issue. Flagging for the pawn-walks task owner.
- #social-media: the "Weekly Social Recap" producer only fired once in September (9/7); the channel is
  otherwise active (Lane C/D community and engagement updates) but the recap format itself is missing
  for weeks of Sep 14, 21, 28.
- #weekly-returns-summary and #google-reviews each had one missing week (Sep 7-14 and Sep 13-19
  respectively) but still cleared the ≥3 gate.
