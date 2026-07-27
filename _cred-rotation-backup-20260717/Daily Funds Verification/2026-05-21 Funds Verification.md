# Daily Funds Verification — 2026-05-21

**Bottom line:** 4 of 5 stores reconcile cleanly. WAY shows a $2,000 gap that is explained by Chadd's note about the bank being closed (pickup deferred to tomorrow). ROA initially failed extraction but was re-verified after a watcher timeout fix — fully matched on retry.

## Summary

| Store | Slack Expected | Bravo BANK→SAFE | Status | Notes |
|---|---:|---:|---|---|
| CUL | $0 | $0 | ✓ Matched | No funds activity today |
| HAR | $0 | $0 | ✓ Matched | No funds activity today |
| LEX | $2,000 | $2,000 | ✓ Matched | Uriah requested ops cash; transferred 12:26 PM (UTIGLAO) |
| WAY | $2,000 | $0 | ⚠ Pending | Chadd asked at 17:24 if pickup could wait until morning — bank was closed. Deposit not entered today; expect it tomorrow. |
| ROA | $1,000 | $1,000 | ✓ Matched (retry) | Gold buy (14k, 20dwt). Transferred 11:59 AM (BENJIE). First extraction failed on EnsureStore timeout; re-ran after fix. |

**Totals:** Expected $5,000 / Verified $3,000 / Pending $2,000 (WAY — expected tomorrow)

## Watcher fix applied

The initial ROA failure was caused by a 10-second timeout in `lib/StoreCycle.ahk` waiting for Bravo's login/session-list screen to render after the store-row double-click. ROA's screen took ~16s today. Bumped timeout from 10000 → 20000 ms on line 205. Backup saved as `StoreCycle.ahk.bak-pre-roa-timeout-2026-05-21`. Watcher restart required to load the change — retry confirmed the fix works.

## Slack ledger

- **#pepper-funds (CUL):** No messages today.
- **#lex-funds (LEX):** Uriah at 09:43 — "Ops cash need 2k". Joshua at 11:25 — "Sent 2k".
- **#boro-funds (WAY):** Chadd at 16:22 — "Ops cash Need 2k". Joshua at 17:11 — "Sent 2k". Chadd at 17:24 — "Is it okay If I get it in the morning? Bank is closed now. So I can only get 1k. I rather just get 2k on the way in if possible."
- **#roanoke-funds (ROA):** Cristofer at 11:33 — "14k 20dwt" (gold buy). Joshua at 11:34 — "Sent 1k".
- **#harrisonburg-funds (HAR):** No messages today.

## Bravo evidence

- **CUL:** Only SAFE OPEN-BALANCE $571.50 cash. No BANK→SAFE transfer.
- **HAR:** Only SAFE OPEN-BALANCE $18.00 cash. No BANK→SAFE transfer.
- **LEX:** Txn VA100107922 at 12:26 PM — TENDER TRANSFER, Till = BANK, Cash ($2,000.00) → SAFE $2,000.00. Associate UTIGLAO.
- **WAY:** No BANK→SAFE cash transfer. Only end-of-day card transfers (TL-01 → SAFE → BANK for debit/Visa/MC/Discover).
- **ROA (after retry):** Txn ROA00028726 at 11:59 AM — TENDER TRANSFER, Till = BANK, Cash ($1,000.00) → SAFE $1,000.00. Associate BENJIE.

## Action items

- **WAY $2,000:** Confirm with Chadd tomorrow morning that the pickup happens and is entered into Bravo.
