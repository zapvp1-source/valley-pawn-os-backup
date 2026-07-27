# 2026-05-11 Daily Funds Verification

**Status: PARTIAL — Slack ledger complete; Bravo verification could not run (Parallels access dialog timed out, user not present)**

---

## Slack ledger — funds sent today (2026-05-11)

| Store | Requester | Amount(s) Sent | Send Time(s) | Notes |
|---|---|---|---|---|
| CUL (Pepper) | Sandi Cole | $2,000 | 14:38 EDT | First attempt "didn't go through" at 14:37; Joshua confirmed it loaded and sent 2k at 14:38. Sandi replied "TY!" |
| LEX | — | $0 | — | No messages today. No funds sent. |
| WAY (Boro) | Chadd / Martin D. | $2,000 + $4,000 + $2,000 = **$8,000** | 10:30, 13:46, 14:20 EDT | Three separate sends. 10:30 ($2k AM ops cash), 13:46 ($4k to fund a gold/silver buy after Martin/Preston phone call), 14:20 ($2k — "Set. 2k. Go get em"). At 17:36 Chadd asked for cash tomorrow — that's a future request, not a cancellation. |
| ROA | — | $0 | — | No funds requested or sent today (only chatter about cameras being down). |
| HAR | Andrew Clark | $2,000 + $2,000 = **$4,000** | 09:54, 14:49 EDT | Two sends. AM ops cash at 09:54 and a second top-up at 14:49. |

**Total sent today across all stores: $14,000**

### Cancellations / non-events
- None observed. The WAY 17:36 "out of cash again, please for tomorrow" is a request for the next business day, not a cancellation of any of today's sends.

---

## Bravo Till Register Journal verification

**Could not run.** The `request_access` call for Parallels Desktop timed out after 180s. Because this is a scheduled task and the user was not present to approve the computer-use dialog, the Bravo cycle (CUL → HAR → LEX → ROA → WAY) was not executed.

### What still needs to happen
For each of the three stores that received money today (CUL, WAY, HAR), open Bravo Till Register Journal → today's date → earliest employee-opened till → and confirm the following entries posted:

- **CUL**: One funds entry totaling $2,000 (around/after 14:38 EDT)
- **WAY**: Funds entries totaling $8,000 (around/after 10:30, 13:46, and 14:20 EDT) — likely 3 separate entries
- **HAR**: Funds entries totaling $4,000 (around/after 09:54 and 14:49 EDT) — likely 2 separate entries

LEX and ROA do not need verification today (no funds sent).

### Open question still pending from 2026-05-09 run
On 2026-05-09 the WAY $1k send at 12:13 PM could not be located as a "PAID IN" transaction. Transaction types observed in the Till Register Journal were SALE / LOAN / BUY / SALE PICKUP / EXTEND LOAN / LAYAWAY. Joshua needs to confirm:
1. What transaction type does a funds-in entry show as in the Till Register Journal?
2. If it's not in Till Register Journal, are funds tracked in Disbursement Journal or Deposits and Paid Outs Spreadsheet instead?

Until this is answered, even when Bravo access works, reconciliation is unreliable.

---

## Recommended next step
Joshua opens Parallels + Bravo, then re-runs this task from chat so the access dialog can be approved interactively. Alternatively, Joshua can manually verify the three stores above using the figures in the Slack ledger table.
