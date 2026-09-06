# HR Department Review & Automation Plan
**Full Circle Finance Inc DBA Valley Pawn — prepared 2026-09-05 — PLAN ONLY, nothing built yet**

Scope reviewed: every file in `Projects/Human Resources/` (42 documents), all 29 people-related scheduled tasks and their SKILL.md files, the 9 HR skills, Gusto live state (19 active employees, pay schedules, PTO, unprocessed payrolls), the Bonus Program tracker, the Open Items Register, PUBLICATION_CALENDAR, and the last 60 days of CHANGELOG. Verified against output, not run records.

---

## 1. Where HR stands today (the honest one-paragraph diagnosis)

A lot has been built in eight weeks — handbook and P&P rewrite, pay transparency, e-signature chase, #ask-handbook, hiring outreach, offboarding skill, timekeeping and clock-in checks, a three-task bonus cycle. But it was built one fire at a time, so it is **29 tasks and 9 skills with no spine**: five separate hand-typed employee rosters that already disagree, two contradictory Gusto login models, two contradictory upload methods, two hiring intakes that don't talk to each other, an older dismissal task still live beside the newer offboarding skill, a bonus tracker that hasn't been written since July 21 while the tasks report success, and every HR task still carrying the Slack failure banner Rule 16 retired. The governing documents are on different version numbers, the P&P "FINAL" still says "pending review before adoption," the attorney packet was never sent, and the handbook has no signature block. Meanwhile the single most important dependency — the Gusto browser session — has been dead at an SMS-MFA prompt since 9/1, which silently blocks signature chasing, policy sends, onboarding and offboarding. The department works because people push it; it does not yet "just work."

---

## 2. Findings that need action regardless of automation (HR-counsel lens)

These are legal/compliance exposures found in the documents and in Gusto. None of them is fixed by a script. Items marked **[J]** are Joshua's decision; the rest I can prepare or execute.

| # | Finding | Exposure | Action |
|---|---|---|---|
| L1 | **Attorney Review Packet (13 items, July 2026) never transmitted.** Governance doc says neither the Handbook nor the P&P may be distributed before counsel sign-off — yet #ask-handbook is already serving both as authoritative. | Handbook adopted without counsel on FMLA/sick leave/cannabis/at-will language | **[J]** name the Virginia employment attorney (or approve me sourcing one); I package and send the same day |
| L2 | **Handbook acknowledgment page has no signature/date/name block**; handbook has no version or effective date in the body. | Can't prove receipt; weakens at-will and policy defenses | I fix in v2026.3 and re-issue via Gusto as one signed document |
| L3 | **Drug-Free Workplace / Cannabis Testing policy (starts 9/2) conflicts with the Handbook's cannabis clause** ("registered medical-cannabis patients will not be disciplined solely for lawful off-duty use"). Va. Code § 40.1-27.4 protects medical cannabis oil users; the federal-law carve-out (FFL / Form 4473, 18 U.S.C. § 922(g)(3)) is the argument for firearms-handling roles — but that carve-out must be written narrowly and reconciled in the Handbook. Policy is also not in Gusto and not in the P&P. | Wrongful-termination claim on a same-day termination | Counsel item #1 in L1; hold the "same-day termination" language for non-firearms roles until reviewed |
| L4 | **Minors on payroll.** Two Corporate Support employees have dates of birth of 2010 and 2017 (ages 15 and 9), title "Gold Sorter," FLSA status "Salaried Nonexempt," one at $12.00/hr. FLSA's parental exemption covers children employed by a business *solely owned by their parents*; the employer here is a corporation, and Virginia child-labor rules (employment certificate for 14–15; hours limits; under-14 restrictions) still need to be confirmed. The Aug 3 compliance memo stated there was no child-labor exposure because all roles are 21+ — that statement is wrong on the facts in Gusto. | Child-labor + minimum-wage findings in any DOL/VEC audit | **[J]** + counsel: confirm the intended treatment (family exemption, hours, rate ≥ VA minimum $12.77) or move these off W-2 payroll |
| L5 | **Two nonexempt Corporate Support/Marketing employees paid $50.00/week with 40.00 hours on the 9/3 payroll breakdown.** On its face that is below minimum wage for the hours recorded. | Back-wage liability, 2× liquidated damages | **[J]**: either the hours are wrong (fix the timesheet record) or the rate is wrong (fix comp). I'll prepare both corrections |
| L6 | **Owner and CSO still "Salaried Nonexempt"** (flagged in the Aug 3 memo as open; still open 9/5). Market Manager was paid $7,500 on a 1099 in Jul–Dec 2025 while also W-2. | Misclassification | **[J]** approve the exempt reclassification; I file the change in Gusto. 1099/W-2 overlap goes to the CPA |
| L7 | **Two tax notices open with no register row:** FL DOR RT-17B Final Assessment Q1-2026, $45.00, 20-day protest window closed ~8/12 (lien/collection-fee risk on a trivial amount); VA Dept. of Taxation missing 2023 W-2/1099 data for Form VA-6 (acct 30-471198118F-001). Florida reemployment-tax account exists at all — worth confirming it should. | Liens, penalties, employee refund delays | I prepare both filings; **[J]** pays the $45 (money) and confirms whether the FL account should be closed |
| L8 | **Workers' Comp premium audit response (7/17) incomplete** — 941s for Q2-25→Q1-26, jewelry-sales %, FT/PT split still "will follow." | Estimated premium + audit non-compliance surcharge | I assemble the package from Gusto/QBO and send |
| L9 | **Gusto has six abandoned off-cycle "Correction" payrolls** (one from March, five from 8/13) sitting unprocessed and flagged late. | Confusion at year-end; accidental submission | I delete the drafts (reversible only in the sense that they are unsubmitted; I'll list them first) |
| L10 | **P&P v2026.3 "FINAL" header says pending review; ~20 [NOTE] extraction gaps** (Melt Calc, Gold Scrap Process, Monthly Gun Audit, NCO checklist, ATF guide, Dress Code, etc.). | Employees are being answered from an unadopted manual | I close the gaps I can from Drive/Slack; the rest become a short punch-list for Preston |
| L11 | Disciplinary ROC (7/25 incident) cites a policy effective 8/3; unsigned "REVISED" settlement draft dated after an executed settlement; vehicle purchase agreement unsigned with blanks. | Record integrity | I annotate/close each in the register; **[J]** confirms how the $7,000 was actually paid |
| L12 | Entity name drift: WC letter signed "Full Circle Finance, LLC … 282 Bald Rock Road"; everything else "Full Circle Finance Inc, a Virginia corporation." Preston's title varies (Market Manager vs Operations Manager). | Insurer/agency records mismatch | I standardize; **[J]** picks the title once |
| L13 | PTO: one manager carries a **–40 hr balance** (advance) under a policy that says no payout/no rollover; new hires 8/31 and 9/3 have no evidence of Slack/Chekkit/Bravo provisioning or policy-pack signatures. | Small, but it's the pattern automation should catch | Covered by Phase 2 below |

---

## 3. Target state — the HR Operating System

One system of record, one roster, one policy register, one compliance calendar, five lifecycle lanes, every task reading from the same files. Additive throughout (Rule 4): new files and new tasks are built alongside; existing tasks are only re-pointed when next touched.

```
                     GUSTO (system of record: people, pay, time, PTO, e-sign)
                                        │  MCP (read) ─ Chrome only for e-sign sends
                                        ▼
   Valley Pawn OS/hr/
   ├── ROSTER.json            ← regenerated daily from Gusto + Slack/Chekkit/Bravo IDs (the ONE roster)
   ├── POLICY_REGISTER.md     ← every policy: version, effective, Gusto template id, sent/signed counts, adopted?
   ├── COMPLIANCE_CALENDAR.md ← every filing, audit, review, poster, wage step, with owner + due date
   ├── HR_OS.md               ← the HR map (replaces the stale Domain-2 table in BUSINESS_OS.md)
   └── state/                 ← per-task state files (last-run markers, dedupe keys)

   LANES        HIRE ──► ONBOARD ──► RUN (time · pay · policy · ask) ──► PERFORM ──► EXIT
   tasks        indeed-outreach   hr-new-hire-detector   hr-payroll-preflight   bonus ×3         offboard-employee
                hiring-inbox      onboard-employee       daily-clockin          rankings         (dismiss-employee retired)
                → one Pipeline    slack-chekkit          weekly-timekeeping     90-day/annual
                  sheet           policy pack + 90-day   signature-chase        reviews
                                                         ask-handbook
   GUARD        fleet-guardian expected_outputs for every HR publication + hr-weekly-health (one plain DM)
```

**Design rules the board locked in**
1. Gusto is the source of truth for *who works here, where, what they earn, what they've signed.* Nothing hand-types a roster again.
2. Reads go through the Gusto MCP (API). The browser is used only for the two things the API can't do: send an e-signature document and run the onboarding/dismissal wizards. One documented login model.
3. Every task writes a state marker and reads the register/calendar; "did we already do this" is a file lookup, not a Slack search.
4. Rule 16/18 everywhere: no failure or technical chatter in any channel; withhold rather than post partial data; one plain-language weekly HR health DM to Joshua.
5. Anything that touches money, people decisions, or legal posture is drafted for Joshua, never auto-sent.

---

## 4. Build plan (phased, additive, each phase proves itself before the next)

### Phase 0 — Unblock and stop the bleeding (this weekend, ~1 day of work)
- **Gusto device trust**: one click from Joshua ("Remember this device" in Chrome after the SMS code). Until then every Gusto-browser flow is dead. Then: rewrite `gusto-keep-alive` to the one login model and retire the passkey narrative in `gusto-access` (or vice-versa — whichever the live session proves).
- **Retire `dismiss-employee`** (disable in registry; `offboard-employee` is the single exit path; add a Preston-callable entry so store-level exits don't need Joshua).
- **Bonus cycle integrity before 9/10**: reconcile the master tracker (no July FINAL, no August tab despite two "successful" runs), unify the Net Revenue formula across targets/qualifiers/payout (they currently differ), fix the "live vs backup" file-ID contradiction, add `expected_outputs` entries so fleet-guardian sees a missed 10th.
- **Rule 16 sweep** of the 29 HR task files: remove the "did not complete" DM banners and the older "stay silent" banners, one backup per file.
- **Contradiction fixes** (30-minute edits): upload method (`file_upload` vs base64) — pick the proven one and delete the other instruction; Indeed account identity; onboarding defaults (department = store, real titles); evening Preston task gets the same data-access wall as the daytime one.
- **Register the two tax notices, WC audit, and attorney packet** as Open Items with due dates.

### Phase 1 — Foundation (week of 9/8, ~2 days)
- `hr-roster-daily-refresh` (native, stdlib, no Chrome): Gusto MCP → `ROSTER.json` with store, title, manager, hire date, FLSA, PTO balance, plus a crosswalk table for Slack user id, Chekkit, Bravo login, time-tracking member UUID. Old rosters in `daily-clockin-check`, `weekly-timekeeping-analysis`, `chekkit-unanswered-alert`, `daily-dress-code-check`, `valley-pawn-context` are re-pointed to it when each is next touched; new tasks read it from day one.
- `POLICY_REGISTER.md` seeded from the reconstructed register in this review (26 policies, template IDs, sent/signed status). `vp-gusto-signature-chase` writes signature counts into it weekly; `ask-handbook`'s `build_sources.py` reads *adopted* versions from it instead of globbing any `*_FINAL.docx`.
- `COMPLIANCE_CALENDAR.md` + `hr-compliance-calendar-weekly` (Mon, DM only): 941 quarterlies, VA-6/W-2 (Jan 31), VEC quarterly, FL RT (or closure), WC audit (June), OSHA 300A posting (Feb 1–Apr 30 if ≥11 employees — we're at 19), poster refresh, VA minimum-wage step to $15.00 on 1/1/2028 with wage-compression review in Q3 2027, paid-sick-leave restructuring Q1 2028, annual handbook review (July), I-9 reverifications, EEO/harassment training cadence, 90-day and anniversary reviews per employee (from ROSTER).
- `HR_OS.md` written and the Domain-2 table in `BUSINESS_OS.md` regenerated from the live registry by `refresh_live_state.py` (it currently lists tasks that don't exist, e.g. `weekly-payroll-to-qbo`, and misses 15 that do).

### Phase 2 — Lifecycle automation (weeks of 9/15–9/22, ~3 days)
- **Hire**: one pipeline. Both `hiring-inbox-watch` and `indeed-applicant-outreach` append to the existing "Valley Pawn — Hiring Pipeline" sheet; outreach state moves out of the 625 KB markdown into a JSON state file; Preston's "already handled" list is read from the sheet (his interview notes in #preston-claude get mirrored there), not appended by hand. One notification target (#employee-prospects digest + Preston DM), one contact log. Straggler list (20 candidates) worked once, then never again.
- **Onboard**: `hr-new-hire-detector` (daily, MCP): any Gusto employee with hire_date ≥ last marker → Slack/Chekkit provisioning via the existing skill, Bravo user creation request to Preston with a checklist, policy signature pack sent (Handbook + P&P + standalone policies from the register, "future hires" flag verified), 90-day review reminder written to the calendar, welcome DM in Joshua's voice. Same detector flags a hire that has no Slack/Chekkit after 3 days.
- **Run**: `hr-payroll-preflight` (Wed 4 PM + Thu 9 AM, MCP only): next unprocessed regular payroll, blockers, employees with zero hours, missed clock-outs, OT > 40, PTO requests overlapping the period but not approved, abandoned off-cycle drafts, check-pickup totals (the ad-hoc CSV from 9/4 becomes a standing output with the manager DM schedule built in). Friday 11 AM `hr-payroll-confirm`: payroll processed = yes/no, one line to Joshua. Payroll → QBO journal stays a Finance-domain build, gated by `books-tax-strategy`.
- **Perform**: `hr-review-reminders` (from calendar): 90-day and annual reviews DM'd to Preston with the employee's rankings/timekeeping summary attached; comp-review flag at anniversary. Weekly/monthly rankings agree on one inclusion rule (FREE1 in or out — board recommends **out** everywhere; Joshua can overrule).
- **Exit**: `offboard-employee` gains a Preston-callable path, VA final-pay checklist writes to the calendar, Bravo disable becomes a Preston checklist item when a computer-use grant isn't available.

### Phase 3 — Governance closes the loop (by 10/1)
- Handbook v2026.3: signature block, version/effective date, cannabis reconciliation (post-counsel), Drug-Free policy folded in. P&P v2026.4: [NOTE] gaps closed, header no longer "pending." Both adopted via one Gusto send, register updated, `_upload_tmp`/superseded drafts archived.
- `vp-hr-compliance-quarterly-review` (first fire 10/2) re-pointed to DM Joshua + Drive rather than #policy-announcements (channel rule), and fed by the calendar + `QUESTION_LOG` NOT-FOUND rows.
- `policy-lifecycle` DELTA applied (send-before-announce, send gate, duplicate guard); in-place Google Doc update replaces the create-a-new-doc-every-time behavior.
- `annual-board-review` corrected (store list, skill path) and dry-run in November.

### Phase 4 — Visibility (October)
- HR section on the Business Dashboard: headcount by store, open reqs, days-to-fill, OT hours, signature completion %, upcoming compliance deadlines, bonus status. Data straight from `ROSTER.json`, register, calendar — no new pulls.
- `hr-weekly-health` (Mon 8 AM, DM only): one plain paragraph — what ran, what's due, what needs Joshua.

---

## 5. Expert board record

🧑‍⚖️ **EXPERT BOARD — How to make HR run itself without breaking what already works**
PANEL: HR-systems architect (Gusto/API-first), employment-law compliance officer, SRE/automation reliability lead, people-ops manager who has to live with it.

OPTIONS WEIGHED
- *Keep patching tasks one at a time*: for — zero disruption; against — the roster/formula/login contradictions already produce wrong output (bonus tracker, rankings), and each patch adds another hand-typed copy.
- *Rebuild HR on a new HRIS/ATS (Rippling, BambooHR, Workable)*: for — turnkey lifecycle; against — 19 employees, Gusto already holds pay/time/PTO/e-sign, and the real gap is glue and governance, not features. Cost with no reliability gain.
- *Gusto-as-SSOT + file spine + additive tasks (chosen)*: for — every fragility found traces to "no single source"; fixing the source fixes the class; API reads remove the browser from 90% of runs; against — two to three weeks of build and a discipline that every task reads the spine.

DECISION — Gusto stays the system of record; build the four spine files and re-point tasks to them additively; browser only for e-sign and wizards; one weekly plain DM instead of per-task chatter.

REJECTED — new HRIS (unjustified at this size); editing hardened tasks in place (Rule 4 — clone/re-point when touched); a Slack-based roster (Slack is not the source of who is employed); auto-sending anything that touches pay, discipline, or legal posture.

FOR JOSHUA — proceeding additively on Phases 0–4 once you say go. The items in §6 are yours.

---

## 6. Decisions only Joshua can make (everything else I do without him)

1. **Go / no-go on the plan** and the Phase 0 start.
2. **Gusto device trust** — one "Remember this device" click in Chrome (30 seconds; unblocks everything).
3. **Attorney** — who reviews the 13-item packet + cannabis reconciliation + minors/family-payroll question (L1, L3, L4). If none, approve me shortlisting three Virginia employment firms.
4. **Family payroll** — intended treatment for the two minors and the two $50/week nonexempt roles (L4, L5). This is the highest-exposure item in the review.
5. **Exempt reclassification** of the two Salaried-Nonexempt executive roles (L6).
6. **$45 FL DOR payment** and whether the Florida reemployment account should be closed (money).
7. **Preston's official title** (Market Manager vs Operations Manager) and confirmation of how the $7,000 settlement was paid (L11, L12).
8. **FREE1 shared login** — excluded from all employee rankings (board recommends yes).
9. **September bonus targets** — still waiting on your "send it" since 9/2 (existing open item).

---

## 7. What "done" looks like (measurable)
- Zero hand-typed rosters in any HR task; `ROSTER.json` is the only one.
- Every policy in the register shows sent/signed counts equal to the active roster, or names who owes.
- Every HR publication has a fleet-guardian expected output; a missed 10th-of-month bonus post is caught by the 11th.
- Payroll preflight catches OT, zero-hour, missed clock-out, and blockers before Thursday 5 PM every week.
- New hire → Slack, Chekkit, Bravo, policy pack, 90-day reminder within 24 hours of appearing in Gusto, without anyone asking.
- Compliance calendar has no past-due row.
- Joshua receives one HR message a week plus only the decisions in §6.

*Sources: Human Resources folder (all files), Scheduled task registry + SKILL.md files, HR skills, Gusto MCP live pull 2026-09-05, Bonus Program tracker, Life OS/OPEN_ITEMS_REGISTER.md, Valley Pawn OS/CHANGELOG.md, PUBLICATION_CALENDAR.md.*
