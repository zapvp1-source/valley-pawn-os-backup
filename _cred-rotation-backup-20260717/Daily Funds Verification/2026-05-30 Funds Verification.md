# Daily Funds Verification — 2026-05-30

**Bottom line:** Joshua's $1,000 send is fully accounted for in Bravo, but it was split across two stores due to a DuPont ATM limit. Net funds reconcile.

## Per-store summary

| Store | Expected (Joshua sent) | Actual (Bravo BANK→SAFE) | Status |
|---|---|---|---|
| CUL (Pepper) | $0 | $0 | ✓ Matched |
| HAR (Harrisonburg) | $1,000 | $300 | ⚠ Discrepancy — see note |
| LEX (Lexington) | $0 | $0 | ✓ Matched |
| ROA (Roanoke) | $0 | $0 | ✓ Matched |
| WAY (Boro) | $0 | $700 | ⚠ Discrepancy — see note |
| **Total** | **$1,000** | **$1,000** | **✓ Net matched** |

## Slack ledger

- **#harrisonburg-funds 16:03 ET** — Joshua: "Ok. Sent 1k" (to Preston, intended for Walker @ HAR)
- **16:11** — Preston: "Sent" (forwarded to Walker via DuPont)
- **16:26** — Walker: "It only let me pull $300. I might need to adjust my limits."
- **16:28** — Preston: "Send me the $700 back and I will use for Waynesboro."
- **16:33** — Walker: "sent" ($700 returned to Preston)
- **#boro-funds 16:37** — Preston: "Grabbing the $700 for boro that Walker sent me back."

Net effect: $300 → HAR safe, $700 → WAY safe.

## Bravo Safe Register Journal hits

- **HAR** — VA500051380 @ 4:39 PM, CCLARK, TENDER TRANSFER BANK→SAFE, Cash, $300.00 ✓
- **WAY** — VAP00071206 @ 5:25 PM, PMONEY@LEX, TENDER TRANSFER BANK→SAFE, Cash, $700.00 ✓

## Reconciliation note

Per-store discrepancies stem from a mid-day manager handoff, not a Bravo entry failure. Joshua's literal "Sent 1k" was posted in #harrisonburg-funds, so the by-store math flags HAR short by $700 and WAY over by $700. The Bravo entries match the actual cash flow once the DuPont-limit / Walker-to-Preston-to-Boro handoff is considered.

All funds entered into Bravo same day. No follow-up required.
