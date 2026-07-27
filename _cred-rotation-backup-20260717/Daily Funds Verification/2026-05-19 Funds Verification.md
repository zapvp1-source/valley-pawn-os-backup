# Daily Funds Verification — 2026-05-19

**Bottom line:** 4 of 5 stores matched. CUL could not be verified (pipeline UIA error — Preview did not render within 30s on the Bravo Reports screen).

| Store | Expected (Slack) | Actual (Bravo Safe Register) | Status |
|---|---:|---:|---|
| CUL | $2,000 | — | ❓ Could not verify |
| HAR | $2,000 | $2,000 | ✓ Matched |
| LEX | $2,000 | $2,000 | ✓ Matched |
| ROA | $0 | $0 | ✓ Matched |
| WAY | $2,000 | $2,000 | ✓ Matched |

## Slack ledger

- **CUL** (#pepper-funds): Sandi requested funds ("down to $287"); Joshua replied "Sent 2k" at 13:51. Net expected = $2,000.
- **HAR** (#harrisonburg-funds): Walker asked for 2k at 09:23; Joshua "Sent 2k" at 09:24. Later Joshua "sent 2k" at 16:45; Preston said "2k not needed now" at 16:55; Joshua "pulled back 2k" at 17:24. Net expected = $2,000.
- **LEX** (#lex-funds): Uriah needed 2k at 09:30; Joshua "sent 2k" at 09:48. Net expected = $2,000.
- **ROA** (#roanoke-funds): No activity. Net expected = $0.
- **WAY** (#boro-funds): Chadd needed 2k at 09:39; Joshua "sent 2k" at 09:48. Net expected = $2,000.

## Bravo Safe Register Journal — TENDER TRANSFER from BANK

- **HAR** — VA500050927 @ 11:27 AM (WTAPLEY): BANK → SAFE, $2,000 Cash.
- **LEX** — VA100107866 @ 10:14 AM (UTIGLAO): BANK → SAFE, $2,000 Cash.
- **ROA** — No BANK→SAFE transfer rows (only SAFE OPEN-BALANCE).
- **WAY** — VAP00070702 @ 10:54 AM (CHADD): BANK → SAFE, $2,000 Cash.

## Notes

- CUL pipeline cell failed with "UIA click sequence failed: Preview did not render within 30s (Export Document button never appeared)." The watcher had also been restarting when this run kicked off, so the CUL retry may need to be manual or wait for tomorrow's run.
- Trigger ID: `daily-funds-verification-2026-05-19T18-08-00`. Pipeline finished at 18:28:56 with status `partial` (4 success / 1 error).
