# Missed Calls & Voicemails — Trend Log

**Data store:** `daily_log.csv`
**Report:** `report.html` (regenerated daily — open in a browser)
**Generator:** `generate_report.py`

## Schema (`daily_log.csv`)

One row per store per day.

| column | meaning |
|---|---|
| `date` | `YYYY-MM-DD`, the day the calls happened |
| `store` | Harrisonburg / Waynesboro / Lexington (Culpeper, Roanoke will appear once their Zoom Phone lines go live) |
| `candidates` | total missed-call/voicemail instances that day for that store (any inbound row not Answered) |
| `resolved` | of those, how many got a same-day callback (staff outbound Connected) or customer reconnect (inbound Answered later) |
| `unresolved` | `candidates - resolved` — still outstanding as of the 5:45 PM end-of-day sweep |
| `callback_pct` | `resolved / candidates * 100`, rounded to 1 decimal |

## How this gets updated

The `zoom-voicemail-eod-review` scheduled task (runs ~5:45 PM daily) appends one row per
store to `daily_log.csv` after it finishes its resolution check, then re-runs
`generate_report.py` to refresh `report.html`. This is additive — nothing else touches
this folder.

## History

- 2026-08-13: created. Backfilled with that day's data (first day this was tracked).
