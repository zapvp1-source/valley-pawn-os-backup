#!/usr/bin/env python3
"""
Generate print-ready 3mm acrylic counter signs for Vistaprint.

Spec:
  - Trim size: 5"×7" portrait (or 6"×8" if --size 6x8)
  - Bleed: 0.125" (1/8") on all sides — extends past the trim line
  - Safety zone: 0.125" inside trim — text/QR must stay inside this margin
  - Resolution: 300 DPI
  - PDF output with crop marks and registration

Why proper bleed/safety:
  - Vistaprint trims the printed sheet; bleed prevents white slivers at the edge
  - Safety zone ensures critical content (QR, text) isn't cut off
  - Final acrylic = white plastic with full-color UV print

Usage:
    python3 generate_acrylic_sign.py "https://thevalleypawn.com/lexington" \
        --store "Lexington" --out signs/01_lexington_acrylic.pdf

    python3 generate_acrylic_sign.py "https://thevalleypawn.com/follow" \
        --store "All Locations" --size 6x8 --out signs/00_brand_acrylic.pdf
"""
from __future__ import annotations
import argparse
import io
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image

# Brand colors per vp-brand-studio
VP_BLUE = HexColor("#0F3D8F")
VP_RED = HexColor("#C7301F")
VP_CREAM = HexColor("#F8F4EC")
VP_INK = HexColor("#0A0A0A")

BLEED = 0.125 * inch      # 1/8" bleed on all sides
SAFETY = 0.125 * inch     # 1/8" inside trim where content must stay
TRIM_LINE_WEIGHT = 0.5    # crop mark line weight


def make_qr(url: str, box_size_px: int = 20) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # 30% — survives micro-scratches over time
        box_size=box_size_px,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def draw_sign(c: canvas.Canvas, url: str, store: str, trim_w: float, trim_h: float, logo_path: str | None):
    # Total page is trim + 2*bleed on each axis
    page_w = trim_w + 2 * BLEED
    page_h = trim_h + 2 * BLEED

    # === BLEED-FILL BACKGROUND (extends past trim) ===
    c.setFillColor(VP_CREAM)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Top accent bar (full-bleed)
    bar_h = 0.6 * inch
    c.setFillColor(VP_BLUE)
    c.rect(0, page_h - bar_h, page_w, bar_h, fill=1, stroke=0)

    # Bottom accent bar (full-bleed)
    bot_h = 0.45 * inch
    c.setFillColor(VP_RED)
    c.rect(0, 0, page_w, bot_h, fill=1, stroke=0)

    # === CONTENT AREA (inside safety zone) ===
    # All real content positioned relative to safety inset from page edges
    safe_x = BLEED + SAFETY
    safe_w = trim_w - 2 * SAFETY
    safe_center_x = page_w / 2

    # Logo (top) — use full available safe width for the landscape logo
    if logo_path and Path(logo_path).exists():
        try:
            logo_w = safe_w * 0.92
            logo_h = 1.1 * inch
            c.drawImage(
                logo_path,
                (page_w - logo_w) / 2,
                page_h - bar_h - logo_h - 0.10 * inch,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                mask='auto',
            )
        except Exception as e:
            print(f"[warn] logo: {e}", file=sys.stderr)

    # Headline
    headline_y = page_h - 2.4 * inch
    c.setFillColor(VP_INK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(safe_center_x, headline_y, "WIN $100 MONTHLY")

    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(safe_center_x, headline_y - 0.3 * inch, "Scan · Enter your email · You're in.")

    if store and store.lower() not in ("brand", "all locations", "all"):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(VP_BLUE)
        c.drawCentredString(safe_center_x, headline_y - 0.55 * inch, f"VALLEY PAWN — {store.upper()}")
        c.setFillColor(VP_INK)

    # QR code — large and centered, well within safety
    qr_size = min(safe_w * 0.85, 3.4 * inch) if trim_w >= 6 else min(safe_w * 0.92, 3.0 * inch)
    qr_x = (page_w - qr_size) / 2
    qr_y = bot_h + 0.5 * inch + (0.3 * inch if trim_w >= 6 else 0.2 * inch)

    # White QR backing card with subtle border
    pad = 0.14 * inch
    c.setFillColor(white)
    c.setStrokeColor(VP_BLUE)
    c.setLineWidth(2)
    c.roundRect(qr_x - pad, qr_y - pad, qr_size + 2 * pad, qr_size + 2 * pad,
                radius=10, fill=1, stroke=1)

    qr_buf = io.BytesIO()
    make_qr(url, box_size_px=22).save(qr_buf, format="PNG")
    qr_buf.seek(0)
    c.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)

    # Platform strip below QR
    c.setFillColor(VP_INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(safe_center_x, qr_y - 0.3 * inch,
                        "FACEBOOK · INSTAGRAM · X · TIKTOK · YOUTUBE")

    # Fine print just above bottom bar
    c.setFont("Helvetica", 6.5)
    c.setFillColor(VP_INK)
    fp_y = bot_h + 0.18 * inch
    c.drawCentredString(safe_center_x, fp_y, "No purchase necessary · VA residents 18+ · See thevalleypawn.com/giveaway-rules")

    # Bottom bar text (white on red)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(safe_center_x, bot_h / 2 - 4, "thevalleypawn.com  ·  5 Virginia Locations")

    # === CROP MARKS (registration for Vistaprint) ===
    c.setStrokeColor(black)
    c.setLineWidth(TRIM_LINE_WEIGHT)
    mark = 0.1 * inch
    gap = 0.06 * inch
    # Bottom-left
    c.line(BLEED - mark - gap, BLEED, BLEED - gap, BLEED)
    c.line(BLEED, BLEED - mark - gap, BLEED, BLEED - gap)
    # Bottom-right
    c.line(page_w - BLEED + gap, BLEED, page_w - BLEED + gap + mark, BLEED)
    c.line(page_w - BLEED, BLEED - mark - gap, page_w - BLEED, BLEED - gap)
    # Top-left
    c.line(BLEED - mark - gap, page_h - BLEED, BLEED - gap, page_h - BLEED)
    c.line(BLEED, page_h - BLEED + gap, BLEED, page_h - BLEED + gap + mark)
    # Top-right
    c.line(page_w - BLEED + gap, page_h - BLEED, page_w - BLEED + gap + mark, page_h - BLEED)
    c.line(page_w - BLEED, page_h - BLEED + gap, page_w - BLEED, page_h - BLEED + gap + mark)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("url", help="Destination URL the QR encodes")
    parser.add_argument("--store", default="all", help="Store name (Lexington/Roanoke/etc), or 'all' for brand")
    parser.add_argument("--size", choices=["5x7", "6x8"], default="5x7", help="Trim size")
    parser.add_argument("--out", default=None, help="Output PDF path")
    parser.add_argument("--logo", default=None, help="Logo PNG path")
    args = parser.parse_args()

    here = Path(__file__).parent
    if not args.logo:
        # Prefer the tighter landscape logo if available; fall back to the padded profile
        landscape = here / "brand_assets" / "valley_pawn_landscape.png"
        profile = here / "brand_assets" / "valley_pawn_profile_1080.png"
        if landscape.exists():
            args.logo = str(landscape)
        elif profile.exists():
            args.logo = str(profile)
    if not args.out:
        args.out = str(here / f"acrylic_sign_{args.store.lower()}_{args.size}.pdf")

    if args.size == "6x8":
        trim_w, trim_h = 6 * inch, 8 * inch
    else:
        trim_w, trim_h = 5 * inch, 7 * inch

    page_w = trim_w + 2 * BLEED
    page_h = trim_h + 2 * BLEED

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(args.out, pagesize=(page_w, page_h))
    draw_sign(c, args.url, args.store, trim_w, trim_h, args.logo)
    c.showPage()
    c.save()
    print(f"Acrylic sign PDF written: {args.out}")
    print(f"  Trim:    {trim_w/inch:.2f} x {trim_h/inch:.2f} inches")
    print(f"  Bleed:   {BLEED/inch:.3f} inch (added on all sides)")
    print(f"  Page:    {page_w/inch:.3f} x {page_h/inch:.3f} inches (full bleed)")
    print(f"  URL:     {args.url}")
    print(f"  Store:   {args.store}")


if __name__ == "__main__":
    main()
