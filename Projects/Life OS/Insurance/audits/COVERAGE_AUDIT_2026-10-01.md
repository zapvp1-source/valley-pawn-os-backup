# Quarterly Insurance Coverage Audit — 2026-10-01

**Task:** `insurance-coverage-audit` (quarterly, 1st of Jan/Apr/Jul/Oct) · **First run of this task.**
**Scope:** coverage versus reality across all three domains. Seven checks.
**Sources read this run:**
`Life OS/Insurance/INSURANCE_REGISTRY.json` (16 policy records, generated 2026-09-05, last regen 2026-09-30) ·
`Life OS/ENTITY_STRUCTURE.md` · `Valley Pawn OS/STORE_LEASES.md` ·
the five executed store leases in `Valley Pawn OS/Store Leases/` (read directly, not from the tracker) ·
`Bravo Data Extraction/output/2026-09-29_{CUL,HAR,LEX,ROA,WAY}_end-of-month.xlsx` ·
`Bravo Data Extraction/output/2026-09-27_{CUL,HAR,LEX,ROA,WAY}_aged-inventory-summary.csv` ·
Gusto MCP (roster, payrolls 2026-03-30 → 2026-09-28, per-employee earnings) ·
Gmail `jdavis@fcfpawn.com` (vehicle/registration/lienholder, `newer_than:120d`).

**No Bravo or Parallels session was opened.** Files only, per the task definition.
**Nothing was changed on any policy. No carrier or broker was contacted.**

Because this is the first audit file in this folder, there is no prior audit to diff against.
Findings below are marked **[NEW]** where the registry did not already carry them, and
**[KNOWN]** where they are already recorded as an open issue or an accepted decision.

---

## 1. Named insured vs ownership

Authority: `ENTITY_STRUCTURE.md` ("this file wins"). Full Circle Finance Inc owns zero real property.

| Property | Owner per ENTITY_STRUCTURE | Named insured on policy | Match? |
|---|---|---|---|
| 282 Bald Rock Rd, Verona VA | Farming Infinity Mountains LLC (Joshua sole member) | **Joshua Davis** individually (Homesite 39168908) | **NO** [KNOWN] |
| 817 Richmond Ave, Staunton VA | Farming Infinity, LLC (Joshua sole member) | **Full Circle Finance, Inc. DBA Valley Pawn** — Loc 5 on the pawn package; Farming Infinity LLC is only Additional Insured / Loss Payee on the building | **NO** [KNOWN] |
| 14300 Woods Walk Ln, Midlothian VA | Farming Infinity Virginia LLC (deed unconfirmed) | Joshua Davis individually (Steadily SP3-VA-33470384-00) | Matches *title as it actually stands*; will mismatch the moment the deed records [KNOWN] |
| 148 Hardinberry St, Oak Ridge TN | Joshua & Hillary jointly (TN LLC intended, deed not recorded) | Joshua Davis only; Hillary added as additional named insured on the 9/23/2026 revised quote, **not on the bound policy** | **PARTIAL — deed is joint, policy is one name** [NEW emphasis] |
| 844 Cypress Crossing Trl, St. Augustine FL | Joshua & Hillary jointly, personally | Joshua Davis; second named insured blank on the 2024-25 dec | **PARTIAL — Hillary is a joint owner and is not a named insured** [NEW emphasis] |
| 5 leased pawn stores | FCF Inc is tenant, owns nothing | Full Circle Finance, Inc. DBA Valley Pawn | OK |

**Exposure stated plainly.**

- **817 Richmond — $577,000 building, $45,000 business income.** The entity with the insurable
  interest in the building (Farming Infinity, LLC) is not the named insured. A total loss claim is
  paid to, and litigated by, FCF Inc — an entity that does not own the asset — with the real owner
  standing behind a loss-payee endorsement. Also a bookkeeping problem: FCF Inc pays $1,104/yr for
  a Domain 2 asset. **Two competing fixes are already in motion** and this is now a decision, not a
  discovery: Wexford/Christian Bandy quoted a standalone LRO in Farming Infinity LLC's own name at
  $3,309.16/yr on 9/23, and on 9/30 Wexford confirmed Special Cause of Loss is **not available** on
  this building because the updates date to 2007 — so the standalone trades $577K Special-form
  cover for Basic-form cover at 3× the Loc 5 premium. Ford Agency (Kyler Mahaney) is also quoting.
  **Nothing to bind until the form question is settled.**
- **Hardinberry and Cypress Crossing — one spouse named on a jointly owned house.** On a partial
  loss this is usually administrative; on a total loss or a liability claim it gives the carrier a
  coverage argument, and in Hardinberry's case Steadily has already produced corrected paper
  (9/23/2026 revised quote adds Hillary Holmes) that has not been bound because the premium
  decision is open. **Cheapest fix in the whole audit: a no-cost or near-no-cost named-insured
  endorsement on each. Worth doing independently of the limit decisions.**
- **Bald Rock named-insured mismatch is live but about to be resolved by replacement**, not by
  endorsement — the Homesite policy is being shopped out (§2). Whatever binds must be written in
  Farming Infinity Mountains LLC's name, or with Joshua **and** the LLC named. Flagging because
  three of the four live quotes (Proper, Steadily/Wexford, Obie/Evanston) were requested in
  Joshua's personal name.

---

## 2. Occupancy vs form

| Property | Actual use | Policy form | Verdict |
|---|---|---|---|
| 282 Bald Rock | Short-term rental (Airbnb + VRBO) with owner use | Homesite **HA 00 03 07 23 Homeowners 3 — Special Form**, dwelling described "PRIMARY RESIDENCE", occupancy type "Primary" | **WRONG FORM — claim-denial risk** [KNOWN] |
| 844 Cypress Crossing | Owner-occupied primary residence since ~8/1/2025 | Kin HO3 | Correct form. Registry still carries an open item to confirm occupancy reads Owner-occupied on the current term (2024 dec showed roof age 0 / "Times rented 0" from the rental era) |
| 14300 Woods Walk | Long-term rental, real tenants | Steadily landlord / dwelling | Correct |
| 148 Hardinberry | Long-term rental (was STR during the 2025-26 renovation) | Obsidian landlord via Steadily — **but rated as a CONDOMINIUM, walls-in** | Occupancy right, **structure classification wrong** [KNOWN] |
| 817 Richmond | Commercial, leased to FirstCash | Lessor's risk on the pawn package | Correct form, wrong named insured (§1) |
| 5 pawn stores | Retail pawn + FFL | Commercial package, pawnshop class 18437 | Correct |

**Exposure stated plainly.**

- **Bald Rock: a paying-guest loss on a policy that says "primary residence" is the single most
  likely claim denial in the portfolio.** Dwelling $897,000, liability only $300,000, and the
  occupancy representation on the dec is false on its face. Annual premium $2,356.
  **Status: four quotes in hand** — Steadily/Wexford DP-0003 $4,073.65 (occupancy listed
  "Seasonal", STR adequacy **unconfirmed in writing**), Proper $6,476.52 (purpose-built STR, but
  building limit only $800K and contents $100K as quoted), Obie/Evanston (Joshua pressed for the
  forms schedule 9/30 and received it; he called Obie "my front runner" on 9/30), Ford
  Agency/NBIC DP-3 (Joshua read the forms 9/30 and found **no STR or home-sharing endorsement
  anywhere on the 29-form schedule**; Kyler replied 10/1 that NBIC classifies STR as occupancy
  "tenant" / usage "seasonal"). **[NEW]** On 9/29 Joshua put the right question to all of them in
  writing — pool, hot tub, paying guests, and whether assault/abuse is excluded (he identified
  DL 24 01 exclusion E.7 on the NBIC form himself). **The audit's position: do not bind anything
  whose occupancy field reads "Seasonal" or "Tenant" without the carrier confirming in writing
  that a paying-guest loss is covered — that is the exact defect the current Homesite policy has,
  and "seasonal" is not the same word as "short-term rental."**
- **Hardinberry: dwelling insured at $105,000 walls-in on a fee-simple attached townhome whose
  county reappraisal is $248,300 and whose full-structure replacement cost Steadily now puts at
  $260,000–$270,000.** That is roughly a **$155,000–$165,000 shortfall** on a total loss, caused
  by a 360Value run that excluded roof, foundation, exterior walls, rough mechanicals and HVAC.
  Steadily has the corrected quote out; the premium "will more than double" (John Jungen, 9/25).
  Joshua's decision, unmade.

---

## 3. Pawn limits vs Bravo

Loan principal and inventory at cost from `*_end-of-month.xlsx` (reporting window 10/1/2025 –
9/29/2026; figures are the **Ending Loan Base** and **Ending Inventory Base** as of 9/29/2026).
Inventory at retail split jewelry vs merchandise from `*_aged-inventory-summary.csv` dated
9/27/2026.

**Two stated assumptions, both carried forward from `insurance-context` §4:**
1. Bravo exports no collateral value for pledged goods, so **pledged exposure is estimated at
   1.5 × loan principal outstanding.** That is a convention, not a measurement.
2. Both pledged and unpledged inventory are scheduled on a **Market Value** election, so
   unpledged exposure is measured at **tag price (retail)**, not cost.
3. Bravo's aged-inventory report splits **Jewelry** vs **Mfg. Goods** and does not break firearms
   out separately. Firearms therefore sit inside the Mfg. Goods line. The jewelry retail figures
   below are a **floor** on Firearms-&-Jewelry exposure, not the whole of it.

| Store | Loc | Loan principal 9/29 | Pledged est. (1.5×) | Pledged limit | **Pledged shortfall** | Jewelry @ retail | Unpledged F&J limit | **Unpledged F&J shortfall** | Mfg. goods @ retail | Other-Than-F&J limit |
|---|---|---|---|---|---|---|---|---|---|---|
| Waynesboro | 1 | $110,054.73 | $165,082 | $100,000 | **($65,082)** | $254,489.17 | $60,000 | **($194,489)** | $170,955.66 | **Not Covered** |
| Lexington | 2 | $87,995.60 | $131,993 | $100,000 | **($31,993)** | $229,526.05 | $60,000 | **($169,526)** | $88,669.54 | **Not Covered** |
| Culpeper | 3 | $212,288.63 | $318,433 | $150,000 | **($168,433)** | $594,401.41 | $150,000 | **($444,401)** | $163,811.88 | **Not Covered** |
| Harrisonburg | 4 | $183,147.00 | $274,721 | $150,000 | **($124,721)** | $402,759.88 | $100,000 | **($302,760)** | $149,866.44 | **Not Covered** |
| Roanoke | 6 | $154,085.47 | $231,128 | $120,000 (60 F&J + 60 OTF&J) | **($111,128)** | $435,170.09 | $50,000 | **($385,170)** | $76,081.69 | $25,000 unpledged → **($51,082)** |
| **Total** | | **$747,571.43** | **$1,121,357** | **$620,000** | **($501,357)** | **$1,916,346.60** | **$420,000** | **($1,496,347)** | **$649,385.21** | **$573,304 uncovered at 4 stores** |

**Exposure stated plainly.**

- **Every store is under-limit on pledged collateral.** Combined scheduled pledged limits of
  **$620,000** sit against an estimated **$1,121,357** of pledged exposure — a **$501,357** gap.
  Culpeper is the worst in dollars ($168,433 short); Waynesboro and Roanoke are the worst as a
  ratio (limit covers about 60% and 52% of estimated exposure).
- **Unpledged firearms-and-jewelry is the largest single number in this audit.** $420,000 of
  limit against **$1,916,347 of jewelry alone at tag price** — a **$1,496,347** gap before a
  single firearm is counted. Under a Market Value election the insurer owes tag price, so retail
  is the correct measure, and Culpeper alone is $444,401 short.
- **The entire "Other Than Firearms & Jewelry" category is uncovered at four of five stores.**
  **$573,304 of merchandise at retail** ($163,812 Culpeper, $149,866 Harrisonburg, $170,956
  Waynesboro, $88,670 Lexington) has no inventory limit at all. Roanoke is the only store that
  carries the category, and it is short $51,082 on the unpledged side. This is the one category
  where the answer is not "raise a limit" but "the coverage does not exist."
- **ULC has been waiting on Joshua since August for the market-value limits to quote all of
  this.** [KNOWN] The registry records the request; the figures in this table are what it needs.
  The practical blocker is not the carrier — it is that nobody has picked the numbers.
- Also still open and relevant to this check: a **$10,000 per-occurrence deductible** applies to
  every inventory line, coinsurance is waived only **per the 8/17/2026 proposal conditions**, and
  the theft-protection warranty requires **95% of jewelry and firearms in the safe at close of
  business** — a warranty breach voids the recovery regardless of limit.

---

## 4. Workers comp vs payroll

| | Figure | Source |
|---|---|---|
| Active employees in Gusto | **18** (non-terminated roster) | Gusto `list_employees`, 2026-10-01 |
| Gross pay, 25 weekly pay periods 3/30/2026 → 9/20/2026 (incl. 2 off-cycle corrections) | **$339,933.68** | Gusto `list_payrolls`, processed, totals |
| Annualized (×52/25) | **≈ $707,062** | computed |
| Class 8017 payroll basis on the **prior** term (-02, after endorsement) | $501,849 | registry |
| Class 8017 payroll basis on the **current** term (-03, Endorsement #1, eff. 6/13/2026) | **$555,697** | registry |
| **Apparent gap** | **≈ $151,365 over the endorsed basis (≈ 27%)** | computed |

**Caveats that make the gap a range, not a number.** Joshua and Hillary are **excluded officers**
on the workers comp policy (confirmed by Edna Villarino 6/10/2026), so their W-2 wages are inside
the $339,933.68 Gusto figure but outside the class 8017 basis. The per-employee earnings pull for
the same window returned **bonus and correction lines only for 11 employees — no officer earnings
appeared**, which is consistent with officers taking no wages through this payroll but does not
prove it, because that report does not return regular wages. **The gap is therefore at most
≈$151,365 and could be materially smaller.** It is not zero: the trailing-25-week run rate alone
annualizes above the endorsed basis.

**Exposure stated plainly.** An audit bill is coming on the -03 term, and a second one is already
open on the -02 term (Legacy National Audit; payroll and 941s were sent 8/4–8/6/2026, outcome not
received). At the -02 term's estimated premium of **$5,750 on a $501,849 basis — a rate of roughly
$1.15 per $100 of payroll** — a $151,365 overage prices out near **$1,700 of additional premium**,
and less if officer wages absorb part of it. **That is a cash-flow surprise, not a coverage gap**,
and it is the kind that lands as a single demand with no warning. [NEW] — the registry records the
endorsement and the open audit, but nobody had compared the endorsed basis to what payroll is
actually running.

Two administrative items on this policy remain unresolved and both are already in the registry
[KNOWN]: the named insured still reads **"Full Circle Finance, LLC"** when the entity is an **Inc**
(ACORD change request + ERM-14 asked for 9/29, not yet issued), and **Glencar has never produced a
statement of account** — the 9/29 request to `ar@glencarum.com` bounced with a delivery delay on
9/30 and Edna is still chasing the right AR contact. Coverage itself is confirmed in force by
binder and the policy document plus Endorsement #1 arrived 9/29/2026.

---

## 5. Vehicles

Policy of record: Progressive Select 998062549, named insured **Hillary D Davis**, Joshua listed
driver, term 5/28/2026 – **11/28/2026**, all four vehicles garaged 32095.

| Vehicle | VIN | Additional interest on policy | On policy? |
|---|---|---|---|
| 2024 Rivian R1S | 7PDSGABA0RN033038 | Chase Auto Finance | Yes |
| 2025 Tesla Model 3 | 5YJ3E1EA8SF981978 | Santander Consumer USA | Yes |
| 2026 Tesla Model Y | 7SAYGDEEXTA402172 | Chase Auto Finance | Yes |
| 2026 Tesla Cybertruck | 7G2CEHED0TA101127 | none (no lien) | Yes, added 8/22/2026 |

**A 120-day sweep of Gmail for registrations, titles, lienholder notices, bills of sale, dealer
paperwork and auto-loan originations found no fifth vehicle and no vehicle disposed of.** Tesla and
Rivian traffic in the window is all subscriptions, shop orders and marketing. The schedule of four
matches reality as far as any source available to this run shows.

**Three real findings, none of them about a missing vehicle.**

1. **[NEW] The Model 3 is a lease, not a loan.** Augusta County's Commissioner of the Revenue
   wrote on 9/21/2026, closing Joshua's request to remove the car from the Virginia personal
   property tax roll: *"We will remove the Tesla for 2026. All bills are sent to the leasing
   company."* Lessee account 244876. The registry carries Santander as a "Lienholder/Additional
   interest," which is the right endorsement either way — but **lease agreements almost always
   impose minimum liability limits well above 50/100/25 and require the lessor to be named as an
   additional insured, not merely as a loss payee.** At 50/100/25 the policy is very likely out of
   compliance with its own lease contract. Worth pulling the lease's insurance clause.
2. **[KNOWN] Limits are far below net worth.** BI **50/100**, PD **$25,000**, UM 50/100
   **nonstacked**, **no MedPay**, $2,000 comp/collision deductibles — against four vehicles
   including a Cybertruck, two drivers, and four residential properties. These limits were held
   down deliberately on 8/22/2026 to take Cybertruck delivery; that was a timing decision, not a
   permanent one. They also **block the RLI personal umbrella**, which requires $500K CSL
   underlying (§7).
3. **[KNOWN, unresolved] Household driver.** State Farm and Travelers prefills both surfaced a
   **"Madison Davis"** at 844 Cypress Crossing. If she is a licensed resident of the household she
   must be listed or excluded **in writing** on 998062549. An unlisted resident driver is a
   rescission argument, and it costs nothing to close. Only Joshua can state the fact.

**Business use.** All four vehicles are rated **Commute**. No vehicle is rated business use, and
the pawn package carries **Hired & Non-Owned Auto at the five retail locations** (~$125/location) —
which covers the company for employee-owned vehicles on company errands but does **not** cover a
personally owned vehicle being used for store runs under a personal policy rated for commuting.
If any of these four is used for inter-store runs, cash movement or bank deposits, the use class is
wrong. [KNOWN as an open issue; still unanswered.]

**Renewal is 11/28/2026 — 58 days out.** [NEW and time-critical] As of this run the upgrade
decision is live, not theoretical: Joshua emailed Thompson Baker 9/29 for 250/500 and 500 CSL side
by side, and on **9/30 20:56 he told JM Partners (Patsy Pernia, cc Howard Baker) "I'm binding
tomorrow at noon with another group."** Patsy replied **today, 10/1 14:31**, with options and a
request for a phone call. **That call is the gating event for the auto limits, the four property
policies and the personal umbrella all at once.**

---

## 6. Lease insurance requirements vs endorsements in force

Read from the executed leases themselves this run, not from the tracker summary. The registry's
`mortgagee_or_AI` array for the pawn package lists exactly three entries: DCCU as Loc 5 mortgagee,
Farming Infinity LLC as Loc 5 AI/loss payee, and **IWC Properties as AI at Loc 3 with its address
"not yet provided to ULC."**

| Store | What the lease requires | What the registry shows | Gap |
|---|---|---|---|
| **Roanoke** (Roanoke Rental Homes LLC, agent for Centerfield Ventures LLC) · §2.8.2 | **$2,000,000 combined single limit per occurrence** for BI/death **and** property damage. Policies must **name the Landlord and the Tenant as the insured parties** (and any Mortgagee on request). 30 days' cancellation notice to Landlord. | GL is **$1,000,000 per occurrence** / $2,000,000 **aggregate**. No AI for Loc 6. Carrier no longer offers a $3M aggregate. | **HARD BREACH — limit.** $1M/occ does not satisfy "$2M CSL per occurrence"; an aggregate is not a per-occurrence limit. Landlord also not named. |
| **Waynesboro** (SRR Investments, LLC) · §31 | CGL **$1M/occ, $2M aggregate** covering Tenant, Landlord, **Landlord's agents** and **Landlord's mortgagee**; and a **Certificate of Insurance naming Landlord AND Landlord's Agent both as additional insureds and as certificate holders**, deposited with Landlord. | Limits ✓. **No AI of any kind at Loc 1.** No COI on record. | **BREACH — additional insured + certificate.** Landlord's Agent is **Henry Liscio Company, 12704 Crimson Ct Suite 101, Henrico VA 23233.** |
| **Harrisonburg** (BZA Spotswood, LLC) · §16(b) | Public liability $1M/$1M BI + **$250K PD**; **fire and extended coverage on Tenant's improvements, stock-in-trade, trade fixtures, furniture, furnishings, special equipment, floor and wall coverings and all other personal property at FULL REPLACEMENT COST**; **all policies name Landlord as additional insured**; COI deposited 15 days before each expiration; 30-day cancellation notice. | GL limits ✓. Loc 4: **BPP Not Covered, tenant improvements Not Covered, Other-Than-F&J inventory Not Covered**; F&J written at **Market Value**, not replacement cost. **No AI.** | **WORST LEASE GAP IN THE PORTFOLIO** — three separate breaches: no AI, no property coverage on stock/fixtures/improvements, and the one inventory line that does exist is on the wrong valuation basis. |
| **Lexington** (Andorra Properties, LLC) · §12 | CGL **$1M per person / $2M per occurrence** (more than one person) / **$1M property damage in or upon the Leased Premises**; **Lessor named as additional insured**; each policy must **require 30 days' prior written notice to Lessor** before lapse, nonpayment, nonrenewal or any change in terms; policy or COI on request. | GL $1M/$2M ✓; damage-to-premises-rented $250,000 (lease wants $1M PD in/upon the premises — arguably satisfied by the $1M/occ GL, not by the $250K DTPR sublimit). **No AI. No 30-day notice-to-Lessor endorsement.** | **BREACH — additional insured + notice endorsement.** Read the PD requirement with Howard; $250K DTPR is the sublimit most likely to be argued. |
| **Culpeper** (IWC Properties, LLC) · §12(b) | Occurrence-form CGL **$1,000,000 per occurrence** including contractual liability; **and all-risk property insurance including THEFT coverage, at replacement cost, on Tenant's fixtures, furnishings, equipment and personal property.** §12 contains **no** additional-insured requirement. | GL ✓. Loc 3: **BPP Not Covered, tenant improvements Not Covered.** AI for IWC Properties is on the schedule but **ULC still does not have the address**, so the endorsement is very likely not issued. | **BREACH — tenant property/theft coverage absent.** AI is not required by the lease but has been promised to ULC; finish it or drop it. |

**Exposure stated plainly.**

- **Roanoke is the only straight limit breach and the easiest one to be caught on.** A landlord
  requesting a certificate gets a document showing $1M per occurrence against a lease that says
  $2M CSL. **The fixed term also ends 10/31/2026 — 30 days out** — and Joshua was in talks with the
  landlord as of 9/18/2026. A lease negotiation is exactly when a landlord reads the insurance
  clause. Closing this before 10/31 costs a limit increase or a $2M excess layer; closing it after
  a landlord notices costs leverage in the negotiation.
- **Four of five landlords are not additional insureds on a policy whose leases require it.**
  Waynesboro, Harrisonburg and Lexington require it in terms; Roanoke requires the landlord be a
  named insured outright. Only Culpeper doesn't ask — and Culpeper is the one that's half-done.
  **Every one of these is an endorsement request to Howard Baker with no premium or nominal
  premium, and every one of them is a default notice waiting to be served.** Harrisonburg has
  issued a formal Notice of Default over paperwork once before (4/29/2022, non-reporting of gross
  sales, cured in 24 hours) and is **right now** demanding 19 months of missing gross-sales reports
  — that landlord reads the lease.
- **Harrisonburg and Culpeper both contractually require tenant property coverage that does not
  exist.** Culpeper's §12(b)(ii) names theft explicitly; Harrisonburg's §16(b)(iii) requires full
  replacement cost on stock-in-trade. The pawn package carries **BPP "Not Covered"** at both. This
  is the same hole as §3's uncovered merchandise, seen from the lease side — which means fixing §3
  fixes a lease breach at the same time, and is a second, independent reason to give ULC the
  limits it has been asking for.

**What was checked and found absent:** no certificate-of-insurance file, log, or tracker exists
anywhere under `Life OS/Insurance/` or `Valley Pawn OS/`. There is no record of a COI ever being
issued to any of the five landlords. The registry's `mortgagee_or_AI` array is the only AI record
and it has three entries. **It is possible certificates were issued historically and never filed;
this audit cannot prove a negative from a source that doesn't record it.** The right next step is
to ask Howard Baker for the certificate history on IK29P109337, not to assume none exist.

---

## 7. Umbrella

**Personal umbrella: NOT IN FORCE.** A bindable self-service quote is in hand from **RLI
Insurance Company**, ref **PUPSUB-0800183**, dated 2026-09-26 and emailed to zapvp1@me.com:

| Limit | Annual premium |
|---|---|
| $1,000,000 | **$597** |
| $2,000,000 | $1,075 |
| $3,000,000 | $1,432 |
| $5,000,000 | $1,881 |
| excess UM/UIM $1M add-on | +$551 |

It is **blocked on one thing**: RLI requires $500K BI per person/per occurrence + $50K PD, **or**
$500K CSL, on **all** household autos. Progressive is at 50/100/25. Progressive's own 8/22/2026
upgrade quote for $500K CSL + stacked UM + extended PIP + MedPay + loan payoff ×4 is **$4,413 per
6-month term** — and per the 9/22/2026 three-carrier market check that number **beats GEICO
($5,543), Travelers ($7,369) and State Farm ($7,402)** at the comparable tier. The second
condition, $300K+ homeowners liability, needs Kin's Cypress Crossing liability limit confirmed —
the registry records it as **$100,000**, which **does not meet the condition** and is the quieter
of the two blockers.

**Commercial umbrella: NOT IN FORCE.** Requested from Laura Sullins at JM Partners on 8/24/2026.
**No quote has been received in five weeks.** biBerk has a self-service commercial umbrella flow
but its appetite for a pawnshop with an FFL and this inventory profile is unconfirmed and was never
attempted.

**Exposure stated plainly — this remains the portfolio's largest single gap, and the audit's
position is that it is now also the cheapest to close.**

The exposed surface is: a pawn business with **five retail locations, firearms sales, 18 employees
and $1M/$2M of primary GL**; **four residential properties**; **four vehicles including two
high-value EVs**; **a short-term rental with a pool and a hot tub taking paying guests on a
$300,000 liability limit written on a homeowners form**; and **auto liability of $50,000 per
person**. A single guest injury at Bald Rock, or one at-fault accident with a passenger vehicle,
exhausts the underlying limit and reaches personal assets directly. **$597 buys the first
$1,000,000 of protection over all of it.** The constraint has never been price — it is the $4,413
auto upgrade that has to come first, and that upgrade is cheaper than any competitor's equivalent
tier.

**[NEW] This is no longer a stalled item.** Joshua has been running a full consolidation shop for
a week: he sent JM Partners (Patsy Pernia, cc Howard Baker) the complete schedule — **4 autos,
5 properties, umbrella** — on 9/23, answered their roof-year questions on 9/29 (**Bald Rock 2023,
Woods Walk 2009, 844 Cypress 2004 with a new roof coming this year**), restated the ask on 9/29 as
**auto at $500K CSL with matching stacked UM/UIM plus a personal umbrella**, and on **9/30 20:56
told them he was binding at noon on 10/1 with another group**. **Patsy replied at 14:31 today with
options and asked for a call.** Three of Joshua's own 9/29–9/30 emails show him interrogating the
STR occupancy question on exactly the right grounds. The umbrella, the auto limits, Bald Rock's
form and the four property named-insureds are converging into one decision this week.

---

## Registry corrections made this run

| Policy | Field | Was | Now |
|---|---|---|---|
| `VP-PKG` | `status` / `open_issues` | "**STILL NOT SIGNED OR PAID as of this run (9/23)**" — IPFS premium finance agreement unsigned, $3,757.13 down payment unconfirmed | **SIGNED AND ACCEPTED.** IPFS submission **36878509** recorded signatures 9/22/2026 14:43 ("Full Circle Finance, Inc. has selected to pay the Down Payment via ACH and has signed the Premium Finance Agreement"), and IPFS issued a **Notice of Acceptance 9/23/2026 02:23** referencing policy IK29P109337-05. The past-due $12,523.78 is financed, not outstanding. |
| `PERS-AUTO` | `property_details` / `open_issues` | 2025 Tesla Model 3 carried as financed, Santander "Lienholder/Additional interest" | **Model 3 is LEASED, not financed.** Augusta County Commissioner of the Revenue 9/21/2026: "All bills are sent to the leasing company"; lessee account 244876; vehicle removed from the VA personal property tax roll for 2026. New open issue added: pull the lease's insurance clause for minimum-limit and lessor-as-additional-insured requirements. |

Both corrections were written to `INSURANCE_REGISTRY.json` and `last_verified` advanced to
2026-10-01. `INSURANCE_PORTFOLIO.md` regenerated via `bin/regen_portfolio.py`.

---

## What this audit says to do next, in order

Everything below is either free, nearly free, or already quoted. None of it is a new idea — the
audit's contribution is the sequence and the dollar figures.

1. **Take Patsy Pernia's call today or tomorrow** (JM Partners, replied 10/1 14:31 with options).
   It is the single event that can settle auto limits, the personal umbrella, Bald Rock's form and
   three property named-insureds at once. Joshua's own 9/30 deadline has passed.
2. **Do not bind any Bald Rock replacement whose occupancy field reads "Seasonal" or "Tenant"
   without written carrier confirmation that a paying-guest loss is covered.** That is the defect
   the current policy has.
3. **Five endorsement requests to Howard Baker, one email, nominal or no premium:** name SRR
   Investments **and Henry Liscio Company** (Waynesboro), BZA Spotswood (Harrisonburg), Andorra
   Properties (Lexington) and Roanoke Rental Homes LLC / Centerfield Ventures LLC (Roanoke) as
   additional insureds; add the 30-day notice-to-Lessor endorsement for Lexington; finish IWC
   Properties at Culpeper by sending the address ULC has been waiting on. **Ask in the same email
   for the certificate history on IK29P109337** — this audit could not find evidence any COI was
   ever issued, but absence of a file is not absence of a certificate.
4. **Fix Roanoke's limit before 10/31/2026.** The lease demands $2M CSL per occurrence; the policy
   provides $1M. The fixed term expires in 30 days and a negotiation is open.
5. **Give ULC the market-value inventory limits it has been waiting on since August.** §3's table
   is the input. The same decision closes a **$1,496,347** unpledged F&J gap, a **$501,357**
   pledged gap, **$573,304** of entirely uncovered merchandise, and two lease breaches.
6. **Two no-cost named-insured endorsements:** add Hillary to Cypress Crossing; bind the Hardinberry
   revision that already adds her. Both houses are jointly owned and insured in one name.
7. **Expect a workers comp audit bill on the order of $1,700** on the -03 term, plus whatever the
   open -02 audit returns. Keep chasing the Glencar statement of account and the Inc-vs-LLC
   named-insured correction.
8. **Confirm or exclude Madison Davis in writing** on Progressive 998062549, and settle whether any
   of the four vehicles is used for store runs. Both are one-line answers only Joshua can give.
9. **$597 for the first $1M of personal umbrella**, the moment the auto upgrade binds. And chase
   Laura Sullins, or try biBerk, for the commercial leg that has gone five weeks without a quote.

---

*Audit run 2026-10-01 by `insurance-coverage-audit`. Nothing bound, nothing cancelled, no carrier
or broker contacted, no email sent. Next scheduled run 2027-01-01.*
