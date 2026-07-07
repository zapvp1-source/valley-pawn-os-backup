# Daily Funds Verification — 2026-06-15

_Run by funds-verification watchdog (6:45 PM ET). The 6:00 PM run errored on all 5 stores ("Bravo window not found/ready"); Bravo was sitting on the store-selector after relaunch. Watchdog relaunched Bravo + watcher, cleared the store picker via _recover_to_dashboard (landed on dashboard, store WAY), re-dropped trigger `watchdog-funds-verification-2026-06-15T18-59-59`, and all 5 cells extracted successfully._

## Reconciliation

| Store | Funds Sent (Slack) | Entered in Safe (Bravo) | Status |
|-------|--------------------|-------------------------|--------|
| CUL | $2,000 | $2,000 | Matched |
| HAR | — | $0 | Matched (no funds sent) |
| LEX | $2,000 | $0 | DISCREPANCY |
| ROA | $2,000 | $2,000 | Matched |
| WAY | — | $0 | Matched (no funds sent) |

**Result: 4 of 5 matched.**

## Discrepancy detail

**LEX — $2,000 sent, $0 in safe.** Joshua posted "Sent 2k" in #lex-funds at ~5:21 PM, but the LEX Safe Register Journal shows no cash TENDER TRANSFER from BANK today; the safe opened at $0.00 cash (SAFE OPEN-BALANCE) and closed with only card settlements. The #lex-funds thread shows form/bank-timing confusion (Preston: "No, that's old one"; Uriah: "they may be closed now"), suggesting the deposit may not have been recorded in Bravo before close. Action: confirm the LEX $2,000 is entered into the safe in Bravo.

## Evidence (cash TENDER TRANSFER from BANK, negative = into safe)

- CUL: VP400061681 2:04 PM — Cash ($2,000.00) BANK→SAFE (BGRAYSON)
- HAR: none (no funds sent)
- LEX: none — DISCREPANCY (expected $2,000)
- ROA: ROA00029655 3:38 PM — Cash ($2,000.00) BANK→SAFE (BENJIE)
- WAY: none (no funds sent)

## Notes

- Slack reconciliation table posted to #daily-funds-reconcilation (C0B3R9B3S8H) on full-success run.
- Per standing watchdog policy: no DMs sent; channel post is the notification surface.
- All 5 SRJ CSVs: output/2026-06-15_<STORE>_safe-register-journal.csv
