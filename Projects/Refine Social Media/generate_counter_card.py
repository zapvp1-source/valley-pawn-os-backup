#!/usr/bin/env python3
"""
Generate the Valley Pawn counter-card QR insert PDF.

Output: 5x7 portrait PDF, ready to print on cardstock and slide into the
acrylic counter holder (Sourcing4U or equivalent).

Usage:
    python3 generate_counter_card.py "https://follow.thevalleypawn.com"
    python3 generate_counter_card.py "https://follow.thevalleypawn.com" \
        --out /path/to/counter_card.pdf
"""
from __future__ import annotations
import argparse
import io
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.pagesizes import inch
from reportlab.lib.units import inch as INCH
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image

# Brand colors per vp-brand-studio (approximated from logo)
VP_BLUE = HexColor("#0F3D8F")        # primary deep blue
VP_RED = HexColor("#C7301F")         # primary red accent
VP_CREAM = HexColor("#F8F4EC")       # warm off-white background
VP_INK = HexColor("#0A0A0A")         # near-black for body text


def make_qr_image(url: str, box_size_px: int = 14) -> Image.Image:
    """Generate a high-error-correction QR. Returns PIL Image (RGB)."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # 30% error correction — survives logo overlay + scuffs
        box_size=box_size_px,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img


def draw_card(c: canvas.Canvas, url: str, page_w: float, page_h: float, logo_path: str | None = None):
    """Render the counter card on the canvas."""
    # Background
    c.setFillColor(VP_CREAM)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Top accent bar
    c.setFillColor(VP_BLUE)
    c.rect(0, page_h - 0.5 * INCH, page_w, 0.5 * INCH, fill=1, stroke=0)

    # Bottom accent bar
    c.setFillColor(VP_RED)
    c.rect(0, 0, page_w, 0.35 * INCH, fill=1, stroke=0)

    # Logo (top)
    if logo_path and Path(logo_path).exists():
        try:
            logo_w = 3.0 * INCH
            logo_h = 0.8 * INCH
            c.drawImage(
                logo_path,
                (page_w - logo_w) / 2,
                page_h - 0.5 * INCH - logo_h - 0.15 * INCH,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                mask='auto',
            )
        except Exception as e:
            print(f"[warn] couldn't draw logo: {e}", file=sys.stderr)

    # Headline
    headline_y = page_h - 2.0 * INCH
    c.setFillColor(VP_INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_w / 2, headline_y, "WIN $100 EVERY MONTH")

    c.setFont("Helvetica", 12)
    c.drawCentredString(page_w / 2, headline_y - 0.28 * INCH, "Follow us anywhere · Drop your email · You're entered.")

    # QR code (centered, large)
    qr_img = make_qr_image(url, box_size_px=18)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)

    qr_size = 3.0 * INCH
    qr_x = (page_w - qr_size) / 2
    qr_y = 1.4 * INCH

    # White card behind QR for contrast
    pad = 0.12 * INCH
    c.setFillColor(white)
    c.setStrokeColor(VP_BLUE)
    c.setLineWidth(2)
    c.roundRect(qr_x - pad, qr_y - pad, qr_size + 2 * pad, qr_size + 2 * pad,
                radius=8, fill=1, stroke=1)

    from reportlab.lib.utils import ImageReader
    c.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)

    # Platform strip (text labels - actual platform icons would be ideal but text works)
    c.setFillColor(VP_INK)
    c.setFont("Helvetica-Bold", 9)
    platforms = "FACEBOOK · YOUTUBE · X · INSTAGRAM · TIKTOK"
    c.drawCentredString(page_w / 2, qr_y - 0.35 * INCH, platforms)

    # Fine print
    c.setFillColor(VP_INK)
    c.setFont("Helvetica", 6.5)
    fine_print_y = 0.55 * INCH
    c.drawCentredString(page_w / 2, fine_print_y, "No purchase necessary. VA residents 18+.")
    c.drawCentredString(page_w / 2, fine_print_y - 0.12 * INCH, "Official rules at follow.thevalleypawn.com/rules")

    # Bottom bar text
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_w / 2, 0.13 * INCH, "thevalleypawn.com  ·  5 Virginia Locations")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("url", help="Linkie URL the QR points to")
    parser.add_argument("--out", default=None, help="Output PDF path")
    parser.add_argument("--logo", default=None, help="Logo PNG path (transparent recommended)")
    args = parser.parse_args()

    here = Path(__file__).parent
    if not args.out:
        args.out = str(here / "counter_card_5x7.pdf")
    if not args.logo:
        # Try the brand asset we already produced
        candidate = here / "brand_assets" / "valley_pawn_profile_1080.png"
        if candidate.exists():
            args.logo = str(candidate)

    # 5x7 portrait
    page_w = 5 * INCH
    page_h = 7 * INCH

    c = canvas.Canvas(args.out, pagesize=(page_w, page_h))
    draw_card(c, args.url, page_w, page_h, args.logo)
    c.showPage()
    c.save()
    print(f"Counter card PDF written: {args.out}")
    print(f"  URL encoded:  {args.url}")
    print(f"  Logo:         {args.logo or '(none)'}")
    print(f"  Page size:    5 x 7 inches portrait (fits standard acrylic holder)")


if __name__ == "__main__":
    main()
