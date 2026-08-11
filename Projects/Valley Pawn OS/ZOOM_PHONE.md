# Zoom Phone — Store Lines & Extension Map

Built 2026-08-07. Reference for anything touching Zoom Phone (missed calls, voicemail, extensions).

## Account

- **Account:** Full Circle Finance Inc — Workplace Pro + Zoom Phone plan
- **Login:** jdavis@fcfpawn.com (Joshua is the Owner/Admin — can see every user's call history/voicemail
  from the admin console, not just his own)
- **Admin path:** zoom.us → left nav "Phone" → scroll sidebar to "Phone System Management" → "Users & Rooms"
  → click a user → "History" tab (has Voicemail / Call Result / Event columns and date-range + filters)
- **No Zoom Phone MCP connector exists** (checked connector registry 2026-08-07 — "Zoom for Claude" is
  meetings-only). Automation drives the admin web UI via Claude in Chrome instead.

## Extension / Line Map (live as of 2026-08-07 — 3 of 5 stores on Zoom Phone so far)

| Store | Zoom user (login) | Ext. | Number |
|---|---|---|---|
| Lexington | jdavis@fcfpawn.com (Joshua Davis, Owner) | 800 | (540) 461-8349 |
| Harrisonburg | harrisonburg@fcfpawn.com | 802 | (540) 574-4500 |
| Waynesboro | waynesboro@fcfpawn.com | 803 | (540) 221-6346 |
| Culpeper | — not yet on Zoom Phone — | — | (540) 445-5510 |
| Roanoke | — not yet on Zoom Phone — | — | (540) 562-0776 |

**Note:** Joshua's own Zoom user (ext 800) carries the Lexington store's public number — that's why every
Zoom voicemail notification email Joshua gets personally is actually a Lexington store call, not a call to
him personally. Harrisonburg and Waynesboro's voicemail notification emails go to their own store Gmail
inboxes (harrisonburg@fcfpawn.com / waynesboro@fcfpawn.com — see `store-credentials` skill), which nobody
reliably checks — this was the gap `zoom-voicemail-alert` was built to close.

Culpeper and Roanoke are expected to be added as Zoom Phone users soon ("will have them at 5 soon" per
Joshua 2026-08-07). When that happens no manual update is needed here for the automation to pick them up —
`zoom-voicemail-alert` re-reads the live Users & Rooms roster every run — but update this table for human
reference once their extensions are assigned.

## Automation

- **`zoom-voicemail-alert`** (Cowork scheduled task, SKILL.md at `~/Documents/Claude/Scheduled/zoom-voicemail-alert/`)
  — runs every 20 min, Mon–Sat 9am–7pm. Reads the live Users & Rooms roster, checks each store line's
  admin History tab (today only) for new missed-call/voicemail events, dedupes against a state file, checks
  whether the call was already returned (Step 3.5, added 2026-08-10), and posts a consolidated alert to
  Slack **#voicemails-missed-calls** so the store team knows to call the customer back. Silent when there's
  nothing new or everything was already called back. Self-heals nothing on a Zoom session logout — DMs
  Joshua instead of attempting a login, per safety policy on credential entry.
- Posts to Slack **#voicemails-missed-calls** (`C0BND1NK65V`) — Joshua created this channel 2026-08-07,
  resolving the earlier #general fallback.
- **Dedupe state:** `~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json` (moved
  here 2026-08-10 — `~/Documents/Claude/Scheduled/` is read-only in Cowork sessions, see CHANGELOG). Never
  scope a run beyond today's date range — today-only + this state file together are what prevent
  re-alerting on a prior day's calls.
- **Callback verification:** since 2026-08-10 the task cross-references each candidate missed call against
  the store's Outbound call log for that day. If the store already placed a later call to the same number
  that Connected, the row is suppressed from the alert instead of nagging about a callback that already
  happened.
