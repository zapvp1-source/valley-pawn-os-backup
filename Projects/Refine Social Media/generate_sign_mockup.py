#!/usr/bin/env python3
"""
Render acrylic sign PDF as a counter-top mockup PNG.

Shows the sign as it would actually appear on a Valley Pawn counter — same
information Vistaprint's automated proof would show, but generated locally
with full visual fidelity.

Usage:
    python3 generate_sign_mockup.py acrylic_signs/01_lexington_5x7.pdf

Output: acrylic_signs/01_lexington_5x7_MOCKUP.png
"""
from __future__ import annotations
import argparse
import io
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def pdf_to_png(pdf_path: Path, dpi: int = 300) -> Image.Image:
    """Render the first page of a PDF to a PIL Image at the given DPI."""
    out_dir = pdf_path.parent / "_tmp"
    out_dir.mkdir(exist_ok=True)
    base = out_dir / pdf_path.stem
    subprocess.run([
        "pdftoppm", "-r", str(dpi), "-png",
        "-singlefile",
        str(pdf_path), str(base),
    ], check=True)
    img_path = Path(str(base) + ".png")
    img = Image.open(img_path).convert("RGBA")
    return img


def make_acrylic_look(sign_img: Image.Image) -> Image.Image:
    """Add a subtle drop shadow + slight clear-acrylic edge highlight."""
    w, h = sign_img.size
    pad = 60
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))

    # Drop shadow — offset 12px down, blurred
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 100))
    shadow.paste(shadow_layer, (pad + 6, pad + 14), shadow_layer)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))

    canvas = Image.alpha_composite(canvas, shadow)

    # Paste sign on top
    canvas.paste(sign_img, (pad, pad), sign_img)

    # Subtle clear-acrylic edge highlight (faint white rim)
    draw = ImageDraw.Draw(canvas)
    rim_w = 2
    draw.rectangle([pad - rim_w, pad - rim_w, pad + w + rim_w, pad + h + rim_w],
                   outline=(255, 255, 255, 80), width=rim_w)

    return canvas


def make_counter_mockup(sign_with_acrylic: Image.Image, output: Path):
    """Place sign on a warm wood counter background, with subtle perspective."""
    w, h = sign_with_acrylic.size
    # Mockup canvas — counter scene
    mockup_w = max(1400, w + 600)
    mockup_h = max(1100, h + 500)
    bg = Image.new("RGB", (mockup_w, mockup_h), (236, 224, 208))

    # Draw a gradient "wall" + "counter surface"
    draw = ImageDraw.Draw(bg)
    counter_top_y = int(mockup_h * 0.55)
    # Wall
    for y in range(counter_top_y):
        t = y / counter_top_y
        r = int(248 - t * 12)
        g = int(245 - t * 18)
        b = int(238 - t * 22)
        draw.line([(0, y), (mockup_w, y)], fill=(r, g, b))
    # Counter surface (warm wood gradient)
    for y in range(counter_top_y, mockup_h):
        t = (y - counter_top_y) / (mockup_h - counter_top_y)
        r = int(180 - t * 30)
        g = int(140 - t * 30)
        b = int(95 - t * 25)
        draw.line([(0, y), (mockup_w, y)], fill=(r, g, b))

    # Wood grain noise
    import random
    random.seed(42)
    for _ in range(800):
        x = random.randint(0, mockup_w)
        y = random.randint(counter_top_y, mockup_h - 1)
        length = random.randint(40, 180)
        color = (random.randint(140, 200), random.randint(110, 150), random.randint(70, 110), random.randint(20, 60))
        draw.line([(x, y), (x + length, y)], fill=color[:3], width=1)

    # Light beam from upper right (subtle)
    overlay = Image.new("RGBA", (mockup_w, mockup_h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for r in range(400, 50, -20):
        a = int(40 * (1 - r / 400))
        odraw.ellipse([mockup_w - 200 - r, -r, mockup_w - 200 + r, r], fill=(255, 245, 220, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    # Position sign — centered horizontally, just above counter top (with easel angle)
    sign_x = (mockup_w - w) // 2
    sign_y = counter_top_y - h + 80  # overlap counter for "sitting on" look

    # Easel back illusion — small darker triangle behind sign right side
    edraw = ImageDraw.Draw(bg.convert("RGBA"))
    # Tilt sign slightly forward (3 degrees)
    sign_tilted = sign_with_acrylic.rotate(2, resample=Image.BICUBIC, expand=True)

    # Reflection on counter
    reflection = sign_tilted.transpose(Image.FLIP_TOP_BOTTOM)
    refl_mask = Image.new("L", reflection.size, 0)
    rm_draw = ImageDraw.Draw(refl_mask)
    for y in range(reflection.size[1]):
        alpha = int(50 * (1 - y / reflection.size[1]))
        rm_draw.line([(0, y), (reflection.size[0], y)], fill=alpha)
    reflection.putalpha(refl_mask)

    bg_rgba = bg.convert("RGBA")
    bg_rgba.paste(reflection,
                  (sign_x - (sign_tilted.size[0] - w) // 2,
                   sign_y + h - 30),
                  reflection)
    bg_rgba.paste(sign_tilted,
                  (sign_x - (sign_tilted.size[0] - w) // 2, sign_y),
                  sign_tilted)

    # Bottom caption
    final = bg_rgba.convert("RGB")
    fdraw = ImageDraw.Draw(final)
    cap_y = mockup_h - 50
    fdraw.text((mockup_w // 2 - 250, cap_y),
               "Vistaprint 5x7 Clear Acrylic · Tabletop Easel · UV-printed both sides",
               fill=(80, 70, 60))

    final.save(output, "PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pdf", help="Path to the acrylic sign PDF")
    parser.add_argument("--out", default=None, help="Output PNG path")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")
    output = Path(args.out) if args.out else pdf_path.with_name(pdf_path.stem + "_MOCKUP.png")

    sign_img = pdf_to_png(pdf_path, dpi=300)
    sign_with_acrylic = make_acrylic_look(sign_img)
    make_counter_mockup(sign_with_acrylic, output)
    print(f"Mockup written: {output}")


if __name__ == "__main__":
    main()
