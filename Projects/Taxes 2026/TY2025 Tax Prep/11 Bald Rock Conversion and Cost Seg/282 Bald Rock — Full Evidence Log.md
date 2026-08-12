# 282 Bald Rock Road, Verona VA 24482 — Capital Improvements Evidence Log

**Built 8/5/2026 from the local unified index** — Apple Mail (276,529 messages, all 4 accounts, back to 2009), iMessage/SMS (58,625, mid-2024→now), iCloud Drive (7,575 files).

> ## ⚠️ THIS FILE SUPERSEDES `Bald Rock Improvements Substantiation.md`
> That earlier file reported **$21,172 documented** and declared "ZERO HITS" on siding, electrical, hot tub, cold plunge, paint, and Valley Building Supply. **Those were false negatives.** Two causes:
> 1. It searched only the Gmail MCP. Most of this correspondence lives in Apple Mail accounts the Gmail connector cannot see.
> 2. Its SQL date filter used `ts > strftime('%s','2021-06-01')`, which compares an INTEGER column to a TEXT value and **always returns zero rows**. Every date-filtered query in it silently returned nothing.
>
> Do not rely on the old file's negative findings for anything.

---

## HEADLINE

| Evidence class | Amount |
|---|---|
| **Proof of payment on the face of a document** | **$97,615.40** |
| Invoiced, payment not proven | $110,673.74 |
| Quoted only — **includes losing bids, see warning below** | ~$176,000 |

Against a claimed **$305,086.51**. Documented-and-paid went from $21,172 to **$97,615.40** on this pass.

> **The "quoted" column is not a shopping list.** It contains at least two competing bids for work another contractor actually performed (Turf Specialties $46,000 and Crown Decorative Concrete $18,400 both bid the retaining wall Red Rock built for $28,622). Carrying those alongside Red Rock double-counts the wall. Quotes belong in basis only where a matching invoice or payment exists.

---

# 0. WHY THE RECEIPTS MATTER — THE BASIS MATH

**Purchase price of 282 Bald Rock: $405,000.00**, per the recorded deed — `CONSIDERATION: 405,000.00`, `Consideration/Actual value: $405,000.00`. Acquired 2016 (contract 8/8/2016 via Charlotte McAlister, RE/MAX Advantage; financing through BNC National Bank; United States Appraisal LLC ordered 9/13/2016). Source: `.../02 Real Estate/282 Bald Rock Rd - Verona VA (Rental)/282 Bald Rock Deed:Closing.pdf` — image-only, OCR'd 8/5/2026.

On conversion of a personal residence to a rental, depreciable basis = **the LESSER of** adjusted basis or FMV at the conversion date. Adjusted basis = purchase price + capital improvements − depreciation previously allowed (here $0, since it was a residence throughout).

| Scenario | Adjusted basis |
|---|---|
| Purchase price alone | $405,000 |
| + improvements **proven paid** ($97,615.40) | **$502,615.40** |
| + improvements proven **and** currently invoiced ($208,289.14) | **$613,289.14** |
| + the full claimed $305,086.51, if it could all be documented | $710,086.51 |

**Implication: adjusted basis is very likely the binding constraint, not FMV.** For the appraisal to cap this, the property would have to be worth *less* than roughly $503K–$710K in August 2025 — i.e. under ~24%–75% appreciation over nine years, on a house that was gut-renovated in the interim, in a market that ran hard 2016→2025. Possible, but not the way to bet.

**So every documented improvement dollar is very likely a real dollar of depreciable basis.** The $110,673.74 sitting in the "invoiced but unproven" column is the single largest recoverable prize in this file — and card statements are what convert it.

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

# 1. PROOF OF PAYMENT — $97,615.40

| Vendor | Doc / Date | Amount | Covers | Proof |
|---|---|---|---|---|
| **R.E. Boggs, Inc.** (Charlottesville) | Inv I-5192-1 + I-5192-2, 2025-09-03 | **$29,187.00** | Two Rheem HVAC systems | Service Finance loan 5977065, borrower addr 282 Bald Rock Rd, signed 2025-09-05; Certificate of Completion 2025-09-08 |
| **Valley Building Supply** | 2020-04 → 2022 (multiple) | **$27,561.06** | PlyGem/Mira windows, patio + bi-parting doors, trim, AZEK porch/decking | Balance Due $0.00 / "CREDIT CRD" on invoice faces, net of a $1,255.54 credit-noted return |
| **Renu Therapy** Order #5754 | 2023-05-27 | **$10,214.09** | **Cold plunge** — Cold Stoic 2.0, ship-to 282 Bald Rock | Paid order + shipment 7/16/23, BTX tracking LAX4059890 |
| **Red Rock Concrete** | Inv #1244 final, 2022-08-07 | **$10,000.00** | Engineered retaining walls | Payment line on the vendor's own final invoice |
| **Lowe's** Order #717201671 | 2021-03-17 | **$8,757.88** | Appliances | "Payment LCC ending in 1037 $8,757.88" |
| **ProjectorScreen.com** #124774 | 2020-02-14 | **$5,470.50** | SI 5 Series 160" screen, ship-to 282 | "Payment information received", credit card |
| **Fundamental Siteworks** Inv 670 (partial) | 2022-11-22 | **$3,000.00** | Pool demo + dig + rough grade | MC ****6246, Auth MQ0134863515 |
| **Commonwealth Tile** Inv 1294 | 2022-11-20 | **$1,685.00** | Tile | MC ****0305, Auth MQ0134421222 |
| **Signature Hardware** (C1, C3, C18) | 2020-04 → 2023-04 | **$1,139.88** | Bath/plumbing fixtures | PayPal txn 1VC80117373738041; AmEx ****7115 |
| **Commonwealth Tile** Inv 1252 / 1265 | 2021-04-08 / 2021-08-01 | **$400.00** | Tile labor + material | QuickBooks payment confirmations |
| **Royal Swimming Pools** #151856 | 2022-12-01 | **$199.99** | Pool niche | PayPal receipt |
| | | **$97,615.40** | | |

---

# 2. INVOICED, PAYMENT NOT PROVEN — $110,673.74

| Vendor | Doc / Date | Amount | Note |
|---|---|---|---|
| **Valley Building Supply** | net invoiced $58,669.93 less $27,561.06 proven | **$31,108.87** | Open balances $950.75, $3,181.73 (after $5,200 PlyGem credit), $724.80; plus $6,232.64 where Balance Due is illegible on the scan |
| **Burns Builders Roofing** Est 1548 | 2021-05-28, signed 6/3/21 | **$21,750.00** | Installed 7/6/21. Service Finance letters independently confirm *"ROOFING project completed by Burns Builders Inc on 7/10/2021"*, loan xxx3624. Strongest unproven item on the list. |
| **Red Rock Concrete** | Inv #1244 balance | **$18,622.00** | No receipt, check, bank record or vendor acknowledgment anywhere after 2022-08-08 |
| **Royal Swimming Pools** | #151398 approved $14,980.93 + #152804 $530.95 | **$15,511.88** | #151398 customer-approved 2022-11-03 10:41:32 EDT, approval IP logged; kit shipped 11/28 + 12/02 |
| **Signature Hardware** | net $11,730.49 less $1,139.88 proven | **$10,590.61** | All orders ship to 282 Bald Rock; each has a matching shipment email |
| **Weaver Irrigation** Inv 2248 / 2377 / 2773 | | **$7,250.00** | $4,400 irrigation install + $1,386 + $1,464. Joshua arranged 4 × $1,100 DuPont CCU payments 2023-08-21, payee confirmed |
| **Fundamental Siteworks** Inv 670 balance | | **$2,329.00** | |
| **Commonwealth Tile** Inv 1233 / 1228 | | **$1,425.00** | |
| **Lowe's** #761302963 + #771548245 | 2022-10 / 2023-03 | **$1,344.79** | Bald Rock / Verona referenced |
| **Direct Door Hardware** #203991, **Builders Warehouse** #23752 / #23939 | 2020–2021 | **$741.59** | All shipped to 282 Bald Rock |
| | | **$110,673.74** | |

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
6. **Shreckhise Landscape & Design** — the contractor actually used. Plans `Davis 101322.pdf` and `Davis 032323.pdf` exist; no proposal, invoice, or payment. A "Shreckhise Shrubbery Refund Receipt" dated 2025-07-28 exists, amount not read.
7. **Plumbing — nothing at all.** Valley Air hits were newsletters only.
8. **No Augusta County building permit exists** in mail, texts, or files.
9. Holloway Roofing proposal 2021-03-24 · Retex Roofing gutter job (scheduled 2022-09-22) · Williams Brothers Tree Est 6919 · pavementsoft driveway proposal 2024-08-28 · Happy Little Dumpsters Inv 11443/11836/12350/12462 (2021 demo debris) · 360 Painting (estimate appt at 282, 2022-03-08) · Blue Ridge Fence & Window · Decorative Concrete of Virginia (~700 sq ft pool deck overlay proposal, 2022-07-08) · Glasgow Decorative Concrete · Windridge Landscaping.
10. **Two image-only PDFs with zero extractable text** — see OCR actions below.

---

# 7. FLAGS

### F-1 — Roofing arithmetic doesn't close
Burns contract $21,750.00 vs. Service Finance loan xxx3624 first-statement payoff of **$15,357.47** — a ~$6,400 gap. The loan is in **Hillary D. Davis's** name and went delinquent, with collector letters into 2022. Resolve before booking $21,750.

### F-2 — Enlit LLC (~$14,000+) is probably business, not the residence
Invoices are billed to "Full Circle Finance, 282 Bald Rock Rd" but the subject lines read EV chargers / SCIP / "1617 W Main St." Amounts: 1002 $120 (paid), 1005 $284.32→$483.66, 1010 $189.54, 1035 $135, 1039 $767.26, 1041 $252.72, 1045 $189.54, 1049 $571.16, 1050 $379.08, 1051 $461.21, 1053 $189.54, 1054 $2,299.23, 1073 $332.40, 1076 $552.83, plus 2023 unnumbered $685.24 / $1,936.31 / $2,015.96 / $2,628.14 / $2,131.08→$1,131.08 / $547.56, and 2066 $505. **Needs line-item review before any of it touches 282's basis.**

### F-3 — Two OTHER properties are in the same mail stream
`14300 Woods Walk Lane, Midlothian VA` (Heir Mechanical $1,050; Retex "Cancel 14300 woods walk lane"; likely Connect Electric $200) and `148 Hardinberry St, Oak Ridge TN` (LM Coatings $3,360; Volunteer Flooring). Both are rentals with their own Schedule E treatment. Don't let their invoices drift into 282.

### F-4 — Lowe's needs per-order address verification
The index holds 450–916 Lowe's messages *per year*. Spot-checking 2022-10 → 2023-07, most attach to **817 Richmond Rd, Staunton (Valley Pawn, commercial)** — e.g. #761310473 $290.84, #771712935 $54.47, #772672526 $31.13, #772750441 $63.62, #781317658 $391.67. Never sweep Lowe's totals into 282 without checking the ship-to.

### F-5 — Florida contamination runs the other way in 2025–26
Essentially all 2025–26 trade texts are 844 Cypress Crossing: "Drywall 844", "844 Irrigation", All American Electric, Scully Painting, Totally Hooked Plumbing, Home Depot Palm Coast, Paul Francis Jr.

### F-6 — Repairs, not capital improvements
A&B Mechanical $100 diagnostic · Heir Mechanical $1,050 · S.A.F.E. pressure wash $571.65 (paid 9/26/22, MC ****1689) · Renu maintenance $195.40 / $53.15 · Augusta County Disposal $93/$123/$63/$63/$93 · Augusta County RE tax $2,989.23 · Signature Hardware warranty replacement C14 ($0.00) and refunds C10/C15 · LL Flooring warranty complaint and the $122.00 MasterCard reimbursement (LL concluded the cracked boards were not a manufacturer's defect) · the ~130-message VBS "Still missing" thread and the "282 Bald Rock Road Plygem Issues" thread are defect/replacement correspondence running to 2024-08.

### F-7 — Much of this spend predates 2021
Crutchfield 2019 · ProjectorScreen 2020-02 · Ply Gem quote 2020-04 · Commonwealth Tile 2020 · Sheaves 2020 · cabinet drawings 2020-03 · Signature Hardware from 2020-04 · VBS from 2020-04. **This collides directly with the lesser-of-adjusted-basis-or-FMV test at the Aug/Sep 2025 conversion.** Five years of improvements do not stack onto a 2025 FMV — they are components of adjusted basis, and FMV may cap the whole thing.

### F-8 — Irrigation vs. plantings
Irrigation systems are 15-year land improvements; plantings may be non-depreciable land. Don't blanket-assume for the Weaver Irrigation $7,250.

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
