## 2026-08-23 (eBay remediation batch — Best Offer, returns, feedback replies, markdown terminal action, credentials finished)

- **Verified the overnight remediation.** A detached process (`/tmp/vp_ebay_fix.py`, started
  2026-08-22 11:48 PM, not started by this session) applied the audit's Best Offer / returns fixes.
  Confirmed against `Projects/eBay/eBay_Channel_Audit_2026-08-22.md`'s targets: **331 of 340 items
  fixed and live-verified** — Culpeper Best Offer 193/193 ON (auto-accept 90% / auto-decline 75%),
  Roanoke 14→30-day returns 95/103, no-returns→30-day 44/45. Live-sampled 24 items via `GetItem`,
  24/24 correct. Ran the remaining 9 (8 Roanoke returns + 1 no-returns) manually — all 9 blocked by
  eBay with "return policy cannot be changed while a Best Offer is pending." The existing
  `ebay-return-policy-retry` one-shot task (8/26, 9 AM) will pick these up once those offers resolve.
- **Replied to the 3 open negative/neutral feedbacks** from the audit (Harrisonburg, Lexington,
  Roanoke) via `RespondToFeedback`. Verified live — `FeedbackResponse` field now carries the reply
  text on all 3. Zero unanswered negatives/neutrals remaining from the audit window.
- **Built the markdown terminal action** the audit flagged as missing (`ebay_markdown_engine.py`
  caps at 30% off after 3 cuts with nothing scheduled next). New additive companion script
  `Projects/eBay/ebay_markdown_terminal.py` — Stage 1 flags an item hitting the 30% floor unsold
  (Slack post, 14-day clock, no eBay write); Stage 2 ends the listing if the grace period expires
  with no intervention, and flags it for a Bravo-side decision. Registered as a new weekly scheduled
  task `ebay-markdown-terminal-weekly` (Mondays 12:15 PM ET) so it's live before the first real
  target hits (2026-09-01 monthly markdown run — dry-run today confirmed 0 items currently at cap,
  as expected).
- **Finished the credentials sweep correctly this time.** The remaining 18 `~/ebay_*.py` scripts
  still held plaintext `APP_ID`/`DEV_ID`/`CERT_ID`/webhook literals after last night's incident
  rollback. Redid the sweep with **compile-only verification** (`py_compile`, never `exec()`) —
  all 18 migrated to load from `~/.vp_secrets/ebay_store_tokens.py`, zero residual literals, 3
  launchd-critical scripts (`ebay_daily_listings`, `ebay_efficiency_weekly`, `ebay_markdown_engine`)
  confirmed compiling with credentials resolving. No live eBay calls made during this pass.
- **Built (not auto-applied) an item-specifics fill queue.** 155 active listings ≥$100 with fewer
  than 5 item specifics ($66,957 total value), ranked by price, saved to
  `Projects/eBay/audit_2026-08-22/SPECIFICS_FILL_QUEUE.md`. Deliberately NOT auto-filled — writing
  item specifics from title text alone risks repeating the exact failure mode from last night's
  incident (fabricating an unverified fact). Handed to the existing `ebay-weekly-quality-fix` /
  `ebay-title-photo-accuracy-audit` process, which already verifies against photos before writing.
- **Remaining from the audit:** the eBay OAuth re-authorization (Joshua only), Promoted Listings ad
  budget, 1-day-handling/free-returns ops policy, and the Culpeper sub-$50 intake floor.
