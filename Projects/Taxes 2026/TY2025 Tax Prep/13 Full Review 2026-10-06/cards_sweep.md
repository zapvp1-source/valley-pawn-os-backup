# Card & Loan Sweep — TY2025 (read-only)

Prepared 2026-10-06. Sources actually read:

| Source | Coverage | Notes |
|---|---|---|
| Apple Card PDFs (Jan–Dec 2025, 12 files, ~/Downloads) | 176 transactions + 27 Apple installment entries | Parsed transaction totals tie to every statement's "Total charges, credits, and returns" except for pennies of "Daily Cash Adjustment" rows. The pre-parsed `apple-card-2025-detail.csv` (199 rows) matches the PDFs exactly for every real purchase/refund; it additionally lists the Daily Cash Adjustment rows and omits the Apple Card Monthly Installment entries. PDFs treated as source of truth. |
| Amex "Card 3001" — `Amex Card 3001 - Pending Transactions.csv` (3,421 rows, 2025–2026) + `American_Express*.csv` ×7 | 2,517 unique 2025 rows after de-dupe on date+description+amount | The 7 small `American_Express*.csv` files are all subsets of the big file (the only two rows not in it are two 2026 "Autopay Thank You" credits). **Data caveat:** the big file is unquoted CSV, so every amount ≥ $1,000 is split on the thousands comma; re-parsed by hand. Descriptions in this export are truncated bank names ("Premier", "Augusta", "Lighting"), so vendor identity is sometimes inferred — flagged where so. This card carries heavy Valley Pawn business spend (Comcast, Security, Surety Bonds, Firearms Explosives, etc.). |
| Chase `2025MMDD-statements-3009-.pdf` ×12 | Fisker Finance auto loan, HILLARY D DAVIS, 2023 Fisker Ocean, 3.99% | Statements dated 01/06/25 – 12/05/25 |
| Chase `2025MMDD-statements-8048-.pdf` ×12 (+ 20260106) | **Rivian Financial Services auto LEASE**, JOSHUA C DAVIS, 2024 Rivian R1S, 36 mo, matures 05/24/2027 | Not a card, not a loan — a lease. No interest component. |
| Pottery Barn card (Hillary) `.../2025/November 2025 Statement.pdf` | Only 2025 statement on file (Oct 09 – Nov 07, 2025) | Card is now "Pottery Barn Key Rewards Visa … ending in 4362", issued by **Capital One** (was Comenity). **$0.00 previous balance, $0.00 transactions, $0.00 new balance.** No 2025 purchases on this card; nothing to assign to Verona vs St Augustine. The 2025 Pottery Barn spend is on the Amex (see §E/§J). |
| Reference: `pl_sent.txt`, `wf_all.txt` | — | Used only for reconciliation. |

Amounts are verbatim from the statements; descriptions quoted as printed. "Amex" = Amex Card 3001. Nothing was estimated for missing months.

---

## A. Health premiums

| Date | Description (verbatim) | Amount | Card |
|---|---|---|---|
| 08/06/2025 | Te Florida Health | 1,019.59 | Amex |
| 11/21/2025 | Te Florida Health | 2,027.57 | Amex |
| **Total 2025** | | **3,047.16** | |

- 11/21 charge ≈ 2 × $1,013.79; 2026 charges run on the 21st (01/21/26 $1,944.62, 02/21/26 $1,862.06, 03/21/26 & 04/21/26 $931.03), so the plan continues. **No FHCP charge found for Sep, Oct or Dec 2025 on any card** — either paid from a bank account not in this sweep or covered by the double charge.
- Anthem / HealthKeepers: nothing on Apple, Amex or Chase. (WF file shows "Anthem Blue Individual … Full Circle Finance *I" $500.16/mo — business account, outside this sweep.)
- Marketplace: none.

## B. HOA

| Item | Result |
|---|---|
| Woodlake Community Association (14300 Woods Walk) | **Not on any card.** P&L says DuPont acct 2291 ACH. |
| Southland Property Management (148 Hardinberry) | **Not on any card.** P&L says DuPont acct 2291 ACH. |
| Palencia (844 — personal) | Amex "The Palencia Club" 06/04 $292.72, 11/29 $8.00, 12/04 $56.71, 12/05 $186.72, 12/12 $248.00, 12/13 $339.03 (club dues/dining, personal); "Mybooster Palencia" 08/26 $80.50; "Schlpay Palenciaes" 09/09 $10.60 (school). No HOA assessment charge visible. |

## C. Property taxes

| Jurisdiction | Result on cards |
|---|---|
| Augusta County | **No tax payment on cards.** (Amex "Augusta" monthly charges are the water/sewer bill — see §E.) |
| Chesterfield County | Amex "Chesterfield" 02/09 $6.35, 06/05 $3.00, 06/22 $14.85 — too small to be tax (likely parking/fees). No tax bill. |
| Roane County / City of Oak Ridge | **Nothing.** ("Roanoketax Rxxxxxx Va" 11/11 $10.68 is Roanoke VA, a Valley Pawn store city — not Roane County TN.) |
| City of Staunton | **Not on cards.** WF: "Business to Business ACH Debit - Cityofstaunton Web Pmts 071025" $798.17 (matches P&L 817 Richmond) and "Bill Pay City of Staunton" 06/04 $126.90. |
| St Johns County | Amex "St Johns County" monthly 01/08 $131.04, 02/16 $48.99, 03/16 $44.39, 04/16 $32.46, 05/17 $37.16, 06/16 $33.88, 07/17 $56.63, 08/16 $33.69, 09/16 $225.58, 10/17 $108.00, 11/16 $111.71, 12/17 $123.20 = $986.73 — monthly pattern = **utility (water) for 844, personal**, not property tax. "St Johns" 10/17 $328.00 and "Aplpay St Johns" 10/09 $53.70 — unidentified county fee (permit?). No property-tax-sized payment. |

## D. Insurance

| Date | Description | Amount | Card |
|---|---|---|---|
| 01/09/2025 | Bt Steadily Ins | 98.80 | Amex |
| 02/09 – 11/09/2025 (10 × monthly, 9th) | Bt Steadily Ins | 80.85 each = 808.50 | Amex |
| 12/09/2025 | Bt Steadily Ins | 80.70 | Amex |
| **Steadily total 2025** | | **988.00** | |

- Only one Steadily policy is billed to the cards (a single ~$80.85/mo stream). It continues at $80.00/mo in 2026.
- Travelers, Homesite, GEICO, Kin: **nothing on any card.**
- Progressive: not on cards (WF card 5075 pays "Progressive Ins" monthly $244.49 → $464.35 — auto, in WF file).
- Other insurance-type items on Amex: "Surety Bonds" 08/05 $100.00, 11/10 $250.00; "Kingfish" ~$59/mo (business).

## E. 282 Bald Rock (Verona VA)

### E1. Aug–Dec 2025 (rental period)

| Date | Description (verbatim) | Amount | Card | Category / note |
|---|---|---|---|---|
| 08/04/2025 | Premier | 690.00 | Amex | Cleaning — "Premier" is truncated; Apple shows the same vendor as "SQ *PREMIER CLEANING S312 W Water St gosq.com 22801 VA" (Harrisonburg). Probable. |
| 08/12/2025 | Premier | 690.00 | Amex | Cleaning (probable) |
| 09/02/2025 | Premier | 190.00 | Amex | Cleaning (probable) |
| 09/02/2025 | Premier | 90.00 | Amex | Cleaning (probable) |
| 10/03/2025 | Premier | 180.00 | Amex | Cleaning (probable) |
| 10/31/2025 | Premier | 135.00 | Amex | Cleaning (probable) |
| 11/12/2025 | Premier | 135.00 | Amex | Cleaning (probable) |
| | **Premier Aug–Dec subtotal** | **2,110.00** | | **Not in P&L** (P&L cleaning = Lam's $8,100 only) |
| 08/05/2025 | Augusta | 4.00 | Amex | Water/sewer (Augusta County Service Authority). WF paid "Doxo Util Dox*Augusta" $37.99/mo Jan–Jun; billing moved to Amex from July. |
| 09/08/2025 | Augusta | 4.00 | Amex | Water/sewer |
| 10/06/2025 | Augusta | 38.00 | Amex | Water/sewer |
| 11/05/2025 | Augusta | 38.00 | Amex | Water/sewer |
| 12/08/2025 | Augusta | 38.00 | Amex | Water/sewer |
| | **Augusta water Aug–Dec subtotal** | **122.00** | | **Not in P&L** |
| 12/30/2025 | Agp Btpropane Pa | 193.58 | Amex | AmeriGas propane — the only Aug–Dec propane charge on any card |
| 11/01/2025 | Aplpay Lowe St | 426.36 | Amex | Lowe's Staunton — nearest Lowe's to Verona; property not provable from the card |
| 11/07/2025 | Aplpay Lowe St | -144.39 | Amex | refund |
| 11/25/2025 | Aplpay Lowe St | 2.12 | Amex | |
| 09/27/2025 | Aplpay Sherwin W | 54.22 | Amex | Sherwin-Williams, location unknown |
| 12/09/2025 | Sp Painting | 112.50 | Amex | Unknown painter (Square) |
| 11/11/2025 | Avail Services | 75.00 | Amex | Avail (rental listing) — more likely Woods Walk, see §G |

Not found on any card Aug–Dec: Dominion, Columbia Gas (on WF — 4 Columbia Gas account numbers, Joshua Davis), EarthLink, Minut (July only — below), Guesty, Airbnb host fees, Vrbo, Shreckhise (July only), Weaver Irrigation, Home Depot/Amazon shipped to Verona (Amex shows Amazon **refunds only**, -$2,063.34, no Amazon charges; Apple has none), Beatbot, pool supplies (Valley Pool & Spa only Mar/Apr).

### E2. Jan–Jul 2025 (personal / pre-placed-in-service)

| Date | Description (verbatim) | Amount | Card |
|---|---|---|---|
| 01/30/2025 | Agp Btpropane Pa | 1,460.89 | Amex |
| 04/05/2025 | Agp Btpropane Pa | 1,595.27 | Amex |
| 07/11/2025 | Agp Btpropane Pa | 740.25 | Amex |
| 03/29/2025 | Valley Pool & Spa | 93.42 | Amex |
| 04/05/2025 | Valley Pool & Spa | 11.84 | Amex |
| 05/22/2025 | Unique | 693.60 | Amex | (Apple 07/28 shows "UNIQUE VAC/REP OF SAND4950 SW 72ND AVE MIAMI 33126 FL USA (RETURN)" -235.00 — vacuum/robot repair vendor) |
| 06/30/2025 | Premier | 150.00 | Amex |
| 07/02/2025 | Minut | 560.00 | Amex | (= P&L Minut $560; charged pre-8/1) |
| 07/05/2025 | Augusta | 28.00 | Amex |
| 07/08/2025 | Jacob Thomas | 870.00 | Amex | individual payee, unknown purpose |
| 07/10/2025 | SHRECKHISE SHRUBBERY S610 WEYERS CAVE RD. WEYERS CAVE 24486 VA USA | 160.06 | Apple (Joshua) |
| 07/10/2025 | SHRECKHISE SHRUBBERY S610 WEYERS CAVE RD. WEYERS CAVE 24486 VA USA | 520.25 | Apple (Joshua) |
| 07/14/2025 | SQ *PREMIER CLEANING S312 W Water St gosq.com 22801 VA USA | 2,500.00 | Apple (Joshua) |
| 07/16/2025 | Premier | 2,038.00 | Amex |
| 07/25/2025 | SQ *PREMIER CLEANING S312 W Water St gosq.com 22801 VA USA | 600.00 | Apple (Joshua) |
| 07/29/2025 | Jacob Thomas | 500.00 | Amex |
| 07/15–07/16/2025 | FERGUSON ENT 2573 402 OTTERSON DR STE 100 CHICO 95928 CA USA | 1,224.07 / 183.70 / 90.57 | Apple (Joshua) | plumbing fixtures, property unknown (returns 07/26 -97.82, 08/15 -176.22, 09/06 -83.09) |
| 07/16/2025 | Ferguson | 241.41 | Amex |
| Jan–Jul groceries/household in Verona/Staunton (MARTINS 6426 Staunton, FOOD LION #0384 Verona, WALGREENS #17279 Verona, TARGET Waynesboro) | personal | — | Apple (Hillary) |

Jul "Premier" cleaning total (Apple $3,100 + Amex $2,038 + 06/30 $150) = $5,288 — pre-opening deep clean; whether capitalizable/start-up is a CPA call. Not in P&L.

## F. Charitable

| Date | Description (verbatim) | Amount | Card |
|---|---|---|---|
| 01/06, 01/13, 01/20, 01/27, 02/03, 02/10, 02/17, 02/24, 03/03, 03/10, 03/17, 03/24, 03/31, 04/07/2025 (14 weekly) | Crosslink Community Church | 25.55 each | Amex |
| | **Crosslink total** | **357.70** | |
| 01/01/2025 | Aplpay Npo Grace | 103.20 | Amex | "NPO" = nonprofit; Grace Christian School? — verify |
| 04/24/2025 | Christian | 37.00 | Amex | truncated; unidentified |
| 09/14/2025 | Aplpay A Turningpo | 100.00 | Amex | "A Turning Point" — possible charity; verify |

Goodwill, Pushpay, Kindful: **nothing** on any card. Crosslink giving stops after 04/07/2025 on this card.

## G. 14300 Woods Walk (Midlothian VA) renovation Sept–Dec

| Date | Description (verbatim) | Amount | Card | Note |
|---|---|---|---|---|
| 10/03/2025 | CARPET AMERICA 6259 MECHANICSVILLE TPKE MECHANICSVILL23111 VA USA | 4,410.08 | Apple (Joshua) | |
| 10/29/2025 | CARPET AMERICA 6259 MECHANICSVILLE TPKE MECHANICSVILL23111 VA USA | 4,410.08 | Apple (Joshua) | |
| 10/31/2025 | CARPET AMERICA 6259 MECHANICSVILLE TPKE MECHANICSVILL23111 VA USA | 521.03 | Apple (Joshua) | |
| 11/07/2025 | CARPET AMERICA 6259 MECHANICSVILLE TPKE MECHANICSVILL23111 VA USA (RETURN) | -521.03 | Apple (Joshua) | **refund of the 10/31 charge** |
| | **Carpet America net** | **8,820.16** | | P&L shows 9,341.19 |
| 11/11/2025 | Avail Services | 75.00 | Amex | listing service |
| 04/19/2025 | Zillow | 29.99 | Amex | listing / Rental Manager (could be Hardinberry rent collection) |
| 08/09/2025 | Zillow | 39.99 | Amex | same |
| 11/04/2025 | Aplpay Lowe Chesterfield | 54.95 | Amex | Lowe's Chesterfield = Midlothian area |
| 11/04/2025 | Lowe Chesterfield Va | -33.84 | Amex | refund |
| 09/18/2025 | Shades Light Midlothian | -150.52 | Amex | refund; the matching charge is "Shades" 08/23 $665.88 (Shades of Light, Midlothian — fixtures; property not provable) |
| 10/25/2025 | Lighting | 1,990.68 | Amex | vendor truncated, location unknown |
| 12/28/2025 | Lighting | 197.03 | Amex | same |
| 11/22/2025 | Lowe's | 2,625.51 | Amex | location not shown in export |
| Sep–Dec | Lowe's (unlocated) 09/26 208.02, 09/30 10.69, 10/04 144.26 (refunded 10/04 "Lowe Lexington Va" -144.26), 10/08 53.52, 10/11 12.68, 10/14 68.46, 10/16 80.75, 10/28 55.86, 10/30 56.12 | | Amex | |
| 09/18/2025 | Floor Store | 445.98 | Amex | possibly Dan's Floor Store (P&L names Dans Floor Store; WF 12/09 "Bill Pay Dans Floor Store on-Line" $5,317.98) |

Dan's Floor Store, Mega Painting, handyman: **not on cards** (WF: "Zelle to Mega Painting on 12/12 … Deck" $500.00; "Bill Pay Dans Floor Store" 12/09 $5,317.98; "Zelle to Adam on 10/16 … Trash" $250.00; "Zelle to Vlad 844 Handyman on 12/27 … Fans" $200.00).

Jacksonville-area materials (Floor & Decor Jacksonville, Tile Shop Jacksonville, Lee Cates Glass, Home Depot Jacksonville) are 844 Cypress Crossing — personal; listed in §J for completeness only.

## H. 148 Hardinberry (Oak Ridge TN)

**Nothing** identifiable to Oak Ridge / Roane County on Apple, Amex or Chase. Only candidates: the Steadily monthly stream (§D) and the two Zillow charges (§G) if Zillow Rental Manager is the Hardinberry rent-collection account.

## I. Vehicle interest / Chase accounts

### Chase …3009 — Fisker Finance auto loan (HILLARY D DAVIS, 2023 FISKER OCEAN, 3.99%)

| Post date | Transaction (verbatim) | Principal | Interest | Total |
|---|---|---|---|---|
| 01/21/25 | PAYMENT - THANK YOU (PRINCIPAL $767.95) (INTEREST$226.58) | 767.95 | 226.58 | 994.53 |
| 01/21/25 | PRINCIPAL REDUCTION | 5.00 | | 5.00 |
| 02/10/25 | PAYMENT - THANK YOU (PRINCIPAL $870.18) (INTEREST$124.35) | 870.18 | 124.35 | 994.53 |
| 03/11/25 | PAYMENT - THANK YOU (PRINCIPAL $816.99) (INTEREST$177.54) | 816.99 | 177.54 | 994.53 |
| 03/11/25 | PRINCIPAL REDUCTION | 100.00 | | 100.00 |
| **04/28/25** | **PRINCIPAL REDUCTION** | **46,348.27** | | 46,348.27 — principal fell from $55,087.38 (04/06) to $8,029.11 (05/06): the **buy-back / settlement credit** |
| 04/29/25 | PAYMENT - THANK YOU (PRINCIPAL $710.00) (INTEREST$290.00) | 710.00 | 290.00 | 1,000.00 |
| 05/28/25 | PAYMENT - THANK YOU (PRINCIPAL $974.54) (INTEREST$25.46) | 974.54 | 25.46 | 1,000.00 |
| 06/20/25 | PAYMENT - THANK YOU (PRINCIPAL $982.26) (INTEREST$17.74) | 982.26 | 17.74 | 1,000.00 |
| 07/25/25 | PAYMENT - THANK YOU (PRINCIPAL $971.30) (INTEREST$23.23) | 971.30 | 23.23 | 994.53 |
| 08/25/25 | PAYMENT - THANK YOU (PRINCIPAL $977.25) (INTEREST$17.28) | 977.25 | 17.28 | 994.53 |
| 09/25/25 | PAYMENT - THANK YOU (PRINCIPAL $980.55) (INTEREST$13.98) | 980.55 | 13.98 | 994.53 |
| 10/24/25 | PAYMENT - THANK YOU (PRINCIPAL $984.57) (INTEREST$9.96) | 984.57 | 9.96 | 994.53 |
| 11/25/25 | PAYMENT - THANK YOU (PRINCIPAL $986.98) (INTEREST$7.55) | 986.98 | 7.55 | 994.53 |
| **2025 interest shown on statements through 12/05/25** | | | **933.67** | |

- No "4/1 settlement" entry appears on any 3009 statement: the 04/04/25 statement's activity ends 03/11/25, and the 05/06/25 statement's activity begins with the 04/28/25 PRINCIPAL REDUCTION.
- No 12/11 payoff entry: the last 3009 statement in Downloads is dated 12/05/25 (principal $1,171.66, payment due 12/25/25). A January 2026 3009 statement would be needed to see the December interest and the payoff; it is not in Downloads (only 8048 has 2026 statements).
- Statement 01/06/25 reports "Interest Paid on this account during 2024 was $2,126.63" (for reference). No 2025 year-end interest figure is on file.
- Mailing address changed from Seattle (Jan–Apr statements) to 282 BALD ROCK RD (05/06/25 statement onward). Loan is in Hillary's name; personal auto interest is not deductible absent business use.

### Chase …8048 — **Rivian Financial Services auto LEASE** (JOSHUA C DAVIS, 2024 RIVIAN R1S, VIN 7PDSGABA0RN033038)

| Post date | Transaction (verbatim) | Amount |
|---|---|---|
| 01/21/25 | PAYMENT - BASE RENT 918.72 | 918.72 |
| 02/10/25 | PAYMENT - BASE RENT 918.72 | 918.72 |
| 03/11/25 | PAYMENT - BASE RENT 918.72 | 918.72 |
| 04/29/25 | PAYMENT - BASE RENT 1000.00 | 1,000.00 |
| 05/31/25 | PAYMENT - BASE RENT 1000.00 | 1,000.00 |
| 06/30/25 | PAYMENT - BASE RENT 1000.00 | 1,000.00 |
| 08/04/25 | ASSESSED LATE CHARGE | 25.00 |
| 08/05/25 | PAYMENT - BASE RENT 975.00; LATE CHARGE 25.00 | 1,000.00 |
| 09/03/25 | ASSESSED LATE CHARGE | 25.00 |
| 09/05/25 | PAYMENT - BASE RENT 1537.32; LATE CHARGE 25.00 | 1,562.32 |
| 10/31/25 | PAYMENT - BASE RENT 1000.00 | 1,000.00 |
| 12/04/25 | ASSESSED LATE CHARGE | 25.00 |
| 12/10/25 | PAYMENT - BASE RENT 990.08; TAX 9.92 | 1,000.00 |
| **2025 lease payments** | | **10,318.48** (incl. $50 late charges; $25 late charge assessed 12/04 still open) |

- It is a lease: **no interest is charged or reported**. Nothing deductible absent business-use substantiation (lease payments would be prorated by business use, not interest).
- Tax: 12/08/25 statement adds "Current Tax Due $59.72" with Message Center note "a recent tax rate change resulted in a change to your Total Payment Due"; 12/10 payment allocated $9.92 to TAX. Billing address changed to 844 CYPRESS CROSSING TRL, SAINT AUGUSTINE FL by the 12/08/25 statement (Verona address through 11/06/25) — consistent with FL sales tax on lease payments starting.

## J. Other potentially deductible personal items (2025)

### Medical / dental / vision (Amex unless noted; excludes supplements, Whoop, Oura, Medical Spa, Gundry)

| Provider (verbatim) | Dates | Total |
|---|---|---|
| Caduceus | 11/13 $590.99, 11/17 $559.55 | 1,150.54 |
| Pt Cora Pt (physical therapy, 20 charges) | 05/08 – 08/19 | 662.56 |
| Nilsen Eye Care | 01/31 $248.20 + $168.40, 02/26 $94.20, 05/09 $150.00 | 660.80 |
| Florida Dpc | 09/02 $77.33, 10/05 $80.00, 11/05 $80.00, 11/24 $180.00, 12/02 $81.07, 12/05 $80.00 | 578.40 |
| Vibrant / Vibrant America (lab) | 11/28 $270.00, 12/27 $270.00 | 540.00 |
| Aplpay Uva Hs (UVA Health) | 05/08 $50.00, 10/30 $312.00, 12/10 $156.00 | 518.00 |
| 1-800-Contacts | 03/03 $117.97, 05/07 $349.98, 06/04 -$10.00 | 457.95 |
| 1-800 CONTACTS, INC. 216 W DATA DRIVE 8002668228 84065 UT USA | 09/29 | 359.98 (Apple, Joshua) |
| Partnermd | 01/06 $208.33, 02/06 $208.33, 02/25 -$10.00 | 406.66 (+ Apple 02/25 "PARTNERMD VIRGINIA PC … (RETURN)" -15.00) |
| Phr St Augustineendo | 10/07 | 400.00 |
| Precision Imaging Centers | 09/03 | 375.00 |
| Clarity Vision | 06/28 | 300.00 |
| Lenscrafters | 11/05 | 263.94 |
| Zip Radiology Assis | 06/19, 07/03, 07/17, 07/31 $76.77 each; 09/10 -$75.27 | 231.81 |
| Elite Smiles (dental) | 10/09, 11/10, 12/09, 12/24 $25.75; 11/24 $103.00 | 206.00 |
| Healing Touch | 01/24 | 174.80 |
| Eye Center | 12/03 | 140.00 |
| Borland Groover | 09/19 $50.00, 10/07 $50.00 | 100.00 |
| 7th Letter Wellness | 11/07 $53.00, 11/24 $40.00 | 93.00 |
| Allergy Partners | 11/11 | 89.11 |
| Carenow | 03/02 | 60.00 |
| Urgent Care | 08/23 | 50.00 |
| Radiology | 06/06 | 40.00 |
| Labcorp Cash Vap | 10/14 | 23.91 |
| Vision | 03/03 | 20.00 |
| PB MY CHART 863 GLENROCK RD STE NORFOLK 23502-3701VA USA | 08/26 | 50.00 (Apple, Joshua) |
| SP ZIMA DENTAL US 1007 N Orange St WILMINGTON 19801 DE USA | 05/21 | 76.75 (Apple, Joshua) |
| **Identified provider total** | | **≈ 8,029** (Amex 7,542.48 + Apple 486.73) |
| Walgreens (34 charges) / CVS (8) — pharmacy vs. retail not determinable | 2025 | 780.93 / 127.76 |
| Zenotiusa Urban (Fishersville) — spa/salon software; likely cosmetic | 01/27 $1,010.00, 03/18 $86.00, 04/04 $676.00, 11/12 $153.00 + $68.00 | 1,993.00 (not medical unless substantiated) |
| VTG*Family Focus, Inc 31 UNION ST HENRICO 23294 VA USA | 03/21 | 187.75 (Apple, Madison) — possibly counseling; verify |

Medical only matters above 7.5% of AGI; listed so the CPA can decide.

### Education

| Item | Dates / amounts | Total | Note |
|---|---|---|---|
| Galen College Nur | 07/24 $200.00, 09/04 $507.00, 10/09 $504.00, 11/10 $504.00, 12/30 $504.00 | **2,219.00** | Galen College of Nursing — post-secondary tuition; **AOTC / Lifetime Learning candidate; request Form 1098-T**. Not in package. |
| Nursing | 04/25 $120.00, 06/03 $29.99 | 149.99 | related fees? |
| Sp Puregalen | 11/07 | 113.42 | unclear |
| Facts Tuition Fexxx | 01/27, 02/25, 03/25, 04/25, 05/27 $706.25 each + $20.83 fees each; 02/28 $40.00 + $1.18 | 3,676.58 | K-12 tuition (FACTS) — not federally deductible; stops after May 2025 |
| Wiley | 03/15 $65.89 + $2.29 | 68.18 | textbook? |
| Parchment (transcripts) | Feb/Jun, 7 charges | 52.03 | |

### Tax payments / prep / investment fees on cards
- Freetaxusa.com 04/22/2025 $14.99 (Amex) — tax prep fee, personal, not deductible.
- Roanoketax Rxxxxxx Va 11/11/2025 $10.68 (Amex) — Roanoke City (business).
- Rivian lease "TAX 9.92" 12/10/25 (Chase 8048).
- No IRS / VA / FL tax payments on cards (IRS & VA estimated payments are in WF).
- No investment / advisory fees on cards.

### 844 Cypress Crossing (personal residence) materials — basis file only, not deductible
Apple: FLOOR AND DECOR 196 Jacksonville 09/11 $2,546.94 (returns 09/12 -1,053.12, 10/27 -207.85, 12/08 -138.56); THE TILE SHOP Jacksonville 08/14 $30.41 (returned 08/20). Amex: Lee Cates Glass 11/07 $517.58, 11/25 $517.58, 12/08 $1,126.83, 12/29 $1,126.82 (= 3,288.81); Tile Shop 12/30 $352.64, Aplpay Tile Shop 12/31 $675.77 (refund -120.81); Floor & Decor 08/14 $203.98, 12/28 $222.25, 12/30 $60.19 (refunded); Aplpay Floor Dec 07/11 $311.45, 09/10 $231.07; Pottery Barn (13 charges 05/24–11/01) gross $3,910.58, refunds -263.80, net **3,646.78** — shipping address not shown on Amex; Comenity/Capital One card had **no** 2025 activity.

### Unidentified / unassigned (property unknown — caller may recognize)
- Apple FERGUSON ENT (online plumbing) net 2025 **$1,775.18** (Jul $1,498.34 less returns $357.13; Aug $221.65; Dec 12/04 $1,173.80 + $83.61 less 12/25 returns $306.33 + $538.76) + Amex "Ferguson" 07/16 $241.41.
- Amex "Lowe's" 11/22 $2,625.51; "Lighting" 10/25 $1,990.68 and 12/28 $197.03; "Shades" 08/23 $665.88; "Twin" 04/20 $1,262.54; "West End" 02/26 $3,050.00; "J Bing Associate" 02/27 $1,900.00; "Jacob Thomas" 07/08 $870.00 + 07/29 $500.00; "Xpress" 09/04 $162.06 + $158.36, 10/08 $750.00; "Woodland" 12/10 $729.95; "Summit" 6 charges $1,214.40; "Wells" 9 charges $1,104.00; "Function" 09/06 $399.00, 12/03 $58.00; "Cottage" 10/03 $218.00; "Mountain" 08/22 $375.00; "Cubesmart" storage $253/mo Jan–Aug, $298/mo Sep–Dec = $3,216.00; "Security" $167.02 + $45.94 monthly = $2,463.64 (two alarm accounts — likely Valley Pawn); "Aplpay Arlotechnologxxx Ca" 03/28 $134.23 + $89.48 (cameras); "Vivint" 04/08 $49.48; "Sunshine Sparks Elec" 04/09 $45.00.
- Apple "HIGH TECH DESIGN AND D1550 COMMERCE RD STAUNTON 24401 VA USA" 05/20 $250.00 (Hillary).

---

## Reconciliation against P&L lines

| P&L line | P&L amount | Found on cards / notes | Status |
|---|---|---|---|
| Propane - AmeriGas (Bald Rock) | 1,151.40 | Amex "Agp Btpropane Pa": 01/30 $1,460.89, 04/05 $1,595.27, 07/11 $740.25, **12/30 $193.58**. Only $193.58 falls in Aug–Dec. No combination of card charges equals $1,151.40. Full-year card total $3,989.99. | **Does not tie** — source of $1,151.40 must be AmeriGas bills paid elsewhere (or an allocation); card evidence supports only $193.58 post-8/1 (plus $740.25 on 07/11 if the delivery was for the rental season). |
| Grounds - Shreckhise Shrubbery | 680.31 | Apple 07/10 $160.06 + $520.25 = **680.31 ✓**. BUT WF card 5075 also shows Shreckhise 04/02 $237.98, 07/07 $721.31 and a **07/30 "Purchase Return" +$1,241.56** (return exceeds WF purchases by $282.27). Net Shreckhise across Apple+WF = $398.04. | Ties to Apple; **flag the WF $1,241.56 return** — if it refunded plants also bought on Apple, the deductible amount is lower. All charges are July (pre-8/1). |
| Noise/occupancy sensors - Minut | 560.00 | Amex 07/02/2025 "Minut" **560.00 ✓** (pre-8/1 purchase; likely equipment, not a subscription). | Ties |
| Insurance - Homesite Aug–Dec | 996.65 | **Not on Apple, Amex or Chase**; not in WF file. | Not found in any account swept |
| Property tax - Augusta County | 1,832.63 (5/12 of 4,398.32) | **Not on cards.** | Not found (DuPont?) |
| Insurance - Steadily 14300 | 1,051.00 | Not on cards as an annual charge. The only Steadily on cards is the $80.85/mo stream ($988.00 for 2025). | Not found as stated |
| Insurance - Steadily 148 | 907.15 | Amex monthly "Bt Steadily Ins" **$988.00** for 2025 (01/09 $98.80; 02–11 $80.85 ×10; 12/09 $80.70). If this stream is the Hardinberry policy, P&L is **short $80.85** (one month) vs. the card. | Ties approximately; $80.85 variance |
| HOA - Woodlake | 1,479.00 | Not on cards (DuPont ACH per P&L). | Not found |
| HOA - Southland | 2,796.00 | Not on cards (DuPont ACH per P&L). | Not found |
| Repairs - painting (Mega Painting) | 1,600.00 | Not on cards. WF shows only "Zelle to Mega Painting on 12/12 … Deck" **$500.00**. | **$1,100 unsupported** in accounts swept; also "Deck" memo — confirm it is Woods Walk |
| Carpet America | 9,341.19 | Apple 10/03 $4,410.08 + 10/29 $4,410.08 + 10/31 $521.03 = 9,341.19 — **but 11/07 "(RETURN)" -$521.03 refunds the 10/31 charge**. Net paid **8,820.16**. | **Overstated by $521.03** |
| (context) Flooring - Dans Floor Store + BillPay | 8,317.98 | WF 12/09 "Bill Pay Dans Floor Store on-Line" $5,317.98 (P&L attributes to DuPont). Amex "Floor Store" 09/18 $445.98 may be the same vendor. | Partial; note account attribution |
| (context) Cleaning - Lam's | 8,100.00 | WF Zelle to Lams Valley Maid and Paint Aug–Dec (not re-totaled here). | — |

## Deductible items FOUND but NOT in the package

| Item | Period | Amount | Card | Where it belongs |
|---|---|---|---|---|
| "Premier" cleaning (Premier Cleaning, Harrisonburg) — 7 charges | 08/04–11/12/2025 | **2,110.00** | Amex | Bald Rock cleaning (vendor identity probable, description truncated) |
| "Augusta" water/sewer | 08/05–12/08/2025 | **122.00** | Amex | Bald Rock utilities |
| Pre-opening cleaning "Premier"/"SQ *PREMIER CLEANING" | 06/30–07/25/2025 | 5,288.00 (Apple 3,100 + Amex 2,188) | Apple + Amex | Bald Rock — pre-8/1; CPA to decide (start-up / capitalize / personal) |
| Galen College Nur tuition | 07/24–12/30/2025 | **2,219.00** | Amex | Education credit (AOTC/LLC) — needs 1098-T and student identity |
| Crosslink Community Church | 01/06–04/07/2025 | **357.70** | Amex | Schedule A charitable |
| Possible charity: Aplpay Npo Grace 103.20; Aplpay A Turningpo 100.00; Christian 37.00 | 2025 | 240.20 | Amex | verify payee |
| Avail Services | 11/11/2025 | 75.00 | Amex | Woods Walk advertising |
| Zillow | 04/19 29.99, 08/09 39.99 | 69.98 | Amex | Rental listing/management fee (Woods Walk or Hardinberry) |
| Lowe's Chesterfield (net) | 11/04/2025 | 21.11 | Amex | Woods Walk materials (if confirmed) |
| Steadily variance | 2025 | 80.85 | Amex | 148 Hardinberry insurance (card shows $988.00 vs P&L $907.15) |
| Medical providers (identified) | 2025 | ≈ 8,029 | Amex + Apple | Schedule A medical, only if over 7.5% AGI floor |
| Fisker loan interest (Hillary) | 2025 | 933.67 (+ Dec not on file) | Chase 3009 | Not deductible unless business use |

Package reductions found: Carpet America **-521.03** (refund); Mega Painting support only $500 of $1,600 in WF.

## Still not found in any account swept (Apple, Amex 3001, Chase 3009/8048, Pottery Barn card, WF extract)

- FHCP premiums for Sep, Oct, Dec 2025 (only 08/06 $1,019.59 and 11/21 $2,027.57 on Amex).
- Anthem / HealthKeepers personal premium (WF has only the Full Circle Finance "Anthem Blue Individual" $500.16/mo).
- Homesite Aug–Dec $996.65; Travelers; Kin; GEICO.
- Augusta County property tax ($2,198.72 + $2,199.60); Chesterfield County $3,313.48; Roane County $855.64; St Johns County property tax.
- Woodlake $1,479; Southland $2,796 (DuPont 2291).
- Steadily 14300 annual $1,051 renewal.
- Mega Painting beyond the $500 WF Zelle; the $950 handyman trash-out (WF shows "Zelle to Adam … Trash" $250 and "Zelle to Vlad 844 Handyman … Fans" $200 only).
- Bald Rock Aug–Dec: Dominion, EarthLink, Guesty, Airbnb/Vrbo host fees, Weaver Irrigation, Beatbot, pool supplies, Amazon/Home Depot orders to Verona (Amazon appears on Amex only as refunds).
- Anything for 148 Hardinberry in Oak Ridge TN (no vendor, utility, or HVAC charge on any card).
- Goodwill, Pushpay, Kindful, Grace Christian School donations (only the 01/01 "Aplpay Npo Grace" $103.20 candidate).
- Fisker: the "4/1 settlement" and "12/11 payoff" entries — not on the 3009 statements in Downloads (only the 04/28/25 PRINCIPAL REDUCTION $46,348.27 appears; no Jan-2026 3009 statement on file).
- Pottery Barn card: no 2025 purchases at all, so no ship-to split is possible; the 2025 Pottery Barn spend ($3,646.78 net) is on Amex with no address data.
