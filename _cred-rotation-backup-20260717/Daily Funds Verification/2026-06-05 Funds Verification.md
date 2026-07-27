# Daily Funds Verification — 2026-06-05

**Bottom line:** Could not verify — Bravo pipeline returned EnsureStore failed for all 5 cells on both the initial run and the retry. No Bravo readback available.

## Reconciliation

| Store | Channel | Requested | Joshua Sent | Bravo Safe (BANK→SAFE) | Status |
|---|---|---|---|---|---|
| CUL | #pepper-funds | — (blank msg from Rob) | $0 | — | Could not verify |
| LEX | #lex-funds | — | $0 | — | Could not verify |
| WAY | #boro-funds | Chadd: 2k (ops cash) | $2,000 | — | Could not verify |
| ROA | #roanoke-funds | Cristofer: 1.5k (ops cash) | $1,500 | — | Could not verify |
| HAR | #harrisonburg-funds | — | $0 | — | Could not verify |

**Total sent today (per Slack):** $3,500

## Slack ledger

- **#pepper-funds (CUL):** Rob posted at 12:45:19 EDT — message body was blank. No funds request, no send.
- **#lex-funds (LEX):** No activity.
- **#boro-funds (WAY):** Chadd 10:12 — "me and andrew took our money from drawer we didnt need to withdraw from account." Chadd 16:28 — "Ops cash, need 2k." Joshua 16:28 — "Sent 2k."
- **#roanoke-funds (ROA):** Cristofer 10:05 — "Ops need cash 1.5k." Joshua 10:22 — "Sent 1500."
- **#harrisonburg-funds (HAR):** No activity.

## Pipeline status

- Initial trigger: `daily-funds-verification-2026-06-05T18-04-30` → finished 18:09:31 → all 5 cells `EnsureStore failed`.
- Waited 180s.
- Retry trigger: `daily-funds-verification-2026-06-05T18-13-25-retry` → finished 18:18:12 → all 5 cells `EnsureStore failed` again.

Pattern (all 5 cells fail on both attempts) is consistent with Bravo being stuck pre-login on the Windows VM — ClickOnce relaunch is unreliable in that state. Watcher restart on the VM is the standard fix.

## Notifications

- ✅ Posted to #daily-funds-reconcilation (C0B3R9B3S8H)
- ✅ DM sent to Joshua (U03BB52MDSA)

