"""Build DRAFT P&P v2026.10 from Valley_Pawn_PP_Manual_v2026.9_FINAL.docx (source left untouched).
Driver: CEO final Academy rulings 2026-11-21 (Training Agent project: ACADEMY_FINAL_RULINGS_2026-11-21.md).
Writes only into _drafts_2026-12/. No FINAL in output names (Ask_Handbook/build_sources.py globs the HR root)."""
import copy, json, os, re, sys
import docx

HR = os.path.expanduser("~/mnt/Projects/Human Resources")
SRC = os.path.join(HR, "Valley_Pawn_PP_Manual_v2026.9_FINAL.docx")
OUT = os.path.join(HR, "_drafts_2026-12", "DRAFT_PP_v2026.10_for_Policy_Day.docx")
LOG = os.path.join(HR, "_drafts_2026-12", "_edit_log.json")

d = docx.Document(SRC)
P = list(d.paragraphs)  # fixed indices from the v2026.9 source

def section_of(i):
    for j in range(i, -1, -1):
        s = P[j].style.name if P[j].style is not None else ""
        if s in ("Heading 2",) or (s == "Heading 3" and re.match(r"^\d\d\.\d", P[j].text)):
            return P[j].text.strip()
        if s == "Heading 1":
            return P[j].text.strip()
    return "Title page"

log = []
def rep(i, old, new, ruling):
    p = P[i]; t = p.text
    assert t.count(old) == 1, (i, old[:60], t[:120])
    assert len(p.runs) == 1, (i, len(p.runs))
    p.runs[0].text = t.replace(old, new)
    log.append(dict(idx=i, section=section_of(i), old=old, new=new, ruling=ruling))

def insert_after(i, new, ruling, anchor=None):
    """New paragraph after P[i] (or after anchor element), cloned from P[i] so style/format match."""
    src = P[i]._p
    el = copy.deepcopy(src)
    runs = el.findall(docx.oxml.ns.qn("w:r"))
    for r in runs[1:]: el.remove(r)
    (anchor if anchor is not None else src).addnext(el)
    from docx.text.paragraph import Paragraph
    np_ = Paragraph(el, P[i]._parent)
    np_.runs[0].text = new
    log.append(dict(idx=i, section=section_of(i), old="(new paragraph)", new=new, ruling=ruling))
    return el

# ---------- Title page ----------
rep(5, "Version 2026.9 — FINAL", "Version 2026.10 — DRAFT for the December 2026 Policy Day", "Version bump")
rep(9, P[9].text, "Version 2026.10 DRAFT — prepared for CEO approval and not in force until it is approved and issued on the December 2026 Policy Day. Once issued, it supersedes all prior versions of this manual and all standalone Slack and Gusto policy documents consolidated into it. Items held pending answers are unchanged from v2026.9.", "Version bump")
rep(11, "Updated: October 25, 2026 (v2026.9)", "Updated: November 22, 2026 (v2026.10 draft)", "Version bump")
rep(11, "Effective November 4, 2026", "Effective: December 2026 Policy Day, once approved", "Version bump")

# ---------- 02.02 Safe ----------
rep(184, "The safe is opened only by the Manager or a designated employee, is kept closed and locked between uses, and is never opened in view of a customer. Combinations and keys are never shared outside the Manager and the Market Manager.",
    "The safe has one combination. An employee is given the combination after 90 days of employment; until then the safe is opened by the Manager or an employee who has the combination. The safe is kept closed and locked between uses and is never opened in view of a customer. There are no spare keys.", "6")
# ---------- 02.03 Bank Withdrawals ----------
rep(186, "Each morning the Manager requests any necessary funds from the Company's bank.",
    "There is no routine morning withdrawal: the till opens with the prior day's closing cash (Section 02.13). When the store does need cash from the bank, it is requested as set out below.", "3")
rep(187, "Place enough cash in the cash drawers to start the day (approximately $275.00 per drawer to make change for customers); secure the remainder in an envelope elsewhere in the office.",
    "Move to the till only what the till needs and keep the rest in the safe; there is no set opening amount. Store cash never exceeds $5,000 (Section 02.06).", "1, 3")
# ---------- 02.04 Cash Drawers ----------
rep(191, P[191].text,
    "Each store runs ONE shared (global) till; employees do not have personal cash drawers. Every employee works the till under their own Bravo login. The till is kept locked whenever it is out of the employee's line of sight. CULPEPER SATELLITE TILL: Culpeper also runs one satellite till holding $250 to $1,000, counted every morning and at end of day.", "5")
rep(192, "Each employee is responsible for his or her own key", "Each employee who holds a till key is responsible for it", "5")
rep(193, P[193].text, "There are no spare keys and no spare-key envelope. A lost key is reported to the Manager immediately (above).", "6")
rep(194, "Since employees are responsible for the contents of their cash drawers, all software passwords must be kept confidential.",
    "Because the till is shared, each employee's own Bravo login is the record of who did each transaction, so all software passwords must be kept confidential.", "5")
# ---------- 02.05 / 02.06 ----------
rep(203, P[203].text,
    "Each store runs one shared till (Section 02.04), so cash is not transferred between employees' drawers. When cash moves between the till and the safe, or between the Culpeper main till and satellite till, the money is counted (by both employees where two are on duty) to ensure the correct amount changes hands. In Bravo, select \"Transfer Tender,\" choose the \"Source\" and the \"Destination,\" select the bills/amount, and click \"save.\"", "5")
rep(205, P[205].text,
    "There is no per-drawer cash limit. The store's cash limit is $5,000: anything over $5,000 goes to the bank (Section 03.15). Cash otherwise stays in the till, including at close (Section 02.13).", "1, 2")
# ---------- 02.07 Balancing ----------
rep(207, "Cash drawers are balanced a minimum of two (2) times per day. A receipt tape is run for each balance; each employee must initial, date and time-stamp the tape, and these tapes are filed each day with the end-of-day paperwork.",
    "The till (and, at Culpeper, the satellite till) is balanced a minimum of two (2) times per day. Each balance is counted with Bravo's counting tool and the Bravo report is printed; the employee initials, dates and time-stamps the printed report, and the reports are filed each day with the end-of-day paperwork. There is no calculator tape.", "4, 5")
rep(208, "The final drawer balance", "The final till balance", "4")
rep(208, "If the drawer is over or short", "If the till is over or short", "4")
rep(208, "This report must be printed; run a calculator tape against the balance, attach it to the report once balanced, and initial/date/time-stamp it.",
    "Count with Bravo's counting tool; the report must be printed and initialed, dated and time-stamped. No calculator tape is run.", "4")
# ---------- 02.13 Open / Close ----------
rep(232, P[232].text, "Open the till with the cash the store closed with the night before — there is no set opening amount. Click Save.", "3")
rep(233, P[233].text, "Transfer Tender is used only when cash actually arrives or moves — there is no daily bank-to-safe-to-till float.", "3")
rep(234, P[234].text, "Cash received from the bank: on the transfer tender screen, select BANK Account as Source and SAFE Store Safe as Destination, enter the amount actually received on the Cash heading, and click Save.", "3")
rep(235, P[235].text, "To move cash from the safe to the till: select SAFE Store Safe as Source and TILL as Destination, enter the amount actually moved on the Cash heading, and click Save. The store is now ready to conduct transactions.", "3")
rep(236, P[236].text, "The amount entered is always the amount actually received or moved. There is no set opening amount and no per-drawer limit. Store cash never exceeds $5,000; anything over $5,000 goes to the bank (Sections 02.06 and 03.15). At Culpeper, count the satellite till ($250–$1,000) at opening.", "1, 3, 5")
rep(239, "Count the cash drawer;", "Count the till with Bravo's counting tool (at Culpeper, the satellite till as well);", "4, 5")
rep(241, "including the amount transferred from the drawer to the store safe", "including any amount transferred from the till to the store safe", "5")
rep(242, "funds transferred from the cash drawer", "funds transferred from the till", "5")
insert_after(244, "CASH STAYS IN THE TILL AT CLOSE. The till is not emptied into a deposit at close. Print the Bravo count report (no calculator tape). A deposit is made only when store cash is over $5,000 or the store has been told to deposit down — see Section 03.15.", "2, 4")
# ---------- 03.06 Personal phones ----------
rep(268, P[268].text, "PERSONAL PHONES. Employees use their personal phones for work — eBay listing photos especially. Personal scrolling, texting, calls and social media wait for breaks, away from the counter. A call to the Market Manager or the CEO about store business is always allowed.", "26")
# ---------- 03.08 Records ----------
rep(274, "(the bound book)", "(the A&D book, kept in Bravo)", "17")
rep(275, "and in practice retained with the firearms records.", "and filed with their Form 4473, with the firearms records.", "17")
rep(289, P[289].text, "Multiple sales (ATF Form 3310.4 and the MHG Acknowledgement Form) — no separate log or binder: each multiple-sale form is filed with its Form 4473 (two or more handguns sold or transferred to the same customer within five consecutive business days, Section 05.02).", "17")
# ---------- 03.09 Confidentiality ----------
PHONE_OLD = "Never confirm a firearm by phone — whether we have it, whether it is on a loan, or whose it is — even to a verified caller."
PHONE_NEW = "Once the account is fully verified, a firearm on a loan is discussed by phone like any other loan item. To a caller who is not fully verified, nothing about a firearm is confirmed — whether we have it, whether it is on a loan, or whose it is."
rep(293, PHONE_OLD, PHONE_NEW, "13")
# ---------- 03.15 Bank Deposits ----------
rep(312, P[312].text, "A deposit is made only when store cash is over $5,000 or the store is told to deposit down; otherwise cash stays in the till. Anything over $5,000 goes to the bank. In Bravo the deposit moves TILL → SAFE, then SAFE → the store's bank account: select \"Tender Transfer,\" choose the source and destination for each step, enter all bills/amounts, and click save. Deposits go to the bank during bank hours.", "1, 2")
# ---------- 04.02 ----------
rep(349, "logged in Bravo and the bound book", "logged in Bravo and its A&D book", "17")
rep(359, "Documentation is retained in the store compliance file for a minimum of five years.", "Documentation is filed with the Form 4473 and kept for a minimum of five years.", "17")
rep(361, "It is retained with the transaction records for a minimum of five years", "It is filed with the Form 4473 for a minimum of five years", "17")
# ---------- 05.0 Charges ----------
rep(420, "Up to 10% of the amount loaned on the item. The late fee applies on the 6TH DAY PAST DUE (day 1 past due is the day after the due date).",
    "The Company's late fee is 5% of the loan principal (the statute allows up to 10% of the amount loaned on the item). Days 1–5 past due are a 5-day grace period with no late fee; the late fee applies on the 6TH DAY PAST DUE (day 1 past due is the day after the due date).", "10")
# ---------- 05.00A Record ----------
rep(428, "a STATEMENT OF OWNERSHIP from the customer.", "a STATEMENT OF OWNERSHIP from the customer, which is part of the signed pawn ticket — not a separate form.", "18")
rep(431, "Capture a digital image of the identification. A customer photo is taken on every intake.", "Capture a digital image of the identification — photograph the ID, not the person. No customer photo is taken (the one exception is military ID, below).", "18")
rep(432, "Do not image the military ID.", "Do not image the military ID. This is the only case in which the customer is photographed.", "18")
rep(433, "Capture it at the time of the transaction, every time.", "It is part of the signed ticket, so it is captured at the time of the transaction, every time.", "18")
# ---------- 05.01 Pawn ----------
rep(438, "Choose cash or check payment and click", "Loans are paid out in cash only — never by check. Choose cash and click", "18")
rep(441, "If the customer does not pay the finance fee, the item enters the 15-day legal hold (Va. Code § 54.1-4005) before it may be placed for sale.",
    "If the customer does not pay, the loan runs the timeline in Section 06.01: a 5-day grace period, the late fee from the 6th day past due, then 10 more days, after which the loan expires at the end of the 15-day legal hold (Va. Code § 54.1-4005).", "10")
rep(442, "Company practice is more conservative — no item is pulled from loan status until it is 31 days past due, on the single timeline in Section 06.01. Staff never pull on day 16.",
    "The Company's timeline in Section 06.01 ends with it: the loan expires at the end of day 15 past due (day 45 of a 30-day loan), and nothing is pulled, priced or sold before then.", "10")
rep(443, "A late fee of up to 10% of the amount loaned applies on the 6th day past due, and only where that fee was disclosed on the ticket.",
    "A late fee of 5% of the principal applies on the 6th day past due, after the 5-day grace period, and only where that fee was disclosed on the ticket.", "10")
rep(443, "The contract must be initialled (confirming it was explained to the customer), signed, dated and fingerprinted.",
    "The contract must be initialled (confirming it was explained to the customer), signed and dated; the signed ticket includes the customer's statement of ownership. No fingerprints are taken.", "18")
rep(445, "Any firearm redeemed must be supplied with a gun lock.", "A gun lock is offered and provided with a redeemed handgun (Section 05.02).", "15")
rep(446, P[446].text, "IF THE PLEDGOR IS DENIED. The loan continues on its normal terms — a denial does not cancel the loan. The pledgor may not receive the firearm, and no one else redeems it for them: Valley Pawn does not do third-party firearm redemptions, in any circumstance (Section 05.04). If the pledgor cannot lawfully redeem, the loan runs to default under Section 06.01 and the firearm becomes Company inventory.", "14")
# ---------- 05.02 Buy ----------
rep(450, P[450].text, "After buying an item from a customer, the customer receives the same pawn ticket contract as a pawn transaction and must sign and date it; the signed ticket includes the statement of ownership. No fingerprints are taken. BUY HOLDS — PRECIOUS METALS ONLY. Precious metals (gold, silver, platinum) bought outright are held for fifteen (15) days before they are priced or sold. Everything else bought outright may be priced immediately.", "11, 18")
rep(452, "If an error is made, photocopy the page, correct the error on the photocopy only (never alter the original), and file the photocopy with the unaltered original.",
    "CORRECTIONS. Until the transaction is complete, a mistake is corrected on the original form. Once the transaction is complete, the original is never changed: any correction is made on a photocopy only, and the photocopy is filed with the original.", "16")
rep(458, "This position is reviewed only if Virginia law changes.", "This position is reviewed only if Virginia law changes. UNDER-21 BUYER AND A RIFLE WITH A DETACHABLE MAGAZINE OR A PISTOL GRIP: call the Market Manager BEFORE starting any paperwork, to confirm current law.", "12")
rep(459, "The Manager files it the same day and copies the CEO.", "The Manager files it the same day and copies the CEO. Multiple-sale forms (Form 3310.4 and the MHG Acknowledgement Form) are filed with their Form 4473.", "17")
rep(460, "The Acquisition and Disposition Record (the bound book)", "The Acquisition and Disposition Record (the A&D book, kept in Bravo)", "17")
rep(460, "Any firearm sold to a customer must be supplied with a gun lock.", "Gun locks are offered with handguns only: every handgun sold, transferred or redeemed goes out with a gun lock offered and provided (18 U.S.C. § 922(z)(1)); gun locks are not offered with long guns.", "15")
# ---------- 05.04 ----------
insert_after(466, "EXTENSION, RENEWAL AND RELOAN. An extension and a renewal are two different options and are never treated as the same thing. Writing a new loan on the same item is a reloan, and a reloan needs a new worksheet; a renewal does not. Every renewal must show the correct loan date in Bravo.", "19")
rep(468, "Two redemption tickets print — one to the customer, one filed in the redemption ticket box.", "There is no redemption ticket and no redemption ticket box.", "19")
rep(468, "EXCEPT that a third party may never redeem a firearm or a vehicle title.", "EXCEPT that a third party may never redeem a firearm or a vehicle title — Valley Pawn does not do third-party firearm redemptions.", "14")
rep(469, "a gun lock must accompany any redeemed firearm", "a gun lock is offered and provided with a redeemed handgun (Section 05.02); long guns do not get one", "15")
# ---------- 05.07 ----------
rep(502, "the signature, fingerprint, and ticket-printing steps", "the signature and ticket-printing steps (no fingerprints are taken)", "18")
# ---------- 05.08 Returns ----------
rep(505, "No returns on firearms, ammunition, or consumables.", "No returns on ammunition or consumables. Firearms follow this same return policy.", "9")
rep(507, P[507].text, "Firearms: the same return policy as every other item — money back within 7 days of purchase, store credit up to 30 days. A returned firearm is entered in the A&D book as an acquisition (Section 05.02).", "9")
rep(510, P[510].text, "Returns beyond 30 days from purchase: none. There is no warranty after 30 days.", "32")
# ---------- 05.10 Employee purchases ----------
rep(523, "ninety (90) consecutive days", "thirty (30) days", "20")
rep(541, "the 90-day sales floor requirement", "the 30-day sales floor requirement", "20")
# ---------- 06.01 ----------
rep(591, "The late fee (Section 05.0) applies on the 6th day past due.", "Days 1–5 past due are a 5-day grace period. The late fee (Section 05.0) — 5% of the principal — applies on the 6th day past due. After 10 more days (days 6–15 past due) the loan expires.", "10")
rep(593, P[593].text, "Company practice follows the legal floor. The loan expires at the end of day 15 past due — the end of the 15-day legal hold, day 45 of a 30-day loan — and only then is the item eligible for Pull From Inventory (PFI), subject to the ownership-statement gate below. The former day-31 pull and day-61 PFI standards are withdrawn. Holding an expired item out of PFI requires the CEO's approval.", "10")
# ---------- 06.02 Pricing ----------
rep(602, "\"Items Waiting to be Priced.\"" if "\"Items Waiting to be Priced.\"" in P[602].text else "Items Waiting to be Priced.",
    ("\"Items Waiting to be Priced.\"" if "\"Items Waiting to be Priced.\"" in P[602].text else "Items Waiting to be Priced.") + " Price at the higher average sold price — you can always come down, you can't go up.", "23")
# ---------- 07.01 Social media ----------
insert_after(617, "SOCIAL MEDIA — NO GUNS. No handgun, and no gun of any kind, is ever posted on social media — Instagram, Facebook or any other platform.", "31")
# ---------- 07.04 Competitors ----------
rep(635, "General tips:", "Never refer a customer to a competitor — tell them what Valley Pawn can do instead. General tips:", "24")
# ---------- 08.02 ----------
rep(669, PHONE_OLD, PHONE_NEW, "13")
# ---------- 10.04 ----------
rep(737, "Skim the drawer frequently per company policy; the cash drawer must be locked when unattended.", "The till must be locked when unattended.", "1, 2")
rep(738, "Never count money or skim the drawer in view", "Never count money in view", "2")
rep(741, P[741].text, "Keep store cash at or under $5,000 — anything over $5,000 goes to the bank, during bank hours (Section 03.15).", "1, 2")
# ---------- 10.06 Gun-safety certificate ----------
rep(756, P[756].text, "THE EMPLOYEE PAYS AND IS REIMBURSED FROM THE TILL. The provider is GunSafety.co (the former gunsafetytrainingpro.com now redirects there). As of September 2026 the roughly 40-minute course itself is FREE, and the $25 charge buys only the separately purchased Certificate of Completion. The employee pays the $25 certificate fee and is reimbursed in full as a paid-out from the store till (Section 02.09), with the receipt attached; it is never deducted from pay. Earlier instructions to 'select the $25 version of the course' are withdrawn — that product no longer exists.", "7")
rep(757, "the verified certificate is kept in the employee's Gusto Documents and personnel file.", "the Market Manager files the verified certificate in the employee's Gusto Documents and personnel file.", "7")
rep(758, "(3) submits the certificate PDF by uploading it to Gusto under Documents and telling their Manager the same day.", "(3) sends the certificate to the Market Manager, who files it in Gusto, and tells their Manager the same day.", "7")
rep(758, "The Company pays the $25 certificate fee, either directly or by reimbursing the employee on submission of the certificate; it is never deducted from pay.", "The employee pays the $25 certificate fee and is reimbursed as a paid-out from the store till; it is never deducted from pay.", "7")
# ---------- 11.01 Glossary ----------
rep(772, "Company practice holds items longer — see Section 06.01.", "The Company's timeline ends with it: the loan expires at the end of the 15-day legal hold — see Section 06.01.", "10")
# ---------- 12.01 / 12.05 ----------
insert_after(792, "MANAGERS' MEETING. The managers' meeting is held weekly at 9:30 AM by Slack huddle.", "25")
rep(800, "Not sure if something counts? Ask the Market Manager.", "Not sure if something counts? Ask the Market Manager. An under-21 buyer who wants a rifle with a detachable magazine or a pistol grip: call the Market Manager BEFORE starting any paperwork.", "12")

# ---------- Changelog (inserted above the v2026.9 entry) ----------
cl = [
 "Cash (02.02–02.07, 02.13, 03.15, 10.04) — one shared till per store (Culpeper satellite till $250–$1,000, counted morning and end of day); the till opens with the prior day's close (the $275 float and $2,000 drawer limit are removed); $5,000 store limit, anything over goes to the bank; cash stays in the till at close; a deposit only when over $5,000 or told to deposit down (till → safe → bank, during bank hours); Bravo counting tool and printed report, no calculator tape; one safe combination, given after 90 days; no spare keys.",
 "Loans (05.0, 05.01, 06.01, glossary) — 5-day grace period; late fee of 5% of principal from the 6th day past due; 10 more days, then the loan expires at the end of the 15-day legal hold; the day-31 pull and day-61 PFI standards are removed.",
 "Pawn paperwork (05.00A, 05.01, 05.02, 05.07) — loans paid out in cash only, no checks; the statement of ownership is part of the signed ticket; photograph the ID, not the person (military ID excepted); no fingerprints.",
 "Refinances and redemptions (05.04, 05.01) — extension and renewal are separate options; a reloan needs a new worksheet; renewals show the correct loan date in Bravo; no redemption ticket; no third-party firearm redemption.",
 "Buys (05.02) — only precious metals are held, 15 days, before pricing or sale; everything else is priced immediately.",
 "Firearms (03.08, 03.09, 04.02, 05.02, 08.02, 12.05) — under-21 buyer wanting a rifle with a detachable magazine or pistol grip: call the Market Manager before any paperwork; a firearm on a loan may be discussed by phone once the account is fully verified; gun locks with handguns only; corrections on the original until the transaction is complete, then on a photocopy only; A&D book in Bravo; multiple-sale forms filed with their 4473.",
 "Returns (05.08) — firearms follow the standard return policy (7-day money back, up to 30 days store credit); no warranty after 30 days.",
 "Employee purchases (05.10) — 30 days on the floor. Pricing (06.02) — price at the higher average sold price. Competitors (07.04) — never refer a customer to a competitor. Social media (07.01) — no guns, ever.",
 "Personal phones (03.06) — used for work, eBay listing photos especially. Managers' meeting (12.01) — weekly, 9:30 AM, Slack huddle. Gun Safety Certificate (10.06) — the employee pays and is reimbursed as a till paid-out; the certificate goes to the Market Manager for filing in Gusto.",
 "Because this revision changes existing rules, a new signed Employee Handbook & P&P Acknowledgment (HR-2026-04) is issued with this version.",
]
h = copy.deepcopy(P[19]._p); P[19]._p.addprevious(h)
from docx.text.paragraph import Paragraph
hp = Paragraph(h, P[19]._parent)
for r in hp.runs[1:]: r._r.getparent().remove(r._r)
hp.runs[0].text = "What's New in Version 2026.10 (draft, November 22, 2026) — aligned to the CEO's final Valley Pawn Academy rulings of November 21, 2026"
anchor = h
for line in cl:
    el = copy.deepcopy(P[20]._p); anchor.addnext(el); anchor = el
    Paragraph(el, P[20]._parent).runs[0].text = line
log.append(dict(idx=19, section="Changelog", old="(new entry)", new="What's New in Version 2026.10 heading + %d lines" % len(cl), ruling="all"))

d.save(OUT)
json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
secs = sorted({e["section"] for e in log})
print("edits", len(log), "sections", len(secs)); print("\n".join(secs))
