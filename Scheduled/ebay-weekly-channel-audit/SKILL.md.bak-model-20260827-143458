---
name: ebay-weekly-channel-audit
description: Weekly read-only eBay channel audit (sales, fees, listing quality, reputation) across all 5 Valley Pawn stores — feeds Slack #ebay-performance and the weekly/monthly summary rollups.
---

Run Valley Pawn's weekly eBay channel audit. This is READ-ONLY — never revise, end, or otherwise
write to a live eBay listing or setting from this task. Its job is measurement and trend-tracking,
not remediation. Load `ebay-context` and `valley-pawn-context` first if available.

## Background
A full one-off audit was done 2026-08-22 (`Projects/eBay/eBay_Channel_Audit_2026-08-22.md`, data in
`Projects/eBay/audit_2026-08-22/`). This task repeats that methodology every Monday so the numbers
become a trend line instead of a one-time snapshot, and so weekly/monthly summary tasks (e.g.
`compile-monthly-minutes`) have a current, dated source to pull from. There is also a published,
Joshua-facing artifact ("eBay Channel Pulse") that must be refreshed every run — see step 6 below.
Its URL is saved in `Projects/eBay/EBAY_DASHBOARD_ARTIFACT.md` — read that file for the exact URL
and refresh instructions before step 6.

Credentials: `~/ebay_weekly_rankings.py` loads `STORES` (5 store OAuth tokens), `APP_ID`, `DEV_ID`,
`CERT_ID`, `SLACK_WEBHOOK` from `~/.vp_secrets/ebay_store_tokens.py` (migrated 2026-08-22). `exec()`
that file to get `STORES` for the Trading API, same pattern the existing eBay automations use.

## CRITICAL SAFETY RULE (from the 2026-08-22 incident)
Never `exec()`, `import`, or otherwise run any `~/ebay_*.py` script to "verify" it — those scripts
are operational with no `__main__` guard and running one performs live eBay writes. If you need to
check a script's syntax, use `py_compile` only. This task should only ever READ via the Trading API
(GetMyeBaySelling / GetSellerList / GetSellerTransactions / GetAccount / GetItem / GetMyMessages /
GetFeedback / GetBestOffers) — never ReviseFixedPriceItem, EndFixedPriceItem, or similar.

## What to pull (all 5 stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke)
1. Active listings (GetMyeBaySelling or GetSellerList) — count, total listed value, aging buckets
   (0-30/31-60/61-90/91-180/181-365/365+ days live), and for each: Best Offer enabled, return policy
   (accepted/window/who-pays-shipping), dispatch/handling time, photo count, item-specifics count.
   NOTE: GetSellerList under-reports item specifics/description — if you need that field, verify a
   sample via GetItem directly rather than trusting GetSellerList (this bit the 2026-08-22 audit).
2. Sold transactions, trailing 90 days (GetSellerTransactions, chunked into <=30-day windows per
   eBay's API limit) — units, revenue, days-to-sell, price-band breakdown.
3. Fees, trailing 90 days (GetAccount, BetweenSpecifiedDates, chunked <=30 days) — Final Value Fee,
   Promoted Listings fee, insertion, international, return-shipping, other. Fee % of revenue.
4. Store subscription level (GetStore) and Top-Rated-Plus eligibility (dispatch time + return window
   + who pays return shipping vs eBay's current TRP requirements).
5. Buyer messages (GetMyMessages, 60-day window) — total, unread, and unread count in
   return/refund and case/dispute categories specifically.
6. Feedback (GetFeedback) — score, 1/6/12-month positive %, and full text of any negative/neutral in
   the window, with whether a seller response exists.
7. Open Best Offers (GetBestOffers, status Active) — count and whether any are approaching
   expiration unanswered.
8. Cross-reference `~/ebay_markdown_state.json` for items approaching or at the 3-cut (30%-off) cap
   with no further scheduled action — flag these explicitly, they are the recurring "items need a
   terminal decision" problem from the 2026-08-22 audit.

## Trend comparison
Look for the most recent prior run's data under `Projects/eBay/audit_weekly/` (dated subfolders,
newest first). If one exists, compute week-over-week deltas for: active listings, listed value,
7-day orders/revenue, fee % of revenue, aged->90d value, unread messages, open negative/neutral
feedback count, TRP-eligible listing count. If none exists (first run), note that and use
`Projects/eBay/eBay_Channel_Audit_2026-08-22.md` as the written baseline instead.

## Output
1. Save raw pulled data + a computed summary as JSON to
   `Projects/eBay/audit_weekly/YYYY-MM-DD/` (use the run date).
2. Write a concise dated markdown summary to the same folder: channel totals, per-store table,
   week-over-week deltas (or "first run" baseline note), and a short flagged-items list (anything
   newly broken: a store dropping out of Top Rated, late-shipment rate crossing 3%, markdown items
   hitting the 30% cap with no next step, new unanswered negative/neutral feedback, Promoted
   Listings spend still at $0 for a store, etc.). Do not re-derive the full original audit's static
   findings every week — only report what's NEW or CHANGED since last run, plus the headline totals.
3. Post the summary (headline numbers + flagged items + link/path to the full file) to Slack
   channel `#ebay-performance`.
4. Append a short dated entry to `Projects/Valley Pawn OS/CHANGELOG.md` (top of file, newest-first)
   summarizing what changed this week — this is what `compile-monthly-minutes` and other
   summarizers read.
5. If anything actionable and clearly Claude-executable surfaces (e.g. a new negative feedback with
   no reply, a listing that dropped to no-returns), do NOT fix it in this task — log it to
   `Projects/Life OS/OPEN_ITEMS_REGISTER.md` per the enterprise-map Rule 14 for a future session or
   the relevant remediation task to pick up. This task stays read-only end to end.
6. **Refresh the published "eBay Channel Pulse" artifact.** Read
   `Projects/eBay/EBAY_DASHBOARD_ARTIFACT.md` for its URL. Rebuild the dashboard HTML (single file,
   dark/light theme aware, favicon 📦, title "eBay Channel Pulse") with this week's numbers: the 5
   summary cards at top, the "what matters most, ranked by money" findings list (update ranks/impact
   figures to reflect what actually changed this week — do not just restate the 8/22 baseline
   forever), the per-store table, and the action tracker (mark items done/in-progress/needs-Joshua
   based on what you can verify actually happened, not what was merely attempted). Publish via the
   Artifact tool passing `url` set to the URL from EBAY_DASHBOARD_ARTIFACT.md so it updates in place
   — do NOT create a new artifact. This is the primary way Joshua reads this report; treat step 6 as
   mandatory, not optional, on every run.

## On failure
If any store's API calls fail or auth has expired, note it in the Slack post, the changelog entry,
AND the dashboard artifact (don't silently present stale or partial data as current) rather than
silently skipping that store's numbers — partial data must be labeled as partial, never presented as
a full channel picture (Rule 12, no diagnosis from metadata / no silent gaps).

Keep the weekly Slack post shorter than the original one-off audit — this is a pulse check that gets
more useful over time as the trend line builds, not a repeat of the full report every week. The
dashboard artifact can carry more detail than the Slack post since Joshua reads it at his own pace.