---
name: insurance-coverage-audit
description: Quarterly check of coverage against reality — named insureds vs the entity table, occupancy vs policy form, Bravo inventory and loan balances vs scheduled limits, Gusto payroll vs workers comp, vehicles vs the auto policy, lease AI requirements vs endorsements, umbrella status.
model: claude-opus-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Quarterly insurance coverage audit for Joshua Davis. Runs 10:40 AM ET on the 1st of January, April, July and October.

STEP 1 — Load context. Invoke `enterprise-map`, then `insurance-context`. Connect ~/Documents/Claude/Projects (request_cowork_directory with that literal path; `mcp__Control_your_Mac__osascript` shell fallback if unattended). Read `Life OS/Insurance/INSURANCE_REGISTRY.json`, `Life OS/ENTITY_STRUCTURE.md`, `Valley Pawn OS/STORE_LEASES.md`.

STEP 2 — Run these seven checks. Each is coverage-versus-reality, not coverage-versus-last-quarter.

1. NAMED INSURED vs OWNERSHIP. For every property policy, does the named insured match the owning entity in ENTITY_STRUCTURE.md? Known live mismatches to re-check, not re-discover: Bald Rock names Joshua individually while Farming Infinity Mountains LLC owns it; 817 Richmond is insured on Full Circle Finance Inc's pawn policy while Farming Infinity, LLC owns it.

2. OCCUPANCY vs FORM. Does each property's policy form match how the property is actually used — STR, long-term rental, owner-occupied? A homeowners form on a short-term rental, or an STR form on a long-term rental, is a claim-denial risk. Bald Rock is the known open one.

3. PAWN LIMITS vs BRAVO. From the Bravo Data Extraction pipeline output folder (`Bravo Data Extraction/output/`), read the most recent `*_end-of-month.xlsx` per store for loan principal outstanding and inventory at cost, and the most recent `*_aged-inventory-summary.csv` for inventory at cost and at retail split jewelry vs merchandise. Compare against the scheduled pledged and unpledged limits per location in the registry. Report any store where the limit is below the exposure, and any category (Other Than Firearms & Jewelry) that is uncovered. Read files only — never open Bravo or Parallels.

4. WORKERS COMP vs PAYROLL. Pull current employee count and annualized payroll from the Gusto MCP. Compare to the class code and payroll basis on the workers comp record. A large gap means an audit bill is coming.

5. VEHICLES. Compare the vehicles on the personal auto policy in the registry against what Joshua actually owns (check recent registration, purchase, or lienholder mail in Gmail newer_than:120d). Flag any vehicle not on the policy, and any that should be rated business use.

6. LEASE REQUIREMENTS vs ENDORSEMENTS. For each of the five stores, does STORE_LEASES.md require an additional insured, a specific limit, or the landlord's agent named — and does the registry show that endorsement in place? Flag every gap by store.

7. UMBRELLA. Is a personal umbrella in force? A commercial umbrella? If either is still absent, say so plainly — it is the portfolio's largest single gap.

STEP 3 — Write the findings to `Life OS/Insurance/audits/COVERAGE_AUDIT_<YYYY-MM-DD>.md`: one section per check, each finding stated as exposure in plain English with the dollar figure and the source file. Update any registry field the audit corrected, then run `python3 "<Projects>/Life OS/Insurance/bin/regen_portfolio.py"`.

STEP 4 — Log a dated row in `Life OS/OPEN_ITEMS_REGISTER.md` and a one-line entry in `Valley Pawn OS/CHANGELOG.md`. Send ONE plain-language Slack DM to Joshua (D03BHQH5VGT) listing only findings that are NEW since the last audit file in that folder — no technical detail, no re-reporting of gaps he already knows about and has decided to live with (vp-operating-rules Rule 16). If nothing is new, send nothing.

Never change a policy, never contact a carrier, never send email.