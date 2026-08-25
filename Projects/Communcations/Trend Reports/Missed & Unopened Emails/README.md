# Missed & Unopened Emails — Trend Log

Companion report to `../Missed Calls & Voicemails/` — same shape, same visual language,
covering the email channel instead of the phone channel.

**Data store:** `daily_log.csv`
**Report:** `report.html` (regenerated daily — open in a browser)
**Generator:** `generate_report.py`

## Schema (`daily_log.csv`)

One row per store per day.

| column | meaning |
|---|---|
| `date` | `YYYY-MM-DD`, the day the emails arrived |
| `store` | Culpeper / Harrisonburg / Waynesboro / Lexington / Roanoke |
| `candidates` | inbound emails that landed in that store's Apple Mail INBOX that day |
| `resolved` | of those, how many were opened the same day (proxy for "handled" — the email equivalent of a same-day callback in the calls report) |
| `unresolved` | `candidates - resolved` — still sitting unopened as of the ~6:00 PM end-of-day sweep |
| `opened_pct` | `resolved / candidates * 100`, rounded to 1 decimal |

## Known limitation (read before trusting a spike)

The 5 store INBOXes currently carry a large backlog of eBay/vendor notification mail —
see `Valley Pawn OS/CHANGELOG.md` 2026-08-22/23/24 and the `store-mail-archive-sweep`
scheduled task, which is fighting that backlog down. This report counts only messages
**received that calendar day**, not the standing backlog, so it should track real daily
inbound volume reasonably well even while the backlog is being drained — but a day where
the archive sweep is behind schedule can still show noise mixed in with genuine customer/
vendor mail. No sender filtering is applied in v1. If `opened_pct` looks structurally low
across all stores (not just one bad day), check whether the noise ratio has changed before
treating it as a staffing/response problem.

## How this gets updated

The `daily-unopened-email-eval` scheduled task (runs ~6:00 PM daily, after the
`zoom-voicemail-eod-review` calls sweep at 5:45 PM) reads each of the 5 store INBOXes via
Apple Mail (osascript — same account list as `store-mail-archive-sweep`), counts
today's arrivals and how many are still unread, appends one row per store to
`daily_log.csv`, then re-runs `generate_report.py` to refresh `report.html`. It also
posts a one-line summary to Slack **#emails-missed** (`C0BNN60347M`) — the email-channel
counterpart to `#voicemails-calls-missed`, which the calls report posts to. Falls back to
a DM to Joshua only if the channel post fails. This is additive — nothing else touches
this folder.

## How the daily count is taken

For each store account, in order (culpeper, waynesboro, lexington, harrisonburg, roanoke),
a separate osascript call walks the INBOX from message 1 (newest first) until it hits a
message received before today, counting how many of those are still unread. This mirrors
the proven-safe reference-based, one-account-per-call technique from
`store-mail-archive-sweep` (never materializes the full message list, which is what times
out on the two largest inboxes).

## History

- 2026-08-24: created (per Joshua's request for a daily eval of unopened/missed emails,
  same shape as the existing missed-calls report). First real row lands from today's
  ~6:00 PM run.
