"""Valley Pawn Mission & Code poster — print-ready PDFs with 0.125in bleed.
Studio palette (vp-brand-studio v2): navy #0F1A2E, gold #B08A3E, ivory #F4EDE0.
Type: Playfair Display (display) + Inter (body)."""
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

F = '/tmp/f/'
for n in ['PF-Bold', 'PF-Black', 'PF-Reg', 'PF-Italic', 'PF-BoldItalic',
          'Inter-Reg', 'Inter-Med', 'Inter-Semi', 'Inter-Bold']:
    pdfmetrics.registerFont(TTFont(n, F + n + '.ttf'))

NAVY, GOLD, IVORY = HexColor('#0F1A2E'), HexColor('#B08A3E'), HexColor('#F4EDE0')
INK2 = HexColor('#3A4458')
LOGO = ImageReader(F + 'logo_t.png')
LOGO_AR = 1879 / 3380

MISSION = ("To be the most trusted name in the Valley — treating every customer "
           "with honesty, fairness and respect, and earning their business every single day.")
CODE = [
    ("We Tell the Truth.",
     "No exaggerations. No half-truths. No fine print. We are honest with our customers, "
     "with each other, and with ourselves."),
    ("We Play It Straight.",
     "Every appraisal fair. Every deal by the book. We never cut corners, "
     "because a win that isn’t earned isn’t a win."),
    ("We Protect What’s Entrusted to Us.",
     "Every item, every dollar and every minute on the clock belongs to someone. "
     "We never take what isn’t ours."),
    ("We Lead With Kindness.",
     "Everyone who walks through our door is treated with dignity and respect — "
     "no judgment, no exceptions."),
    ("The Customer Comes First.",
     "Every decision starts with one question: what is right for the customer?"),
    ("Good Enough Never Is.",
     "Mediocrity has no place here. We take pride in our work, we do it right, "
     "and we get better every day."),
]
STORES = "CULPEPER  ·  WAYNESBORO  ·  HARRISONBURG  ·  LEXINGTON  ·  ROANOKE"


def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def tracked(c, text, font, size, x, y, track, center=True):
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    cx = x - total / 2 if center else x
    c.setFont(font, size)
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch); cx += w + track
    return total


def build(path, W_in, H_in, bleed=0.125):
    B = bleed * inch
    W, H = W_in * inch, H_in * inch
    c = canvas.Canvas(path, pagesize=(W + 2 * B, H + 2 * B), initialFontName='Inter-Reg')
    c.setTitle('Valley Pawn - Our Mission & The Valley Pawn Code')
    c.setAuthor('Valley Pawn')
    c.translate(B, B)
    u = W_in / 18.0  # scale factor: 1.0 at 18in wide

    # background (full bleed)
    c.setFillColor(IVORY); c.rect(-B, -B, W + 2 * B, H + 2 * B, stroke=0, fill=1)

    # bottom navy band (full bleed)
    band_h = 2.55 * inch * u
    c.setFillColor(NAVY); c.rect(-B, -B, W + 2 * B, band_h + B, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(2.2 * u); c.line(-B, band_h, W + B, band_h)

    # inset double gold frame (above band)
    m = 0.6 * inch * u
    c.setLineWidth(1.6 * u); c.rect(m, band_h + m * 0.6, W - 2 * m, H - band_h - m * 1.6, stroke=1, fill=0)
    c.setLineWidth(0.6 * u)
    g = 0.12 * inch * u
    c.rect(m + g, band_h + m * 0.6 + g, W - 2 * (m + g), H - band_h - m * 1.6 - 2 * g, stroke=1, fill=0)

    # --- band content
    c.setFillColor(IVORY)
    size = 64 * u
    c.setFont('PF-BoldItalic', size)
    c.drawCentredString(W / 2, band_h * 0.48, "What’s Right Is Right.")
    c.setFillColor(GOLD)
    tracked(c, STORES, 'Inter-Semi', 18 * u, W / 2, band_h * 0.2, 2.6 * u)

    # --- top content
    top = H - m - 1.05 * inch * u
    logo_w = 4.6 * inch * u
    logo_h = logo_w * LOGO_AR
    c.drawImage(LOGO, W / 2 - logo_w / 2, top - logo_h, logo_w, logo_h, mask='auto')
    y = top - logo_h - 0.95 * inch * u

    c.setFillColor(GOLD)
    tracked(c, "OUR MISSION", 'Inter-Bold', 20 * u, W / 2, y, 6 * u)
    y -= 1.0 * inch * u

    c.setFillColor(NAVY)
    ms = 46 * u
    lines = wrap(MISSION, 'PF-Italic', ms, W - 2 * m - 2.4 * inch * u)
    c.setFont('PF-Italic', ms)
    for ln in lines:
        c.drawCentredString(W / 2, y, ln); y -= ms * 1.32
    y -= 0.25 * inch * u

    # ornament rule
    c.setStrokeColor(GOLD); c.setLineWidth(1.4 * u)
    rw = 2.2 * inch * u
    c.line(W / 2 - rw - 0.3 * inch * u, y, W / 2 - 0.3 * inch * u, y)
    c.line(W / 2 + 0.3 * inch * u, y, W / 2 + rw + 0.3 * inch * u, y)
    c.setFillColor(GOLD)
    d = 0.11 * inch * u
    p = c.beginPath(); p.moveTo(W / 2, y + d); p.lineTo(W / 2 + d, y); p.lineTo(W / 2, y - d); p.lineTo(W / 2 - d, y); p.close()
    c.drawPath(p, stroke=0, fill=1)
    y -= 0.95 * inch * u

    c.setFillColor(NAVY)
    tracked(c, "THE VALLEY PAWN CODE", 'Inter-Bold', 20 * u, W / 2, y, 6 * u)
    y -= 0.55 * inch * u

    # --- six standards in 2 columns x 3 rows; fill remaining space evenly
    area_top = y
    area_bot = band_h + m * 0.6 + g + 0.55 * inch * u
    col_gap = 0.8 * inch * u
    inner_l = m + g + 0.7 * inch * u
    col_w = (W - 2 * inner_l - col_gap) / 2
    num_w = 1.15 * inch * u
    ts, bs = 36 * u, 22 * u
    text_w = col_w - num_w

    blocks = []
    for title, body in CODE:
        tl = wrap(title, 'PF-Bold', ts, text_w)
        bl = wrap(body, 'Inter-Reg', bs, text_w)
        h = len(tl) * ts * 1.15 + 0.14 * inch * u + len(bl) * bs * 1.45
        blocks.append((tl, bl, h))
    rows = [max(blocks[i][2], blocks[i + 1][2]) for i in (0, 2, 4)]
    free = (area_top - area_bot) - sum(rows)
    if free < 0:
        raise SystemExit(f'overflow {path}: {free / inch:.2f}in')
    gap = free / 3
    yy = area_top - gap / 2
    for r in range(3):
        for col in range(2):
            i = r * 2 + col
            tl, bl, _ = blocks[i]
            x = inner_l + col * (col_w + col_gap)
            c.setFillColor(GOLD); c.setFont('PF-Bold', 40 * u)
            c.drawString(x, yy - 34 * u, ['I','II','III','IV','V','VI'][i])
            c.setStrokeColor(GOLD); c.setLineWidth(0.8 * u)
            ty = yy - ts
            c.setFillColor(NAVY); c.setFont('PF-Bold', ts)
            for ln in tl:
                c.drawString(x + num_w, ty, ln); ty -= ts * 1.15
            ty -= 0.14 * inch * u - ts * 0.15
            c.setFillColor(INK2); c.setFont('Inter-Reg', bs)
            for ln in bl:
                ty -= bs * 0.2
                c.drawString(x + num_w, ty, ln); ty -= bs * 1.25
        yy -= rows[r] + gap

    c.showPage(); c.save()
    print('ok', path, f'free={free / inch:.2f}in')


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    build(f'{out}/VP_Mission_Poster_18x24_PRINT.pdf', 18, 24)
    build(f'{out}/VP_Mission_Poster_24x36_PRINT.pdf', 24, 36)
    build(f'{out}/VP_Mission_Poster_11x17_PRINT.pdf', 11, 17)
    build(f'{out}/VP_Mission_Letter_8.5x11.pdf', 8.5, 11, bleed=0)
