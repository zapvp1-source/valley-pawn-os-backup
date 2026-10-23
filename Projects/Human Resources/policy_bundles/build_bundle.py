#!/usr/bin/env python3
"""
build_bundle.py — builds the Monthly Policy Update packet for Valley Pawn.

One update per month = ONE Gusto Team document = ONE employee signature (current team + future hires).
  page 1      : "Policy Update — <Month YYYY>" cover — what changed, in plain words
  pages 2..n  : each new/changed one-page policy (house format, no per-policy signature block)
  last pages  : the acknowledgment (monthly ack generated here, OR an attached PDF such as
                HR-2026-04 when the Handbook / P&P version changes)

Usage:
  python3 build_bundle.py manifests/2026-11.json
Writes out/<YYYY-MM>_Policy_Update.docx and .pdf (+ page PNGs for the preview).

Manifest (JSON):
{
  "month": "November 2026", "slug": "2026-11", "policy_day": "Monday, November 2, 2026",
  "sign_by": "Tuesday, November 10, 2026",
  "handbook": "2026.8", "pp": "2026.9",
  "whats_new": ["plain sentence", ...],                 # cover bullets, <= 10
  "policies": [{"title": "...", "area": "Firearms|eBay|Operations|Pay|...", "starts": "...", "box": "the rule",
                "lines": ["→ line 1", "→ line 2", "→ line 3"]}],     # house-format one-pagers
  "md_pages": [{"title": "...", "area": "...", "starts": "...", "md": "path.md"}],   # longer policies
  "attachments": [{"title": "...", "area": "...", "pdf": "path.pdf"}],              # finished PDFs (e.g. mission letter)
  "ack_pdf": "path/to/ack.pdf" | null                     # null = generate the standard monthly ack
}
Stdlib + python-docx + pypdf + LibreOffice (soffice). House format per the policy-lifecycle skill.
"""
import json, os, subprocess, sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pypdf import PdfReader, PdfWriter

NAVY = RGBColor(0x2D, 0x1A, 0x5E); BLUE = RGBColor(0x00, 0x99, 0xDD); GREY = RGBColor(0x59, 0x59, 0x59)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HERE = os.path.dirname(os.path.abspath(__file__))


def para(doc, text, size, color=None, bold=False, after=4, align=None):
    p = doc.add_paragraph(); r = p.add_run(text); r.font.size = Pt(size); r.bold = bold
    if color is not None: r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(after)
    if align: p.alignment = align
    return p


def navy_box(doc, text, size=16):
    tb = doc.add_table(rows=1, cols=1); c = tb.cell(0, 0)
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), '2D1A5E'); c._tc.get_or_add_tcPr().append(sh)
    c.text = ''; p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = WHITE
    doc.add_paragraph()


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def header(doc, title, sub):
    para(doc, 'VALLEY PAWN', 9, BLUE, True, 0)
    para(doc, title, 22, NAVY, True, 0)
    para(doc, sub, 9.5, GREY, False, 10)


def build(manifest_path):
    m = json.load(open(manifest_path))
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    base = os.path.join(out, f"{m['slug']}_Policy_Update")
    doc = Document(); s = doc.sections[0]
    s.page_width = Inches(8.5); s.page_height = Inches(11)
    s.left_margin = s.right_margin = Inches(0.75); s.top_margin = s.bottom_margin = Inches(0.5)
    st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(12)

    # ---- cover
    cf = float(m.get('cover_font', 11.5))  # optional manifest key; default unchanged
    header(doc, f"Policy Update — {m['month']}", f"Policy Day {m['policy_day']}   ·   All stores   ·   Sign in Gusto by {m['sign_by']}")
    navy_box(doc, 'One signature covers everything in this packet.', 16)
    para(doc, "What's new this month", 13, NAVY, True, 4)
    for b in m['whats_new']:
        p = doc.add_paragraph(); r = p.add_run('→  ' + b); r.font.size = Pt(cf); p.paragraph_format.space_after = Pt(4)
    pol = m.get('policies', [])
    mdp = m.get('md_pages', [])
    att = m.get('attachments', [])
    items = [(x['title'], x.get('area', ''), x.get('starts', '')) for x in pol + mdp + att]
    if items:
        para(doc, 'In this packet, in order', 13, NAVY, True, 4).paragraph_format.space_before = Pt(8)
        for t, area, starts in items:
            tail = (f" — {area}" if area else '') + (f" · starts {starts}" if starts else '')
            p = doc.add_paragraph(); r = p.add_run(f"→  {t}{tail}"); r.font.size = Pt(cf)
            p.paragraph_format.space_after = Pt(3)
    p = para(doc, f"Current manuals: Employee Handbook v{m['handbook']} and Policies & Procedures Manual v{m['pp']} — in Gusto under Documents. "
                  "Questions: your Store Manager, Preston, or #ask-goldilocks.", 10, GREY, False, 4)
    p.paragraph_format.space_before = Pt(10)

    # ---- one page per policy (house format, no per-policy signature; the packet ack covers them)
    for pp in pol:
        page_break(doc)
        header(doc, pp['title'], f"Starts {pp['starts']}   ·   All stores")
        navy_box(doc, pp['box'], 17)
        for ln in pp['lines']:
            p = doc.add_paragraph(); r = p.add_run(ln if ln.startswith('→') else '→  ' + ln); r.font.size = Pt(12)
            p.paragraph_format.space_after = Pt(6)

    # ---- longer policies written in markdown (e.g. bonus program), rendered plainly
    import re as _re
    for mp in mdp:
        page_break(doc)
        header(doc, mp['title'], f"Starts {mp.get('starts','')}   ·   All stores")
        src = mp['md'] if os.path.isabs(mp['md']) else os.path.join(HERE, mp['md'])
        rows = []
        def flush():
            if not rows: return
            cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not _re.match(r'^\|?\s*-+', r.strip().strip('|').strip())]
            tb = doc.add_table(rows=len(cells), cols=max(len(c) for c in cells)); tb.style = 'Table Grid'
            for i, c in enumerate(cells):
                for j, v in enumerate(c):
                    rr = tb.cell(i, j).paragraphs[0].add_run(_re.sub(r'[*_`]', '', v)); rr.font.size = Pt(9.5); rr.bold = (i == 0)
            doc.add_paragraph(); rows.clear()
        for line in open(src).read().splitlines():
            if line.startswith('|'): rows.append(line); continue
            flush()
            t = line.strip()
            if not t or t.startswith('# ') or t.startswith('_Generated') or t.startswith('**Full Circle'): continue
            clean = _re.sub(r'\*\*|__|`', '', t)
            if t.startswith('## '): para(doc, clean[3:], 13, NAVY, True, 3).paragraph_format.space_before = Pt(6)
            elif t.startswith(('- ', '* ')): p = doc.add_paragraph(); r = p.add_run('→  ' + clean[2:]); r.font.size = Pt(10.5); p.paragraph_format.space_after = Pt(2)
            else: para(doc, clean, 10.5, None, False, 4)
        flush()

    # ---- standard monthly acknowledgment (only when no ack_pdf is attached)
    if not m.get('ack_pdf'):
        page_break(doc)
        header(doc, f"Acknowledgment — Policy Update, {m['month']}", 'Signed once in Gusto')
        txt = (f"I received the {m['month']} Policy Update, including every policy listed on page 1. I have read it, asked about anything "
               f"I did not understand, and will follow it, together with the Employee Handbook (v{m['handbook']}) and the Policies & "
               "Procedures Manual (v" + m['pp'] + "), which I can read at any time in Gusto. The Company may change or end any policy at any "
               "time without notice. These policies are not an employment contract and do not change at-will employment: either the "
               "Company or I may end employment at any time, with or without cause or notice. Nothing in them limits my right to talk "
               "about pay or working conditions or to contact any government agency.")
        para(doc, txt, 10, None, False, 14)
        sig = doc.add_table(rows=2, cols=4)
        for j, (u, l) in enumerate([('_' * 17, 'Signature (via Gusto)'), ('_' * 15, 'Printed Name'), ('_' * 15, 'Store'), ('_' * 15, 'Date')]):
            sig.cell(0, j).text = u; rr = sig.cell(1, j).paragraphs[0].add_run(l); rr.font.size = Pt(8); rr.font.color.rgb = GREY

    doc.save(base + '.docx')
    import tempfile, shutil   # convert in a private temp dir (a stale LibreOffice lock or a synced file in out/ made soffice fail 2026-10-21)
    tmp = tempfile.mkdtemp(prefix='pu_'); prof = 'file://' + os.path.join(tmp, 'lo_profile')
    subprocess.run(['soffice', f'-env:UserInstallation={prof}', '--headless', '--convert-to', 'pdf', '--outdir', tmp, base + '.docx'],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    with open(os.path.join(tmp, os.path.basename(base) + '.pdf'), 'rb') as src, open(base + '.pdf', 'wb') as dst: dst.write(src.read())
    shutil.rmtree(tmp, ignore_errors=True)
    extra = [a['pdf'] for a in att] + ([m['ack_pdf']] if m.get('ack_pdf') else [])
    if extra:
        extra = [p if os.path.isabs(p) else os.path.join(HERE, p) for p in extra]
        w = PdfWriter()
        for src in [base + '.pdf'] + extra:
            for pg in PdfReader(src).pages: w.add_page(pg)
        with open(base + '.pdf', 'wb') as f: w.write(f)
    n = len(PdfReader(base + '.pdf').pages)
    subprocess.run(['pdftoppm', '-r', '60', '-png', base + '.pdf', base + '_page'], check=False)
    print(f'OK {base}.pdf pages={n}')


if __name__ == '__main__':
    build(sys.argv[1])
