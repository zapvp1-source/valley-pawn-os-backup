# Daily Funds Verification — 2026-06-06

**Bottom line:** 4 of 5 matched. HAR is short $1,000 — bank closed Saturday, Preston could only retrieve 1k of the second 2k send from the ATM.

## Reconciliation

| Store | Sent (Slack ledger) | Entered to Safe (Bravo) | Status |
|---|---|---|---|
| CUL | $0 | $0 | ✓ Matched |
| HAR | $4,000 | $3,000 | ⚠ Discrepancy −$1,000 |
| LEX | $0 | $0 | ✓ Matched |
| ROA | $0 | $0 | ✓ Matched |
| WAY | $0 | $0 | ✓ Matched |

## Slack ledger (HAR — the only store with activity)

- 9:09 AM Walker Tapley: "Ops cash need 2k"
- 9:11 AM Joshua: Sent 2k
- 1:36 PM Preston Peters: "Ops cash, need 2k"
- 1:36 PM Joshua: Sent 2k
- 2:06 PM Preston: "Only could get 1k from ATM. Forgot bank is closed."

Net expected: $4,000.

## Bravo Safe Register Journal — HAR TENDER TRANSFER from BANK

| Txn | Time | Associate | Amount |
|---|---|---|---|
| VA500051646 | 9:40 AM | WTAPLEY | $2,000.00 |
| VA500051672 | 1:55 PM | PMONEY@LEX | $1,000.00 |

Total entered: $3,000.

## Outstanding

$1,000 from Joshua's 1:36 PM send still in transit — Preston could not retrieve the full 2k Saturday since the bank was closed and the ATM was capped at $1k. Expect this to be pulled and entered Monday 2026-06-08.

## Run notes

- Manual on-demand run via Bravo Pipeline.
- Required 3 trigger drops to get all 5 stores — the SafeRegisterJournal handler has a Preview-render race that fails intermittently (Preview / Export Document button doesn't appear within the 30s wait). Each failed cell tended to succeed on the next attempt.
- Source CSVs: `Bravo Data Extraction/output/2026-06-06_{store}_safe-register-journal.csv`
- Triggers used: `manual2` (5 stores → WAY succeeded), `retry` (4 stores → HAR + LEX succeeded), `retry2` (2 stores → CUL + ROA succeeded).
- Bravo had to be brought to Dashboard manually first — VM was sitting at the login screen with a stale 2021 session. Discovered along the way that the User Name field at the Bravo login auto-uppercases input, and computer-use's `type` was scrambling Parallels keystrokes; switched to per-character `hold_key` with explicit waits.
