# Tax Management Department — Full Review + Automation Plan
**Date:** 2026-09-05 · **Scope:** all three domains (FCF Inc/Valley Pawn · Farming Infinity LLCs/real estate · Joshua & Hillary personal) · **Status:** PLAN — nothing built yet, per Joshua's instruction

Sources read in full: `Taxes 2026/` (5 master docs, TY2025 Tax Prep tree, REQ_1120S/REQ_1040, Vehicle Basis, REVIEW 2026-09-04), the claude.ai "Taxes" project (8 docs + memory), `Sales Tax/` (STATUS, script, both workbooks), 10 tax-touching scheduled tasks, 10 skills (books-tax-strategy, qbo-context, quickbooks-online, real-estate-context, personal-life-context, 5 property skills), PERSONAL_OS, REAL_ESTATE_OS, BANK_ACCOUNTS, OPEN_ITEMS_REGISTER, BUSINESS_OS, CHANGELOG, the live scheduled-task registry, launchd, and the actual workbook contents (Rule 12).

---

## 1. What the department is today

**Three execution layers (the enterprise-map only knows about two):**

| Layer | Tax items living there | Health |
|---|---|---|
| Cowork scheduled tasks (`~/Documents/Claude/Scheduled`) | `eom-bravo-gl-export` (1st 6am) · `eom-bravo-gl-export-watchdog` (2nd 8am) · `sales-tax-monthly-update` (1st 8am) · `quarterly-capex-sweep` (Jan/Apr/Jul/Oct 1) · `northwest-registered-agent-daily-check` (daily) · `annual-board-review` (Jan 1) | GL export + sales-tax **both blocked since 9/1** (8/29 unposted in Bravo, "Post" click failed on all 5 stores). August sales-tax row is blank (verified in workbook). |
| Native launchd (`com.valleypawn.*`) | none tax-specific | — |
| **Orphan layer: `~/.claude/scheduled-tasks/`** (Claude Code CLI tasks) | `daily-sales-tax-sweep` (8:02am, DRY-RUN — ledger IS updating, last row 2026-09-05 $241.11/day, cumulative $9,345.54) · `july-va-sales-tax-filing-prep` (one-shot, never evidenced) | Running, but invisible to the registry, fleet-guardian, LIVE-STATE, and every prior audit. Nobody knew it was alive. |

**Manual / human-carried:** VA ST-1 filing + payment (Joshua, 20th) · Mercury $250/day reserve transfer (bank UI, unverified since 7/20) · estimated payments · BPOL/property tax/SCC/FFL renewals · every CPA interaction (Silverline; Claude never contacts them) · all deed/entity work · evidence hunting for basis.

**Knowledge base (12+ documents, no single owner):** Taxes 2026 master docs (evidence logs, strategy notes, REQ maps, One-Page Status) · claude.ai Taxes project (Master Plan v19, Numbers & Models, Whole-Org Target Structure, Entity Plan v7, Retirement Roadmap, Working Notes, Correction List) · `Quickbooks Set UP/` (FY2025 close plan, tie-out, readiness review, vehicle memos, worklists) · 4 OS/context files · 10 skills. The TY2025 Tax Prep folder has 13 numbered slots; **8 are empty** (all the business-side slots: payroll, Bravo inventory, books, banking, leases/licenses, info returns, FL residency, tax admin).

---

## 2. Findings (ranked by exposure)

1. **Hard dates inside 10 days with no owner task.** FCF 1120-S extended due date is **9/15/2026** (files only say "on extension — Silverline to confirm"). Q3 federal/VA estimated payments due **9/15**. Bald Rock appraisal **9/15 11am**. Nothing in the fleet watches any of these. The 10/15 personal deadline, the cost-seg critical path (appraisal ~9/29 + 3–4 wk study lands after 10/15), and the Form 3115 fallback decision are all tracked only in prose.
2. **No tax calendar exists anywhere.** ~30 recurring obligations (ST-1 20th, 941/940, VA-5/VA-6, VEC, FL RT-6, 1099/1096, W-2/W-3, BPOL ×5, SCC annual fees ×5 entities, TN FONCE/annual report, Augusta TOT, property tax ×5 counties, FFL renewals ×5, VA PTET election, estimates ×8, IRS/VA installment plans, §121 window, refund SOLs) are scattered across ≥8 files. Known live misses: FL Reemployment Tax filings missing since Jan 2026 (account # never entered in Gusto, FDOR notice 8/3) · Chesterfield 2025 property tax payment returned 1/5/26, never re-paid · Culpeper BPOL $955.86 due 5/1 bounced, unpaid · VA sales tax back months Sep–Dec 2025 + Apr–May 2026 · no evidence July or August 2026 ST-1 was filed.
3. **The month-end tax chain has a single point of failure.** Both the GL export and the sales-tax figure require every Bravo day to be posted, discovered at 6 AM on the 1st with no human available. A pre-flight on the 28th–last day would surface it during business hours with days of runway. The sales-tax number itself only needs taxable-sales totals, not a posted Consolidated GL — the coupling is a design choice, not a Bravo constraint (to be verified against the daily pipeline cells).
4. **Sales-tax system is half-built and undocumented as running.** Phase 1 dry-run is alive in the orphan layer; Phase 2 (money) is a manual Mercury transfer nobody verifies (a read-only Mercury API token exists at `~/.vp_secrets/mercury_token` and could); Phase 3 (filing prep) was never built; script divides by calendar days where the plan said business days; `#sales-tax` channel never created; STATUS.md cadences are stale.
5. **Books→tax feeds are gone or manual.** `weekly-payroll-to-qbo`, `monthly-reconciliation-report`, `monthly-cpa-report`, `vsp-nics-fee-monthly-check` are absent from the registry but still listed in BUSINESS_OS. No account has ever been reconciled in QBO. Gusto payroll JEs are manual. The QBO MCP connector (discovered 9/2) is unverified for read accuracy. The 1099 flow has never run.
6. **Evidence tooling silently loses receipts** (REVIEW 9/4): 54,616 partial `.emlx` (attachments never downloaded — a 10-minute Mail setting), ~1,200 image-only PDFs/photos never OCR'd, `photosindex.py` failing nightly while the wrapper reports success, Hillary's Gmail not indexed, card statements for 8 cards never pulled. Every "no invoice found" conclusion for those vendors is unreliable.
7. **Three sources of truth that disagree.** CPA firm named as Lodestar in one skill, Silverline elsewhere (same firm, renamed); "there is no external bookkeeper" vs "bookkeeper maintains zapvp1"; BUSINESS_OS Rule 12 and LIFE_MAP still say Bald Rock is on FCF's return (it is Joshua individually / Mountains LLC); Master Plan says "three EVs fully §179'd" as fact while memory says Rivian is a lease; 817 lease called NNN in two docs after being corrected to gross; VA PTET "sunsets 2027" vs "made permanent"; Working Notes cross-references (§-7…§-12) point to sections that no longer exist. The claude.ai project docs were last updated 7/22–7/31 and predate the $621K Bald Rock basis work.
8. **Evidence-log totals are hand-maintained.** The Full Evidence Log's own header still prints $475,119.42 while §39 carries $621,683.83; the 9/3 pass found the §1 footer stale and a $107.41 headline error. Totals must be computed, never typed.
9. **Structural exposures with no home:** 2016–2024 Bald Rock income never on any located return; J Davis Group final 1120-S "in nobody's plan"; shareholder loan $164K / APIC $127K undocumented; ~$127K personal spend through FCF accounts; furniture bucket ~$280K carried at cost against an FMV cap; vehicles depreciated on FCF books it doesn't own.

---

## 3. 🧑‍⚖️ Expert Board — target architecture

**Panel:** controller/accounting-systems analyst · tax-compliance operations lead (multistate small-business) · SRE/data-pipeline engineer · data-integrity reviewer (the three posting gates).

**Options weighed**
- *A. Patch each broken task in place* — fastest; but leaves the calendar, orphan layer, and doc drift, and violates additive-only on hardened tasks.
- *B. Buy a compliance-calendar/sales-tax SaaS (DAVO, TaxJar, a bookkeeper)* — offloads filing; but the July plan already rejected DAVO-style cost, Bravo has no API for them, and it does nothing for basis/entity/CPA work, which is where the dollars are.
- *C. Build a Tax OS layer alongside the existing tasks* — one machine-readable obligations register, one guardian, one monthly close, one annual package builder, one master map with a generated LIVE-STATE block, all additive. Slower to stand up (3–4 weeks) but it is the only option that makes the department predictable rather than heroic.

**Decision: C, sequenced so the 9/15–10/15 window is protected first.**
Rejected A (re-litigates hardened infra, no calendar). Rejected B (doesn't touch the exposure that matters, still needs the data plumbing anyway). House rules: additive only; every new task is Sonnet-tier (`model:` frontmatter), Rule 16/18 compliant (DM-only, withhold rather than caveat), registered in `fleet/expected_outputs.json`, and gated behind the three posting gates for anything that touches QBO.

---

## 4. Build plan

### Phase 0 — Protect the next 40 days (this week; no new infra)
- **Deadline sheet for Joshua/Silverline**, one page, computed from the files: 9/15 1120-S extended date (confirm filed/extended), 9/15 Q3 estimates ($13,804 fed / $3,710 VA vouchers), 9/15 appraisal, 9/21 Augusta court date, 10/1 next month-end run, 10/15 1040+760PY, cost-seg timing and the Form 3115 fallback question. Delivered as a DM + file; logged in the register.
- **Unblock month-end**: run the 8/29 post + GL pull + JE + August sales-tax row with a human present (one Parallels approval from Joshua), then close July/August ST-1 numbers into a file-ready packet.
- **Verify the Mercury reserve**: read balance via the existing read-only token, compare to the $9,345.54 ledger, report the gap once.
- **Stop the silent receipt loss** (REVIEW items 7–9): patch the refresh wrapper to fail loudly, run `ocr_run.py` on the image-only PDFs, add 8 card statements to the "what to download" list.

### Phase 1 — Tax Calendar + Guardian (week 1–2)
- `Life OS/TAX_CALENDAR.json` — every obligation as data: entity, agency, form, cadence rule, due-day, owner, amount source, evidence-of-completion pattern (mail subject / file / QBO txn), status. Seeded from the ~30 items above including the four known delinquencies.
- `bin/tax_calendar.py` — computes next-due dates, flags overdue, renders `Life OS/TAX_CALENDAR.md` (human view) and feeds the LIVE-STATE block.
- `tax-calendar-guardian` — Monday 7 AM, Sonnet: 30-day look-ahead + overdue list, verifies completion against evidence (unified-search mail, Drive, QBO) not memory, one plain DM. Fleet-guardian entry added. Rule 16: never to field.
- `estimated-tax-prep` — 14 days before each federal/VA due date: pulls YTD P&L via QBO MCP (once verified), computes safe-harbor vs. voucher, DMs the number. Payment stays Joshua's.

### Phase 2 — Sales tax end-to-end (week 2–3)
- **Decouple**: new pipeline cell (additive, own AHK handler clone) or reuse of the daily sales CSVs to compute per-store taxable sales without requiring a posted Consolidated GL; `sales-tax-monthly-update` unchanged, a new `sales-tax-monthly-compute-v2` runs alongside and both must agree for one cycle before v1 is retired.
- **Pre-flight** `eom-unposted-days-check` — 28th and last day of month, 4 PM: lists unposted days per store, DMs Joshua so a human fixes it in business hours. Never re-drives Bravo itself.
- **Move the daily sweep out of the orphan layer** into a native launchd agent (pure python, no Claude) staged in `fleet/`; register `daily-sales-tax-sweep` in the registry as a verifier only. Fix the calendar-vs-business-days rule per the plan of record. Create `#sales-tax` (or keep DM — Joshua's call, default DM).
- `sales-tax-reserve-reconcile` — weekly, Mercury API balance vs ledger cumulative, drift ≥1 day flagged.
- `monthly-va-st1-prep` (the never-built Phase 3) — 10th of month: per-locality figures, dealer discount, delinquent-month balances, "file by the 20th" packet. Filing/payment stays Joshua's until he says otherwise; the packet makes it a 5-minute task.

### Phase 3 — Books→tax monthly close (week 3–4)
- **QBO MCP accuracy gate**: one-time reconciliation of MCP P&L/BS vs Chrome-exported reports; result recorded in `qbo-context`. Only after passing is the MCP used by any task.
- `monthly-close-checklist` — 3rd of month: Bravo JEs present per store, Gusto JE present, uncategorized count, bank-feed backlog, sales-tax row populated, GL residual within tolerance; writes `Quickbooks Set UP/closes/YYYY-MM.md`; one DM. Replaces the vanished `monthly-reconciliation-report` without touching it.
- `monthly-gusto-payroll-je` — Gusto MCP (`list_payrolls`) → JE package (`GUSTO-PAY-YYYY-MM`) per the "two allowed JE types" rule; posted via the existing Chrome path under the session lock; source file + row range cited (Gate 2). Replaces the vanished `weekly-payroll-to-qbo`.
- `quarterly-payroll-filings-check` — after each quarter: confirms 941/VEC/VA-5/FL RT-6 filed via Gusto; FL RT-6 account gap surfaces here until closed.
- `annual-1099-prep` — Jan 5: vendors ≥$600 from QBO, W-9 status, package for the QBO 1099 flow.

### Phase 4 — Evidence & basis pipeline (week 4–5)
- Trackers become the source of truth: `build_tracker.py` emits the evidence-log totals section; the markdown headline is generated, never typed. Same pattern for 844 Cypress.
- `quarterly-capex-sweep` extended to append to the evidence logs and CAP GAIN trackers with source citations (additive step, existing steps untouched).
- Unified-search hardening per REVIEW 9/4: loud-fail wrapper, OCR corpus, skill doc corrected (8 corpora, real scheduler), Hillary's mailbox added once she signs in.
- Contemporaneous logs as data: Bald Rock hours log and FL work-location day-log as simple sheets with a monthly reminder — these are the audit-defense items every strategy doc asks for and nothing captures.

### Phase 5 — Annual cycle + CPA handoff (week 5–6; first live use TY2025)
- `tax-prep-package-builder` — on demand + Jan 15: populates the 13 numbered TY folders from sources automatically (Gusto W-2/941s via MCP, QBO TB/P&L/BS/fixed assets via MCP, Bravo 12/31 inventory via a pipeline cell, bank statements from the statement folders, 1099s received via unified-search, property P&Ls). REQ_1120S/REQ_1040 checklists become a status file with found/missing per line.
- `CPA_PACKAGE_INDEX.md` + versioned Drive folder `TY2025 → Silverline` — one place, one version; superseded intake packages marked so nothing wrong gets sent. Joshua remains the only sender.
- `CPA_QUESTION_QUEUE.md` — the ~20 open Silverline questions (PTET, 3115 fallback, reasonable comp, Bald Rock income history, J Davis Group final, vehicles, shareholder loan, furniture FMV, material participation) consolidated into batched asks instead of one-offs.

### Phase 6 — One map, one truth (runs alongside)
- `Life OS/TAX_OS.md` — the department's master map: entities/EINs/agencies, the calendar, the automation inventory, CPA/advisor roster, open structural questions, plus a generated `<!-- LIVE-STATE -->` block (task health, last month closed, sales-tax row status, reserve vs ledger, days to next deadline). Enterprise-map gets a Step 2c pointing to it and a note that a third execution layer exists.
- Stale-fact sweep: BUSINESS_OS Domain 3 table and Rule 12, LIFE_MAP, Sales Tax STATUS.md, books-tax-strategy preparer name, bookkeeper status, 817 lease type, PTET status, vehicle §179 claim. Superseded docs get a header pointing to the current one (never deleted).
- claude.ai Taxes project: local `Taxes 2026/` declared source of truth; project docs receive a short "current state" doc and supersession headers.

---

## 5. What genuinely needs Joshua (everything else proceeds without him)
1. **Money/filings** (his by right): pay Chesterfield 2025 property tax; Culpeper BPOL; VA back months + July/Aug ST-1 once packets are handed over; 9/15 estimates; IRS/VA installment status.
2. **Ten minutes of setup that only he can do**: Mail → Accounts → Download Attachments: All; Hillary signs into her Gmail once for indexing; FL RT-6 account number into Gusto; confirm the Mercury $250/day transfer is still active.
3. **One click each** when the permission classifier blocks autonomous registration of a new scheduled task or launchd agent (it blocked three this week) — files will be staged in `Valley Pawn OS/pending-tasks/` ready to register.
4. **Send the Robbie (appraiser) draft** before 9/15 and put the Form 3115 fallback in front of Silverline this week (decision is Silverline's, the ask is Joshua's).
5. **Business decisions** for the CPA queue: PTET election, reasonable-comp level, retirement plan sponsor/TPA, whether to amend 2024 for QBI.

## 6. Dependencies, blast radius, risk
- Touches: Bravo trigger pipeline (new cells only; `bravo_watcher.ahk` gets registration lines with backups, same as 9/5), QBO Chrome path + session lock, Gusto/QBO/Drive/Mercury/unified-search read paths, fleet-guardian expected outputs, enterprise-map + 4 OS files.
- Nothing hardened is edited: `eom-bravo-gl-export`, `sales-tax-monthly-update`, `quarterly-capex-sweep`, existing AHK handlers and cell names stay as-is; v2 runs alongside and must agree before v1 retires.
- Risk the narrow fix would miss: fixing the 8/29 Post click alone leaves the calendar, the orphan layer, and the 10/15 critical path untouched — the same failure repeats on 10/1.
- Cost: all recurring tasks on Sonnet; the package builder on Opus once a year.

## 7. Sequencing summary
Week 0 (now): Phase 0 · Weeks 1–2: Phase 1 + Phase 6 map skeleton · Weeks 2–3: Phase 2 · Weeks 3–4: Phase 3 · Weeks 4–5: Phase 4 · Weeks 5–6: Phase 5, first full run for TY2025.

*Claude's organizing analysis, not a filed position or CPA opinion. Silverline signs the returns.*
