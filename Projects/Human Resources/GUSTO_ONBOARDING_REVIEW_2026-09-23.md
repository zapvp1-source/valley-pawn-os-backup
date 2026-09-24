# Gusto Onboarding Review & New-Hire Frontload Packet
**Full Circle Finance Inc DBA Valley Pawn — 2026-09-23**
Prepared on Joshua's instruction: *"customize the Gusto onboarding so they have to sign off on the current handbook and policy and procedure … review the onboarding process as a whole and see what else we can frontload."*

Companion to `HR_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md` (this executes finding **L2** and part of that plan's **Phase 2 — Onboard** and **Phase 3 — Governance**).

> **STATUS 2026-09-23 (PM) — SEND IS ON HOLD.** Joshua: *"before we do all this I want to make sure the handbook and P&P are accurate so we are doing a review in another session."* HR-2026-04 names the Handbook and P&P by **exact version and effective date**, which is what gives it evidentiary force — so it must not be sent until that review settles what the current versions are. If the review produces Handbook v2026.3 and/or P&P v2026.4, §1 of HR-2026-04 gets the new version/date and it is re-rendered before sending. Nothing else in the document changes.
>
> **ALSO ADDED 2026-09-23 (PM) — mandatory firearm safety certification within 3 days of starting, or employment ends.** Built as **HR-2026-05** (see §4e below). This one is self-contained — it does not cite the Handbook or P&P by version — so it **can be sent independently of the review**, on Joshua's word.

---

## 1. What was wrong

The Employee Handbook's own "Acknowledgment" section ends with three paragraphs of agreement language and then simply **stops** — no signature line, no printed-name line, no date, no store. There is no version number or effective date anywhere in the body. The Policies & Procedures Manual has no acknowledgment page at all.

Net effect: **Valley Pawn has never been able to prove that any employee received, read, or agreed to either governing document.** That is the single weakest link in every at-will defense, every policy-based termination, and every wage-hour or harassment claim the company could face. It is also the reason `#ask-handbook` has been answering employees from documents nobody has signed.

Seven of the nineteen active employees were hired in 2026, three of them in the last five weeks (Jacob Cox 9/17, Camden Ahern 9/21, Joshua Stagner starting 9/24). Every one of them onboarded without a policy signature.

## 2. What was built today

**`Valley Pawn — Employee Handbook and Policies & Procedures Acknowledgment` (Policy No. HR-2026-04, effective 2026-09-23)** — a standalone, two-page, e-signable document covering both governing manuals at once.

Why standalone rather than a signature page bolted onto the back of the Handbook:

- One signature covers **both** manuals plus every standalone policy issued under them.
- When either manual revs, we re-issue a one-page acknowledgment instead of re-sending a 60-page handbook for signature.
- Gusto's field editor places signature fields reliably on a short document; on page ~45 of a 1.3 MB file it is fragile.
- It is the document that has to survive a subpoena, and it reads as one.

**What it binds the employee to, section by section:**

| § | Covers | Why it matters legally |
|---|---|---|
| 1 | Named receipt of Handbook **v2026.2 (eff. 8/3/2026)** and P&P **v2026.3 (eff. 8/21/2026)**, by exact version and date | Proves *which* document was received — a generic "I got a handbook" is worth little |
| 2 | Read and understood; asked questions before signing; duty to read revisions | Defeats the "I never read it / nobody explained it" defense |
| 3 | Agrees to abide; compliance is a condition of employment | Makes every policy enforceable as a term of employment |
| 4 | Virginia at-will; not a contract; only the CEO in writing can change at-will | The core at-will disclaimer, restated *in the signed document* rather than only in the unsigned manual |
| 5 | Company's unilateral right to amend; continued employment = acceptance | Lets policies change without renegotiating with 19 people |
| 6 | Duty to report violations — expressly naming firearms/ATF recordkeeping, cash reporting, and customer privacy; no retaliation; **NLRA/whistleblower savings clause** | Pawn + FFL exposure; the savings clause keeps the document from being an unlawful overbroad rule |
| 7 | E-SIGN Act and Va. Code § 59.1-479 (UETA); record kept in Gusto; employee **may view and download but cannot alter or delete**; paper copy on request | Makes the electronic signature enforceable and states the non-deletion rule on the face of the document |

Files: `Human Resources/Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04.docx` / `.pdf`.

## 3. How it is wired into Gusto

Gusto e-signature documents are sent as a **Team document** with two audience toggles. The second one is what makes this permanent:

1. **Future hires → "All future hires"** — every person added to Gusto from that moment forward automatically receives the document as part of their onboarding checklist. No one has to remember.
2. **Current team members → "All N individuals"** — backfills the existing 19.

Storage and deletion, verified against how Gusto handles company-issued documents:

- The signed PDF lands in the employee's **Documents** tab in Gusto, in the employee's own view and in the admin view.
- Employees can **view and download** it. They have **no delete control** over company-issued or signed documents — the delete/archive action exists only for the admin, and archiving preserves already-signed copies. Employees can only remove documents they uploaded themselves.
- This is stated on the face of HR-2026-04 (§7) as well, so the employee is on notice.

**Verification standard (Rule 12):** a send is not "done" when the Send button is clicked. It is done when **Documents → Team artifacts** shows exactly one "Needs signing" row per person, and signed rows appear as people complete it.

## 4. The rest of the onboarding review — what else to frontload

Reviewed: Gusto's native onboarding flow, the 19 active employee records, the P&P index (11 sections, 78 subsections), the Handbook, and the standalone policy inventory.

### 4a. Gaps in what Gusto is already collecting — fix these first, they cost nothing

| # | Finding | Action |
|---|---|---|
| **G1** | **Five active employees show no I-9 document on file** (Preston Peters, Madison Davis, Savannah Davis, Kennedy Davis, Audrey Davis). Form I-9 is required for **every** employee within 3 business days of hire, family included. | Complete/reverify I-9 Section 1 + 2 for all five. This is a per-violation civil-penalty item in any ICE audit and is the highest-dollar gap in this review. |
| **G2** | No offer-letter template in use, so the Va. Code § 40.1-28.7:12 pay range is not documented at hire even though the Pay Transparency Policy requires it in postings. | Build a Gusto offer-letter template carrying the approved range and the at-will sentence. |
| **G3** | Onboarding has no checklist for the things that actually happen on day one — Slack, Chekkit, Bravo user, store keys/alarm code, uniform order, firearm-safety walkthrough. Today these live in a skill and in Preston's head. | Add them as Gusto onboarding checklist tasks so they are visible and auditable in the same place as the paperwork. |
| **G4** | No 90-day review date is set at hire. | Write it to the HR compliance calendar at onboarding (Phase 2 of the HR plan). |
| **G5** | Emergency contact is not enforced as required. | Turn on as a required self-onboarding step. |

### 4b. Policies that already exist and are adopted — just need the "All future hires" flag confirmed ON

These were sent to the current team but a future-hires flag was never systematically verified. Each one that is off means every new hire silently misses it.

- Pay Transparency & Salary History Policy (HR-2026-03)
- Drug-Free Workplace / Cannabis Testing Policy (eff. 9/2/2026) — **not confirmed in Gusto at all**
- Store Email Password Policy (P&P 03.17)
- Daily Jewelry Count (P&P 02.14)
- Jewelry Display One-In-One-Out (P&P 05.11)
- Gold Scrap Bucket Naming Standard
- Jewelry Category Standard
- eBay Listing-Age Standard (amended version still unsent per the 9/17 open item)

### 4c. New signature documents worth building — ranked by exposure

**Tier 1 — restate policy Valley Pawn already has, so no new legal decision is needed. Recommend building these next.**

| ID | Document | Why |
|---|---|---|
| A3 | **Confidentiality & Customer Information Agreement** | A pawnbroker is a "financial institution" under the GLBA Safeguards Rule. Employees handle customer SSNs, IDs, and loan records daily. P&P 03.09 covers it as policy; nobody has signed a duty of confidentiality. Survives termination. |
| A4 | **Timekeeping & Pay Accuracy Acknowledgment** (nonexempt) | Employee certifies time records are accurate, no off-the-clock work, must report any missed punch or unpaid time. This is the single cheapest defense against an FLSA back-wage claim — and the 9/5 review already flagged two $50/week nonexempt records and a −40 hr PTO balance. |
| A5 | **Firearms Compliance Acknowledgment** | FFL exposure: Form 4473 accuracy, straw-purchase prohibition, 18 U.S.C. § 922(g)(3) unlawful-user rule, NICS procedure, A&D book discipline, and the P&P 10.06 handling rules. ATF inspections look for documented employee training. |
| A6 | **Cash Handling & Loss Prevention Acknowledgment** | P&P 02.01–02.13 plus 05.10 employee purchases. Makes drawer shortages and employee-purchase violations enforceable misconduct rather than a disputed expectation. Also covers Form 8300 awareness for cash over $10,000. |
| A8 | **Anti-Harassment, EEO & Complaint Reporting Acknowledgment** | Signed proof the employee received the complaint procedure is a required element of the *Faragher/Ellerth* affirmative defense. It is in the Handbook; it is not separately signed. |
| A9 | **Company Property & Return Agreement** | Keys, alarm codes, phones, tablets, uniforms. Handbook says property must be returned; nothing signed says what was issued. Pairs with the offboarding skill. |
| A10 | **Video & Audio Surveillance Notice** | Stores are camera-covered. A signed notice removes any expectation-of-privacy argument and is the cleanest basis for using footage in an investigation. |

**Tier 2 — real value, but each is a decision only Joshua makes.**

| ID | Document | The decision |
|---|---|---|
| B1 | **Mutual Arbitration Agreement with class/collective-action waiver** | The highest-value single document available to a 19-employee retail business — it converts a potential FLSA collective action into individual arbitrations. Trade-off: arbitration fees are employer-paid, and some employers dislike the optics. Given the open wage-hour findings (L4/L5), my recommendation is **yes**, drafted with an opt-out window and a carve-out for agency charges. |
| B2 | **FCRA background-check disclosure & authorization** | Must be a *standalone* document, not part of the application — that is a per-violation statutory-damages trap. Needed if Valley Pawn runs background checks (it should, for cash/firearm handling). |
| B3 | **Non-solicitation & confidentiality covenant** (not a non-compete) | **Virginia bans non-competes for "low-wage employees"** (Va. Code § 40.1-28.7:7), which covers most Valley Pawn store staff. A non-compete would be unlawful and carries a $10,000 civil penalty per violation. A narrow customer/employee non-solicit plus confidentiality is enforceable and is what I would draft. |
| B4 | **Virginia pawnbroker employee requirements** | Confirm with each locality whether store employees must be individually registered or fingerprinted with the local police/sheriff under the local pawnbroker ordinance. Five jurisdictions, five answers. Worth one pass. |
| B5 | **Bonus Program acknowledgment** | Deferred with the program itself to January 2027. |

### 4e. Firearm safety certification — HR-2026-05 (added on Joshua's instruction, 2026-09-23)

Joshua: *"We also require a gun safety course to be completed within three days of starting work or they will be terminated."*

This is not a new practice — it is an existing one being given teeth and a deadline. Preston announced it in `#policy-announcements` on 3/2/2026, and it is already carried in `Ask_Handbook/SOURCES_CURRENT.md` under P&P 10.06 and on the compliance calendar as `gun-safety-training-annual`. What did not exist was a deadline, a consequence, a verification step, or any record you could produce on demand. The calendar entry's own status is **⚪ unknown** — nobody has ever confirmed the certificates are on file per employee.

**Verified against the provider today, and the standing instruction is stale on two counts:**

- **gunsafetytrainingpro.com now redirects to GunSafety.co** — the company rebranded.
- **The pricing model flipped.** The "Basic Gun Safety 101" class is now **free** (about 40 minutes, any browser). The **$25 buys only the Certificate of Completion**, purchased separately after the class. Preston's instruction to "select and complete the $25 certificate version of the course" describes a product that no longer exists in that form. Anyone following it literally today would be confused about what to buy.
- **Upside found:** GunSafety.co certificates are unique per student and **independently verifiable at gunsafety.co/verify**. HR should verify rather than accept a printout — that is a real control we were not using.

**Built:** `Valley_Pawn_Firearm_Safety_Certification_HR-2026-05.docx` / `.pdf`. Key decisions written into it, with the reasoning:

| Decision | What the policy says | Why |
|---|---|---|
| Deadline | End of the **third calendar day** of employment, first day worked = day one | Matches Joshua's instruction exactly; "calendar" is defined so nobody argues business days later |
| Consequence | Completion is a **condition of employment**; employment ends at that point if not met | Cleanest framing under Virginia at-will — it is a condition, not a disciplinary process that could be argued was skipped |
| Escape valve | CEO may extend **in writing only where the Company caused the delay** (no device, no internet, no paid time scheduled) | Without this, the first time a store's internet is down we terminate someone for our own failure and hand them a claim. Narrow, written, CEO-only — it cannot be abused |
| Pay | Class and certificate done **on the clock at regular rate**; Company pays the $25, never a deduction | Required training is compensable hours worked under the FLSA — this was already the practice, now it is written down. A $25 deduction from a first paycheck could also push a new hire under minimum wage |
| Who | All employees; **under-18 employees excluded** while they do not handle firearms or work the floor | The course is 18+, so the requirement is impossible for them. This intersects finding **L4** (two minors on payroll as "Gold Sorter") and is written narrowly on purpose |
| Verification | HR verifies at gunsafety.co/verify and records holder, certificate number and date | Replaces "Preston has a printout somewhere" with a checkable record |
| Renewal | Annually by **January 31** | Aligns with the existing `gun-safety-training-annual` calendar entry |

**Two things to settle before this goes out:**

1. **It cannot apply retroactively as a termination trigger.** Three current hires are already past a three-day window — Jacob Cox (9/17), Camden Ahern (9/21), and Joshua Stagner starting 9/24. Existing staff need a stated cure date rather than an instant deadline. Recommend: **all current employees certify by 2026-10-24** (30 days), new hires from the effective date forward on the three-day rule.
2. **Nobody has confirmed who already holds a certificate.** QBO shows reimbursements for at least two ("Robert Swagger Gun Safety Certificate", "emma's firearms safety cert"), so some are done — but there is no list. First step is an audit of who has one, not a blanket send.

### 4d. Recommended sequence

1. **HELD** — HR-2026-04 send waits on the separate Handbook/P&P accuracy review. Re-render §1 with the confirmed versions, then send to all future hires + all 19 current employees.
2. **Ready on Joshua's word, independent of the review** — HR-2026-05 firearm safety certification: audit who already holds a certificate, then send with the 3-day rule for new hires and a 2026-10-24 cure date for current staff. Correct Preston's standing instruction in `#policy-announcements` (free class + $25 certificate, GunSafety.co) so the field isn't working from the old URL and the old pricing.
3. **This week** — G1 I-9 remediation for the five employees; confirm the future-hires flag on every policy in 4b, and get the Drug-Free policy into Gusto.
4. **Next** — build Tier 1 A3–A10 as a single "New Hire Policy Pack," all flagged All-future-hires, so a new hire signs one stack on day one.
5. **On Joshua's word** — Tier 2 B1–B4.
6. **Then** — G2–G5 (offer letter, checklist tasks, 90-day date, emergency contact) and hand the whole thing to the `hr-new-hire-detector` task from the HR plan so it runs without anyone watching.

---

## 5. Open legal items this review does not resolve

Carried forward from the 9/5 review, unchanged and still open:

- **L1** — the 13-item Attorney Review Packet (July 2026) has still never been sent to counsel. The governance document says neither manual may be distributed before counsel sign-off, and both are now being distributed.
- **L3** — the Drug-Free/Cannabis policy conflicts with the Handbook's medical-cannabis clause (Va. Code § 40.1-27.4). The FFL carve-out under 18 U.S.C. § 922(g)(3) is the right argument for firearms-handling roles but must be written narrowly.
- **L4 / L5** — two minors on payroll as "Gold Sorter," and two nonexempt employees at $50.00/week against 40.00 recorded hours. Highest-exposure items in the file.
- **L6** — CEO and CSO still coded Salaried Nonexempt.

HR-2026-04 does not fix any of these. It makes every *other* policy enforceable, which is a prerequisite for fixing them cleanly.

*Sources: Employee_Handbook_v2026.2_FINAL.docx (Acknowledgment section, verified verbatim); Valley_Pawn_PP_Manual_v2026.3_FINAL.docx (full section index); Gusto MCP live employee pull 2026-09-23 (19 active); HR_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md; gusto-access skill (proven e-sign flow); Life OS/OPEN_ITEMS_REGISTER.md; Valley Pawn OS/CHANGELOG.md.*
