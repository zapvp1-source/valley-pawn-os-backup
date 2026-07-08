#!/usr/bin/env python3
"""
Valley Pawn acrylic counter sign — v3

Same brand-bible-compliant composition as v2, but scaled up to 8x11 portrait
to meet Vistaprint Custom Acrylic Signs' 8-inch minimum width (vertical orientation).

Scaling ratio vs v2 (5x7):
  width:  8/5  = 1.60x
  height: 11/7 = 1.571x
  -> average scale 1.586 — applied uniformly to all element sizes/positions.

Output: 8.25 x 11.25 inches page (8x11 trim + 1/8" bleed) with crop marks, fonts embedded.

Usage:
  python3 generate_acrylic_sign_v3.py "https://thevalleypawn.com/lexington" --store Lexington
"""
from __future__ import annotations
import argparse
import io
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor, white, Color
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ----- Locked palette ---------------------------------------------------------
NAVY      = HexColor("#0F1A2E")
IVORY     = HexColor("#F4EDE0")
BRASS     = HexColor("#B08A3E")
IVORY_60  = Color(0xF4/255, 0xED/255, 0xE0/255, alpha=0.65)
IVORY_75  = Color(0xF4/255, 0xED/255, 0xE0/255, alpha=0.80)

# ----- Print spec — 8x11 (Vistaprint Custom Acrylic Signs minimum width) -----
BLEED      = 0.125 * inch
SAFETY     = 0.32  * inch          # scaled from 0.20 (v2) by 1.6x
TRIM_W     = 8.0   * inch
TRIM_H     = 11.0  * inch
PAGE_W     = TRIM_W + 2 * BLEED
PAGE_H     = TRIM_H + 2 * BLEED
SCALE      = 1.6                    # 8/5 width scale, applied to all element sizes

# ----- Font registration ------------------------------------------------------
HERE = Path(__file__).parent
FONT_DIR = HERE / "fonts"

def register_fonts():
    fonts = {
        "PlayfairItalic": FONT_DIR / "PlayfairDisplay-Italic.ttf",
        "Playfair":       FONT_DIR / "PlayfairDisplay.ttf",
        "Inter":          FONT_DIR / "Inter.ttf",
    }
    for name, path in fonts.items():
        if not path.exists():
            raise SystemExit(f"missing font {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))

# ----- QR ---------------------------------------------------------------------
def make_qr(url: str, box_size_px: int = 32):
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=box_size_px, border=2)
    qr.add_data(url); qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

# ----- Helpers ----------------------------------------------------------------
def thin_rule(c, x1, y, x2, color=BRASS, weight=1.3):
    c.setStrokeColor(color); c.setLineWidth(weight); c.line(x1, y, x2, y)

def draw_string_with_kerning(c, x, y, text, font, size, color, kerning=0.0):
    t = c.beginText(x, y); t.setFont(font, size); t.setFillColor(color)
    if kerning: t.setCharSpace(kerning)
    t.textOut(text); c.drawText(t)

def measure(text, font, size, kerning=0.0):
    base = pdfmetrics.stringWidth(text, font, size)
    if kerning and len(text) > 1: base += kerning * (len(text) - 1)
    return base

def center_string(c, cx, y, text, font, size, color, kerning=0.0):
    w = measure(text, font, size, kerning)
    draw_string_with_kerning(c, cx - w/2, y, text, font, size, color, kerning)

# ----- The sign ---------------------------------------------------------------
def draw_sign(c, url: str, store: str, logo_path: str):
    # 1. NAVY FULL-BLEED BACKGROUND
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    cx = PAGE_W / 2
    inner_left = BLEED + SAFETY
    inner_right = PAGE_W - BLEED - SAFETY
    inner_w = inner_right - inner_left

    # 2. TOP HAIRLINE GOLD RULE
    y_top_rule = PAGE_H - BLEED - 0.48 * inch
    thin_rule(c, inner_left, y_top_rule, inner_right, BRASS, 1.3)

    # 3. LOGO
    logo_max_w = inner_w * 0.70
    logo_max_h = 1.20 * inch
    try:
        from PIL import Image
        with Image.open(logo_path) as im:
            iw, ih = im.size
            aspect = iw / ih
    except Exception:
        aspect = 5.2
    if logo_max_w / aspect <= logo_max_h:
        lw, lh = logo_max_w, logo_max_w / aspect
    else:
        lh, lw = logo_max_h, logo_max_h * aspect
    logo_y = y_top_rule - lh - 0.29 * inch
    c.drawImage(logo_path, cx - lw/2, logo_y, width=lw, height=lh,
                preserveAspectRatio=True, mask='auto')

    # 4. CAPTION
    if store and store.lower() not in ("brand", "all", "all locations"):
        cap = f"VALLEY PAWN  ·  {store.upper()}"
    else:
        cap = "FAMILY-OWNED  ·  5 VIRGINIA LOCATIONS"
    center_string(c, cx, logo_y - 0.35 * inch, cap, "Inter", 13.5, IVORY_75, kerning=2.2)

    # 5. HEADLINE — "Win $100" + "Every Month."
    headline_font = "PlayfairItalic"
    line1_size = 90
    line1_y = logo_y - 1.52 * inch

    win_w        = measure("Win ", headline_font, line1_size)
    dollar_w     = measure("$",    headline_font, line1_size)
    onehundred_w = measure("100",  headline_font, line1_size)
    line1_total  = win_w + dollar_w + onehundred_w
    l1_x = cx - line1_total / 2
    c.setFont(headline_font, line1_size)
    c.setFillColor(IVORY); c.drawString(l1_x, line1_y, "Win ")
    c.setFillColor(BRASS); c.drawString(l1_x + win_w, line1_y, "$")
    c.setFillColor(IVORY); c.drawString(l1_x + win_w + dollar_w, line1_y, "100")

    line2_size = 60
    line2_y = line1_y - 0.93 * inch
    center_string(c, cx, line2_y, "Every Month.", headline_font, line2_size, IVORY)

    # 6. SUBHEAD
    sub = "Scan to enter   ·   New winner every month   ·   No purchase necessary"
    center_string(c, cx, line2_y - 0.58 * inch, sub, "Inter", 12.5, IVORY_60, kerning=1.0)

    # 7. QR CARD
    qr_size = 3.92 * inch
    qr_x = cx - qr_size / 2
    qr_y = 2.08 * inch

    pad = 0.26 * inch
    c.setFillColor(IVORY); c.setStrokeColor(BRASS); c.setLineWidth(2.0)
    c.roundRect(qr_x - pad, qr_y - pad, qr_size + 2*pad, qr_size + 2*pad,
                radius=13, fill=1, stroke=1)

    qr_img = make_qr(url, box_size_px=36)
    buf = io.BytesIO(); qr_img.save(buf, format="PNG"); buf.seek(0)
    c.drawImage(ImageReader(buf), qr_x, qr_y, width=qr_size, height=qr_size)

    # 8. PLATFORM STRIP
    platforms = "FACEBOOK   ·   INSTAGRAM   ·   X   ·   TIKTOK   ·   YOUTUBE"
    center_string(c, cx, qr_y - 0.45 * inch, platforms, "Inter", 12.5, IVORY_75, kerning=2.4)

    # 9. BOTTOM HAIRLINE GOLD RULE
    y_bot_rule = 0.88 * inch
    thin_rule(c, inner_left, y_bot_rule, inner_right, BRASS, 1.3)

    # 10. FINE PRINT
    fine = "VA RESIDENTS 18+   ·   thevalleypawn.com/giveaway-rules"
    center_string(c, cx, y_bot_rule - 0.29 * inch, fine, "Inter", 10.5, IVORY_60, kerning=0.8)

    # 11. FOOTER
    center_string(c, cx, y_bot_rule - 0.57 * inch, "thevalleypawn.com", "Inter", 15.5, IVORY, kerning=1.2)

    # 12. CROP MARKS
    c.setStrokeColor(white); c.setLineWidth(0.5)
    mark = 0.16 * inch; gap = 0.09 * inch
    for (mx, my, dx_in, dy_in) in [
        (BLEED, BLEED, -1, -1),
        (PAGE_W - BLEED, BLEED, 1, -1),
        (BLEED, PAGE_H - BLEED, -1, 1),
        (PAGE_W - BLEED, PAGE_H - BLEED, 1, 1),
    ]:
        c.line(mx + dx_in * gap, my, mx + dx_in * (gap + mark), my)
        c.line(mx, my + dy_in * gap, mx, my + dy_in * (gap + mark))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("url")
    p.add_argument("--store", default="all")
    p.add_argument("--out", default=None)
    p.add_argument("--logo", default=str(HERE / "brand_assets" / "valley_pawn_landscape_transparent.png"))
    args = p.parse_args()

    register_fonts()
    out = Path(args.out) if args.out else HERE / f"acrylic_signs_v3/{args.store.lower()}_8x11.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=(PAGE_W, PAGE_H))
    draw_sign(c, args.url, args.store, args.logo)
    c.showPage(); c.save()
    print(f"v3 sign written: {out}")
    print(f"  Trim:  8.00 x 11.00 inches (Vistaprint 8\" min width compliant)")
    print(f"  Page:  {PAGE_W/inch:.3f} x {PAGE_H/inch:.3f} inches (with 1/8\" bleed)")
    print(f"  URL:   {args.url}")
    print(f"  Store: {args.store}")


if __name__ == "__main__":
    main()
