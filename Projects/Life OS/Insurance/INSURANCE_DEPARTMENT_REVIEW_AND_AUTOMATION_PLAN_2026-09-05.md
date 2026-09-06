# Insurance Department — Full Review & Automation Plan
Date: 2026-09-05 · Status: PLAN ONLY — nothing built, nothing sent · Domains: all 3 (Valley Pawn, Real Estate, Personal)

---

## 1. What the "department" is today (verified against files, Gmail, Drive, task registry)

| Layer | What exists | Verdict |
|---|---|---|
| System of record | One file: `Life OS/Insurance/INSURANCE_PORTFOLIO.md`, last updated 2026-08-22. Header still says Bald Rock is "owned by FCF Inc" (wrong — corrected 8/10 and 9/2). Missing: Kin policy #, surety bond, Hardinberry policy #, Cybertruck-era changes, EPLI/ED app status, claim. | Stale, partial, wrong on ownership |
| Renewal tracking | A 5-row hand table in the same file. Kin 10/15 renewal appears **only** in a mail-brief STATUS file. No reminders anywhere. | No calendar, no alerts |
| Skills | **Zero** insurance skills. All 5 property skills have empty "Insurance: carrier / policy / renewal" placeholders. `valley-pawn-context`, `personal-life-context`, `real-estate-context`: no insurance content. | Every session starts blind |
| Scheduled tasks | ~170 registered tasks; **none** touch insurance. `ceo-mail-brief` surfaces insurance mail ad hoc ("1-Action" tier), then it goes silent — the Ricci nudge was flagged 8/26 and never re-chased. | No cadence |
| Open Items Register | One row (8/22), non-standard columns, **no next-action cell**. No rows for the 10/15 Kin renewal, the 11/28 auto renewal, or Howard's 8/24 asks. | Not tracked |
| Documents | Declarations/EOIs scattered across ≥6 Drive folders ("07 Insurance", "06 Business - Leases Insurance Licenses", per-property folders, Desktop Import, 2022 imports). No index. | Findable only by search |
| Ownership truth | Bald Rock stated four ways across live files (FCF Inc / Farming Infinity Mountains LLC / Joshua personally / "left FCF July 2026"); `ENTITY_STRUCTURE.md` referenced in memory **does not exist on disk**. Named-insured on the Bald Rock policy = Joshua Davis. | Insurance can't be right until this is one table |

### Live exposures found (as of 9/5, from actual email — not metadata)
1. **Howard Baker (JM Partners) 8/24 email — unanswered 12 days.** He needs: approve Lexington→125 Walker St / delete 645 Oakley change; Lexington supplemental app; IWC Properties address (Culpeper AI form); **market-value inventory limits per store** (pledged + unpledged); Employee Dishonesty supp app; EPLI app; BI limits per store; BPP limits per store; keep/drop Hired & Non-Owned Auto ($125/loc); when to remove 817 Richmond. Umbrella $2M/$5M sits with Laura Sullins — nothing back.
2. **Kin homeowners (KINHOFL275099318) renews 10/15** — ServiceMac notice 8/31 is **unread**; needs mortgagee clause check ("ServiceMac ISAOA ATIMA"). Coverage A still never pulled (MSFH ≤$700K gate).
3. **Personal auto renews 11/28** — upgrade declined 8/22 ($4,413/6mo), still at 50/100 with 4 vehicles incl. Cybertruck, no umbrella, no MedPay.
4. **Broker shop: 4 brokers emailed 8/22 (Ricci, WeShop/Augustyniak, Leigh, Ancient City) — zero replies.** Rebecca emailed 3× (8/22, 8/31, 9/1). Email-only outreach has failed twice now (April and August).
5. **Bald Rock STR on a homeowners form (GEICO/Homesite)** — claim-denial risk; Steadily declined 7/30. No STR-form quote in flight.
6. **Workers' comp:** NEXT declined 6/18 (state fund only), Joshua said "get a quote," none arrived. 6/18 loss-runs/COI request to ULC never answered. WC renews 6/13.
7. **Claim PBIH26050007** (~$10K necklace, HDI/NARS) — payment still pending; last adjuster reply 8/7; Joshua's 8/10 nudge unanswered. $7,000 settlement paid to customer 8/24 must be reconciled against payout in QBO.
8. **No umbrella anywhere** (personal or commercial). Unchanged since April.
9. Surety bond #72603580 renewed 9/2 (continuous) — not in the portfolio at all.

---

## 2. Expert board

PANEL: commercial-lines risk manager (CPCU, pawn/FFL specialty) · ops-automation architect (owns the Cowork/launchd fleet conventions) · controller/data-integrity reviewer.

OPTIONS WEIGHED
- **A. Keep the single markdown file, add reminders.** For: cheap. Against: the file is already wrong and nobody updates it; reminders on bad data produce confident wrong nudges.
- **B. Buy an insurance-tracking SaaS.** For: built-in renewal alerts. Against: another login, no link to Bravo inventory / Gusto payroll / entity table; Joshua becomes the data-entry clerk.
- **C. Registry-driven system inside the existing OS (recommended).** One machine-readable registry + one context skill + three scheduled tasks that read the registry and the mailbox. Same pattern already proven for leases (`STORE_LEASES.md`) and HR (9/5 plan). Against: 2–3 weeks of build; needs the ownership table settled first — which is a prerequisite either way.

DECISION: **C.** Insurance is a data problem first (what's insured, under whom, until when, at what limit) and a cadence problem second. Fix the data spine once, then let tasks drive every renewal, every broker thread, and every coverage-vs-reality check without Joshua remembering anything.

REJECTED: A (perpetuates the stale-file failure), B (disconnected from the enterprise data that makes the audit possible), and "just answer Howard's email" alone (fixes today, not the pattern).

---

## 3. Target architecture (all additive — nothing existing is modified)

### 3.1 Data spine — `Life OS/Insurance/`
- **`INSURANCE_REGISTRY.json`** (source of truth, one record per policy): entity / named insured / property or line / carrier / policy # / term start–end / premium / key limits & deductibles / broker + contact / mortgagee or AI clauses / declarations doc link / status / last verified date. Seeded from the 8/24 "Current Coverage as of 7-31-26" attachment, ServiceMac notice, Steadily receipts, Kin decs, Progressive ID cards, surety bond, and Drive PDFs.
- **`INSURANCE_PORTFOLIO.md`** — regenerated from the registry (human-readable view + renewal calendar). Never hand-edited again.
- **`ENTITY_STRUCTURE.md`** — created for real this time (it doesn't exist). Ownership table = REAL_ESTATE_OS.md §portfolio, "this file wins." Registry validates every named insured against it.
- **`CLAIMS.md`** — open/closed claims with adjuster, status, last contact, payout, QBO reconciliation flag.
- **`BROKER_PIPELINE.md`** — every broker/carrier approached, date, channel, response, decision. Prevents the April/August "emailed blind, stalled" repeat.
- **Drive `Insurance/` vault** — one folder, per-policy subfolders; existing PDFs **copied** in (originals untouched), registry links point here.

### 3.2 Context skill — `insurance-context`
Loads registry + entity table + house rules (STR must be on STR form; named insured must match title; FFL pawn needs specialty market; no umbrella = primary gap; Joshua's deliberate 2022 cuts are not "gaps"; broker outreach = phone + email, never email alone). Referenced from the 5 property skills' empty placeholders (one line each: "see insurance-context"), `personal-life-context`, `real-estate-context`, `valley-pawn-context`.

### 3.3 Scheduled tasks (Cowork, Sonnet tier; Haiku for the inbox watch)
| Task | Cadence | Does |
|---|---|---|
| `insurance-inbox-watch` | daily 6:30 AM | Gmail search on all carrier/broker/adjuster/servicer senders + keywords across both inboxes. New declarations/renewal notice → updates registry + files PDF to the vault. Broker/adjuster thread with no reply in 5 business days → sends the nudge itself (existing thread, Joshua's voice, `my-writing-style`). Anything needing a decision → one line in the existing `ceo-mail-brief` (no new Slack noise, Rule 16). Logs to Open Items Register. |
| `insurance-renewal-runner` | Monday 7:30 AM | Walks the registry. T-90: request renewal + 2 competing quotes (email + phone script). T-60: comparison table drafted. T-30: DM Joshua a **recommendation** (bind X at $Y — approve/decline) — the only touch he gets. T-14: confirm bound. Post-bind: verify decs, named insured, mortgagee clause, limits vs. request; file to vault. |
| `insurance-coverage-audit` | quarterly (1st of Jan/Apr/Jul/Oct) | Coverage vs reality: named insureds vs `ENTITY_STRUCTURE.md`; STR/LTR occupancy vs policy form; Cypress Coverage A vs MSFH gate; **pledged + unpledged inventory value per store from the Bravo pipeline CSVs vs scheduled limits**; Gusto payroll vs WC class/estimate; vehicles on the auto policy vs actual garage; umbrella status; additional-insured requirements from `STORE_LEASES.md`. Output: gap report to the register + one plain DM only if a gap is new. |
| `insurance-claims-follow-up` | Wednesdays | Each open claim: nudge adjuster at 7 days silent, check for payment, flag QBO reconciliation to the books flow. Closes the loop on PBIH26050007. |

### 3.4 On-demand skill — `insurance-coi-request`
Landlord/vendor asks for a certificate or additional-insured endorsement → pulls the lease party from `STORE_LEASES.md`, emails the broker with exact wording, tracks until received, files to vault. (Culpeper/IWC Properties is the first use.)

---

## 4. Phased execution (no check-ins after go; Joshua only sees §6 decisions)

**Phase 0 — Stop the bleeding (days 1–3)**
1. Create `ENTITY_STRUCTURE.md`; fix the 13 files/skills still saying Bald Rock = FCF Inc (list in the 9/5 inventory).
2. Reply to Howard's 8/24 with everything answerable now: approve Lexington/Oakley change; IWC address from `STORE_LEASES.md`; per-store inventory market values from the Bravo pipeline (pledged + unpledged, retail value); attach the completed ED + EPLI answer sheets from the prior session (locate on disk/Drive); recommended BI/BPP limits per store; drop HNOA (no company vehicles); 817 Richmond removal deferred until Farming Infinity policy is placed.
3. Kin: read the ServiceMac notice, pull the declarations, record Coverage A, confirm mortgagee clause. Register row + 10/15 in calendar.
4. Broker shop, phone-first: call Augustyniak (Chubb-appointed), Ancient City, Blue Marlin, Ricci; log to `BROKER_PIPELINE.md`. Add two STR-specialty markets for Bald Rock (Proper Insurance, CBIZ/American Modern, Foremost) and one FFL-pawn specialty market for the commercial side.
5. WC: chase the state-fund quote (NEXT) and re-send the loss-runs request to ULC with a 5-day follow-up. Claim: nudge David Roper on payment; add QBO reconciliation item.
6. Seed `INSURANCE_REGISTRY.json` from all documents above; regenerate the portfolio file.

**Phase 1 — Spine + skill (week 2):** registry validator, `insurance-context` skill, property-skill pointers, Drive vault copy, `CLAIMS.md`, `BROKER_PIPELINE.md`.

**Phase 2 — Cadence (week 2–3):** `insurance-inbox-watch`, `insurance-renewal-runner`, `insurance-claims-follow-up` registered with `model:` pins per `scheduled-task-models`; each proven on one real cycle (Kin 10/15 is the live test).

**Phase 3 — Audit + COI (week 3–4):** `insurance-coverage-audit` wired to Bravo CSVs and Gusto; `insurance-coi-request` skill; first audit run before 10/1.

**Phase 4 — Run:** 11/28 auto renewal and the umbrella placement are the first full renewal-runner cycles. Hardinberry 1/9, Woods Walk 4/12, WC 6/13, commercial 7/2 follow automatically.

---

## 5. What this fixes, in Joshua's terms
- Nothing renews unnoticed; every renewal arrives as one "approve/decline" message 30 days out with quotes already in hand.
- Brokers and adjusters get chased automatically — no more 12-day silences on either side.
- Coverage is checked against what's actually true (who owns what, what inventory is on the floor, who's on payroll, what's parked in the garage) every quarter.
- One place has every policy, every document, every open claim.

## 6. Decisions that stay with Joshua (business/money — not technical)
1. **Go / no-go** on this plan.
2. Limits to request from Howard: recommended BI $100K/store (Roanoke/Staunton already), BPP $50K/store, Employee Dishonesty $100K, EPLI $100K, umbrella $2M commercial / $2M personal — approve or change.
3. Broker strategy: consolidate everything under one Chubb/PURE-appointed broker if one will take the FFL pawn side, vs. keep JM for commercial + new broker for personal/rentals.
4. LLC consolidation of the three income properties (with Liana) — changes umbrella architecture from three programs to two.
5. Auto: accept a competing quote near the declined $4,413/6mo level, or hold 50/100 (recommendation will come with quotes by 10/28).

---

## 7. Rules applied
Additive only (Rule 4) · no diagnosis from metadata (Rule 12 — every exposure above is from the email body) · Rule 16 (no technical/failure noise to Slack; the only DM is the T-30 recommendation and new gaps) · Rule 14 (register row logged 9/5) · `scheduled-task-models` tiering · entity separation (real-estate correspondence from zapvp1@me.com, never fcfpawn.com — the 7/31 Howard email already violated this and is noted).
