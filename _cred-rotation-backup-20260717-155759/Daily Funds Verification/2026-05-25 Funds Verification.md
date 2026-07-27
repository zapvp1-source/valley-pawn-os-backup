# Daily Funds Verification — 2026-05-25

**Status:** ❓ Could not verify — Bravo extraction pipeline failed on all 5 stores

## Slack Ledger (Expected)

| Store | Channel | Sends | Net Expected |
|---|---|---|---|
| CUL | #pepper-funds | none | $0 |
| LEX | #lex-funds | none | $0 |
| WAY | #boro-funds | $1k (09:38), $1k (16:06) | $2,000 |
| ROA | #roanoke-funds | $1k (15:22) | $1,000 |
| HAR | #harrisonburg-funds | $2k (11:46) | $2,000 |

**Total expected:** $5,000

## Bravo Extraction Result

Trigger: `daily-funds-verification-2026-05-25T18-04-00`
Status: **partial** (all 5 cells errored — same root cause)

| Store | Status | Error |
|---|---|---|
| CUL | error | Bravo window not found/ready within 30s |
| HAR | error | Bravo window not found/ready within 30s |
| LEX | error | Bravo window not found/ready within 30s |
| ROA | error | Bravo window not found/ready within 30s |
| WAY | error | Bravo window not found/ready within 30s |

## Reconciliation

| Store | Expected | Actual | Result |
|---|---|---|---|
| CUL | $0 | — | ❓ Could not verify |
| HAR | $2,000 | — | ❓ Could not verify |
| LEX | $0 | — | ❓ Could not verify |
| ROA | $1,000 | — | ❓ Could not verify |
| WAY | $2,000 | — | ❓ Could not verify |

## Notes

All 5 cells failed with the same error pattern — Bravo POS appears to be stuck pre-login on the Windows VM (ClickOnce relaunch issue). Joshua needs to bring Bravo to a logged-in state on the VM so the watcher can drive it. Once Bravo is up, this verification can be re-run from the trigger folder.
