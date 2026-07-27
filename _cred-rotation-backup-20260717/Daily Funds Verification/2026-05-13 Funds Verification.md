# Daily Funds Verification — 2026-05-13

**Bottom line:** 4 of 5 stores matched. **ROA has a \$2,000 discrepancy** — funds sent but not recorded in Bravo.

## Reconciliation

| Store | Sent (Slack) | In Bravo (BANK→SAFE) | Result |
|---|---|---|---|
| CUL (Pepper) | \$2,000 | \$2,000 (VP400060128, 10:29 AM, SANDI) | ✓ Matched |
| HAR | \$0 | \$0 | ✓ Matched |
| LEX | \$0 | \$0 | ✓ Matched |
| ROA | \$2,000 | — (no data) | ⚠ Discrepancy |
| WAY (Boro) | \$0 | \$0 | ✓ Matched |

**Total sent:** \$4,000 | **Total verified:** \$2,000 | **Unverified:** \$2,000

## Slack ledger (today)

- CUL (#pepper-funds): Joshua "Sent 2k" @ 09:17
- ROA (#roanoke-funds): Joshua "Sent 2k" @ 09:17
- HAR, LEX, WAY: no activity

## Bravo result

Trigger: daily-funds-verification-2026-05-13T21-01-24 (success — all 5 cells)

- CUL CSV had the BANK→SAFE leg recorded by SANDI at 10:29 AM for \$2,000.00 — matches the Slack send.
- HAR / LEX / WAY had no safe-register activity today, consistent with zero funds expected.
- ROA returned 'No data returned for current report configuration' — there is no Safe Register Journal entry for ROA on 2026-05-13. The \$2,000 Joshua sent has *not* been entered.

## Action needed

Contact Roanoke and confirm the \$2,000 was received and entered into Bravo. If it hasn't been entered yet, they need to record the BANK→SAFE TENDER TRANSFER today.

## Pipeline note

Required 4 trigger runs — first 3 failed with 'Bravo window not found/ready within 30s' on all 5 stores. Watcher restarted at ~19:48; first post-restart trigger also failed. Final trigger at 21:01 succeeded after Joshua brought Bravo back into focus. The watcher requires the active Bravo window to be in a state where title contains 'VALLEY PAWN - <STORE>'.

