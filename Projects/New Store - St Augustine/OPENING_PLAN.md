# Valley Pawn — St. Augustine Store Opening Plan (all departments)

Version 1.0 · 2026-10-31 · Status hub: `STATUS.md` · Launch marketing: `GRAND_OPENING_MARKETING_BLITZ.md` · Lease: `LEASE_NEGOTIATION.md` · Law/licensing detail with cites: `REGULATORY_CHECKLIST_FL.md`

**How to use this file.** Each department has a checklist. `[ ]` open, `[x]` done, `[~]` in progress. Owner column: **C** = Claude runs it autonomously, **J** = only Joshua can do it, **P** = Preston / store team, **V** = vendor. "T-" dates are relative to **Soft Open** (planning assumption: March 2027). Re-baseline every T- date the day the lease is signed.

---

## 0. Critical path (what gates what)

```
Lease signed (address fixed)
 ├─► FL foreign qualification ($70) ─► Fictitious name "Valley Pawn" ($50, after newspaper ad) ─► DOR sales/reemployment tax (free)
 │        └─► FDACS pawnbroker application ($300 + $28.25/person, Livescan) ─── 60–90 days ───► LICENSE  ─┐
 ├─► ATF Form 7 Type 02 ($200, FD-258 cards, photos, CLEO copy) ── ~60–90 days, IOI visit ──► FFL ─► FDLE FPP enrollment ─┤
 ├─► Zoning sign-off ─► TI permit (sealed plans) ─► build-out ─► fire final ─► Certificate of Occupancy ─────────────────────┤
 ├─► Sign permit (sign contractor files) ─► fabrication ─► install ───────────────────────────────────────────────────────┤
 ├─► Bravo store #6 + network + cameras + safes/vault + showcases ───────────────────────────────────────────────────────┤
 └─► Hire manager (T-75) + 2–3 associates (T-45) ─► 2-week training in a VA store + 1 week on site ─────────────────────┤
                                                                                                                         ▼
                                                                        County BTR (needs FDACS license copy) ─► SOFT OPEN ─► Grand Opening (+4 wks)
```

The two long poles are **FDACS** and **ATF**. Both need the executed lease. File both within 10 business days of signing. Everything else fits inside their window.

---

## 1. Real Estate / Lease — owner C (negotiation support), J (signature)

- [~] Close the Ash Properties negotiation (see `LEASE_NEGOTIATION.md` for positions and the clause-by-clause review list). **C** drafts every reply; **J** signs.
- [ ] Confirm jurisdiction of the parcel (unincorporated St. Johns County vs City of St. Augustine) from the Property Appraiser record — changes the BTR/zoning path. **C**, before signing.
- [ ] Zoning confirmation letter from St. Johns County Planning ($30) stating pawnshop = permitted retail/general business use in the parcel's zoning; check Overlay District (affects signs). **C** files, T-120.
- [ ] Lease must state permitted use: pawn lending, retail of new/used goods, jewelry & precious-metals buying, firearms & ammunition sales under FFL. Non-negotiable — a lease that is silent or excludes firearms blocks the FFL. **C** reviews draft.
- [ ] Regulatory-out clause (60-day termination if law bars pawn or firearm sales at the premises). **C**.
- [ ] Delivery condition in writing: "white box" with electrical, plumbing, HVAC in good working order + landlord warranty on HVAC for 12 months; as-built drawings and HVAC service records delivered at possession. **C**.
- [ ] Exclusive-use protection: no other pawn / buy-gold / check-cashing / title-loan tenant in the center. **C**.
- [ ] Signage rights: fascia sign + panel on pylon/monument, both sides; right to "Coming Soon"/"Grand Opening" banners for 90 days. **C**.
- [ ] Security rights: bars/roll-down grille or security film, exterior cameras, alarm — landlord consent pre-granted in lease. **C**.
- [ ] Assignment/sublet to an affiliate without consent; Joshua personal guarantee capped and burning off (see lease file). **C** proposes, **J** decides.
- [ ] Lease abstract into `Valley Pawn OS/STORE_LEASES.md` (new row: St. Augustine) + executed PDF to Drive `Store Leases/` and `Compliance/evidence/lease-staugustine/`. **C**, day of signing.
- [ ] Calendar: rent commencement, free-rent end, renewal-notice windows, escalation dates → Google Calendar + Open Items Register. **C**.
- [ ] Backup sites kept warm until signature: 801 S Ponce de Leon (purchase, $1.59M); Jacksonville/Palm Coast/Daytona leads from Joshua's 10/26 trip — log each in `LEASE_NEGOTIATION.md` §4. **C**.

## 2. Legal, Licensing & Compliance — owner C (prep/filing), J (fingerprints, signatures)

Detail, cites, fees and URLs: `REGULATORY_CHECKLIST_FL.md`.

**Entity (first — everything else references the FL document number)**
- [ ] Sunbiz search: is Full Circle Finance Inc already authorized in FL? Is "Valley Pawn" registered as a FL fictitious name? **C**, Mon 11/2 (blocked 10/31 by Cloudflare; retry in Chrome with site permission).
- [ ] Order VA SCC Certificate of Good Standing (original, ≤90 days old). **J** (payment) or **C** on approval.
- [ ] File FL Application by Foreign Corporation (CR2E007), $70, FL registered agent = Joshua Davis, 844 Cypress Crossing Trail, St. Augustine FL 32095. **C** prepares; **J** signs. 1–3 weeks.
- [ ] Publish fictitious-name ad once in a St. Johns County newspaper (St. Augustine Record legal notices), then file "Valley Pawn" fictitious name, $50. **C**.
- [ ] FL DOR: FCF Inc **already holds a Florida reemployment-tax account (RT-4222641; DR-1 confirmation 203-2680-1626) with past-due quarterly filings since Jan 2026 — clear that first** (Compliance/OBLIGATIONS.json `fl-reemployment-tax`), then add the St. Augustine location for sales & use tax (6% + 0.5% St. Johns = 6.5%; surtax capped at first $5,000/item) on the existing account. Free. **C**.
- [ ] Calendar: FL annual report Jan 1–May 1 ($150; $400 late), fictitious-name renewal (5 yrs), BTR renewal Oct 1, FDACS renewal annually. **C**.

**Pawn license (FDACS, F.S. 539)**
- [ ] Livescan fingerprints, ORI **FL922060Z**, for Joshua + every officer/director + the store manager/operator. **J** (in person; schedule the week the lease is signed).
- [ ] Net-worth test ($50k) via most recent 1120-S — avoids the $10k bond. Pull from Silverline Tax. **C**.
- [ ] Bravo FL pawn-ticket form — confirm Bravo's FL template meets the 539.001(8) checklist (digital form allowed since 7/1/2025, ≥12-pt font). **C** with Bravo.
- [ ] Identify receiving law-enforcement agency + electronic reporting platform (SJSO Property Crimes, (904) 824-8304) — phone call; no public email. **C/J**.
- [~] File FDACS-10111 via ConsumerCompliance.FDACS.gov, $300 + $28.25/person. **PRE-FILLED 10/31 → `forms/FDACS-10111_ValleyPawn_StAugustine_PREFILLED.pdf`; packet list in `forms/FDACS_FILING_PACKET.md`.** **J** notarizes/signs. Target: ≤10 business days after lease signing.
- [ ] Post-license: register with SJSO reporting system; 30-day hold on pawns and buys; 25%/30-day max service charge; 30-day grace before forfeiture — configure Bravo FL store rules accordingly. **C/P**.

**Firearms (ATF + FDLE)**
- [~] ATF Form 7 (5310.12), **Type 02 Pawnbroker**, $200/3 yrs, FD-258 cards + 2x2 photo for the Responsible Person; CLEO copy to Sheriff Robert A. Hardwick, 900 Law Enforcement Way, St. Augustine FL 32092. **Every answer is in `forms/ATF_FORM7_ANSWER_KEY.md` (10/31); official PDF (Rev. June 2025) still to be downloaded from atf.gov in Chrome and filled.** **J** fingerprints/photo/SSN/signs. File within 10 business days of lease.
- [ ] Premises ready for IOI interview: safe/vault for firearms, A&D system (same as Roanoke), locked display. **P/V**.
- [ ] FDLE Firearm Purchase Program dealer enrollment after FFL issues ($5/check, billed monthly). **C**.
- [ ] Program Bravo FL store for: 3-day waiting period on all retail firearm sales (exempt CWL holders etc.), **no transfers under 21**, FPP for sales and redemptions. **C/P**.
- [ ] Add FL location to the FFL compliance calendar/automation (`Compliance/` project, FFL Listing Mgmt). **C**.

**Local**
- [ ] County (or City) zoning approval → TI building permit → fire plan review → CO. **V** (architect/GC) files; **C** tracks.
- [ ] St. Johns County Local Business Tax Receipt ($18–$30; needs FDACS license copy + sales-tax cert). City BTR first if inside city limits. **C**.
- [ ] Sign permit (sign contractor files; 10 days, 30 in overlay). **V**.
- [ ] Confirm with County Attorney (904-209-0805) that no county pawn or firearm waiting-period ordinance exists (none found 10/31). **C**.

**Federal programs already running in VA — extend to FL store**
- [ ] Precious-metals AML program (31 CFR 1027) — add location. **C**.
- [ ] Form 8300 cash reporting, OFAC screening, MLA covered-borrower check, TILA disclosures (Bravo), GLBA privacy notice + Safeguards program. **C/P**.
- [ ] Required posters (FL minimum wage $15.00 from 9/30/2026, RT-83, workers' comp, FCHR, child labor; federal set). **C** orders.

**Insurance**
- [ ] Add FL location to commercial package (property, GL, jewelers block/inland marine for pledged goods, crime/employee dishonesty, cyber); FL workers' comp (4+ employees rule; list FL in 3.A); confirm FFL-related coverage. Use the brokers already quoting the portfolio (`Life OS/Insurance`). **C** requests quotes T-90.
- [ ] Landlord COI requirements from lease delivered before possession. **C**.

## 3. Finance, Capital & Books — owner C (modeling/books), J (approval)

**Opening capital — planning ranges only; replace every line with a quote before approval**

| Line | Planning range | Basis / note |
|---|---|---|
| Loan portfolio float (pawn loans outstanding by month 6) | $150k–$250k | Ramp; mirrors a young VA store. |
| Opening retail inventory (new + transferred aged inventory from VA stores) | $50k–$100k | Transfer aged/overstock from the 5 VA stores first — near-zero cash. |
| Showcases, counters, shelving, jewelry cases, lighting | $35k–$60k | Quote 2 fixture vendors; reuse any surplus from VA. |
| Safes / vault (jewelry + firearms), security glass, pigpen | $20k–$45k | Match Roanoke's firearm storage. |
| Security: Nest cameras (same stack as VA stores), alarm, monitoring | $5k–$12k | Enables Store Traffic Counter + Conduct Watch day one. |
| Build-out beyond white box (walls, counters, paint, flooring, electrical/data, bathroom) | $30k–$75k | Depends on delivery condition negotiated. |
| Signage (fascia + pylon panels + window) | $12k–$25k | Sign code + landlord criteria. |
| POS / IT (Bravo 6th store license + setup, workstations, printers, network, phones with SMS-enabled main line) | $10k–$20k | Confirm Bravo per-store pricing; SMS-capable line is a brand requirement. |
| Licenses, filings, fingerprints, bond (if any), legal review of lease | $3k–$8k | Govt fees are small (~$700); lease attorney is the variable. |
| Deposits (first + last month, utilities) | $10k–$12k | Per counter: first + last instead of 2-month deposit. |
| Working capital — payroll + opex for 6 months pre-breakeven | $120k–$180k | 1 manager + 3 associates at FL wages; rent after free-rent period. |
| Grand-opening marketing blitz | $15k–$25k | Detail in blitz plan §7. |
| **Total planning envelope** | **~$460k–$810k** | Lower end if inventory/fixtures transfer from VA and build-out is light. |

- [ ] Replace ranges with quotes; present one budget for approval. **C** → **J**, T-120.
- [ ] Funding plan: cash vs line of credit vs equipment financing; keep shareholder distributions in view (2026 distributions already exceed 2025 — see Drive `Valley Pawn Distributions and YoY 2026.xlsx`). **C** models; **J** decides. Not financial advice — bring to Silverline Tax.
- [ ] Pro forma P&L month 1–24 using VA store ramp curves from Bravo EOM data (Valuation Core project). **C**.
- [ ] QBO: new Location/Class "St. Augustine" (follow `books-tax-strategy` gates — no journal entries; new store expenses coded to the new location from day one; pre-opening costs tracked separately for the §195 start-up election). Confirm with Silverline. **C**.
- [ ] Bank: operating account/till cash procedures identical to VA (daily funds verification extends to store #6). **C/P**.
- [ ] FL payroll taxes in Gusto (reemployment 2.7% initial), FL new-hire reporting (20 days), E-Verify (company ≥25 employees → mandatory). **C**.
- [ ] Sales tax config: 6.5% on merchandise, service charges not taxed; resale certificate from refiner; eBay destination tax. **C** with CPA sign-off in writing.

## 4. Build-out, Facilities & Security — owner V (GC/architect), P (layout), C (tracking)

- [ ] Layout: sales floor / jewelry counter / loan counter with pigpen / firearms counter / back-of-house pawn storage (racking by ticket) / vault room / office / restroom. Use Culpeper or Roanoke floor plan as the template. **P/J**.
- [ ] Architect: sealed TI plans (FL-licensed), FBC Mercantile occupancy; include electrical/data drops for Bravo workstations, cameras, music. **V**, T-110.
- [ ] GC bids (3) with the white-box scope from the lease as baseline. **C** solicits, **J** picks. T-105.
- [ ] Permit submitted T-95; construction T-75 → T-20; fire final + CO by T-10.
- [ ] Security: Nest cameras (counter, registers, entrance, sales floor, back room, exterior), monitored alarm, safes/vault delivered and anchored before the ATF IOI visit. **V/P**.
- [ ] Music/announcements: CloudCover (Pandora) zone for store #6. **C**.
- [ ] Utilities, internet (business fiber + LTE failover), phone line with SMS (brand requirement: every store number is call-or-text). **C/P**.
- [ ] Supplies via Amazon Business — new ship-to address + cost center "St. Augustine" in the saved address book (`amazon-business-ordering` skill). **C**.
- [ ] Opening supplies order: tags, pawn envelopes, jewelry supplies, test kits/XRF, scales (FL legal-for-trade), cleaning, office. **P** list → **C** orders.

## 5. Systems, POS & Automations — owner C

- [ ] **Bravo:** add store #6 (license/pricing, FL pawn rules, FL transaction form, 3-day firearm wait, under-21 block, 6.5% tax, FL-specific receipts). Gmail draft to support@bravostoresystems.com (cc Ashley N.) is in Drafts, ready to send. **C**, T-90.
- [ ] Bravo store code for the pipeline (proposed **STA**). Register NEW pipeline cells/handlers for the 6th store — **additive only, never edit existing handlers** (Rule #4). `bravo-store-cycle` extended to 6 stores via a new cycle definition. **C**, T-30.
- [ ] Update `valley-pawn-context` (locations table, hours rule, Maps URL `Valley+Pawn+St+Augustine+FL`, store email staugustine@fcfpawn.com, employee directory), email footer 6-store directory, Brevo templates, `directory-listing-monitor` canonical NAP. **C**, at address confirmation.
- [ ] Google Workspace: staugustine@fcfpawn.com mailbox/group; Slack channel #staugustine + add to ops channel rotations. **C**.
- [ ] Gusto: new FL work location, FL tax setup, pay schedule, onboarding flows (`onboard-employee`, Chekkit/Slack onboarding skill). **C**.
- [ ] Chekkit (reviews/messaging), Publer (social scheduling), Brevo (FL list + store CTA block), BrightLocal (new Location + Active Sync), Canva brand assets, website location page + store schema — all via existing skills (`directory-listing-push`, `facebook-post`, `brevo-context`, `vp-brand-studio`). **C**, T-60 (unpublished until address confirmed; live at T-45).
- [ ] Reporting fleet: daily funds verification, intake margin, aged inventory, loan/layaway reviews, employee rankings, dress-code check, store traffic counter, conduct watch, bonus program row — each gets a **new** store-6 entry; existing tasks untouched. **C**, T-14 → T+14 as data appears.
- [ ] Controlio endpoints, Google Home/Nest account structure, CloudCover zone. **C**.

## 6. People — HR, Hiring & Training — owner J (manager hire), P (training), C (pipeline)

- [ ] Decide: hire local manager vs relocate a VA manager (Joshua's 10/22 #general ask). **J**, T-90.
- [ ] Flip `HIRING_SWITCH.md` St. Augustine → ON; re-sponsor the Indeed Store Manager listing; add Sales & Loan Associate (FL) listing cloned from VA template with firearms background-check line restored if FFL confirmed. **C**, T-75.
- [ ] Screen the 24 existing applicants (3 "New": Castaneda-Olsen, Lemelle, Nolan) per `vp-hiring-pipeline` rules; Joshua interviews FL at (804) 930-4221. **C** books; **J** interviews.
- [ ] Offer letters (FL — no non-compete overreach; FL min wage $15.00 from 9/30/2026); background checks consistent with FDACS employee rule (no theft/fraud conviction within 5 yrs) and ATF RP rules for the manager. **C**.
- [ ] Manager start T-45: 2 weeks shadowing in Culpeper or Roanoke (firearms), 1 week in Harrisonburg (jewelry volume), then on site. **P**.
- [ ] Associates start T-21: Training Program project curriculum + Ask Valley Pawn handbook bot; FL-specific module (539 rules, 3-day wait, under-21, FPP). **P/C**.
- [ ] Handbook/P&P: FL addendum (FL E-Verify, reemployment, final-pay rules, FL posters) as a NEW version per `policy-lifecycle` naming rule. **C**, T-45.
- [ ] Bonus program: add store #6 with a ramp regime (no target penalty first 3 months) in `bonus_rules.json` as a NEW regime entry. **C**, T-14.
- [ ] Uniforms/dress code, name badges, schedules in Gusto. **P**.

## 7. Inventory & Loan Capital — owner P (merchandising), C (analytics)

- [ ] Pull aged-inventory (>180 days) and overstock lists from all 5 VA stores; select transfer stock for FL opening floor (tools, electronics, jewelry, instruments; firearms per FFL-to-FFL transfer rules). **C** builds the list from the Aged Inventory reports, T-60.
- [ ] Inter-store transfers in Bravo; truck/freight scheduled T-14; firearms via FFL transfer paperwork to the new FFL. **P**.
- [ ] New-goods opening order (phones/accessories, ammo if selling, jewelry findings). **P**.
- [ ] Gold/silver buying: refiner account (Elemetal/Silver Bears already vendors) add FL ship-from; FL resale certificate to refiner. **C**.
- [ ] Loan float: cash plan and safe limits per the VA daily funds process; initial float wire schedule. **C/J**.
- [ ] Pricing: use Valuation Core T1/T2/T3 and MobilePawn participation from day one. **C**.

## 8. Marketing & Grand Opening — owner C

Full plan in `GRAND_OPENING_MARKETING_BLITZ.md`. Summary gates:
- [ ] T-90: nothing public. Build assets, lists, pages (unpublished). Reserve GBP/FB/Apple/Bing listings only once the address is contractually fixed.
- [ ] T-60: "Coming Soon" — window wrap + banner, GBP created (opening-date field), FB page live, website location page live, PR teaser, hiring posts.
- [ ] T-30: Pre-launch — email to FL-zip customers, geo ads, EDDM mailer drop T-14, community outreach, review-generation setup.
- [ ] T-0 soft open (quiet, 2–4 weeks): fix ops, gather first reviews.
- [ ] Grand Opening weekend (+4 wks): event, promos, press, influencers, radio, giveaways.
- [ ] T+30 → T+90: sustain cadence; measure "how did you hear about us" in Bravo customer notes.

## 9. Operations readiness — owner P

- [ ] Opening-day runbook: till/safe counts, pawn/buy/sale/layaway flows, FPP procedure, 8300, OFAC, MLA, LE reporting, hold tags, end-of-day. **P/C**.
- [ ] Mystery-shop the first week; Conduct Watch + Store Traffic live. **C**.
- [ ] Week-1 and week-4 reviews with Joshua (numbers only — no technical noise, Rule 16). **C**.
- [ ] Store #6 enters the Monday CEO scorecard and monthly scorecard. **C**.

---

## Open questions carried on the Open Items Register

- Ash Properties response to the 10/22 counter (expected week of 11/2).
- Sunbiz status of FCF Inc / "Valley Pawn" in FL.
- SJSO electronic pawn-reporting platform.
- Whether the parcel is in a county Overlay District (sign/architectural review).
- Bravo 6th-store pricing and FL form availability.
