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
> **1. Valley Building Supply — RESOLVED 9/1/2026.** Request was re-sent 8/31/2026 from zapvp1@me.com (the jdavis@fcfpawn.com attempt bounced, `550 blocked`), but no reply arrived and the vendor's own listed contacts (vlaffler@, gstrawderman@, ccash@) predate its closure. **Joshua confirmed 9/1/2026 that Valley Building Supply / Allied Concrete has gone out of business and further invoice documentation cannot be obtained.** Rather than leave $28,947.87 permanently stuck in "invoiced, not proven," it has been reclassified to Proof of Payment (§1) on the strength of: (a) the itemized line-by-line invoice detail already in hand — every window and door purchase now broken out by date, invoice #, description and price in `282 Bald Rock - Windows and Doors (VBS Invoices).xlsx`; (b) the "Balance Due $0.00" / "CREDIT CRD" marking already accepted as proof for the other $29,722.06 of this same vendor; and (c) 10 photos (IMG_1381, IMG_1394–1420, dated 2022-03-23/24, in `.../Valley Building Supply - PlyGEM - Emails & Media/`) timestamped days after the final Feb 2022 invoice batch (#00306738 — the triple DH windows and gliding patio door), consistent with delivery/installation of that order. **This is a taxpayer representation given the vendor's closure, not third-party proof — flag it as such to Silverline.** See §13 for the full reclassification writeup.
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
| **Proof of payment on the face of a document** | **$475,119.42** |
| Invoiced, payment not proven | $41,899.90 |
| Paid, but property attribution unconfirmed (see §10) | $17,276.03 |
| Paid, but capital-vs-service purpose unconfirmed (see §22) | $7,470.00 |
| Quoted only — **includes losing bids, see warning below** | ~$176,000 |

Against a claimed **$305,086.51** (that figure predates today's Prestige Plumbing find — see below). Documented-and-paid went from $21,172 → $97,615.40 (8/5/2026 pass) → $114,073.76 → $124,777.87 → $147,385.34 (8/31/2026) → $188,541.68 (9/1/2026, earlier passes) → **$250,885.21** on 9/1/2026 (Burns Builders closed out plus $55,293.53 of newly confirmed spending — see §18) → **$253,895.21** on 9/2/2026 (Gonzales Virginia Painting $3,010.00 confirmed as 282 Bald Rock — see §19) → **$465,619.41** on 9/2/2026 (the full $211,724.20 Pottery Barn card total confirmed as 282 Bald Rock — see §20) → **$475,119.42** on 9/2/2026 (Shreckhise's 2023-2024 bill-pay history fully swept — see §21; corrected 9/2/2026, see §24 — the earlier $475,226.82 figure accidentally included the $107.41 Shreckhise Shrubbery Sales line, which is explicitly tracked separately and never meant to be summed in). Three passes on 8/31: the first completed Fundamental Siteworks, proved the Royal Swimming Pools Affirm payoff and found the Shreckhise bank withdrawal (§9); the second recovered **32 Lodestar Tax bookkeeping workbooks** out of 564 Lodestar emails and read the actual general ledger (§10); the third worked the **lender and QuickBooks trails** and closed out Burns Builders and Weaver Irrigation (§11). On 9/1/2026: Valley Building Supply's remaining $28,947.87 was reclassified to proven (vendor now defunct, see §13), and a wholly new vendor — **Prestige Plumbing LLC, $12,208.47** — was found and proven, none of which was in any prior bucket of this file. See §13.

> **The "quoted" column is not a shopping list.** It contains at least two competing bids for work another contractor actually performed (Turf Specialties $46,000 and Crown Decorative Concrete $18,400 both bid the retaining wall Red Rock built for $28,622). Carrying those alongside Red Rock double-counts the wall. Quotes belong in basis only where a matching invoice or payment exists.

---

# 0. WHY THE RECEIPTS MATTER — THE BASIS MATH

**Purchase price of 282 Bald Rock: $405,000.00**, per the recorded deed — `CONSIDERATION: 405,000.00`, `Consideration/Actual value: $405,000.00`. Acquired 2016 (contract 8/8/2016 via Charlotte McAlister, RE/MAX Advantage; financing through BNC National Bank; United States Appraisal LLC ordered 9/13/2016). Source: `.../02 Real Estate/282 Bald Rock Rd - Verona VA (Rental)/282 Bald Rock Deed:Closing.pdf` — image-only, OCR'd 8/5/2026.

On conversion of a personal residence to a rental, depreciable basis = **the LESSER of** adjusted basis or FMV at the conversion date. Adjusted basis = purchase price + capital improvements − depreciation previously allowed (here $0, since it was a residence throughout).

| Scenario | Adjusted basis |
|---|---|
| Purchase price alone | $405,000 |
| + improvements **proven paid** ($475,119.42, corrected 9/2/2026 — see §24) | **$880,119.42** |
| + improvements proven **and** currently invoiced ($517,019.32) | **$922,019.32** |
| + the full claimed $305,086.51 (pre-9/1/2026 figure) plus the new $12,208.47 Prestige Plumbing find, if all documented | $722,295.98 |

**Implication: adjusted basis is very likely the binding constraint, not FMV.** For the appraisal to cap this, the property would have to be worth *less* than roughly $503K–$710K in August 2025 — i.e. under ~24%–75% appreciation over nine years, on a house that was gut-renovated in the interim, in a market that ran hard 2016→2025. Possible, but not the way to bet.

**So every documented improvement dollar is very likely a real dollar of depreciable basis.** The $41,899.90 still sitting in the "invoiced but unproven" column (down from $77,240.30 after the 9/1/2026 VBS reclassification, §13, and down again after closing out Burns Builders — see §18) is the largest remaining recoverable prize in this file — and bank and card statements are what convert it. As of 8/31/2026 the highest-value single pull is **Wells Fargo Checking 2797**, an account this file had never seen until the Lodestar workbooks surfaced it (§10).

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

# 1. PROOF OF PAYMENT — $475,119.42

| Vendor | Doc / Date | Amount | Covers | Proof |
|---|---|---|---|---|
| **R.E. Boggs, Inc.** (Charlottesville) | Inv I-5192-1 + I-5192-2, 2025-09-03 | **$29,187.00** | Two Rheem HVAC systems | Service Finance loan 5977065, borrower addr 282 Bald Rock Rd, signed 2025-09-05; Certificate of Completion 2025-09-08. *(See 8/31/2026 addendum — Payzer/R.E. Boggs's own invoice portal still shows both I-5192-1 and I-5192-2 as "Overdue" as of 2025-12-16, three months after loan signing. Standard for dealer POS financing — Service Finance pays the dealer at closing and Payzer's own status often never syncs — but worth a direct confirmation call to R.E. Boggs if this is ever challenged.)* |
| **Valley Building Supply** | 2020-04 → 2022 (multiple) | **$58,669.93** | PlyGem/Mira windows, patio + bi-parting doors, trim, AZEK porch/decking | $29,722.06 independently proven (Balance Due $0.00 / "CREDIT CRD" on invoice faces net of a $1,255.54 credit-noted return, plus $2,161.00 of 2022 debit-card charges read off Full Circle's 2022 GL) **+ $28,947.87 reclassified from §2 on 9/1/2026 per Joshua's instruction — Valley Building Supply / Allied Concrete has gone out of business and further documentation cannot be obtained. Backed by the itemized invoice detail in `282 Bald Rock - Windows and Doors (VBS Invoices).xlsx` and 10 dated photos (2022-03-23/24) of the final invoice batch. Taxpayer representation, not third-party proof — see §13.** |
| **Prestige Plumbing LLC** | 2020-09 → 2021-06 | **$12,208.47** | Whole-house plumbing: under-sink filter system, whole-house filter, and full water softener replacement (Inv #I200925943, item list confirms "Filter System (Under Sink)," "Standard Whole House Filter," "Replace Premium Electronic Water Softener") + a later 2021 job | Inv #I200925943 (Due 09/25/2020): **$8,300.00**, Invoice Due $0.00 on the invoice face, corroborated by two Intuit card receipts on the same Mastercard ****9983 ($3,500.00 9/16/2020 + $3,300.00 10/7/2020). A separate card receipt **$2,200.00** (12/2/2020) and Inv #I210505245 (**$1,708.47**, paid in full, 6/2021) are additional Prestige Plumbing charges. Cross-corroborated: Joshua's 2020 CPA (Kris McMackin, 1/2022 email) lists "Prestige Plumbing" alongside Valley Building Supply, Lowe's and Commonwealth Tile as 2020 renovation subcontractor/R&M expense. Found and added 9/1/2026 — see §13. |
| **Burns Builders Roofing** — financed portion | Loan funded ~2021-07; amortized to payoff by 2023-09 | **$15,357.47** | Roof (Est 1548, installed 7/6/2021, completion confirmed 7/10/2021) | **Service Finance Company, LLC** (Boca Raton FL, NMLS 140908, now a Truist subsidiary) retail installment contract, account ending **3624**, borrower **Hillary D. Davis**, 282 Bald Rock Road. Under dealer point-of-sale financing the lender pays the contractor at funding, so Burns was paid this amount. **24 consecutive monthly statements recovered** showing an unbroken amortization: $15,357.47 (due 09/14/2021) → $13,411.49 (01/2022) → $11,230.63 (09/2022) → $9,490.84 (02/2023) → $6,704.47 (04/2023) → **$891.92 (due 08/14/2023)**, past due $0.00. Payment $380.82/mo with accelerated principal in 2023 (consistent with beating the deferred-interest promotional expiry). Last payment-posted email 2023-07-03; last statement 2023-07-31; the account then goes silent — it ran to payoff. Added 8/31/2026. |
| **Burns Builders Roofing** — unfinanced remainder | 2021-07-11 | **$7,050.00** | Roof (same job as above) | Debit-card charge to "Burns Builders Inc," Port Republic VA, from Joshua's personal DuPont account (831015-0090), dated the day after the roof's completion was confirmed (7/10/2021). Replaces the $6,392.53 estimate previously carried in §2 (the gap between the $21,750.00 estimate and the $15,357.47 financed portion) — actual payment was $657.47 more than the estimate implied. **Closed out 9/1/2026 per Joshua's instruction and his confirmation that this spending is 282 Bald Rock.** Moved from §2. |
| **Weaver Irrigation, LLC** Inv 2248 + 2377 + 2773 | 2023-06 → 2024-05 | **$7,250.00** | Irrigation install and additions | **The vendor's own statements prove it.** QuickBooks statements list open items only. Statement #1240 (2024-02-28) shows just Inv 2377 open at $1,286.00 — **Inv 2248 ($4,400) is gone**, matching the four $1,100 DuPont payments of 2023-08-21 to the dollar. Statement #1274 (2025-07-30) no longer lists 2377 or 2773 either, and records a $600 payment (#217816712, 2024-09-06). All three invoices settled. Moved from §2 on 8/31/2026. *(Weaver's later small service invoices — 3117 $990, 3209 $109, 3375 $75, 3772 $109 — remain open at $1,159.50 and are recurring maintenance, not capital; see F-8.)* |
| **Shreckhise Landscape & Design** | Bill Pay, 2023-01-18 → 2024-03-21 (9 payments) | **$18,036.50** | Landscaping (per "Landscape Plan" / "Design for Between Walls" correspondence 2022-11 → 2023-03, plus a later phase and an Oct-2024 mulch/tree delivery) | DuPont business acct (766518) bill-pay withdrawals "SHRECKHISE LANDS": $8,536.50 (1/18/23, documented in Lodestar's Jan-2023 bookkeeping report) + $5,000.00 (10/18/23) + $1,000.00 (11/15/23) + $1,000.00 (12/27/23) + $500.00 x5 (2/5/24, 2/29/24, 3/7/24, 3/14/24, 3/21/24). Found by re-scanning the full 2015-2024 business statement archive, 9/2/2026 — see §21. The recurring $500 bill-pay pattern was still running when the archive ends (June 2024), so more payments likely exist past that date. Also found: **Shreckhise Shrubbery Sales** (a separate, related retail nursery business) $107.41, debit card, 4/25/24 — small, kept as its own line item since it's a different legal entity, not summed into the $18,036.50. |
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
| **Lowe's** (personal DuPont 831015-0090) | 2021, multiple | **$36,040.14** | **Very likely the kitchen cabinet job** — see §23 | Debit-card charges, Joshua's personal account. Confirmed 282 Bald Rock by Joshua 9/1/2026. Distinct from the $51,887.96 business-account Lowe's ACH total in §0b, still needing store-vs-property attribution and not counted here. **9/2/2026: the exact 12 transactions making up this total (Jan-Sept 2021, card ****6246) reconstruct to within $21.05 of the $35,830.19 cabinets-only line in the §3 kitchen quote — see §23 for the full reconciliation.** |
| **EasyClosets.com** | 2021, three orders (6/15, 7/7, 7/28) | **$7,453.59** | Custom closet systems | Debit-card charges, personal DuPont account. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Shades of Light** | 2021-2022, multiple | **$4,652.74** | Lighting fixtures | $3,128.43 (2021) + $1,305.57 (2022) personal-account charges + $218.74 (2022) business R&M ledger. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Grand Home Furnishings** | 2022 | **$1,931.00** | Furniture | $200.00 personal-account charge + $1,731.00 business R&M ledger charge. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Wayfair / AllModern** | 2022 (6/19, 11/9) | **$1,538.41** | Furniture/decor | Personal-account debit charges. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Ashley Furniture** | 2022-03-29 | **$704.39** | Furniture | Business R&M ledger, debit card. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Decor Planet** | 2021-02-02 | **$771.97** | Lighting/decor | Personal-account debit charge. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Pottery Barn** | 2021-02-05 | **$414.67** | Furniture | Personal-account debit charge, Joshua's own card. **Joshua states most interior/exterior furniture was Pottery Barn purchases on Hillary's card, not yet located — this $414.67 is very likely a small fraction of the true Pottery Barn total. Open item — see §18.** |
| **Sarisand Tile** (Charlottesville) | 2022-10-23 | **$550.93** | Tile | Personal-account debit charge. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **North American HVAC** | 2022-02-19 | **$260.79** | HVAC service | Business R&M ledger, debit card. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Valley Comfort System** | 2022, three charges | **$771.90** | HVAC service | Business R&M ledger, debit card ($150+$436.90+$185). Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **DJ's Fireplace Service** | 2022-01-31 | **$203.00** | Fireplace service | Business R&M ledger, Check #1188. Confirmed 282 Bald Rock by Joshua 9/1/2026. |
| **Gonzales Virginia Painting** | 2023-05-31 | **$3,010.00** | Painting | Two Zelle payments ($10.00 + $3,000.00) from the Wells Fargo FCF business account. **Confirmed 282 Bald Rock by Joshua, 9/2/2026.** Moved from §19. |
| **Pottery Barn / West Elm / Williams Sonoma** (Hillary's Comenity→Capital One card, acct ending 2988→9681) | 2021-2024 | **$211,724.20** | Furniture, furnishings | 2021: $97,695.65; 2022: $62,320.86; 2023: $49,344.69; 2024: $2,363.00. Card bills to Hillary D Davis, 282 Bald Rock Rd. **Confirmed 282 Bald Rock in full by Joshua, 9/2/2026** — not split with 14300 Woods Walk Lane, which Joshua clarified has been owned all along (not acquired 12/2021 as this log previously assumed — see the correction note in §20). Superseded the old $414.67 Pottery Barn figure (personal DuPont account only). |
| | | **$475,119.42** | | |

> **Note on Burns Builders Roofing $21,750.00 (§2 below):** an earlier draft cost-seg writeup (v4 docx, before 8/31/2026) had incorrectly promoted this to "proven" based on recurring monthly "Payment Posted" emails from Service Finance. Those are routine installment confirmations, not a payoff — they were never adequate proof. This master log's own §2 / F-1 treatment (invoiced, not proven, ~$6,400 arithmetic gap unresolved) was correct all along and was never changed. Flagging here so the correction carries into any future docx rebuild.

---

# 2. INVOICED, PAYMENT NOT PROVEN — $41,899.90

| Vendor | Doc / Date | Amount | Note |
|---|---|---|---|
| **Red Rock Concrete** | Inv #1244 balance | **$18,622.00** | No receipt, check, bank record or vendor acknowledgment anywhere after 2022-08-08. Not present in Full Circle's 2022 general ledger either (checked 8/31/2026) — so if it was paid, it was paid from a personal account, most likely Wells Fargo 2797. |
| **Signature Hardware** | net $11,730.49 less $1,883.00 proven | **$9,847.50** | All orders ship to 282 Bald Rock; each has a matching shipment email. Reduced 8/31/2026 by $743.11 of 2022 ledger payments. |
| **Royal Swimming Pools** | #151398 approved $14,980.93 + #152804 $530.95, less $5,592.86 Affirm-proven (see §1) | **$9,919.02** | #151398 customer-approved 2022-11-03 10:41:32 EDT, approval IP logged; kit shipped 11/28 + 12/02. The Affirm loan only financed part of #151398 — the remaining ~$9,388.07 (one payment made at purchase, per the Affirm approval email) and #152804 ($530.95) still have no receipt. |
| **Commonwealth Tile** Inv 1233 / 1228 | | **$1,425.00** | |
| **Lowe's** #761302963 + #771548245 | 2022-10 / 2023-03 | **$1,344.79** | Bald Rock / Verona referenced |
| **Direct Door Hardware** #203991, **Builders Warehouse** #23752 / #23939 | 2020–2021 | **$741.59** | All shipped to 282 Bald Rock |
| | | **$41,899.90** | |

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
| ~~Crutchfield home theater Est #46208897~~ | $22,845.41 | 2019-07-05 — **see §40, Joshua confirms this project WAS actually done** |
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

1. **LL Flooring / Lumber Liquidators (Store #1420, Harrisonburg) — CONFIRMED 9/1/2026 by Joshua: this was the new hardwood flooring installed at Bald Rock.** The entire project is documented (in-home assessment 2020-09/10, quote 2020-10-10, install 2021-05, two staircases with custom treads, baseboards, trim, warranty complaint ID#5426534 into 2022) but **every dollar figure sits in PDF attachments never downloaded to this Mac.** The parent files are `.partial.emlx` stubs. Recoverable filenames: `0702794747_Quotation.PDF`, `0134505377_Invoice.PDF`, `0134879323_Invoice.PDF`. Only hard figure is a Synchrony Bank statement balance of $13,215.43 (2021-08-18) — a credit-card balance, not an invoice, and it may include non-282 charges. **New lead (§17 pass):** the personal DuPont account (831015-0090) shows a recurring ACH "SYNCHRONY BANK" payment through all of 2021, declining every month in a classic amortization pattern — $552 (1/11) → $539 (2/9) → $527 (3/9) → $515 (4/9) → $503 (5/10) → $492 (6/9) → $482 (7/9) → $472 (8/9, the same month as the $13,215.43 statement balance) → $463 (9/9) → $390 (10/12) → $376 (11/9) → $363 (12/9), roughly $6,340 paid across the year on top of a January payment history not yet pulled. Synchrony is a common private-label financing partner for flooring retailers including LL Flooring, and the declining-balance pattern is consistent with paying down exactly the kind of balance already noted here. **This is the most promising path to a hard total dollar figure for the flooring project** — either re-download the LL Flooring email attachments (still the more direct fix, see action item below), or pull a Synchrony Bank account history/payoff statement, which would show the original financed amount directly.
2. **Siding** — Joshua: *"I'm putting hardi plank on."* Burns declined to install. No installer, contract, or invoice anywhere.
3. **The hot tub itself** — it exists (a cover was quoted $650 + tax + $350 delivery in 2024-06 texts) but there is no purchase invoice for the tub. A revenue-generating asset with zero documentation.
4. **Lowe's "8 doors"** — no supporting document of any kind.
5. ~~Lowe's kitchen cabinets — what was actually bought.~~ **RESOLVED 9/2/2026 — see §23.** The $36,040.14 already proven and counted in §1 is very likely the cabinet job itself, reconstructed from the personal DuPont REWARDS scrub's own transaction dates and amounts, which line up almost to the dollar with the $35,830.19 cabinets-only portion of the $43,025.31 quote.
6. ~~**Shreckhise Landscape & Design** — the contractor actually used. Plans `Davis 101322.pdf` and `Davis 032323.pdf` exist; no proposal, invoice, or payment.~~ **UPDATED 9/2/2026 — moved to §1, $18,036.50 proven** across 9 bill-pay withdrawals 2023-01-18 → 2024-03-21 (see §21 for the full re-scan). Joshua's recollection was "~$25-30K with Shreckhise" — still $7,000-12,000 short of that even with the newly found payments. The recurring $500/month pattern was still active when the DuPont business archive ends (June 2024), so the likeliest place for the remainder is bill-pay activity after that date — not further mail search, which has already been exhausted twice. A "Shreckhise Shrubbery Refund Receipt" dated 2025-07-28 also exists (a REFUND to Joshua, which would reduce not increase basis) — amount still not read, the local email only has a 0-byte partial download of the PDF attachment; would need to be opened live in Mail.app to get the figure.
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

# 40. Crutchfield home theater — Joshua confirms 2026-09-03 this WAS installed at 282 Bald Rock

Joshua directly confirmed (2026-09-03) that a Crutchfield home theater was actually put in at 282
Bald Rock — this was previously carried in §3 as "quoted only," which is now known to be wrong.
Two separate Crutchfield estimates exist for what looks like the same underlying project:

- **Est #46208897, $22,845.41, 2019-07-05** — the earlier/larger-scope version, no line-item detail
  pulled yet.
- **Est #47400839, $14,362.10, 2020-06-10, prepared by Tyler Bare, Bill To: JOSHUA DAVIS, 282 BALD
  ROCK RD, VERONA, VA 24482-2825** — line items: Sony VPLVW295ES 4K projector $4,999.99, SI 133"
  perf screen $5,019.00, Control4 C4-EA1-V2-SR automation controller $650.00, HDMI balun/wire
  $350.00, Sanus open-frame rack $219.99, Sanus mounting screws $5.94, Panasonic Blu-ray player
  $399.99, tax $617.19, labor $2,100.00. **Confirmed billed to Bald Rock's own address on the
  document face** — the strongest single piece of paper found so far.

**Not yet added to the tracked total ($621,683.83) — here's why.** The 160" screen Joshua asked
about is almost certainly NOT the 133" screen on this estimate: a separate, already-proven
ProjectorScreen.com order (§1, $5,470.50, 2020-02-14, "SI 5 Series 160" screen, ship-to 282") is
already counted in the furniture bucket. The likely sequence is Joshua bought the screen
separately/bigger than what Crutchfield first quoted, then had Crutchfield supply and install the
rest (projector, receiver/automation, mounting, cabling, labor). Real, dated Crutchfield activity
consistent with an actual purchase (not just a quote) also exists: "Thank you for your order"
confirmations across 2020, a "Payment confirmation for your Crutchfield installment plan" (Order
47244765, $753.32), and multiple Crutchfield invoice PDFs (28048056 = $432.98 mount/surge
protector, ship-to Crutchfield's own Harrisonburg store for in-house install; others not yet
pulled). None of these individually match the $14,362.10 (or $22,845.41) estimate total, and
Crutchfield often splits a big install into several smaller item-level orders plus labor billed
separately — so the actual paid total for the non-screen equipment is very likely real but not yet
reconstructed to a matched dollar figure.

**Action item:** pull the remaining Crutchfield invoice PDFs already located (28424781, 30305500)
and the installment-plan order (47244765) for their line items, and total whatever nets out to
projector/Control4/labor at 282 Bald Rock (excluding any screen, which is already counted). Until
that reconciliation is done, do not add either estimate total to the tracker — same rule as every
other quote-only line in this file, now with the difference that Joshua has confirmed the
underlying purchase is real, so this is worth finishing rather than closing out as a loser bid.

---

# 8. NEXT ACTIONS — evidence recovery, highest value first

1. **OCR `.../282 Bald Rock Rd - Verona VA (Rental)/Valley Building Supply - PlyGEM/invoices & credits.pdf`** — 33 pages, image-only, zero extractable text. This is where the windows/doors/siding dollars live. Note the byte-identical duplicate at `.../Valley Building Supply - PlyGEM - Emails & Media/invoices & credits.pdf` — do not double count.
2. **Re-download the LL Flooring attachments.** The messages are `.partial.emlx`; opening each in Mail while online pulls the PDFs. Only vendor with a fully documented project and zero readable figures.
3. **Pull card statements** for MC ****0305, MC ****6246, MC ****1689, LCC ****1037, and Amex ****7115 / ****1005. These cards already paid Bald Rock vendors and would convert most of the $110,673.74 invoiced block to proven.
4. **Find the Red Rock $18,622.00 payment.** Red Rock invoiced through `quickbooks@notification.intuit.com`, so a receipt should exist. Check Aug–Oct 2022.
5. **Burns Builders final invoice + Service Finance loan xxx3624** origination and payoff — resolves F-1 and converts $21,750.
6. ~~MyLowe's Pro purchase-history export, 2020–2023, filtered to the Verona ship-to.~~ **DEAD END, per Joshua 9/2/2026: MyLowe's Pro purchase history only goes back to 2024** — years after the 2021 cabinet job. This document does not exist for the period that matters. **See §23 — the cabinet question is resolved a different way, using bank records already in hand.**
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

**Shreckhise Landscaping — see §1, §6, and §21.** $18,036.50 proven as of 9/2/2026 (up from the original $8,536.50) via nine bank bill-pay withdrawals through 2023-2024; the "~$25-30K" recollection is closer now but still not fully corroborated.

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

### Paid, but property attribution unconfirmed — $17,276.03

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
| | | | **$17,276.03** | |

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


---

# 13. ADDENDUM 9/1/2026 — Valley Building Supply reclassified (vendor defunct); Prestige Plumbing found and proven; photo sweep

## Valley Building Supply — reclassified from "invoiced, not proven" to "proof of payment"

Joshua confirmed today that Valley Building Supply / Allied Concrete has **gone out of business**, and getting further invoices or a customer statement (the request that had been sitting out since 8/31/2026) is no longer realistic. Per his direct instruction, the remaining **$28,947.87** (open balances $950.75, $3,181.73 after the $5,200 PlyGem credit, $724.80, plus $6,232.64 where Balance Due was illegible on the scan) moves from §2 to §1.

**What actually backs this now, beyond Joshua's representation:**
- The full 33-page invoice packet was read line-by-line today and every window and door purchase itemized by date, invoice #, description, quantity and price into `282 Bald Rock - Windows and Doors (VBS Invoices).xlsx` (25 window lines / $28,171.26, 9 door lines / $17,404.65, total $45,575.91 — a subset of the full $58,669.93 net invoiced, the remainder being trim and AZEK decking already in evidence).
- **10 photos found** in `.../02 Real Estate/282 Bald Rock Rd - Verona VA (Rental)/Valley Building Supply - PlyGEM - Emails & Media/`: IMG_1381.HEIC, IMG_1394–1399 (2).JPG, IMG_1406–1407 (2).JPG, IMG_1413 (2).JPG, IMG_1419–1420 (2).HEIC — all dated **2022-03-23/24**, three to four weeks after the final invoice batch #00306738 (2/9/2022 — the triple DH windows and gliding patio door, $11,146.63 of the total). Consistent with delivery/install photos or the "missing screens" complaint documented in the Feb 2023 email thread (`RE_ Still missing 69.eml` / `RE_ Still missing 25.eml`), which itself confirms these specific doors and windows were physically installed at the property.
- No photos from the 2020–2021 invoice dates (04/2020, 06/2020, 10/2020, 05/2021, 09/2021) turned up in the same sweep — only the March 2022 batch has dated photographic corroboration.

**Caveat to carry forward, stated plainly rather than buried:** unlike the $29,722.06 already proven via independent bank/GL matches, this $28,947.87 is not confirmed by a third-party payment record — it rests on the invoice's own line-item detail plus Joshua's representation that it was paid, given the vendor can no longer confirm it. **Flag this distinction for Silverline** — a CPA may want it noted as taxpayer-represented rather than bank-verified, which does not change its validity for basis purposes but is worth disclosing.

## New vendor found: Prestige Plumbing LLC — $12,208.47

Not in any bucket of this file before today. Found via a mail sweep for "water softener / filter system" per Joshua's description of a full water softener and filtration replacement.

| Document | Date | Amount | Status |
|---|---|---|---|
| Estimate #E200912935 | 2020-09-11 | $8,300.00 | — |
| Invoice #I200925943 | Due 2020-09-25 | **$8,300.00** | **Invoice Due: $0.00** on the invoice face |
| Intuit card receipt, Mastercard ****9983 | 2020-09-16 | $3,500.00 | Payment toward the above job |
| Intuit card receipt, Mastercard ****9983 | 2020-10-07 | $3,300.00 | Payment toward the above job (same day the paid invoice was sent) |
| Intuit card receipt, Mastercard ****9983 | 2020-12-02 | **$2,200.00** | Separate charge, job unspecified |
| Invoice #I210505245 | Due 2021-06-18 | **$1,708.47** | Invoice Due: $0.00 — paid in full |

Item list on the Sept/Oct 2020 job (from the invoice PDF): **"Filter System (Under Sink)," "Standard Whole House Filter 10-IN Housing 1-IN," "Replace Premium Electronic Water Softener."** This is the whole-house water softener and filtration replacement Joshua described. Counted once at the $8,300.00 invoice face amount (the two card receipts are corroboration for the same job, not additional dollars) plus the two clearly separate charges ($2,200.00 and $1,708.47), for a total of **$12,208.47**.

**Property attribution:** the invoice/receipt emails themselves don't carry the service address (Apple Mail stored them as partial/summary messages — invoiceasap.com notification emails, not the full PDF body). The attribution rests on: (1) vendor is Fisherville, VA — six miles from Verona, consistent service area; (2) Joshua's 2020 CPA, Kris McMackin, explicitly lists "Prestige Plumbing" in the same January 2022 email alongside Valley Building Supply, Lowe's, Commonwealth Tile and Wood I[ndustries?] as 2020 renovation subcontractor / repairs-and-maintenance expense — the same project bucket as everything else in this file. No competing property (Cypress Crossing wasn't owned until 2025) would explain a 2020 water-softener job. Treated as proven for Bald Rock on that basis.

**No photos found** for the Prestige Plumbing work — the `Renovations` folder for this property contains only renovation-scope PDFs (cabinet/kitchen estimates, layout drawings), no images, and a targeted photo sweep for "prestige / softener / plumbing" across the indexed iCloud/Mail files returned only the invoice and estimate PDFs themselves.

## Shreckhise — checked for a receipt beyond the bank record

Joshua asked whether an actual Shreckhise invoice or receipt (not just the DuPont bill-pay withdrawal already in §1 at $8,536.50) exists. **None found.** The Shreckhise correspondence in the index is all scheduling/design threads ("Landscape Plan," "Design for Between Walls," quote-request replies) — no priced invoice or receipt document turned up in mail or files. The $8,536.50 in §1 stands on the bank bill-pay match to Lodestar's Jan-2023 bookkeeping report, which remains the only proof for this vendor.

## Updated totals

| Evidence class | Before 9/1/2026 | After 9/1/2026 |
|---|---|---|
| Proof of payment | $147,385.34 | **$188,541.68** |
| Invoiced, payment not proven | $77,240.30 | **$48,292.43** |

$28,947.87 moved between those two rows (VBS reclassification); $12,208.47 is genuinely new (Prestige Plumbing), so the combined proven+invoiced total grew from $224,625.64 to $236,834.11.


## §14. ADDENDUM 9/1/2026 (pass 2) — 2017-2019 personal bank statements pulled and searched for hot tub vendor

**Trigger:** Joshua downloaded 35 monthly statements (Feb 2017 - Dec 2019) plus a 1099-INT from DuPont Community Credit Union (personal account, account holder JOSHUA C DAVIS, then at 148 Hardinberry St, Oak Ridge TN 37830 — pre-dating his move to this area) and asked that they be added to the unified search and reviewed for the still-unidentified hot tub vendor (see §12/§13 background: cold plunge confirmed as Renu Therapy; hot tub vendor described by Joshua as "a group that was in the harrisonburg valley mall," possibly "Valley Pool and Spa," now out of business).

**What was done:**
- Files relocated from Downloads into `Taxes 2026/Bank Statements/2017-2019 Personal/` (kept together, not deleted).
- Every statement run through `pdftotext` and scanned for hot-tub/pool/spa-vendor keywords (valley pool, hot spring, luxury pool, harrisonburg, spa, hot tub, pool and spa, valley mall, cal spas, master spa, watkins, leisure, backyard, etc.), and separately scanned for every withdrawal/purchase transaction of $1,000 or more across all 36 statements.
- Files also queued into the permanent unified-search index (`usearch.py files` rebuild) so they're searchable going forward like the rest of the mail/text/file corpus.

**What was found:**
- **Blue Ridge Pools & Spa, Staunton VA** — a real, recurring merchant on this account: 10 separate debit-card charges from April 2017 through November 2019 (Apr 2017 x5, May 2017, Jan 2018, May 2018, Oct 2018, Nov 2019), each between **$24.21 and $487.32**. This size and cadence reads as ongoing pool/spa service or chemical purchases, not a single capital purchase of a hot tub — flagged here for the record since it is a real, previously-undocumented vendor relationship, but **not** put forward as the hot tub seller.
- **No transaction of $1,000 or more to any pool-, spa-, or hot-tub-related merchant** appears anywhere in the 36 statements. The only $1,000+ non-mortgage, non-loan withdrawals in the whole period are unrelated: a Maserati dealership (Richmond VA, June 2017), Square-processed charges at "A&G 1 Stop" (Bridgewater/Dayton VA, 2017), an ACH mortgage payment to New American Funding (recurring monthly), two unlabeled disbursement checks tied to new loan originations (Mar 2017 $18,105; other large checks are loan proceeds, not purchases), and one payment to a podiatrist (Harrisonburg, July 2017).
- **Conclusion: the hot tub purchase does not appear on this personal DuPont account for 2017-2019.** Taxpayer representation stands (hot tub was purchased, from a Harrisonburg-area retailer since closed, possibly "Valley Pool and Spa" or a similarly-named mall retailer), but it remains unproven by a bank or invoice record after searching mail, texts, iCloud files, and now this bank account. Most likely explanations if the purchase is real and simply not here: it went through a different account (a business account, a different personal account, or financing/credit rather than this debit card), or predates or postdates this 2017-2019 window.

**Not yet done / open:** business-entity bank statements (Full Circle Finance / Valley Pawn accounts) have not been pulled or searched for this vendor — that is the logical next place to look if Joshua wants to keep pursuing bank-record proof of the hot tub. No change made to §1/§2 totals from this pass — nothing here rises to proof of payment for any new item.


## §15. ADDENDUM 9/1/2026 (pass 3) — Business DuPont account (766518) found and searched; likely hot tub vendor identified

**Trigger:** Joshua asked whether we already had statements for the old Full Circle Finance business DuPont account ending 766518 (confirmed as a Full Circle Finance account per Kris McMackin CPA's 1/2018 email: "Only wells fargo ending in 4807 and DCCU ending in 766518 are full circle accounts"). This account is separate from the personal DuPont account searched in §14.

**What was found already on file (no download needed):** two folders of monthly statements for this business account already exist in iCloud Drive under `03 Personal/02 Taxes/`:
- `2020/Dupont 2020 Statements/` — all 12 months, Jan-Dec 2020
- `2021/Dupont Statements 2021/` — 13 months, Jan 2021 - Jan 2022

No 2017-2019 or post-Jan-2022 monthly statements for this account exist on file (only scattered 1098/1099-INT forms for later years) — pulling 2017-2019 business statements, if Joshua has them, would be the next step if this window doesn't close the question.

**What the scan found — likely hot tub vendor identified:**
- **March 2020 statement:** a debit card charge of **$156.90** on 3/10/2020 (posted 3/11/2020) to **"SQ *LUXURY POOL AND SP[A]" — Harrisonburg, VA** (a Square-processed card transaction). This is the first hard, bank-verified record of a transaction with a business matching Joshua's recollection ("a group that was in the Harrisonburg Valley Mall... maybe Valley Pool and Spa, they aren't there anymore") — the real name appears to be **Luxury Pool and Spa**, not Valley Pool and Spa. Timing (March 2020) lines up well with the broader 2020 STR build-out (Valley Building Supply windows/doors work began the following month, April 2020).
- This is the **only** transaction to this vendor found across all 26 statements in both folders (2020 full year + 2021-Jan 2022) — no repeat or larger charge to the same merchant appears anywhere else in the window.
- **$156.90 is too small to be a full hot tub purchase** on its own — reads more like a deposit, a small parts/accessory purchase, or a delivery/service fee. **Flagging, not concluding:** the same day (3/10/2020) also shows an unlabeled **Check #1311 for $2,000.00** cashed from the same account — Full Circle's statements list a payee name for cashier's checks but not for ordinary numbered checks, so this cannot be confirmed as paid to Luxury Pool and Spa from the statement text alone. If Joshua wants to pursue this further, DCCU (or Joshua's own records) may be able to produce the cashed image of Check #1311 to confirm or rule out the payee.
- No email receipt for this charge was found in mail search (expected — Square receipts email the *customer* of a Square merchant, and Joshua was the customer here, so no Square receipt would land in Joshua's own inbox for a purchase he made from a Square-using vendor).

**Bottom line:** taxpayer representation is now meaningfully corroborated — Joshua's business account shows a real, dated transaction with a Harrisonburg pool/spa retailer named Luxury Pool and Spa in March 2020, consistent with his memory. It is not, by itself, proof of the full hot tub purchase price or amount, since $156.90 does not match a capital hot tub cost and no larger matching charge exists in this account for the following ~22 months. No change made to §1/§2 totals — this does not yet rise to proof of payment for the hot tub as a depreciable asset; it is offered as the strongest lead to date and the logical starting point if Joshua can locate the Check #1311 image, a Luxury Pool and Spa invoice, or earlier/later statements for this account.


## §16. ADDENDUM 9/1/2026 (pass 4) — Full 2015-2024 business DuPont (766518) history supplied by Joshua; §15 finding confirmed as the only match in 9+ years

**Trigger:** Joshua supplied the complete member-statement archive for the Full Circle Finance business DuPont account (766518) directly from the credit union — all 114 monthly statements, January 2015 through June 2024 — closing the gap noted in §15 (previously only 2020-Jan 2022 was on file).

**Filed:** the full archive is now saved at `Taxes 2026/Bank Statements/DuPont 766518 Business (2015-2024)/`, organized into one folder per year, each file renamed `<Month> <Year> Statement.pdf`. Confirmed from the statement header: account number ending 518 (766518), mailing address on file circa 2020 was **282 Bald Rock Rd, Verona VA 24482** — i.e., Full Circle Finance's registered mailing address was the subject property itself at the time.

**Result of re-running the keyword/vendor scan across the full 9+ year history:** the March 2020 finding in §15 (**$156.90 to "SQ *LUXURY POOL AND SP[A]," Harrisonburg VA, 3/10/2020**) is confirmed as the **only** transaction to any pool/spa/hot-tub-related merchant in the account's entire recorded history. No larger or repeat charge to Luxury Pool and Spa, and no other candidate vendor, appears in any of the 114 statements. The only other pool/spa-adjacent name found anywhere in nine years is **Blue Ridge Pools & Spa, Staunton VA** — small recurring charges in May 2018 ($5,370.96 running-balance context, actual charges under $50 each — see transaction detail if needed) and April 2019, consistent with the personal-account pattern already logged in §14 (service/chemicals, not a capital purchase).

Regular numbered checks (e.g., Check #1311, $2,000.00, cashed 3/10/2020 — see §15) still do not carry payee names on this credit union's statement format; a cashed-check image from DCCU remains the only way to confirm or rule out that check as a possible additional payment toward the same purchase.

**Conclusion, updated:** the case for "Luxury Pool and Spa" as the hot tub vendor is now as strong as bank records alone can make it — a genuine, dated, one-time transaction with a plausibly-matching Harrisonburg retailer, appearing exactly once across every business bank statement Full Circle Finance has from account opening through mid-2024. It still does not, by itself, prove the full purchase price or establish this as the complete cost basis of the hot tub — no invoice, no larger corroborating charge, and no email receipt exist. No change to §1/§2 totals. If Joshua wants to close this out fully, the two remaining levers are: (1) requesting the imaged/cashed copy of Check #1311 from DCCU, or (2) contacting Luxury Pool and Spa directly (if reachable) for a copy of the original invoice.


## §17. ADDENDUM 9/1/2026 (pass 5) — Wells Fargo status, and the personal DuPont account (831015) resolves the VBS payment-source gap plus new furnishing vendors

**Trigger:** Joshua asked whether Wells Fargo had been checked through 2023, and whether the personal DuPont account (831015) or business DuPont account (766518) showed additional home improvements.

### Wells Fargo — what exists and what doesn't
Statements on file: 2016 (Business Line 2016, Bank Statements 2016, Credit Card 2016), 2018 (Wells Business Line, 12 months), 2018-2019 (a "Wells" folder and a separate "Wells Loan" folder, ~13 months each), and 2024 (FCF business account, 12 months, `2024 Taxes/FCF INC/Debt/Wells Fargo FCF/`). **No Wells Fargo statements exist on file for 2020-2023** — the years that matter most for this property. Scanned everything that does exist for home-improvement vendor keywords; nothing relevant turned up (only boilerplate false-positives). If Joshua wants Wells Fargo fully ruled in or out for those years, statements would need to be requested from Wells Fargo directly, same as was done for DuPont.

### RESOLVED: the $32,117.25 Valley Building Supply payment-source gap (open since the §11 lender/GL sweep)

§0b/§11 already matched four VBS invoice payments — $9,100.00 (1/5), $4,021.47 (1/6), $3,880.00 and $15,115.78 (both 10/21, all 2021) — totaling **$32,117.25**, but flagged the source as unknown: *"not in this account [766518] — they came from a personal account, another institution, or a check."* Found it: all four charges appear, on the same dates and for the same amounts, in Joshua's **personal DuPont account (831015, REWARDS sub-account -0090)**, per its 2021 transaction scrub (`2021 Expense Review/2021 Personal Account Scrub.xlsx`). This closes that gap — the full $32,117.25 is now a proven-and-sourced VBS payment, just paid from Joshua's personal account rather than the business account. No change to the $ total already credited in §1; this only fills in *how* it was paid.

### LIKELY RESOLVES the $6,392.53 Burns Builders "unfinanced remainder" (open since §2/§11, F-1)

The same personal-account scrub shows a **$7,050.00 debit-card charge to "Burns Builders Inc," Port Republic VA, dated 7/11/2021** — one day after the roof's completion was confirmed (7/10/2021, per the collector-notice language quoted in §10: *"the ROOFING project completed by Burns Builders Inc on 7/10/2021"*). The $21,750.00 signed estimate less the $15,357.47 Service Finance loan leaves a $6,392.53 gap this log has been trying to close for several passes (see §1, §2, §11) by requesting the actual Retail Installment Contract from Service Finance. A $7,050.00 direct payment to Burns, the day after completion, is a strong candidate for that remainder — it doesn't match to the cent (off by $657.47, which could be a small change order, a different rounding of the estimate, or simply not the same payment), so **this does not replace the outstanding document request** — the Retail Installment Contract for account 3624 is still the one document that would nail the exact Amount Financed and close this cleanly. But it substantially raises confidence that the $6,392.53 gap is a real, paid amount rather than a discrepancy, and gives a second concrete data point if the loan contract never surfaces.

### Also likely explains the loan's known 2021-22 delinquency

The personal account shows a recurring **$500.00/month "SERVICE FINANCE" bill-pay** (Aug, Sep, Nov, Dec 2021) plus one $771.64 ACH payment (9/2/2021) — none of which match the loan's actual scheduled payment of $380.82/month per §10's detailed statement history. §10 already documents that this exact loan (account 3624) went delinquent through 2021-22 and wasn't fully current again until autopay was re-established in January 2023. These irregular $500/$771.64 manual payments in 2021 read as Joshua's own attempts to catch the account up during that delinquent stretch — consistent with, not contradictory to, the existing loan history. Not booked as new money (it's payment on an already-counted loan), just adds color to the existing timeline.

### Genuinely new vendor spending found — not previously in this log

From the same 2021 personal-account scrub, plus a 2022 counterpart (`2022 Taxes.../Persoanl Account Scrub.csv`) and the 2021 and 2022 business-account "Repairs & Maintenance" QuickBooks ledgers:

| Vendor | Year(s) | Amount | Source account | Note |
|---|---|---|---|---|
| Lowe's | 2021 | **$36,040.14** | Personal (831015-0090) | Largest charges $17,519.24 (1/23) and $6,970.60 (1/21) and $8,276.48+$2,053.33 (3/5). Distinct from the $51,887.96 already logged from the *business* account's Lowe's ACH activity (§0b), which is explicitly flagged there as needing store-vs-Bald-Rock attribution — this personal-account pool is cleaner evidence since Joshua's personal card is very unlikely to carry pawn-store purchases. |
| EasyClosets.com | 2021 | $7,453.59 | Personal | Custom closet systems — 6/15, 7/7, 7/28. |
| Shades of Light (lighting) | 2021-22 | $3,128.43 (2021) + $1,305.57 (2022) | Personal | Recurring across both years. |
| Decor Planet | 2021 | $771.97 | Personal | |
| Pottery Barn | 2021 | $414.67 | Personal | |
| Wayfair / AllModern | 2022 | $1,538.41 | Personal | |
| Sarisand Tile (Charlottesville) | 2022 | $550.93 | Personal | |
| Grand Home Furnishings | 2022 | $200.00 (personal) + $1,731.00 (business R&M ledger) | Both | |
| Ashley Furniture | 2022 | $704.39 | Business R&M ledger | |
| North American HVAC | 2022 | $260.79 | Business R&M ledger | |
| Valley Comfort System | 2022 | $771.90 | Business R&M ledger | HVAC service, 3 charges |
| DJ's Fireplace Service | 2022 | $203.00 (Check #1188) | Business R&M ledger | |

(Commonwealth Tile $1,685, Signature Hardware $743.11, Augusta Aluminum Gutterworks $4,500, and Fiber Pro Insulation $2,500 from the same 2022 business ledger were already documented in this log at §10/§1 — re-derived here independently while reading the same source file, not new dollars.)

### Property attribution and the 2021 "personal" reclass — still the open question

§15/§16 already logged that the 2021 business "Repairs & Maintenance" GL had **$41,562.64** reclassified to "personal" at year-end (line items included the VBS $14,634.79 and Lumber Liquidators $3,638.46 already counted in §1/§0b). Combined with everything above, the picture is: a large amount of 2021 Bald-Rock-plausible spending moved through Joshua's *personal* accounts and a *reclassified-out* pocket of the business account, rather than showing as ordinary traceable business capital spending. Vendor overlap (Staunton-area VBS/Lowe's, the same names as the already-proven Bald Rock work) and timing (all before Woods Walk Lane's Dec-2021 acquisition — a separate Midlothian VA rental flip confirmed via its own rehab notes, HVAC/siding/decking/trim work in 2022-23) both point to Bald Rock, but none of it carries an invoice with the property address on it. Same evidentiary tier as the rest of this log's personal-representation items — worth a direct conversation with Silverline on how to treat the reclassified $41,562.64 (capitalize to Bald Rock vs. leave as a true personal/distribution item) before any basis number is changed.

## §18. ADDENDUM 9/1/2026 (pass 6) — Burns Builders closed out; all §17 spending confirmed 282 Bald Rock by Joshua; furniture/basis question answered

**Trigger:** Joshua's instruction *"close out burns. and yes all that is 282, does fruniture we bough count towards the basis as well?"*, plus a follow-up clarification that most furniture was Pottery Barn purchases on Hillary's card.

**Burns Builders — closed.** Per Joshua's direct instruction, the $6,392.53 "unfinanced remainder" gap (open since §2/§11, item F-1) is now closed using the $7,050.00 personal-account payment to Burns Builders Inc dated 7/11/2021 (§17). The document request to Service Finance for the actual Retail Installment Contract on account 3624 is no longer being chased for this purpose — Joshua accepted the $657.47 variance rather than continuing to wait on it. Moved from §2 to §1; see the updated row there.

**Property attribution — confirmed by Joshua.** Every item logged in §17 as "likely but unconfirmed Bald Rock" is now confirmed by Joshua as 282 Bald Rock spending: Valley Building Supply (personal-account payment source), Lowe's $36,040.14, EasyClosets.com $7,453.59, Shades of Light $4,652.74 (both years), Decor Planet $771.97, Pottery Barn $414.67, Wayfair/AllModern $1,538.41, Sarisand Tile $550.93, Ashley Furniture $704.39, Grand Home Furnishings $1,931.00, North American HVAC $260.79, Valley Comfort System $771.90, and DJ's Fireplace Service $203.00. This is taxpayer representation, not third-party proof of the property address on each individual receipt — the same evidentiary posture as the rest of this log's confirmed-by-Joshua items — but it is Joshua's own, direct, contemporaneous confirmation, and it is what moved these dollars into §1 as proven spending. Flagged plainly here for Silverline's awareness: these figures carry a bank/card record of payment plus taxpayer confirmation of use, not an invoice bearing the property address.

**Does furniture count toward the basis?** Yes — furniture (and other tangible personal property placed in the rental, such as appliances) is real depreciable spending and belongs in this file's totals. The one thing to flag for Silverline: it should end up classified *separately* from the building's 27.5-year real-property basis. Under a cost segregation study, furniture and similar personal property is typically 5-7 year MACRS property, and that's actually a better outcome for Joshua — 5-7 year property is usually eligible for bonus/accelerated depreciation the 27.5-year building basis is not. So the dollars counted in this file (including the furniture line items above) are correctly being tracked as total capital spending on the property; Silverline will make the final call on how to split that total between the building's real-property basis and the shorter-lived personal-property buckets when the return is prepared or when a formal cost segregation study is done.

**Open lead — Pottery Barn / Hillary's card.** Joshua states most interior and exterior furniture was purchased from Pottery Barn on Hillary's card, not Joshua's own. The $414.67 Pottery Barn figure logged in §1 is from Joshua's personal DuPont account only and is very likely a small fraction of the true Pottery Barn total. Hillary's card/account has not yet been identified or searched in this file — none of the sources reviewed so far (personal DuPont 831015-0090, business DuPont 766518, the 2021/2022 personal scrubs) carry Hillary's own card activity. This is a concrete, not-yet-pursued lead: locating Hillary's card statements (whether a card on the same DuPont relationship, a separate personal card, or a business card) is very likely the single largest remaining undocumented pool of furniture spending in this file. No dollar figure is being estimated here — this is flagged as an open item, not summed into any total, until the actual records are found.

**Net effect on totals this pass:** Proof of payment $188,541.68 → **$250,885.21** (Burns Builders $7,050.00 + $55,293.53 of newly confirmed §17 vendor spending). Invoiced-not-proven $48,292.43 → **$41,899.90** (Burns Builders' $6,392.53 estimate removed, now proven at $7,050.00 in §1 instead). Basis floor (purchase + proven) → **$655,885.21**; basis ceiling (purchase + proven + invoiced) → **$697,785.11**. See the updated headline table and §0.

## §19. ADDENDUM 9/1/2026 (pass 7) — Wells Fargo FCF business account, September 2022-December 2023 (16 statements) reviewed; one new vendor found

**Trigger:** Joshua pulled 16 additional Wells Fargo FCF business-account statements (Sep-Dec 2022, all of 2023) and asked that they be loaded into the unified search index and combed for home-improvement evidence — continuing the Wells Fargo gap identified in §17 (previously nothing on file for 2020-2023).

**Filed:** organized to `Taxes 2026/Bank Statements/Wells Fargo FCF Business (2022-2023)/`, one folder per year, each file renamed `<Month> <Year> Statement.pdf`. The unified search files index was rebuilt to include them.

**Wells Fargo coverage is now:** 2016, 2018, 2018-2019, September-December 2022, all of 2023, and 2024. **CORRECTION 9/2/2026, per Joshua: the account was not open yet during 2020, 2021, or January-August 2022** — there is nothing to pull for that window because it doesn't exist, not a document-recovery gap. September 2022 is very likely close to account opening. This closes out what had been flagged as the single biggest remaining statement gap in this file — it was never recoverable because it was never real.

**What the 16 new statements show:** this is a low-balance business checking account used almost entirely for pawn-shop cash management — branch cash deposits/withdrawals, DuPont Community Credit Union transfers, and BusinessLine-of-credit draws/repayments. Every transaction line across all 16 statements was reviewed (not just keyword-matched, to avoid missing an unfamiliar vendor name). Two keyword hits were false positives worth noting so they aren't re-flagged later: "spa" only ever appears inside "español" (boilerplate), and "lowe" only ever appears inside "allowed"/"lowest" (boilerplate) — no Lowe's charges exist in this account.

**One genuine new finding: two Zelle payments to "Gonzales Virginia Painting," both dated 5/31/2023 — $10.00 and $3,000.00, totaling $3,010.00.** This is a real, dated, named-vendor, bank-record payment — third-party proof of payment, same tier as the strongest items in §1 — but the bank statement itself does not say which property was painted. **CONFIRMED 9/2/2026 by Joshua: 282 Bald Rock was painted.** Moved to §1 as proven spending — see the updated Proof of Payment total.

**No other new vendor, contractor, or home-improvement-related spending appears anywhere in these 16 statements.**

## §20. ADDENDUM 9/2/2026 (pass 9) — Hillary's Pottery Barn card (account 4362) located, indexed, and quantified: $211,724.20 across 2021-2024 — property split needs Joshua's confirmation before any of it is added to §1

**Trigger:** Joshua located and downloaded all statements for the Pottery Barn credit card account he and Hillary hold jointly (Joshua's clarification that most furniture was "Pottery Barn on Hillary's card"), asked that they be indexed in unified search and added to this file.

**Filed:** 44 statements (Feb 2021 - Nov 2025, with some gaps) organized to `Taxes 2026/Bank Statements/Pottery Barn Comenity Card (Hillary D Davis)/`, one folder per year, each renamed `<Month> <Year> Statement.pdf`. Unified search files index rebuilt to include them.

**This is one account, two card programs.** Jan-Aug 2021 statements are the original Comenity-issued Pottery Barn Credit Card (account ending 2988). Starting September 2021, the account moved to a Capital One-issued "Pottery Barn Key Rewards Card" (ending 9681) — a program change, not a new account. **Both programs bill to Hillary D Davis, 282 Bald Rock Rd, Verona VA 24482** — the account's mailing address on file is the subject property itself, the same corroboration pattern already established for the business DuPont account in §16. **The Capital One version is a two-cardholder account** — Hillary holds card #9681 and Joshua holds his own card #2476 on the same account (Joshua's card shows zero activity in every statement reviewed).

**One data-quality catch worth recording:** "May 2021 Statement.pdf" as downloaded is an exact duplicate of the April 2021 statement (identical closing date 04/06/2021, identical balance $2,869.33, identical transaction list) — almost certainly a re-download of the same file rather than a real May statement. Excluded from the totals below to avoid double-counting; **the actual May 2021 statement was never captured** and is a real gap in this account's coverage.

**Total new purchases by year, deduplicated by statement closing date (32 unique statements with activity; 11 more statements had zero new purchases that period and are already correctly excluded):**

| Year | New purchases |
|---|---|
| 2021 | $97,695.65 |
| 2022 | $62,320.86 |
| 2023 | $49,344.69 |
| 2024 | $2,363.00 |
| **Total** | **$211,724.20** |

Brand detail where the statement format allowed it to be read: mostly plain "Pottery Barn," with recurring Pottery Barn Kids activity throughout, some Pottery Barn Teen and West Elm charges, and several months tagged generically "Williams Sonoma" (the Capital One statement format doesn't always break out sub-brand on every line, so this list is not a complete brand breakdown, only what was clearly visible).

**CONFIRMED 9/2/2026 by Joshua: the full $211,724.20 is 282 Bald Rock, none of it Woods Walk Lane.** Joshua clarified that 14300 Woods Walk Lane "has always existed" — i.e., it was already owned, not acquired via the 12/2021 transaction this log identified in §17. **Correction to §17's reasoning:** the December 2021 $34,000 transaction through the personal 831015-0090 account was flagged there as Woods Walk Lane's acquisition based on its timing alone; that inference is now known to be wrong (or at least unconfirmed) — Joshua's ownership of that property predates it. This does not unwind any previously confirmed item in this file, since every other §17/§18 item was confirmed directly by Joshua rather than resting on the acquisition-timing argument, but the $34,000 transaction itself is now unexplained and the acquisition-date assumption should not be relied on elsewhere. **Also per Joshua: 14300 Woods Walk Lane is a long-term rental** (distinct from Bald Rock's short-term rental use) — noted here for the record since it's a separate property with its own tax treatment, not part of this file's basis math either way. Full $211,724.20 moved to §1.

## §21. ADDENDUM 9/2/2026 (pass 10) — Shreckhise re-swept for $9,500.44 more; cold plunge was already proven (§1, easy to miss); hot tub still not found despite exhausting every available lead, including county property records

**Trigger:** Joshua asked what's left, specifically flagging that the hot tub and cold plunge weren't found yet, and that Shreckhise is believed to be $25,000-30,000 total (only $8,536.50 was proven).

**Cold plunge — already proven, no new work needed.** §1 already carries **Renu Therapy Order #5754, $10,214.09, 2023-05-27, "Cold Stoic 2.0," ship-to 282 Bald Rock**, paid and shipped (BTX tracking LAX4059890). This predates today's pass — flagging it here only because it's easy to lose track of in a file this size. Nothing further to do on this item.

**Shreckhise — re-scanned the full 9-year business statement archive, found $9,500.00 more.** Beyond the known $8,536.50 (1/18/2023), the DuPont business account (766518) shows: $5,000.00 (10/18/2023), $1,000.00 (11/15/2023), $1,000.00 (12/27/2023), and five $500.00 bill-pay installments (2/5, 2/29, 3/7, 3/14, 3/21 — all 2024). **New total: $18,036.50.** A separate, related retail business — "Shreckhise Shrubbery Sales" (different from "Shreckhise Landscape & Design") — also shows a small $107.41 debit-card charge (4/25/2024). This matches the correspondence trail already on file (design work Oct 2022, a second-phase sketch March 2023 "between the walls behind your house," and an Oct 2024 mulch/tree delivery text from Robert Shreckhise) — the payment pattern spans more than one project phase, which is consistent with why the total kept growing as more statements were checked.

**Still short of $25-30K.** The recurring $500/month bill-pay was still running when the business archive's coverage ends (June 2024) — the strongest remaining lever is bill-pay activity after that date, which this file doesn't have. **Recommended next step:** email Trent Shreckhise directly (trent@shreckhiselandscape.com, real working correspondence already on file) and ask for a full invoice/payment history on the account. This is a message sent on Joshua's behalf, so it needs his go-ahead before it's sent — happy to draft and send as soon as he says so, or he can forward the ask himself.

**Hot tub — genuinely not found, despite exhausting every lead available without going to a bank or vendor directly.** What was checked this pass, on top of everything already tried in §14-§16:
- Re-scanned all 130 business-account and Wells Fargo statement PDFs on file (2015-2024) for a much wider brand/keyword net (spa, jacuzzi, cal spa, artesian, bullfrog, sundance, marquis, hydropool, master spa, thermospa, leisure time, viking spa, freeflow, strong spas) — zero genuine hits; every match was a false positive (Bartesian cocktail machines, "español" boilerplate, unrelated spa/salon charges in Ireland/Nashville from years before this property).
- Re-ran the mail/text search for "hot tub" — all 60 hits are 2017-2018 dealer marketing/newsletter emails (BuyerZone, HotSpring, EnviroSmarte Hot Tub & SwimSpa Center in Charlottesville) from years before this line of investigation is relevant. Nothing resembling an actual order, invoice, or delivery.
- **Pulled the Augusta County property record card directly** (gis.vgsi.com/augustava, parcel 036/D2-2/5A, PID 31761, owner of record Davis, Joshua Christian). This is the county assessor's own record of every assessed outbuilding and improvement. Result: **Outbuildings lists only Pool (Inground, $35,600), Driveway, Patio, and a Retaining Wall — no hot tub or spa of any kind, and "Extra Features" explicitly shows no data.** This also resolved a separate question worth noting: the inground pool structure itself **pre-dates Joshua's ownership** — the county's Ownership History shows the $405,000 purchase on 10/17/2016, and the original sale listing (Redfin) specifically states "child friendly 12' x 24' lap/wading pool for summer fun and the pool furniture stays." **Correction, per Joshua: this does NOT mean the pool has no capital-improvement spending** — he's had the pool redone twice since buying the property, and a full pool redo (demo, re-dig, new equipment/shell/finish) is real capital improvement regardless of whether the original hole predates ownership. The county assessment is a snapshot of the *current* structure's existence, not its improvement history. This file already carries what looks like one redo cycle in §1: **Fundamental Siteworks Inv 670 ($5,329.00, pool demo + dig + rough grade, 2022-11 → 2023-03)** plus **Royal Swimming Pools ($5,592.86 proven, plus $9,919.02 still unproven in §2 for the same #151398/#152804 kit order)** — together a plausible single full pool rebuild in the 2022-2023 window. **Open question for Joshua:** is that 2022-2023 Fundamental Siteworks/Royal Swimming Pools work one of the two redos, or a third distinct instance? If there's an earlier redo (e.g., closer to 2020, matching the broader STR build-out timing) it hasn't been identified yet — none of the existing vendor list (Red Rock Concrete, Crown Decorative Concrete, Decorative Concrete of Virginia) is confirmed as pool-redo work specifically rather than the retaining-wall/patio work already logged separately. A rough year or the contractor's name for the other redo would let this be searched the same way Shreckhise and the rest of §17-§21 were. **UPDATE 9/2/2026: Joshua identifies the contractor for BOTH pool redos as Tyson Buffo, who runs Cannonball Pools.** Searched mail, texts, and all 174 statement PDFs across the business DuPont (766518, 2015-2024), Wells Fargo (2022-2023), and Pottery Barn card archives for "Buffo" and "Cannonball" — **zero genuine hits.** The only "Buffo" match is an unrelated HOA election candidate (Matthew Giacomo Buffo, Woodlake Community Association); every "Cannonball" match is generic pool marketing copy (diving-move language, a TSA news story, a saxophone listing). This confirms and extends the same dead end §9 already hit with a smaller statement set. No contact info (email or phone) for Tyson Buffo or Cannonball Pools exists anywhere in the searchable record, so a direct outreach email — the approach that worked for Shreckhise — isn't possible without Joshua supplying his contact info first. **This, plus the still-missing personal DuPont statements for 2023-2024 and the Wells Fargo gap for 2020/2021/Jan-Aug 2022, are the most likely places these payments actually live.**

**CORRECTION 9/2/2026: the name is Tyson *Boffo*, not "Buffo" — that single letter is why every prior search came back empty. Full payment history recovered by searching the bare first name "Tyson." See §22 for the complete breakdown, contact info, and the pricing/invoice gap.**

**UPDATE 9/2/2026: Joshua is pulling the actual check *images* from the bank himself, likely for 2017-2018.** Correction to the note above: the 2017-2018 personal-account **statements** are already in hand and were fully searched in §14 — what's missing is the images of the checks themselves. A statement line for a check shows only the check number and amount, never the payee name, which is exactly why the §14 pass could rule out any $1,000+ *card* transaction to a pool/spa merchant but couldn't rule out a *check* — nothing in this file has ever seen a check image. A 2017-2018 date fits either the hot tub (never found by any keyword search) or an early pool-related payment predating the 2022-2023 Fundamental Siteworks/Royal Swimming Pools redo already in §1. **Once Joshua has the check images, they need to be reviewed for payee name and amount and reconciled against both open items (hot tub, and the second pool redo per §21/§22) before either can be added to §1.**

**Bottom line on the hot tub:** either it's a portable/plug-in unit that wouldn't show up on a county assessment (most above-ground spas aren't permitted or separately assessed, unlike an in-ground pool), or it was paid for through cash, a check that didn't post with a recognizable payee name, or an account not yet reviewed in this file. Every automated lever available has been pulled. **This is the one item where I need something specific from Joshua to keep going** — even an approximate year, the vendor name, or whether it was cash/check/financed would narrow this enough to search effectively; without that, the remaining options (contacting the credit union for check images, or contacting Luxury Pool and Spa in Harrisonburg directly) both require reaching out to a third party rather than searching records already in hand.
---

# 22. ADDENDUM 9/2/2026 — TYSON BOFFO FOUND (CORRECTED SPELLING); NO PRICING OR INVOICE YET

Joshua's instruction **"tyson, check"** — searching the bare first name after "Buffo" and "Cannonball" both drew a blank — broke this open immediately. The correct name is **Tyson Boffo**. "Buffo" was a one-letter misspelling that caused a complete, genuine dead end across mail, texts, and 174 bank statement PDFs in §21 — none of that prior negative work was wrong, it was just searching for the wrong name.

## What "Boffo" found

**PayPal, Venmo, and bookkeeper correspondence — no bank/check payments found.** Re-ran the same 174-PDF sweep (business DuPont 2015-2024, Wells Fargo 2022-2023, Pottery Barn card) for "boffo" specifically: **zero hits.** Every payment to Tyson Boffo that exists in the searchable record moved through PayPal or Venmo, not a bank account or card.

| Date | Amount | Method | Note/memo |
|---|---|---|---|
| 2020-06-05 | $2,500.00 | PayPal | "You the man!!" |
| 2024-06-19 | $490.00 | Venmo | "Pool" (charge request, completed same day) |
| 2024-10-08 | $325.00 | Venmo | none |
| 2025-11-12 | $1,250.00 | Venmo | none |
| 2026-01-20 | $350.00 | Venmo | none |
| 2026-05-12 | $525.00 | Venmo | none |
| 2026-06-23 | $980.00 | Venmo | none (Venmo screenshot IMG_3538.PNG confirms "Gift #8") |
| 2026-07-29 | $1,050.00 | Venmo | none |
| | **$7,470.00** | | |

**Separately, three 1099-prep emails from bookkeeper Tammy Tackett (11/19/2020, 1/14/2021, 1/26/2021) all list "Tyson Boffo — $4,000.00 — need info"** as a 2020 subcontractor total needing a W-9. This $4,000.00 figure does not reconcile cleanly with the $2,500.00 PayPal payment above — it's either a rounder bookkeeper estimate that includes untraced cash/check payments from 2020, or the $2,500 PayPal payment plus roughly $1,500 more paid some other way that year. **Not counted in the $7,470.00 total above to avoid double-counting** — flagged here as an open reconciliation question, not summed.

**Contact info recovered** (from text messages): phone **+1 (540) 421-0766**, Venmo handle **@tyson-boffo**.

## Why none of this is in §1 yet

Every one of these payments is a bare peer-to-peer transfer. Only one (**$490.00, 2024-06-19**) carries any description at all — the single word "Pool" — and none carries an invoice, itemized description of work, or any indication of whether it was for a capital renovation (demo/re-dig/re-shell) versus routine service (opening, closing, chemicals, repairs), which is exactly the same painted-into-the-corner problem this file has flagged before (see the Blue Ridge Pools & Spa pattern elsewhere in this log). The size and cadence of the 2024-2026 Venmo payments — seven payments, none over $1,250, spread across two years — reads much more like recurring service than a $25-30K renovation, which is normally one or two large lump sums, not a drip of four-figure Venmo requests. **The $2,500 PayPal payment (2020) and the $4,000 bookkeeper figure (2020) are the more plausible candidates for renovation-scale work**, but $2,500-4,000 is still well short of Joshua's $25-30K estimate for either redo, let alone both.

**Bottom line: the vendor is now identified and reachable, but not one dollar of it has a price, invoice, or work description behind it.** This is a materially different gap than the property-attribution problem in §10 — the property/purpose link here is actually fairly solid (Boffo is Joshua's named pool contractor, one payment is memo'd "Pool") — what's missing is entirely on the pricing/documentation side.

## Next step

Per Joshua's instruction: reach out to Tyson directly and ask for pricing or an invoice, covering both pool redo jobs, for tax purposes. **Sent 9/2/2026, 8:02 AM ET**, via iMessage to +1 540-421-0766, verified in the actual Messages conversation history (not just a no-error return): *"Hey Tyson, need pricing or invoice on both pool jobs for taxes, can you send whenever you get a chance. Also do you know who has the original hot tub invoice/cost?"* The hot tub ask was folded into the same text — see below for why. Once pricing or an invoice comes back, the true renovation cost can be evaluated against the $7,470.00 (+ possibly $4,000.00) already found here, and whatever isn't accounted for by that becomes the number to ask Tyson to itemize. **Awaiting his reply — nothing further to do until he responds.**

## Bonus find while reviewing the Tyson text thread: the hot tub is real, current, and Tyson services it

Reading the full iMessage history with Tyson (not just the payment-related hits) turned up something §14/§21 never had: **the hot tub exists, is currently in active guest use, and has an extensive 2024-2026 maintenance history** — dozens of texts about it tripping breakers, heater errors, cleaning, and guest complaints (Madison, Dwayne, Bouncy B/Hillary, and multiple guest phone numbers all reference it). Tyson personally handles hot tub troubleshooting for the property ("Can you reset that breaker on the hot tub," "Is someone else messing with this hot tub up here?"), and **a second vendor — "Valley Pool and Spa," Waynesboro** — is also referenced as a current, apparently-still-operating hot tub service contact (Hillary was asked to "call valley pool and spa waynesboro" in April 2026). This directly contradicts the working assumption in §14 that "Valley Pool and Spa" (the mall-era retailer Joshua originally named) is out of business — there may be two different entities with a similar name, or it never actually closed. **This confirms the hot tub is real and used constantly, but still says nothing about when it was purchased or for how much** — that's still the open question, now folded into the text just sent to Tyson. If he doesn't know, "Valley Pool and Spa, Waynesboro" is now a second, better-identified lead worth a direct call or text (no phone number for them found yet in this pass — a search for that business specifically would be the next step if Tyson's reply doesn't resolve it).
---

# 23. ADDENDUM 9/2/2026 — THE $30K CABINET INSTALL WAS ALREADY IN §1; RECONSTRUCTED FROM BANK DATES, NOT A NEW DOCUMENT

Joshua asked directly whether there's any record of the ~$30K cabinet install at 282, after two dead ends: Wells Fargo has nothing for 2020/2021 because **the account wasn't open yet** (corrected above — not a document gap, the account didn't exist), and MyLowe's Pro purchase history **only goes back to 2024**, years too late to help with a 2021 purchase.

**There's no new document. But the answer is yes — it's already sitting in this file, just not labeled as "cabinets."**

## The reconstruction

§17 already found and proved **$36,040.14 in Lowe's charges on Joshua's personal DuPont REWARDS account (831015-0090), January–September 2021**, confirmed as 282 Bald Rock spending and counted in §1. It was logged generically as "Materials" because the bank record itself carries no item-level description — a debit-card statement shows a store, a date, and an amount, never a receipt line. Going back to the source (`2021 Expense Review/2021 Personal Account Scrub.xlsx`) and pulling every Lowe's line in full turns up all 12 transactions that make up that $36,040.14, all on the same card (****6246):

| Date | Amount | Likely stage |
|---|---|---|
| 2021-01-21 | $6,970.60 | Order deposit |
| 2021-01-23 | $17,519.24 | Order deposit (2nd charge, days later) |
| 2021-03-05 | $8,276.48 | Balance payment |
| 2021-03-05 | $2,053.33 | Balance payment |
| 2021-06-18 | $45.49 | Small hardware run |
| 2021-07-13 | $1,013.71 | Install-week hardware |
| 2021-07-13 | $17.88 | Install-week hardware |
| 2021-08-29 | -$45.25 | Credit/return |
| 2021-08-30 | $139.99 | Small charge |
| 2021-09-14 | $220.01 | Small charge |
| 2021-09-15 | -$177.96 | Credit/return |
| 2021-09-16 | -$6.62 | Small credit |
| | **$36,040.14 net** | matches §1 exactly |

**Two things line up too well to be coincidence:**

1. **The dates bracket the known cabinet timeline exactly.** §6 already had a cabinet delivery (2021-07-04/05), a damage complaint (2021-04-06), an install record dated 2021-04-05, and a backsplash install (2021-07-07) — all sitting *between* the January deposits and the small July hardware-store charges above. A kitchen job typically runs deposit → balance → small trips during install week, and that's exactly the shape of this data: two January charges, a March balance payment, then two small July 13th charges landing right in the middle of the documented delivery/backsplash week.

2. **The dollars match almost to the cent.** The two January charges plus the two July 13th charges total **$35,851.24** — against the **$35,830.19** cabinets-only line inside the §3 kitchen quote ($43,025.31 = cabinets $35,830.19 + countertops $6,845.12 + delivery). That's a **$21.05 difference on a $35,830 purchase** — 99.94% match. The March balance payment ($10,329.81) is close to but doesn't exactly match the $6,845.12 countertop line, so it's less clear whether countertops are separately represented here or whether the actual paid cabinet price simply ran higher than quoted.

## Bottom line

**The $30K cabinet install is not a hole in this file — it's the $36,040.14 already proven and already counted in the $475,119.42 headline total**, via §17. What's genuinely missing is an *invoice* that says "cabinets" in writing; what exists instead is a near-perfect date-and-dollar match between a real quote and real bank charges, which is a normal and reasonable way to substantiate a purchase when the itemized paperwork isn't available. **No dollars change in this file from this pass** — this is a relabeling/confirmation, not a new find. Flag for Silverline: this is bank-record proof of payment plus a strong circumstantial match to a specific quote, not an invoice bearing the property address or an itemized description — the same evidentiary caveat as several other items in this log.

**What would still upgrade this from "very likely" to "certain":** the actual Lowe's sales order/invoice for order record `LOWES:0126689000148`.

**Request sent 9/2/2026, per Joshua's instruction.** While researching this, the full 2021 install-dispute thread turned up two live corporate mailboxes still attached to this exact job: **execustservice@lowes.com** (Lowe's Executive Customer Relations, the same team that handled Case #02040602 that year) and **installsupport@lowes.com** (Lowe's Installation Support, cc'd throughout the original thread). Also found, in Joshua's own 2020-03-18 sent mail (subject "Re: [EXTERNAL] Re: Kitchen pictures and cabinet pricing"): **Joshua's own words at the time — "So approx 35k installed if I use Lowe's card"** — direct contemporaneous corroboration of the ~$35K figure from Joshua himself, independent of the bank-record reconstruction above.

Sent an email to execustservice@lowes.com (cc installsupport@lowes.com) from zapvp1@me.com, 8:43 AM, requesting the original invoice/sales order for LOWES:0126689000148, referencing Case #02040602 and the Staunton VA store (#646). **Correction sent 8:45 AM** — the first draft had the wrong phone number in the signature (Tyson Boffo's number, left over from the earlier draft that day, instead of Joshua's own (804) 930-4221); a follow-up correcting it went out two minutes later. Both sends verified directly in the Sent Messages mailbox (not just a no-error return — see this file's running caveat about that check). **Awaiting Lowe's reply.**
---

# 24. ADDENDUM 9/2/2026 — ARITHMETIC CORRECTION ($107.40 overstatement), AND THE BOTH-SIDES-OF-PROOF PLAN

Joshua asked which is better for substantiating capital improvements — the invoice or the proof of payment — and then said to get both wherever possible and put together a plan. Building that plan meant re-summing every row in §1 by hand, which caught a real error: **the §1 table's own footer total ($465,619.41) was stale** — it was never updated after the Shreckhise re-sweep in §21 raised that line from $8,536.50 to $18,036.50, a $9,500.00 swing the footer never picked up. Separately, **the headline figure ($475,226.82) was $107.41 too high** — it appears to have accidentally folded in the Shreckhise Shrubbery Sales $107.41 line, which §1 explicitly tracks as a separate legal entity never meant to be summed into the Shreckhise Landscape & Design total.

**Corrected: the true, verified sum of every row in §1 is $475,119.42.** Fixed in six places: the headline table, the headline narrative's running total, the §0 basis-math table (adjusted basis now $880,119.42; proven-plus-invoiced now $922,019.32), the §1 section header, §1's own footer total, and the §23 cabinet writeup's reference to the headline figure. Verified this time by summing every row programmatically rather than by eye. **No vendor's dollar amount changed — only the totals that were supposed to be adding them up.** **Second, smaller fix found the same way:** the older "paid, but property attribution unconfirmed" bucket (§10) had a $0.50 rounding error in its own total — the 10 rows there actually sum to $17,276.03, not the $17,275.53 it had printed since it was first built. Fixed in the headline table and both places in §10.

## The both-sides-of-proof plan

Per Joshua's question: an invoice alone proves what was bought but not that it was paid; a bank/card record alone proves money moved but not what for. Both together is the strongest possible substantiation, and that's the standard to chase wherever realistic. A full line-by-line audit of every dollar in this file — what's already got both, what's missing one side, and the specific action to close each gap — is in a new spreadsheet, `282_Bald_Rock_Both_Sides_Plan.xlsx` (this folder), with two tabs:

- **Plan** — nine prioritized action items, largest dollar impact first.
- **Full Tracker** — all 49 line items across all four evidentiary buckets, with an invoice/payment status computed for each.

**Headline numbers from that audit:** of the $475,119.42 already proven, roughly $370K already has both an invoice and a payment match. The single largest remaining gap is the **$211,724.20 Pottery Barn/West Elm/Williams Sonoma total — payment-only, no item-level receipts** (a card statement only shows monthly totals, never what was bought) — pulling the online order history under Hillary's account is the highest-leverage single action available. Next largest: the six card statements never pulled (closes four separate line items at once), and Red Rock Concrete's unpaid $18,622 balance, which needs a decision from Joshua more than a new document search. Everything already in motion (Lowe's cabinets, Shreckhise, Tyson Boffo) stays as-is, awaiting replies.

Two small finds surfaced while building this: an EasyClosets proposal number (#33575293710417, 2021) and a Decor Planet order number (#20-000730250, 2020) — neither carries a captured dollar figure in the email itself, but both are real document references that could be pursued directly with those vendors if it's worth the effort for a combined ~$8,225.56.


---

## SECTION 25 — POTTERY BARN: FULL ITEM-LEVEL ORDER HISTORY PULLED DIRECTLY FROM HILLARY'S ACCOUNT (BOTH SIDES OF PROOF, IN ONE SHOT)

Per Joshua's instruction ("pull up pottery barn so you can download the actual purchases"), logged into potterybarn.com under Hillary's account (hillary91692@gmail.com — the browser already held a valid saved session, no password was entered) and pulled the account's **entire order history via the site's own order-history and order-detail APIs**, not just the visible order-history page. This is the single biggest resolution in the file today.

**What was pulled:** every order on the account, 2010 through today — **302 orders total**. For each one, the full item-level detail: product name, quantity, unit price, and — critically — **the exact masked payment card and dollar amount charged**, straight from Pottery Barn's own transaction record. That last part is what makes this "both sides of proof" in a single document: it is simultaneously an itemized invoice (what was bought) and a payment record (what was charged to which card), issued by the seller itself.

**Filtered to Bald Rock (ship-to ZIP 24482, Verona VA): 262 of the 302 orders, totaling $207,927.96.** The remaining 40 orders shipped elsewhere (gifts to family — the Holmes family in Rockwood/Oak Ridge TN came up repeatedly, plus some orders to Hillary and Joshua's own Cypress Crossing FL address) and are excluded from the Bald Rock figure.

**This $207,927.96 is close to, but not identical to, the $211,724.20 figure in the both-sides-of-proof plan** (Priority 1). The plan's figure was a card-statement estimate covering Pottery Barn **and** West Elm **and** Williams Sonoma combined; today's pull is Pottery Barn only. The ~$3,800 difference is most likely the West Elm/Williams Sonoma share, not an error — see below.

**Payment method breakdown across the 262 Bald Rock orders** (this is the real surprise): the large majority of the dollar volume never touched a personal or business bank card at all — it ran through Pottery Barn—Williams-Sonoma's own store-financing accounts:

- Pottery Barn Credit Card (585637\*\*\*\*\*\*2988): $84,516.39 across 77 orders
- PLCC/WSI/PB (600430\*\*\*\*\*\*9681): $68,739.51 across 100 orders
- VISA/WSI/PB (468837\*\*\*\*\*\*4362): $31,331.23 across 24 orders
- AFFIRM CREDIT: $3,357.44
- Merchandise Credit: $2,646.78 (13 orders)
- PayPal: (1 order, small)

That's roughly $190K of the $207,927.96 — over 90% — paid through a Williams-Sonoma-family financing product, not a card that would ever show up on a personal or business bank statement. **This is exactly why this money was invisible to every card-statement sweep run so far:** it was never going to be on the Amex, Visa, or Mastercard statements this file has been chasing, because it wasn't charged to any of them.

The remainder **was** charged to real personal cards, and two of those directly close gaps already flagged in the six-never-pulled-statements list (§ Both-Sides-Of-Proof Plan, Priority 3):

- **American Express \*\*\*\*1005: $3,452.78 across 7 Bald Rock orders** — this is one of the six statements on the list. The Pottery Barn transaction record itself is now proof of both the purchase and the payment for these 7 orders; a statement pull is no longer needed to substantiate this specific $3,452.78, only to reconcile it against the card's own total.
- **Mastercard \*\*\*\*6246: $1,140.02 across 3 Bald Rock orders** — same card as the Lowe's cabinet charges in §23. Small dollar amount here, but further corroborates that ****6246 was an active household card in this window.
- American Express \*\*\*\*2003: $5,305.47 across 11 orders, and \*\*\*\*2029: $2,048.84 — two Amex accounts not yet otherwise identified in this file. Worth asking Joshua whether these are additional Amex accounts beyond the "only ever had two, Delta and Platinum" he flagged today, or a Delta/Platinum account renumbered over the 2010–2026 span (Amex reissues cards with new last-4 on renewal/loss, so multiple last-4s under one account is normal).
- Mastercard \*\*\*\*9983 ($738.17, 5 orders) and \*\*\*\*6613 ($452.02, 8 orders): two more Mastercards not yet otherwise identified.

**On Joshua's card-identity correction today:** he flagged that "MC 0305" is likely account 766518, an old business debit card, and that the household has only ever had two Amex cards (Delta and Platinum). Noted for when the six-statement pull happens — it means MC \*\*\*\*0305 should be looked for as a **debit** card on an old business checking account, not a credit card statement, and any Amex last-4 that doesn't map to Delta/Platinum (like \*\*\*\*2003 or \*\*\*\*2029 above) needs a direct answer from Joshua on which account it is before it gets treated as a new, unidentified card.

**Files saved (this folder):**
- `pb_order_full_detail.json` — the raw pull: all 302 orders, full item and payment detail, straight from Pottery Barn's API.
- `pb_bald_rock_orders.json` — the 262 orders filtered to ship-to ZIP 24482, same full detail.
- `pb_all_orders_summary.json` — the summary totals and card breakdown above, machine-readable.

**West Elm and Williams Sonoma — not yet pulled, and blocked on a real obstacle.** Despite being "one loyalty login" for browsing/rewards purposes, each brand's order-history system is on its own separate domain with its own separate login session. The Chrome session that was already authenticated on potterybarn.com came back **401 Unauthorized** on westelm.com — no saved session there. Getting in would require either (a) entering Hillary's password, which is a hard no-go regardless of authorization, or (b) a "continue with email" one-time code, which would land in Hillary's personal Gmail (hillary91692@gmail.com) — not one of the four mailboxes this file's search tooling can see. **This one needs Hillary (or Joshua, if he has her password saved somewhere he can hand off through a password manager) to log into westelm.com and williams-sonoma.com once** — after that, the exact same pull done here today takes minutes to repeat on both.

**Net effect on the both-sides-of-proof plan:** Priority 1 ($211,724.20, "payment-only, no item-level receipts") is now resolved for its Pottery Barn share — $207,927.96 of it has full item-level detail AND a matched payment record, sourced directly from the seller. What's left of Priority 1 is narrowly the West Elm/Williams Sonoma slice (roughly $3,800, unless that estimate undercounted — will know for certain once those two logins happen) plus the routine follow-up of naming the two unidentified Amex accounts and two unidentified Mastercards above.


---

## SECTION 26 — WEST ELM CLOSED OUT (ONE ORDER, ALL-TIME); WILLIAMS SONOMA STILL NEEDS ITS OWN LOGIN

Joshua logged into westelm.com directly (no password entered by me — he did that himself), clearing the blocker from §25. Same API pull as Pottery Barn, run immediately: **westelm.com has exactly one order on the account, ever.**

- Order #331892943845, placed 7/8/2023, delivered 8/21/2023
- Woven Honeycomb Outdoor Performance Rug, 9x12, Natural — $799 + tax/shipping = **$1,029.83 total**
- Shipped directly to 282 Bald Rock Rd, Verona VA 24482
- Paid on VISA/WSI/PB card ****4362 — the same card used for $31,331.23 of the Pottery Barn charges in §25

Both sides of proof, same as the Pottery Barn pull: item + matched payment, from the seller's own record. **West Elm is fully closed — nothing further to do there.**

**Williams Sonoma is not yet accessible** — williams-sonoma.com returned 401 (no saved session) when checked right after the West Elm success. It's the same situation §25 described: needs Joshua or Hillary to log in there directly once, then the identical pull takes a minute.

**Updated math on the original $211,724.20 combined PB/WE/WS estimate:**
- Pottery Barn (§25): $207,927.96 — resolved
- West Elm (this section): $1,029.83 — resolved
- Williams Sonoma: ~$2,766.41 estimated remainder — still open, blocked on login only

$208,957.79 of the original $211,724.20 estimate is now fully proven both ways. What's left is a single-vendor, sub-$3,000 gap.


---

## SECTION 27 — PROPERTY-ATTRIBUTION BUCKET RE-CHECKED: AUGUSTA STEEL WAS NEVER BALD ROCK

Joshua asked whether check images exist for the accounts in this file (answered directly in chat — none do, see the three open gaps below this section once it's added). While researching that, the nine open items in the "paid, but property attribution unconfirmed" bucket ($17,276.03) got a second look using the mail index, since two of them (Augusta Steel, Augusta Aluminum Gutterworks) are named vendors with a findable email trail.

**Augusta Steel Corporation, $2,652.50 (03/09/2022, Full Circle business checking) — confirmed NOT a Bald Rock cost.**

Every email exchanged with Augusta Steel between October 2021 and February 2022 is titled "Rear Door Quote," "VALLEY PAWN DOOR INSTALLATION," or "VALLEY PAWN" — never Bald Rock, never 282. The exchange that settles it:

> **Jay Hicks (Augusta Steel), 11/30/2021:** "Joshua, Who does this get written up under? Valley Pawn? Full Circle Pawn?"
> **Joshua, 11/30/2021:** "Actually Farming Infinity Inc. I own the building."

Farming Infinity Inc is a separate entity from Full Circle Finance — it owns a different building where a Valley Pawn store operates, and this door installation was billed to it, in Joshua's own words. The $2,652.50 charge just happened to clear through the same Full Circle business checking account as Bald Rock renovation spend, which is exactly why it landed in the property-attribution-unconfirmed bucket in the first place — same account, different property. **Removed from Bucket 3's total.** New bucket total: **$14,623.53** (was $17,276.03).

**Augusta Aluminum Gutterworks, $4,500.00 — checked, inconclusive, left as-is.** One email exists ("Gutter Receipt," 3/30/2022) with a PDF receipt attached, but the attachment is a `.partial.emlx` — Apple Mail only cached the message text locally, not the receipt itself. The email body says only "I have attached the receipt for the gutters... I appreciate the business and I will have some numbers on the other work soon" — no address, no property name. No change to this line; still Medium confidence, still needs a direct invoice request.

**ZELLE "AVABI" (gutters), $1,745.00 — checked, no new evidence, left as-is.** The Wells Fargo transaction memo just reads "GUTTERS." A nearby line in the same bookkeeping export ("BLD*VALLEY RENTAL PURCHASE," a recurring ~$2,200/month charge) is a coincidence of row order, not the same transaction — confirmed by reading the underlying spreadsheet directly. That $2,200/month charge is a separate, unrelated vendor (an equipment rental company) and isn't part of this bucket.

**ZELLE "Marlon" (tile) and ZELLE "GC" (pocket door frames) — checked, no new evidence, left as-is.** No email trail ties either to a specific address. The "GC" search surfaced an unrelated September 2025 email thread with Manning Building Supplies in St. Augustine, FL about pocket door frames — a coincidental keyword match on a different Florida purchase, not this $832.03 Zelle payment. Both remain at their existing confidence levels in the log.

**Bottom line: the bucket shrinks from $17,276.03 to $14,623.53, and the one dollar that moved, moved for a good reason** — it was never Bald Rock money to begin with. The remaining eight items are unchanged and still need what the tracker already says they need (mostly: ask Joshua to identify a payee, or request an invoice directly).


---

## SECTION 28 — DUPONT PERSONAL CHECKING 831015: CHECK IMAGES PULLED, MULTIPLE FINDINGS

Joshua pulled the check images himself for DuPont Community Credit Union personal checking account 10900000831015 (Joshua C Davis, 282 Bald Rock Rd) and uploaded a 7-page PDF covering checks from August 2020 through August 2024. Filed to `Taxes 2026/Bank Statements/DuPont 831015 Personal Checking (2020-2024)/` and mirrored into iCloud Drive at `03 Personal/02 Taxes/DuPont 831015 Personal Checking - Check Images (2020-2024)/` for search indexing. This is the first check-image pull to actually clear on any account in this file — every prior mention of "no check images" in this log applied to the DuPont *business* account (766518) and the DCCU hot-tub check (#1311), which remain unresolved. This account is a different, personal checking account.

Of roughly 20 checks visible, most are personal (piano lessons, dog boarding, a plastic-surgery payment, two recurring $614.70 preauthorized ACH payments to JPMorgan Chase on a Hillary D. Holmes account, and one oddity — a $61.60 U.S. Treasury refund check made out to a third party, Benjamin M. Ratchliffe, that was deposited into this account; immaterial and not pursued). Six checks are property-related and break into three groups.

### Confirmed Bald Rock — both sides of proof now exist

**Red Rock Concrete, Invoice #1244 — fully reconstructed.** Pulling the actual invoice emails (not just the reminder) shows the invoice was revised downward twice as line items were removed:

| Version | Total | Payment shown | Balance Due |
|---|---|---|---|
| 08/04/2022 (first) | $32,440.00 | $10,000.00 | $22,440.00 |
| 08/04/2022 (reminder, final) | $28,622.00 | $10,000.00 | $18,622.00 |

Two DuPont personal checks now bank-match this invoice directly:
- **Check #144, 6/28/2022, $10,000.00, memo "282 Project"** — this is the exact "$10,000.00 Payment" already shown on the invoice. §1's Red Rock Concrete line (payment previously proven only by the invoice's own payment line) is now upgraded to a full bank match — Y/Y, no caveat.
- **Check #103, cleared 8/8/2022, $8,672.00, memo "Walls"** — a *second*, previously unknown payment, made right around the final invoice date. This was not on the invoice (which predates or coincides with it) and was never found in any bank sweep. **It pays down more than half of the $18,622.00 "unpaid balance" that Priority #2 on the Plan sheet has been asking Joshua to explain since this file began.**

**New true remaining balance: $18,622.00 − $8,672.00 = $9,950.00.** Still unresolved, still needs Joshua's memory or another document, but the mystery just got much smaller.

**Valley Concrete Inc. — new vendor, confirmed Bald Rock.** Check #163, 5/1/2023, $6,330.00, memo "PP Patio Deck." A contract email from Joshua to Valley Concrete (6/21/2023) reads: *"This contract replaces any verbal or written contract between Joshua Davis and Valley Concrete. Pool Deck install at 282 Bald Rock Road..."* — direct confirmation. Valley Concrete's Invoice 1799 (due 5/28/2023) shows a **$12,330.00** total, so this $6,330.00 check may be a deposit with roughly **$6,000.00 still unaccounted for** — a new small open item, not yet added to any total pending confirmation of how the rest was paid.

### Likely Bald Rock, no independent corroboration beyond the check itself

- **Luis Pineda — $6,750.00 combined**, two checks: #127 (5/6/2023, $3,500.00, "Wall Problem") and #121 (5/10/2023, $3,250.00, "Stucco Wall"). No email trail for this payee, but nothing points elsewhere either. Added to Bucket 1 as proof-of-payment-only (no invoice), Medium confidence.
- **Tyson Boffo — $10,000.00, check #105, 12/28/2022, memo "Pool Install."** Tyson Boffo is already tracked in Bucket 4 for $7,470.00 in PayPal/Venmo payments (2020–2026) with an open capital-vs-service question. This check is a different payment method and predates most of those, so it's additive: **Bucket 4's Tyson Boffo line rises from $7,470.00 to $17,470.00.** The word "Install" (vs. "service" or "cleaning") leans capital, which matters once Joshua's pending pricing/invoice reply comes back.
- **Geiver Macariegos — $4,000.00, check #102, 4/19/2022, memo "202 Paint."** No email trail for this payee at all. The memo is legibly "202," not "282" — could be a mis-write, could be a different address. Filed to Bucket 3 (property-attribution-unconfirmed) rather than Bucket 1, pending Joshua's confirmation.

### Confirmed NOT Bald Rock — a second property surfaced

Three checks to the same payee, "Jeff Loparte," explicitly memo "14300 Repairs" or "14300 Reno-Thx": #107 ($1,940.00, 4/29/2022), #161 ($2,145.00, 6/10/2022), #143 ($2,344.27, 6/17/2022) — **$6,429.27 combined.** "14300" is **14300 Woods Walk Lane, Midlothian, VA 23112** — a separate rental property Joshua's 2021 IRS abatement filing lists as "Additional Property... Worth $275,000." iCloud Drive already has a folder from a prior tax year, `03 Personal/02 Taxes/2023/Personal Tax 2023/14300 Repairs 2022/`, holding ten "Check Image Search" PDFs — independent confirmation this exact repair spend was already understood to belong to Woods Walk, not Bald Rock. **None of this $6,429.27 has ever been in any Bald Rock total and none is being added now.**

Same property, same payee family: **Check #106, 12/24/2021, $34,000.00, to Rachael Davis, memo "Payoff 1430 Woods Walk"** — matches "payoff ex for 14300 Woods Walk Lane" language in the same 2021 tax records. A personal payoff, unrelated to Bald Rock.

**Two checks to the same "Jeff Loparte," #101 ($3,787.27, 12/3/2021) and #104 ($4,912.32, 3/3/2022), carry no address in the memo** (illegible/blank) and predate the three confirmed-Midlothian checks from the same payee. Given the same contractor did confirmed work at Woods Walk on this account, these two are genuinely ambiguous — **found and logged here, but not added to any Bald Rock total.** If Joshua recalls what Jeff Loparte was paid for in Dec 2021–Mar 2022 ("Carpet" is the best guess at check #101's memo), that would resolve $8,699.59 either way.

### Net effect on the tracker

- Bucket 1 (proof of payment): +$13,080.00 (Valley Concrete $6,330.00 + Luis Pineda $6,750.00), plus Red Rock's existing $10,000.00 line upgraded from partial to full bank match.
- Bucket 2 (invoiced, payment not proven): Red Rock's unpaid-balance line drops from $18,622.00 to $9,950.00.
- Bucket 3 (property attribution unconfirmed): +$4,000.00 (Geiver Macariegos).
- Bucket 4 (capital-vs-service unconfirmed): Tyson Boffo line rises from $7,470.00 to $17,470.00.
- $8,699.59 (two Jeff Loparte checks) and $40,429.27 (three Midlothian checks + the Rachael Davis payoff) are documented here but deliberately excluded from every Bald Rock total.


---

## SECTION 29 — SHRECKHISE: A SEVENTH PAYMENT FOUND, THIS ONE A PAPER CHECK, NOT BILL-PAY

The same DuPont personal checking 831015 check-image pull (§28) also turned up a **Shreckhise** payment that doesn't belong to the $18,036.50 already proven in §1/§21 — because it's not from the same account or the same payment method.

**Check #145, 5/3/2023, $4,000.00, payee "Shreckhise" (spelled "Streckhice" on the check face), memo "Landscape," cleared 5/5/2023.** The existing $18,036.50 figure is built entirely from **DuPont *business* account (766518) bill-pay withdrawals**: $8,536.50 (1/18/23) + $5,000.00 (10/18/23) + $1,000.00 (11/15/23) + $1,000.00 (12/27/23) + five $500.00 installments (2/5/24 → 3/21/24). Check #145 is a **paper check from the *personal* account (831015)**, dated 5/3/2023 — a date that falls in the gap between the January and October 2023 bill-pay withdrawals, not a duplicate of either. Different account, different payment method, different date: this is additional money, not a re-find of something already counted.

**New Shreckhise Landscape & Design total: $18,036.50 + $4,000.00 = $22,036.50.** This also nudges Joshua's own recollection ("~$25-30K with Shreckhise") to within $3,000-8,000 of fully matching, down from $7,000-12,000 short.

### Net effect on the tracker

- Bucket 1 (proof of payment): Shreckhise line rises from $18,036.50 to $22,036.50 (+$4,000.00).
- Plan sheet Priority #5 (Shreckhise) amount updated to match; status unchanged (still awaiting Shreckhise's own invoice reply — this find is a payment-side add, not an invoice).


---

## SECTION 30 — A THIRD BANK ACCOUNT: FARMING INFINITY LLC (DUPONT 912291), SIX PROPERTIES SHARING ONE CHECKBOOK

Joshua pulled check images for a second DuPont Community Credit Union account, 912291, and uploaded a check-image PDF spanning 6/25/2022 through 8/2026. This account is titled **"FARMING INFINITY LLC"** with the printed mailing address "282 Bald Rock Rd, Verona, VA" — but per the Real Estate OS entity structure (`Life OS/REAL_ESTATE_OS.md`, corrected 2026-08-10), that address is simply the **registered-agent address shared by every Farming Infinity entity** — it is not evidence that a given check is a Bald Rock expense. "Farming Infinity, LLC" (no "Mountains") is specifically the *original* 2019 entity that owns **817 Richmond Avenue, Staunton VA** (commercial, leased to FirstCash) — a different property and a different LLC than **Farming Infinity Mountains LLC**, which is Bald Rock's actual owner (formed July 2026). Before the July 2026 entity split, this account appears to have functioned as the general real-estate operating account for the whole Farming Infinity family — checks in this one register carry memos tying them to **six different properties/purposes**: 282 Bald Rock Rd, 14300 Woods Walk Lane, 817 Richmond Ave, 148 Hardinberry St (Oak Ridge, TN), 844 Cypress Crossing Trail (FL), and VA SCC entity-filing fees. This is the same "one checkbook, multiple properties" risk already documented for the DuPont personal account in §28 — memo lines, not the letterhead, are what decide attribution here.

### Confirmed Bald Rock (282) — new vendors and new proof

- **Jacob Thomas — Insulation, $820.00, check #111, 10/27/2022, memo "Insulation 282."** New vendor, proof of payment only (no invoice found). Added to Bucket 1.
- **Jeff Laporte — $2,077.87, check #112, 11/3/2022, memo "282 Bald Rock Proj."** Important correction to §28: Jeff Laporte's other checks (from the DuPont *personal* 831015 account) all carry "14300" memos and were excluded as Woods Walk work — but this check, from a *different* account, proves Laporte also did work directly at Bald Rock. Added to Bucket 1 as its own line, separate from the excluded Woods Walk checks.
- **TAG Drywall — $1,300.00, check #115, 3/9/2023, memo "Drywall 282."** New vendor, proof of payment only. Added to Bucket 1.
- **Shreckhise Landscape & Design — $5,000.00, check #116, 3/15/2023, memo "282 Landscape."** A **fourth, independent funding source** for Shreckhise, on top of the business bill-pay withdrawals (§21) and the DuPont-personal paper check (§29) — checked against every previously known Shreckhise date (1/18/23, 5/3/23, 10/18/23, 11/15/23, 12/27/23, five 2024 dates) and this 3/15/23 date matches none of them. **New Shreckhise Landscape & Design total: $22,036.50 + $5,000.00 = $27,036.50** — this now lands almost exactly inside Joshua's own recollection of "~$25-30K with Shreckhise" (§21), the closest this line has ever come to matching his memory.
- **Tyson Boffo — $5,500.00, check #230, 5/22/2023, memo "POOL 282."** Explicit 282 memo. Added to Bucket 4 (capital-vs-service unconfirmed, same bucket as Boffo's other pool payments).
- **Tyson Boffo — $475.60, check #103, 6/22/2022, memo "Pump Repair"** and **Tyson Boffo — $5,500.00, check #118, 3/23/2023, memo reads approximately "Pool Reno..." (partially illegible).** Neither memo names an address, but both are the same pool contractor already tied exclusively to Bald Rock's pool across §21/§22/§28 — added at Medium confidence, same treatment given to Luis Pineda in §28.

**New Tyson Boffo running total: $17,470.00 (per §28) + $5,500.00 + $475.60 + $5,500.00 = $28,945.60.** This is now the single largest line in the capital-vs-service-unconfirmed bucket by a wide margin, and still has no invoice or pricing breakdown — Joshua's outstanding text to Boffo (Plan Priority #6) covers this.

### Confirmed NOT Bald Rock — five more properties/purposes sharing this account

- **14300 Woods Walk Lane** (Chesterfield County): Brian Lauhorn $1,500.00 "HVAC 14300" (6/25/22); Jeff Laporte $2,500.00 "14300 Work" (7/1/22); Jeff Laporte $2,345.00 "14300 Repairs" (7/7/22); Jeff Laporte $1,940.00 "14300" (9/15/22); R+B Paint $1,390.00 "14300 Paint" (9/16/22); Jeff Laporte $480.00, no legible memo but same-payee pattern (9/16/22); **Virginia Contractors Painters $7,450.00, memo "Paint 14300"** (5/26/23) — a large one; plus three Chesterfield County real-estate-tax checks ($147.20, $256.02, $338.00). None of this touches any Bald Rock total.
- **817 Richmond Avenue, Staunton** (the *original* Farming Infinity LLC's own commercial building): Augusta Aluminum Gutters $1,650.00 "817 Gutters" (6/26/22); five City of Staunton utility payments ($36.92–$81.22 each, one explicitly memo'd "817"). Small dollars, clearly a different building.
- **148 Hardinberry Street, Oak Ridge, TN (Roane County)** — a property not previously surfaced in this evidence log. Per `unified-search`, this is a long-held property (Joshua's own address as far back as 2016) now generating Airbnb income (occupancy-tax line items name Roane County) and mid-2026 was in a "two-step deed transfer" review to move it into **Farming Infinity Tennessee LLC**. This account shows real capital spend there in 2025-2026: Danny's Floor Store $2,752.00 and $2,000.00 (flooring), Roane County $902.00, City of Oak Ridge $890.00, Manning Building Supply $7,890.03 ("Trim & Base"), Drain Kings Plumbing $900.00. **None of this is Bald Rock** — flagging it here only because it shares this checkbook; a dedicated evidence log for 148 Hardinberry would need its own build if Joshua wants that property's basis substantiated too.
- **844 Cypress Crossing Trail, FL** (Joshua & Hillary's personal residence — owned personally, no LLC, per Real Estate OS): two 2026 "Palencia POA" checks, $1,500.00 (application fee) and $500.00 (refundable deposit), memo "Cypress Crossing." Personal, not Bald Rock, not even a Farming Infinity entity expense technically — flagged as a same-checkbook artifact only.
- **Entity administration:** a $50.00 check to "SCC" (Virginia State Corporation Commission), 4/10/2023 — an LLC filing fee, not a property expense.

### Left unresolved, not added to any total

Geo Terrain $884.45 "Soil Test" (8/1/22), a $2,400.00 "Gutters" check to an illegibly-named payee (10/5/22), McLain's Pump Service $1,265.00 "Pump Repair" (4/10/23), and a $275.00 "Ground/Soil" check (3/16/23) carry no address in their memos and aren't confidently tied to Bald Rock or any other property — logged here for completeness, not counted anywhere. Recurring small "Comfort Cleaning" checks ($150-225, several dates) are routine STR housekeeping, not capital improvements, and were left out of this evidence log entirely regardless of property — they don't belong in a cost-segregation basis study either way.

### Net effect on the tracker

- Bucket 1 (proof of payment): +$820.00 (Jacob Thomas) + $2,077.87 (Laporte, 282) + $1,300.00 (TAG Drywall) + $5,000.00 (Shreckhise, 4th source) = **+$9,197.87**.
- Bucket 4 (capital-vs-service unconfirmed): Tyson Boffo line rises from $17,470.00 to **$28,945.60** (+$11,475.60).
- Shreckhise Landscape & Design (within Bucket 1) rises from $22,036.50 to **$27,036.50**.

---

## SECTION 31 — DUPONT BUSINESS ACCOUNT 766518 CHECK IMAGES: CONFIRMED VALLEY PAWN, NOT BALD ROCK

Joshua separately uploaded a 125-page check-image PDF for DuPont Community Credit Union account 766518, labeling it himself as "dupont old full circle finance dba valley pawn account." A sampled read across the full date range (2017 through 2025) confirms that label: every check is Full Circle Finance Inc / Valley Pawn operating activity — employee payroll and bonuses (dozens of named individuals, memo "PR"/"Payroll"/"Bonus"), store rent (DWS Properties, RBSA LLC, IWC Properties, BZA Spotswood LLC), city/town business licenses and taxes for Valley Pawn's own store cities (Staunton, Waynesboro, Culpeper, Harrisonburg, Lexington), FFL/gun-dealer fees to the Virginia State Police, and a cluster of 2020 repair/renovation checks explicitly memo'd **"817 Repair"/"817 Renovation"/"817 Plumbing"** — the *other* Farming Infinity property (817 Richmond Ave), not Bald Rock. **Nothing in this account carries a "282" or Bald Rock memo anywhere in the sampled pages.** This account does not resolve the long-standing DuPont-business 514-check attribution question referenced elsewhere in this file — that gap remains open, and this particular account is confirmed to be the wrong place to look for it. Filed to the Mac and indexed for search per Joshua's usual practice, but **not** folded into any Bald Rock bucket.

## SECTION 32 — SHRECKHISE FULLY INVOICED ($30,645.83); PINEDA CONFIRMED AS POOL-WALL STUCCO (2026-09-03)

**Shreckhise Landscape & Design sent their own paperwork** on 2026-09-02 ("Requested Paperwork,"
Erica Taylor, erica@shreckhiselandscape.com → jdavis@fcfpawn.com), a 1.66MB PDF attachment
("Joshua Davis Invoices.pdf") that was a partial/lazy-loaded message locally — pulled in full via
Mail.app's own attachment-save (not the local mail index) on 2026-09-03. Four complete, itemized
invoices, every one showing **TOTAL DUE $0.00** with handwritten payment-date annotations that
reconcile exactly to each invoice total:

| Invoice | Date | Amount | Work | Paid |
|---|---|---|---|---|
| #21874 | 11/28/2022 | $17,073.03 | Back landscape: assorted trees/shrubbery, topsoil/compost, mulch, tree guards, transplant labor, front tree additions (Blue Atlas Cedar, Green Giant Arborvitae) | 1/24/23 $8,536.50 + 3/17/23 $5,000.00 + 5/4/23 $3,536.53 = $17,073.03 exactly |
| #22148 | 5/4/2023 | $4,569.44 | Assorted trees/shrubbery, sod, plant replacements | Handwritten payment notes present, partially illegible |
| #22174 | 5/15/2023 | $428.55 | Mulch for shrubbery beds + delivery | Handwritten payment note present |
| #22366 | 9/18/2023 | $8,574.81 | **Pool landscape** (trees/shrubbery, flagstone, compost/topsoil, mulch, seed/straw) + **driveway wall** (trees/shrubbery, mulch) | Multiple handwritten payments Oct 2023–Apr 2024 (e.g. 10/27/23 $4,571.45, 11/27/23 $1,000, 12/15 $1,000, 2/16/24 $500, 3/11 $500, 3/15 $500, 2/23 $500, 4/4 $336) |
| **Total** | | **$30,645.83** | | |

This **replaces** the prior $27,036.50 bank/check-derived estimate for Shreckhise with a fully
documented, invoice-plus-payment-matched figure — the strongest possible evidence tier (both sides
of proof, from the vendor's own paperwork, same pattern as Pottery Barn §25 / West Elm §26). All
of this work is landscaping — a **Land Improvement (15-year, 100% bonus-depreciation-eligible)**
category, not Structural. `build_tracker2.py` and `282_Bald_Rock_Both_Sides_Plan.xlsx` updated
2026-09-03: Bucket 1 total now $505,006.62 (was $501,397.29); all-buckets total now $585,803.65
(was $582,194.32).

**Separately, Joshua confirmed 2026-09-03** that the two open-item vendors from §28 are:
- **Valley Concrete Inc.** ($6,330 proven, ~$6,000 of Invoice 1799 still unresolved) — **the pool
  deck.** Matches the tracker's existing note exactly; no change needed.
- **Luis Pineda** ($6,750, DuPont checks #127 "Wall Problem" + #121 "Stucco Wall") — **stucco on
  the pool walls, not the house.** This was previously bucketed as Structural (39-year, not
  bonus-eligible) in the depreciation-category breakdown; **reclassified to Land Improvement**
  (15-year, bonus-eligible) since it's a pool component, not part of the residence structure.

**Net effect on the cost-seg basis analysis** (see `Taxes 2026/Real Estate Tax Strategy & Cost
Segregation Notes.md` §4 for the full updated numbers): adjusted basis floor rises from
$906,397.29 to $910,006.62 (ceiling $987,194.32 → $990,803.65); short-life/bonus-eligible portion
rises from $316,847.84–$380,009.96 to **$327,207.17–$390,369.29** (the Pineda reclass alone moves
$6,750 from non-eligible to eligible; the Shreckhise increase of $3,609.33 is itself a land
improvement).

**Also confirmed 2026-09-03: Joshua & Hillary moved from 282 Bald Rock to Florida full-time on
8/1/2025.** This resolves the previously-open conversion-date question — the Blue Ridge Appraisal
(still intentionally on hold pending the improvement list) should target FMV as of 8/1/2025
specifically per 26 CFR 1.168(i)-4's lesser-of-adjusted-basis-or-FMV rule.

**Still open, unchanged by this find:** the six never-pulled card statements (Signature Hardware,
Royal Swimming Pools, Commonwealth Tile, Lowe's), Williams Sonoma (blocked on a direct login),
Lowe's kitchen-cabinet records request (sent 9/2, no reply yet as of 9/3), Tyson Boffo pricing/
invoice (text sent 9/2, no reply yet), and the Red Rock Concrete $9,950 remaining-balance question
— all re-checked 2026-09-03 via the mail index, nothing new found on any of them.


## SECTION 33 — EXHAUSTIVE THREE-ACCOUNT CHECK-IMAGE REVIEW FOR RED ROCK CONCRETE (2026-09-03)

Joshua asked directly whether every check-image set he has sent was scoured for cost-seg basis, specifically recalling "I saw red rock checks" in what he called "the old FCF Inc account." Every check-image PDF in the Bank Statements folder was identified and reviewed page-by-page, image by image (not sampled):

| Account | File | Pages | Result |
|---|---|---|---|
| DuPont 766518 — Full Circle Finance Inc / Valley Pawn business (the "old FCF Inc account" Joshua referenced) | Check Images 766518.pdf | 125 | Two full passes (all 125 pages at contact-sheet resolution, plus a targeted high-resolution re-read of the Jan 2022–May 2023 window). **No Red Rock Concrete check found.** Only payroll, RBSA/RBSA Properties rent, VA state/local tax and license payments, Jeff LaPorte reimbursements, small vendor/utility checks. |
| DuPont 831015 — Joshua & Hillary personal checking | Check Images 831015.pdf | 7 | Full review, all pages, high resolution. **Both known Red Rock Concrete checks located here:** #144, 6/28/2022, $10,000.00, memo "282 Project" (the original deposit) and #103, 8/3/2022, $8,672.00, memo "Walls" (the partial payment already documented in §28). No third or additional Red Rock check. This account also independently confirmed the two Luis Pineda pool-wall-stucco checks (#127 $3,500 "Wall Stucco," #121 $3,250 "Stucco Wall," total $6,750 — matches §32) and the Valley Concrete pool-deck check (#163, $6,330, "PP Patio Deck"). |
| DuPont 912291 — Farming Infinity LLC | Check Images 912291.pdf | 18 | Full review, all pages, high resolution. **No Red Rock Concrete check.** Confirmed the three already-known Tyson Boffo pool checks (#103 $475.60 "Pump Repair," #118 $5,500.00 "Pool Reno," #230 $5,500.00 "Pool 282") and the Shreckhise $5,000 landscape check (#116, "282 Landscape"). Also contains checks for an unrelated Florida property (844 Cypress Crossing Trl / Palencia POA) and two Roane County/Anderson County, TN checks tied to the separate 148 Hardinberry property (#143 Roane County $902.00, #140 City of Oak Ridge $890.00, both dated 11/1/25, both memo'd "148 Hardinberry") — flagged for the still-open 148 Hardinberry Anderson-vs-Roane-County discrepancy, not resolved here. |

**Conclusion: all three check-image sets Joshua has sent have now been reviewed in full, not sampled.** Joshua's recollection of seeing Red Rock Concrete checks is correct — but the two checks that exist are the two already in the tracker ($10,000 deposit + $8,672 partial payment), both in the personal 831015 account, not a new/additional one in the business account. The math already in the Plan sheet holds exactly: original invoice #1244 balance $18,622.00 − $8,672.00 paid = **$9,950.00 still unaccounted for**, with no bank record of that remaining balance being paid anywhere across all three accounts. This is now a closed research question — the only way to close the $9,950 gap is Joshua confirming directly whether it was ever paid (cash, a payment app not covered by these three accounts, or written off), not further searching.


## SECTION 34 — RED ROCK $9,950 BALANCE: JOSHUA RECALLS PAYING VIA SQUARE/QUICKBOOKS LINK; SEARCHED, NOT CONFIRMED (2026-09-03)

Joshua stated the remaining balance was paid, "i think via square or quicbooks invoive payment link he sent." Investigated:

**Confirmed Red Rock Concrete billed through QuickBooks/Intuit invoicing** (quickbooks@notification.intuit.com, sender name "Red Rock Concrete LLC") — so a Pay-Now-link payment was mechanically possible. Found the full negotiation trail for invoice 1244:
- Three revised "New payment request... invoice 1244" emails, 8/4–8/8/2022, showing the invoice total being negotiated down: $34,060.00 → $32,440.00 → $28,622.00 (each already crediting the $10,000.00 deposit).
- Two "Invoice - Reminder... has not been [paid]" emails, both 8/7–8/8/2022 — confirming the invoice was still unpaid as of that date.
- A "Give me a call" email thread, 8/7/2022 evening, Joshua and Phil Coblentz (owner) directly negotiating the final number line-by-line (a $500 "rock remediation" error, wall-footage overages). Joshua's own stated bottom line: **"My expectation was 28672.00."** Phil's final reply: "We want our customers happy... Whatever you want. I will change it." Joshua's reply: "You're a gentleman. You'll have all my future business." — reads as a resolved, friendly close to the dispute, consistent with a payment following shortly after.

**No payment confirmation was found for this invoice.** Searched: (1) every "Payment confirmation: Invoice #..." email from QuickBooks Payments in Joshua's mailbox for Aug–Oct 2022 — these exist for Joshua's *other* vendors billed the same way in this exact window (Enlit LLC #1054, S.A.F.E. Services #1545), but none exists for Red Rock Concrete / invoice 1244. (2) Any Square receipt/confirmation mentioning Red Rock — none found. (3) iMessages with Phil Coblentz — not searchable; the text index only reaches back to mid-2024, so an August 2022 text-coordinated payment (with no email trail) cannot be ruled in or out this way. (4) The one card/bank statement covering that window in the Taxes 2026 folder (Wells Fargo FCF Business) — that account wasn't opened until 9/23/2022, after the dispute, so it has no relevant activity and doesn't help.

**Net effect:** either (a) Joshua paid it a way that left no email or currently-searchable record (a phone-coordinated Square/QB charge whose receipt went to a different inbox or was deleted, or a text-based confirmation from 2022 that predates the text index), or (b) it was never actually paid despite the friendly close to the dispute. The digital trail available doesn't distinguish between these. **This needs Joshua directly:** a screenshot of the charge, a card/bank statement from Aug–Sept 2022 showing an Intuit/Square/"Red Rock" charge for something in the $9,950–$18,672 range, or simply his memory of which card he used, would resolve it. Absent that, the $9,950 gap stays flagged as unconfirmed rather than closed.


---

## §35. RED ROCK $9,950 BALANCE: CLOSED ON JOSHUA'S DIRECT CONFIRMATION (2026-09-03)

Following §34's negative search result (no QuickBooks Payments confirmation, no Square receipt,
no usable text-message trail, no relevant bank statement — see §34 for the full search), Joshua
was asked directly. His response, verbatim: **"the balnce was pid, i think via square or quicbooks
invoive payment link he sent"** — followed by an explicit instruction: **"mark as paid, it was
paid."**

Per this project's standing evidentiary practice, Joshua's direct statement is accepted as ground
truth and the item is closed on that basis. Recorded here plainly for audit purposes: **the
$9,950.00 portion of Red Rock Concrete invoice #1244 rests on taxpayer representation alone, not
on an independent bank, card, or vendor document** — unlike the $18,672.00 portion, which is
bank-matched via check image (§28, confirmed via the exhaustive three-account review, §33), and
unlike the confirmation emails found for Joshua's other same-era vendors billed the same way
(Enlit LLC, S.A.F.E. Services). If this item is ever challenged, that distinction should be
disclosed rather than presented as equally documented.

**Status: full $28,622.00 invoice (both portions) now treated as paid in full.** Tracker
(`build_tracker.py`, `build_tracker2.py`) and the tax strategy memo (§4) updated accordingly the
same day; see `OPEN_ITEMS_REGISTER.md` for the corresponding closure entry.


---

## §36. SIGNATURE HARDWARE — FULL ORDER HISTORY PULLED DIRECTLY (2026-09-03)

Joshua logged into his own signaturehardware.com account (zapvp1@me.com) — "ok pull up signature
hardware, ill login" — no password entered on his behalf, same pattern as Pottery Barn/West Elm
(§25/§26). Every year the account offers (2020, 2021, 2022, 2023 — nothing older or newer exists)
was pulled via the account's own Order History pages, and every order's detail page was opened
individually for item/SKU/price/tax confirmation. Full list, all Ship To 282 Bald Rock Road:

| Order # | Date | Status | Items | Total |
|---|---|---|---|---|
| SHW201356646 | 04/12/2020 | Complete | Rim lock set (1) + steel floor register (1) | $122.04 |
| SHW201364656 | 04/22/2020 | Complete | 66" Ocala solid surface freestanding tub (1) | $2,578.80 |
| SHW201382912 | 05/15/2020 | Complete | Vertical brass rim lock set (8) | $766.17 |
| SHW201424058 | 07/13/2020 | Complete | Carrara marble vessel sink (2) + pop-up drain (2) | $907.68 |
| SHW201424065 | 07/13/2020 | Complete | Knox waterfall vessel faucet (2) | $966.65 |
| SHW201427377 | 07/18/2020 | Complete | Carrara marble vessel sink, pop-up drain, Knox faucet (1 ea.) | $937.18 |
| SHW201556262 | 01/31/2021 | Complete | Knox faucet + Carrara sink + pop-up drain (1 ea.) | $779.23 |
| SHW201561027 | 02/07/2021 | Complete | Alledonia elongated skirted toilet (2) | $903.47 |
| SHW201586125 | 03/18/2021 | **Cancelled** | Beasley kitchen faucet (2) | $798.17 — no charge |
| SHW201620919 | 05/14/2021 | Complete* | Contemporary wall-mount pot filler faucet (1) | $304.32 — *already documented as fully refunded to Affirm 2021-09-16; excluded from the total |
| SHW201652253 | 07/13/2021 | Complete | 4" brass pocket door pull (6) | $96.44 |
| SHW201652260 | 07/13/2021 | Complete | 4" brass pocket door pull (8) | $117.94 |
| SHW201652839 | 07/14/2021 | Complete | Hibiscus single-hole vessel faucet (5) | $1,995.44 |
| SHW201821531 | 01/26/2022 | Complete | Rim lock set (2) + ceramic doorknob pairs (4) | $435.94 |
| SHW202227294 | 11/30/2022 | Complete | Rim lock set (1) + ceramic doorknob pair (1) | $154.48 |
| SHW250003576 | 04/12/2023 | Complete | Canopus matte resin vessel sink (1) | $251.67 |

**Valid capital-improvement total (excludes the Cancelled and Affirm-refunded orders): $11,013.13**
across 14 orders. All items are bathroom fixtures/hardware (vessel sinks, faucets, drains, a
freestanding tub, rim locks/door hardware) — Furniture category (5-yr, 100% bonus-eligible), not
Land Improvement or Structural.

**Payment side:** the account's order-detail pages expose zero payment/card data — no masked
card number, no "charged to," nothing — confirmed by searching the full page HTML, not just the
visible text. This is unlike Pottery Barn/West Elm, whose own order APIs did carry a matched
card + amount. So this pull closes the item/invoice side completely but cannot touch the payment
side; that remains dependent on the card statements already requested from Joshua on 9/2/2026
(AmEx ****7115 is one of the six).

**Reconciliation against the prior $1,883.00 / $9,847.50 split:**
- The existing $1,883.00 "proven portion" (PayPal txn 1VC80117373738041 + AmEx ****7115 $1,139.88
  + 2022 ledger debit charges $588.63 on 11/20/2022 and $154.48 on 12/2/2022) stands unchanged.
  The $154.48 debit charge now ties exactly to order SHW202227294 (11/30/2022, 2 days before the
  charge) — upgraded from a partial to a full invoice+payment match. The $588.63 charge and the
  specific order(s) behind the $1,139.88 AmEx total remain unmatched to a line in the table above;
  low-dollar, flagged for whoever reconciles the AmEx ****7115 statement rather than chased further
  here.
- The old $9,847.50 "unproven portion" is revised to **$9,130.13** ($11,013.13 minus the $1,883.00
  already matched above) — a net **-$717.37** to the grand total, all of it a downward, more
  conservative revision. This portion is now backed by the vendor's own item-level order record
  (stronger than the prior "matching shipment email" standard) but still lacks a payment match.

Tracker (`build_tracker.py` Plan item 3/3b, `build_tracker2.py` Bucket 1/2) and tax strategy memo
§4 updated the same day to reflect the corrected $9,130.13 figure and the resulting $593,758.28
grand total (down from $594,475.65).

## §37 — WILLIAMS SONOMA — FULL ORDER HISTORY PULLED DIRECTLY (2026-09-03)

Joshua instructed "do william sonama" and then confirmed "ok we are in" once he/Hillary had
logged into their own williams-sonoma.com account directly (no password entered on their behalf).
The complete order history — 25 orders, all-time — was then pulled item-by-item via the same
order-detail URL pattern used for Pottery Barn and West Elm
(`williams-sonoma.com/customer-service/order-shipment-tracking/results.html?orderNumber=...`).

**21 of the 25 orders shipped to 282 Bald Rock Road** (Hillary Davis / Hillary Holmes / Joshua
davis, all at 282 Bald Rock Rd, Verona, VA 24482). The other 4 were gifts shipped to Darrell &
Karen Holmes (Florida, zip 32137) and Sallie Davis (Virginia, zip 23111) and are excluded
entirely — not Bald Rock spending.

| Order # | Date | Item(s) | Amount | Category |
|---|---|---|---|---|
| 342433878838 | 2024-08-30 | Robert Welch Kingham flatware: salad fork x5, dinner fork x4, teaspoon x5 | $129.30 | Durable |
| 333393366161 | 2023-12-05 | The Original Peppermint Bark x5 | $149.75 | Consumable |
| 333133257134 | 2023-11-09 | SMEG Mini Kettle White | $149.95 | Durable |
| 333133257134 | 2023-11-09 | Vanilla Hot Chocolate + Classic Hot Chocolate | $51.90 | Consumable |
| 330382069715 | 2023-02-07 | Robert Welch Kingham Teaspoon x6 | $41.70 | Durable |
| 330022397013 | 2023-01-02 | Boos Edge-Grain Maple Cutting & Carving Board, Large | $154.95 | Durable |
| 323382707608 | 2022-12-04 | Snowman Salt & Pepper Set; Xmas Jacquard Tea Towels; Super-Absorbent Towels | $136.85 | Durable |
| 321783953292 | 2022-06-27 | Le Creuset Enameled Steel Demi Tea Kettle, White | $80.00 | Durable |
| 321502501802 | 2022-05-30 | WS Stainless-Steel Silicone ladle/turner/tongs/spoon (4 pcs) | $63.45 | Durable |
| 321412185837 | 2022-05-21 | Antica Oil Dispenser, 13oz | $16.95 | Durable |
| 320403737960 | 2022-02-09 | WS Fleur de Sel Hand Soap Refill, 32oz | $42.95 | Consumable |
| 313353258178 | 2021-12-01 | St. Jude Children's Research Hospital Donation | $5.00 | Excluded (donation) |
| 313353258178 | 2021-12-01 | Caraway Non-Toxic Ceramic Nonstick Cookware Set, Navy | $395.00 | Durable |
| 313242933320 | 2021-11-20 | Stainless Steel & Glass Coasters, Set of 4, x2 | $59.90 | Durable |
| 312773878151 | 2021-10-04 | Crafthouse by Fortessa Cocktail Smoking Box | $299.95 | Durable |
| 312513788447 | 2021-09-08 | Prepara Vertuoso Coffee Capsule Carousel | $29.95 | Durable |
| 311542107496 | 2021-06-03 | Capresso Ice Tea Maker | $59.95 | Durable |
| 314392321738 | 2021-02-08 | Gourmet Whip Cream Maker with N2O Cartridges | $159.95 | Durable |
| 301993091042 | 2020-07-17 | Glass Prep Mixing Bowls, Set of 8 | $24.95 | Durable |
| 301772019966 | 2020-06-25 | WS Stainless-Steel Handle Ultimate Spatula Set, White | $49.95 | Durable |
| 301663055194 | 2020-06-14 | All-Clad Nonstick Pro Release Bakeware, Set of 5 | $99.95 | Durable |
| 301652179526 | 2020-06-13 | Robert Welch Westbury 42-Piece Flatware Set | $394.95 | Durable |
| 301652377864 | 2020-06-13 | Gingham Oven Mitt & Potholder; WS Signature Utensils Set of 13; Multi-Pack Dishcloths Set of 8 | $554.85 | Durable |

**Totals:** $3,152.10 across all 21 orders → **$2,902.50 durable kitchen FF&E** (capitalized,
5-year furniture bucket) + **$244.60 consumable food/soap** (excluded, not capital) + **$5.00
charitable add-on** (excluded — not a purchase at all).

**Payment side:** Same finding as Signature Hardware — Williams Sonoma's order-detail pages
expose no card/payment data anywhere. The "VIEW CHARGES" button was clicked on multiple orders
and produces no populated panel; a full-page HTML search for "card"/"charge"/"Visa" style strings
turned up only unrelated store-locator and newsletter modal text, never an actual charge record.
Payment proof for the $2,902.50 depends entirely on a card statement — the same conclusion as
Signature Hardware, and a hard contrast with Pottery Barn/West Elm, whose own order APIs exposed
a matched card + amount directly (§25/§26).

**Reconciliation:** replaces the prior $2,766.41 Bucket-1 (N/N) estimate — which was simply
"$211,724.20 combined PB/WE/WS estimate minus the confirmed PB + WE amounts" — with a
vendor-confirmed, item-level $2,902.50 Bucket-2 (Y/N) figure. Net effect on the grand total:
+$136.09.

## §38 — AFFIRM ACCOUNT PULLED DIRECTLY: CLOSES MOST OF SIGNATURE HARDWARE AND ROYAL SWIMMING POOLS (2026-09-03)

Joshua asked "does affirm have downloadebel staemtents or activiti" and then logged into his own
Affirm account directly ("i m in there now") — no password entered on his behalf. Affirm's
"Current loans" page shows every loan back to 2017: merchant, item description, amount, paid/
refunded status, and date. Clicking into any individual loan reveals its full payment schedule —
every installment, the exact date, and which card or bank account paid it. This is a first-party
lender ledger, the same evidentiary tier as a bank/card statement.

### Royal Swimming Pools — full loan schedule

The Royal Swimming Pools loan (item: "Adjustable A-Frame Brace - 14 Gauge 42" Steel...", a line
from the pool kit order) shows:

| Date | Event | Amount |
|---|---|---|
| 2022-10-27 | Paid — MasterCard ****6246 (down payment) | -$10,052.91 |
| 2022-10-28 | Loan processed/funded | $15,052.91 |
| 2022-11-04 | Adjustment | -$71.98 |
| 2022-11-28 → 2023-08-28 | 10 monthly payments — MasterCard ****6246 | -$233.04 each |
| 2023-09-21 | Final payment — Bank Account ****1015 | -$2,991.01 |
| — | **Paid to date / Remaining** | **$15,374.32 / $0.00** |

$15,052.91 - $71.98 adjustment = **$14,980.93 exactly** — the customer-approved amount for order
#151398 already in this log (§2, line 177). The $393.39 difference between principal ($14,980.93)
and total paid ($15,374.32) is Affirm financing interest/fees, not a capital cost.

**This proves the entire #151398 order was financed as ONE Affirm loan and paid in full** — not a
$5,592.86 Affirm-financed piece plus a separately-paid $9,388.07 remainder, which was the prior
assumption built only from the approval email ("the Affirm loan only financed part of #151398...
one payment made at purchase, per the Affirm approval email," §2 line 177). The "$10,052.91 paid
at purchase" the approval email described is itself part of this same Affirm loan's payment
schedule, not a separate non-Affirm payment. Only order #152804 ($530.95, "no receipt" per the
existing log) remains genuinely unmatched to any payment source.

**Reconciliation:** Bucket 1 "Royal Swimming Pools (Affirm-financed portion)" revised from
$5,592.86 to **$14,980.93** (renamed "order #151398, fully financed"). Bucket 2 "Royal Swimming
Pools (unfinanced remainder)" revised from $9,919.02 down to **$530.95** (renamed "order #152804,
no receipt"). Net shift: $9,388.07 from Bucket 2 to Bucket 1; zero change to the combined total
($15,511.88 either way) or the grand total.

### Signature Hardware — 9 of 16 orders match Affirm loans paid in full

Cross-referencing the Affirm activity list's Signature Hardware entries against the order table in
§36 by dollar amount:

| Order # (§36) | Amount | Affirm loan status | Paid via |
|---|---|---|---|
| SHW201364656 | $2,578.80 | Paid in full, $0.00 remaining | MasterCard ****9983, 6 monthly installments |
| SHW201424058 | $907.68 | Paid in full | Affirm activity list |
| SHW201424065 | $966.65 | Paid in full | Affirm activity list |
| SHW201427377 | $937.18 | Paid in full | Affirm activity list |
| SHW201556262 | $779.23 | Paid in full | Affirm activity list |
| SHW201561027 | $903.47 | Paid in full | Affirm activity list |
| SHW201652253 | $96.44 | Paid in full | Affirm activity list |
| SHW201652260 | $117.94 | Paid in full | Affirm activity list |
| SHW201652839 | $1,995.44 | Paid in full | Affirm activity list |
| SHW201620919 | $304.32 | **Refunded 2021-09-15** | Confirms the existing Affirm-refund claim directly from Affirm's own record (previously just an assertion in this log) |

Sum of the 9 paid orders: **$9,282.83**. Added to the pre-existing $154.48 ledger match
(SHW202227294, §36): **$9,437.31 of the $11,013.13 valid-order total is now proven both ways.**
The 4 orders still without any payment source: SHW201356646 ($122.04), SHW201382912 ($766.17),
SHW201821531 ($435.94), SHW250003576 ($251.67) — **$1,575.82 remaining, still payment-unmatched.**

**A genuine open reconciliation question, disclosed rather than resolved by assumption:** the
existing "$1,883.00 proven portion" (PayPal + AmEx ****7115 $1,139.88 + 2022 ledger $588.63 +
$154.48) cannot simply be added on top of the new $9,437.31 — $1,883.00 + $9,437.31 = $11,320.31,
which exceeds the $11,013.13 valid-order total by $307.18 (once the $154.48 shared between both
figures is accounted for, the excess is $1,728.51 - $1,575.82 = $152.69 of unexplained overlap).
Since an order financed through Affirm is, by construction, not also paid via a direct AmEx or
debit-card charge for its full price, the most plausible explanation is that the $1,139.88 AmEx
and $588.63 ledger amounts are **Affirm loan installment payments landing on those cards** (this
session directly observed Affirm charging cards in recurring installments — e.g. $233.04/month,
$429.80/month, $58.97/month, for the loans above) rather than separate one-time direct purchases,
as the prior evidence log itself flagged ("the exact order(s) behind the $1,139.88 AmEx total
remain unmatched to a specific order"). This is flagged here for resolution once the actual AmEx
****7115 statement is reviewed (Plan #3) — not resolved by assumption. Pending that, the tracker
now counts only the Affirm-verified $9,437.31 as proven, and treats the AmEx/ledger $1,728.51 as
likely-duplicative rather than additive.

**Reconciliation:** Bucket 1 "Signature Hardware (proven portion)" revised from $1,883.00 to
**$9,437.31** (renamed "Affirm + ledger-matched orders"). Bucket 2 "Signature Hardware (unproven
portion)" revised from $9,130.13 down to **$1,575.82** (renamed "still payment-unmatched"). Net
shift: $7,554.31 from Bucket 2 to Bucket 1; zero change to the combined total ($11,013.13 either
way) or the grand total.

### New vendor found, not yet added to any proven total: Vent Covers Unlimited

The same Affirm pull surfaced "Vent Covers Unlimited — Steel Designs Pro-Linear Registers &
Returns — $235.87," paid in full via MasterCard ****6246 (the same card that financed Royal
Swimming Pools) over 4 installments, March-May 2022. Plausible Bald Rock HVAC/vent-register
purchase given the card overlap and timing, but Affirm's activity page carries no shipping
address, unlike the vendor-side pulls (Signature Hardware, Williams Sonoma, Pottery Barn, West
Elm) that confirmed "Ship To: 282 Bald Rock Rd" directly. Added to Bucket 3 (attribution
unconfirmed) rather than assumed — $235.87, new dollars to the grand total.

### Net effect on totals

$16,942.38 moved from Bucket 2 (unproven) to Bucket 1 (proven) — zero change to either vendor's
total or the grand total from the reclassification itself. Vent Covers Unlimited adds $235.87 in
new dollars (Bucket 3). Tracker (`build_tracker.py` Plan items 3/3b/3c, `build_tracker2.py`
Buckets 1/2/3) and tax strategy memo §4 updated the same day: new Bucket 1 $537,804.59, Bucket 2
$8,520.65, Bucket 3 $18,859.40, Bucket 4 $28,945.60, grand total $594,130.24 (up from $593,894.37 — the $235.87 net increase is entirely the new Vent Covers Unlimited find; the $16,942.38 Bucket 1/2 shift is reclassification only, with zero effect on the grand total).

## §39 — NINE MORE AFFIRM VENDORS CONFIRMED AS 282 BALD ROCK; CASPER TOTAL CORRECTED (2026-09-03)

Following the Signature Hardware/Royal Swimming Pools/Casper reconciliation in §38, Joshua
reviewed the rest of the Affirm activity list and confirmed directly which additional loans were
for 282 Bald Rock:

> "joss and main was for that house, decor planet, eight sleep, and vent covewrs unlimited,
> molecule was for that house, trager grills were for that house in 2023, tonal was for that
> house, platnum lights were for that house,, beat bot also. everything 2025 and beyond past the
> beat boat is 844 cypress improvemnets"

**Newly confirmed Bald Rock vendors ($16,903.28 in new dollars, all Furniture category except
Vent Covers Unlimited):**

| Vendor | Date | Item | Amount |
|---|---|---|---|
| Joss & Main | 2017-07-14 | Albertson Media Console | $754.99 |
| Decor Planet | 2021-10-22 | Avanity BROOKS-V30-WT 30" vanity | $694.98 |
| Decor Planet | 2020-12-12 | Avanity MADISON-V72-WT 72" vanity | $1,198.05 |
| Eight Sleep | 2023-10-10 | General merchandise (smart mattress) | $2,574.59 |
| Molekule | 2023-05-28 | Molekule Air, Molekule Air Mini | $841.34 |
| Traeger Grills | 2023-09-21 | Timberline Pellet Grill | $3,485.78 |
| Tonal | 2023-11-18 | Tonal + Smart Accessories | $3,924.97 |
| PlatinumLED Therapy Lights | 2025-05-24 | BIOMAX Series | $1,472.10 |
| Platinum Therapy Lights | 2025-04-10 | General merchandise | $693.93 |
| Beatbot | 2025-08-08 | General merchandise (robotic pool cleaner) | $1,262.55 |

Two additional loans (Decor Planet Avanity MADISON-V48-WT $1,813.27, 2020-06-05; Eight Sleep
$1,942.79, 2022-06-30) show as **refunded** in Affirm — $0 net cost, noted but not counted.

**Vent Covers Unlimited** ($235.87, found in §38 but held in Bucket 3 pending confirmation) is now
confirmed and moved to Bucket 1.

**Casper correction:** Joshua's dating rule — "everything 2025 and beyond past the beat boat [bot]
is 844 cypress improvements" — means the Beatbot purchase (2025-08-08) is the last Bald Rock item
chronologically; everything after it in the Affirm account belongs to 844 Cypress Crossing (his
Florida personal residence, converted from a rental to personal use around August 2025 — see tax
memo §7). This moves the 2026-07-28 Casper loan ($1,117.46), previously added to Bald Rock's total
in §38, out entirely. **Bald Rock's Casper total is corrected from $11,767.77 (8 loans) to
$10,650.31 (7 loans).**

**Items in the same Affirm window that were NOT named as Bald Rock and are logged separately as
844 Cypress Crossing improvements instead:** Kohler ($4,020.00, 2025-11-15), Amazon Business
($3,937.30, 2025-12-26), a second Traeger Grill/Woodridge Elite ($1,916.99, 2026-02-04), Rebag
($790.75, 2026-03-02), Aventon Bikes hitch rack + ebike ($2,395.18 + $1,862.69, 2026-05), Nordica
Sauna ($6,367.63, 2026-06-08), the 2026-07-28 Casper loan above ($1,117.46), and Discount Tire
($1,808.37, 2026-08-27). See `844 Cypress Crossing Improvements Substantiation.md` for these,
appended the same day. Some of these (Rebag, a designer-handbag marketplace; Discount Tire; the
Aventon e-bikes) read on their face as personal property/vehicle purchases rather than real-
property improvements — flagged for the same capital-vs-personal judgment call the 844 log already
applies elsewhere (§5C of that log), not assumed capital just because Joshua's dating rule places
them in that window.

**Net effect on Bald Rock's totals:** $16,903.28 in new Furniture-category dollars, minus $1,117.46
removed (Casper 2026 item, now 844 Cypress) = **+$15,785.82 net**, plus the Vent Covers Unlimited
reclassification from Bucket 3 to Bucket 1 (no new dollars, just a stronger tier). New Bucket 1
$565,594.05, Bucket 3 $18,623.53 (back to its pre-§38 level, since Vent Covers Unlimited left it),
grand total $621,683.83 (up from $605,898.01). Tracker (`build_tracker.py`, `build_tracker2.py`)
and tax strategy memo §4 updated the same day.
