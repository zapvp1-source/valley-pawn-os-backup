# Daily Funds Verification — 2026-05-14

**Bottom line:** 4 of 5 stores matched. WAY (Boro) is short $2,000 in Safe Register Journal vs. what was sent in Slack.

| Store | Sent (Slack) | In Bravo Safe (BANK→SAFE) | Diff | Status |
|-------|-------------:|---------------------------:|-----:|--------|
| CUL (Pepper)         | $2,000  | $2,000  | $0          | ✓ Matched |
| HAR (Harrisonburg)   | $3,000  | $3,000  | $0          | ✓ Matched |
| LEX (Lexington)      | $2,000  | $2,000  | $0          | ✓ Matched |
| ROA (Roanoke)        | $2,000  | $2,000  | $0          | ✓ Matched |
| WAY (Boro)           | $8,000  | $6,000  | **−$2,000** | ⚠ Discrepancy |
| **Totals**           | **$17,000** | **$15,000** | **−$2,000** | |

## Per-store detail

### ✓ CUL (Pepper) — $2,000 matched
- Slack: Bree at 15:08 "need funds, down to 209 in till" → Joshua "Sent 2k" 15:10
- Bravo: VP400060190 at 3:32 PM, BANK→SAFE $2,000 (BGRAYSON)

### ✓ HAR (Harrisonburg) — $3,000 matched
- Slack: Walker at 13:18 "Halp" → Joshua "Sent 2k" 13:21; Andrew at 17:14 "Need to grab 1k from the ATM!!" → Joshua "Sent 1k" 17:15
- Bravo: VA500050724 at 2:11 PM BANK→SAFE $2,000 (WTAPLEY); VA500050742 at 5:51 PM BANK→SAFE $1,000 (CCLARK)

### ✓ LEX (Lexington) — $2,000 matched
- Slack: Preston at 15:06 "Need ops cash, COH 284 in mostly small bills" → Joshua "Sent 2k" 15:10
- Bravo: VA100107766 at 3:33 PM BANK→SAFE $2,000 (PMONEY)
- Note: a second BANK→SAFE $2,000 entry (VA100107768 at 3:47 PM, UTIGLAO) was VOIDED — excluded from total

### ✓ ROA (Roanoke) — $2,000 matched
- Slack: Joshua at 10:00 "Did you grab the 2k Benjie?" → Benjie "Getting it now" 10:01
- Bravo: ROA00028484 at 11:14 AM BANK→SAFE $2,000 (BENJIE)

### ⚠ WAY (Boro) — $8,000 sent, $6,000 in safe, **−$2,000**
- Slack sends:
  - 10:00 — Joshua "sent 2k" (after Chadd asked for cash at 09:58)
  - 10:34 — Chadd: "Im at bank i can grab the 2500 with the 2k for a total of 4500" (implies the early $2k was combined with $2,500 for the Lincoln tomahawk customer buy)
  - 10:41 — Joshua "Sent 4000" (after Martin/Chadd discussed the large buy at $5k+ value, $8k MSRP)
  - 16:13 — Joshua "Sent 2k"
- Bravo BANK→SAFE entries:
  - VAP00070523 at 11:26 AM $4,000 (MDOWDEN@CUL)
  - VAP00070546 at 5:13 PM $2,000 (CHADD)
- **Likely explanation:** the early 10:00 $2k was used directly for the Lincoln tomahawk customer buy ($2,500 buy + $2,000 = $4,500 cash grab, per Chadd's 10:34 message). A buy transaction does not pass through the Safe Register Journal, which is why it doesn't appear here. **Action item:** confirm with Chadd that the $2k was applied to that buy receipt and not lost in transit.

## Sources
- Bravo Data Extraction trigger: `daily-funds-verification-2026-05-14T18-04-00`
- CSVs: `2026-05-14_{CUL,HAR,LEX,ROA,WAY}_safe-register-journal.csv` (all status=success)
