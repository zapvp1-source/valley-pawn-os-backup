# Daily Funds Verification — 2026-05-22

**Status:** ⚠️ OPERATIONAL FAILURE — Bravo window not ready in VM. Could not pull Safe Register Journal for any store.

**Trigger ID:** `daily-funds-verification-2026-05-22T18-04-54`

## Slack ledger (expected funds sent today)

| Store | Net Expected | Detail |
|---|---|---|
| CUL (Pepper) | $0 | No activity |
| HAR (Harrisonburg) | $1,000 | Andrew Clark requested 1k ops cash 17:01; Joshua "Sent 1k" 17:10 |
| LEX (Lexington) | $0 | No activity |
| ROA (Roanoke) | $1,200 | Cristofer requested $1,200 ops cash 11:04; Joshua "Sent 1200" 11:04 |
| WAY (Boro/Waynesboro) | $4,000 | Chadd requested 2k ops cash 09:09 → Joshua "2k for ops sent" 09:34; second 2k request 11:17 → Joshua "Sent 2k" 11:34 |
| **Total** | **$6,200** |  |

## Bravo verification — ALL STORES ❓ Could not verify

All 5 Safe Register Journal cells errored:

- error: `Bravo window not found/ready within 30s`
- duration_ms: ~30,000 each
- output_path: (empty)

The watcher produced the result JSON, but the Bravo POS app in the Windows VM was not in a usable state when each store was attempted.

## Action needed

Bravo needs to be open / brought to the foreground in the Parallels VM. Once that's done, drop a manual trigger (or re-run the daily-funds-verification scheduled task) to retry.

Net expected verification: **$6,200 across HAR, ROA, WAY**.
