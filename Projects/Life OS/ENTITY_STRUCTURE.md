# Entity Structure — Canonical Ownership Table

**Created:** 2026-09-05 · **Owner:** Joshua Davis · **Scope:** all three domains (Valley Pawn, Real Estate, Personal)

> ## THIS FILE WINS
> When any file, skill, scheduled-task prompt, spreadsheet, or generated output disagrees with the
> table below about **who owns what** or **who is the named insured on a policy**, this file is
> correct and the other source is stale. Do not "reconcile" toward the other source. Fix the other
> source to match this one and log it in the Correction manifest.
>
> Upstream evidence for this table: `Life OS/REAL_ESTATE_OS.md` ("Portfolio at a glance",
> "Ownership — confirmed directly by Joshua 2026-09-03", and "Legal entity structure — Farming
> Infinity"), the IRS CP-575 letters and VA SCC filings in the Drive folder **"Farming Infinity"**,
> and Joshua's direct corrections on 2026-08-10, 2026-09-02 and 2026-09-03.

---

## The one fact that keeps getting wrong

**Full Circle Finance Inc DBA Valley Pawn owns ZERO real property and never has.** It operates
5 leased Virginia pawn stores. 282 Bald Rock Road was never FCF Inc's — there is no "moved out of
FCF Inc in July 2026" period to reference either. Any sentence that says or implies otherwise is
wrong and must be corrected to match the table.

The real cross-domain overlap is a **tax-return overlap on Joshua's side, not an entity overlap on
FCF's side:** every Farming Infinity LLC is a single-member disregarded entity, so its activity
flows to **Joshua's personal Form 1040 (Schedule E)** — the same return that receives his K-1 from
FCF Inc's Form 1120-S. Nothing from the property LLCs goes through FCF Inc's 1120-S, its books, or
its P&L.

---

## Ownership table

| Entity | Type / EIN / SCC | Beneficial owner(s) | Assets held | Named insured on current policy (if known) | Notes / unconfirmed items |
|---|---|---|---|---|---|
| **Full Circle Finance Inc DBA Valley Pawn** | Virginia S-corporation · EIN 47-1198118 | Joshua Davis (sole shareholder). **Hillary has no ownership interest** (she is an employee only). | 5 **leased** VA pawn stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro) + Roanoke FFL. **No real property, ever.** | Commercial BOP IK29P109337-05 (HDI Global via JM Insurance Agency Partners), GL, Workers Comp GC29P101236-02 (ULC) — named insured presumed FCF Inc, not yet verified against the dec page | ⚠️ The FCF commercial BOP schedules "Building, 817 Richmond Ave = $577,000" — but that building is owned by Farming Infinity, LLC, not FCF Inc. Named-insured / insurable-interest alignment on that policy is an **open question** — flag to broker, do not resolve here. |
| **Farming Infinity, LLC** (original) | Virginia single-member LLC, disregarded for federal tax · VA SCC S8306609 (formed 5/30/2019) · EIN 81-3269313 (confirmed via 1099-MISC; CP-575 letter still to be located) | Joshua alone | **817 Richmond Avenue, Staunton VA 24401** — commercial, leased to FirstCash. Mortgagee: DuPont Community Credit Union. | See FCF Inc row — the building appears on FCF's commercial BOP; named insured for the building itself not confirmed | Gross-vs-NNN lease conflict unresolved (see `richmond-ave-property`). Suspended passive loss entering 2025: $26,391. |
| **Farming Infinity Mountains LLC** | Virginia single-member LLC, disregarded · VA SCC 12045879 (eff. 7/13/2026) · EIN 42-4031872 (CP-575 issued 7/23/2026, in Drive) | Joshua alone | **282 Bald Rock Road, Verona VA 24482** — short-term rental (Airbnb + VRBO). Purchased 2016, basis $405,000 per deed. | **GEICO / Homesite policy 39168908** (EOI dated 2024-10-08) — named insured on the policy is **"Joshua Davis" individually**, not the LLC | ⚠️ Named-insured vs. title question: policy names Joshua individually while the LLC is intended owner. Also confirm the deed is actually in the LLC's name (LLC formed July 2026; property purchased 2016). Both are **open questions — noted, not resolved here.** Steadily declined to quote 7/30/2026; STR-form adequacy review needed. |
| **Farming Infinity Virginia LLC** | Virginia single-member LLC, disregarded · VA SCC 12045876 (eff. 7/13/2026) · EIN 42-3980374 (CP-575 issued 7/21/2026, in Drive) | Joshua alone | **14300 Woods Walk Lane, Midlothian (Chesterfield County) VA 23112** — active long-term rental, real tenants (Avail / Zillow rent collection). Sch E activity #1. | Steadily landlord policy 6116141556531 (renews ~4/12) — named insured not confirmed | **Deed-into-LLC unconfirmed.** Property was held personally for years (in service 8/1/2008); LLC formed July 2026. Suspended PAL entering 2025: $0. |
| **Farming Infinity Tennessee LLC** | Virginia single-member LLC (formed in VA despite the name), disregarded · VA SCC 12045877 (eff. 7/13/2026) · EIN 42-3788196 (CP-575 issued 7/13/2026, in Drive) | **Intended** holder — but the property is currently owned by **Joshua & Hillary jointly** (see next row); LLC is single-member (Joshua) | **Intended:** 148 Hardinberry Street, Oak Ridge TN | — | **Deed transfer NOT confirmed** — "two-step deed transfer" was under TN attorney review July–Aug 2026. Needs TN foreign-LLC registration if it will hold TN property. Also note a joint-owned property going into a single-member LLC is itself a question for counsel. Anderson vs. Roane County discrepancy unresolved. |
| **Joshua Davis, personally** | Individual · Form 1040 (joint with Hillary) | Joshua | Sole member of all four Farming Infinity LLCs above (so beneficially: 817 Richmond, 282 Bald Rock, 14300 Woods Walk). Sole shareholder of FCF Inc. | Named insured on GEICO/Homesite 39168908 (Bald Rock); listed driver on Progressive auto 998062549 | All Farming Infinity SMLLC activity + the FCF Inc K-1 land on this return. 2025 return on extension — due 10/15/2026. |
| **Joshua & Hillary Davis, jointly** | Individuals · joint Form 1040 | Joshua & Hillary | **844 Cypress Crossing Trail, St. Augustine FL 32095** (Parcel 072085-0710) — primary personal residence since ~Aug 2025, converted from LTR. **No LLC, no EIN.** · **148 Hardinberry Street, Oak Ridge TN** — long-term rental (was STR during 2025–26 capital-spend period). | Cypress Crossing: Kin Interinsurance Network homeowners (KIN-HO-FL, bound Oct 2024) — named insured presumed Joshua & Hillary. Hardinberry: Steadily landlord (renews ~1/09) — named insured not confirmed. Auto: Progressive 998062549, named insured **Hillary D. Davis**, driver Joshua. | Cypress Crossing suspended PAL entering 2025: $24,681 (depreciation-recapture exposure on eventual sale). Hardinberry suspended PAL: $6,600. |
| **Salt Run Landscape Co.** | Separate business — entity type, EIN, and ownership split **not documented in this OS** | Not documented — do not assume | Not documented | — | Placeholder row so no session assumes Salt Run is part of FCF Inc or a Farming Infinity LLC. Fill in from Joshua / Drive before relying on anything about it. |
| **Davis Management LLC** | Planned Florida LLC (Sunbiz), intended S-corp election — **NOT FORMED**, no EIN | Would be Joshua & Hillary | None | — | Setup checklist + MSA template exist in Drive; nothing filed. Do not treat as existing. |

### Quick ownership answers

- "Who owns Bald Rock?" → Farming Infinity Mountains LLC → Joshua alone. **Not FCF Inc.**
- "Who owns Richmond Ave?" → Farming Infinity, LLC (original) → Joshua alone.
- "Who owns Woods Walk?" → Farming Infinity Virginia LLC (intended; deed unconfirmed) → Joshua alone.
- "Who owns Hardinberry?" → Joshua & Hillary jointly (Farming Infinity Tennessee LLC intended; deed unconfirmed).
- "Who owns Cypress Crossing?" → Joshua & Hillary jointly, personally. No LLC.
- "What real estate does Valley Pawn / FCF Inc own?" → **None.** Five leased stores.
- "Does Hillary own part of Valley Pawn?" → **No.**

---

## How to use

1. **Any file, skill, scheduled-task prompt, or generated output that states property ownership,
   entity structure, EINs, or insurance named-insureds must match this table.** If you are about
   to write such a statement, look it up here first — do not carry it forward from another file.
2. **When Joshua corrects an ownership or entity fact:** update **this file first**, then
   propagate to `REAL_ESTATE_OS.md`, `LIFE_MAP.md`, `BUSINESS_OS.md` Rule 12, the property skills,
   `enterprise-map`, `valley-pawn-context`, and any bookkeeping rule files
   (`Quickbooks Set UP/VENDOR-CLASSIFICATION-MAP.md`, `_ac_categorize.py`). Add a row to the
   Correction manifest for every file touched.
3. **Bookkeeping consequence:** because FCF Inc owns no real estate, **no property cost ever
   belongs in the FCF Inc P&L or QBO books** — not Bald Rock, not Cypress, not Woods Walk, not
   Richmond, not Hardinberry. Property costs go to the property's own ledger / Schedule E basis.
4. **Named-insured column is a "known so far" column, not a resolution.** Where it says "not
   confirmed" or flags a mismatch, that is an open question for Joshua and his broker — record it,
   do not decide it.
5. **Do not re-derive ownership from older files or skills.** Several still carried "Bald Rock =
   FCF Inc" after the 2026-08-10 correction and were only fixed on 2026-09-05 (see manifest). If
   you find another, fix it and add it below.

---

## Correction manifest

Every file corrected to match this table. Add a row for each future propagation.

| Date | File | What was wrong | What it now says |
|---|---|---|---|
| 2026-09-05 | `Life OS/LIFE_MAP.md` — domain table row 2 | Bald Rock "business-owned", owner "FCF Inc (Bald Rock)" | Bald Rock owned by Farming Infinity Mountains LLC (Joshua); pointer to this file |
| 2026-09-05 | `Life OS/LIFE_MAP.md` — "Why they're kept separate" | "…just because FCF Inc owns Bald Rock" | "…FCF Inc owns no real estate; Bald Rock is Farming Infinity Mountains LLC" |
| 2026-09-05 | `Life OS/LIFE_MAP.md` — Hard separation rule | "Bald Rock is legally FCF Inc, same entity and tax return as Valley Pawn" | Overlap is on Joshua's 1040 (SMLLC Schedule E + FCF K-1), not a shared entity |
| 2026-09-05 | `Life OS/LIFE_MAP.md` — Cross-domain overlap bullet | "Bald Rock (Domain 2) is legally owned by Full Circle Finance Inc" | Owned by Farming Infinity Mountains LLC / Joshua; tax overlap is on the 1040 |
| 2026-09-05 | `Life OS/LIFE_MAP.md` — Quick facts | (no pointer) | Added bullet pointing to `ENTITY_STRUCTURE.md` |
| 2026-09-05 | `Life OS/PERSONAL_OS.md` — Personal Finance | "Bald Rock is FCF Inc money" | "Bald Rock is Farming Infinity Mountains LLC money (Joshua's 1040, not FCF Inc)" |
| 2026-09-05 | `Valley Pawn OS/BUSINESS_OS.md` — Rule 12 | Pawn and real estate "share the same legal entity (FCF Inc) and the same tax return" | Separate entities; the only shared thing is Joshua's personal 1040 |
| 2026-09-05 | `Life OS/Insurance/INSURANCE_PORTFOLIO.md` — STR header | "(owned by FCF Inc)" | "(Farming Infinity Mountains LLC / Joshua — named insured on policy: Joshua Davis)" |
| 2026-09-05 | `Quickbooks Set UP/VENDOR-CLASSIFICATION-MAP.md` — Shreckhise Shrubbery row | "BUSINESS (FCF Inc)… company-owned STR" | PERSONAL / Farming Infinity (282), not an FCF deduction — matches the file's own property-code table |
| 2026-09-05 | `Quickbooks Set UP/_ac_categorize.py` — SHRECKHISE rule | label "(FCF Inc)", bucket BUSINESS | label "282 Bald Rock — grounds", bucket PROPERTY |
| 2026-09-05 | `Life OS/OPEN_ITEMS_REGISTER.md` — Culpeper lease amendment row | "that property left FCF Inc in July 2026" | "that property was never FCF Inc's (owned by Farming Infinity Mountains LLC)" |
| PENDING | `enterprise-map/SKILL.md` lines 101, 108 | "Bald Rock STR (FCF Inc money)"; "Domain 1's entity for tax purposes" | Proposed replacement recorded in the 2026-09-05 CHANGELOG entry — skill cache is read-only from a session |
| PENDING | `valley-pawn-context/SKILL.md` line 518 | "Full Circle Finance Inc operates a short-term vacation rental at:" | Proposed replacement recorded in the 2026-09-05 CHANGELOG entry — skill cache is read-only from a session |
| 2026-09-05 (verified, no edit needed) | `real-estate-context`, `bald-rock-property` skills | Flagged 9/2/26 in VENDOR-CLASSIFICATION-MAP as carrying the FCF Inc claim | Checked 2026-09-05: both already state Bald Rock is Farming Infinity Mountains LLC / never FCF Inc. The 9/2 flag is stale for these two; `enterprise-map` and `valley-pawn-context` are the ones still wrong. |
