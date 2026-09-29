# Daily Funds Verification — 2026-09-28

**Status: COMPLETE — all 5 verified. ALL MATCHED.**

## Bottom line
$6,000.00 expected vs $6,000.00 actual across all 5 stores — every dollar sent today is in the Bravo safes. Lexington had an open $2k cash-ops request at 4:22 PM ET with no confirmed send from Joshua in the channel by the time this ran (~6:20 PM ET) — nothing to reconcile since nothing was sent, but flagged in case it's still needed.

## Step 1 — Slack ledger (today, 2026-09-28 ET)
| Store | Channel | Request(s) | Joshua's reply | Net expected |
|---|---|---|---|---|
| CUL — Culpeper | #pepper-funds | 9:43 AM "Cash ops needed $2k"; 1:35 PM re-ping (no new stated amount); 2:00 PM "Not available" (troubleshooting the PM send) | 10:20 AM "Sent 2k"; 1:53 PM "Sent 2k"; 2:04 PM Preston "Sending now" (re-confirmation of the same 1:53 PM $2k send, not a new transfer — Bravo shows only two BANK cash transfers) | $4,000.00 |
| HAR — Harrisonburg | #harrisonburg-funds | 12:18 PM "Ops cash need 2k" | 12:26 PM "sent 2k" | $2,000.00 |
| LEX — Lexington | #lex-funds | 4:22 PM "Need cash daily ops 2k" | none in channel as of run time | $0.00 (unfulfilled — see note) |
| ROA — Roanoke | #roanoke-funds | none (channel only had unrelated VoIP phone chat) | — | $0.00 |
| WAY — Waynesboro | #boro-funds | none | — | $0.00 |

Cancellations: none. **Total expected: $6,000.00.**

## Step 2 — Bravo extraction
Trigger `daily-funds-verification-2026-09-28T18-15-00` → watcher status `success` on 5/5 cells (via host queue `bravo_pull.sh`, health gate PASS before trigger).

## Step 3 — Bravo signature rows (TENDER TRANSFER · BANK · Cash · negative leg)
| Store | Txn Num | Time | From→To | Amount |
|---|---|---|---|---|
| CUL | VP400066695 | 10:48 AM | Safe→Bank (cash) | $2,000.00 |
| CUL | VP400066721 | 2:13 PM | Safe→Bank (cash) | $2,000.00 |
| HAR | VA500055969 | 12:43 PM | Safe→Bank (cash) | $2,000.00 |
| LEX | — | — | (no cash transfer) | $0.00 |
| ROA | — | — | (no cash transfer) | $0.00 |
| WAY | — | — | (no cash transfer) | $0.00 |

## Step 5 — Reconciliation
| Store | Net expected (Slack) | Net actual (Bravo) | Status |
|---|---|---|---|
| CUL — Culpeper | $4,000.00 | $4,000.00 | ✓ Matched |
| HAR — Harrisonburg | $2,000.00 | $2,000.00 | ✓ Matched |
| LEX — Lexington | $0.00 | $0.00 | ✓ Matched |
| ROA — Roanoke | $0.00 | $0.00 | ✓ Matched |
| WAY — Waynesboro | $0.00 | $0.00 | ✓ Matched |
| **Total** | **$6,000.00** | **$6,000.00** | **5/5 matched** |

**Slack post: made** (#daily-funds-reconcilation, https://valleypawnworkspace.slack.com/archives/C0B3R9B3S8H/p1790634075784529). Fleet publish guard checked first — dry run was off (publications live), so posting proceeded normally.

_Report generated 2026-09-28 ~18:22 ET._
