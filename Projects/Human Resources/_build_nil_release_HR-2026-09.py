"""Builds HR-2026-09 Name, Image, Likeness & Voice Release in the HR-2026-07 house style.
Outputs a blank template and a Preston Peters pre-filled copy (docx + pdf)."""
import copy, os, subprocess, sys
import docx
from docx.shared import Pt, RGBColor, Emu

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "Valley_Pawn_Confidentiality_Customer_Information_Agreement_HR-2026-07.docx")
BLUE, GREY, NAVY = RGBColor(0x00, 0x99, 0xDD), RGBColor(0x59, 0x59, 0x59), RGBColor(0x2D, 0x1A, 0x5E)

def build(employee_name, employee_title, out_base):
    d = docx.Document(TEMPLATE)
    body = d.element.body
    sig_tbl_proto = copy.deepcopy(d.tables[0]._tbl)
    for el in list(body):
        if not el.tag.endswith("sectPr"):
            body.remove(el)

    def para(text, size=10.5, bold=False, color=None, after=5, style=None):
        p = d.add_paragraph(style=style)
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
        p.paragraph_format.space_after = Pt(after)
        return p

    def rich(parts, after=5, style=None):
        p = d.add_paragraph(style=style)
        for text, b in parts:
            r = p.add_run(text); r.bold = b; r.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(after)
        return p

    def h(text):
        para(text, size=11.5, bold=True, color=NAVY, after=3)

    def bullets(items):
        for it in items:
            if isinstance(it, tuple):
                rich([(it[0], True), (it[1], False)], after=2, style="List Bullet")
            else:
                para(it, after=2, style="List Bullet")

    def sig_table(rows):
        t = copy.deepcopy(sig_tbl_proto)
        body.insert(len(body) - 1, t)
        tbl = d.tables[-1]
        for ri, (l, r) in enumerate(rows):
            for cell, txt in ((tbl.rows[ri * 2 + 1].cells[0], l), (tbl.rows[ri * 2 + 1].cells[1], r)):
                p = cell.paragraphs[0]
                keep = p.runs[-1]
                for run in p.runs[:-1]:
                    run._r.getparent().remove(run._r)
                keep.text = txt
        return tbl

    para("VALLEY PAWN", size=9, bold=True, color=BLUE, after=0)
    para("Full Circle Finance Inc DBA Valley Pawn", size=9, color=GREY, after=6)
    para("Name, Image, Likeness and Voice Release", size=17, bold=True, color=NAVY, after=2)
    para("Form No. HR-2026-09 · Effective October 1, 2026 · Applies to: employees who appear in Company "
         "training or marketing content · Owner: Chief Executive Officer", size=9, color=GREY, after=6)
    rich([("Employee: ", True), (employee_name, False), ("     Position: ", True), (employee_title, False)], after=10)

    h("1. Why this release exists")
    para("Valley Pawn is building the Valley Pawn Academy and other training materials — lessons, videos, "
         "Bravo walkthroughs, recorded calls and meetings, and the Company operations knowledge base — and you "
         "are being asked to appear in, narrate, or contribute to them. Virginia law (Va. Code § 8.01-40 and "
         "§ 18.2-216.1) requires a person's written consent before their name, portrait, picture, voice, or likeness "
         "is used for trade or advertising. This release gives that consent, explains exactly how the Company may use it, and "
         "sets the limits the Company agrees to follow.")

    h("2. What this release covers")
    para("\"Your Likeness\" means any of the following, whether captured before or after you sign:", after=3)
    bullets([
        "Your name, nickname, title, signature, and biographical information you provide.",
        "Photographs and video of you, and your image and appearance.",
        "Your voice, including audio and video recordings, recorded phone and Zoom calls, and recorded meetings "
        "or huddles.",
        "Screen recordings in which you appear or narrate.",
        ("Your Contributions: ", "the explanations, procedures, answers, and know-how you provide for Company "
         "training materials, scripts, tests, and the operations knowledge base."),
        ("A Digital Replica: ", "an AI-generated voice or on-screen likeness created from your recordings — "
         "only as allowed in Section 5."),
    ])
    para("Everything the Company makes using Your Likeness is called the \"Materials.\" You consent to the Company "
         "recording training sessions, meetings, and calls you take part in for use under this release.")

    h("3. What you grant the Company")
    para("You grant Full Circle Finance Inc, its successors, and vendors acting on its behalf a worldwide, "
         "royalty-free, irrevocable right to record, edit, caption, translate, adapt, combine with other material, "
         "reproduce, distribute, and display Your Likeness and the Materials, in any format or medium now known or "
         "later developed, for:", after=3)
    bullets([
        ("Internal use: ", "training, onboarding, testing, coaching, policies, and store operations at Valley Pawn "
         "(for example the Academy on TalentLMS, Slack, Gusto, the operations knowledge base, and in-store use). "
         "This right continues after your employment ends, so the training program keeps working."),
        ("Public marketing: ", "only if you choose YES in Section 8."),
    ])
    para("The Company may edit the Materials for length, clarity, and accuracy, and you do not need to approve the "
         "final version. The Company will ask you to review lessons that feature you for accuracy before they are "
         "released to staff while you are employed.")

    h("4. Ownership")
    para("All recordings, videos, scripts, lessons, and Contributions you create within the scope of your "
         "employment are works made for hire owned by the Company. To the extent any of it is not, you assign your "
         "rights in it to the Company. You keep your own general skills, knowledge, and experience. This is not a "
         "non-compete agreement and does not limit where you may work in the future.")

    h("5. Digital Replica (AI voice or likeness) — the rules")
    para("You consent to the Company creating and using a Digital Replica of your voice or likeness for internal "
         "training materials, subject to these limits, which the Company agrees to follow:", after=3)
    bullets([
        "It will only narrate or present Company training content consistent with Company policy. It will never be "
        "used to endorse a product or service, express a political or religious view, or create sexual, offensive, "
        "or defamatory content, or to disclose your personal information.",
        "It will never be used to impersonate you in any live or one-to-one communication — calls, texts, voicemail, "
        "Slack, or email — with employees, customers, or anyone else.",
        "The Company will review every piece of content made with it before release and will note in the course "
        "credits when narration is AI-generated.",
        "It will be stored only in Company-controlled vendor accounts with access limited to Company administrators. "
        "The Company will not sell, license, or give it to anyone for their own use.",
        ("When your employment ends: ", "the Company may keep using Materials already finished, but it will not "
         "create new content with your Digital Replica without your new written consent, and it will delete the "
         "voice model or likeness model from its vendors within 90 days of your last day unless you agree otherwise "
         "in writing."),
    ])

    h("6. Pay and time")
    para("You will not receive additional compensation for this release; it is given in exchange for your "
         "employment and the Company's promises in this release. All time you spend recording, reviewing, or "
         "preparing Materials is work time and is paid under the Employee Handbook.")

    h("7. Release, duration, and what this does not change")
    bullets([
        "You release the Company from claims of invasion of privacy, right of publicity, misappropriation of name "
        "or likeness (including under Va. Code § 8.01-40 and § 18.2-216.1), and defamation arising from uses this "
        "release permits. You do not release claims for any use outside this release or for a breach of it by "
        "the Company.",
        "This release is irrevocable for Materials already created. You may stop future recordings or new Digital "
        "Replica content at any time by written notice to the Chief Executive Officer; that notice applies going "
        "forward only.",
        "Nothing here limits your rights under Section 7 of the National Labor Relations Act, your right to report "
        "possible violations of law to any government agency, or any other right the law does not allow to be "
        "waived.",
        "This release does not change the at-will employment relationship. It survives the end of your employment, "
        "is governed by Virginia law, and is the entire agreement on this subject. If any part is unenforceable, "
        "the rest remains in effect. An electronic signature through Gusto is as valid as a handwritten one "
        "(Va. Code § 59.1-485).",
    ])

    h("8. Public marketing use — choose one")
    para("☐  YES — the Company may also use Your Likeness (not a Digital Replica) in public marketing, such as social "
         "media, the website, advertising, and signage. After my employment ends, the Company will not publish new "
         "marketing featuring me and will remove me from paid advertising within 30 days of my written request; "
         "content already posted may otherwise remain.", after=4)
    para("☐  NO — internal training and operations use only.", after=4)
    para("Employee initials: ____________", after=8)

    d.add_paragraph().add_run().add_break(docx.enum.text.WD_BREAK.PAGE)
    h("9. Signatures")
    para("I have read this release, I understand it, and I agree to it. I understand it is signed electronically "
         "through Gusto, kept in my personnel file, and that I may view and download it but cannot alter or "
         "delete it.")
    sig_table([("Employee signature (via Gusto)", "Date"), ("Employee printed name", "Position")])
    para("", after=4)
    sig_table([("Company signature — Joshua Davis", "Date"),
               ("Printed name and title", "Full Circle Finance Inc DBA Valley Pawn")])

    out_docx = os.path.join(HERE, out_base + ".docx")
    d.save(out_docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", HERE, out_docx],
                   check=True, capture_output=True)
    return out_docx

if __name__ == "__main__":
    build("Preston Peters", "Market Manager", "Valley_Pawn_Name_Image_Likeness_Voice_Release_HR-2026-09_Preston_Peters")
    build("______________________", "______________________", "Valley_Pawn_Name_Image_Likeness_Voice_Release_HR-2026-09")
    print("ok")
