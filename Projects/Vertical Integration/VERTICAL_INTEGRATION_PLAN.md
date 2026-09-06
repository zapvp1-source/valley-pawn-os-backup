# Valley Pawn — Vertical Integration Plan (Ammunition Manufacturing + Adjacent Verticals)

**Owner:** Full Circle Finance Inc DBA Valley Pawn (Domain 1) · **Created:** 2026-09-05 · **Status:** v1 — plan approved for execution pending Joshua's 3 decisions (Section 9)
**Companion:** `STATUS.md` (running log) · `Compliance/FFL_REGISTRY.md` (current Type 02 licenses) · `Valley Pawn OS/BUSINESS_OS.md`

---

## 0. Executive recommendation (expert-review-board output)

Board convened: firearms-industry attorney, TTB excise-tax CPA, ammunition plant operations manager, pawn-industry CFO, insurance underwriter.

**Recommendation: do this in a new entity, on a new premises, under a Type 07 FFL + Class 2 SOT — not a Type 06 and not inside the pawn licenses.** Reasons, in priority order:

1. **Liability isolation.** Ammunition is a product-liability business. A squib, double charge, or case failure that injures a shooter becomes a lawsuit against the manufacturer. Keep it out of the entity that owns five stores, the loan book, and Bald Rock. Form **Valley Ammunition LLC** (or similar; brand decision in Section 9), 100% owned by Joshua or by FCF Inc — CPA to pick for the 1120S/K-1 picture — and let it sell to FCF Inc at arm's length.
2. **Type 07 costs $150 vs $30 and unlocks three verticals for one license:** ammunition manufacturing, firearm manufacturing/assembly (AR builds, refinishing pawn inventory into "factory-refurbished"), and — with the $500/yr reduced-rate Class 2 SOT — suppressors, whose $200 federal tax dropped to $0 on 2026-01-01 and whose demand is the fastest-growing category in the industry. A Type 06 permits ammunition only and cannot transfer a single firearm.
3. **Federal explosives license is NOT required.** Smokeless powder for small-arms ammunition and small-arms primers are exempt from ATF explosives licensing (27 CFR 555.141; 18 U.S.C. § 845). Storage is a fire-code question (Virginia SFPC Ch. 56 / NFPA 495: over 50 lb commercial smokeless powder → Type 4 magazine), not an ATF license question.
4. **ITAR/DDTC registration is NOT required for standard sporting ammunition.** Since the March 2020 export reform, non-linked, non-tracer ammunition for firearms ≤ .50 cal is EAR ECCN 0A505 — no State Department registration, no annual fee. Do not make tracer, linked, or armor-piercing product and this stays true.
5. **The 11% FAET is the real tax, and selling through your own stores triggers the constructive-sale-price rules.** TTB collects 11% of the manufacturer's sale price quarterly (TTB F 5300.26). When a manufacturer sells at retail or to an affiliated retailer, tax is computed on a constructive price (27 CFR 53.94–53.97), not the retail price — good news, but the affiliated-corporation rule means the Valley Ammunition → Valley Pawn transfer price must be documented as if to an unrelated wholesaler. This is the single biggest compliance trap and the reason the CPA is a Phase 1 hire.
6. **Market timing is favorable.** 2026 has a narrow shortage in 9mm / 5.56 / .22LR driven by government contracts, a smokeless-powder bottleneck, and 35% tariffs on imported brass and primers (Jan 2026). Wholesale is up 8–12% YoY; branded/house ammo carries 40–60% margin vs 20–30% on name brands. Primer supply is reported stable for small OEMs. That said, components are the constraint — lock supply before buying machines.

**Sequence:** entity + premises + license (Q4 2026) → components + one pistol-caliber line (Q1 2027) → in-store sell-through + FAET rhythm (Q2 2027) → second caliber + wholesale (H2 2027) → suppressors / firearm assembly on the same license (2028).

**What this is NOT:** it is not reloading in the back of a store. Every FFL is premises-specific; the pawn licenses are Type 02; the fire code will not allow production quantities of powder in a retail unit; and you do not want product liability under the pawn roof.

---

## 1. Why vertical integration fits this business

- Valley Pawn already holds five FFLs, runs monthly gun audits, NICS rankings, FFL transfer traffic, and sells firearms in every store. Ammunition is the consumable those customers buy every visit; today 100% of that margin goes to distributors.
- Five retail doors = guaranteed first-party sell-through for a new line. Most start-up ammo makers fail on distribution; this one starts with it.
- The team already runs weekly KPIs, aged-inventory, margin, and compliance cadences in Bravo/Slack. A manufacturing line plugs into the same reporting spine (Section 8).
- Hard constraint carried over from `valley-pawn-context`: **firearms/ammo cannot be marketed on Meta or Google.** Ammunition marketing runs on Brevo email, the website, in-store, GunBroker, AmmoSeek/ammo aggregators, and word of mouth. Plan for that from day one.

---

## 2. Vertical candidates — ranked

| # | Vertical | License needed | Start-up capital (est.) | Margin | Priority |
|---|---|---|---|---|---|
| 1 | **Ammunition manufacturing** (new + remanufactured pistol/rifle) | Type 07 (or 06) + FAET registration | $150k–$300k | 40–60% on house brand | **Phase 1** |
| 2 | **Suppressor sales / manufacturing** | Type 07 + Class 2 SOT (pawn stores would also need Class 3 SOT to sell) | $10k–$50k (dealer) / $150k+ (manufacture) | 30–50% | Phase 3 |
| 3 | **Firearm refurbishment / assembly** (AR builds, Cerakote, "certified refurbished" pawn guns) | Type 07 | $25k–$75k | 30–50% uplift on existing inventory | Phase 3 |
| 4 | **Precious-metals in-house melt + XRF assay** | None federal; VA precious-metals dealer permits already held | $15k–$40k (XRF ~$20k, furnace/molds) | Recaptures 3–8% refiner spread on 4,700+ dwt/yr | Phase 2 (parallel, low risk) |
| 5 | **Bench jewelry repair / laser welding / custom from scrap** | None | $20k–$50k | 60–80% service margin | Phase 2 (parallel) |
| 6 | **Firearms training / range** | VA range regs, NRA instructor certs | $500k+ (range) / $10k (classroom-only) | Range 15–25%; training 50%+ | Phase 4 / opportunistic |
| 7 | Check cashing / money services | VA SCC license, BSA/AML program | Regulatory burden high | Thin | **Not recommended** |

Items 4 and 5 are cheap, unlicensed, and use scrap the stores already generate — run them in parallel with Phase 1 so the integration program shows profit before the ammo line ships a round.

---

## 3. Phase 1 — Ammunition manufacturing (the core plan)

### 3.1 Education (Sept–Nov 2026)
- **Regulatory self-study (2 weeks):** ATF Form 7 instructions; 27 CFR 478 (FFL recordkeeping — manufacturer's A&D for ammunition is NOT required, only firearms); 27 CFR 53 (FAET); TTB F 5300.26 instructions; SAAMI cartridge and pressure standards (Z299 series, free downloads); NFPA 495 / VA SFPC Ch. 56; DOT 49 CFR 173 (ammunition ships as UN0012 Cartridges, Small Arms, ORM-D-equivalent "Limited Quantity" — affects e-commerce).
- **Machine-vendor training (mandatory, 3–5 days):** Mark 7 runs commercial start-up training at their facility and on-site setup at yours; Ammoload trains with machine purchase. Send Joshua plus the designated plant lead. This is where the actual "how to run a line" knowledge transfers — there is no university course.
- **Peer learning:** join NSSF (also unlocks Lockton Affinity insurance program and the FAET compliance webinars — NSSF runs "Common Errors on the FAET Quarterly Return"). Visit two small regional manufacturers (VA/NC/TN have several remanufacturers); most will host a fellow licensee.
- **Professional bench:** firearms-industry attorney (Form 7, entity, PLCAA posture, product warnings/labels), CPA with FAET experience (constructive-price memo), insurance broker via Lockton Affinity Outdoor / Joseph Chiarello & Co.

### 3.2 Conferences (attend in this order)
| Event | Dates | Why |
|---|---|---|
| **NASGW Expo** | Oct 13–15, 2026, Phoenix | Distributor-only show. Wholesale channel for Phase 4, and where component suppliers (brass, primers, powder, projectiles) actually do deals. Member-only — apply for NASGW manufacturer membership now. |
| **SHOT Show 2027** | Jan 19–22, 2027, Las Vegas | Machine vendors (Mark 7, Ammoload, Camdex, Dillon/Setpoint), component vendors, packaging, insurance, SAAMI, NSSF compliance seminars all under one roof. Book the Supplier Showcase day. |
| NSSF Range-Retailer Business Expo | Summer 2027 | Only if the range/training vertical (Phase 4) stays on the table. |
| Regional: Nation's Gun Show (Chantilly), Roanoke gun shows | Ongoing | Retail sell-through and brand seeding for the house ammo. |

### 3.3 Entity, premises, licenses (Oct 2026–Jan 2027)
1. **Form Valley Ammunition LLC** (VA SCC, ~$100) — separate EIN, separate bank account, separate QBO company file. Never commingle with FCF Inc books (same rule as the real-estate entities).
2. **Premises:** light-industrial lease, 2,500–5,000 sq ft, Roanoke or Harrisonburg corridor (nearest stores, nearest I-81 freight). Requirements: industrial zoning that expressly permits manufacturing, sprinklered or fire-marshal-approved for powder storage, room for a detached Type 4 magazine, 3-phase power preferred, loading door. Get a written zoning letter — ATF Form 7 asks for it.
3. **Fire marshal pre-consult** on smokeless-powder and primer quantities. Plan storage at ≤ 50 lb inside (approved cabinet) plus a Type 4 outdoor magazine for bulk; primers in original DOT packaging, separated from powder.
4. **ATF Form 7 — Type 07** ($150, 3-yr) with Part B responsible-person questionnaires, fingerprints (FD-258), photos, articles of organization, lease, zoning letter. Expect ATF IOI interview 60–90 days in. **Add Class 2 SOT (ATF Form 5630.7, $500 reduced rate)** only when suppressor work actually begins — no reason to pay it in year 1.
5. **TTB FAET registration:** file TTB F 5300.28 (Application for Registration) once licensed; calendar quarterly F 5300.26 returns (due last day of month after quarter). Set up a FAET liability account in the new QBO file from day one so the 11% is accrued on every sale, never discovered at quarter-end.
6. **Virginia:** no state ammunition-manufacturing license. Register for VA sales tax (retail sales), local business license (BPOL) in the locality, VA new-hire/Gusto workers-comp class for ammunition manufacturing.
7. **Insurance before the first primer arrives:** product liability + general liability + property (with explosives endorsement) + ATF-defense coverage. Lockton Affinity Outdoor (NSSF member program) and Joseph Chiarello & Co. are the two carriers that actually write small ammo makers. Budget $8k–$20k/yr at start.
8. **Trademark the house brand** (USPTO Class 13) before the first box is printed.

### 3.4 Machinery (order after license approval; 8–16 week lead times)
Start with **one pistol-caliber line (9mm)** — it is the highest-volume SKU in every store and the tightest in the 2026 market.

| Tier | Equipment | Approx. cost | Output |
|---|---|---|---|
| **A — recommended start** | Mark 7 Evolution or Apex 10 with autodrive + full sensor suite (powder check, primer check, bullet feeder, case feeder), plus Mark 7 brass processor | $35k–$60k all-in | 2,500–3,500 rds/hr, 1 operator |
| B — scale-up | Ammoload Mark X or Camdex 2100 series | $60k–$120k per line | 3,500–5,500 rds/hr, industrial duty |
| C — used market | Used Ammoload/Camdex lines surface at $25k–$40k | — | Only with vendor inspection + retraining |

Supporting equipment: case cleaning (wet tumbler/roll sizer for remanufactured brass) $5k–$10k; pressure/velocity testing — chronograph $1k, SAAMI-spec test barrel + pressure trace $10k–$25k (or contract testing at an outside lab per lot); gauging/ammo checker $2k; packaging — boxes, trays, label printer, case sealer $5k–$10k; magazine (Type 4) $3k–$6k; compressor, benches, ventilation, PPE $10k.

**Capital budget Phase 1: $120k–$180k equipment + $60k–$120k initial components (see 3.5) + $30k working/legal/insurance ≈ $210k–$330k.**

### 3.5 Components and supply (start contracting at NASGW)
- **Brass:** new (Starline, Jagemann, domestic — tariff-exempt) vs once-fired range brass (cheapest input; requires processing; product must be labeled "remanufactured"). Contract a range-brass source: local ranges, law-enforcement ranges, brass brokers. This is where a future range vertical (Phase 4) feeds back into the ammo line.
- **Primers:** the choke point. Federal/CCI/Winchester/Remington domestic; Fiocchi/Ginex/Sellier & Bellot imported (tariffed). Get on distributor allocation early — quantity commitments, not spot buys.
- **Powder:** Hodgdon/Alliant/Vihtavuori/Shooters World canister and OEM bulk. Bulk (8-lb+ or drum) is far cheaper but drives the magazine requirement.
- **Projectiles:** plated (Berry's, X-Treme, RMR), FMJ (Hornady, Zero), coated lead (cheapest for range ammo). Lock a plated-9mm 115/124 gr contract first.
- **Packaging:** 50-round boxes with house branding; bulk 250/500/1000 for range/wholesale.
- Rule of thumb, 9mm 115 gr plated remanufactured: components ≈ $0.10–$0.14/rd; new brass ≈ $0.16–$0.20/rd. Sept 2026 retail: $0.17–$0.25/rd bulk FMJ, median observed $0.31+/rd. Margin only works at volume and with sensor-verified quality — no shortcuts on powder-check sensors.

### 3.6 Production (Q1–Q2 2027)
- **Staffing:** 1 plant lead (mechanically inclined, ideally an experienced reloader — recruit via the stores' customer base and Indeed) + 1 operator/packer. Joshua is not the operator.
- **Quality system (this is what keeps you out of court):** written SOPs per caliber; every lot gets powder-charge verification (sensor + periodic scale check), OAL and case-gauge checks, primer-seat depth checks, and a chronograph/pressure test to SAAMI spec; lot numbers on every box; retained samples per lot; recall procedure written before day one. Document everything — the defense in a product case is the QA record.
- **Throughput target:** one 8-hour shift at 2,500 rds/hr ≈ 15–20k rds/day realistic after downtime → 300k–400k rds/month per line. Five stores can absorb an estimated 50k–150k rds/month of 9mm; the rest goes to wholesale/online (Phase 4).
- **Safety:** no smoking/no phones on floor, grounded equipment, static control, powder and primer handling SOPs, spill/fire procedures, blast-resistant primer feed shields, fire-marshal walkthrough before start.

### 3.7 Sales (channel plan)
1. **In-store, five doors (Month 1):** house brand at a price point under name-brand, bundled with every used-firearm sale ("gun + 100 rounds"), loyalty tie-in via Brevo. Bravo SKUs set up as new inventory via `new-inv-intake` with cost = transfer price.
2. **Web store on thevalleypawn.com (Month 2–3):** VA and most states shippable; block CA, NY, IL, MA, CT, NJ, DC, and city-restricted areas (verify list at go-live — attorney task). Ships UPS/FedEx ground, hazmat "Limited Quantity" labeling. List on AmmoSeek and GunBroker.
3. **Local B2B (Month 3+):** ranges, LE agencies (municipal PDs buy training ammo locally on quotes), sportsman's clubs, other FFLs. Ranges are the best account: they buy volume AND return brass.
4. **Wholesale via distributors (Year 2):** NASGW relationships; requires consistent lot quality, UPC/case packs, and volume. This is where line 2 gets justified.
5. **Marketing constraint:** zero Meta/Google spend (policy). Use Brevo (the existing gold/loan cadence gains an "ammo restock" send), website, in-store signage via `vp-brand-studio`, YouTube/Reels only where platform policy allows product shots without sales language, gun-show presence.

---

## 4. Phase 2 (parallel, Q4 2026–Q1 2027) — Precious metals + jewelry services
- **XRF analyzer** in the highest-volume scrap store first (Roanoke/Culpeper per the August scrap rankings: ROA 166 dwt, CUL 163) — stops under-buying on karat and stops overpaying on plated. ~$18k–$25k.
- **In-house melt to bars** (induction furnace ~$3k–$8k, molds, fluxes, ventilation): sell assayed bars to the refiner at a tighter spread than loose scrap; also enables "stone removal → melt → refine" on unsellable jewelry. Tie into the existing `precious-metals-settlement-handler`.
- **Bench jeweler service** (laser welder ~$15k–$30k, sizing/repair tooling): repairs, sizing, chain solder, custom from customer or scrap gold. Service margin 60–80%, drives foot traffic that loans and sells.
- No new licenses. Staffing: one certified bench jeweler (Harrisonburg or Roanoke), repair intake from all five stores via the existing inter-store transfer flow.

## 5. Phase 3 (2028) — Suppressors + firearm assembly on the Type 07
- Add Class 2 SOT to Valley Ammunition LLC; the pawn stores need Class 3 SOT ($500/yr reduced rate each, or centralize NFA sales in one store) to retail NFA items. With $0 tax stamps, suppressors are the growth category in every FFL's mix.
- "Certified refurbished" program: pawn firearms refinished/Cerakoted and function-tested at the plant, returned to stores at a higher price point. Manufacturer marking rules apply if a firearm is materially altered — attorney to define the line between gunsmithing and manufacturing.
- AR-15 assembly under house brand from stripped lowers (requires manufacturer's marking + A&D book + FAET 11% on rifles).

## 6. Phase 4 (2028+) — Range / training / wholesale scale
- Training classroom (concealed-carry, new-shooter) attached to the plant or a store: cheap, licensed via NRA/USCCA instructor certs, feeds ammo and firearm sales.
- Indoor range only if a site with an existing range or a build-to-suit partner appears — capital-heavy, but it closes the loop (brass in, ammo out, customers on site).

---

## 7. Budget and timeline summary

| Quarter | Milestone | Cash out (est.) |
|---|---|---|
| Q4 2026 | LLC, attorney/CPA engaged, NASGW, lease signed, Form 7 filed, insurance bound, component contracts | $40k |
| Q1 2027 | SHOT Show, ATF interview/approval, machine delivered, vendor training, fire-marshal sign-off, XRF + melt in stores | $150k–$200k |
| Q2 2027 | First lots (9mm), in-store launch, first FAET return, web store live | $60k components |
| H2 2027 | Second caliber (5.56 or .45/.40), LE/range accounts, wholesale prep | $50k–$100k |
| 2028 | Class 2 SOT, suppressors/refurb program, line 2 | $100k+ |

Break-even math (9mm line): at $0.12/rd component cost, $0.02/rd labor/overhead, 11% FAET on a ~$0.19 constructive wholesale price (≈$0.021/rd), landed cost ≈ $0.16/rd. Retail at $0.24/rd = 33% gross at the store plus manufacturer margin; wholesale at $0.19 = ~16% manufacturer gross. 150k rds/month at blended $0.05 contribution ≈ $7.5k/month; line pays back in ~18–24 months on in-store volume alone, faster with B2B.

---

## 8. Integration with the existing operating system (Rule 4 — additive)
- New QBO company for the LLC; FCF Inc buys ammo as inventory (vendor: Valley Ammunition LLC). No new gates on the existing books.
- Bravo: ammo SKUs via `new-inv-intake` — no pipeline change.
- Reporting: add a weekly "Ammo Line" section (rounds produced, lots passed, rds sold by store, margin) to the existing Monday KPI compile once production starts — new task, alongside, never inside `monday-bravo-combined-*`.
- Compliance: add Valley Ammunition LLC to `Compliance/FFL_REGISTRY.md` when the license issues; FAET quarterly return goes on the same calendar as the sales-tax monthly task; renewal watch note — ATF mail for FCF licenses currently lands at 844 Cypress Crossing (FL); set the new license's mailing address deliberately.
- Register rows and this plan live in `Projects/Vertical Integration/`.

---

## 9. Decisions only Joshua can make (everything else executes autonomously)
1. **Go/no-go and capital ceiling** for Phase 1 (~$210k–$330k over 9 months). Cash vs equipment financing (QBO lending tools show peer offers; SBA 7(a) works for equipment but many lenders decline ammo — Lockton/NSSF have lender lists).
2. **Entity ownership:** Joshua personally vs FCF Inc as the LLC member (CPA input on the 1120S/K-1 and on the affiliated-corporation FAET rule).
3. **Brand name** for the house ammunition (Valley Ammunition / Valley Arms / a non-"Pawn" name — recommended so wholesale accounts don't carry the pawn association).

Once those three are answered: file the LLC, engage counsel/CPA/insurance, register for NASGW and SHOT, and open the premises search — all without further check-ins.

---

## Sources (verified 2026-09-05)
- ATF FFL types and fees — https://www.atf.gov/firearms/federal-firearms-licenses ; https://rocketffl.com/ffl-cost/ ; https://www.e4473.com/ffl-license-types/
- Type 06 vs 07 and Class 2 SOT — https://www.pewpewtactical.com/types-of-federal-firearms-licenses/ ; https://gununiversity.com/ffl-license-types/
- Explosives exemption for smokeless powder / small-arms components — https://www.law.cornell.edu/cfr/text/27/555.141 ; https://www.atf.gov/explosives/questions-and-answers?page=4
- Export reform (ammo to EAR 0A505, no DDTC registration) — https://www.federalregister.gov/documents/2020/01/23/2020-00574/international-traffic-in-arms-regulations-us-munitions-list-categories-i-ii-and-iii ; https://www.exportsolutionsinc.com/resources/blog/export-control-reform-for-firearms-ammunition-part-1 ; https://orchidadvisors.com/are-you-registered-with-ddtc/
- FAET 11% / TTB F 5300.26 / constructive sale price — https://www.ttb.gov/regulated-commodities/firearms/taxes-and-tax-exemptions ; https://www.ecfr.gov/current/title-27/chapter-I/subchapter-C/part-53/subpart-J/section-53.95 ; https://www.ecfr.gov/current/title-27/chapter-I/subchapter-C/part-53/subpart-J/section-53.97 ; https://www.nssf.org/event/tax-compliance-common-errors-on-the-firearm-ammunition-excise-tax-faet-quarterly-return/
- Virginia fire code smokeless-powder storage — https://law.lis.virginia.gov/admincode/title13/agency5/chapter52/section530/ ; https://up.codes/viewer/virginia/va-fire-code-2018/chapter/56/explosives-and-fireworks
- $0 NFA tax effective 2026-01-01 — https://www.nssf.org/articles/now-that-the-dust-has-settled-on-the-one-big-beautiful-bill/ ; https://www.fastbound.com/nfa-tax-stamp/
- Market 2026 — https://www.ironscout.ai/learn/blog/9mm-ammo-prices-2026 ; https://www.ironscout.ai/caliber/9mm ; https://firehole.com/arms/2026-supply/ ; https://www.leappayments.com/ammo-shortages-2026-bulletproof-inventory/
- Equipment and training — https://commercial.mark7reloading.com/commercial-start-up ; https://www.mark7reloading.com/commercial-line ; https://ammoload.com/mark-x-loading-machine/
- Conferences — https://www.nssf.org/event/shot-show/ ; https://nasgw.org/ ; https://nasgwexpo.org/agenda
- SAAMI / NSSF / insurance — https://saami.org/membership/membership-requirements/ ; https://www.nssf.org/articles/outdoor-sports-and-recreation-insurance-products-now-available-to-nssf-members/ ; https://locktonaffinityoutdoor.com/nssf/
- Pawn margins — https://www.bravostoresystems.com/post/how-to-increase-revenue-in-your-pawn-shop-gun-store-or-consignment-business-27-proven-strategies-for-2026
