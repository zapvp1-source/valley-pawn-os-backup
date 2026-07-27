# Daily Funds Verification — 2026-05-12

Run completed manually at 6:20 PM ET via the Bravo Data Extraction pipeline. The scheduled 6 PM cron agent got stuck on a sandbox write (Write tool can't reach the pipeline folder); fix has been deployed for tomorrow.

## Bottom line

| Store | Expected | Found (BANK to SAFE Cash) | Status |
|---|---|---|---|
| CUL | \$0 | \$0 | Matched |
| HAR | \$2,000 | \$2,000 at 3:55 PM by CCLARK | Matched |
| LEX | \$1,000 | \$1,000 at 11:25 AM by UTIGLAO | Matched |
| ROA | \$0 | \$0 | Matched |
| WAY | \$2,000 | \$2,000 at 10:02 AM by MDOWDEN@CUL | Matched |

Matched: 5, Discrepancy: 0, Could not verify: 0

## Slack ledger (today)

- CUL (#pepper-funds): Sandi asked for \$1k at 5:12 PM. No 'sent' reply.
- HAR (#harrisonburg-funds): Andrew requested 3:24 PM, Joshua sent 2k at 3:35 PM.
- LEX (#lex-funds): Uriah requested 10:14 AM, Joshua sent 1k at 11:03 AM.
- ROA (#roanoke-funds): Benjie low on COH at 5:53 PM. No send.
- WAY (#boro-funds): Chadd requested 9:02 AM, Joshua sent 2k at 9:14 AM.

## Pipeline triggers used

- daily-funds-recovery-2026-05-12T18-13-00 (4 stores, partial success)
- funds-har-only-2026-05-12T18-19-00 (HAR catch-up)

## Note

HAR has a second \$1,000 BANK to SAFE at 6:03 PM by CCLARK that wasn't in Slack — likely internal cash management, not from Joshua. Captured for awareness, doesn't affect the \$2k match.

## Scheduled-run confirmation (2026-05-13)

The 6 PM cron task re-ran successfully after the Bravo Data Extraction cowork-directory fix.

- Trigger dropped: `daily-funds-verification-2026-05-12T18-07-19.json`
- Watcher was busy at run time with `monday-bravo-combined-2026-05-13T16-49-00`, so the scheduled run reused the existing same-day CSVs from 2026-05-12 23:09–23:13 (full EOD data — 5/12 is closed, identical to a fresh re-pull).
- Independently re-parsed all 5 store CSVs. Conclusions are unchanged from the 6:20 PM manual run.

| Store | Expected (Slack) | Found (Bravo BANK→SAFE Cash) | Status |
|---|---|---|---|
| CUL | \$0 | \$0 | ✓ Matched |
| HAR | \$2,000 | \$2,000 @ 3:55 PM CCLARK (+\$1,000 @ 6:03 PM CCLARK noted, not from Slack) | ✓ Matched |
| LEX | \$1,000 | \$1,000 @ 11:25 AM UTIGLAO | ✓ Matched |
| ROA | \$0 | \$0 | ✓ Matched |
| WAY | \$2,000 | \$2,000 @ 10:02 AM MDOWDEN@CUL | ✓ Matched |

