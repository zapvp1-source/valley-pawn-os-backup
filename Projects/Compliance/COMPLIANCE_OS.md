# COMPLIANCE OS — Full Circle Finance Inc DBA Valley Pawn

**The map of the Compliance department. Read this first for ANY licensing, permit, bond, filing,
lease-date, insurance, HR-compliance, or firearms-records question.** Created 2026-09-06 from the
department review (`COMPLIANCE_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md`).

## How it works (one register, one calendar, one vault, one brief)

```
OBLIGATIONS.json  ──render_calendar.py──►  COMPLIANCE_CALENDAR.md   (never hand-edit the .md)
      │                                          │
      │  every date/number lives here            └─►  state/horizon.json  ──►  compliance-weekly-brief (Mon 7:30 AM, DM to Joshua only)
      │
      └─►  evidence/<obligation-id>/   the license / bond / permit / filing / receipt that proves the row
```

- **Add or change an obligation:** edit `OBLIGATIONS.json`, drop the proof in `evidence/<id>/`, run
  `python3 bin/render_calendar.py`. That's the whole workflow.
- **A row may only say `current` when a file exists in `evidence/<id>/` and `last_verified` is a real
  check against the authority (eZ Check, portal, receipt) — never a run record.** The renderer lists
  violations under "Integrity problems".
- **Rule 4 (additive):** nothing here modifies an existing task or handler. Existing trackers keep their
  narrative role; their dates were imported into the register:
  `FFL_REGISTRY.md` · `FFL_LISTINGS_STATUS.md` · `VSP-NICS-Fee-Payment-Runbook.md` ·
  `Valley Pawn OS/SURETY_BONDS.md` · `Valley Pawn OS/ROANOKE_PRECIOUS_METALS_PERMIT.md` ·
  `Valley Pawn OS/STORE_LEASES.md` · `Life OS/Insurance/INSURANCE_PORTFOLIO.md` · `Sales Tax/STATUS.md`.
  When those files change a date, change the register the same day.
- **The HR plan's `COMPLIANCE_CALENDAR.md` is this calendar** (`class: hr` rows). One calendar, not two.
- **Owner semantics:** `joshua` = money, signature, government filing, or a people/strategy decision.
  Everything else is `claude` (drives it without checking in) or `preston` / `store-manager`.
- **Rule 13:** never post a Drive link or any of these files into an employee-visible channel.
  **Rule 16/18:** the brief is plain language, DM-only, and withholds any section whose data did not verify.

## Department boundaries — who warns on what (set 2026-09-06)

Three registries now exist and they must never warn on the same thing twice:

| Registry | Owns | Warned by |
|---|---|---|
| `Compliance/OBLIGATIONS.json` (this one) | bonds · local permits · pawnbroker & business licenses · taxes · lease dates · entity/SCC · HR-compliance filings · records controls · unknown-annuals | `com.valleypawn.compliance-brief` (Mon 7:30 AM DM) |
| `Compliance/ffl_vendors.json` + `FFL_DEPT_OS.md` | the 5 FFLs, vendor copies, transfer relays, FFL directories | `com.valleypawn.ffl-guardian` (daily 7:15 AM) — its own 120/90/60/30/14-day ladder |
| `Life OS/Insurance/INSURANCE_REGISTRY.json` | every policy, renewal, COI, claim | the insurance department's own runner |

The brief **skips every `ffl-*` row** and does not warn on insurance renewals — it echoes one
headline line from `ffl_status.json` so Monday is still a single view. FFL rows stay in this
register only so the calendar is complete. **If you add an obligation, put it in exactly one
registry.**

## Obligation classes and where the truth comes from

| Class | Authority of record | How Claude verifies | Cadence |
|---|---|---|---|
| `ffl` (5 licenses, all Type 02) | ATF FFLC; eZ Check | `bin/`-driven eZ Check ×5 vs register (expiry, LOA, mailing address) | weekly (brief); renewal 3-yr |
| `state-firearms` (VSP NICS fees, premises records) | VSP eReceivables (login X009686) / Firearms Transaction Center | Portal balance read (Chrome) from the 5th; corrections by email | monthly |
| `local-permit` (precious-metals dealer permits ×5, pawnbroker licenses ×5, scale certs, LeadsOnline) | Each city/town PD + Commissioner of Revenue + VDACS | Evidence on disk; annual renewal steps in `ROANOKE_PRECIOUS_METALS_PERMIT.md` are the template for all five | annual |
| `bond` (Augusta $50K pawnbroker + 4 PM $10K) | SuretyBonds.com (Brooklyn Ventures), 800-308-4358 | Continuation certificate in `evidence/` | annual |
| `business-license` (BPOL ×5) | Locality Commissioner of Revenue | Receipt in `evidence/` | annual (Mar 1 typical; Culpeper May 1) |
| `tax` (sales tax ST-1, personal-property returns, FL RT, VA notices, entity returns) | Virginia Tax / localities / FL DOR / IRS | Filed-row check (`Sales Tax.xlsx`), notices in `evidence/` | monthly / annual |
| `lease` (5 stores) | Landlords per `STORE_LEASES.md` | Executed docs in `evidence/`; notice windows in register | per lease |
| `insurance` (WC, BOP/GL, umbrella gap) | JM Insurance Agency (305-445-5050) | Dec pages in `evidence/` | annual |
| `entity` (SCC, registered agent) | Virginia SCC; Northwest RA (task `northwest-registered-agent-daily-check`) | Receipt; daily task output | annual / daily |
| `hr` (941, VEC, VA-6/W-2, OSHA 300A, posters, I-9, wage step, handbook) | IRS/VEC/VA Tax/OSHA/DOL — Gusto files most | Gusto filing PDFs in `evidence/`; photo evidence for posters | quarterly / annual |
| `records-control` (gun audit, A&D 7-day, nightly police report, Form 8300, vendor FFL copies, directories) | ATF / Va. Code §54.1 / internal | `#monthly-gun-audit` output; Phase-3 discovery for A&D + police report | monthly / continuous |
| `unknown-annual` | Apple Reminders dates nobody labeled | Brief asks Joshua to identify each the first time it comes due | annual |

## Tasks and files that touch compliance (as of 2026-09-06)

| Owner task / file | What it does | Channel / output | Status |
|---|---|---|---|
| **`com.valleypawn.compliance-brief`** (NEW — native launchd, Mon 7:30 AM) | Re-renders the calendar, then DMs Joshua what is overdue / due in 30 days / needs his signature or payment. Script `Valley Pawn OS/bin/compliance_brief.py`, wrapper `compliance_brief_run.sh`. **Not a Cowork task** — zero fleet pressure. Sends nothing on a quiet week; full detail always written to `state/brief_YYYY-MM-DD.md` | Joshua DM only | **installed + loaded 2026-09-06** |
| `monthly-gun-audit-report` (16th 2:30 AM) | Reads 5 manager forms from `#monthly-gun-audit`, posts summary | `#monthly-gun-audit` (C07CPN020G0) | repaired 2026-09-06 — see below |
| `nics-weekly-mtd-ranking` / `nics-monthly-ranking` | Transfer VOLUME rankings (sales, not compliance) | `#ffl-transfer-performance` | healthy |
| `ffl-transfer-email-responder` (8:50 AM / 4:50 PM) | Answers customer transfer inquiries with the website link | email | healthy |
| `sales-tax-monthly-update` (1st 8 AM) | Fills `Sales Tax.xlsx` from the GL export | file | August row blocked 9/1 |
| `northwest-registered-agent-daily-check` (8 AM) | Registered-agent notices | DM | fragile (portal freezes) |
| `vp-gusto-signature-chase` (Mon 9:05) / `vp-hr-policy-monthly-sync` (1st) / `vp-hr-compliance-quarterly-review` (Q) | Policy signatures; policy sync; quarterly law review | `#policy-announcements` / DM | HR plan owns |
| `FFL-Transfer-page.html` | Reference copy of thevalleypawn.com/ffl-transfer/ (page 648) | web | current (9J) |
| `ffl-files/` | Signed 8/21/26 license masters (+ `-web` versions, `SUPERSEDED-*`) | — | current |
| ~~`vsp-nics-fee-monthly-check`~~ | Referenced by the runbook and BUSINESS_OS — **never existed in the registry or on disk** | — | phantom; replaced by the brief's VSP section |

## Hard facts every session needs

- Licensee on all five FFLs: `FULL CIRCLE FINANCE INC`, trade name `VALLEY PAWN`, EIN 47-1198118. **All Type 02.**
- **ATF mailing address of record for ALL FIVE licenses = 844 Cypress Crossing Trail, St. Augustine, FL 32095** (verified eZ Check 2026-09-06; Joshua moved it there deliberately 7/30/26). Renewal forms arrive in Florida ≈90 days before expiry. **Roanoke's form ≈2026-10-03.**
- FFLC duplicate-renewal line 304-616-4590 · FFLC@atf.gov / 866-662-2750 · renewal must be **postmarked before expiry**; 27 CFR 478.45 lets the store keep operating while a timely renewal is pending.
- VSP: portal login X009686 (password in Chrome — **rejected 2026-09-06, needs re-save**); Firearms Transaction Center 804-674-2292 / firearms@vsp.virginia.gov; billing 804-674-2151.
- Bonds broker: SuretyBonds.com, customercare@suretybonds.com, 800-308-4358.
- Roanoke PM permit: Teresa Huddleston (RPD) 540-853-5714; Sheriff fingerprints Mon–Thu 1–4 PM, $10 cash; VDACS scales 276-228-4127; LeadsOnline 800-311-2656.
- Lexington: Kelly Glass, kglass@lexingtonva.gov, 540-462-3701 (Karen Roundy retired 12/31/2025).
- Culpeper business license: Deputy Town Clerk 540-829-8240.
- Never use "Dixie Pawn" in any submission. Never publish a superseded FFL number (Culpeper `6J` is dead; `9J` is current).

## Apple Reminders → register

The 38-item "Annual Compliance and Tax Items" Reminders list was captured 2026-09-06
(`state/apple_reminders_compliance_capture_2026-09-06.md`). The register now carries its dates; Reminders
is no longer the calendar. Note the list had **Roanoke's 1/1/2027 FFL renewal checked off in error** —
that is exactly the failure a rendered calendar with evidence prevents.

## Phase status (from the plan)

- **Phase 0 (stop the bleeding)** — 2026-09-06: eZ Check ×5 ✅; Reminders captured ✅; VSP balance check ⛔ (password); outbound vendor/VSP/broker drafts staged (see Open Items Register); gun-audit task repaired.
- **Phase 1 (register + calendar + brief)** — 2026-09-06: register (69 rows), renderer, calendar, evidence vault built; brief task registered.
- **Phase 2 (verification wired in)** — eZ Check + VSP + gun-audit + expected_outputs entries + notice sweep inside the brief.
- **Phase 3 (records controls)** — police-report/A&D discovery, insurance location schedule, per-store pawnbroker licenses.
- **Phase 4 (visibility)** — dashboard panel + Month-in-Review line.

## How to extend this file
Add a row to the class table when a new obligation class appears; add a task row when a task starts
reading or writing compliance data; log every material change in `Valley Pawn OS/CHANGELOG.md` and
anything with a pending follow-up in `Life OS/OPEN_ITEMS_REGISTER.md` (Rule 14).
