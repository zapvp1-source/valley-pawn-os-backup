# Compliance Department — Review & Automation Plan
**Full Circle Finance Inc DBA Valley Pawn · 2026-09-05 · status: PLAN, awaiting go**

Scope reviewed: every file in `Projects/Compliance/`, every compliance-touching file in the Projects tree (Valley Pawn OS, Life OS, Human Resources, Sales Tax, Precious Metals, Taxes 2026, Admin Assistant), all compliance-related scheduled tasks (registry + on-disk + launchd), and the channels they post to. Verified against output, not run records (Rule 12). Companion: `Human Resources/HR_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md` — this plan absorbs its `COMPLIANCE_CALENDAR.md` so there is ONE calendar, not two.

---

## 1. What exists today (the honest picture)

There is no compliance department — there is an FFL folder. `Compliance/` holds 2 markdown files (FFL registry, FFL listings), 1 runbook (VSP fees), 1 reference HTML, an ATF address-change mailing package, and 19 license scans. Every other obligation lives somewhere else or nowhere:

| Area | Where it lives | Tracked? | Monitored? |
|---|---|---|---|
| FFL licenses (5) | `Compliance/FFL_REGISTRY.md` | Yes, by hand | **No** — Culpeper near-miss was caught by a human noticing missing mail |
| FFL directory/vendor listings | `Compliance/FFL_LISTINGS_STATUS.md` | Yes, by hand | No |
| VSP NICS fees (5 accounts) | `Compliance/VSP-NICS-Fee-Payment-Runbook.md` | Runbook only | **No — `vsp-nics-fee-monthly-check` is referenced by the runbook and BUSINESS_OS but does not exist** (not in registry, not on disk) |
| Monthly gun audit (4473 error rates) | task `monthly-gun-audit-report` → #monthly-gun-audit | Yes | **Broken** — 8/16 run posted nothing (verified in channel: last summary 8/3). Three different deadlines in three files (5th / 15th / "runs the 7th"). Posts a Drive link into an employee channel (violates Rule 13) |
| Surety bonds / precious-metals permits | `Valley Pawn OS/SURETY_BONDS.md`, `ROANOKE_PRECIOUS_METALS_PERMIT.md` | Yes, by hand | No. **Roanoke unbonded ~22 months; Lexington no bond found; Augusta $50K pawnbroker bond expires 12/1/2026** |
| Business licenses (BPOL) | One Open Items row | No | No. **Culpeper 2026 license ($955.86 + late fee) appears unpaid since 5/1** |
| Sales tax (ST-1 monthly) | `Sales Tax/STATUS.md` + task | Yes | Partial — August row BLOCKED, July was backfilled by hand |
| Store leases | `Valley Pawn OS/STORE_LEASES.md` | Yes, by hand | No. Roanoke 60-day notice window already passed; Harrisonburg percentage-rent reports 19 months behind; WAY/LEX rows empty |
| HR / employment law | HR plan (today) — 13 open legal findings | Yes (as of today) | Quarterly task only |
| Insurance | `Life OS/Insurance/INSURANCE_PORTFOLIO.md` | Yes, by hand | No. No broker, no umbrella, **no store location appears on any policy** |
| Entity / SCC / registered agent | task `northwest-registered-agent-daily-check` | Task only | Fragile (portal freezes, SMS 2FA) |
| Payroll tax notices (FL RT, VA-6) | `Human Resources/Tax Notices/` | No register rows | No. FL reemployment filings missing since Jan; protest window on the FL assessment already closed |
| A&D book / 4473 retention / 3310.4 / Form 8300 | Policy text only | **No** | **No** |
| Nightly police reporting (Bravo → PD) | Policy text only | **No** | **No** verification that it runs at any store |
| LeadsOnline, DCJS, second-hand dealer, pawnbroker licenses per store | — | **Nothing** | **Nothing** |
| Labor posters, I-9, OSHA 300A, W-2/1099 calendar | — | **Nothing** (planned in HR plan) | **Nothing** |
| Compliance calendar | An Apple Reminders list ("Annual Compliance and Tax Items", 38 items) never captured into any file | — | — |

**Pattern:** four good trackers exist (FFL, bonds, leases, insurance) — each built reactively after a near-miss, each hand-maintained, none machine-readable, none monitored, none referenced from BUSINESS_OS. "Did we already do this" still requires a Slack/Drive search. Every failure in this department traces to the same root: **no single register of obligations with dates, and nothing that reads it.**

---

## 2. Findings that need action now (not automation — action)

Ordered by legal exposure. Items marked **J** need Joshua (money, signature, or an in-person step); everything else Claude does.

| # | Finding | Exposure | Owner |
|---|---|---|---|
| F1 | **Roanoke precious-metals dealer bond lapsed 10/26/2024**; permit prerequisites (fingerprints, background checks, scale cert, $200/person fee, LeadsOnline) not done | Va. Code §54.1-4108 — Class 2 misdemeanor | Bond applied 8/25 — Claude chases delivery + files it; fingerprints/fee **J** (Preston + Benjie in person) |
| F2 | **Lexington precious-metals bond/permit** — broker says none exists; license was tied to the old 439 E Nelson address | Same statute | Claude: confirm with Kelly Glass (Lexington) + SuretyBonds.com, draft the application |
| F3 | **Culpeper business license unpaid since 5/1/2026** (~$1,051 with late fee); Roanoke Nov-2025 CommRev summons unconfirmed | Late fees, summons | Claude confirms balances by phone/email; payment **J** |
| F4 | **Augusta County $50K pawnbroker bond expires 12/1/2026** | Waynesboro can't operate as pawnbroker without it | Claude: get renewal invoice from SuretyBonds.com by 11/1; payment **J** |
| F5 | **Roanoke FFL renewal form mails ≈10/3/2026 to 844 Cypress Crossing** — Joshua's own July letters moved the mailing address to Florida deliberately; eZ Check confirms it took for CUL + WAY, unknown for HAR/LEX/ROA | If Roanoke's form goes to a store instead, repeat of the July scramble | Claude: eZ Check all five this week; if Roanoke still shows a VA mailing address, send the Roanoke letter (already drafted) now. Watch = weekly brief, not the store mail |
| F6 | **VSP premises records wrong** — Culpeper billed to "Joshua Christian Davis", Lexington at old address — flagged 6/23, never fixed | Personal-name record on a federally licensed premise | Claude drafts the correction to firearms@vsp.virginia.gov for Joshua's send |
| F7 | **FL reemployment tax filings missing since Jan 2026**; FL RT-17B assessment unprotested; VA-6 TY2023 W-2/1099 notice open | Penalties accruing monthly | Claude drafts the Gusto account-ID fix + VA response; **J** signs |
| F8 | **Harrisonburg percentage-rent reports (19 months) built, not sent**; renewal proposal expired unanswered 8/31; **Roanoke lease auto-rolls month-to-month 11/1** with the notice window passed | Landlord default claims; renewal leverage | Both decisions **J**; Claude sends once told |
| F9 | Stale FFL data still in circulation: GrabAGun/vendors hold pre-renewal Culpeper copy; 2026-05-04 dealer applications had 2 wrong FFL numbers + wrong license type; Drive "READ ME" doc says Culpeper expires 2026-09-01; MidwayUSA's 8/1 request unanswered; MasterFFL profiles unclaimed; "Dixie Pawn" on GunBroker/FFLeasy/Yext | Lost transfer revenue; vendors reading a wrong number as fraud | Claude, all of it (Chrome + email) |
| F10 | **Monthly gun audit not publishing** (8/16 silent); no chase of uncorrected 4473 errors (Culpeper 0/4, Roanoke 0/2 last period) | ATF inspection finding | Claude fixes the task (see §4) |
| F11 | Insurance: no store locations on any policy, no umbrella, no broker; WC premium audit response incomplete | Uninsured loss at 5 stores (a $7K claim was just paid — confirm which policy paid it) | Claude assembles the location/coverage question for JM Insurance; **J** decides broker/umbrella |
| F12 | HR legal L1–L13 (minors on payroll, sub-minimum pay lines, cannabis policy conflict, unsent attorney packet, etc.) | Covered by the HR plan | HR plan Phase 0 |

---

## 3. Target state — the Compliance OS

One register, one calendar, one evidence vault, one weekly brief. Additive throughout (Rule 4).

```
Projects/Compliance/
├── COMPLIANCE_OS.md              the map: every obligation class, owner, source file, task, channel
├── OBLIGATIONS.json              THE register — one row per license/permit/bond/filing/report/lease date/
│                                 policy review/insurance renewal, for all 5 stores + entity + HR rows:
│                                 id, class, store, entity, authority, number, issued, expires, lead_days,
│                                 renewal_steps, evidence_path, status, owner (claude|joshua|preston), last_verified
├── COMPLIANCE_CALENDAR.md        RENDERED from OBLIGATIONS.json — never hand-edited (same pattern as LIVE STATE)
├── evidence/<obligation-id>/     the actual license/bond/permit/filing/receipt — one folder per obligation
├── FFL_REGISTRY.md, FFL_LISTINGS_STATUS.md, VSP-NICS-Fee-Payment-Runbook.md   (kept; become the
│                                 narrative layer; their dates/numbers move INTO OBLIGATIONS.json)
├── state/                        per-check markers (last eZ Check, last VSP check, last gun-audit post…)
└── bin/
    ├── render_calendar.py        OBLIGATIONS.json → COMPLIANCE_CALENDAR.md + horizon list (120/60/30/7 days)
    ├── ffl_ezcheck.py            eZ Check ×5 → diff vs register (number, expiry, LOA, mailing address)
    ├── gun_audit_format.py       deterministic #monthly-gun-audit message (exit 2 = withhold, Rule 18)
    └── compliance_brief.py       assembles the Monday DM from calendar + state + output checks
```

**Design rules (board-locked)**
1. `OBLIGATIONS.json` is the only place a date or license number lives. Markdown is rendered from it. `SURETY_BONDS.md`, `STORE_LEASES.md`, `INSURANCE_PORTFOLIO.md` keep their narrative but their date rows are imported into the register so one horizon check covers all of them.
2. The HR plan's `COMPLIANCE_CALENDAR.md` is **this** calendar — HR rows (941, VA-6, VEC, OSHA 300A, posters, I-9, wage step, reviews) are `class: hr` rows in the same file. No second calendar.
3. **One new scheduled task, total** (`compliance-weekly-brief`). The fleet is at 148 enabled tasks with ~7,900 skips/week; every other check runs inside that task or as stdlib Python it calls. Prior decision in `FFL_LISTINGS_STATUS.md` not to add per-topic tasks stands.
4. Rule 16/18: the brief goes to Joshua's DM only, plain language, and withholds any section whose data didn't verify. Nothing compliance-related ever posts a failure or a Drive link to an employee channel (Rule 13).
5. Anything that is money, a signature, a government filing, or a people decision is **drafted and staged for Joshua** — never auto-sent, never auto-paid. Everything else (vendor emails, directory claims, evidence filing, chasing store managers) Claude does.
6. Evidence-or-it-didn't-happen: a row can only be marked `current` when a file exists in `evidence/<id>/`. The brief flags rows with a status but no evidence.

**What the Monday brief contains (one DM, ~15 lines)**
- Due inside 120/60/30/7 days, with the exact next step and who owns it
- Past-due rows (should be zero — this is the KPI)
- Verification results: eZ Check ×5 matched the register; gun audit posted for the period; VSP balances checked (month ≥ 5th) and what's owed; sales-tax row filled for last month; registered-agent check ran; police-report evidence present (once Phase 3 lands)
- New notices found (ATF/VSP/locality/landlord mail, from `unified-search` across Mail + iMessage)
- Items staged for Joshua's signature/payment, with the file path

---

## 4. Build plan (phased, each phase proves itself)

### Phase 0 — Stop the bleeding (this week)
Actions F1–F11 above. Concretely, Claude:
- runs eZ Check on all five, records mailing address + LOA per store, sends the Roanoke address letter if needed
- emails the signed Culpeper (9J) license to GrabAGun and every vendor of record; resends corrected dealer applications; answers MidwayUSA; updates the Drive "READ ME" doc
- chases SuretyBonds.com for the Roanoke bond document and the Augusta renewal; contacts Lexington (Kelly Glass) on the permit; schedules Roanoke scale certification
- confirms the Culpeper license balance with the Town Clerk and stages payment details for Joshua
- drafts the VSP premises-record correction, the FL DOR/Gusto fix, and the VA-6 response for Joshua's send
- writes every one of these into the Open Items Register with a due date (Rule 14)

### Phase 1 — Register + calendar (week of 9/8)
- Seed `OBLIGATIONS.json` from FFL_REGISTRY, SURETY_BONDS, ROANOKE permit checklist, VSP runbook, STORE_LEASES, INSURANCE_PORTFOLIO, Sales Tax STATUS, the HR plan's calendar list, the entity/tax rows (SCC annual report, 941s, VA-6/W-2, VEC, FL RT, J Davis Group final return), and the 38-item Apple Reminders list (Claude pulls it via the Reminders MCP/osascript — it has never been captured)
- Per-store pawnbroker license / second-hand dealer / precious-metals permit rows for ALL five localities — status `unknown` until evidence is found (this is the biggest blind spot; Claude runs the discovery against each locality's site + Mail search)
- `render_calendar.py` + `COMPLIANCE_CALENDAR.md`; `COMPLIANCE_OS.md`; `evidence/` populated from `ffl-files/`, `Surety Bonds/`, `Store Leases/`, Drive
- Register `compliance-weekly-brief` (Mon 7:30 AM, Sonnet, DM only) — v1 is calendar + past-due + staged-items only

### Phase 2 — Verification wired in (week of 9/15)
- `ffl_ezcheck.py` (headless HTTP if the DOJ banner allows, else Chrome) → brief section + `state/`
- VSP monthly balance check rebuilt inside the brief (Chrome, read-only; runs when day ≥ 5 and month unmarked) — replaces the phantom `vsp-nics-fee-monthly-check`; staged payment list for Joshua
- `monthly-gun-audit-report` repaired: deterministic formatter, 15th deadline / 16th run only, Drive link removed from the channel, uncorrected-error chase DM to the store manager on the 20th, `expected_outputs` entry so fleet-guardian sees a miss
- `expected_outputs.json` entries for `northwest-registered-agent-daily-check`, `sales-tax-monthly-update`, `vp-hr-policy-monthly-sync`, `vp-gusto-signature-chase` (none is guarded today)
- Notice detection: brief runs `unified-search` for ATF / VSP / "business license" / "Commissioner of Revenue" / landlord senders in the last 7 days and lists anything without a register row

### Phase 3 — The records controls nobody checks (by 10/15)
- **Police reporting**: discover whether Bravo's nightly "Police Report" leaves an artifact the pipeline can read (report log, LeadsOnline upload, PD confirmation email). If yes, add an additive pipeline cell + brief line per store; if no, a Monday self-attest in the manager EOD sheet — decided by discovery, not assumption
- **A&D / 4473**: monthly gun-audit form gains fields for A&D entries >7 days and 3310.4 same-day compliance; brief trends error rate per store; ATF inspection-readiness checklist (`COMPLIANCE_OS.md` section) built from the 4473 error notes managers already write
- **Insurance**: location schedule + coverage per store confirmed with JM; COI tracking rows for landlords
- **Roanoke permit annual cycle** and Lexington permit rows fully populated with evidence

### Phase 4 — Visibility (October)
- Compliance panel on the Business Dashboard site: days-to-expiry per license/bond/permit, past-due count, gun-audit error trend, signature completion — read straight from `OBLIGATIONS.json`, no new pulls
- Monthly compliance line in the Month-in-Review / minutes (via `monthly-eom-recap` once registered)

---

## 5. Expert board — options considered

- *Buy a compliance platform (e.g., FFL-specific SaaS like FastBound/Orchid, or a generic GRC tool):* for — purpose-built A&D and 4473 tooling; against — Bravo already is the bound book and records system, the gap is obligations tracking not transaction recording, and a second system of record for firearms is a new inspection risk. **Revisit only if the Phase 3 discovery shows Bravo's police/A&D artifacts can't be verified.**
- *One scheduled task per obligation class (FFL monitor, VSP monitor, bond monitor…):* for — simple; against — fleet is capped and skipping thousands of runs; five tasks that each fire monthly and read the same file is waste. Rejected.
- *Extend `directory-listing-monitor` with an FFL block (prior recommendation):* for — zero new tasks; against — that task is website/NAP-owned, hardened, and Rule 4 says don't edit it; and its channel is not Joshua's DM. Superseded by the single brief.
- *Register + rendered calendar + one weekly brief + stdlib checkers (chosen):* every failure found is a "nobody was looking at a date" failure; a register with a horizon check fixes the class, not the instance. One task, Sonnet, ~5 min/week of fleet budget.

**DECISION:** build the Compliance OS as in §3; Phase 0 actions start immediately on go.

---

## 6. What only Joshua can do (the short list)
1. **Go / no-go** on this plan.
2. **Pay**: Culpeper business license (~$1,051), Roanoke permit fees ($200/person), Augusta bond renewal (when invoiced), any VSP balance the check surfaces.
3. **Sign/send**: VSP premises correction, FL DOR/Gusto account fix, VA-6 response, Harrisonburg percentage-rent package, Culpeper First Amendment.
4. **Decide**: Roanoke lease (month-to-month or renew), Harrisonburg renewal ($20/SF proposal expired), whether to appoint a broker / buy an umbrella, headcount for Roanoke permits (who handles precious metals there).
5. **In person**: Preston + Benjie fingerprints at Roanoke Sheriff (Mon–Thu 1–4 PM, $10 cash).

Everything else in this document Claude does without checking in.

---

## 7. Success criteria (90 days)
- `COMPLIANCE_CALENDAR.md` has zero past-due rows and every `current` row has evidence on disk
- Roanoke FFL renewal submitted ≥30 days before 1/1/2027 with the receipt filed
- Roanoke + Lexington precious-metals permits in hand; Augusta bond renewed before 12/1
- Gun audit publishes on the 16th every month; uncorrected errors chased by the 20th
- VSP balances checked by the 7th every month; all five premises records correct
- No compliance fact exists only in an email, a Slack post, or Joshua's head

*Sources: `Compliance/*`, `Valley Pawn OS/{BUSINESS_OS,CHANGELOG,PUBLICATION_CALENDAR,STORE_LEASES,SURETY_BONDS,ROANOKE_PRECIOUS_METALS_PERMIT,SECURITY_HARDENING_PLAN}.md`, `Life OS/{OPEN_ITEMS_REGISTER,LIFE_MAP}.md`, `Life OS/Insurance/INSURANCE_PORTFOLIO.md`, `Human Resources/HR_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md`, `Human Resources/Ask_Handbook/SOURCES_CURRENT.md`, `Sales Tax/STATUS.md`, `Taxes 2026/TY2025 Tax Prep/`, `Admin Assitant/Reminders_Backup_2026-07-14.md`, scheduled-task registry (238 on disk / 148 enabled), `launchctl list`, Slack #monthly-gun-audit (read 2026-09-05).*
