# -*- coding: utf-8 -*-
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x11, 0x2B, 0x49)
GREY = RGBColor(0x55, 0x5A, 0x60)
RED  = RGBColor(0x9B, 0x1C, 0x1C)

doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Inches(8.5), Inches(11)
for m in ("top_margin","bottom_margin"): setattr(s, m, Inches(0.7))
for m in ("left_margin","right_margin"): setattr(s, m, Inches(0.7))
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.08

def para(text, size=10, bold=False, color=None, after=6, before=0, align=None, italic=False):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(before)
    if align is not None: p.alignment = align
    r = p.add_run(text); r.bold = bold; r.italic = italic
    r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color
    return p

def h1(text):
    p = para(text, 14, True, NAVY, after=4, before=14)
    pr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); bo = OxmlElement("w:bottom")
    bo.set(qn("w:val"),"single"); bo.set(qn("w:sz"),"6"); bo.set(qn("w:space"),"3"); bo.set(qn("w:color"),"112B49")
    b.append(bo); pr.append(b)
    return p

def h2(text): return para(text, 11, True, NAVY, after=3, before=10)

def bullets(items, size=10):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Inches(0.25)
        r = p.add_run(it); r.font.size = Pt(size)

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"),"clear"); sh.set(qn("w:color"),"auto"); sh.set(qn("w:fill"),hexcolor)
    tcPr.append(sh)

def table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    hdr = t.rows[0].cells
    for i,htxt in enumerate(headers):
        hdr[i].width = Inches(widths[i]); shade(hdr[i],"112B49")
        p = hdr[i].paragraphs[0]; p.paragraph_format.space_after = Pt(2)
        r = p.add_run(htxt); r.bold=True; r.font.size=Pt(8.5); r.font.color.rgb=RGBColor(0xFF,0xFF,0xFF)
    for ri,row in enumerate(rows):
        cells = t.add_row().cells
        for i,val in enumerate(row):
            cells[i].width = Inches(widths[i])
            if ri % 2 == 1: shade(cells[i], "F2F4F7")
            p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val); r.font.size=Pt(8.5)
            if i == 0: r.bold = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ---------------- COVER ----------------
para("FULL CIRCLE FINANCE INC", 11, True, GREY, after=0)
para("d/b/a VALLEY PAWN", 11, True, GREY, after=10)
para("Quarterly HR & Employment-Law Compliance Review", 20, True, NAVY, after=2)
para("Q4 2026 cycle  ·  Prepared October 2, 2026", 11, False, GREY, after=12)

para("Documents under review", 10, True, NAVY, after=2)
bullets([
 "Employee Handbook — v2026.5 FINAL, effective September 24, 2026 (~15,100 words)",
 "Valley Pawn Policies & Procedures Manual — v2026.8 FINAL, effective September 23, 2026 (12 sections, ~23,500 words)",
 "Eight standalone HR policy documents issued September 23 – October 1, 2026",
])
para("Prior review built on", 10, True, NAVY, after=2, before=6)
bullets([
 "Valley_Pawn_PP_Manual_Compliance_Review_2026-09-23 (P&P v2026.3; 24 findings F1–F23 + W1)",
 "Valley_Pawn_Handbook_Compliance_Review_2026-09-23 (Handbook v2026.2; Top-10 plus internal-consistency items C1–C14)",
])
para("Law verified through October 2, 2026  ·  Headcount basis: 19 active employees (Gusto)", 9.5, False, GREY, after=10, before=6)

p = para("", after=0)
r = p.add_run("CONFIDENTIAL — ATTORNEY REVIEW RECOMMENDED.  "); r.bold=True; r.font.size=Pt(9.5); r.font.color.rgb=RED
r2 = p.add_run("This is a compliance review, not legal advice. It states what the Company's documents and the cited authorities say. "
 "Nothing in it creates an attorney-client relationship or substitutes for advice from a Virginia-licensed employment attorney. "
 "Items in Section 6 should be reviewed by counsel before the affected policy is enforced or re-issued. Every citation below was "
 "checked against primary or practitioner sources on October 2, 2026; anything that could not be confirmed is marked "
 "“VERIFY WITH COUNSEL” rather than stated.")
r2.font.size=Pt(9.5)

# ---------------- 1. EXEC SUMMARY ----------------
h1("1.  Executive summary")
para("The remediation cycle that followed the September 23 reviews worked. Of the 24 findings in the P&P review, 21 are closed, "
     "two remain open as programs rather than drafting (the anti-money-laundering determination and the bonus/overtime regular-rate check), "
     "and one is a standing watch item. Of the Handbook review's Top 10, all 10 are closed, as are all fourteen internal-consistency "
     "items C1–C14. Both manuals are now internally consistent, name real people instead of absent departments, and carry the "
     "protected-activity savings language they previously lacked. That is a materially stronger position than the Company was in nine days ago.",
     after=6)
para("What is new this quarter falls into three groups.", after=6)
h2("A policy conflict created by the remediation itself")
para("Two training policies issued four days apart say opposite things about where required training happens, and a third version "
     "was announced in Slack. One tells employees to complete training at home and self-report the time; the next says never train "
     "at home or off the clock. Self-reported off-the-clock work is the classic unrecorded-hours exposure, and the employer — not "
     "the employee — carries the recordkeeping duty. This is the highest-value fix in this review and it takes one sentence (N1).", after=6)
h2("Three provisions that over- or under-state what the law requires")
para("A first-day doctor's-note rule, a wage-deduction floor stated against the federal rather than the Virginia minimum wage, and a "
     "volunteer-emergency-responder clause granted without the statute's own notice condition. None is unlawful on its face; each "
     "either invites a claim or commits the Company to more than the statute does — the same error the removed FMLA reference was (N2–N4).", after=6)
h2("Execution risk, not drafting risk")
para("Nothing in either manual is enforceable against an employee who has not acknowledged it. As of the September 30 Gusto check, "
     "74 documents sat “Needs signing” and 26 “Needs acknowledgement” with no completions on the page read — including the "
     "Handbook, the P&P Manual, the HR-2026-04 Acknowledgment and several Form W-4s. The documents are correct and nobody has signed them. "
     "That, plus the accommodation-rights poster that no one has confirmed is up at any of the five stores, is where this quarter's "
     "real exposure sits (N5, N6).", after=6)
para("One Virginia change does affect the manuals directly: the statewide injunction against the assault-firearm and magazine-capacity "
     "bans means P&P §12.06 currently tells staff a magazine limit applies that no agency in the Commonwealth may enforce. It needs a "
     "dated status note and a December review trigger, not a rewrite (N7).", after=6)

# ---------------- 2. TABLE A ----------------
h1("2.  Table A — status of every open finding from the September 23, 2026 reviews")
para("Verification method: each finding was checked against the text of the current governing document (P&P v2026.8, Handbook v2026.5), "
     "not against the changelog's claim that it was fixed. Where a finding was a program or a practice rather than a document provision, "
     "it was checked against the Open Items Register and the operating record.", 9.5, False, GREY, after=8)

h2("A.1  Policies & Procedures Manual review (v2026.3) — 24 findings")
table(
 ["ID","Finding (short)","Status","Where / evidence"],
 [
  ["F1","Timecard corrections deferred to next payroll (CRITICAL)","RESOLVED","§01.04 rewritten in v2026.4; deferral reframed as a processing limit, both Slack quotes deleted, 14-day cure commitment added."],
  ["F2","Lock-change chargeback for lost drawer key (CRITICAL)","RESOLVED in P&P — REOPENED in Handbook","§02.04/§02.08 now state pay is never docked for lost keys or shortages. But Handbook v2026.5 Return of Company Property re-introduces a re-key deduction. See N2."],
  ["F3","Manual told staff to stall regulators and police (CRITICAL)","RESOLVED","§01.06 split in v2026.4; law enforcement, ATF and inspectors admitted immediately, notification in parallel."],
  ["F4","Va. Code § 54.1-4009 record fields not stated","RESOLVED","New §05.00A lists the statutory fields, the military-ID rule and the statement-of-ownership gate."],
  ["F5","No TILA treatment; unmapped 12.5% grace charge","RESOLVED as drafting — COUNSEL ITEM OPEN","New §05.0 states the four permitted charges with caps and the TILA duty; 12.5% withdrawn. The per-store ticket reconciliation and APR check have not been evidenced. See §6."],
  ["F6","AML dealer status never determined","STILL OPEN","No AML content appears anywhere in v2026.8 and no record of the two-limb $50,000 calculation was found. Longest lead time of any open item."],
  ["F7","Return to work requires full doctor's release (ADA)","RESOLVED","§10.01 replaced with a work-restrictions and interactive-accommodation process; 10-day Commission filing duty added."],
  ["F8","Title-pawn procedure omits Va. motor-vehicle statutes","RESOLVED","§04.04/§04.06 now cite the perfection and default sequence; 40%/50% reconciled; “$1” threshold corrected; CEO approval required."],
  ["F9","Manual bonus program contradicts the live program","RESOLVED","§01.08 is now a pointer to the current published rules; earned bonuses are not reduced after the fact."],
  ["F10","Non-discretionary bonuses and the FLSA regular rate","STILL OPEN — ESCALATED","No evidence the one-month overtime recomputation was run. Compounded by $6,114.48 of corrected July/August bonus still unpaid per the Open Items Register. See N8."],
  ["F11","Solo-coverage locked-door lunch probably compensable","RESOLVED","§01.01 makes solo-coverage lunch paid; Handbook Meal periods section matches it word for word."],
  ["F12","PTO policy grants FMLA rights the Company does not owe","RESOLVED","FMLA struck from §01.11 and replaced with the protected-leave categories that do apply."],
  ["F13","~90 references to roles and systems that do not exist","RESOLVED","v2026.4/v2026.7 role sweep. Verified: Division Manager, Region Manager, Home Office, Director of Operations, COO and “Human Resources Department” now appear only inside the changelog entry describing their removal."],
  ["F14","Three conflicting default/pull timelines","RESOLVED","One timeline in §06.01, stated against the § 54.1-4005 floor; §05.01 and §08.03 cross-reference it; ownership-statement gate explicit."],
  ["F15","No protected-activity savings clause","RESOLVED","Protected Rights statement in P&P front matter; Handbook carries matching language and an express carve-out that wages are not confidential information."],
  ["F16","Firearm safety course facts stale; employee fronts the fee","RESOLVED","§10.06 rewritten to current provider facts, Company buys the certificate, no employee outlay; standalone HR-2026-05 certification policy issued."],
  ["F17","Telemarketing and SMS have no TCPA guardrails","RESOLVED","§07.06 adds the internal do-not-call list, calling hours, the 18-month EBR limit and express coverage of text messaging including Chekkit."],
  ["F18","“Keep all records indefinitely” + 4473 purge myth","RESOLVED with one gap","§03.08 is now a retention schedule and states firearms records are kept until the business is discontinued. It routes personnel records to the Handbook, which has no retention rule. See N9."],
  ["F19","No data-breach notification procedure","RESOLVED","§03.09 adds incident response and the Va. Code § 18.2-186.6 notice duties, including that the Attorney General notice has no size threshold."],
  ["F20","Cannabis / drug-testing policy in neither document","RESOLVED","Handbook v2026.5 Drug-Free Workplace and Cannabis Testing section expressly supersedes the September 2 one-pager and every earlier cannabis clause. Whether the #ask-handbook guard was lifted was not verified."],
  ["F21","Six unresolved numeric contradictions","RESOLVED","Drawer balancing twice daily; 15-day grace; 90-day employee-purchase floor; layaway terms confirmed by the CEO and written into v2026.6."],
  ["F22","Empty section headings","RESOLVED","Scheduling, Dress Code, Training Bonus, Bump Loans, Voided Checks, Stop Payments, Floor Audits, Credit Card Payments and Section 9 all filled or closed out."],
  ["F23","Lost-ticket fee $2 where statute permits $5","RESOLVED","Corrected to $5 in §05.0 with the ticket-disclosure condition stated."],
  ["W1","DOJ opinion on handgun sales to 18–20 year olds","WATCH — unchanged","§05.02 holds 21 as the floor and instructs staff not to act on news coverage. No court action found through October 2, 2026. Correct posture; take no action."],
 ],
 [0.45, 1.85, 1.15, 3.65])

h2("A.2  Employee Handbook review (v2026.2) — Top 10 by exposure")
table(
 ["#","Finding (short)","Status","Where / evidence"],
 [
  ["1","“Wages” listed as confidential information","RESOLVED","Confidential Information section now says expressly that it does not include an employee's own wages, hours or working conditions."],
  ["2","Termination promised a vacation payout the PTO section denied","RESOLVED","Both the PTO section and the Termination section now say PTO is not paid out at separation. Final-pay timing stated against Va. Code § 40.1-29."],
  ["3","No lawful way for a first-year employee to be sick","RESOLVED with a new issue","New Sick Leave and Unpaid Personal and Medical Leave sections, plus an Attendance policy with defined call-in, no-call/no-show and protected-absence rules. The doctor's-note trigger it adopted is a new finding — see N3."],
  ["4","“Human Resources” / “owner” / “CFO” undefined","RESOLVED","“Who to Contact” defines HR, Owner/President, Market Manager and Store Manager by name. CFO references removed."],
  ["5","Discipline for failing to volunteer medical information","RESOLVED","The conduct line is gone; the prescription-disclosure rule is narrowed and does not require naming the condition."],
  ["6","Civility / “discord” / “gossip” / bulletin-board rules","RESOLVED","Those rules no longer appear; a Section 7 savings clause is in place and solicitation limits are tied to working time with meal periods and breaks carved out."],
  ["7","Federal COBRA cited where the Company is under 20 employees","RESOLVED","Health Insurance section rewritten: no group plan is offered, Marketplace notice at hire, continuation rights addressed only if a plan is added. Virginia continuation (§ 38.2-3541) is not engaged absent a plan."],
  ["8","“According to law” meal-period statement false in Virginia","RESOLVED","Meal periods section now tracks P&P §01.01, states the paid solo-coverage rule, and requires clocking back in on an interrupted lunch."],
  ["9","Wage-deduction authorization said “may be asked to sign”","RESOLVED with a new issue","Deduction now runs only under a signed Company Property & Wage Deduction Authorization. The stated wage floor is the wrong one — see N2."],
  ["10","W-2/W-4 confusion, “District Attorney,” “AC AC,” 02/01/08 date","RESOLVED","All four artifacts verified absent from v2026.5; Vehicle Safety Policy rewritten as the Company's own."],
 ],
 [0.35, 1.95, 1.2, 3.6])

h2("A.3  Other Handbook-review items, including items raised outside the handbook")
table(
 ["Item","Status","Where / evidence"],
 [
  ["PUMP Act / lactation entitlement never stated","RESOLVED","Pregnancy section now states the break-time entitlement for one year, the private non-bathroom space, and identifies the store office."],
  ["No whistleblower paragraph (Va. Code § 40.1-27.3)","RESOLVED","Reporting Legal Violations section added, tracking all five statutory limbs."],
  ["Jury duty read as a withholdable benefit","RESOLVED","Jury and witness duty section states time off is given, cites Va. Code § 18.2-465.1, and confirms PTO cannot be required."],
  ["Emergency-responder leave omitted","RESOLVED with a new issue","Added as a protected absence citing Va. Code § 40.1-27.5 — verified as the correct section. The statute's conditions were not carried across. See N4."],
  ["Four-year retention rule for personnel records","STILL OPEN","Neither document contains one. P&P §03.08 routes personnel records to the Handbook; the Handbook has no retention provision. See N9."],
  ["Pay-transparency audit of every posting since July 1, 2026","STILL OPEN","Handbook now states the § 40.1-28.7:12 obligation correctly. No record was found that the live postings were audited against it. Statute carries a private right of action with a 15-business-day cure window."],
  ["Jacob Cox accommodation notice due by September 28","RESOLVED on delivery","HR-2026-08 was sent via Gusto; the Open Items Register confirms it is out. It is unsigned, like the rest of the set — see N5."],
  ["Company-wide § 2.2-3905.1(C) notice gap, three prongs","PARTLY RESOLVED","Prong (b), inclusion in the handbook: resolved. Prong (c), direct provision to new hires: addressed by the revised onboarding checklist. Prong (a), conspicuous posting at all five stores: not confirmed at any store. See N6."],
  ["Gold Sorter paid $12.00/hr below the $12.77 minimum","RESOLVED","Both Corporate Support junior roles were documented September 23 at $12.77/hr with automatic escalation to $13.75 on January 1, 2027."],
  ["Two minor employees — exemption not documented","RESOLVED","Written job descriptions set the parental-exemption basis, youth hour limits, and an express prohibition on firearms, torches, acids, melting, power-driven tools and ladders. One citation gap — see N10."],
  ["Contractor roster re-check against HB 238 presumption","STILL OPEN","Virginia's employee presumption took effect July 1, 2026 and the federal independent-contractor rule is itself being rewritten. Nothing found indicating the 1099 roster was re-tested."],
  ["Virginia-licensed attorney review of the handbook by 12/31/2026","STILL OPEN","Target date unchanged. The scope has grown — see §6."],
 ],
 [2.0, 1.15, 3.95])

# ---------------- 3. TABLE B ----------------
h1("3.  Table B — new gaps and deficiencies identified this quarter")
para("Severity reflects the cost of being wrong, not the effort to fix. “HIGH” means a provision as written invites a claim the "
     "Company would have difficulty defending, or a statutory duty is going unperformed.", 9.5, False, GREY, after=8)
table(
 ["ID","Issue","Document & section","Risk","Law / source","Recommended fix"],
 [
  ["N1",
   "Three different, live answers to where required training happens. HR-2026-10 (eff. 10/1) says “do it on your phone at home; tell your manager how long it took so it's paid.” The Training Happens at the Store policy (eff. 10/5) says “do all required training at the store, on the clock… no training at home or off the clock.” The 10/1 Slack announcement says “work it in during slow time on your shift.” Neither policy supersedes the other expressly, and both are going out for signature.",
   "Valley_Pawn_Sales_Training_HR-2026-10 vs. Training_At_The_Store_Policy_2026-10; neither is in the Handbook or the P&P Manual",
   "HIGH",
   "FLSA training-time rules, 29 C.F.R. §§ 785.27–785.32; employer recordkeeping duty, 29 C.F.R. § 516.2 and § 785.11–13 (work suffered or permitted must be recorded and paid); Va. Code § 40.1-29",
   "Issue a single training-time policy that expressly supersedes HR-2026-10 and states one rule. If any training may be done away from the store, require the employee to clock in for it rather than report it afterwards — self-reported time shifts a duty the employer cannot delegate. Fold the surviving rule into the Handbook so it cannot drift again."],
  ["N2",
   "The re-key chargeback deleted from the P&P Manual as finding F2 reappears in the Handbook, and the wage floor it is capped against is the wrong one: the text says no deduction will reduce pay “below the federal minimum wage,” and measures it over “the pay period” rather than the workweek. It also relies on a single authorization signed at hire for a loss that has not happened yet.",
   "Handbook v2026.5 — Return of Company Property",
   "HIGH",
   "Va. Code § 40.1-29(D) (written signed authorization); Va. Code § 40.1-28.10 (Virginia minimum wage, $12.77 through 12/31/2026, $13.75 from 1/1/2027); FLSA free-and-clear rule, 29 C.F.R. § 531.35 (measured per workweek, and overtime is protected as well as minimum wage)",
   "Change the floor to the Virginia minimum wage, measure it per workweek, and protect overtime as well. Best practice is a second authorization signed at the time of the loss naming the actual amount. Simplest and safest: drop the deduction, keep the return obligation, and recover by other lawful means — which the section already permits."],
  ["N3",
   "A healthcare-provider note is required for every illness absence “starting with the first day.” The September 23 review recommended three or more consecutive days; the issued text went the other way. A universal first-day note requirement pushes a cost onto the employee for a one-day illness, and in practice is the rule most often cited as evidence that an employer discouraged protected absences.",
   "Handbook v2026.5 — Attendance and Punctuality (Illness)",
   "MEDIUM",
   "ADA medical-inquiry limits, 42 U.S.C. § 12112(d)(4)(A); Va. Code § 2.2-3905.1. Also forward-looking: Virginia's paid sick leave law (2026 Acts, HB 5 / SB 199) restricts documentation demands once it reaches this employer",
   "Move the trigger to three or more consecutive days, which is what the Handbook's own Unpaid Personal and Medical Leave section already says. Keep the existing and correct rule that the note need not state a diagnosis, and keep repeated unexcused absence as a performance matter."],
  ["N4",
   "The volunteer emergency-responder absence is granted unconditionally, while the statute conditions the protection on the employee giving notice at least one hour before the scheduled start and providing documentation on return. The Handbook also limits it to “a declared emergency,” omitting the statute's separate limb for actively responding to an emergency alarm.",
   "Handbook v2026.5 — Attendance and Punctuality (Protected absences)",
   "LOW–MEDIUM",
   "Va. Code § 40.1-27.5 (verified October 2, 2026): covers a member in good standing of a recognized volunteer fire or EMS agency, (i) actively responding to an alarm or (ii) during a state of emergency as defined in § 44-146.16, with one hour's advance notice",
   "Restate the clause in the statute's own terms, including both limbs and the notice and documentation conditions. Granting more than the statute requires creates the entitlement by contract — the same mechanism that made the removed FMLA reference a finding."],
  ["N5",
   "Nothing is acknowledged. As of the September 30 Gusto check: 74 rows “Needs signing,” 26 “Needs acknowledgement,” zero completions on the page read — covering the Handbook, the P&P Manual, HR-2026-04 through HR-2026-08, the Company Property & Wage Deduction Authorization, and several unsigned Form W-4s. An unacknowledged handbook is not enforceable against the employee, and the wage-deduction authorization at N2 is the specific case where the unsigned form defeats the control it exists to create.",
   "Gusto document set — all current employees",
   "HIGH",
   "Not a statutory violation in itself. Va. Code § 40.1-29(D) makes the unsigned deduction authorization operative; unsigned W-4s are a withholding exposure under IRC § 3402 and 26 C.F.R. § 31.3402(f)(2)-1",
   "Treat signature completion as a tracked obligation with a named owner and a deadline, not a reminder. Chase the W-4s first — they are a payroll exposure independent of policy. Verify per-person rows past the first page before reporting completion, since the September 30 read was truncated and showed zero completions rather than proving none exist."],
  ["N6",
   "The accommodation-rights notice is not confirmed posted at any of the five stores. The statute requires all three prongs, and this is the only one still open.",
   "Store premises — all five locations",
   "HIGH",
   "Va. Code § 2.2-3905.1(C)(i): an employer shall post accommodation-rights information in a conspicuous location. VHRA now reaches employers of five or more (eff. July 1, 2026) and the filing window is two years (SB 637 / HB 925, eff. July 1, 2026)",
   "Produce one poster from the body of the notice already drafted for HR-2026-08, ship a copy to each store, and have each Store Manager confirm by photograph that it is up. This is a one-afternoon fix on an open statutory duty and should be the first thing done from this review."],
  ["N7",
   "P&P §12.06 tells staff that magazine-capacity limits still apply. Since July 21, 2026 every law-enforcement agency and Commonwealth's Attorney in Virginia has been enjoined from enforcing the assault-firearm and magazine-capacity bans, and the Lancaster County injunction runs to December 31, 2026 or final order. The manual carries no note of the injunction, its expiry, or the pending appeal.",
   "P&P v2026.8 §12.05, §12.06",
   "MEDIUM",
   "Crump v. Katz (Lancaster Co. Cir. Ct., preliminary injunction June 25, 2026, in effect to December 31, 2026 or final order); Santolla v. Katz (Washington Co. Cir. Ct., letter opinion July 7, 2026, extended statewide from July 21, 2026). Attorney General appealing both. Whether the §12.05 under-21 rule (2026 session, emergency clause) falls inside the enjoined scope: VERIFY WITH COUNSEL",
   "Keep the conservative practice — declining a transfer no one may currently prohibit costs a sale, enforcing a prohibition later reinstated costs the licence. Add a dated status note to §12.06 recording the injunction and the appeal, and set a December 2026 review trigger tied to the injunction's expiry. Confirm with counsel whether the under-21 rule is separately enjoined before relaxing anything."],
  ["N8",
   "Two linked wage items carried forward and now overdue. $6,114.48 of corrected July and August bonus remains unpaid, and there is still no evidence that overtime was recomputed to include the monthly bonus in the weeks it covered.",
   "Bonus program — payroll practice, not a document provision",
   "HIGH",
   "FLSA regular-rate inclusion of non-discretionary bonuses, 29 U.S.C. § 207(e) and 29 C.F.R. § 778.208–209; Va. Code § 40.1-29 (treble damages, liquidated damages, 8% interest and fees where the failure is knowing, with the § 40.1-29(P) good-faith safe harbour available only on a cure within 14 days of notice)",
   "Pay the $6,114.48. The 14-day cure provision is the Company's best protection and it only operates if the money moves promptly. Then run the one-month test the prior review specified: take one month where a store had both a bonus payout and overtime hours and check whether the overtime was recomputed. Document the answer either way."],
  ["N9",
   "A circular reference: P&P §03.08 says employee personnel records are “retained per the Employee Handbook,” and the Handbook contains no retention provision at all. The result is that the one record category with a newly extended exposure window has no stated retention period in either document.",
   "P&P v2026.8 §03.08 → Handbook v2026.5 (no corresponding section)",
   "MEDIUM",
   "VHRA filing window extended from 300 days to two years (SB 637 / HB 925, eff. July 1, 2026); FLSA payroll records three years and supporting records two years, 29 C.F.R. § 516.5–516.6; EEOC personnel-record rule, 29 C.F.R. § 1602.14",
   "Adopt the four-year rule the September 23 review recommended — personnel files, timekeeping, schedules, discipline and accommodation records, including for separated employees — and put it in the Handbook so the P&P cross-reference resolves. One short paragraph closes both the gap and the dangling pointer."],
  ["N10",
   "The minor job descriptions are careful and substantively compliant — they already exclude torches, acids, melting, power-driven tools and ladders — but their stated legal basis predates this year's amendment, which brought the federal hazardous-occupation list into Virginia law.",
   "Job_Description_Kennedy_Davis_Gold_Sorter; Job_Description_Audrey_Davis_Gold_Sorter",
   "LOW",
   "Va. Code § 40.1-100 as amended effective July 1, 2026 (2026 Acts; HB 1218 and related) now prohibits a minor from any occupation declared hazardous by the Commissioner of Labor and Industry OR by the U.S. Secretary of Labor — i.e. the FLSA Hazardous Orders at 29 C.F.R. part 570 subpart E apply as state law. The § 40.1-79.01 parental-exemption citation in the descriptions: VERIFY WITH COUNSEL",
   "Add § 40.1-100 as amended to the legal-basis line and confirm the parental-exemption citation with counsel. No duty needs to change. Separately confirm whether a Virginia employment certificate is required for the under-16 role."],
 ],
 [0.38, 2.0, 1.0, 0.5, 1.45, 1.77])

# ---------------- 4. TABLE C ----------------
h1("4.  Table C — policies announced since September 23 and not yet in a governing document")
para("Reconciliation method and what it covered: #policy-announcements (C03BHQ9RLR0) read for the full window September 23 – October 2, 2026; "
     "the Human Resources folder listed by modification date for the same window; company email searched for policy, handbook, employment-law, "
     "compliance, minimum-wage and attorney traffic over the last fourteen days. Email produced nothing policy-related — no HR or legal "
     "correspondence in the window. Note the monthly policy-sync task's own last run (October 1) reported no new Slack policies; that report "
     "is incomplete — the October 1 sales-training announcement and the eight documents below all post-date the September 23 consolidation.",
     9.5, False, GREY, after=8)
table(
 ["Policy / document","Issued","Source","Recommended placement"],
 [
  ["Account Details by Phone & Text","Eff. Oct 5, 2026","HR folder, Sep 28","P&P Manual — new subsection under §03.09 (Confidentiality). It is a customer-information disclosure control and belongs beside the breach procedure. Note it also instructs staff to call police back on a department main line, which complements §01.06; cross-reference rather than restate."],
  ["Phone & Text Scripts — Counter Card","Sep 28, 2026","HR folder","No placement needed — job aid, not policy. Reference it from the §03.09 subsection above so the card cannot drift from the rule."],
  ["Name, Image, Likeness and Voice Release (HR-2026-09)","Eff. Oct 1, 2026","HR folder, Sep 30","Keep as a standalone signed release — correct. Add a one-line pointer in the Handbook under Confidential Information. Substantively strong: it carries the Va. Code § 8.01-40 and § 18.2-216.1 consent basis, express digital-replica limits, a 90-day post-employment model-deletion commitment, a paid-time statement, and a Section 7 / agency-reporting carve-out."],
  ["Sales Training in Your First Week (HR-2026-10)","Eff. Oct 1, 2026","HR folder + Slack Oct 1","Must be reconciled before placement — conflicts with the October 5 training-location policy. See N1. Once settled, the surviving rule goes in the Handbook under Introductory Period, with the course list held separately so the Handbook does not go stale."],
  ["Training Happens at the Store","Eff. Oct 5, 2026","HR folder, Oct 1","Same as above — one combined training-time policy, placed in the Handbook, expressly superseding HR-2026-10."],
  ["New Hire Onboarding Checklist (OB-2026-01) Rev 2","Oct 1, 2026","HR folder","Process document, not policy. Confirm it carries the § 2.2-3905.1(C)(iii) accommodation-rights notice as a day-one item — that is the prong it was revised to close (N6)."],
  ["Retail Sales Academy rollout (platform change)","Announced Oct 1, 2026","Slack #policy-announcements","Operational, no placement required. Tracked here because the announcement states a third and different rule about when training is done — see N1."],
  ["Goldilocks reporting-bot rename","Announced Sep 30, 2026","Slack #policy-announcements","Not a policy. Logged for completeness of the reconciliation."],
  ["Mutual Arbitration Agreement (DRAFT — FOR COUNSEL)","Drafted Sep 23, 2026","HR folder","Do not distribute. Held correctly for attorney review — see §6. If adopted it must be reconciled with the Handbook's at-will, complaint-escalation and whistleblower sections, none of which currently contemplate arbitration."],
 ],
 [1.55, 0.85, 1.0, 3.7])

# ---------------- 5. LAW CHANGES ----------------
h1("5.  Virginia and federal law — what was checked and what changed")
para("Virginia's employment-law changes cluster around January 1 (minimum wage) and July 1 (everything else), so the September 23 – "
     "October 2 window was never likely to contain a new effective date, and it does not. The items below are the verification pass: "
     "what was confirmed unchanged, what was confirmed and had been mis-stated, and what is coming.", after=8)
h2("Confirmed unchanged since the prior review")
bullets([
 "Virginia minimum wage — $12.77/hr through December 31, 2026; $13.75 from January 1, 2027; $15.00 from January 1, 2028; CPI-indexed from 2029. Va. Code § 40.1-28.10 (HB 1 / SB 1, signed April 9, 2026). Confirmed against DOLI.",
 "FLSA white-collar exempt salary threshold — $684/week ($35,568/yr); highly-compensated employee $107,432/yr, following the 2024 rule's vacatur and the Department of Labor's May 14, 2026 technical amendment. Virginia sets no higher figure. Any salaried-exempt manager below $684/week is misclassified.",
 "Virginia paid sick leave (HB 5 / SB 199, signed May 20, 2026) — compliance dates confirmed as the Handbook states them: July 1, 2027 for 50+ employees, January 1, 2028 for 25–49, January 1, 2029 for all employers. At 19 employees the Company's date is January 1, 2029 unless headcount reaches 25. Handbook v2026.5 is accurate on this point; an earlier-looking “July 2027” figure in general commentary refers to the 50+ tier only.",
 "Virginia Paid Family & Medical Leave (HB 1207) — payroll contributions from April 1, 2028, benefits from December 1, 2028. Above the 11-employee threshold the employer share applies. Handbook note is accurate.",
 "VHRA — employer definition broadened to five or more employees and the filing window extended from 300 days to two years, both effective July 1, 2026 (SB 637 / HB 925). This is the change that makes the retention gap at N9 matter.",
 "Virginia pay transparency, Va. Code § 40.1-28.7:12, effective July 1, 2026 — unchanged. Private right of action with a 15-business-day cure window after written notice.",
 "Title VII, ADA, ADEA, PDA/PWFA, PUMP, USERRA, NLRA, FCRA, IRCA, OSHA — no change affecting a 19-employee Virginia retailer in the window. The Company remains outside FMLA (50-employee threshold) and outside federal COBRA (20-employee threshold, and no group plan is offered).",
])
h2("Confirmed, and previously mis-stated or newly relevant")
bullets([
 "Va. Code § 40.1-100 as amended effective July 1, 2026 — a minor may not work in an occupation declared hazardous by the Commissioner of Labor and Industry OR by the U.S. Secretary of Labor. The federal Hazardous Orders now operate as Virginia law. Directly relevant to the two Corporate Support junior roles (N10).",
 "Va. Code § 40.1-27.5 — verified as the correct section for volunteer emergency-responder protection, and verified to carry conditions the Handbook omits (N4).",
 "Virginia non-compete law, Va. Code § 40.1-28.7:8 — the 2026 session added that a non-compete is unenforceable where the employer terminates without cause and provides no severance, and barred non-competes with licensed healthcare professionals outright. Low impact here: the Handbook's Outside Employment section is a conflict-of-interest rule, not a restrictive covenant, and no store role is subject to one. Re-check if the arbitration agreement or any future offer letter introduces restrictive covenants.",
 "Assault-firearm and magazine-capacity bans — enjoined statewide since July 21, 2026, Lancaster County injunction running to December 31, 2026 or final order, Attorney General appealing both (N7).",
 "Virginia worker-classification presumption (HB 238, effective July 1, 2026) — workers are presumed employees unless the hiring entity proves IRS independent-contractor status. Still unaddressed against the 1099 roster.",
])
h2("Watch items — no action this quarter")
bullets([
 "Federal independent-contractor rule — the Department of Labor signalled an October 2026 final rule rescinding the 2024 regulation and returning to a core-factors test. It would not relax Virginia's HB 238 presumption, which is the binding constraint here.",
 "Heat-illness standard — Virginia's Safety and Health Codes Board remains directed to issue indoor and outdoor regulations. Nothing issued; the Safety section will need a paragraph when they do.",
 "DOJ Office of Legal Counsel opinion of September 17, 2026 on handgun sales to 18–20 year olds — no court action found through October 2, 2026. Va. Code § 18.2-308.7(C) continues to make under-21 handgun purchase unlawful in the Commonwealth and is the binding rule. P&P §05.02 handles this correctly. Change nothing.",
 "EEO-1 reporting — the EEOC has proposed rescinding EEO-1 through EEO-5. The Company is below the 100-employee filing threshold either way.",
])

# ---------------- 6. COUNSEL ----------------
h1("6.  Items needing Virginia-licensed employment attorney sign-off")
para("In order of the cost of being wrong. The prior review scoped a flat-fee handbook review at roughly $1,500–$3,500 and targeted it "
     "before December 31, 2026; that target should hold, and the scope below should be sent in one package rather than piecemeal.", after=8)
table(
 ["#","Item","Why counsel rather than drafting","Who"],
 [
  ["1","Pawn fee structure and TILA disclosure (carried from F5)","It touches every pawn ticket the Company writes, the finance charge must include storage and service fees, and Va. Code § 54.1-4014(B) routes any pawnbroker-chapter violation into the Virginia Consumer Protection Act with its own private remedies. The new §05.0 states the law correctly; whether the tickets Bravo actually prints match it is the open question.","Counsel experienced in Virginia pawnbroker regulation and consumer credit"],
  ["2","Mutual Arbitration Agreement (drafted, correctly held)","Enforceability, the carve-outs it must preserve, and its interaction with the Handbook's at-will, complaint-escalation and whistleblower provisions. Distributing an unreviewed arbitration agreement is worse than having none.","Virginia employment attorney"],
  ["3","Anti-money-laundering scope determination (carried from F6)","The pawnbroker carve-out at 31 C.F.R. § 1027.100(b)(2)(ii) covers pawn transactions and the sale of pawn collateral but not outright buys from the public. Where a gold buy ends and a pawn begins is exactly the line a practitioner draws faster and more reliably than a reader of the regulation. Run the two-limb $50,000 calculation first so counsel is pricing a question, not a research project.","Counsel familiar with 31 C.F.R. part 1027"],
  ["4","Whether the §12.05 under-21 assault-firearm rule is inside the enjoined scope (N7)","Two circuit-court injunctions, one statewide, both on appeal, against a statute enacted with an emergency clause. The commercially cautious answer is clear; the legal answer is not, and it should be in writing before anyone relaxes a practice.","Counsel experienced in Virginia firearms law and ATF regulation"],
  ["5","Wage-deduction mechanics for the Company Property authorization (N2)","Whether a single authorization signed at hire satisfies Va. Code § 40.1-29(D) for a loss that has not yet occurred, and how the FLSA free-and-clear rule interacts with it. The alternative — drop the deduction — needs no opinion, so this is only worth counsel's time if the Company wants to keep the right.","Virginia employment attorney"],
  ["6","Minor-employment citations and certificate requirement (N10)","Confirm the parental-exemption citation, confirm no Virginia employment certificate is required for the under-16 role, and confirm the duty list clears the federal Hazardous Orders now incorporated by Va. Code § 40.1-100. The substantive controls look right; the paperwork should be provable on inspection.","Virginia employment attorney"],
  ["7","Drug-free workplace and cannabis policy as consolidated (carried from F20)","Now resolved as a drafting matter — the Handbook controls and expressly supersedes. It still decides terminations, and Virginia's lawful-off-duty-use protection and the federal firearms prohibition at 18 U.S.C. § 922(g)(3) pull in different directions for the Corporate Support roles that do not handle firearms.","Virginia employment attorney"],
 ],
 [0.35, 1.7, 3.5, 1.55])

# ---------------- 7. RECOMMENDED SEQUENCE ----------------
h1("7.  Recommended sequence")
h2("This week")
bullets([
 "Produce and ship the accommodation-rights poster to all five stores, with photo confirmation back from each Store Manager (N6). Open statutory duty, one afternoon.",
 "Issue one training-time policy that expressly supersedes HR-2026-10, and hold the October 5 rollout until it exists (N1).",
 "Pay the $6,114.48 of corrected July and August bonus (N8). The 14-day cure protection only works if the money moves.",
 "Chase the unsigned Form W-4s ahead of the policy signatures (N5).",
])
h2("Next two weeks")
bullets([
 "Handbook amendment pass, one version: the Virginia minimum-wage and per-workweek deduction floor (N2), the three-day doctor's-note trigger (N3), the emergency-responder clause restated in the statute's terms (N4), and a four-year records-retention paragraph that resolves the P&P §03.08 pointer (N9).",
 "Add the dated injunction status note and a December review trigger to P&P §12.06 (N7).",
 "Run the bonus/overtime regular-rate test on one month and document the answer either way (N8).",
 "Run the AML two-limb calculation on non-pawn buy and sell activity only, and write down the determination whichever way it comes out (F6).",
 "Audit every job posting since July 1, 2026 for a good-faith wage range, and re-test the 1099 roster against the HB 238 presumption.",
 "Drive signature completion to zero outstanding, verifying per-person rows past the first page (N5).",
])
h2("Before December 31, 2026")
bullets([
 "Send the Section 6 package to a Virginia-licensed employment attorney in one engagement.",
 "Re-check P&P §12.06 against the injunction's December 31 expiry and the appeal's posture.",
 "Confirm the January 1, 2027 minimum-wage step to $13.75 is scheduled in Gusto, including the two Corporate Support junior roles whose pay is pegged to it.",
])

# ---------------- 8. METHOD ----------------
h1("8.  Scope, method, and what was not checked")
para("Read in full: Employee Handbook v2026.5 FINAL; Policies & Procedures Manual v2026.8 FINAL; both September 23, 2026 compliance "
     "reviews; the v2026.7 and v2026.8 handoff notes; and the eight standalone policy documents issued September 23 – October 1, 2026.", after=6)
para("Reconciled against: Slack #policy-announcements for the full window September 23 – October 2, 2026; the Human Resources folder "
     "by modification date; company email (jdavis@fcfpawn.com) for the last fourteen days on policy, handbook, employment-law, compliance, "
     "minimum-wage and attorney terms; and the Open Items Register across all three domains.", after=6)
para("Legal sources checked live on October 2, 2026 rather than from recall: Va. Code §§ 40.1-28.10, 40.1-27.3, 40.1-27.5, 40.1-29, "
     "40.1-28.7:8, 40.1-28.7:12, 40.1-100, 2.2-3905.1, 18.2-465.1, 18.2-308.7, 54.1-4009 and 54.1-4014; the 2026 Acts of Assembly for "
     "HB 1 / SB 1, HB 5 / SB 199, HB 1207, SB 637 / HB 925, HB 238 and HB 1218; the Department of Labor's May 2026 restoration of the "
     "white-collar salary levels; the two 2026 circuit-court injunctions against the assault-firearm and magazine-capacity bans; and the "
     "federal independent-contractor rulemaking status.", after=6)
para("Each prior finding was closed only against the text of the current governing document, not against the changelog entry claiming "
     "it had been fixed. Where a finding was a program or a payroll practice rather than a document provision, it was checked against "
     "the Open Items Register and the operating record, and is reported as open where no completion record was found.", after=6)
para("Not checked, and reported here so the gaps are visible rather than assumed: whether the accommodation-rights poster is physically "
     "up at any store (asserted nowhere, confirmed nowhere — this is N6); whether the #ask-handbook assistant's cannabis guard was lifted "
     "after the F20 consolidation; per-person Gusto signature status for the six employees whose rows fell past the first page of the "
     "September 30 read; whether the pay-transparency posting audit was ever performed; whether any Bravo-side control that a P&P section "
     "assumes exists actually does; and the contents of the one screenshot in the Jacob Cox disclosure thread, which no session has opened "
     "and which should be opened only into a confidential medical file, never into Gusto.", after=6)
para("This review states what the documents and the cited authorities say. It is not legal advice. The items in Section 6 should go to a "
     "Virginia-licensed attorney before the affected policy is enforced or re-issued.", 9.5, True, GREY, after=4, before=6)

OUT = os.environ.get("OUT_DIR", ".")
path = os.path.join(OUT, "Valley_Pawn_Compliance_Review_October_2026.docx")
doc.save(path)
print("wrote", path)
