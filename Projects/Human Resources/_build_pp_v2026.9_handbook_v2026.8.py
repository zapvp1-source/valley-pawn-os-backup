#!/usr/bin/env python3
"""
_build_pp_v2026.9_handbook_v2026.8.py

Builds Valley_Pawn_PP_Manual_v2026.9_FINAL.docx and Employee_Handbook_v2026.8_FINAL.docx
from v2026.8 / v2026.7 (which are NEVER modified), aligning both manuals to the
Valley Pawn Academy final pre-launch review (2026-10-20/21).

ADDITIVE ONLY: the source files are opened read-only and saved under the new names.
Every edit is quote-matched: the paragraph is located by a unique needle and the old
text must occur exactly once, or the build aborts and nothing is written.
All other paragraphs, styles and formatting are untouched.

Run:  python3 _build_pp_v2026.9_handbook_v2026.8.py
Writes the two .docx files plus PP_v2026.9_CHANGES.md (change table) in this folder.
"""
import copy
import os
import sys

import docx
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
PP_SRC = os.path.join(HERE, "Valley_Pawn_PP_Manual_v2026.8_FINAL.docx")
PP_OUT = os.path.join(HERE, "Valley_Pawn_PP_Manual_v2026.9_FINAL.docx")
HB_SRC = os.path.join(HERE, "Employee_Handbook_v2026.7_FINAL.docx")
HB_OUT = os.path.join(HERE, "Employee_Handbook_v2026.8_FINAL.docx")
CHANGES_MD = os.path.join(HERE, "PP_v2026.9_CHANGES.md")

DATE = "October 21, 2026"
LOG = []          # (doc, section, old, new, source)
ALREADY = []      # (doc, section, what, source)


class BuildError(Exception):
    pass


def find_one(doc, needle):
    hits = [p for p in doc.paragraphs if needle in p.text]
    if len(hits) != 1:
        raise BuildError("needle matched %d paragraphs (need 1): %r" % (len(hits), needle))
    return hits[0]


def replace(doc, docname, section, needle, old, new, source):
    p = find_one(doc, needle)
    full = p.text
    if full.count(old) != 1:
        raise BuildError("old text found %d times in %s: %r" % (full.count(old), section, old))
    done = False
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new, 1)
            done = True
            break
    if not done:  # match spans runs: collapse into first run, keep its formatting
        runs = p.runs
        runs[0].text = full.replace(old, new, 1)
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
    LOG.append((docname, section, old, new, source))
    return p


def insert_after(anchor, text, template=None):
    """Insert a new paragraph after `anchor`, cloned from `template` (default anchor)
    so it carries the same paragraph and run formatting."""
    tpl = template if template is not None else anchor
    new_p = copy.deepcopy(tpl._p)
    # never duplicate the template's bookmarks (heading anchors) or comments
    for tag in ("bookmarkStart", "bookmarkEnd", "commentRangeStart", "commentRangeEnd"):
        for el in new_p.findall(qn("w:" + tag)):
            new_p.remove(el)
    para = Paragraph(new_p, anchor._parent)
    runs = para.runs
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    runs[0].text = text
    anchor._p.addnext(new_p)
    return para


def add(doc, docname, section, anchor_needle, text, source, template_needle=None):
    anchor = find_one(doc, anchor_needle)
    tpl = find_one(doc, template_needle) if template_needle else None
    p = insert_after(anchor, text, tpl)
    LOG.append((docname, section, "(new paragraph)", text, source))
    return p


# --------------------------------------------------------------------------- P&P
HOURS_PP = (
    "STORE HOURS. Culpeper, Roanoke and Waynesboro: Monday through Saturday — 10:00 AM to 6:00 PM "
    "Monday through Friday, and 10:00 AM to 5:00 PM Saturday. Harrisonburg and Lexington: Monday, "
    "Tuesday, Thursday, Friday and Saturday, 10:00 AM to 6:00 PM — CLOSED WEDNESDAY. All five stores "
    "are closed Sunday. Any store open six days a week closes at 5:00 PM on Saturday."
)


def build_pp():
    d = docx.Document(PP_SRC)
    n0 = len(d.paragraphs)
    P = "P&P"

    # Title page
    replace(d, P, "Title page", "Version 2026.8 — FINAL", "Version 2026.8 — FINAL", "Version 2026.9 — FINAL", "Version bump")
    replace(d, P, "Title page", "Version 2026.8 FINAL — supersedes", "Version 2026.8 FINAL", "Version 2026.9 FINAL", "Version bump")
    replace(d, P, "Title page", "Prepared: July 8, 2026", "Updated: September 23, 2026 (v2026.8)",
            "Updated: %s (v2026.9)" % DATE, "Version bump")

    # 1. 01.01 hours
    replace(d, P, "01.01 Hours of Operation", "STORE HOURS. Culpeper: Monday through Saturday",
            "STORE HOURS. Culpeper: Monday through Saturday, 10:00 AM to 6:00 PM. Harrisonburg, Waynesboro, "
            "Lexington and Roanoke: Monday, Tuesday, Thursday, Friday and Saturday, 10:00 AM to 6:00 PM — "
            "CLOSED WEDNESDAY. All five stores are closed Sunday. No Valley Pawn store ever closes at 5:00 PM; "
            "Culpeper is the only store open on Wednesday.",
            HOURS_PP,
            "CEO rule 2026-10-01 (six-day stores close 5 PM Saturday); Roanoke six days from 2026-10-01, "
            "Waynesboro six days from 2026-10-14; Academy review blocker 3")
    # 1b. 12.02 closing time restated hours
    replace(d, P, "12.02 Closing Time (restates hours)", "Stores close at 6:00 PM. Staff do not stay past 6:30 PM",
            "Stores close at 6:00 PM. Staff do not stay past 6:30 PM unless they are still helping customers.",
            "Stores close at the time in Section 01.01 — 6:00 PM, or 5:00 PM on Saturday at the six-day stores "
            "(Culpeper, Roanoke and Waynesboro). Staff do not stay more than 30 minutes past closing unless "
            "they are still helping customers.",
            "Same as 01.01")

    # 2. 06.01 timeline
    replace(d, P, "06.01 Pull for Inventory", "DEFAULT AND PULL — THE CONTROLLING TIMELINE",
            "Day 1 is the loan due date.", "Day 1 past due is the day after the loan due date.",
            "Academy review blocker 2 / M-01; Va. Code § 54.1-4005")
    replace(d, P, "06.01 Pull for Inventory", "CHANGE EFFECTIVE OCTOBER 1, 2026",
            "are expired as soon as they are past due, at any dollar amount.",
            "are marked expired in Bravo as soon as they are past due, at any amount, but nothing is pulled, "
            "priced or sold before the 15-day legal grace period ends (day 45 of the loan; Va. Code § 54.1-4005).",
            "Academy review blocker 2; Va. Code § 54.1-4005")

    # 3. 05.00A ID
    replace(d, P, "05.00A Required Transaction Record", "IDENTIFICATION: verify identity from an UNEXPIRED",
            "Capture a digital image of the identification.",
            "For a firearm transfer (Form 4473), the supplemental document must be government-issued — e.g. "
            "vehicle registration, tax bill, voter card (27 CFR 478.124(c)(3)(i)). A utility bill or lease does "
            "not qualify. Capture a digital image of the identification. A customer photo is taken on every intake.",
            "Va. Code § 54.1-4009 (pawn/buy: other documentation allowed); 27 CFR 478.124(c)(3)(i); "
            "Academy default D8 (customer photo every intake)")

    # 4. 08.02 account details
    replace(d, P, "08.02 FDCPA — Privacy & Confidentiality", "Do not discuss a debtor's account in front of",
            "anyone other than the debtor and their spouse.",
            "anyone other than the verified account holder.",
            "Account Details by Phone & Text policy (draft, October 2026); Academy decision 2")
    replace(d, P, "08.02 FDCPA — Disinterested Third Parties", "Anyone other than the debtor, the debtor's spouse",
            "Anyone other than the debtor, the debtor's spouse, or the debtor's attorney is a disinterested third "
            "party — never divulge account details or request payment from such a party.",
            "Account details go only to the verified account holder: the customer gives their full name plus one "
            "non-public identifier — the ticket number, their date of birth, or the last four digits of the phone "
            "number on file. Anyone else — a spouse, relative, friend or attorney included — is a disinterested "
            "third party: never divulge account details or request payment from such a party. That person comes "
            "in with ID and the ticket, or the customer calls.",
            "Account Details by Phone & Text policy (draft, October 2026); Academy decision 2")

    # 5. 3310.4 + gift
    replace(d, P, "05.02 Buy Transactions — Form 3310.4", "ATF Form 3310.4 (Multiple Sales) is completed",
            "It is not required for a customer redeeming multiple pawned firearms — sales and transfers only.",
            "It is not required for a customer redeeming multiple pawned firearms — sales and transfers only "
            "(27 CFR 478.126a(a)). The Store Manager files it the same day and copies Joshua Davis (CEO).",
            "27 CFR 478.126a(a); Academy blocker 1")
    replace(d, P, "03.08 Company Records — 3310.4 log", "Multiple Gun Sales (3310.4) Log",
            "used when a customer purchases two or more firearms within a five-day period.",
            "used when two or more handguns are sold or transferred to the same customer within five consecutive "
            "business days (Section 05.02).",
            "27 CFR 478.126a(a); consistency with 05.02")
    add(d, P, "05.02 Buy Transactions — straw purchases", "Prohibited purchasers include (non-exhaustive)",
        "STRAW PURCHASES AND GIFTS. The person who completes Form 4473 must be the actual buyer. A genuine gift "
        "paid for with the buyer's own money is lawful — the buyer is the actual transferee. If someone else "
        "chose it, is paying, or will reimburse the buyer, stop.",
        "18 U.S.C. § 922(a)(6); ATF Form 4473 question 21.a; Academy review (L6-02, L7-14)")

    # 6. under-21
    replace(d, P, "05.02 Age script", "The reasons: a Department of Justice opinion",
            "and does not repeal the statute, which remains in the U.S. Code.",
            "and does not repeal the statute (18 U.S.C. § 922(b)(1)), which remains in the U.S. Code.",
            "18 U.S.C. § 922(b)(1)")
    replace(d, P, "05.02 Age script", "The reasons: a Department of Justice opinion",
            "Virginia law (Va. Code § 18.2-308.7) makes it unlawful for any person younger than 21 to knowingly "
            "and intentionally purchase a handgun anywhere in the Commonwealth — a Class 1 misdemeanor — and that "
            "state prohibition is unaffected.",
            "Virginia law (Va. Code § 18.2-308.7(C), HB 1525 of 2026, signed April 22, 2026) makes it unlawful for "
            "any person younger than 21 to knowingly and intentionally purchase a handgun or an \"assault firearm\" "
            "anywhere in the Commonwealth — a Class 1 misdemeanor — and that state prohibition is unaffected. It is "
            "in force: it is being challenged in Boyer v. Katz (Lynchburg Circuit Court, filed October 6, 2026), "
            "with no injunction as of this writing. It is a separate law from the 2026 assault-firearm sales ban "
            "(HB 217 / SB 749), which is enjoined and is not treated as law.",
            "Va. Code § 18.2-308.7(C) (HB 1525, 2026); Boyer v. Katz; Academy review A2 #31–32")
    replace(d, P, "05.02 Age script", "Accordingly: no handgun or handgun ammunition is sold",
            "no handgun or handgun ammunition is sold or transferred to anyone under 21, and no long gun to anyone "
            "under 18. If a customer raises the news coverage, tell them Virginia law sets the age at 21",
            "no handgun or handgun ammunition is sold or transferred to anyone under 21, no assault firearm to "
            "anyone under 21 (Section 12.05), and no long gun to anyone under 18. Not sure if something counts as "
            "an assault firearm? Ask the Market Manager (Section 12.06). If a customer raises the news coverage, "
            "tell them federal and Virginia law set the age at 21",
            "18 U.S.C. § 922(b)(1); Va. Code § 18.2-308.7(C)")
    replace(d, P, "12.05 Assault Firearms — Under-21 Rule", "Effective April 2026 (Virginia HB 1525",
            "Effective April 2026 (Virginia HB 1525, 2026 Session, enacted with an emergency clause), no store "
            "sells or transfers an assault firearm to any person under 21 years of age. Federal law already bars "
            "a dealer from selling a handgun to anyone under 21.",
            "Federal law (18 U.S.C. § 922(b)(1)) and Virginia law (Va. Code § 18.2-308.7(C), HB 1525 of 2026, "
            "signed April 22, 2026) bar anyone under 21 from buying a handgun, and Virginia law also bars anyone "
            "under 21 from buying an \"assault firearm.\" No store sells or transfers a handgun or an assault "
            "firearm to any person under 21. The Virginia rule is in force — it is being challenged in Boyer v. "
            "Katz (Lynchburg Circuit Court, filed October 6, 2026), with no injunction as of this writing. It is "
            "not part of the separate 2026 assault-firearm sales ban (HB 217 / SB 749), which is enjoined; do not "
            "treat that ban as law. Not sure if something counts? Ask the Market Manager.",
            "18 U.S.C. § 922(b)(1); Va. Code § 18.2-308.7(C); Academy review A2 #32")

    # 7. 07.04 greeting
    replace(d, P, "07.04 Customer Service", "Greeting standards: in uniform, name visible",
            "acknowledge every customer entering ('Welcome to Valley Pawn!'), walk around the counter to greet "
            "them, introduce yourself, and ask how you can help. TELL EVERY CUSTOMER about the three things that "
            "set Valley Pawn apart: the 30-day warranty on everything we sell, the mobile app to shop and pay "
            "online, and free layaway. Every customer, every visit.",
            "acknowledge every customer entering, walk around the counter to greet them, introduce yourself, and "
            "ask how you can help. The greeting is: 'Welcome to Valley Pawn! Have you ever been here before?' A "
            "first-time customer hears the three things that set Valley Pawn apart: the 30-day warranty on "
            "everything we sell (firearms, ammunition and consumables excluded — Section 05.08), free layaway, and "
            "the mobile app to pay loans and shop from anywhere. Before any customer leaves, they have also heard "
            "what's on clearance — together, \"the four things.\" Every customer, every visit.",
            "CEO greeting standard (2026-10-13); Academy review A1 X4/X5, A2 #49")

    # 8. 05.03 discounts
    replace(d, P, "05.03 Sell Transactions", "Items purchased from customers or pulled from inventory",
            "Employees may discount sale purchases up to 30% of listed price; no item may be sold at more than a "
            "50% discount.",
            "Associates may discount up to 30% of the listed price (10% is the normal give). A discount of 31% to "
            "50% needs the Store Manager's approval on the ticket. No item is ever sold at more than a 50% discount.",
            "Academy review A1 X9 / 10-14 default; M-03")

    # 9. 05.08 returns / warranty
    replace(d, P, "05.08 Refunds", "30-day return/warranty window from date of purchase",
            "30-day return/warranty window from date of purchase, with receipt, for most retail items; no returns "
            "on firearms, ammunition, or consumables.",
            "30-day return window from date of purchase for most retail items: a return needs the receipt and the "
            "item in original condition. No returns on firearms, ammunition, or consumables.",
            "Academy review A2 #52")
    add(d, P, "05.08 Refunds", "30-day return window from date of purchase for most retail items",
        "30-day warranty: everything we sell carries a 30-day warranty except firearms, ammunition and "
        "consumables. The warranty needs a customer account with an email address on file — no email, no "
        "warranty. A return does not depend on an email; it depends on the receipt and the item's condition.",
        "Academy review A2 #52, #77 (warranty requires account with email)")
    add(d, P, "05.08 Refunds", "30-day warranty: everything we sell carries",
        "Firearms: no returns. A firearm that stops working within 30 days of purchase comes in, and the Store "
        "Manager and the Market Manager decide what happens.",
        "Academy review A2 #83 / L6-06")

    # 10. counterfeit (02.04)
    add(d, P, "02.04 Cash Drawers", "New drawer hardware includes an 'auto-open' feature",
        "COUNTERFEIT CHECK. Check every $50 and $100 with the UV light and watermark; the pen is a backup. A "
        "suspected counterfeit is never handed back to the customer — give it to the Store Manager, who calls "
        "the police.",
        "U.S. Secret Service counterfeit procedure; Academy review A1 #28",
        template_needle="Since employees are responsible for the contents of their cash drawers")

    # 11. 02.07 Bravo step names
    replace(d, P, "02.07 Balancing Cash Drawers", "The final drawer balance is conducted at the end of the day",
            "select \"Close Till\" from the menu, then \"End of Day,\" and confirm the correct date is entered.",
            "follow the Bravo close in Section 02.13 — Close Till, count total funds, Close Store — and confirm "
            "the correct date is entered.",
            "Consistency with 02.13; Academy review (Close Till → Close Store)")

    # 12. 04.04 title pawn
    add(d, P, "04.04 Vehicles", "When conducting a pawn/pledge loan on a vehicle",
        "The vehicle is held by the store for the life of the pawn; a loan where the customer keeps the vehicle "
        "is a motor-vehicle title loan, which Valley Pawn does not make.",
        "Va. Code § 54.1-4005; Va. Code § 6.2-2200 et seq.; Academy review A2 #88")

    # 13. 07.03 phone
    add(d, P, "07.03 Telephone Etiquette", "Offer to take the customer's application information",
        "A caller who says they're a police officer: take their name and department and call back through the "
        "department's main number before discussing anything.",
        "Industry practice; Account Details by Phone & Text policy (2026-10); Academy review A1 #26")
    add(d, P, "07.03 Telephone Etiquette", "A caller who says they're a police officer",
        "Firearm background checks by phone: to a verified buyer only, say \"Your background check is finished, "
        "you can come in.\" Never say \"approved\" or \"denied\", never name the gun, and never say that a gun "
        "is on the premises.",
        "Academy review A2 #45 (L6-03, L6-05)")

    # 14. 12.06 — enjoined ban (coordinator follow-up 2026-10-21)
    replace(d, P, "12.06 Assault Firearm Classification", "Whether a firearm is an \"assault firearm\" is decided",
            "rimfire firearms are not covered, but magazine-capacity limits still apply;",
            "rimfire firearms are not covered;",
            "HB 217 / SB 749 enjoined statewide since July 21, 2026 (Compliance Review October 2026, N7)")
    replace(d, P, "12.06 Assault Firearm Classification", "Whether a firearm is an \"assault firearm\" is decided",
            "Employees under 21 do not handle assault firearms until the Market Manager confirms they may lawfully do so.",
            "Employees under 21 do not handle assault firearms until the Market Manager confirms they may lawfully do so. "
            "The 2026 Virginia assault-firearm and magazine sales ban is blocked by a court order and is not in force; "
            "do not tell customers it applies. The under-21 rule (§12.05) is separate and is in force. Any question "
            "about whether a product is restricted goes to the Market Manager.",
            "HB 217 / SB 749 enjoined statewide (Compliance Review October 2026, N7); CEO/coordinator direction 2026-10-21")

    # Already correct (verified, not changed)
    ALREADY.append((P, "05.02 Form 3310.4",
                    "Already says sales/transfers of two or more handguns to the same person within five consecutive "
                    "business days, by close of business that day, and not for redemptions — only the filer and "
                    "citation were added.", "27 CFR 478.126a(a)"))
    ALREADY.append((P, "05.00A ID", "Already allowed 'other documentation verifying' the current address for "
                    "pawn/buy records — kept as is.", "Va. Code § 54.1-4009"))
    ALREADY.append((P, "06.01 timeline", "Grace through day 15, hold through day 30, pull from day 31 finished by "
                    "day 61, CEO approval past 61 — unchanged.", "Va. Code § 54.1-4005"))
    ALREADY.append((P, "01.01 staff arrival", "'In the store preparing to open no later than 9:30 AM' — unchanged.", ""))

    # Changelog entry at the top of the Changelog section
    changelog = find_one(d, "Changelog")
    head_tpl = find_one(d, "What's New in Version 2026.8 (September 23, 2026)")
    item_tpl = find_one(d, "Six operating standards that had been issued only as separate Gusto documents")
    entries = [
        "Store hours (01.01, 12.02) — Culpeper, Roanoke and Waynesboro are open Monday–Saturday and close at "
        "5:00 PM on Saturday; Harrisonburg and Lexington stay closed Wednesday; the sentence \"No Valley Pawn "
        "store ever closes at 5:00 PM\" is removed.",
        "Default timeline (06.01) — Day 1 past due is the day after the due date; a first-payment default is "
        "marked expired at once, but nothing is pulled, priced or sold before the 15-day grace period ends "
        "(day 45 of the loan).",
        "Customer ID (05.00A) — for a Form 4473 the second address document must be government-issued "
        "(27 CFR 478.124(c)(3)(i)); a utility bill or lease does not qualify; a customer photo is taken on every "
        "intake.",
        "Account details (08.02) — adopts the account-holder-only rule: account details go only to the verified "
        "account holder (name plus ticket number, date of birth or last four of the phone on file); a spouse or "
        "attorney is no longer an exception.",
        "Multiple handguns and straw purchases (05.02, 03.08) — the Store Manager files Form 3310.4 the same day "
        "and copies the CEO; the 3310.4 log line now says handguns and business days; the genuine-gift rule is "
        "added to the straw-purchase text.",
        "Under-21 (05.02, 12.05) — the rule rests on federal law (18 U.S.C. § 922(b)(1)) and Va. Code "
        "§ 18.2-308.7(C) (HB 1525), which is in force and separate from the enjoined HB 217 / SB 749 ban.",
        "Customer service (07.04) — greeting is \"Welcome to Valley Pawn! Have you ever been here before?\"; "
        "first-timers hear the three things; every customer hears the four things, including clearance, before "
        "leaving.",
        "Discounts (05.03) — 31% to 50% needs the Store Manager's approval on the ticket; never past 50%.",
        "Returns and warranty (05.08) — the warranty needs an account with an email; returns need the receipt "
        "and original condition; a firearm that fails within 30 days goes to the Store Manager and Market "
        "Manager.",
        "Counterfeit bills (02.04) — UV light and watermark on every $50 and $100; a suspected counterfeit is "
        "never handed back.",
        "End of day (02.07) — Bravo step names now match Section 02.13: Close Till, count total funds, Close "
        "Store.",
        "Title pawns (04.04) — the vehicle is held by the store for the life of the pawn; Valley Pawn does not "
        "make motor-vehicle title loans.",
        "Telephone (07.03) — a caller who says they are police is verified by calling back through the "
        "department's main number; background-check results are given only as \"finished, you can come in\".",
        "Assault-firearm classification (12.06) — the statement that magazine-capacity limits apply is removed; "
        "the 2026 Virginia assault-firearm and magazine sales ban (HB 217 / SB 749) is blocked by a court order "
        "and is not in force, and the under-21 rule in 12.05 is separate and in force.",
        "Because this revision changes existing rules, a new signed Employee Handbook & P&P Acknowledgment "
        "(HR-2026-04) is issued with this version, per Acknowledgment Section 5.",
    ]
    h = insert_after(changelog, "What's New in Version 2026.9 (%s) — aligned to the Valley Pawn Academy final review"
                     % DATE, head_tpl)
    last = h
    for e in entries:
        last = insert_after(last, e, item_tpl)
    LOG.append((P, "Changelog", "(new entry)", "v2026.9 heading + %d lines" % len(entries), "This revision"))

    added_expected = 1 + len(entries) + 7  # changelog + 7 inserted paragraphs (entries includes the 12.06 line)
    n1 = len(d.paragraphs)
    if n1 - n0 != added_expected:
        raise BuildError("P&P paragraph count %d -> %d, expected +%d" % (n0, n1, added_expected))
    d.save(PP_OUT)
    print("WROTE", PP_OUT, "paragraphs %d -> %d" % (n0, n1))


# ---------------------------------------------------------------------- Handbook
def build_hb():
    d = docx.Document(HB_SRC)
    n0 = len(d.paragraphs)
    H = "Handbook"

    replace(d, H, "Title page", "Version 2026.7 FINAL — Full Circle Finance",
            "Version 2026.7 FINAL", "Version 2026.8 FINAL", "Version bump")
    replace(d, H, "Title page", "Version 2026.8 FINAL — Full Circle Finance",
            "Effective October 14, 2026", "Effective %s" % DATE, "Version bump")
    replace(d, H, "Acknowledgment of Receipt", "Employee Handbook, version 2026.7, and have read it",
            "version 2026.7", "version 2026.8", "Version bump")

    # a. Hours of Business
    replace(d, H, "Hours of Business", "Store hours are 10:00 a.m. to 6:00 p.m. Culpeper is open",
            "Store hours are 10:00 a.m. to 6:00 p.m. Culpeper is open Monday through Saturday. Harrisonburg, "
            "Waynesboro, Lexington, and Roanoke are open Monday, Tuesday, Thursday, Friday, and Saturday, and are "
            "closed Wednesday. All stores are closed Sunday.",
            "Culpeper, Roanoke, and Waynesboro are open Monday through Saturday: 10:00 a.m. to 6:00 p.m. Monday "
            "through Friday, and 10:00 a.m. to 5:00 p.m. Saturday. Harrisonburg and Lexington are open Monday, "
            "Tuesday, Thursday, Friday, and Saturday, 10:00 a.m. to 6:00 p.m., and are closed Wednesday. Any store "
            "open six days a week closes at 5:00 p.m. on Saturday. All stores are closed Sunday.",
            "CEO rule 2026-10-01; Waynesboro six days from 2026-10-14; P&P v2026.9 §01.01")

    # c. Communication — no HR department
    replace(d, H, "Communication", "If a complaint or problem involves the employee",
            "inform either the next person in the chain of command or Human Resources.",
            "inform the next person in the chain of command (the Market Manager, then the CEO).",
            "Valley Pawn has no HR department; Academy decision 7.3 ('Human Resources' line)")

    # d. Harassment by customers / vendors
    add(d, H, "Reporting Harassment", "Each employee has the responsibility to help keep his or her work environment",
        "Harassment of an employee by a customer, vendor or visitor is reported the same way — to the Store "
        "Manager, the Market Manager or the Owner. The company will act to protect the employee, and management "
        "decides whether that person is welcome back in the store.",
        "Title VII / VHRA employer duty for non-employee harassment (EEOC guidance)")

    # b. Head coverings — already correct
    ALREADY.append((H, "Dress Code — hats and head coverings",
                    "Already allows an approved medical accommodation and a religious head covering (hijab, yarmulke, "
                    "turban). Left as is; it routes the request to 'Human Resources', which the Handbook defines as "
                    "Joshua Davis, rather than the Store Manager.", "Title VII; VHRA"))

    # Changelog — the Handbook has no Changelog section; add one short entry after the title block.
    sub = find_one(d, "Version 2026.8 FINAL — Full Circle Finance")
    head_tpl = find_one(d, "Who to Contact")
    item_tpl = find_one(d, "“Market Manager” means Preston Peters.")
    entries = [
        "Hours of Business — Culpeper, Roanoke and Waynesboro are open Monday–Saturday and close at 5:00 p.m. on "
        "Saturday; Harrisonburg and Lexington stay closed Wednesday.",
        "Communication — a complaint about your supervisor goes to the next person in the chain of command (the "
        "Market Manager, then the CEO); \"or Human Resources\" is removed because Valley Pawn has no HR department.",
        "Reporting Harassment — harassment of an employee by a customer or vendor is reported the same way, and "
        "management decides whether that person is welcome back.",
    ]
    h = insert_after(sub, "What's New in Version 2026.8 (%s) — aligned to the Valley Pawn Academy final review"
                     % DATE, head_tpl)
    last = h
    for e in entries:
        last = insert_after(last, e, item_tpl)
        last.runs[0].bold = False  # template run is a bold defined term; changelog lines are plain
    LOG.append((H, "Changelog (new)", "(no changelog section existed)", "v2026.8 heading + %d lines" % len(entries),
                "This revision"))

    added_expected = 1 + len(entries) + 1
    n1 = len(d.paragraphs)
    if n1 - n0 != added_expected:
        raise BuildError("Handbook paragraph count %d -> %d, expected +%d" % (n0, n1, added_expected))
    d.save(HB_OUT)
    print("WROTE", HB_OUT, "paragraphs %d -> %d" % (n0, n1))


NOTES_MD = """## Assumptions (stated, not asked)

- Effective date for both new versions: October 21, 2026.
- Account-holder verification uses the brief's wording: full name plus one non-public identifier (ticket number, date of birth, or last four of the phone on file). The draft Account Details by Phone & Text card (2026-10) says "full name and date of birth" only. The two don't conflict, since date of birth is one of the accepted identifiers, but the card is narrower. Settle on one wording before the card goes out.
- Counterfeit-bill rule placed in 02.04 Cash Drawers. v2026.8 had no counterfeit text anywhere in Section 2.
- Police-caller and background-check phone rules placed in 07.03 Telephone Etiquette, not 01.06, because 01.06 covers people who come into the store.
- Gift rule placed as a new paragraph right after the prohibited-purchasers list in 05.02. That is the only place "straw" appears in the manual.
- Customer photo: v2026.8 required a photo only when military ID is presented. "A customer photo is taken on every intake" was added per Academy default D8.
- The 3310.4 log line in 03.08 ("two or more firearms within a five-day period") restated the rule wrongly, so it was corrected to handguns and five consecutive business days.
- 12.02 Closing Time restated store hours and was updated to match. "Do not stay past 6:30 PM" became "not more than 30 minutes past closing" so it holds on 5 PM Saturdays.
- The Handbook had no Changelog section. A short "What's New in Version 2026.8" block was added under the title, using the Handbook's own heading and list styles.
- Handbook "Human Resources": only the Communication complaint-routing line was changed, as directed. Other mentions were left alone because "Who to Contact" defines "Human Resources" as Joshua Davis.
- At-will and Protected Rights text is untouched in both manuals.

## Follow-up applied 2026-10-21 (same day)

- 12.06 Assault Firearm Classification: "magazine-capacity limits still apply" removed and the enjoined-ban statement added (rows above). One line was added to the v2026.9 changelog.
- `Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04_Rev2.docx/.pdf` built from HR-2026-04. Only the effective date and the two version lines changed (Handbook v2026.8 and P&P v2026.9, effective October 21, 2026). It has NOT been sent; the original HR-2026-04 is untouched.
- #ask-handbook renamed: the only place "#ask-handbook" or any "handbook bot/assistant" wording appeared in the three new documents was Section 1 of the Rev2 acknowledgment. It now reads "of Goldilocks in the #ask-goldilocks Slack channel" (row above). Searched P&P v2026.9 and Handbook v2026.8, including tables, and found no other mentions. Note: `Ask_Handbook/build_sources.py` still writes a header that names the #ask-handbook responder. That is automation code, not a policy document, so it was not changed.

## Items that could not be placed

- None. Every listed item (P&P 1-13, Handbook a-d) was placed or confirmed already correct.

## Noticed, out of scope, not changed

- The Handbook's head-covering exception sends the request to "Human Resources" (Joshua), not the Store Manager. Left as is because the allowance is already there.
- Wording difference, NOT edited: the draft Account Details by Phone & Text card (`Account_Details_Phone_Text_Policy_2026-10.docx`) says account details go out only after the customer gives their "full name and date of birth". P&P v2026.9 §08.02 (and the Academy) accept full name plus ONE of ticket number, date of birth, or last four of the phone on file. The card is narrower. Joshua should pick one wording before the card is sent; the card file was left untouched.
- The v2026.7 changelog entry ("only Culpeper is Monday-Saturday") is history and was left as written.
- The Handbook has a duplicate internal bookmark ("unpaid-personal-and-medical-leave"). It was already in v2026.7 and is harmless.

## Verification

- Paragraph counts: P&P 767 -> 790 (+23: changelog heading, 15 changelog lines, 7 new policy paragraphs). Handbook 400 -> 405 (+5: changelog heading, 3 lines, 1 new harassment paragraph). Every other paragraph is identical to the source (paragraph-level diff).
- Source files v2026.8 P&P and v2026.7 Handbook (.docx and .pdf): checksums unchanged before and after the build.
- PDFs exported with LibreOffice. Title page, changelog page and 01.01 hours page were rendered and checked (P&P 57 pages, Handbook 37 pages).
- Ask_Handbook/build_sources.py: exit 0. SOURCES_CURRENT.md now names P&P v2026.9 and Employee Handbook v2026.8 and contains the new hours text.
"""


ACK_SRC = os.path.join(HERE, "Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04.docx")
ACK_OUT = os.path.join(HERE, "Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04_Rev2.docx")


def build_ack():
    """Copy HR-2026-04 and change ONLY the version references and the effective date."""
    d = docx.Document(ACK_SRC)
    n0 = len(d.paragraphs)
    A = "Acknowledgment HR-2026-04 Rev2"
    replace(d, A, "Header", "Policy No. HR-2026-04  ·  Effective September 23, 2026",
            "Effective September 23, 2026", "Effective %s" % DATE, "New versions issued")
    replace(d, A, "Section 1", "Valley Pawn Employee Handbook, version 2026.4 FINAL",
            "version 2026.4 FINAL, effective September 23, 2026", "version 2026.8 FINAL, effective %s" % DATE,
            "Handbook v2026.8")
    replace(d, A, "Section 1", "Valley Pawn Policies & Procedures Manual, version 2026.8 FINAL",
            "version 2026.8 FINAL, effective September 23, 2026", "version 2026.9 FINAL, effective %s" % DATE,
            "P&P v2026.9")
    replace(d, A, "Section 1", "in the #ask-handbook Slack channel",
            "in the #ask-handbook Slack channel", "of Goldilocks in the #ask-goldilocks Slack channel",
            "#ask-handbook retired; replaced by Goldilocks in #ask-goldilocks (Academy blocker 4; coordinator 2026-10-21)")
    if len(d.paragraphs) != n0:
        raise BuildError("acknowledgment paragraph count changed")
    d.save(ACK_OUT)
    print("WROTE", ACK_OUT, "paragraphs %d -> %d" % (n0, len(d.paragraphs)))


def md_cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def write_changes():
    L = []
    L.append("# P&P v2026.9 and Employee Handbook v2026.8 — change record")
    L.append("")
    L.append("Built %s by `_build_pp_v2026.9_handbook_v2026.8.py` from `Valley_Pawn_PP_Manual_v2026.8_FINAL.docx` "
             "and `Employee_Handbook_v2026.7_FINAL.docx` (both left untouched). Driver: Valley Pawn Academy final "
             "pre-launch review, 2026-10-20/21 (`Training Program/academy/FINAL_PRELAUNCH_REVIEW_2026-10-20.md`, "
             "board reports A1/A2)." % DATE)
    L.append("")
    L.append("Status: built, NOT distributed. No Gusto signature request, Slack post or email has been sent.")
    L.append("")
    L.append("## Changes")
    L.append("")
    L.append("| # | Manual | Section | Old text | New text | Source / citation |")
    L.append("|---|---|---|---|---|---|")
    for i, (doc, sec, old, new, src) in enumerate(LOG, 1):
        L.append("| %d | %s | %s | %s | %s | %s |" % (i, doc, md_cell(sec), md_cell(old), md_cell(new), md_cell(src)))
    L.append("")
    L.append("## Already correct — verified, left as is")
    L.append("")
    for doc, sec, what, src in ALREADY:
        L.append("- **%s %s** — %s%s" % (doc, sec, what, (" (%s)" % src) if src else ""))
    L.append("")
    with open(CHANGES_MD, "w") as f:
        f.write("\n".join(L) + "\n" + NOTES_MD)


def main():
    for p in (PP_OUT, HB_OUT, ACK_OUT):
        if os.path.exists(p) and "--overwrite" not in sys.argv:
            print("REFUSING: %s exists (pass --overwrite to rebuild it)" % p)
            return 1
    try:
        build_pp()
        build_hb()
        build_ack()
    except BuildError as e:
        print("BUILD ABORTED, nothing more written:", e)
        return 2
    write_changes()
    print("%d changes logged, %d already-correct notes" % (len(LOG), len(ALREADY)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
