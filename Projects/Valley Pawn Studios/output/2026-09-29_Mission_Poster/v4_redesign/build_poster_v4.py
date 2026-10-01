"""Valley Pawn Mission poster v4 (redesign 9/30: thin footer band, bigger logo, no script/italic fonts, tighter top) — two-fold (customers + team), everyday language.
Studio palette: navy #0F1A2E, gold #B08A3E, ivory #F4EDE0. Playfair Display + Inter."""
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

F = os.path.dirname(os.path.abspath(__file__)) + '/../'
for n in ['PF-Bold', 'Inter-Reg', 'Inter-Semi', 'Inter-Bold']:
    pdfmetrics.registerFont(TTFont(n, F + n + '.ttf'))

NAVY, GOLD, IVORY = HexColor('#0F1A2E'), HexColor('#B08A3E'), HexColor('#F4EDE0')
INK2, IVORY2, PANEL = HexColor('#3A4458'), HexColor('#D9D2C3'), HexColor('#EBE2D0')
LOGO = ImageReader(F + 'logo_t.png')
LOGO_AR = 1879 / 3380

SIDES = [
    dict(label="TO OUR CUSTOMERS",
         line="Every customer gets a fair deal, the straight truth, and respect. Every time.",
         items=[
             ("Straight talk.", "We’ll always tell you the truth, plain and simple."),
             ("A fair deal.", "Fair prices, fair loans, and everything up front."),
             ("Respect for everyone.", "Whatever brings you in, you’ll be treated like family."),
             ("You come first.", "It’s not about us. It’s always about you, in every situation."),
             ("We stand behind it.", "Everything we sell comes with our 30-day warranty."),
         ]),
    dict(label="TO OUR TEAM",
         line="A place where honest people can work, always do the right thing, work hard, and take care of their families.",
         items=[
             ("Be honest and play fair.", "Tell the truth and do every deal by the book."),
             ("Be kind.", "To every customer and every coworker."),
             ("Treat it like it’s yours.", "Every item, every dollar, every minute on the clock."),
             ("Bring your best.", "Take pride in your work and get a little better every day."),
             ("Have each other’s back.", "We win as a team and fix problems as a team."),
         ]),
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
    # avoid a one-word last line
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        prev = lines[-2].split()
        lines[-2], lines[-1] = ' '.join(prev[:-1]), prev[-1] + ' ' + lines[-1]
    return lines


def tracked(c, text, font, size, x, y, track):
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    cx = x - total / 2
    c.setFont(font, size)
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch); cx += w + track


def build(path, W_in, H_in, bleed=0.125):
    B = bleed * inch
    W, H = W_in * inch, H_in * inch
    c = canvas.Canvas(path, pagesize=(W + 2 * B, H + 2 * B), initialFontName='Inter-Reg')
    c.setTitle('Valley Pawn - Our Mission'); c.setAuthor('Valley Pawn')
    c.translate(B, B)
    u = W_in / 18.0
    I = inch * u

    c.setFillColor(IVORY); c.rect(-B, -B, W + 2 * B, H + 2 * B, stroke=0, fill=1)

    # bottom band
    band_h = 1.35 * I
    c.setFillColor(NAVY); c.rect(-B, -B, W + 2 * B, band_h + B, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(2.2 * u); c.line(-B, band_h, W + B, band_h)
    c.setFillColor(IVORY); tracked(c, "WHAT’S RIGHT IS RIGHT.", 'PF-Bold', 34 * u, W / 2, band_h * 0.50, 2.0 * u)
    c.setFillColor(GOLD)
    tracked(c, STORES, 'Inter-Semi', 16 * u, W / 2, band_h * 0.20, 2.4 * u)

    # top band (matches bottom band)
    c.setFillColor(NAVY); c.rect(-B, H - band_h, W + 2 * B, band_h + B, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(2.2 * u); c.line(-B, H - band_h, W + B, H - band_h)
    c.setFillColor(GOLD); tracked(c, "OUR MISSION", 'Inter-Bold', 30 * u, W / 2, H - band_h * 0.58, 9 * u)

    # logo + headline
    m = 0.75 * I
    top = H - band_h - 0.45 * I
    lw = 5.0 * I; lh = lw * LOGO_AR
    c.drawImage(LOGO, W / 2 - lw / 2, top - lh, lw, lh, mask='auto')
    y = top - lh - 1.3 * I
    c.setFillColor(NAVY); c.setFont('PF-Bold', 60 * u)
    c.drawCentredString(W / 2, y, "Do right by our customers.")
    y -= 0.95 * I
    c.drawCentredString(W / 2, y, "Do right by each other.")
    y -= 0.7 * I

    # two panels
    gap = 0.45 * I
    pw = (W - 2 * m - gap) / 2
    p_top = y
    p_bot = band_h + 0.55 * I
    ph = p_top - p_bot
    pad = 0.55 * I
    tw = pw - 2 * pad
    lead_s, body_s, line_s = 33 * u, 23 * u, 24 * u

    for k, side in enumerate(SIDES):
        x0 = m + k * (pw + gap)
        dark = (k == 1)
        c.setFillColor(NAVY if dark else PANEL)
        c.roundRect(x0, p_bot, pw, ph, 0.18 * I, stroke=0, fill=1)
        c.setStrokeColor(GOLD); c.setLineWidth(1.2 * u)
        c.roundRect(x0 + 0.12 * I, p_bot + 0.12 * I, pw - 0.24 * I, ph - 0.24 * I, 0.12 * I, stroke=1, fill=0)
        cx = x0 + pw / 2
        yy = p_top - 0.85 * I
        c.setFillColor(GOLD); tracked(c, side['label'], 'Inter-Bold', 19 * u, cx, yy, 5 * u)
        yy -= 0.75 * I
        c.setFillColor(IVORY if dark else NAVY); c.setFont('Inter-Semi', line_s)
        for ln in wrap(side['line'], 'Inter-Semi', line_s, tw):
            c.drawCentredString(cx, yy, ln); yy -= line_s * 1.3
        yy -= 0.2 * I
        c.setStrokeColor(GOLD); c.setLineWidth(1 * u)
        c.line(cx - 1.0 * I, yy, cx + 1.0 * I, yy)
        # items: distribute remaining space
        blocks = []
        for lead, body in side['items']:
            ll = wrap(lead, 'PF-Bold', lead_s, tw - 0.35 * I)
            bl = wrap(body, 'Inter-Reg', body_s, tw - 0.35 * I)
            blocks.append((ll, bl, len(ll) * lead_s * 1.12 + 0.08 * I + len(bl) * body_s * 1.4))
        avail = (yy - 0.3 * I) - (p_bot + 0.45 * I)
        free = avail - sum(b[2] for b in blocks)
        if free < 0:
            raise SystemExit(f'overflow {path} side {k}: {free / inch:.2f}in')
        g = free / len(blocks)
        yy -= 0.3 * I + g / 2
        for ll, bl, h in blocks:
            tx = x0 + pad + 0.35 * I
            c.setFillColor(GOLD)
            d = 0.07 * I
            c.circle(x0 + pad + 0.1 * I, yy - lead_s * 0.33, d, stroke=0, fill=1)
            ty = yy - lead_s * 0.72
            c.setFillColor(IVORY if dark else NAVY); c.setFont('PF-Bold', lead_s)
            for ln in ll:
                c.drawString(tx, ty, ln); ty -= lead_s * 1.12
            ty -= 0.08 * I
            c.setFillColor(IVORY2 if dark else INK2); c.setFont('Inter-Reg', body_s)
            for ln in bl:
                c.drawString(tx, ty, ln); ty -= body_s * 1.4
            yy -= h + g
    c.showPage(); c.save()
    print('ok', path)


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    build(f'{out}/VP_Mission_v4_18x24_PRINT.pdf', 18, 24)
    build(f'{out}/VP_Mission_v4_24x36_PRINT.pdf', 24, 36)
    build(f'{out}/VP_Mission_v4_11x17_PRINT.pdf', 11, 17)
    build(f'{out}/VP_Mission_v4_Letter_8.5x11.pdf', 8.5, 11, bleed=0)
