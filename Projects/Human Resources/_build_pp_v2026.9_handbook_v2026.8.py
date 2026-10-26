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
      python3 _build_pp_v2026.9_handbook_v2026.8.py --ceo-20261025   (second stage: CEO decisions 2026-10-25,
      applied in place to the FINAL files from their _backups/*.bak-20261025-ceo copies; see that section)
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



# =========================================================================================
# CEO DECISIONS 2026-10-25 — second stage, revises the built FINAL files IN PLACE.
#
#   python3 _build_pp_v2026.9_handbook_v2026.8.py --ceo-20261025
#
# Source = the pre-decision copies in _backups/*.bak-20261025-ceo (the FINAL files as they stood on
# 2026-10-25, including the 2026-10-21 "kpirights" bonus edits that were made after the first stage).
# Re-running is idempotent: it always starts again from those backups. Version numbers are unchanged
# (P&P v2026.9, Handbook v2026.8, HR-2026-04 Rev2); effective date becomes Policy Day, Nov 4, 2026.
# Changes are logged to PP_v2026.9_CHANGES.md under "CEO decisions 2026-10-25" (section replaced on re-run).
# =========================================================================================
import re as _re

CEO_DATE = "October 25, 2026"
EFFECTIVE = "November 4, 2026"
BAK_DIR = os.path.join(HERE, "_backups")
CEO_LOG = []
SRC_CEO = "CEO decisions 2026-10-25"


def _bak(name):
    p = os.path.join(BAK_DIR, name + ".bak-20261025-ceo")
    if not os.path.exists(p):
        raise BuildError("missing pre-decision backup: " + p)
    return p


def _all_paragraphs(doc):
    seen = set()
    out = []
    def visit(paras):
        for p in paras:
            if id(p._p) not in seen:
                seen.add(id(p._p)); out.append(p)
    visit(doc.paragraphs)
    def tables(ts):
        for t in ts:
            for row in t.rows:
                for c in row.cells:
                    visit(c.paragraphs); tables(c.tables)
    tables(doc.tables)
    for s in doc.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            try:
                visit(part.paragraphs); tables(part.tables)
            except Exception:
                pass
    return out


def sub_runs(p, pattern, repl, flags=0):
    """Regex substitution across a paragraph's runs, keeping every run's formatting: text replaced
    inside one run stays in that run; a match spanning runs is written into the first run touched."""
    runs = p.runs
    text = "".join(r.text for r in runs)
    ms = list(_re.finditer(pattern, text, flags))
    for m in reversed(ms):
        new = repl(m) if callable(repl) else m.expand(repl)
        s, e = m.start(), m.end()
        pos = 0
        first = True
        for r in runs:
            t = r.text; a, b = pos, pos + len(t); pos = b
            if b <= s or a >= e:
                continue
            ls, le = max(s, a) - a, min(e, b) - a
            if first:
                r.text = t[:ls] + new + t[le:]; first = False
            else:
                r.text = t[:ls] + t[le:]
            if b >= e:
                break
    return len(ms)


def gsub(doc, docname, pattern, repl, label, flags=0):
    n = 0
    for p in _all_paragraphs(doc):
        n += sub_runs(p, pattern, repl, flags)
    if n:
        CEO_LOG.append((docname, "All sections (global)", label, "%d replacement(s)" % n, SRC_CEO))
    return n


def rsub(doc, docname, section, needle, old, new, source=SRC_CEO):
    """Needle-located, run-preserving single replacement (old must occur once in that paragraph)."""
    p = find_one(doc, needle)
    if p.text.count(old) != 1:
        raise BuildError("old text found %d times in %s: %r" % (p.text.count(old), section, old))
    sub_runs(p, _re.escape(old), lambda m: new)
    CEO_LOG.append((docname, section, old, new, source))
    return p


def cadd(doc, docname, section, anchor_needle, text, source=SRC_CEO, template_needle=None):
    anchor = find_one(doc, anchor_needle)
    tpl = find_one(doc, template_needle) if template_needle else None
    p = insert_after(anchor, text, tpl)
    CEO_LOG.append((docname, section, "(new paragraph)", text, source))
    return p


def cdel(doc, docname, section, needle, source=SRC_CEO):
    p = find_one(doc, needle)
    old = p.text
    p._p.getparent().remove(p._p)
    CEO_LOG.append((docname, section, old, "(paragraph removed)", source))


NAME_SUBS = [  # (pattern, replacement) — most specific first; applied to P&P, Handbook and acknowledgment
    (r"Approved by: Joshua Davis \(CEO\) · Preston Peters \(Market Manager\)", "Approved by: CEO · Market Manager"),
    (r"the Market Manager, CEO \(Joshua Davis\), and Joshua Davis \(CEO\) numbers", "the Market Manager's and the CEO's numbers"),
    (r"(personnel file) with Preston Peters", r"\1"),
    (r"Preston Peters \(Market Manager\) — or, if he cannot be reached, to Joshua Davis \(CEO\)",
     "the Market Manager — or, if the Market Manager cannot be reached, to the CEO"),
    (r"Owner: Joshua Davis / Preston Peters\.", "Owner: CEO and Market Manager."),
    (r"Owner: Joshua Davis\.", "Owner: CEO."),
    (r"\(Joshua Davis, ", "(CEO, "),
    (r"\(Joshua Davis\)", "(CEO)"),
    (r"by Preston Peters, Market Manager,", "by the Market Manager,"),
    (r"Joshua Davis's \(CEO\)", "the CEO's"),
    (r"Joshua Davis \(CEO\)", "the CEO"),
    (r"Joshua Davis, Chief Executive Officer", "the Chief Executive Officer (CEO)"),
    (r"Market Manager \(Preston Peters\)", "Market Manager"),
    (r"CEO \(Joshua Davis\)", "CEO"),
    (r"Owner \(Joshua Davis\)", "CEO"),
    (r"Preston Peters \(Market Manager\)", "the Market Manager"),
    (r"Preston Peters, Market Manager,", "the Market Manager,"),
    (r"Preston Peters or Joshua Davis", "the Market Manager or the CEO"),
    (r"Preston Peters and Joshua Davis", "the Market Manager and the CEO"),
    (r"Joshua Davis or Preston Peters", "the CEO or the Market Manager"),
    (r"Joshua Davis and Preston Peters", "the CEO and the Market Manager"),
    (r"Joshua Davis's", "the CEO's"),
    (r"Joshua Davis", "the CEO"),
    (r"Hillary Davis", "management"),
    (r"Preston Peters", "the Market Manager"),
    (r"\bPreston\b", "the Market Manager"),
    (r"\bJoshua\b", "the CEO"),
    (r"\bthe Owner\b", "the CEO"),
]
TITLE_SUBS = [  # Gusto titles: Manager, Sales and Loan Associate, Sales and Loan Representative, Market Manager, CEO
    (r"\bStore Managers\b", "Managers"),
    (r"\bStore Manager's\b", "Manager's"),
    (r"\bStore Manager\b", "Manager"),
    (r"\bstore managers\b", "Managers"),
    (r"\bstore manager's\b", "Manager's"),
    (r"\bstore manager\b", "Manager"),
    (r"\bSales Associates\b", "Sales and Loan Associates and Sales and Loan Representatives"),
]
GRACE_SUBS = [  # the statutory window is the "15-day legal hold (Va. Code § 54.1-4005)"; never "grace"
    (r"REDEEMING DURING THE GRACE PERIOD", "REDEEMING DURING THE 15-DAY LEGAL HOLD"),
    (r"15-day legal grace period", "15-day legal hold"),
    (r"15-day grace period", "15-day legal hold"),
    (r"the grace period is 15 days", "the legal hold is 15 days (Va. Code § 54.1-4005)"),
    (r"grace-period charge", "legal-hold charge"),
    (r"during the grace period", "during the 15-day legal hold"),
    (r"enters the grace period", "enters the 15-day legal hold (Va. Code § 54.1-4005)"),
    (r"statutory holding and grace periods", "loan term and the 15-day legal hold"),
]
CLEAN_SUBS = [
    (r"\bthe the\b", "the"),
    (r"\b([Yy]our|a|an) the (CEO|Market Manager)\b", r"\1 \2"),
    (r"(^|[.!?]\s+|[“‘]\s*)the (CEO|Market Manager|Chief Executive Officer)\b",
     lambda m: m.group(1) + "The " + m.group(2)),
]


def _global_pass(d, docname):
    for pat, rep in NAME_SUBS:
        gsub(d, docname, pat, rep, "names → roles: /%s/" % pat)
    for pat, rep in TITLE_SUBS:
        gsub(d, docname, pat, rep, "titles per Gusto: /%s/" % pat)
    for pat, rep in GRACE_SUBS:
        gsub(d, docname, pat, rep, "'grace' → 15-day legal hold: /%s/" % pat)
    for pat, rep in CLEAN_SUBS:
        gsub(d, docname, pat, rep, "wording clean-up: /%s/" % pat)


LADDER = ("DISCOUNTS — ONE RULE, BY THE ITEM'S AGE AND YOUR ROLE. The most any item may be discounted is set by its age "
          "in Bravo: up to 30 days old, 10%; 31–60 days, 15%; 61–90 days, 20%; 91–180 days, 30%; 181 days to one year, "
          "40%; over one year, 50%. Within that ladder, a Sales and Loan Associate or Sales and Loan Representative may "
          "give up to 30% (10% is the normal give). A discount of 31% to 50% needs the Manager's approval on the ticket. "
          "No item is ever sold at more than a 50% discount. A discount deeper than the ladder allows for the item's age "
          "needs the Manager's approval and the reason on the ticket, and it is reviewed on the daily discount review.")

GUN_CERT = ("GUN SAFETY CERTIFICATE REQUIREMENT — A CONDITION OF EMPLOYMENT (Firearm Safety Certification policy HR-2026-05). "
            "Every employee (1) completes the free Basic Gun Safety 101 online class at GunSafety.co, (2) obtains the $25 "
            "Certificate of Completion, and (3) submits the certificate PDF by uploading it to Gusto under Documents and "
            "telling their Manager the same day. A new hire finishes all three steps by the end of their THIRD CALENDAR DAY "
            "of employment (the first day worked is day one); an employee who has not finished by then has their employment "
            "end at that point. Every employee recertifies once each calendar year, by January 31. The class and certificate "
            "are completed at the store during scheduled working hours and are paid at the employee's regular rate. The "
            "Company pays the $25 certificate fee, either directly or by reimbursing the employee on submission of the "
            "certificate; it is never deducted from pay. The only extension is one the CEO grants in writing, and only "
            "where the Company caused the delay (no working device, no internet access at the store, or no paid time "
            "scheduled for the class); no manager may extend the deadline. Employees under 18 may not handle firearms or "
            "work the sales floor and are excluded while that remains true.")


def ceo_pp():
    src = _bak("Valley_Pawn_PP_Manual_v2026.9_FINAL.docx")
    d = docx.Document(src)
    n0 = len(d.paragraphs)
    P = "P&P"
    # Title page
    rsub(d, P, "Title page", "Prepared: July 8, 2026", "Updated: October 21, 2026 (v2026.9)",
         "Updated: %s (v2026.9)  ·  Effective %s" % (CEO_DATE, EFFECTIVE))
    # History line that named retired roles
    rsub(d, P, "Changelog (v2026.4)", "Roles and systems — references to Division Managers",
         "references to Division Managers, Region Managers, Home Office, a Human Resources department, a Director of "
         "Operations and a Chief Operating Officer are replaced with the actual chain: Store Manager to Preston Peters "
         "(Market Manager) to Joshua Davis (CEO).",
         "references to roles the Company does not have are replaced with the actual chain: Manager to Market Manager "
         "to CEO.")
    # v2026.9 changelog lines brought into line with the decisions (this version has not been distributed)
    rsub(d, P, "Changelog (v2026.9)", "Default timeline (06.01) — Day 1 past due is the day after",
         "nothing is pulled, priced or sold before the 15-day grace period ends (day 45 of the loan).",
         "nothing is pulled, priced or sold before the 15-day legal hold (Va. Code § 54.1-4005) ends (day 45 of the "
         "loan). The late fee applies on the 6th day past due. Customers hear: \"Your loan is due on its due date.\"")
    rsub(d, P, "Changelog (v2026.9)", "Account details (08.02) — adopts the account-holder-only rule",
         "account details go only to the verified account holder (name plus ticket number, date of birth or last four "
         "of the phone on file); a spouse or attorney is no longer an exception.",
         "account details go only to the verified account holder (full name, date of birth and the phone number on "
         "file — all three) or to someone with a signed power of attorney on file; no spouse, relative, friend or "
         "attorney exception; a firearm is never confirmed by phone (also 03.09).")
    rsub(d, P, "Changelog (v2026.9)", "Discounts (05.03) — 31% to 50% needs",
         "Discounts (05.03) — 31% to 50% needs the Store Manager's approval on the ticket; never past 50%.",
         "Discounts (05.03) — one rule: the age ladder (10% up to 30 days … 50% over a year) sets the most off; "
         "associates up to 30%; 31% to 50% needs the Manager's approval on the ticket; never past 50%.")
    rsub(d, P, "Changelog (v2026.9)", "Returns and warranty (05.08) — the warranty needs",
         "returns need the receipt and original condition;",
         "a return needs that same account with an email on file (no email, no return), the receipt and original "
         "condition;")
    rsub(d, P, "Changelog (v2026.9)", "Monthly bonus (01.08) — from the December 2026 bonus month",
         "the CEO approves every bonus;", "management approves every bonus;")

    # 01.02 — call-outs, Market Manager contact, training at the store
    a = cadd(d, P, "01.02 Scheduling", "Schedules are set by the Store Manager to match store volume",
             "CALL-OUTS. An employee who cannot work a scheduled shift, or will be late, calls the Market Manager by "
             "VOICE CALL at the Market Manager's Zoom number, 540-202-4200, at least two (2) hours before the shift "
             "starts. Only a voice call counts: a text, a Slack message, an email or a message passed through a co-worker "
             "is not a call-out. The full attendance rules are in the Employee Handbook (Attendance and Punctuality).")
    cadd(d, P, "01.02 Scheduling", "CALL-OUTS. An employee who cannot work a scheduled shift",
         "CONTACTING THE MARKET MANAGER. Messages to the Market Manager go through Slack. Calls go to the Market "
         "Manager's Zoom number, 540-202-4200.")
    cadd(d, P, "01.02 Scheduling", "CONTACTING THE MARKET MANAGER. Messages to the Market Manager",
         "TRAINING HAPPENS AT THE STORE. All required training — Valley Pawn Academy lessons, the gun-safety course "
         "(Section 10.06) and any other assigned training — is done at the store, during business hours, on the clock, "
         "at the employee's normal rate of pay. No training is done at home or off the clock. An employee running "
         "behind a training due date tells their Manager that day.")
    # 01.03 staffing / titles
    rsub(d, P, "01.03 Employee Staffing", "Each pawnshop is staffed with one full-time Manager and a Pawnbroker",
         "one full-time Manager and a Pawnbroker,",
         "one full-time Manager and a Sales and Loan Associate or Sales and Loan Representative,")
    cadd(d, P, "01.03 Employee Staffing", "Each pawnshop is staffed with one full-time Manager",
         "Job titles are the ones in Gusto: Sales and Loan Associate, Sales and Loan Representative, Manager (one per "
         "store), Market Manager (all five stores) and CEO. There are no assistant managers.")
    # 01.08 bonus approval
    rsub(d, P, "01.08 Monthly Bonus Program", "Every bonus is approved by the CEO before payroll",
         "Every bonus is approved by the CEO before payroll", "Every bonus is approved by management before payroll")
    # pronoun / "owner" leftovers that named the CEO
    rsub(d, P, "04.04 Vehicles", "EVERY title pawn — at any dollar amount", "referred to him", "referred to the CEO")
    rsub(d, P, "02.03 Bank Withdrawals", "High-volume days may require additional withdrawals",
         "make the request to the owner", "make the request to the CEO")
    # 01.10 — remove personal quote
    cdel(d, P, "01.10 Prohibited Lending", "\"Reminder, All employee/Family transactions must be approved by me.\"")
    # 03.09 — account details
    cadd(d, P, "03.09 Confidentiality", "Due to the confidential nature of customer information, customer information may not",
         "ACCOUNT DETAILS — VERIFIED ACCOUNT HOLDER ONLY. Account details (balance, payoff, items, due date, or whether "
         "a loan exists) go only to the verified account holder — full name, date of birth AND the phone number on file, "
         "all three matching Bravo — or to a person whose signed power of attorney for the customer is on file. There is "
         "no exception for a spouse, relative, friend or attorney without a power of attorney on file. Never confirm a "
         "firearm by phone — whether we have it, whether it is on a loan, or whose it is — even to a verified caller. "
         "See Section 08.02.")
    # 04.03 — remove personal quote
    cdel(d, P, "04.03 Precious Metals Melt", "\"I sent out another policy that needs a signature on gusto for precious metals")
    # 05.0 late fee
    rsub(d, P, "05.0 Charges — Late fee", "4. LATE FEE (Va. Code § 54.1-4009(C)(2))",
         "Up to 10% of the amount loaned, for each item not claimed by the pledged date.",
         "Up to 10% of the amount loaned on the item. The late fee applies on the 6TH DAY PAST DUE (day 1 past due is "
         "the day after the due date).")
    # 05.01
    rsub(d, P, "05.01 Pawn Transactions", "All pawn transactions are thirty (30) day loans.",
         "the flat 12.5% figure used in earlier editions is withdrawn.",
         "the flat 12.5% figure used in earlier editions is withdrawn. If a customer asks how long the Company will "
         "hold the item, the answer is: \"Your loan is due on its due date.\" (Section 06.01).")
    rsub(d, P, "05.01 Pawn Transactions", "Each item on pawn may only have one loan on it at a time.",
         "applies to an item not claimed by the pledged date,", "applies on the 6th day past due,")
    # 05.03 discount ladder
    rsub(d, P, "05.03 Sell Transactions", "Items purchased from customers or pulled from inventory (PFI) are sold",
         "Associates may discount up to 30% of the listed price (10% is the normal give). A discount of 31% to 50% needs "
         "the Store Manager's approval on the ticket. No item is ever sold at more than a 50% discount.", LADDER)
    # 05.08 returns / warranty
    rsub(d, P, "05.08 Refunds", "30-day return window from date of purchase for most retail items",
         "a return needs the receipt and the item in original condition.",
         "a return needs a customer account with an email address on file (the warranty sign-up), the receipt, and the "
         "item in original condition. No email on file means the customer is not signed up, and there is no return.")
    rsub(d, P, "05.08 Refunds", "30-day warranty: everything we sell carries",
         "no email, no warranty. A return does not depend on an email; it depends on the receipt and the item's condition.",
         "no email, no warranty and no return.")
    # 05.04 payments toward principal (CEO correction 2026-10-25: "customers can make partial payments towards
    # principal", read with the Market Manager's 10/23 answer that nothing smaller than the extension is taken)
    cadd(d, P, "05.04 Refinances / Redemptions", "Employees should always offer the refinance option so the customer knows",
         "PAYMENTS AND PRINCIPAL. The minimum payment on a loan is the refinance (the extension): the current charges, "
         "which start a new 30-day term. A customer may pay more than the refinance amount; the extra is applied to "
         "principal, which lowers the loan amount and the next month's charges. Payments toward principal are taken in "
         "the store, and the new balance is quoted only once Bravo shows it. A payment smaller than the refinance amount "
         "is not accepted. Redemption (the payoff) pays the loan in full and the item goes home with the customer. The "
         "MobilePawn app takes refinance (extension) payments only, by debit card ($1.99 per payment); payoffs and "
         "payments toward principal are taken in the store. A card number is never taken by phone.",
         source="CEO correction 2026-10-25 ('customers can make partial payments towards principal'); Market Manager "
                "2026-10-23 (no payment smaller than the extension; app: debit only, extensions only, $1.99)")
    # 06.01
    rsub(d, P, "06.01 Pull for Inventory", "DEFAULT AND PULL — THE CONTROLLING TIMELINE",
         "Day 1 past due is the day after the loan due date.",
         "Day 1 past due is the day after the loan due date. The late fee (Section 05.0) applies on the 6th day past due.")
    rsub(d, P, "06.01 Pull for Inventory", "CHANGE EFFECTIVE OCTOBER 1, 2026.",
         "Joshua Davis (CEO), 2026-08-13: 'October 1st, the 75 day rule goes away, meaning we won't hold anything past "
         "then.' From October 1 the 75-day tolerance ends:",
         "From October 1 the 75-day tolerance ends (CEO decision, August 13, 2026):")
    rsub(d, P, "06.01 Pull for Inventory", "CHANGE EFFECTIVE OCTOBER 1, 2026.",
         "are marked expired in Bravo as soon as they are past due,", "are marked expired in Bravo at once,")
    cadd(d, P, "06.01 Pull for Inventory", "CHANGE EFFECTIVE OCTOBER 1, 2026.",
         "WHAT CUSTOMERS HEAR. This timeline is for staff only and is always read from Bravo. When a customer asks how "
         "long the Company will hold an item or how much time they have, the answer is: \"Your loan is due on its due "
         "date.\" Never describe the 15-day legal hold or the pull timeline to a customer, never promise a hold, and "
         "never give a date or a fee that was not read from Bravo.")
    # 08.02 account details
    rsub(d, P, "08.02 FDCPA — Disinterested Third Parties", "Account details go only to the verified account holder: the customer gives",
         "Account details go only to the verified account holder: the customer gives their full name plus one non-public "
         "identifier — the ticket number, their date of birth, or the last four digits of the phone number on file. "
         "Anyone else — a spouse, relative, friend or attorney included — is a disinterested third party: never divulge "
         "account details or request payment from such a party. That person comes in with ID and the ticket, or the "
         "customer calls.",
         "Account details go only to the verified account holder — the customer gives their full name, date of birth AND "
         "the phone number on file, and all three must match Bravo — or to a person whose signed power of attorney for "
         "the customer is on file. A ticket number or the last four of a phone is not enough. Anyone else — a spouse, "
         "relative, friend or attorney without a power of attorney on file — is a disinterested third party: never "
         "divulge account details or request payment from such a party. If a caller can't verify, say: \"I can't go "
         "over account details on the phone, but come in with your ID and we'll take care of it.\" Never confirm a "
         "firearm by phone — whether we have it, whether it is on a loan, or whose it is — even to a verified caller.")
    # 10.06 gun-safety certificate (HR-2026-05 in the P&P)
    rsub(d, P, "10.06 Firearm Handling — fee", "THE COMPANY PAYS — NO EMPLOYEE OUT-OF-POCKET COST.",
         "The Company purchases the certificate directly. Employees are not asked to pay the fee and seek reimbursement. "
         "Earlier instructions to 'select the $25 version of the course' and claim petty-cash reimbursement are withdrawn "
         "— they no longer describe a product that exists, and requiring an employee to front a job-related cost can "
         "unlawfully reduce pay below minimum wage in the week it is incurred.",
         "The Company pays the $25 certificate fee, either directly or by reimbursing the employee on submission of the "
         "certificate (HR-2026-05 Section 4); it is never deducted from pay. Earlier instructions to 'select the $25 "
         "version of the course' are withdrawn — that product no longer exists.")
    rsub(d, P, "10.06 Firearm Handling — verification", "VERIFICATION. Certificates are unique per student",
         "Preston Peters verifies each certificate at the provider rather than accepting a printout, and files the "
         "verification record in the employee's personnel file with Preston Peters.",
         "The Market Manager verifies each certificate at gunsafety.co/verify rather than accepting a printout and "
         "records the holder's name, certificate number and completion date; the verified certificate is kept in the "
         "employee's Gusto Documents and personnel file.")
    p = find_one(d, "Completion deadline and recertification: a new hire completes the course")
    old = p.text
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = GUN_CERT
    CEO_LOG.append((P, "10.06 Gun Safety Certificate Requirement", old, GUN_CERT, "HR-2026-05 §§3–7; " + SRC_CEO))
    # Glossary
    p = find_one(d, "Grace Period: the 15-day statutory period")
    old = p.text
    sub_runs(p, _re.escape(old), lambda m: (
        "15-Day Legal Hold (Va. Code § 54.1-4005): the 15 days after a loan's term during which, by law, the item may "
        "not be sold. It is never described to customers — a loan is due on its due date. Company practice holds items "
        "longer — see Section 06.01."))
    CEO_LOG.append((P, "11.01 Glossary", old, p.text, SRC_CEO))
    # 12.01 team meetings → weekly Slack huddle
    rsub(d, P, "12.01 Team Meetings", "Team meetings are held on the first and third Monday",
         "Team meetings are held on the first and third Monday of each month at 9:00 AM by Zoom from each store. Every "
         "employee scheduled that morning attends; meeting time is paid working time. The Market Manager announces any "
         "change to the schedule in Slack.",
         "The team huddle is held in Slack every week, on Mondays, in the #monday-meetings channel. Every employee reads "
         "it and takes part during their shift; huddle time is paid working time. The Market Manager posts any change to "
         "the schedule in Slack.")

    _global_pass(d, P)

    # Changelog — revision note under the v2026.9 block
    anchor = find_one(d, "Because this revision changes existing rules, a new signed Employee Handbook & P&P Acknowledgment (HR-2026-04) is issued with this version")
    head_tpl = find_one(d, "What's New in Version 2026.9 (")
    entries = [
        "Loans (05.0, 05.01, 06.01, glossary) — the late fee applies on the 6th day past due; the statutory window is "
        "called the 15-day legal hold (Va. Code § 54.1-4005); customers hear \"Your loan is due on its due date.\"",
        "Account details (03.09, 08.02) — full name, date of birth and phone number on file (all three), or a signed "
        "power of attorney on file; never confirm a firearm by phone.",
        "Payments (05.04) — the minimum payment is the refinance (extension); a customer may pay more, in the store, "
        "and the extra goes toward principal; a payment smaller than the refinance is not accepted; the app takes "
        "extensions only.",
        "Discounts (05.03) — the age ladder is policy, combined with the 30% / 31–50% Manager / 50% cap bands.",
        "Returns (05.08) — a return needs an account with an email on file; no email, no return.",
        "Call-outs, Market Manager contact and training at the store (01.02); job titles per Gusto (01.03).",
        "Gun Safety Certificate Requirement (10.06) — HR-2026-05 written into this manual, including the "
        "reimbursement rule.",
        "Bonuses (01.08) — management approves every bonus. Weekly team huddle in Slack (12.01). Personal names "
        "replaced by roles throughout.",
    ]
    h = insert_after(anchor, "Revised %s (CEO decisions) — effective %s with the November Policy Update" % (CEO_DATE, EFFECTIVE), head_tpl)
    last = h
    for e in entries:
        last = insert_after(last, e, anchor)
    CEO_LOG.append((P, "Changelog", "(new entry)", "CEO-decisions heading + %d lines" % len(entries), SRC_CEO))
    d.save(PP_OUT)
    print("WROTE", PP_OUT, "paragraphs %d -> %d" % (n0, len(d.paragraphs)))


def ceo_hb():
    d = docx.Document(_bak("Employee_Handbook_v2026.8_FINAL.docx"))
    n0 = len(d.paragraphs)
    H = "Handbook"
    rsub(d, H, "Title page", "Version 2026.8 FINAL — Full Circle Finance", "Effective October 21, 2026",
         "Effective %s" % EFFECTIVE)
    rsub(d, H, "Who to Contact", "“Human Resources” or “HR” means Joshua Davis",
         "goes to him directly", "goes to the CEO directly")
    rsub(d, H, "Who to Contact", "“Human Resources” or “HR” means Joshua Davis",
         "who will bring it to him", "who will bring it to the CEO")
    rsub(d, H, "Who to Contact", "“Market Manager” means Preston Peters.", "means Preston Peters.",
         "means the manager over all five stores. Messages to the Market Manager go through Slack; calls go to the "
         "Market Manager's Zoom number, 540-202-4200.")
    rsub(d, H, "Who to Contact", "“Store Manager” means the manager of the store where you work.",
         "the manager of the store where you work.",
         "the manager of the store where you work. Job titles are the ones in Gusto: Sales and Loan Associate, Sales "
         "and Loan Representative, Manager, Market Manager and CEO.")
    rsub(d, H, "Attendance and Punctuality — Calling in", "Calling in. If you cannot report for a scheduled shift",
         "you must call Preston Peters, Market Manager, by telephone at the number provided to you at hire, at least two "
         "(2) hours before the shift starts. A phone call is the only accepted method. Text messages, emails, Slack "
         "messages, and messages passed through co-workers do not count. If the call is not answered, leave a voicemail "
         "and keep calling until you reach him; a voicemail alone is not a completed call-in unless he confirms it.",
         "you must call the Market Manager by voice call at the Market Manager's Zoom number, 540-202-4200, at least two "
         "(2) hours before the shift starts. A voice call is the only accepted method. Text messages, emails, Slack "
         "messages, and messages passed through co-workers do not count. If the call is not answered, leave a voicemail "
         "and keep calling until you reach the Market Manager; a voicemail alone is not a completed call-in unless the "
         "Market Manager confirms it.")
    cadd(d, H, "Time Tracking — Training", "Each employee is responsible for accurately recording his or her time worked.",
         "Training happens at the store. All required training — Valley Pawn Academy lessons, the gun-safety certificate "
         "course and any other assigned training — is done at the store, during business hours, on the clock, at your "
         "normal rate of pay. Never at home or off the clock. If you are running behind a training due date, tell your "
         "Manager that day.")
    cadd(d, H, "Communication — huddle and contact", "In addition to the exchanges of information and expression of ideas",
         "Every week the team huddle is held in Slack, on Mondays, in the #monday-meetings channel; read it and take part "
         "during your shift (paid time). Messages to the Market Manager go through Slack; calls go to the Market "
         "Manager's Zoom number, 540-202-4200. A call-out is always a voice call (see Attendance and Punctuality).")
    rsub(d, H, "Chain of Command", "Sales Associates report to the Store Manager.",
         "Sales Associates report to the Store Manager. Store Managers report to the Market Manager (Preston Peters). "
         "The Market Manager reports to the Owner (Joshua Davis).",
         "Sales and Loan Associates and Sales and Loan Representatives report to their store's Manager. Managers report "
         "to the Market Manager. The Market Manager reports to the CEO.")

    _global_pass(d, H)

    anchor = find_one(d, "Bonus Pay — starting with the December 2026 bonus month")
    head_tpl = find_one(d, "What's New in Version 2026.8 (")
    entries = [
        "Who to Contact and Chain of Command — roles, not names; job titles as in Gusto (Sales and Loan Associate, "
        "Sales and Loan Representative, Manager, Market Manager, CEO).",
        "Attendance — a call-out is a voice call to the Market Manager's Zoom number, 540-202-4200, at least two hours "
        "before the shift; texts and Slack messages don't count.",
        "Communication — weekly team huddle in Slack (#monday-meetings); messages to the Market Manager by Slack, calls "
        "to 540-202-4200.",
        "Training — all training is done at the store, on the clock; never at home.",
    ]
    h = insert_after(anchor, "Revised %s (CEO decisions) — effective %s with the November Policy Update" % (CEO_DATE, EFFECTIVE), head_tpl)
    last = h
    for e in entries:
        last = insert_after(last, e, anchor)
    CEO_LOG.append((H, "What's New", "(new entry)", "CEO-decisions heading + %d lines" % len(entries), SRC_CEO))
    d.save(HB_OUT)
    print("WROTE", HB_OUT, "paragraphs %d -> %d" % (n0, len(d.paragraphs)))


def ceo_ack():
    d = docx.Document(_bak("Valley_Pawn_Handbook_PP_Acknowledgment_HR-2026-04_Rev2.docx"))
    A = "Acknowledgment HR-2026-04 Rev2"
    rsub(d, A, "Header", "Policy No. HR-2026-04  ·  Effective", "Effective October 21, 2026", "Effective %s" % EFFECTIVE)
    rsub(d, A, "Section 1", "Valley Pawn Employee Handbook, version 2026.8 FINAL",
         "effective October 21, 2026", "effective %s" % EFFECTIVE)
    rsub(d, A, "Section 1", "Valley Pawn Policies & Procedures Manual, version 2026.9 FINAL",
         "effective October 21, 2026", "effective %s" % EFFECTIVE)
    cadd(d, A, "Section 1", "Each standalone Company policy issued under them and delivered to me for signature",
         "This acknowledgment expressly covers the Policies & Procedures Manual including the Gun Safety Certificate "
         "requirement in Section 10.06 (Firearm Safety Certification policy HR-2026-05): I must complete the Basic Gun Safety 101 class, obtain the Certificate "
         "of Completion and submit it in Gusto by the end of my third calendar day of employment as a condition of "
         "employment, and recertify every year by January 31. The Company pays for the certificate, and the training is "
         "done at the store, on the clock.")
    _global_pass(d, A)
    d.save(ACK_OUT)
    print("WROTE", ACK_OUT)


def ceo_write_changes():
    head = "## CEO decisions 2026-10-25 — revision in place (versions unchanged)"
    L = [head, "",
         "Applied %s by `_build_pp_v2026.9_handbook_v2026.8.py --ceo-20261025` to the FINAL files as they stood that "
         "day (pre-decision copies: `_backups/*.bak-20261025-ceo`). Effective date: %s (Policy Day). Still NOT "
         "distributed — rides the November 2026 Policy Update." % (CEO_DATE, EFFECTIVE), "",
         "| # | Document | Section | Old text | New text | Source |", "|---|---|---|---|---|---|"]
    for i, (doc, sec, old, new, src) in enumerate(CEO_LOG, 1):
        L.append("| %d | %s | %s | %s | %s | %s |" % (i, doc, md_cell(sec), md_cell(old), md_cell(new), md_cell(src)))
    L.append("")
    txt = open(CHANGES_MD).read()
    i = txt.find(head)
    tail = ""
    if i >= 0:
        # keep any later subsections (e.g. "### CEO decisions 2026-10-25 — standalone documents ...") on re-run
        j = txt.find("\n### ", i + len(head))
        k = txt.find("\n## ", i + len(head))
        ends = [x for x in (j, k) if x >= 0]
        if ends:
            tail = txt[min(ends):].strip("\n")
        txt = txt[:i].rstrip() + "\n"
    with open(CHANGES_MD, "w") as f:
        f.write(txt.rstrip() + "\n\n" + "\n".join(L) + "\n" + (("\n" + tail + "\n") if tail else ""))


def main_ceo():
    try:
        ceo_pp()
        ceo_hb()
        ceo_ack()
    except BuildError as e:
        print("CEO STAGE ABORTED:", e)
        return 2
    ceo_write_changes()
    print("%d CEO-decision changes logged" % len(CEO_LOG))
    return 0


def main():
    if "--ceo-20261025" in sys.argv:
        return main_ceo()
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
