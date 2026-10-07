# Pass C — TY2025 Federal + Virginia Tax Estimate (Joshua & Hillary Davis, MFJ)

Prepared 2026-10-06. Read-only technical review from the stated fact pattern. All figures are estimates to the dollar from the facts supplied; nothing here was tied to source documents. Items marked **[ASSUMPTION]** change the result if wrong.

---

## 0. 2025 figures relied on (confirmed by search 10/6/2026)

| Item | 2025 value | Source |
|---|---|---|
| MFJ brackets | 10% to $23,850; 12% to $96,950; 22% to $206,700; 24% to $394,600; 32% to $501,050; 35% to $751,600; 37% above | [NerdWallet / IRS Rev. Proc. 2024-40](https://www.nerdwallet.com/article/taxes/tax-changes) |
| MFJ standard deduction (post-OBBBA) | $31,500 (OBBBA raised from the $30,000 in Rev. Proc. 2024-40) | [Kiplinger](https://www.kiplinger.com/taxes/the-new-standard-deduction-is-here), [Porte Brown](https://blog.portebrown.com/9-key-tax-law-changes-for-individuals-under-the-obbba) |
| SALT cap | $40,000; reduced by 30% of MAGI over $500,000, floor $10,000 (fully $10,000 at MAGI ≥ $600,000) | [Drake](https://blog.drakesoftware.com/taxing-subjects/state-and-local-tax-update), [Blue J](https://www.bluej.com/answer/what-is-the-salt-cap-for-married-filing-jointly-in-2025) |
| §199A threshold MFJ | $394,600; phase-in range $100,000 (fully limited at $494,600) | [TaxSlayer](https://support.taxslayer.com/hc/en-us/articles/4410847935501-Increased-Income-Thresholds-for-2025-Qualified-Business-Income-Deduction-QBID) |
| HSA family limit / catch-up | $8,550; $1,000 catch-up only if age 55+ (Rev. Proc. 2024-25). Joshua b. 1973 = 52, **no catch-up** | [Journal of Accountancy](https://www.journalofaccountancy.com/news/2024/may/hsa-inflation-adjusted-maximum-contribution-amounts-for-2025-announced.html) |
| Roth IRA MFJ phase-out | $236,000–$246,000 | [IRS](https://www.irs.gov/newsroom/401k-limit-increases-to-23500-for-2025-ira-limit-remains-7000) |
| Child tax credit | $2,200/child (OBBBA); phase-out $50 per $1,000 (or fraction) over $400,000 MFJ | [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2025/11/11/new-tax-law-gives-a-boost-to-the-child-tax-credit-obbba/168069/) |
| Bonus depreciation | 100% for property **acquired after 1/19/2025** and placed in service after that date; property acquired on/before 1/19/2025 and placed in service in 2025 stays at the old 40% phase-down; Notice 2026-11 interim guidance; one-time election to use 40% (60% LPPP) for first tax year ending after 1/19/2025 | [BPM on Notice 2026-11](https://www.bpm.com/insights/irs-notice-2026-11/), [Thomson Reuters](https://tax.thomsonreuters.com/news/irs-provides-guidance-on-post-obbb-bonus-depreciation/) |
| Form 8962 repayment | TY2025: no repayment limitation at household income ≥ 400% FPL (full repayment). Caps abolished entirely from TY2026 | [Current Federal Tax Developments on FS-2025-10](https://www.currentfederaltaxdevelopments.com/blog/2025/12/23/technical-analysis-of-irs-fact-sheet-2025-10-statutory-revisions-to-premium-tax-credit-reconciliation-and-eligibility), [healthinsurance.org](https://healthinsurance.org/faqs/under-what-circumstances-might-i-have-to-repay-my-aca-subsidy/) |
| IRS underpayment rate | 7% all 2025 quarters; 2026: Q1 7%, Q2 6%, Q3 7%, Q4 7% | [IRS quarterly rates](https://www.irs.gov/payments/quarterly-interest-rates), [IRS IR Q1-2026](https://www.irs.gov/node/152321) |
| Virginia conformity | HB 29 (Ch. 7, 2026 Acts) signed 2/20/2026 sets static conformity to IRC as of **12/31/2025**, so Virginia conforms to OBBBA for TY2025 (incl. $40,000 SALT cap on VA Sch. A) but **continues to deconform from bonus depreciation** (addback required). VA Tax Bulletin 26-1 | [Forvis Mazars](https://www.forvismazars.us/forsights/2026/03/virginia-updates-tax-law-in-response-to-one-big-beautiful-bill-act), [Drake VA conformity](https://kb.drakesoftware.com/kb/Drake-Tax/19002.htm), [TaxSlayer VA addback](https://support.taxslayer.com/hc/en-us/articles/360015713172-Enter-the-difference-in-special-depreciation-to-add-to-Virginia-taxable-income-due-to-Fixed-Date-Conformity) |
| Virginia standard deduction / exemption | $17,500 MFJ for 2025 (prorated on 760PY); personal exemption $930 each, prorated | [TaxSlayer VA 2025](https://support.taxslayer.com/hc/en-us/articles/360031308612-What-s-new-in-2025-for-Virginia), [Legal Clarity](https://legalclarity.org/virginia-standard-deduction-amounts-and-exemptions/) |
| Virginia 502PTET | Due 15th day of 4th month (4/15/2026 for CY2025); automatic 6-month extension to file (10/15/2026) but tax must be paid by 4/15; election is made by filing 502PTET and is binding once filed; e-file only; owners cannot claim the credit until 502PTET is filed | [Legal Clarity VA PTET](https://legalclarity.org/virginia-ptet-election-who-qualifies-rates-and-credits/), [VA TB 23-8](https://TAX.VIRGINIA.GOV/sites/default/files/inline-files/tb-23-8-ptet-late-filing-penalty-waiver.pdf) |
| Virginia 760PY | Part-year resident taxed on all income during residency plus VA-source income during nonresidency; pass-through income is first apportioned to the residency period, then VA-source share for the nonresident period | [VA P.D. 06-4](https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/06-4), [VA 760PY Schedule of Income](https://www.tax.virginia.gov/forms/search?page=4) |
| §199A rental safe harbor | Rev. Proc. 2019-38: 250 hours; safe harbor is not exclusive. STR with average stay ≤ 7 days is not a "rental activity" under Reg. 1.469-1T(e)(3)(ii)(A) | [IRS](https://www.irs.gov/node/71431), [Tax Adviser](https://www.thetaxadviser.com/issues/2019/apr/sec-199a-rental-real-estate-activity-safe-harbor-proposed/) |
| Bonus on converted/used property | Reg. 1.168(k)-2(b)(3)(iii): "no prior depreciable interest" test; property converted from personal use is depreciated from conversion date on lesser of FMV or adjusted basis (Reg. 1.168(i)-4(b)) | [Cornell 1.168(k)-2](https://www.law.cornell.edu/cfr/text/26/1.168(k)-2), [Cornell 1.168(i)-4](https://www.law.cornell.edu/cfr/text/26/1.168(i)-4), [Tax Adviser](https://www.thetaxadviser.com/issues/2020/apr/bonus-depreciation-proposed-regs/) |

AMT exemption used: $137,000 MFJ (OBBBA made permanent; not re-searched, immaterial here).

---

## 1. Federal computation — three scenarios

Common inputs (all scenarios):

- Wages: $2,613.18 + $2,049.17 + W-2c health add $20,092.06 = **$24,754.41** **[ASSUMPTION A1: FCF actually paid/reimbursed the $20,092.06 of premiums during 2025 and had already deducted them on the 1120-S (e.g., as insurance expense), so the W-2c merely reclassifies; K-1 Box 1 stays $419,523. If the premiums were NOT previously deducted on the 1120-S, an amended 1120-S lowers Box 1 by $20,092 and AGI drops by the same — see §4 item 2.]**
- Interest $274.34; ordinary dividends $31.66; net ST capital loss ($133.32).
- Passive rentals (817, 14300, 148): current net +$6,138.22 (= 9,428.49 − 11,203.48 + 7,913.21); fully absorbed by suspended PALs (817 $26,391; 148 $6,600) → **net $0 to AGI**; remaining suspended carryover ≈ $26,853 (allocated between 817/148/14300 per Form 8582 Part VII) plus 844's $24,681 stays frozen.
- HSA: eligible months Jan–Aug (HDHP) → $8,550 × 8/12 = **$5,700** deductible; **excess $2,750** (6% excise $165/yr via Form 5329 unless withdrawn with earnings by 10/15/2026).
- Roth $8,000: no deduction; excess in every scenario (MAGI > $246,000); 6% excise $480 unless removed/recharacterized by 10/15/2026.
- SEHI deduction **$20,092.06** (Sch. 1 line 17) — limited to Joshua's FCF Medicare wages (≈$53k incl. 401(k) deferral and health add) → not binding. With full APTC repayment, SEHI equals total premiums (Rev. Proc. 2014-41 iteration collapses when final PTC = 0).
- Schedule A (all scenarios itemize; standard $31,500 loses): mortgage interest $42,730.72 (loan $667k < $750k; second home Jan–Jul, main home Aug–Dec — fully qualified residence interest); SALT paid $44,016.89 (property $14,759.43 + VA income tax $29,257.46) capped at **$40,000** (MAGI < $500k in every scenario); charitable $435.35 cash + $358 K-1 12A + $3,276 Goodwill noncash (Form 8283 Sec. A required) = $4,069.35. **Itemized total $86,800.07.** (OBBBA's 0.5%-of-AGI charitable floor starts 2026, not 2025.)
- Excess APTC repayment: $11,029.72 — household income ≈ 960%+ of FPL in every scenario → full repayment, no cap (TY2025 rule confirmed above).
- Form 3800: current-year 8881 credits $12,469 (13AE $11,969 + 13AF $500). **2024 carryforward assumed $0 [ASSUMPTION A2 — confirm 2024 Form 3800 Part III/§38 carryover; any carryforward is usable here, limit shown below].** §38(c)(1) limit = net income tax − greater of (TMT, 25% × (net regular tax − $25,000)). Form 3800 Part II line 1 uses Form 1040 line 16 **plus Schedule 2 line 2** (excess APTC), so the repayment is inside the base.
- NIIT (Form 8960): FCF and Bald Rock are nonpassive (base) and the passive rentals net to zero after PALs, so NII ≈ $173 (interest + dividends − cap loss). Immaterial.

### Table

| Line | (a) Base: Bald Rock non-passive + SEHI/W-2c | (b) Bald Rock passive | (c) Base + JDG K-1 $19,713 |
|---|---:|---:|---:|
| Wages | 24,754 | 24,754 | 24,754 |
| Interest / dividends / cap loss | 274 / 32 / (133) | same | same |
| Sch. E: FCF K-1 Box 1 | 419,523 | 419,523 | 419,523 |
| Sch. E: Bald Rock STR | (169,828) | 0 (suspended) | (169,828) |
| Sch. E: passive rentals net (after PAL) | 0 | 0 | 0 |
| Sch. E: JDG K-1 | 0 | 0 | 19,713 |
| **Total income** | **274,622** | **444,450** | **294,335** |
| HSA deduction | (5,700) | (5,700) | (5,700) |
| SEHI deduction | (20,092) | (20,092) | (20,092) |
| **AGI** | **248,830** | **418,658** | **268,543** |
| Itemized (vs std $31,500) | 86,800 | 86,800 | 86,800 |
| TI before QBID | 162,029 | 331,858 | 181,742 |
| QBI (FCF 419,523 − SEHI 20,092 ± BR/JDG) | 229,602 | 399,431 | 249,315 |
| 20% × QBI | 45,920 | 79,886 | 49,863 |
| 20% × (TI − net cap gain) limit | **32,406** | **66,372** | **36,348** |
| **QBI deduction (8995, below threshold)** | **32,406** | **66,372** | **36,348** |
| **Taxable income** | **129,624** | **265,486** | **145,394** |
| Regular tax (2025 MFJ) | 18,345 | 49,411 | 21,815 |
| NIIT (8960) | 0 | 7 | 7 |
| Excess APTC repayment (8962) | 11,030 | 11,030 | 11,030 |
| HSA excess 6% (5329) — if not withdrawn | (165) | (165) | (165) |
| Roth excess 6% (5329) — if not removed | (480) | (480) | (480) |
| CTC (Audrey) | (2,200) | (1,250) | (2,200) |
| GBC limit (§38(c)) / credit used | 18,693 / (12,469) | 15,391 / (12,469) | 18,069 / (12,469) |
| **Total tax (excl. 5329 excise)** | **14,706** | **46,728** | **18,182** |
| Withholding | (159) | (159) | (159) |
| **Balance due (before penalties)** | **14,547** | **46,569** | **18,023** |
| 2210 required annual payment (lesser of 90% / 110% × 57,780 = 63,558) | 13,235 | 42,055 | 16,364 |
| Est. 2210 penalty (7%/6%, regular method) | ≈ 603 | ≈ 1,931 | ≈ 747 |
| Failure-to-pay 4/15 → 10/15/2026 (0.5% × 6 mo) | ≈ 436 | ≈ 1,397 | ≈ 541 |
| Interest 4/15 → 10/15/2026 (6% Q2, 7% Q3/Q4) | ≈ 480 | ≈ 1,537 | ≈ 595 |
| **All-in at 10/15/2026** | **≈ 16,066** | **≈ 51,435** | **≈ 19,906** |

Notes on the table:

1. **QBI threshold.** In all three scenarios taxable income is below $394,600, so Form 8995 (not 8995-A) applies: no W-2 wage/UBIA limit, no SSTB test. The 20%-of-taxable-income cap is what binds. Consequence: **whether Bald Rock is a §199A trade or business is moot in (a) and (c)** — with or without netting the ($169,828) against FCF's QBI the deduction is capped at 20% of TI. (If Bald Rock is treated as a §162 business, Reg. 1.199A-1(d)(2)(iii)(A) allocates the negative QBI against FCF's positive QBI; the W-2 wages/UBIA of the loss business are disregarded.) In (b) the loss is suspended under §469 and carries forward for §199A too (Reg. 1.199A-3(b)(1)(iv)), so it does not reduce QBI this year.
2. **CTC.** Full $2,200 in (a) and (c) (AGI < $400k). In (b) AGI $418,658 → 19 × $50 = $950 reduction → $1,250. Audrey must be under 17 at 12/31/2025 with an SSN issued before the due date.
3. **GBC.** Fully absorbed in every scenario because TMT is low and the APTC repayment is in the base. If a preparer excludes Schedule 2 line 2 from "net regular tax," the (a) limit falls to ≈ $7,663 and ≈ $4,800 of credit would carry forward instead — confirm the software follows the Form 3800 instructions.
4. **AMT.** TMT $8.5k / $43.8k / $12.6k vs regular tax — no AMT.
5. **Roth.** MAGI in (a) is $248,830 — only $2,830 above the $246,000 ceiling. If the 1120-S is amended to deduct the $20,092 premiums (Assumption A1 false), MAGI falls to ≈ $228,738 and the **entire $8,000 Roth contribution becomes allowable** — do not remove it until the FCF treatment is settled.
6. **NIIT** is nil because passive rental income is fully sheltered by PALs and FCF/Bald Rock are nonpassive. In (b) the suspended Bald Rock loss is also excluded from NII.
7. **Estimates.** Required annual payment is the lesser of 90% of 2025 tax and 110% of 2024 ($63,558) — because 2025 tax is small, 90% governs. 2210 penalty computed on four equal installments at 7% to 3/31/2026 and 6% to 4/15/2026. Failure-to-pay assumes a timely Form 4868 (otherwise add failure-to-file at 5%/month up to 25%). Interest ≈ 6.3% for the six months.

### Additional sensitivities (apply to base case (a))

| Change | Δ AGI | Δ federal tax (approx.) |
|---|---:|---:|
| 1120-S amended to remove Porsche (sold 6/2024) $16,982 and leased Rivian $17,626 depreciation → K-1 +$34,608 | +34,608 | **+6,098** (total tax 20,803; balance 20,645) |
| Bald Rock conversion components limited to **40% bonus** instead of 100% (house acquired before 1/20/2025) — assume ≈$193k of 5/15-yr components → depreciation falls ≈ $95–100k | ≈ +97,000 | ≈ **+19,000 to +22,000** |
| §280A(d)(4) 12-month rule fails → Bald Rock deductions limited to gross rents, loss disallowed | +169,828 | ≈ **+32,000** (≈ scenario (b) result) |
| 1120-S amended to deduct the $20,092 premiums (A1 false) | −20,092 | ≈ **−3,600** and Roth $8,000 becomes allowable |
| 2024 GBC carryforward exists | — | −$1 per $1 up to ≈ $6,200 of remaining §38(c) room |

---

## 2. Virginia 760PY estimate (base case (a))

Residency 1/1–7/31/2025 = 212 days; ratio 212/365 = 58.08%. Filing status 2 on 760PY.

| Line | Amount | Basis |
|---|---:|---|
| FCF K-1 Box 1 | 419,523 | 100% VA-apportioned; taxable as resident Jan–Jul and as VA-source nonresident Aug–Dec → full year |
| Bald Rock (VA property, nonpassive) | (169,828) | VA-source all year |
| Passive rentals 817 / 14300 (VA), 148 (TN) | 0 | Net $0 in FAGI after PAL; nothing to allocate |
| Wages (prorated 58.08%) | 14,378 | **[ASSUMPTION V1: post-move services performed in FL; if Joshua still worked in VA stores Aug–Dec those wages are VA-source]** |
| Interest/dividends/cap loss (prorated) | 100 | Intangibles follow residency |
| HSA deduction (prorated) | (3,311) | Conservative; contributions were likely all made while a resident — allocating 100% lowers VA tax ≈ $140 |
| SEHI deduction (prorated) | (11,670) | Conservative; argument exists to allocate 100% to the VA-source FCF income (saves ≈ $485) |
| **VA share of FAGI** | **249,192** | |
| **Addition: fixed-date-conformity bonus depreciation** | **≈ +161,600** | Rough: ≈$193k of cost-seg components taken at 100% federally vs. VA MACRS without bonus (≈ 75% 5-yr HY 20% + 25% 15-yr HY 5% ≈ $31.4k). **Replace with the actual cost-seg/4562 detail.** Creates a VA subtraction in later years |
| Subtraction: VA529 | (2,800) | Contributed while resident; under $4,000/account cap |
| **VA AGI** | **≈ 407,992** | |
| Itemized deductions (must itemize since federal itemizes): $86,800 − VA income tax $29,257 = $57,543 + property tax within $40k cap … = $61,559, prorated | (35,755) | 760PY ADJ; proration method per 760PY instructions |
| Exemptions 3 × $930 prorated | (1,620) | |
| **VA taxable income** | **≈ 370,654** | |
| **VA tax** (2%/3%/5%/5.75%) | **≈ 21,055** | |
| Credit: Form 502 nonresident withholding (VK-1) | (8,338) | or (19,892) if FCF remits the full-year amount |
| **Balance due to Virginia** | **≈ 12,717** | **≈ 1,163 if the $19,892 is paid** |
| Form 760C addition (underpayment), rough | ≈ 480 | Required 90% × 21,055 = 18,950 vs 8,338 withholding credited ratably; VA rate = federal + 2% |
| VA extension penalty / interest | 2%/month of unpaid if < 90% paid by 5/1/2026; interest federal + 2% | Due date 5/1/2026 |

Without the bonus-depreciation addback VA tax would be ≈ $11,761 — the addback is worth ≈ $9,300 of 2025 Virginia tax, recovered over the VA recovery periods via subtraction.

Other VA points: QBID and the federal SALT deduction do not enter the VA computation (VA starts from FAGI and strips state income tax from itemized deductions). No other-state credit (TN and FL have no income tax). The 2024 VA balance paid in 2025 is a 2025 federal Schedule A item only — not a VA payment credit. The nonresident withholding on Form 502 is a shareholder credit, not an entity deduction (contrast PTET, §4 item 1).

---

## 3. Position risks ranked by dollar exposure (federal unless noted)

| # | Position | Exposure | Authority | What makes it bulletproof |
|---|---|---:|---|---|
| 1 | **§280A personal-use conversion of Bald Rock.** Residence Jan–Jul (212 personal days) then STR from 8/1. Without the §280A(d)(4) "qualified rental period" exception, personal use > 14 days limits deductions to gross rental income and kills the whole ($169,828) loss. | ≈ $32k fed + ≈ $8k VA (loss) + loss of future allocation | §280A(c)(5), (d)(1), (d)(4); Reg. 1.280A-3 (proposed); §280A(e) | Property must be rented or held out for rent at fair rental for **12 consecutive months from 8/1/2025 (through 7/31/2026)** or sold; no owner personal nights after 8/1 beyond the 14-day/10% test; written 12-month statement already built — keep listing history, calendar exports, and a declaration that no personal use occurred; keep pre-8/1 expenses off Schedule E. |
| 2 | **Bonus depreciation rate / basis on converted components ($198,386 depreciation).** OBBBA 100% requires acquisition after 1/19/2025. If the house was bought earlier, converted components are "acquired" at the original purchase (binding-contract) date and get the **40%** 2025 phase-down, not 100%. Also basis at conversion = lesser of FMV or adjusted basis (Reg. 1.168(i)-4(b)); §179 is not available for property converted from personal use. | ≈ $19–22k fed; VA addback shrinks correspondingly | §168(k)(2)(E), (k)(6); OBBBA §70301; Notice 2026-11; Reg. 1.168(k)-2(b)(3)–(5), 1.168(i)-4(b); Pub. 946 (no §179 on converted property) | Pull the Bald Rock deed/contract date; have the cost-seg provider re-run at 40% if pre-1/20/2025; obtain a conversion-date appraisal supporting FMV ≥ basis for each component class; separately document post-8/1 purchases (furniture, appliances, linens) which do qualify for 100% bonus or the §1.263(a)-1(f) de minimis election. Consider Notice 2026-11's 40% election only if it simplifies (it does not help here). |
| 3 | **Material participation in Bald Rock (108 hrs vs cleaner 70–99).** Relying on Reg. 1.469-5T(a)(3) (>100 hrs and not less than any other individual). Also Reg. 1.469-1T(e)(3)(ii)(A) average stay 3.58 nights ≤ 7 days. Failure = scenario (b). | ≈ $32k fed + 2210 effects | §469(c)(1), (h); Reg. 1.469-5T(a)(3), (f)(4) (contemporaneous log); Reg. 1.469-1T(e)(3)(ii)(A); spouse hours count §469(h)(5) | Contemporaneous time log (already built) with dates/tasks; exclude investor-type hours (Reg. 1.469-5T(f)(2)(ii)(B)); cleaner invoices showing actual hours < 108; confirm no co-host/manager exceeded owner hours; Airbnb/VRBO stay-length report supporting 3.58-night average; consider test (a)(7) facts-and-circumstances as backup. |
| 4 | **W-2c / SEHI mechanics ($20,092).** Deduction requires FCF to have paid or reimbursed the premiums in 2025 and reported them in Box 1 (Notice 2008-1). A W-2c for wages not actually paid in 2025 is defective; a 2026 reimbursement is a 2026 item. Market-reform excise risk (§4980D, $100/day) for reimbursing individual-market premiums is suspended for 2% shareholders by Notice 2015-17 (still in force) but not for other employees. Also Assumption A1 (whether the 1120-S already deducted the premiums). | ≈ $3,600–$6,000 fed; Roth $8k allowance hinges on it | §162(l); Notice 2008-1; Notice 2015-17 Q&A; Rev. Proc. 2014-41 | Evidence of 2025 reimbursement (check/ACH dated 2025) or 2025 payroll run; W-2c and W-3c filed; Box 1 (not Box 3/5) only; FCF ledger shows the premiums once (either comp or insurance), then 1120-S amended if needed. |
| 5 | **Reasonable compensation (FCF).** Joshua's FCF Medicare wages ≈ $33k against $419,523 of pass-through; distributions $388,705. Classic recharacterization target. | Payroll tax ≈ 15.3% of any recharacterized amount (to SS wage base $176,100) + penalties; also raises QBI W-2 wages (irrelevant here) | §3121(d); Rev. Rul. 74-44; Watson v. US (8th Cir. 2012); Glass Blocks Unlimited | Document that Joshua also draws $50k W-2 from JDG, hours in FCF, comparable pawn-operator pay; move to a defensible salary in 2026. Entity-level issue, flagged here because it drives 1040 numbers. |
| 6 | **1120-S depreciation on Porsche (sold 6/2024) and leased Rivian** | ≈ $6,100 fed + ≈ $2,000 VA via K-1 | §167/168; §1001 on the 2024 disposition; leased vehicle not depreciable by lessee | Amend 2024/2025 1120-S; report 2024 vehicle disposition; the 1040 should be filed on the corrected K-1 or disclose the expected amendment. |
| 7 | **GBC base includes excess APTC** | ≈ $4,800 of credit timing | §38(c)(1); Form 3800 instr. Part II line 1 (1040 line 16 + Sch. 2 line 2) | Follow the form instructions; keep the 2024 Form 3800 for any carryforward (Assumption A2). |
| 8 | **Virginia bonus addback computation and part-year allocation** | VA ≈ $9,300 if the addback is omitted; allocation of SEHI/HSA/wages ± $600 | Va. Code §58.1-301(B); §58.1-322.02; 760PY instructions; VA P.D. 06-4 | Compute addback from the actual Form 4562 (asset by asset: federal bonus+MACRS vs VA MACRS-only); keep a VA depreciation schedule for the future subtraction. |
| 9 | **HSA eligibility by month** | $165/yr excise; small | §223(b)(2), (b)(8) (last-month rule not met) | Confirm the VA Marketplace plan was HDHP Jan–Aug; withdraw $2,750 excess + earnings by 10/15/2026. |
| 10 | **Form 8283 noncash $3,276 to Goodwill** | ≈ $720 fed | §170(f)(8), (f)(11); Reg. 1.170A-13 | Dated receipts, itemized list with FMV method; > $500 requires Form 8283 Section A. |
| 11 | **Passive loss carryforwards (844, 817, 148)** | Carryforward accuracy only | §469(b), (g); Form 8582 | Keep an activity-by-activity suspended-loss schedule; 844's $24,681 stays frozen until a fully taxable disposition. |
| 12 | **Estimated-tax penalty / late payment** | ≈ $1,500 (a) to $4,900 (b) | §6654, §6651(a)(2), §6601 | Pay the balance (or a good-faith amount) now rather than at 10/15; a 2210 annualized-income schedule will not help (Bald Rock loss falls in Q3–Q4). |

---

## 4. Deductions, credits and elections the facts suggest but nobody has claimed

1. **Virginia PTET election for FCF (Form 502PTET)** — still available for 2025 by filing on extension by 10/15/2026 (tax should have been paid 4/15; late-payment penalty/interest apply). At 5.75% on Joshua's ≈ $419k share ≈ $24k of entity-level tax deductible federally (Notice 2020-75 remains valid; OBBBA's final text did not restrict PTET deductions), with a refundable credit on 760PY in place of the nonresident withholding. Federal benefit for 2025 is modest because the $40,000 SALT cap is only $4k over; the deduction is taken in the year the S corp pays (2026 for a cash-basis entity). Strong 2026-forward planning item; decide before the 10/15/2026 extended deadline.
2. **Amend 1120-S for the health premiums if they were not deducted** (see Assumption A1) — $20,092 deduction, ≈ $3,600 federal, and it pulls MAGI under $236,000 so the **$8,000 Roth contribution becomes fully allowable** (saves the $480 excise and preserves the Roth year).
3. **Roth excess remedy** — instead of removing, **recharacterize** the $8,000 to a traditional IRA (nondeductible given 401(k) participation and MAGI) and convert (backdoor). Check the pro-rata rule for any pre-tax IRA balances. Deadline 10/15/2026.
4. **§25C Energy Efficient Home Improvement Credit on 844 Cypress (2025 is the last year — OBBBA ends §25C for property placed in service after 12/31/2025).** The impact-window/door/pool-renovation work at the FL house, if installed after it became the principal residence (8/1/2025) and the products carry Energy Star Most Efficient certification with a 2025 qualified manufacturer PIN: windows up to $600, exterior doors $250/$500, heat pump/water heater up to $2,000, home energy audit $150; $1,200 general cap. Impact windows often are not Most-Efficient-rated — check the NFRC labels before claiming.
5. **De minimis safe harbor election (Reg. 1.263(a)-1(f), $2,500/invoice)** on the Bald Rock STR and 148 Hardinberry for furnishings, appliances, electronics bought in 2025 — expensed outright, immune to the bonus-depreciation acquisition-date problem in risk #2. Requires an annual election statement attached to the 1040.
6. **Small-taxpayer building safe harbor (Reg. 1.263(a)-3(h))** for 148 Hardinberry's 2025 renovation spend: if the unadjusted basis ≤ $1M and total repairs/improvements ≤ lesser of $10,000 or 2% of basis, the whole amount is deductible; otherwise apply the routine-maintenance safe harbor and the betterment/restoration tests rather than capitalizing everything. Separately, TN occupancy-tax wind-down and any 2025 casualty/insurance items.
7. **Bald Rock §195 start-up costs** incurred before 8/1/2025 to ready the STR (listing photography, licenses, STR permit, initial supplies): up to $5,000 deductible in 2025 with the balance amortized over 180 months — only if treated as a §162 trade or business.
8. **Form 8582 suspended-loss sweep** — the $26,391 (817) and $6,600 (148) carryovers are what shelter 2025 passive income; confirm they are actually loaded in the software so the +$6,138 of net passive income does not land in AGI (it would cost ≈ $1,400 and trigger a little NIIT).
9. **2026 estimated-tax safe harbor** — because 2025 total tax is ≈ $14.7k (base), the 2026 required annual payment can be as low as 110% × 2025 tax ≈ **$16,200**, regardless of 2026 income. That is a large interest-free deferral until 4/15/2027; set 2026 estimates accordingly (or run $16.2k of withholding through FCF payroll in Q4 2026, which counts as paid ratably).
10. **401(k) catch-up for Joshua** — 2025 deferral $30,721.85 vs $23,500 + $7,500 catch-up = $31,000 limit: $278 of room left; fine. If Hillary is 50+, her $23,483.83 leaves $7,516 of unused catch-up for future years.
11. **Accountable-plan reimbursements and §280A(g) ("Augusta") rental of 844 to FCF** — 2026 planning only (no 2025 facts); flagged because the S-corp-owner structure makes both routine and currently unused.
12. **Work Opportunity Tax Credit (Form 5884) at Valley Pawn** — five stores with hourly hiring; needs Form 8850 within 28 days of hire, so prospective only, but it flows to Form 3800 next to the 8881 credits.

---

## 5. Open facts that move the number

- Bald Rock acquisition (contract) date and cost-segregation report detail (drives risks #2 and the VA addback).
- Whether FCF deducted the $20,092 premiums on the 2025 1120-S as filed, and the 2025 reimbursement date (Assumption A1; risk #4).
- 2024 Form 3800 carryforward (Assumption A2).
- Audrey's age/SSN; Hillary's age (catch-up); confirmation the VA Marketplace plan was HDHP Jan–Aug.
- JDG final K-1 (scenario (c) uses 2024's $19,713 nonpassive; if JDG is passive to Joshua, the income would instead free up passive losses and the result is similar).
- Whether any Bald Rock owner nights occurred after 8/1/2025 (risk #1).
