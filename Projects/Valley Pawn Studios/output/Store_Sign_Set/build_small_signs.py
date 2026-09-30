"""Valley Pawn small signs in the 2026 studio style (navy #0F1A2E, gold #B08A3E, ivory #F4EDE0,
Playfair Display + Inter) — matches the mission poster and the signs.com 'FFL Transfers $25' saved design.
  - Smile for the Camera: 6in circle (0.125in bleed, square page; signs.com cuts the circle)
  - FFL Transfers $25: 8x6in, store-specific footer line
"""
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

F = '/tmp/f/'
for n in ['PF-Bold', 'PF-Black', 'PF-Italic', 'PF-BoldItalic', 'Inter-Reg', 'Inter-Semi', 'Inter-Bold']:
    pdfmetrics.registerFont(TTFont(n, F + n + '.ttf'))
NAVY, GOLD, IVORY = HexColor('#0F1A2E'), HexColor('#B08A3E'), HexColor('#F4EDE0')


def tracked(c, text, font, size, x, y, track):
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    cx = x - total / 2
    c.setFont(font, size)
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch); cx += w + track


def fit(text, font, size, maxw):
    while pdfmetrics.stringWidth(text, font, size) > maxw:
        size -= 0.5
    return size


def smile(path, D_in=6.0, bleed=0.125):
    B = bleed * inch; D = D_in * inch
    c = canvas.Canvas(path, pagesize=(D + 2 * B, D + 2 * B), initialFontName='Inter-Reg')
    c.setTitle('Valley Pawn - Smile for the Camera'); c.translate(B, B)
    s = D_in / 6.0
    cx = cy = D / 2
    c.setFillColor(NAVY); c.rect(-B, -B, D + 2 * B, D + 2 * B, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.2 * s); c.circle(cx, cy, D / 2 - 0.22 * inch * s, stroke=1, fill=0)
    c.setLineWidth(0.8 * s); c.circle(cx, cy, D / 2 - 0.34 * inch * s, stroke=1, fill=0)
    c.setFillColor(GOLD)
    tracked(c, "VALLEY PAWN", 'Inter-Bold', 10.5 * s, cx, cy + 1.72 * inch * s, 3.2 * s)
    c.setStrokeColor(GOLD); c.setLineWidth(0.8 * s)
    c.line(cx - 0.9 * inch * s, cy + 1.52 * inch * s, cx + 0.9 * inch * s, cy + 1.52 * inch * s)
    c.setFillColor(IVORY)
    c.setFont('PF-Italic', 26 * s); c.drawCentredString(cx, cy + 0.95 * inch * s, "Dang…")
    c.setFont('PF-Italic', 26 * s); c.drawCentredString(cx, cy + 0.50 * inch * s, "you look fine!")
    c.setFillColor(GOLD)
    sz = fit("Smile", 'PF-Black', 58 * s, 3.6 * inch * s)
    c.setFont('PF-Black', sz); c.drawCentredString(cx, cy - 0.32 * inch * s, "Smile")
    c.setFillColor(IVORY)
    sz = fit("for the camera.", 'PF-Bold', 27 * s, 3.9 * inch * s)
    c.setFont('PF-Bold', sz); c.drawCentredString(cx, cy - 0.82 * inch * s, "for the camera.")
    # diamond rule
    y = cy - 1.25 * inch * s
    c.setStrokeColor(GOLD); c.setLineWidth(0.8 * s)
    c.line(cx - 0.75 * inch * s, y, cx - 0.12 * inch * s, y); c.line(cx + 0.12 * inch * s, y, cx + 0.75 * inch * s, y)
    d = 0.05 * inch * s
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(cx, y + d); p.lineTo(cx + d, y); p.lineTo(cx, y - d); p.lineTo(cx - d, y); p.close()
    c.drawPath(p, stroke=0, fill=1)
    tracked(c, "WHAT’S RIGHT IS RIGHT", 'Inter-Semi', 7.2 * s, cx, cy - 1.62 * inch * s, 1.6 * s)
    c.showPage(); c.save(); print('ok', path)


def ffl(path, store, W_in=8.0, H_in=6.0, bleed=0.125):
    B = bleed * inch; W, H = W_in * inch, H_in * inch
    c = canvas.Canvas(path, pagesize=(W + 2 * B, H + 2 * B), initialFontName='Inter-Reg')
    c.setTitle(f'Valley Pawn - FFL Transfers $25 - {store}'); c.translate(B, B)
    u = W_in / 8.0
    I = inch * u
    c.setFillColor(NAVY); c.rect(-B, -B, W + 2 * B, H + 2 * B, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(1.4 * u)
    m = 0.28 * I
    c.rect(m, m, W - 2 * m, H - 2 * m, stroke=1, fill=0)
    cx = W / 2
    c.setFillColor(GOLD); tracked(c, "VALLEY PAWN", 'Inter-Bold', 14 * u, cx, H - 1.05 * I, 4.2 * u)
    c.setLineWidth(0.8 * u); c.line(cx - 1.4 * I, H - 1.25 * I, cx + 1.4 * I, H - 1.25 * I)
    c.setFillColor(IVORY)
    sz = fit("FFL TRANSFERS", 'PF-Black', 44 * u, W - 1.4 * I)
    c.setFont('PF-Black', sz); c.drawCentredString(cx, H - 2.05 * I, "FFL TRANSFERS")
    c.setFillColor(GOLD); c.setFont('PF-Black', 76 * u); c.drawCentredString(cx, H - 3.17 * I, "$25")
    c.setFillColor(IVORY); tracked(c, "PER FIREARM", 'Inter-Semi', 13 * u, cx, H - 3.62 * I, 3 * u)
    c.setStrokeColor(GOLD); c.line(cx - 1.4 * I, H - 3.9 * I, cx + 1.4 * I, H - 3.9 * I)
    c.setFillColor(IVORY)
    tracked(c, f"LICENSED FEDERAL FIREARMS DEALER · {store.upper()}", 'Inter-Semi', 9.5 * u, cx, H - 4.3 * I, 1.2 * u)
    y = 0.72 * I
    c.setStrokeColor(GOLD); c.setLineWidth(0.8 * u)
    c.line(cx - 1.9 * I, y, cx - 0.12 * I, y); c.line(cx + 0.12 * I, y, cx + 1.9 * I, y)
    d = 0.05 * I; c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(cx, y + d); p.lineTo(cx + d, y); p.lineTo(cx, y - d); p.lineTo(cx - d, y); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.showPage(); c.save(); print('ok', path)


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    smile(f'{out}/VP_Smile_for_the_Camera_6in_circle_2026.pdf')
    for st in ['Culpeper', 'Waynesboro', 'Harrisonburg', 'Lexington', 'Roanoke']:
        ffl(f'{out}/VP_FFL_Transfers_25_8x6_{st}.pdf', st)
