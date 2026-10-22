#!/usr/bin/env python3
"""Blank DocuSign form for the Monthly Policy Update (Policy Day). No employee data and no policy text on it:
all month-specific content arrives as locked DocuSign text tabs at send time (policy_update_envelope.py).
House style and anchor convention = HR e-sign make_forms.py (white 1pt anchors \\f_<name>\\, \\s_1\\, \\d_1\\, \\n_1\\).
Usage: python3 make_policy_update_form.py <outdir>   -> VP_Policy_Update_Form_v1.pdf + layout_policy_update.json"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
import json, sys
NAVY, BLUE, GREY, LINE = HexColor('#2D1A5E'), HexColor('#0099DD'), HexColor('#595959'), HexColor('#BFBFBF')
W, H = letter; M = 40; LAYOUT = {}
def anchor(c, x, y, name): c.setFillColor(white); c.setFont('Helvetica', 1); c.drawString(x, y, f'\\{name}\\')
def header(c, title, sub, page):
    c.setFillColor(BLUE); c.setFont('Helvetica-Bold', 9); c.drawString(M, H-46, 'VALLEY PAWN · FULL CIRCLE FINANCE INC')
    c.setFillColor(GREY); c.setFont('Helvetica', 8); c.drawRightString(W-M, H-46, f'Page {page} of 4')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 20); c.drawString(M, H-70, title)
    c.setFillColor(GREY); c.setFont('Helvetica', 9); c.drawString(M, H-84, sub)
    c.setStrokeColor(NAVY); c.setLineWidth(1.2); c.line(M, H-92, W-M, H-92)
def box(c, x, top, w, h, label, name):
    c.setFillColor(GREY); c.setFont('Helvetica-Bold', 7.5); c.drawString(x, top-9, label.upper())
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.rect(x, top-12-h, w, h)
    anchor(c, x+3, top-20, f'f_{name}'); LAYOUT[name] = [int(w-8), int(h-6)]
    return top-12-h
def row(c, top, fields, h=20):
    gap = 8; n = len(fields); w = (W-2*M-gap*(n-1))/n; x = M; b = top
    for label, name in fields: b = box(c, x, top, w, h, label, name); x += w+gap
    return b-8
def para(c, top, text, size=7.4, bold=False):
    c.setFillColor(GREY if not bold else NAVY); f = 'Helvetica-Bold' if bold else 'Helvetica'; c.setFont(f, size)
    for ln in simpleSplit(text, f, size, W-2*M): c.drawString(M, top, ln); top -= size+2.4
    return top-3
ACK = [
 ('1. What I received.', 'This Monthly Policy Update, every policy in it, and the current Valley Pawn Employee Handbook and Policies & Procedures Manual named above. When a new Handbook or Policies & Procedures version is named above, this acknowledgment also replaces the separate Handbook & P&P acknowledgment (HR-2026-04) for that version. The manuals are available to me at any time in Gusto under Documents and from my store manager. I may ask about any policy at any time: Goldilocks in the #ask-goldilocks Slack channel, my store manager, the Market Manager or the Chief Executive Officer.'),
 ('2. I read and understand them.', 'I have read everything in this update. Where anything was unclear, I asked before signing and my question was answered.'),
 ('3. I agree to follow them.', 'I agree to comply with the Employee Handbook, the Policies & Procedures Manual and every Company policy, procedure, standard and lawful instruction issued under them, for as long as I am employed. Compliance is a condition of employment; failure to comply may result in corrective action up to and including termination of employment.'),
 ('4. My employment is at will.', 'My employment is at will under Virginia law: either I or the Company may end it at any time, with or without notice or cause. No handbook, manual, policy, this acknowledgment or any statement is a contract of employment. Only a written agreement signed by the Chief Executive Officer can change this.'),
 ('5. The Company may change these documents.', 'Except for at-will employment, the Company may add to, change, suspend or withdraw any policy, practice or benefit at its discretion, with or without notice. Changes are delivered in a Monthly Policy Update, and my continued employment after notice of a change is my acceptance of it.'),
 ('6. My duty to speak up.', 'Valley Pawn is a licensed pawnbroker and a federal firearms licensee. I will promptly report to my store manager, the Market Manager or the Chief Executive Officer anything I believe in good faith breaks the law or a Company policy, including firearms transactions and records, cash reporting, customer records and privacy, and Company or customer property. The Company will not retaliate against a good-faith report. Nothing here limits my right to contact or give information to any government agency or any other activity protected by law.'),
 ('7. Electronic signature.', 'I am signing electronically through DocuSign. My electronic signature has the same force and effect as a handwritten signature under the federal E-SIGN Act and the Virginia Uniform Electronic Transactions Act (Va. Code § 59.1-479 et seq.). The signed copy is a Company employment record that I cannot alter; DocuSign emails me a copy when I sign, and I may ask for a paper copy at no charge.'),
]
def build(path):
    c = canvas.Canvas(path, pagesize=letter); c.setTitle('Valley Pawn Monthly Policy Update')
    header(c, 'Monthly Policy Update', 'Read all four pages, then sign on page 4 · One signature covers everything in this update', 1)
    t = row(c, H-102, [('Month', 'month'), ('Policy Day', 'day'), ('Sign by', 'signby')])
    box(c, M, t, W-2*M, 600, "What's new this month", 'new'); c.showPage()
    header(c, 'Monthly Policy Update', 'The policies — new or changed this month', 2)
    box(c, M, H-102, W-2*M, 640, 'Policies (part 1)', 'pol1'); c.showPage()
    header(c, 'Monthly Policy Update', 'The policies — continued', 3)
    box(c, M, H-102, W-2*M, 640, 'Policies (part 2) and anything else in this update', 'pol2'); c.showPage()
    header(c, 'Monthly Policy Update', 'Acknowledgment and signature', 4)
    t = row(c, H-102, [('Employee Handbook version', 'hb'), ('Policies & Procedures version', 'pp'), ('Update reference', 'ref')])
    for head, body in ACK:
        t = para(c, t, head, 8, bold=True) + 2; t = para(c, t, body)
    t -= 4; t = para(c, t, 'By signing below I confirm that I received everything in this Monthly Policy Update and the manuals named above, that I have read and understand them, and that I agree to abide by them.', 7.6, bold=True)
    colw = (W-2*M-16)/2; L = t-36; L2 = L-26; xd = M+colw*0.68 + 0
    c.setStrokeColor(GREY); c.setLineWidth(0.6)
    c.line(M, L, M+colw*1.2, L); c.line(M+colw*1.3, L, W-M, L); c.line(M, L2, M+colw*1.2, L2)
    anchor(c, M+2, L+4, 's_1'); anchor(c, M+colw*1.3+2, L+4, 'd_1'); anchor(c, M+2, L2+4, 'n_1')
    c.setFillColor(GREY); c.setFont('Helvetica', 7)
    c.drawString(M, L-8, 'Employee signature'); c.drawString(M+colw*1.3, L-8, 'Date'); c.drawString(M, L2-8, 'Printed name')
    LAYOUT['n_1'] = [int(colw*1.2), 12]
    c.setFont('Helvetica', 6.5); c.drawString(M, 30, 'Valley Pawn Monthly Policy Update form v1 · Retain in the employee personnel record · Supersedes any unsigned acknowledgment page for the same update')
    c.showPage(); c.save()
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    build(f'{out}/VP_Policy_Update_Form_v1.pdf'); json.dump(LAYOUT, open(f'{out}/layout_policy_update.json', 'w'), indent=1); print(json.dumps(LAYOUT))
