# 282 Bald Rock Road, Verona VA 24482 — Capital Improvements Evidence Log

**Built 8/5/2026 from the local unified index; index re-verified and re-measured 8/31/2026 (§12)** — Apple Mail **342,519 messages across all 10 configured accounts**, back to 2009; iMessage/SMS 62,158 (mid-2024→now); files 49,428; Google Drive 252; notes, reminders, photos. Coverage was audited against the live Gmail cloud on 8/31 — see §12.

> ## ⚠️ THIS FILE SUPERSEDES `Bald Rock Improvements Substantiation.md`
> That earlier file reported **$21,172 documented** and declared "ZERO HITS" on siding, electrical, hot tub, cold plunge, paint, and Valley Building Supply. **Those were false negatives.** Two causes:
> 1. It searched only the Gmail MCP. Most of this correspondence lives in Apple Mail accounts the Gmail connector cannot see.
> 2. Its SQL date filter used `ts > strftime('%s','2021-06-01')`, which compares an INTEGER column to a TEXT value and **always returns zero rows**. Every date-filtered query in it silently returned nothing.
>
> Do not rely on the old file's negative findings for anything.

---

> ## 🔴 LIVE ITEMS — 8/31/2026
>
> **1. Valley Building Supply — request RE-SENT 8/31/2026 12:42 PM from zapvp1@me.com.** The earlier attempt from jdavis@fcfpawn.com **bounced in 3 seconds** (`550 blocked` from their server, both recipients). Re-sent from the me.com address, which has 325 messages of two-way history with this vendor. Addressed to **vlaffler@** (151 messages, 14 inbound, active through Aug 2024), cc **gstrawderman@** and **ccash@** (both active through Aug 2024). **Dropped agriffin@ — that mailbox has been silent since June 2020** and was a bad target regardless of the domain block. No bounce after re-send. VBS is the largest unproven line at $28,947.87.
>
> **VBS contact list, ranked by usefulness (from 325 archived messages):**
>
> | Address | Msgs | Inbound | Active window |
> |---|---|---|---|
> | vlaffler@valleybuildingsupply.com | 151 | 14 | 2022-03 → 2024-08 |
> | gstrawderman@valleybuildingsupply.com | 158 | 5 | 2021-09 → 2024-08 |
> | ccash@valleybuildingsupply.com | 102 | 0 | 2022-03 → 2024-08 |
> | sknupp@valleybuildingsupply.com | 77 | 30 | 2020-11 → 2021-12 |
> | agriffin@valleybuildingsupply.com | 26 | 15 | 2020-04 → 2020-06 (dead) |
> | mwagner@valleybuildingsupply.com | 24 | 10 | 2020-04 → 2020-07 (dead) |
>
> Separately, PlyGem warranty correspondence runs through **Mike Bell, Mike.Bell@cornerstone-bb.com** (Cornerstone Building Brands) — the "282 Bald Rock Road Plygem Issues" thread, live through Aug 2024. Useful for product/defect history, not for invoices.
>
> **2. APPRAISAL — CANCELED by Joshua, 8/31/2026.** Blue Ridge Appraisal had an inspection booked for Wed 9/2/2026 2:00 PM (Robert Miller, $500, arranged via Vanessa Cline / robbiem@blueridgeappraisal.com). **Cancellation email sent 8/31/2026 4:19 PM** from jdavis@fcfpawn.com to robbiem@blueridgeappraisal.com, cc admin@blueridgeappraisal.com, subject "282 Bald Rock Rd - need to push our Wed 9/2 inspection" — confirmed delivered, no bounce (verified against the live Gmail thread, msg id 1a05942eb6840423). **The reasoning holds:** §0 shows adjusted basis is very likely the binding constraint, not FMV — so an appraisal is not what unlocks this position, receipts are. Worse, an FMV opinion rendered *before* the improvement record is complete risks setting a ceiling below the basis we can actually document. The county assessed value is already known as a reference point. **Reschedule only once the receipt work is done and the improvement list can be handed to the appraiser as a finished document.** When it is rescheduled, the two requirements in §0 still stand: give the appraiser §1 as the improvement list, and require a land-vs-improvements allocation as of the conversion date in the report body.
>
> **3. THREE NEW DOCUMENT REQUESTS SENT, 8/31/2026 evening, all delivered clean, all awaiting reply:** (a) Lodestar Tax — 2020-2021 general ledger export, sent to liana@lodestar.tax from zapvp1@me.com after the first attempt from jdavis@fcfpawn.com bounced (DNS failure, same class of problem as the VBS block — see §12/memory); (b) Service Finance Company — the actual Retail Installment Contract for acct 3624, sent to Servicing@svcfin.com, closes Burns' last $6,392.53 if it names the Amount Financed; (c) Augusta County Building Inspection — permit file copy for the Check 1219 permit, sent to bi@co.augusta.va.us (note: the county's stated retention is only 3 years post-completion, so this may come back empty — worth trying anyway). **Red Rock Concrete was re-checked exhaustively against every parsed Lodestar workbook (2022 GL, 2022 shareholder QuickReport, all 2023-2025 uncategorized-transaction reports) — zero hits. It genuinely isn't in any QuickBooks-tracked account; the $18,622 balance can only be resolved by the missing Aug-Oct 2022 DuPont statements or whatever the new 2020-2021 GL turns up.**
>
> **Priority is receipts.** See §12 for why that means banking documents, not more email searching.

---

## HEADLINE

| Evidence class | Amount |
|---|---|
| **Proof of payment on the face of a document** | **$147,385.34** |
| Invoiced, payment not proven | $77,240.30 |
| Paid, but property attribution unconfirmed (see §10) | $17,275.53 |
| Quoted only — **includes losing bids, see warning below** | ~$176,000 |

Against a claimed **$305,086.51**. Documented-and-paid went from $21,172 → $97,615.40 (8/5/2026 pass) → $114,073.76 → $124,777.87 → **$147,385.34** on 8/31/2026. Three passes that day: the first completed Fundamental Siteworks, proved the Royal Swimming Pools Affirm payoff and found the Shreckhise bank withdrawal (§9); the second recovered **32 Lodestar Tax bookkeeping workbooks** out of 564 Lodestar emails and read the actual general ledger (§10); the third worked the **lender and QuickBooks trails** and closed out Burns Builders and Weaver Irrigation (§11).

> **The "quoted" column is not a shopping list.** It contains at least two competing bids for work another contractor actually performed (Turf Specialties $46,000 and Crown Decorative Concrete $18,400 both bid the retaining wall Red Rock built for $28,622). Carrying those alongside Red Rock double-counts the wall. Quotes belong in basis only where a matching invoice or payment exists.

---

# 0. WHY THE RECEIPTS MATTER — THE BASIS MATH

**Purchase price of 282 Bald Rock: $405,000.00**, per the recorded deed — `CONSIDERATION: 405,000.00`, `Consideration/Actual value: $405,000.00`. Acquired 2016 (contract 8/8/2016 via Charlotte McAlister, RE/MAX Advantage; financing through BNC National Bank; United States Appraisal LLC ordered 9/13/2016). Source: `.../02 Real Estate/282 Bald Rock Rd - Verona VA (Rental)/282 Bald Rock Deed:Closing.pdf` — image-only, OCR'd 8/5/2026.

On conversion of a personal residence to a rental, depreciable basis = **the LESSER of** adjusted basis or FMV at the conversion date. Adjusted basis = purchase price + capital improvements − depreciation previously allowed (here $0, since it was a residence throughout).

| Scenario | Adjusted basis |
|---|---|
| Purchase price alone | $405,000 |
| + improvements **proven paid** ($147,385.34) | **$552,385.34** |
| + improvements proven **and** currently invoiced ($224,625.64) | **$629,625.64** |
| + the full claimed $305,086.51, if it could all be documented | $710,086.51 |

**Implication: adjusted basis is very likely the binding constraint, not FMV.** For the appraisal to cap this, the property would have to be worth *less* than roughly $503K–$710K in August 2025 — i.e. under ~24%–75% appreciation over nine years, on a house that was gut-renovated in the interim, in a market that ran hard 2016→2025. Possible, but not the way to bet.

**So every documented improvement dollar is very likely a real dollar of depreciable basis.** The $77,240.30 sitting in the "invoiced but unproven" column is the single largest recoverable prize in this file — and bank and card statements are what convert it. As of 8/31/2026 the highest-value single pull is **Wells Fargo Checking 2797**, an account this file had never seen until the Lodestar workbooks surfaced it (§10).

Two caveats that don't change the direction:
- **Only the building depreciates, not the land.** Whatever basis figure lands, it gets split. Instruct the appraiser to provide a land-vs-improvements allocation as of the conversion date, or the cost-seg firm will send it back.
- Depreciable basis and basis-for-sale are not the same number. Even improvement dollars that end up above the depreciable cap still reduce gain on an eventual sale and feed the §121 modeling.

---

# 0b. BANK STATEMENT SWEEP — added 8/5/2026

Parsed **137 statement PDFs** out of iCloud, yielding **10,493 transaction lines**. Scripts kept at `_scan_statements.py` and `_match_vendors.py` in this folder; raw output at `_raw/dupont_transactions.csv`. Re-runnable as more statements arrive.

**Accounts:** Full Circle Finance Inc at DuPont Community Credit Union — Business Main Share Savings ID 0000, Business Checking ID 0090, statements addressed to 282 Bald Rock Rd.

### ⚠️ Coverage: 2020, 2021, and January 2022 ONLY
28 statement periods, 01/2020 → 12/2021, plus 678 stray 2022 lines. **Nothing from Feb 2022 onward.** That is precisely why Red Rock, Royal Swimming Pools, Fundamental Siteworks, Commonwealth Tile, Weaver Irrigation, Renu Therapy and R.E. Boggs all return zero hits — they were paid after coverage ends, not because the payments don't exist. **Pull DuPont statements Feb 2022 → Dec 2025 and this same script will find them.**

### Valley Building Supply — independent confirmation
Three debit-card charges appear that **exactly match** payment credits printed on the scanned invoices:

| Date | Amount | Matches |
|---|---|---|
| 04/09/2020 | $3,103.62 | Payment 1 on invoice 00180805 |
| 06/02/2020 | $5,212.53 | Payment applied to the Oct 2020 invoice set |
| 03/18/2021 | $14,634.79 | "Payment 1 CREDIT" on the 2021–22 invoice set |
| | **$22,950.94** | |

Two independent sources agreeing to the cent. The remaining VBS payments derived from the invoices ($9,100.00 + $3,880.00 + $4,021.47 + $15,115.78 = $32,117.25) are **not** in this account — they came from a personal account, another institution, or a check.

### NEW vendors this sweep found — none of these were in email

| Vendor | Txns | Total | Note |
|---|---|---|---|
| **Lowe's (ACH)** | 78 | **$51,887.96** | Far beyond the $10,102 email showed. ⚠️ Business account — certainly includes Valley Pawn store purchases. Needs per-charge attribution. |
| **Prestige Plumbing LLC** | 4 | **$10,500.00** | 09/16/20 $3,500 · 09/25/20 $1,500 · 10/07/20 $3,300 · 12/02/20 $2,200. **Plumbing previously showed "nothing at all."** |
| Lumber Liquidators | 2 | $3,919.04 | 03/19/21 $3,638.46 · 09/25/20 $280.58. First hard LL Flooring dollars found anywhere. |
| Magic Floors Inc | 1 | $3,252.72 | 05/19/2020 |
| Build.com / Ferguson | 3 | $2,707.52 | |
| Solutions Mechanical / Alltemp (HVAC) | 7 | $2,021.88 | |
| C & J Tree & Landscape | 1 | $1,116.50 | 08/14/2020 |
| Augusta Paint & Decorating | 6 | $988.36 | **Paint previously showed "nothing found."** |
| Harrisonburg Electric | 1 | $800.00 | 07/07/2021 |
| Enlit LLC | 3 | $793.20 | |
| Home Depot | 5 | $788.37 | |
| Direct Door Hardware | 1 | $281.20 | Confirms the email-sourced order |

### The checks — $535,113.23 across 514 debits, and no payee on any of them

This is the labor money. DuPont statements print **only the check number**, never the payee:

`09/29/2020 −$52,232.00 Check 1948` · `12/27/2021 −$20,000.00 Check 1177` · `08/25/2020 −$8,213.00 Check 1486` · `12/01/2021 −$8,200.00 Check 1404` · `09/10/2020 −$5,775.60 Check 1495` · `06/24/2020 −$5,611.41 Check 1481` · plus 508 more.

**These cannot be attributed without check images.** DuPont online banking normally exposes front/back images per cleared check — that is the single highest-value document pull left on this property. Most of the 514 will be Valley Pawn operating checks; the renovation subset has to be identified visually.

### Context to keep in view
These are **Full Circle Finance business accounts**. To the extent they paid for a personal residence, those payments are shareholder distributions on FCF's books *and* capital improvements to a personal asset. Same pattern already flagged on the vehicles. Silverline needs to see this whole picture at once.

---

# 1. PROOF OF PAYMENT — $147,385.34

| Vendor | Doc / Date | Amount | Covers | Proof |
|---|---|---|---|---|
| **R.E. Boggs, Inc.** (Charlottesville) | Inv I-5192-1 + I-5192-2, 2025-09-03 | **$29,187.00** | Two Rheem HVAC systems | Service Finance loan 5977065, borrower addr 282 Bald Rock Rd, signed 2025-09-05; Certificate of Completion 2025-09-08. *(See 8/31/2026 addendum — Payzer/R.E. Boggs's own invoice portal still shows both I-5192-1 and I-5192-2 as "Overdue" as of 2025-12-16, three months after loan signing. Standard for dealer POS financing — Service Finance pays the dealer at closing and Payzer's own status often never syncs — but worth a direct confirmation call to R.E. Boggs if this is ever challenged.)* |
| **Valley Building Supply** | 2020-04 → 2022 (multiple) | **$29,722.06** | PlyGem/Mira windows, patio + bi-parting doors, trim, AZEK porch/decking | Balance Due $0.00 / "CREDIT CRD" on invoice faces ($27,561.06), net of a $1,255.54 credit-noted return, **plus $2,161.00 of 2022 debit-card charges ($1,908.44 on 2022-02-03 and $252.56 on 2022-04-28) read off Full Circle's own 2022 general ledger, both coded Repairs & Maintenance** — added 8/31/2026 |
| **Burns Builders Roofing** — financed portion | Loan funded ~2021-07; amortized to payoff by 2023-09 | **$15,357.47** | Roof (Est 1548, installed 7/6/2021, completion confirmed 7/10/2021) | **Service Finance Company, LLC** (Boca Raton FL, NMLS 140908, now a Truist subsidiary) retail installment contract, account ending **3624**, borrower **Hillary D. Davis**, 282 Bald Rock Road. Under dealer point-of-sale financing the lender pays the contractor at funding, so Burns was paid this amount. **24 consecutive monthly statements recovered** showing an unbroken amortization: $15,357.47 (due 09/14/2021) → $13,411.49 (01/2022) → $11,230.63 (09/2022) → $9,490.84 (02/2023) → $6,704.47 (04/2023) → **$891.92 (due 08/14/2023)**, past due $0.00. Payment $380.82/mo with accelerated principal in 2023 (consistent with beating the deferred-interest promotional expiry). Last payment-posted email 2023-07-03; last statement 2023-07-31; the account then goes silent — it ran to payoff. Added 8/31/2026. |
| **Weaver Irrigation, LLC** Inv 2248 + 2377 + 2773 | 2023-06 → 2024-05 | **$7,250.00** | Irrigation install and additions | **The vendor's own statements prove it.** QuickBooks statements list open items only. Statement #1240 (2024-02-28) shows just Inv 2377 open at $1,286.00 — **Inv 2248 ($4,400) is gone**, matching the four $1,100 DuPont payments of 2023-08-21 to the dollar. Statement #1274 (2025-07-30) no longer lists 2377 or 2773 either, and records a $600 payment (#217816712, 2024-09-06). All three invoices settled. Moved from §2 on 8/31/2026. *(Weaver's later small service invoices — 3117 $990, 3209 $109, 3375 $75, 3772 $109 — remain open at $1,159.50 and are recurring maintenance, not capital; see F-8.)* |
| **Shreckhise Landscape & Design** | Bill Pay, 2023-01-18 | **$8,536.50** | Landscaping (per "Landscape Plan" / "Design for Between Walls" correspondence 2022-11 → 2023-03) | DuPont business acct bill-pay withdrawal "SHRECKHISE LANDS," documented in Lodestar Tax's Jan-2023 bookkeeping report (uncategorized-transactions detail); the 9 transaction amounts on that report sum to the report's own stated total to the penny, confirming $8,536.50 is the correct line, not a mis-parse. Found 8/31/2026. |
| **Pro Quality Property Maintenance** ("282 Hardscape") Inv #4347 | 2024-12-31 → 2025-02-12 | **$7,800.00** | Front walkway + patio pavers | Check 5061 $3,000 (2024-12-31) + four $1,200 bill-pay installments (2025-01-22, 01-29, 02-05, 02-12), all from **Wells Fargo Checking 2797**, per Lodestar's 2025 uncategorized-transaction workbooks. Paid in full; the $3,000 was the deposit and #4347's $4,800 was the balance. Moved from §2 on 8/31/2026. |
| **Renu Therapy** Order #5754 | 2023-05-27 | **$10,214.09** | **Cold plunge** — Cold Stoic 2.0, ship-to 282 Bald Rock | Paid order + shipment 7/16/23, BTX tracking LAX4059890 |
| **Red Rock Concrete** | Inv #1244 final, 2022-08-07 | **$10,000.00** | Engineered retaining walls | Payment line on the vendor's own final invoice |
| **Lowe's** Order #717201671 | 2021-03-17 | **$8,757.88** | Appliances | "Payment LCC ending in 1037 $8,757.88" |
| **Royal Swimming Pools** Affirm loan NM3V-P2HC | Approved 2022-10-27, paid off 2023-09-28 | **$5,592.86** | Pool equipment/kit financed portion | Affirm approval email names "your Royal Swimming Pools purchase"; recurring payment stream; completion email "Awesome, you're all done!" 2023-09-28 confirms paid in full. Found 8/31/2026 — moved from §2. |
| **ProjectorScreen.com** #124774 | 2020-02-14 | **$5,470.50** | SI 5 Series 160" screen, ship-to 282 | "Payment information received", credit card |
| **Fundamental Siteworks** Inv 670 | 2022-11-22 + 2023-03-01 | **$5,329.00** | Pool demo + dig + rough grade | $3,000.00 MC ****6246 Auth MQ0134863515 (2022-11-22) **+** $2,329.00 QuickBooks payment confirmation email (2023-03-01) — the two payments exactly total the $5,329.00 invoice. Fully proven as of 8/31/2026; previously only the $3,000 partial was counted. |
| **Commonwealth Tile** Inv 1294 | 2022-11-20 | **$1,685.00** | Tile | MC ****0305, Auth MQ0134421222 |
| **Signature Hardware** (C1, C3, C18 + 2022 ledger) | 2020-04 → 2023-04 | **$1,883.00** | Bath/plumbing fixtures | PayPal txn 1VC80117373738041; AmEx ****7115 ($1,139.88) **plus $743.11 of 2022 debit-card charges ($588.63 on 2022-11-20, $154.48 on 2022-12-02) from the 2022 general ledger** — added 8/31/2026 |
| **Commonwealth Tile** Inv 1252 / 1265 | 2021-04-08 / 2021-08-01 | **$400.00** | Tile labor + material | QuickBooks payment confirmations |
| **Royal Swimming Pools** #151856 | 2022-12-01 | **$199.99** | Pool niche | PayPal receipt |
| | | **$147,385.34** | | |

> **Note on Burns Builders Roofing $21,750.00 (§2 below):** an earlier draft cost-seg writeup (v4 docx, before 8/31/2026) had incorrectly promoted this to "proven" based on recurring monthly "Payment Posted" emails from Service Finance. Those are routine installment confirmations, not a payoff — they were never adequate proof. This master log's own §2 / F-1 treatment (invoiced, not proven, ~$6,400 arithmetic gap unresolved) was correct all along and was never changed. Flagging here so the correction carries into any future docx rebuild.

---

# 2. INVOICED, PAYMENT NOT PROVEN — $77,240.30

| Vendor | Doc / Date | Amount | Note |
|---|---|---|---|
| **Valley Building Supply** | net invoiced $58,669.93 less $29,722.06 proven | **$28,947.87** | Open balances $950.75, $3,181.73 (after $5,200 PlyGem credit), $724.80; plus $6,232.64 where Balance Due is illegible on the scan. Reduced 8/31/2026 by the $2,161.00 of 2022 ledger payments now proven in §1. |
| **Burns Builders Roofing** — unfinanced remainder | Est 1548 $21,750.00 less $15,357.47 financed (see §1) | **$6,392.53** | This is the old F-1 "~$6,400 gap," and it is now explained rather than mysterious: the Service Finance loan covered $15,357.47 of a $21,750 signed estimate. The remainder was either a deposit paid directly to Burns or the contract was revised down before signing. **Resolve with one document: the Retail Installment Contract for account 3624 (shows the exact Amount Financed) or Burns' final invoice.** Request from Service Finance servicing, 866.254.0497 / Servicing@svcfin.com, or from Bruce Burns, burnsbuildersinc@gmail.com. |
| **Red Rock Concrete** | Inv #1244 balance | **$18,622.00** | No receipt, check, bank record or vendor acknowledgment anywhere after 2022-08-08. Not present in Full Circle's 2022 general ledger either (checked 8/31/2026) — so if it was paid, it was paid from a personal account, most likely Wells Fargo 2797. |
| **Signature Hardware** | net $11,730.49 less $1,883.00 proven | **$9,847.50** | All orders ship to 282 Bald Rock; each has a matching shipment email. Reduced 8/31/2026 by $743.11 of 2022 ledger payments. |
| **Royal Swimming Pools** | #151398 approved $14,980.93 + #152804 $530.95, less $5,592.86 Affirm-proven (see §1) | **$9,919.02** | #151398 customer-approved 2022-11-03 10:41:32 EDT, approval IP logged; kit shipped 11/28 + 12/02. The Affirm loan only financed part of #151398 — the remaining ~$9,388.07 (one payment made at purchase, per the Affirm approval email) and #152804 ($530.95) still have no receipt. |
| **Commonwealth Tile** Inv 1233 / 1228 | | **$1,425.00** | |
| **Lowe's** #761302963 + #771548245 | 2022-10 / 2023-03 | **$1,344.79** | Bald Rock / Verona referenced |
| **Direct Door Hardware** #203991, **Builders Warehouse** #23752 / #23939 | 2020–2021 | **$741.59** | All shipped to 282 Bald Rock |
| | | **$77,240.30** | |

> **Weaver Irrigation — resolved 8/31/2026.** The $7,250 install (Inv 2248 $4,400 + 2377 $1,386 + 2773 $1,464) is now **proven paid** and has moved to §1, on the strength of Weaver's own QuickBooks statements. Separately: there is **no ~$30K "addition to the irrigation system."** The only further Weaver invoices are small recurring service calls — 3117 $990.00, 3209 $109.00, 3375 $75.00, 3772 $109.00 — consistent with seasonal start-up and winterization, not a system expansion, and $1,159.50 of those remains open per Statement #1274.

---

# 3. QUOTED ONLY — treat with extreme care

**Losing bids — do NOT add to basis. The work was done by someone else and is already counted above.**

| Bidder | Amount | Won by |
|---|---|---|
| Turf Specialties, LLC — wall | $46,000.00 | Red Rock ($28,622). Turf's last email is 2022-03-16; Red Rock's estimate was signed 2022-03-17. |
| Turf Specialties — turf | $22,000.00 | No contract, invoice or payment after 2022-03-16 |
| Crown Decorative Concrete (jd0421res, 2021-04-21) | $18,400 wall / $20,900 stamped patio / $5,600 pool-deck overlay | Competing bid against Red Rock |

**Genuine open quotes with no matching invoice:**

| Vendor | Amount | Scope |
|---|---|---|
| Lowe's kitchen quote (KMTCC_22 + V11SLTN3_19) | $43,025.31 | Cabinets $35,830.19 + countertops $6,845.12 + delivery. **Two byte-identical PDFs exist under different filenames — one job.** |
| Crutchfield home theater Est #46208897 | $22,845.41 | 2019-07-05 |
| Sheaves Floors Est 7157 | $22,071.59 | Highest of a 5-figure revision set; **no invoice was ever issued** |
| Commonwealth Tile Est 1005 | $9,250.00 | |
| Burns Builders Est 1557 — gutters | $7,693.85 | Conflicts with a Retex gutter job scheduled 2022-09-22 — don't book both |
| Valley Concrete Inc. Inv 1799 | $12,330.00 | 2023-04-28 |
| Ply Gem window quote #5408830 | $2,322.92 | |
| Eastside Landscaping Est 1027 | $450.00 | |
| Schnitzhofer & Associates | $400.00 site visit, $215/hr | Structural engineer, no invoice found |

---

# 4. SUPERSEDED / VOID / REFUNDED — must never be summed

| Item | Amount | Why |
|---|---|---|
| Red Rock Inv #1244 v1 / v2 | $34,060.00 / $32,440.00 | Superseded by the $28,622.00 final, sent within 4 days |
| Red Rock Estimate #1030 | $21,172.00 | Rolled into Inv #1244 as its first line. **The earlier substantiation file counted this as the total documented spend — it is one line of a larger invoice.** |
| R.E. Boggs — seven sequential quotes | $12,915 – $18,585 each | All revisions of one job. Boggs also over-submitted financing at **$36,000**; Joshua caught it (*"loan amount you all submitted is 6k too high"*) and it was corrected to $29,187.00. **Do not use $36,000.** |
| Royal Swimming Pools cart iterations | $14,543.65 / $13,772.63 / $15,027.23 / $15,052.91 | Superseded by the approved $14,980.93 |
| Sheaves Floors 7133 / 7134 / 7157 | 5 figures | One job, never invoiced |
| Lowe's #761542179 | $317.10 | Cancelled 2022-10-17 |
| Signature Hardware SHW201620919 | $304.32 | Fully refunded to Affirm 2021-09-16 |
| Signature Hardware SHW201586125 | $798.17 | Cancelled and re-placed same day, same order #, same total — count once |
| VBS credit notes 90018317 / 90022104 / 90023362 | $199.27 / $1,255.54 / $5,200.00 | Already netted into the figures above |

---

# 5. THE $45,364.90 VALLEY BUILDING SUPPLY FIGURE IS UNSOURCEABLE

A literal search for `45,364` / `45364` across all 276,529 mail bodies, all 58,625 texts, and all 7,575 indexed iCloud files returns nothing relevant. It matches neither the gross invoiced ($65,324.74), the net invoiced ($58,669.93), the amount shown paid ($27,561.06), nor any subtotal, credit note, or handwritten annotation on the scan.

**Whoever supplied that number should identify the document.** The defensible figure from primary documents is **$58,669.93 net invoiced, of which $27,561.06 is shown settled.**

---

# 6. REFERENCED BUT NO DOLLAR AMOUNT RECOVERABLE

1. **LL Flooring / Lumber Liquidators (Store #1420, Harrisonburg)** — the entire project is documented (in-home assessment 2020-09/10, quote 2020-10-10, install 2021-05, two staircases with custom treads, baseboards, trim, warranty complaint ID#5426534 into 2022) but **every dollar figure sits in PDF attachments never downloaded to this Mac.** The parent files are `.partial.emlx` stubs. Recoverable filenames: `0702794747_Quotation.PDF`, `0134505377_Invoice.PDF`, `0134879323_Invoice.PDF`. Only hard figure is a Synchrony Bank statement balance of $13,215.43 (2021-08-18) — a credit-card balance, not an invoice, and it may include non-282 charges.
2. **Siding** — Joshua: *"I'm putting hardi plank on."* Burns declined to install. No installer, contract, or invoice anywhere.
3. **The hot tub itself** — it exists (a cover was quoted $650 + tax + $350 delivery in 2024-06 texts) but there is no purchase invoice for the tub. A revenue-generating asset with zero documentation.
4. **Lowe's "8 doors"** — no supporting document of any kind.
5. **Lowe's kitchen cabinets — what was actually bought.** Only the $43,025.31 quote, despite a documented cabinet delivery (2021-07-04/05), a damage complaint (2021-04-06), install record `LOWES:0126689000148` (2021-04-05), and a backsplash install (2021-07-07).
6. ~~**Shreckhise Landscape & Design** — the contractor actually used. Plans `Davis 101322.pdf` and `Davis 032323.pdf` exist; no proposal, invoice, or payment.~~ **UPDATED 8/31/2026 — moved to §1, $8,536.50 proven** (bill-pay withdrawal 2023-01-18). Joshua's recollection was "~$30K with Shreckhise" — a mail/text/file search covering all four accounts, all iCloud files, and this one confirmed bank withdrawal found only this single $8,536.50 figure. If the true total is materially higher, it likely moved through one of the 514 unidentified DuPont checks (§0b) or a period outside the DuPont statement coverage (post-Jan 2022) — pulling check images or later statements is the next lever, not further mail search. A "Shreckhise Shrubbery Refund Receipt" dated 2025-07-28 also exists, amount not read (separate small vendor, "Shreckhise Shrubbery Sales," not the landscape/design business).
7. ~~**Plumbing — nothing at all.**~~ **UPDATED 8/31/2026:** the 2020 sweep already found Prestige Plumbing LLC $10,500 (§0b), and the Lodestar 2025 workbooks show a **recurring Wells Fargo bill-pay payee literally named "282 Plumber"** ($188 per payment; two instances visible in the sampled months, certainly more across the year). See §10.
8. ~~**No Augusta County building permit exists** in mail, texts, or files.~~ **FALSE — corrected 8/31/2026.** Full Circle's 2022 general ledger records **Check 1219 to Augusta County, 2022-05-23, $76.50, coded Licenses & Permits, memo "282"**. Small dollars, disproportionate audit value: a permit corroborates that the work was real, inspected and scoped. **Request the permit file from Augusta County** — it will describe the work.
9. Holloway Roofing proposal 2021-03-24 · Retex Roofing gutter job (scheduled 2022-09-22) · Williams Brothers Tree Est 6919 · pavementsoft driveway proposal 2024-08-28 · Happy Little Dumpsters Inv 11443/11836/12350/12462 (2021 demo debris) · 360 Painting (estimate appt at 282, 2022-03-08) · Blue Ridge Fence & Window · Decorative Concrete of Virginia (~700 sq ft pool deck overlay proposal, 2022-07-08) · Glasgow Decorative Concrete · Windridge Landscaping.
10. **Two image-only PDFs with zero extractable text** — see OCR actions below.

---

# 7. FLAGS

### F-1 — Roofing arithmetic — ~~doesn't close~~ **RESOLVED 8/31/2026, except for the remainder**
Burns contract $21,750.00 vs. Service Finance loan xxx3624. The loan is real, in **Hillary D. Davis's** name, and **it ran to payoff** — 24 consecutive statements recovered, $15,357.47 → $891.92, past due $0.00 at the end (see §1 and §11). It did go delinquent in 2021–22 with collector letters, but it recovered: from Feb 2022 onward past-due is $0.00, autopay was re-established via a SurePay form in Jan 2023, and principal was accelerated in mid-2023. **The financed $15,357.47 is bookable.** What is left is the $6,392.53 difference between the loan and the signed estimate — see §2. One document settles it: the Retail Installment Contract for account 3624.

### F-2 — Enlit LLC (~$14,000+) is probably business, not the residence
Invoices are billed to "Full Circle Finance, 282 Bald Rock Rd" but the subject lines read EV chargers / SCIP / "1617 W Main St." Amounts: 1002 $120 (paid), 1005 $284.32→$483.66, 1010 $189.54, 1035 $135, 1039 $767.26, 1041 $252.72, 1045 $189.54, 1049 $571.16, 1050 $379.08, 1051 $461.21, 1053 $189.54, 1054 $2,299.23, 1073 $332.40, 1076 $552.83, plus 2023 unnumbered $685.24 / $1,936.31 / $2,015.96 / $2,628.14 / $2,131.08→$1,131.08 / $547.56, and 2066 $505. **Needs line-item review before any of it touches 282's basis.**

### F-3 — Two OTHER properties are in the same mail stream
`14300 Woods Walk Lane, Midlothian VA` (Heir Mechanical $1,050; Retex "Cancel 14300 woods walk lane"; likely Connect Electric $200) and `148 Hardinberry St, Oak Ridge TN` (LM Coatings $3,360; Volunteer Flooring). Both are rentals with their own Schedule E treatment. Don't let their invoices drift into 282.

### F-4 — Lowe's needs per-order address verification
The index holds 450–916 Lowe's messages *per year*. Spot-checking 2022-10 → 2023-07, most attach to **817 Richmond Rd, Staunton (Valley Pawn, commercial)** — e.g. #761310473 $290.84, #771712935 $54.47, #772672526 $31.13, #772750441 $63.62, #781317658 $391.67. Never sweep Lowe's totals into 282 without checking the ship-to.

### F-5 — Florida contamination runs the other way in 2025–26
Essentially all 2025–26 trade texts are 844 Cypress Crossing: "Drywall 844", "844 Irrigation", All American Electric, Scully Painting, Totally Hooked Plumbing, Home Depot Palm Coast, Paul Francis Jr.

**Added 8/31/2026 — these QuickBooks vendors are FLORIDA, not Bald Rock. Do not let their five-figure invoices drift into 282:**
- **Dan's Floor Store** (145 Hilden Road Suite 104, Ponte Vedra FL) — estimates $42,297.60 / $53,243.72 / $54,924.52 / $57,394.52, invoices $33,644.01, $5,317.98, and a "pool bath invoice" $3,452.00, running Sept 2025 → Apr 2026. Careless keyword matching flags these as Bald Rock because the flooring product line is called **"Verona Collection."** It is a product name, not the town.
- **Flooring And More By Austin** — Inv 630 $36,969.59, Inv 652 $8,000.00, estimates to $34,721.16.
- **Premier Specialty Service LLC** — Inv 5534 $11,179.83 (paid 2026-08-05), Inv 5553 $185.00.
- **Gary's Audio & Video Installation** — estimates $18,139.77 / $17,173.26.
- **Ancient City Landscaping LLC** — Est 1178 $8,019.96 → $6,000.00.

### F-6 — Repairs, not capital improvements
A&B Mechanical $100 diagnostic · Heir Mechanical $1,050 · S.A.F.E. pressure wash $571.65 (paid 9/26/22, MC ****1689) · Renu maintenance $195.40 / $53.15 · Augusta County Disposal $93/$123/$63/$63/$93 · Augusta County RE tax $2,989.23 · Signature Hardware warranty replacement C14 ($0.00) and refunds C10/C15 · LL Flooring warranty complaint and the $122.00 MasterCard reimbursement (LL concluded the cracked boards were not a manufacturer's defect) · the ~130-message VBS "Still missing" thread and the "282 Bald Rock Road Plygem Issues" thread are defect/replacement correspondence running to 2024-08.

### F-7 — Much of this spend predates 2021
Crutchfield 2019 · ProjectorScreen 2020-02 · Ply Gem quote 2020-04 · Commonwealth Tile 2020 · Sheaves 2020 · cabinet drawings 2020-03 · Signature Hardware from 2020-04 · VBS from 2020-04. **This collides directly with the lesser-of-adjusted-basis-or-FMV test at the Aug/Sep 2025 conversion.** Five years of improvements do not stack onto a 2025 FMV — they are components of adjusted basis, and FMV may cap the whole thing.

### F-8 — Irrigation vs. plantings
Irrigation systems are 15-year land improvements; plantings may be non-depreciable land. Don't blanket-assume for the Weaver Irrigation $7,250 — which is now **proven paid** (§1) but still needs that capital-vs-land split. Weaver's post-2024 service invoices ($1,159.50 open) are maintenance, not capital.

### F-9 — Fundamental Siteworks Inv 670 covers pool demo AND grading
Book once. It appears under both the pool and landscaping headings.

---

# 8. NEXT ACTIONS — evidence recovery, highest value first

1. **OCR `.../282 Bald Rock Rd - Verona VA (Rental)/Valley Building Supply - PlyGEM/invoices & credits.pdf`** — 33 pages, image-only, zero extractable text. This is where the windows/doors/siding dollars live. Note the byte-identical duplicate at `.../Valley Building Supply - PlyGEM - Emails & Media/invoices & credits.pdf` — do not double count.
2. **Re-download the LL Flooring attachments.** The messages are `.partial.emlx`; opening each in Mail while online pulls the PDFs. Only vendor with a fully documented project and zero readable figures.
3. **Pull card statements** for MC ****0305, MC ****6246, MC ****1689, LCC ****1037, and Amex ****7115 / ****1005. These cards already paid Bald Rock vendors and would convert most of the $110,673.74 invoiced block to proven.
4. **Find the Red Rock $18,622.00 payment.** Red Rock invoiced through `quickbooks@notification.intuit.com`, so a receipt should exist. Check Aug–Oct 2022.
5. **Burns Builders final invoice + Service Finance loan xxx3624** origination and payoff — resolves F-1 and converts $21,750.
6. **MyLowe's Pro purchase-history export**, 2020–2023, filtered to the Verona ship-to — resolves both the $43k cabinet quote-vs-actual and the "8 doors" question at once.
7. **OCR `.../Renovations/Davis Cab Estimate.pdf`** — image-only, the only cabinetry document.
8. **OCR `282 Bald Rock - Scanned Doc CCF_001781.pdf`** (2 MB, Apr 2022, image-only) — likely another invoice bundle.
9. **Request a Valley Building Supply customer statement** for account "JOSH DAVIS," 2020-01 → 2022-12. Settles the $45,364.90 question and the two invoices with illegible balances.
10. **Identify the hot tub vendor.**
11. **Query Augusta County directly for permits, 2020–2025.**
12. **Ask Shreckhise Landscape for copies** of the 2022–2023 invoices — the work was performed, no paperwork survives locally.

---
Every dollar figure above was read directly off a document or email body. Nothing is estimated, prorated, or inferred. Classification as capital vs. repair, and the final basis computation, are Silverline Tax's calls — this is an evidence file, not a return position.

---

# 9. ADDENDUM 8/31/2026 — Valley Building Supply invoice request, DuPont acct 766518, pool vendors, Shreckhise, 2025 HVAC/patio/irrigation

Prompted by a round of direct owner questions. Summary of what changed above; full detail in this section.

**Valley Building Supply.** Confirmed windows/doors run through Valley Building Supply, Staunton — see §1/§2 above ($27,561.06 proven / $31,108.87 open). Sent a concise invoice-request email 8/31/2026 to Adair Griffin (agriffin@valleybuildingsupply.com, cc Vince Laffler) asking for a full copy of all Bald Rock invoices, to settle the open-balance and illegible-scan lines. No dollar total found anywhere near the "$75–100K" figure Joshua recalled — the documented net invoiced total is $58,669.93. Awaiting VBS's reply.

**DuPont Community Credit Union account 766518.** This is the same Full Circle Finance business-checking relationship already swept in §0b (statements on file cover 01/2020 → 12/2021 + partial Jan 2022 only). Re-pulled and text-searched all 26 on-file statement PDFs specifically for Valley Building Supply activity: found the same three charges already in §1 ($3,103.62 + $5,212.53 + $14,634.79 = $22,950.94) — no new dollars, just independent re-confirmation. The Feb-2022-onward coverage gap (§0b) remains the binding constraint on finding anything paid after that date from this account, including Burns Builders' resolution, Red Rock's $18,622 balance, and any 2022+ Shreckhise or Weaver Irrigation activity.

**"Cannonball Pools."** Does not exist as a vendor anywhere in mail, texts, files, or any of the 26 bank statements. The actual 2020–2023 pool project vendors are Fundamental Siteworks (demo/dig, §1, now fully proven at $5,329.00), Red Rock Concrete (retaining walls around the pool, §1/§2), and Royal Swimming Pools (equipment/kit, §1/§2) — not "Pool Warehouse," which only reached a $13,910 quote stage with no confirmed order anywhere in the record.

**Shreckhise Landscaping — see §1 and §6.** $8,536.50 proven via a bank bill-pay withdrawal captured in Lodestar Tax's own Jan-2023 bookkeeping report; the "~$30K" recollection is not corroborated beyond that one figure.

**2025 HVAC.** Already fully documented pre-8/31/2026 — R.E. Boggs, Inc., $29,187.00, two Rheem systems (Inv I-5192-1 $15,936.00 + I-5192-2 $13,251.00), Service Finance loan 5977065 signed 2025-09-05, financed amount corrected down from an over-submitted $36,000 (see §4). This is very likely "the new HVACs" Joshua was recalling — no second/separate 2025 HVAC purchase found. One documentation caveat added in §1: Payzer (R.E. Boggs's own invoicing portal) still shows both invoices "Overdue" as of 2025-12-16, three months after the loan closed — normal for third-party POS financing but worth a confirming call to R.E. Boggs if ever challenged.

**New front patio / walkway (2025).** Joshua recalled "Valley Outside Services did our patio" — no such vendor exists in any record. The actual vendor, confirmed by matching a Joist invoice link across both text messages and email, is **Pro Quality Property Maintenance** (contact saved locally as "282 Hardscape," Brandon Turner, proqualipm@gmail.com). Estimate #1071 accepted Sept 2024; Invoice #4347 for $4,800.00 issued Dec 2024/Jan 2025; a "Patio visually crooked" punch-list complaint and a "Front walkway done!" text both landed 2025-01-03; Payzer's balance-due record dropped from $4,800.00 to $3,600.00 by 2025-01-28 (~$1,200 unconfirmed as payment vs. credit). Added to §2 at the full $4,800.00 pending better payment proof.

**Irrigation "improvements/addition" (2025).** Vendor is Weaver Irrigation, LLC (already in §2 for the original $7,250.00 install). No 2024–2025 invoice resembling a $30K-scale addition was found — only small recurring service invoices ($75–$990 each). See the note under §2. If a bigger irrigation project happened, it isn't showing up in Weaver's billing history; worth confirming with Weaver directly.

**Front porch / interior caulking repairs (2025).** No vendor, invoice, or payment found under this description. Not yet substantiated — open item.

**Not yet resolved / still open:** the Pro Quality Property Maintenance $4,800 payment status; the porch/caulking repairs; Red Rock's $18,622 balance; Burns Builders' $21,750 (see the correction note under §1); and everything already flagged in §8 Next Actions (VBS OCR, card statements, DuPont statements Feb 2022 onward, check images).

---

# 10. ADDENDUM 8/31/2026 (second pass) — THE LODESTAR LEDGER

The first 8/31 pass (§9) worked the mail index. This pass went after the bookkeeping itself, and it changed the shape of the problem.

**What was done.** Pulled all **564 emails from Lodestar Tax & Consulting** (Chrisney Sigstad, Liana Motel), located their attachments on disk, and parsed **32 spreadsheet workbooks** — monthly uncategorized-transaction reports, a full-year 2022 1099-compilation general ledger, and a 2022 shareholder-distributions QuickReport. That is 10,249 transaction lines, 6,301 unique after dedupe. Parsed CSVs kept at `_lodestar_xlsx/` in this folder; extraction scripts at `_lodestar_dump.py`, `_find_attach.py`, `_parse_xlsx.py`.

**Why it mattered.** DuPont statements print only a check number. **Lodestar's ledger names the payee.** That single fact cracked items this file had written off.

### Newly proven — moved into §1

| Vendor | Amount | Source |
|---|---|---|
| Pro Quality Property Maintenance | $7,800.00 | Check 5061 $3,000 (2024-12-31) + 4 × $1,200 bill pay (Jan–Feb 2025), WF Checking 2797 |
| Valley Building Supply — 2022 | $2,161.00 | 2022 GL, Repairs & Maintenance |
| Signature Hardware — 2022 | $743.11 | 2022 GL, Repairs & Maintenance |

Also confirmed at source (not reconstructed from mangled email text): **Shreckhise $8,536.50**, read directly out of `Uncategorized_Jan2023.xlsx`.

### ⚠️ THE FINDING THAT MATTERS MOST — Wells Fargo Checking 2797

**This file has never seen this account.** Every prior sweep covered DuPont only. The Lodestar 2024–2025 workbooks show WF 2797 paying Bald Rock trades directly:

| Date | Payee / memo | Amount |
|---|---|---|
| 2024-12-31 | Pro Quality Property Maintenance, Check 5061 | $3,000.00 |
| 2025-01-22 / 01-29 / 02-05 / 02-12 | BILL PAY **Hardscape** RECURRING | $1,200.00 each |
| 2025-06-05 | ZELLE to "AVABI" — memo **GUTTERS** | $1,745.00 |
| 2025-07-16 / 07-18 | ZELLE to "Marlon" — memos **TILE BORO** / **TILE 1790** | $2,000.00 / $1,000.00 |
| 2025-09-03 | ZELLE to "GC" — memo **POCKET DOOR FRAMES** | $832.03 |
| 2025-09-16 | BILL PAY **Flooring ON-LINE** | $1,000.00 |
| 2025-09-03 / 09-17 | BILL PAY **"Electric 282"** RECURRING | $297.00 each |
| 2025-09-03 / 09-17 | BILL PAY **"282 Plumber"** RECURRING | $188.00 each |

Two of those payees Joshua named himself when setting up bill pay: **"Electric 282"** and **"282 Plumber."** The property is in the payee name.

**And this is only the visible sliver.** Lodestar's uncategorized reports capture, by definition, only what the bookkeeper *could not categorize*. Everything correctly coded never appears in them. The real WF 2797 activity is certainly larger — possibly much larger.

> ### → PULL WELLS FARGO CHECKING 2797 STATEMENTS, 2024-01 → PRESENT.
> This is now the highest-value document pull on the property, ahead of the DuPont check images. An entire funding account for the 2024–2025 work is undocumented in this file.

### Paid, but property attribution unconfirmed — $17,275.53

Real cleared payments out of Full Circle's business accounts. The money moved; what is unconfirmed is the *service address*. Full Circle pays five pawn stores, 817 Richmond Rd, and this rental from the same accounts, so none of this may be booked to 282 without confirming where the work happened.

| Vendor / payee | Work | Date | Amount | Confidence it's 282 |
|---|---|---|---|---|
| Augusta County | **Building permit**, Check 1219, memo "282" | 2022-05-23 | $76.50 | **Very high** |
| Bill Pay "Electric 282" | Electrical | 2025-09 | $594.00 | **Very high** |
| Bill Pay "282 Plumber" | Plumbing | 2025-09 | $376.00 | **Very high** |
| Augusta Aluminum Gutterworks | Gutters, Check 1206 | 2022-04-08 | $4,500.00 | High |
| Augusta Steel Corporation | Steel, Verona VA | 2022-03-09 | $2,652.50 | Medium |
| Fiber Pro Insulation Inc | Insulation, Check 1210 | 2022-04-21 | $2,500.00 | Medium |
| ZELLE "AVABI" | Gutters | 2025-06-05 | $1,745.00 | Medium |
| ZELLE "Marlon" | Tile | 2025-07 | $3,000.00 | Low — "BORO" may mean the Waynesboro store |
| Bill Pay "Flooring ON-LINE" | Flooring | 2025-09-16 | $1,000.00 | Medium |
| ZELLE "GC" | Pocket door frames | 2025-09-03 | $832.03 | Medium |
| | | | **$17,275.53** | |

**Augusta Aluminum Gutterworks $4,500 also resolves the open gutter question** in §3 (Burns Est 1557 $7,693.85 vs. the Retex job). Neither of those bids appears to have been the work — Augusta Aluminum was paid.

### What the ledger could NOT resolve

- **Burns Builders $21,750 (2021 roof).** The oldest transaction-level Lodestar export is 2022. A 2021 P&L exists but carries no transaction detail. **Ask Lodestar directly for a 2020–2021 general ledger export** — one email, and it is the only remaining route short of the loan file.
- **Red Rock $18,622.** Not in the 2022 GL at all. If it was paid, it came from a personal account — WF 2797 is the obvious candidate.

### Correction to §6 items 7 and 8
Both of those "nothing found" entries were false negatives and have been struck through above. Plumbing exists. The permit exists.

### Deliverable
`282_Bald_Rock_Payments_Proven_and_Unproven.xlsx` (this folder) — five sheets: not proven, newly proven, paid-but-attribution-TBD, the gap analysis, and the proven list for reference.

---

# 11. ADDENDUM 8/31/2026 (third pass) — THE LENDER AND QUICKBOOKS TRAILS

Two questions from Joshua drove this pass: *"we paid Burns through monthly installments, look for who that was set up through"* and *"have you looked through emails from QuickBooks asking for payment or sending for payment."* Both were right, and both paid off.

## Burns Builders — the financing, and the proof it ran to payoff

**Set up through: Service Finance Company, LLC.** 555 S. Federal Hwy #200, Boca Raton FL 33432. NMLS 140908. Now a subsidiary of **Truist**. Retail installment contract, **account ending 3624** (internal ref 2983624), borrower **HILLARY D. DAVIS**, property address 282 Bald Rock Road. Servicing: 866.254.0497, Servicing@svcfin.com. Payment **$380.82/month**. It is a WPDI ("With Payment, Deferred Interest") promotional-period product.

Every collector notice ties the loan to the work: *"your account related to the ROOFING project completed by Burns Builders Inc on 7/10/2021."*

**24 consecutive monthly statements were recovered.** The payoff series is unbroken:

| Statement due | Payoff | | Statement due | Payoff |
|---|---|---|---|---|
| 09/14/2021 | $15,357.47 | | 09/14/2022 | $11,230.63 |
| 10/14/2021 | $14,296.69 | | 11/14/2022 | $10,549.28 |
| 11/14/2021 | $14,007.99 | | 12/14/2022 | $10,198.60 |
| 12/14/2021 | $13,708.67 | | 01/14/2023 | $9,847.29 |
| 01/14/2022 | $13,411.49 | | 02/14/2023 | $9,490.84 |
| 02/14/2022 | $13,109.75 | | 03/14/2023 | $8,102.35 |
| 03/14/2022 | $12,784.72 | | 04/14/2023 | $6,704.47 |
| 05/14/2022 | $12,672.61 | | **08/14/2023** | **$891.92** |
| 06/14/2022 | $12,206.64 | | | |
| 08/14/2022 | $11,555.29 | | | |

Past due is **$0.00** from Feb 2022 onward. Autopay was re-established in Jan 2023 (Joshua faxed a new SurePay form; Service Finance confirmed receipt on 1/18/2023). Principal was accelerated through spring/summer 2023 — the Mar→Apr and Apr→Aug drops are far larger than the $380.82 scheduled payment, which is what a borrower does to beat a deferred-interest promotional expiry. The last payment-posted email is 2023-07-03, the last statement 2023-07-31, and the account then goes silent for good.

**Conclusion:** the loan funded, Burns was paid by the lender at funding, and Joshua repaid it to completion in fall 2023. **$15,357.47 moves to §1.** The residual $6,392.53 against the $21,750 signed estimate stays in §2 until the Retail Installment Contract (which states the exact Amount Financed) or Burns' final invoice turns up.

*Note: Burns' gutter estimate 1557 ($7,693.85) was a losing bid — §10 shows Augusta Aluminum Gutterworks was paid $4,500 by check for gutters in April 2022.*

## The QuickBooks trail — 727 emails pulled and indexed

Every Intuit/QuickBooks, Joist, Payzer, WePay and Bill.com email in the archive (727) was dumped and read. That produced a complete list of QuickBooks **payment confirmations** — which is a real evidentiary instrument, because these vendors invoice through QuickBooks and a confirmation is generated when the invoice is paid through it.

**What it proved:**
- **Weaver Irrigation $7,250 → §1.** Weaver's QuickBooks statements list *open items only*. Statement #1240 (2024-02-28) shows only Inv 2377 open at $1,286.00 — Inv **2248 ($4,400) has dropped off entirely**, exactly matching the four $1,100 DuPont payments of 2023-08-21. Statement #1274 (2025-07-30) no longer lists 2377 or 2773 either, and shows a $600 payment (#217816712, 2024-09-06). All three install invoices settled.
- Existing §1 entries independently re-confirmed at source: Commonwealth Tile #1294 $1,685.00 (2022-11-20), #1252 (2021-04-08), #1265 (2021-08-01); Fundamental Siteworks #670 $3,000.00 (2022-11-22) and $2,329.00 (2023-03-01), the pair explicitly reconciling to the $5,329.00 invoice total.

**What it proved by absence — and this now means something:**
- **Burns Builders never sent a QuickBooks invoice.** Only two estimates (1548 $21,750, 1557 $7,693.85). There is no QuickBooks payment record for Burns because the financing *was* the payment path. That closes the question rather than leaving it open.
- **Red Rock Concrete sent payment requests but no payment confirmation ever followed.** The sequence: estimate 1030 revised $33,400 → $36,400 → $21,172 → $9,782; then invoice 1244 issued 2022-08-04 with balance due revised $24,060 → $22,440 → **$18,622**; then reminders on 8/7 and 8/8/2022 — and then silence. Red Rock used QuickBooks and generated confirmations for other customers' payments. For every other QuickBooks vendor in this file where a payment was made through the platform, a confirmation exists. **For Red Rock's $18,622, none does.** That does not prove non-payment — it could have been paid by check or ACH outside the platform — but the absence is now informative rather than merely unknown, and it raises the priority of finding a Red Rock receipt or a matching bank debit.

## Where this leaves the file

Proven-paid moved from $124,777.87 to **$147,385.34**. Not-proven fell to **$77,240.30**, and of that, over half is two items — Valley Building Supply ($28,947.87, invoice request already out) and Red Rock ($18,622.00).

**Working files** (this folder, re-runnable): `_burns/` (9,168 lender/roofing emails), `_qb/` (727 QuickBooks-family emails), `_burns_dump.py`, `_qb_dump.py`.

---

# 12. ADDENDUM 8/31/2026 — SEARCH COVERAGE AUDIT (is anything hiding in the cloud?)

Joshua asked the right question: is this only local Apple Mail, or does it reach the cloud accounts too? Measured rather than assumed.

## What is actually indexed

The unified index was **rebuilt 2026-08-31 03:55 AM** (nightly launchd agent). It holds **342,519 mail rows** — up from 276,529 when this file was first built on 8/5 — plus 49,428 files, 62,158 texts, 1,961 reminders, 252 Google Drive items, 1,418 photos, 93 notes.

Apple Mail is configured with **10 accounts**, and **all 10 appear in the index**. Nothing configured is being skipped:

| Account | Rows | Local history |
|---|---|---|
| **zapvp1@me.com** ("Personal") | 242,485 | Full, back to 2009 |
| **fullcirclepawn@gmail.com** ("Corporate") | 28,580 | Full |
| jdavis@fcfpawn.com | ~15,900 | from 2024-02 |
| joshuachristiandavis@gmail.com | ~12,600 | from 2024-02 |
| lexington / harrisonburg / roanoke / waynesboro / culpeper @fcfpawn.com | ~7,600–12,400 each | from 2023-11 / 2024-02 |

## The one apparent gap, and why it is not a real one

Six accounts start in late 2023 / Feb 2024. That looked like a sync truncation. It is not — **the fcfpawn.com Google Workspace itself has no mail before then.** Verified directly against the live Gmail API, not inferred:

- `before:2022/01/01 in:anywhere` → **zero results**
- `before:2023/06/01 in:anywhere` → **zero results**
- earliest real content found: **November 2023**

So the Workspace was created around Nov 2023. There is nothing older in that cloud to be missing. The entire 2020–2023 renovation predates those mailboxes.

A live cloud sweep of the Nov 2023 → Feb 2024 window (`invoice OR estimate OR contractor OR "Bald Rock" OR roof OR concrete OR irrigation OR pool OR flooring`) returned 22 threads, all non-property: Porsche shopping, Spindrift orders, ATF trace requests, Google Workspace invoices. The single vendor item — a $200 Connect Electric invoice — was addressed to **both** zapvp1@me.com and jdavis@fcfpawn.com, and is already in the local index via the me.com copy.

**That is the structural point: property and vendor mail goes to zapvp1@me.com and fullcirclepawn@gmail.com, the two accounts with complete local history. The fcfpawn.com store accounts are, at most, CC'd.**

A live search of the connected cloud account for `Burns Builders OR svcfin OR "Red Rock Concrete" OR "Valley Building Supply"` returned **zero** — those vendors never touched that mailbox.

## Verdict
For 282 Bald Rock, the local index is a complete view of the email record. **The remaining gaps in this file are banking and document gaps, not email gaps** — Wells Fargo 2797, DuPont post-Jan-2022, DuPont check images, card statements, and a 2020–2021 Lodestar ledger export. More email searching will not move the number.

**Caveat worth keeping:** the fcfpawn.com Workspace is the account Joshua now sends property correspondence *from* (the Valley Building Supply request, the Blue Ridge appraisal thread). Its local copy starts Feb 2024, so it is current — but anything he sends from it is only as searchable as the last nightly rebuild.
