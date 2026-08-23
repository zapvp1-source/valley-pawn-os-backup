#!/usr/bin/env python3
"""
vp_deal_reel.py — Valley Pawn machine-made Deal Reel engine (Lane B1).

WHY THIS EXISTS
---------------
2026-08-22 audit (audit_2026-08-22/): the content pipeline produced TWO videos in
90 days and ZERO in the last 49, because the only video path (`vp-casual-video-daily`)
depends on a human dropping a file into `Valley Pawn Studios/casual-video-inbox/`,
which has been empty since 2026-07-06.

Meanwhile the #deal-of-the-week channel delivers 5 real product photos with real
prices EVERY Monday, 10/10 two weeks running. This engine turns that reliable
input into vertical Reels with ZERO human involvement.

Brand lock (vp-brand-studio): navy #0F1A2E, gold #B08A3E, ivory #F4EDE0,
oxblood #722F37 (urgency only). Playfair Display for display, Inter for
body + tabular numerals. STYLE-F register (9:16, negative space reserved
for headline overlay).

DESIGN NOTES
------------
* All typography is rendered by PIL into transparent PNG layers, then composited
  by a SINGLE ffmpeg call. Rationale: ffmpeg's drawtext escaping is a reliable
  source of silent corruption with currency symbols, apostrophes and em-dashes —
  every one of which appears in Valley Pawn deal copy. PIL removes that class
  of bug entirely.
* The product photo is never cropped to fill. It is fitted, and the gap is filled
  with a blurred, darkened copy of itself. Cropping a product photo to 9:16
  routinely decapitates the product.
* NO music bed in v1. We do not have a license we can point at, and Reels autoplay
  muted anyway. Adding an unlicensed track to five store Pages is a real legal and
  Page-strike risk. Music is a v2 item pending a purchased pack.
* Everything degrades rather than dies: a missing retail price drops the strike-through
  card, a missing address drops the address line, an unreadable photo is skipped with
  a logged reason and the other four stores still ship. See render_batch().

USAGE
-----
    python3 vp_deal_reel.py --spec deals.json --outdir reels/
    python3 vp_deal_reel.py --selftest          # renders from the newest deal photos on disk

SPEC FORMAT (list of dicts):
    [{
        "store":       "Lexington",
        "photo":       "/abs/path/to/photo.jpg",
        "product":     "Pulsar 12,000-Watt Dual-Fuel Generator",
        "price":       "849.99",
        "retail":      "1399.00",          # optional
        "hook":        "Serious backup power, gas or propane.",   # optional
        "address":     "125 Walker St, Lexington"                 # optional
    }, ...]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ----------------------------------------------------------------------------
# Brand lock — vp-brand-studio. Never freelance these.
# ----------------------------------------------------------------------------
NAVY = (15, 26, 46)
GOLD = (176, 138, 62)
IVORY = (244, 237, 224)
CHARCOAL = (28, 28, 28)
OXBLOOD = (114, 47, 55)

W, H = 1080, 1920
FPS = 30

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
BRAND_DIR = ROOT / "brand_assets"
LOGO_PATH = BRAND_DIR / "valley_pawn_landscape_transparent.png"

F_DISPLAY = FONT_DIR / "PlayfairDisplay.ttf"
F_BODY = FONT_DIR / "Inter.ttf"

# Storefront addresses — canonical, from valley-pawn-context.
STORE_ADDRESS = {
    "Culpeper": "571 James Madison Hwy, Culpeper",
    "Harrisonburg": "1790 E Market St STE 22, Harrisonburg",
    "Lexington": "125 Walker St, Lexington",
    "Roanoke": "2362 Peters Creek Rd Suite C, Roanoke",
    "Waynesboro": "1321 W Broad St, Waynesboro",
}

# Timeline (seconds). Total 15.0s — inside every platform's Reel sweet spot.
T_TOTAL = 15.0
SEG = {
    "store_chip": (0.20, 15.0),   # persistent top chip
    "product": (0.60, 6.60),      # product name, lower third
    "price": (6.40, 11.20),       # price reveal
    "trust": (10.60, 13.40),      # warranty + layaway
    "endcard": (13.10, 15.0),     # brand end card
}


class ReelError(Exception):
    pass


# ----------------------------------------------------------------------------
# Font loading — fail loudly at import time rather than silently at 2 AM.
# ----------------------------------------------------------------------------
def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise ReelError(
            f"Required brand font missing: {path}. "
            "vp-brand-studio locks Playfair Display + Inter; do not substitute."
        )
    return ImageFont.truetype(str(path), size)


# ----------------------------------------------------------------------------
# Text helpers
# ----------------------------------------------------------------------------
def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _money(v: str | float | int) -> str:
    """'849.99' | 849.99 | '$849.99' -> '$849.99'. Whole dollars lose the .00."""
    s = str(v).replace("$", "").replace(",", "").strip()
    try:
        f = float(s)
    except ValueError:
        return f"${s}"
    return f"${f:,.0f}" if abs(f - round(f)) < 0.005 else f"${f:,.2f}"


def _draw_text_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font,
    fill,
    cx: int,
    top: int,
    leading: float = 1.18,
    shadow: bool = True,
) -> int:
    """Center-aligned block. Returns the y coordinate just past the block."""
    y = top
    lh = int(font.size * leading)
    for ln in lines:
        w = draw.textlength(ln, font=font)
        x = cx - w / 2
        if shadow:
            draw.text((x + 3, y + 3), ln, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def _scrim(img: Image.Image, top: int, bottom: int, strength: int = 205) -> None:
    """Vertical gradient scrim so type stays legible over any photo."""
    d = ImageDraw.Draw(img)
    span = max(1, bottom - top)
    for i in range(span):
        a = int(strength * (i / span) ** 1.4)
        d.line([(0, top + i), (W, top + i)], fill=(*NAVY, a))


# ----------------------------------------------------------------------------
# Overlay layers
# ----------------------------------------------------------------------------
def layer_store_chip(store: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = _font(F_BODY, 34)
    label = f"VALLEY PAWN  ·  {store.upper()}"
    tw = d.textlength(label, font=f)
    pad_x, pad_y = 34, 20
    bw, bh = int(tw + pad_x * 2), int(f.size + pad_y * 2)
    bx, by = (W - bw) // 2, 96
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=(*NAVY, 230))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, outline=(*GOLD, 255), width=2)
    d.text((bx + pad_x, by + pad_y - 4), label, font=f, fill=(*IVORY, 255))
    return img


def layer_product(product: str, hook: str | None) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _scrim(img, 1180, 1920, strength=215)
    d = ImageDraw.Draw(img)

    size = 78 if len(product) <= 42 else (64 if len(product) <= 70 else 54)
    fp = _font(F_DISPLAY, size)
    lines = _wrap(d, product, fp, W - 150)[:3]

    block_h = int(fp.size * 1.18) * len(lines)
    top = 1560 - block_h if not hook else 1500 - block_h
    y = _draw_text_block(d, lines, fp, (*IVORY, 255), W // 2, top)

    d.line([(W // 2 - 70, y + 26), (W // 2 + 70, y + 26)], fill=(*GOLD, 255), width=3)

    if hook:
        fh = _font(F_BODY, 40)
        hl = _wrap(d, hook, fh, W - 190)[:2]
        _draw_text_block(d, hl, fh, (*IVORY, 225), W // 2, y + 58)
    return img


def layer_price(price: str, retail: str | None) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _scrim(img, 1080, 1920, strength=230)
    d = ImageDraw.Draw(img)

    y = 1300
    if retail:
        fr = _font(F_BODY, 46)
        rtxt = f"Retail {_money(retail)}"
        rw = d.textlength(rtxt, font=fr)
        rx = W // 2 - rw / 2
        d.text((rx + 2, y + 2), rtxt, font=fr, fill=(0, 0, 0, 140))
        d.text((rx, y), rtxt, font=fr, fill=(*IVORY, 190))
        sy = y + int(fr.size * 0.62)
        d.line([(rx - 12, sy), (rx + rw + 12, sy)], fill=(*OXBLOOD, 255), width=5)
        y += int(fr.size * 1.55)

    fpz = _font(F_BODY, 168)
    ptxt = _money(price)
    pw = d.textlength(ptxt, font=fpz)
    px = W // 2 - pw / 2
    d.text((px + 5, y + 5), ptxt, font=fpz, fill=(0, 0, 0, 160))
    d.text((px, y), ptxt, font=fpz, fill=(*GOLD, 255))
    y += int(fpz.size * 1.02)

    fl = _font(F_BODY, 40)
    lab = "OUR PRICE"
    lw = d.textlength(lab, font=fl)
    d.text((W // 2 - lw / 2, y), lab, font=fl, fill=(*IVORY, 210))
    return img


def layer_trust(address: str | None) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _scrim(img, 1180, 1920, strength=225)
    d = ImageDraw.Draw(img)

    f = _font(F_BODY, 52)
    y = 1420
    for line in ("30-Day Warranty", "Free Layaway"):
        tw = d.textlength(line, font=f)
        x = W // 2 - tw / 2
        d.ellipse([x - 46, y + 12, x - 20, y + 38], outline=(*GOLD, 255), width=3)
        d.line([(x - 40, y + 25), (x - 33, y + 32)], fill=(*GOLD, 255), width=3)
        d.line([(x - 33, y + 32), (x - 25, y + 18)], fill=(*GOLD, 255), width=3)
        d.text((x + 2, y + 2), line, font=f, fill=(0, 0, 0, 150))
        d.text((x, y), line, font=f, fill=(*IVORY, 255))
        y += int(f.size * 1.45)

    if address:
        fa = _font(F_BODY, 38)
        al = _wrap(d, address, fa, W - 180)[:2]
        _draw_text_block(d, al, fa, (*IVORY, 205), W // 2, y + 26)
    return img


def layer_endcard(store: str, address: str | None) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*NAVY, 255))
    d = ImageDraw.Draw(img)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        tw = 760
        logo = logo.resize((tw, max(1, int(logo.height * tw / logo.width))), Image.LANCZOS)
        img.alpha_composite(logo, ((W - tw) // 2, 700))
        y = 700 + logo.height + 70
    else:
        fb = _font(F_DISPLAY, 96)
        y = _draw_text_block(d, ["Valley Pawn"], fb, (*IVORY, 255), W // 2, 760, shadow=False) + 40

    d.line([(W // 2 - 120, y), (W // 2 + 120, y)], fill=(*GOLD, 255), width=3)
    y += 46

    ft = _font(F_DISPLAY, 54)
    y = _draw_text_block(d, ['"What\'s Right Is Right"'], ft, (*GOLD, 255), W // 2, y, shadow=False)
    y += 40

    fs = _font(F_BODY, 42)
    y = _draw_text_block(d, [f"Valley Pawn {store}"], fs, (*IVORY, 255), W // 2, y, shadow=False)
    if address:
        fa = _font(F_BODY, 36)
        y = _draw_text_block(d, _wrap(d, address, fa, W - 200)[:2], fa, (*IVORY, 200), W // 2, y + 12, shadow=False)

    fw = _font(F_BODY, 34)
    _draw_text_block(d, ["thevalleypawn.com"], fw, (*GOLD, 220), W // 2, y + 34, shadow=False)
    return img


# ----------------------------------------------------------------------------
# Source classification — PHOTO vs FLYER
#
# Found 2026-08-22 during the first live render: managers do NOT always submit a
# raw product photo. Culpeper and Lexington submitted finished marketing FLYERS
# (vendor-made graphics that already carry the product name, our price, retail
# price, savings, warranty badge and a Valley Pawn logo). Overlaying our own
# product/price cards on top of those double-stacks the branding and collides
# with the flyer's own type — it looked broken.
#
# So the engine classifies the source and picks a treatment:
#   PHOTO -> full treatment (product card, price reveal, trust card, end card)
#   FLYER -> minimal treatment (store chip + slow read-pan + end card only).
#            The flyer already says everything; our job is just to make it move.
#
# Heuristic (measured on the five live 2026-08-22 submissions):
#   edge density = fraction of strong edges — dense small type spikes this
#   sat variance = spread of HSV saturation — flyers mix brand-saturated panels
#                  with white/black type, photos of real objects do not
#     FLYERS: CUL 14.8% / 96.3   LEX 17.9% / 95.6
#     PHOTOS: HAR  8.6% / 79.9   WAY  8.9% / 61.2   ROA  2.2% / 20.8
# A first attempt at "share of top quantized colors" was tried and REJECTED —
# it scored the CUL flyer lowest of all five, because that flyer is itself
# photo-rich. Do not reintroduce it.
#
# n=5 is a thin sample, so classification is NOT load-bearing on its own:
# build_plate() independently guarantees that a tall source can never reach the
# lower-third type band (see SAFE_BOTTOM). A misread therefore costs a plainer
# reel, never a broken one — in either direction.
# ----------------------------------------------------------------------------
EDGE_FLYER = 0.11      # worst flyer 0.148, best photo 0.089
SAT_FLYER = 88.0       # worst flyer 95.6,  best photo 79.9


def classify_source(photo: Path) -> tuple[str, dict]:
    """Return ('photo'|'flyer', metrics). Never raises — defaults to photo."""
    metrics = {"edge": 0.0, "satvar": 0.0}
    try:
        from PIL import ImageOps
        import statistics

        im = Image.open(photo).convert("RGB")
        im.thumbnail((900, 900), Image.LANCZOS)

        edges = ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES).getdata()
        px = list(edges)
        metrics["edge"] = sum(1 for v in px if v > 60) / max(1, len(px))

        hsv = im.convert("HSV")
        w, h = hsv.size
        sats = [hsv.getpixel((x, y))[1] for y in range(0, h, 9) for x in range(0, w, 9)]
        metrics["satvar"] = statistics.pstdev(sats) if len(sats) > 1 else 0.0

        is_flyer = metrics["edge"] >= EDGE_FLYER and metrics["satvar"] >= SAT_FLYER
        return ("flyer" if is_flyer else "photo"), metrics
    except Exception:
        return "photo", metrics


# ----------------------------------------------------------------------------
# Product plate: fit (never crop) the photo onto a blurred fill of itself
# ----------------------------------------------------------------------------
def build_flyer_plate(photo: Path, out: Path) -> None:
    """
    Flyer treatment: show the WHOLE graphic, tall, on a brand-navy field, with
    enough headroom top and bottom that the persistent store chip and the fade to
    the end card never sit on the flyer's own type. The reel's motion is a slow
    downward read-pan (handled in render_reel), not a zoom — a zoom on a
    text-dense flyer just makes it unreadable.
    """
    src = Image.open(photo)
    if src.mode in ("RGBA", "LA", "P"):
        flat = Image.new("RGB", src.size, IVORY)
        src = src.convert("RGBA")
        flat.paste(src, mask=src.split()[-1])
        src = flat
    else:
        src = src.convert("RGB")

    # Tall canvas: 1080 wide, 1.6x the reel height so there is real travel to pan.
    cw, ch = W, int(H * 1.6)
    canvas = Image.new("RGB", (cw, ch), NAVY)

    margin_x = 44
    fit_w = cw - margin_x * 2
    # Leave a clear band top and bottom for the chip and the end-card fade.
    band = int(H * 0.16)
    fit_h = ch - band * 2
    s = min(fit_w / src.width, fit_h / src.height)
    fitted = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)

    fx = (cw - fitted.width) // 2
    fy = band + (fit_h - fitted.height) // 2

    shadow = Image.new("RGBA", (fitted.width + 60, fitted.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([30, 30, fitted.width + 30, fitted.height + 30], fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    canvas.paste(shadow, (fx - 30, fy - 30), shadow)
    canvas.paste(fitted, (fx, fy))
    ImageDraw.Draw(canvas).rectangle(
        [fx - 2, fy - 2, fx + fitted.width + 2, fy + fitted.height + 2], outline=GOLD, width=3
    )
    canvas.save(out, "PNG")


def build_plate(photo: Path, out: Path) -> None:
    src = Image.open(photo)
    if src.mode in ("RGBA", "LA", "P"):
        bg_flat = Image.new("RGB", src.size, IVORY)
        src = src.convert("RGBA")
        bg_flat.paste(src, mask=src.split()[-1])
        src = bg_flat
    else:
        src = src.convert("RGB")

    # Oversized canvas so ffmpeg's zoompan has real pixels to pan into (no mush).
    cw, ch = int(W * 1.35), int(H * 1.35)

    scale = max(cw / src.width, ch / src.height)
    blur = src.resize((max(1, int(src.width * scale)), max(1, int(src.height * scale))), Image.LANCZOS)
    left = (blur.width - cw) // 2
    top = (blur.height - ch) // 2
    blur = blur.crop((left, top, left + cw, top + ch)).filter(ImageFilter.GaussianBlur(58))
    blur = Image.blend(blur, Image.new("RGB", (cw, ch), NAVY), 0.55)

    # Fit the real product inside a safe box clear of the chip and the lower third.
    #
    # SAFE_BOTTOM is a hard geometric guarantee, not a preference: whatever the
    # source aspect ratio, and whatever classify_source() decided, the fitted
    # image must END above the band where the product/price/trust cards are drawn.
    # This is what makes a misclassified flyer produce a plain reel instead of a
    # broken one — the 2026-08-22 collision bug, fixed at the geometry level so it
    # cannot recur through a different path.
    SAFE_TOP, SAFE_BOTTOM = 0.155, 0.665   # fractions of the oversized canvas
    # Account for the 1.35x push-in: content drifts outward as the zoom grows, so
    # the usable band must be shrunk by the zoom factor, not just clipped.
    ZOOM_MAX = 1.35
    usable_h = (SAFE_BOTTOM - SAFE_TOP) * ch / ZOOM_MAX
    box_w, box_h = int(cw * 0.90 / ZOOM_MAX), int(usable_h)

    fs = min(box_w / src.width, box_h / src.height)
    fitted = src.resize((max(1, int(src.width * fs)), max(1, int(src.height * fs))), Image.LANCZOS)

    canvas = blur
    fx = (cw - fitted.width) // 2
    # Center the fitted image inside the safe band rather than pinning to the top,
    # so short/wide products don't float with a dead gap beneath them.
    fy = int(SAFE_TOP * ch + (usable_h - fitted.height) / 2)
    shadow = Image.new("RGBA", (fitted.width + 60, fitted.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([30, 30, fitted.width + 30, fitted.height + 30], fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    canvas.paste(shadow, (fx - 30, fy - 30), shadow)
    canvas.paste(fitted, (fx, fy))

    ImageDraw.Draw(canvas).rectangle(
        [fx - 2, fy - 2, fx + fitted.width + 2, fy + fitted.height + 2], outline=GOLD, width=3
    )
    canvas.save(out, "PNG")


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
@dataclass
class Deal:
    store: str
    photo: Path
    product: str
    price: str
    retail: str | None = None
    hook: str | None = None
    address: str | None = None
    force_mode: str | None = None  # 'photo' | 'flyer' — overrides auto-detection

    def resolved_address(self) -> str | None:
        return self.address or STORE_ADDRESS.get(self.store)


@dataclass
class RenderResult:
    ok: bool
    store: str
    path: Path | None = None
    reason: str = ""
    mode: str = ""


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not Path(exe).exists():
        raise ReelError("ffmpeg not found. brew install ffmpeg")
    return exe


def render_reel(deal: Deal, outdir: Path) -> RenderResult:
    outdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "", deal.product.lower())[:26] or "item"
    out = outdir / f"{date.today():%Y%m%d}_{deal.store[:3].upper()}_dealreel_{slug}.mp4"

    if not deal.photo.exists():
        return RenderResult(False, deal.store, reason=f"photo not found: {deal.photo}")

    kind = deal.force_mode or classify_source(deal.photo)[0]

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        plate = tmp / "plate.png"
        try:
            (build_flyer_plate if kind == "flyer" else build_plate)(deal.photo, plate)
        except Exception as e:  # unreadable/corrupt image — skip this store, not the batch
            return RenderResult(False, deal.store, reason=f"unreadable photo ({e})")

        addr = deal.resolved_address()
        if kind == "flyer":
            # The flyer already carries product, price, retail, savings and warranty.
            # Adding our own cards on top double-brands it and collides with its type.
            segments = {"store_chip": SEG["store_chip"], "endcard": SEG["endcard"]}
            layers = {
                "store_chip": layer_store_chip(deal.store),
                "endcard": layer_endcard(deal.store, addr),
            }
        else:
            segments = dict(SEG)
            layers = {
                "store_chip": layer_store_chip(deal.store),
                "product": layer_product(deal.product, deal.hook),
                "price": layer_price(deal.price, deal.retail),
                "trust": layer_trust(addr),
                "endcard": layer_endcard(deal.store, addr),
            }
        for name, im in layers.items():
            im.save(tmp / f"{name}.png", "PNG")

        frames = int(T_TOTAL * FPS)
        if kind == "flyer":
            # Slow downward read-pan over the tall plate — no zoom. Text-dense
            # graphics become unreadable under a zoom; a pan lets people read.
            kb = (
                f"[0:v]scale={W}:-1,crop={W}:{H}:0:'(ih-{H})*(t/{T_TOTAL})',"
                f"fps={FPS},format=rgba[base]"
            )
        else:
            # Slow 1.35x push-in. zoompan needs an explicit s= or it defaults to hd720.
            kb = (
                f"[0:v]zoompan=z='min(zoom+0.00045,1.35)':d={frames}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
                f"format=rgba[base]"
            )

        parts, prev = [kb], "base"
        for idx, (name, (t0, t1)) in enumerate(segments.items(), start=1):
            fade_in = 0.35
            fade_out = 0.35 if name != "endcard" else 0.0
            alpha = (
                f"[{idx}:v]format=rgba,"
                f"fade=t=in:st={t0}:d={fade_in}:alpha=1"
                + (f",fade=t=out:st={max(t0, t1 - fade_out)}:d={fade_out}:alpha=1" if fade_out else "")
                + f"[L{idx}]"
            )
            nxt = f"v{idx}"
            over = (
                f"[{prev}][L{idx}]overlay=0:0:enable='between(t,{t0},{t1})':"
                f"format=auto[{nxt}]"
            )
            parts += [alpha, over]
            prev = nxt

        parts.append(f"[{prev}]format=yuv420p[vout]")
        filtergraph = ";".join(parts)

        cmd = [
            _ffmpeg(), "-y", "-loglevel", "error",
            "-loop", "1", "-t", str(T_TOTAL), "-i", str(plate),
        ]
        for name in segments:
            cmd += ["-loop", "1", "-t", str(T_TOTAL), "-i", str(tmp / f"{name}.png")]
        # Encode into scratch, then move into place.
        #
        # 2026-08-22: the Harrisonburg render died on "-movflags +faststart":
        #   "Unable to re-open <path> output file for shifting data".
        # faststart rewrites the file in place after encoding, and writing that
        # directly into ~/Documents races the Google Drive File Provider and
        # Spotlight — which also left a truncated 2 MB .mp4 sitting on disk
        # looking like a real deliverable. Encoding in /tmp and moving the
        # finished file into place removes both problems: no re-open race, and a
        # failed render leaves NOTHING behind rather than a plausible-looking stub.
        staged = tmp / "out.mp4"
        cmd += [
            "-filter_complex", filtergraph,
            "-map", "[vout]",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
            "-movflags", "+faststart",
            "-t", str(T_TOTAL),
            str(staged),
        ]

        last_err = ""
        for attempt in (1, 2):   # transient FS/encoder hiccups are retried, not reported
            staged.unlink(missing_ok=True)
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0 and staged.exists() and staged.stat().st_size >= 200_000:
                out.unlink(missing_ok=True)
                shutil.move(str(staged), str(out))
                return RenderResult(True, deal.store, path=out, mode=kind)
            last_err = (proc.stderr or "no stderr")[-400:]

        out.unlink(missing_ok=True)   # never leave a partial file behind
        return RenderResult(False, deal.store, mode=kind,
                            reason=f"ffmpeg failed after 2 attempts: {last_err}")


def render_batch(deals: list[Deal], outdir: Path) -> list[RenderResult]:
    """Degraded mode by design: one bad photo never zeroes the week."""
    results = []
    for d in deals:
        try:
            r = render_reel(d, outdir)
        except Exception as e:
            r = RenderResult(False, d.store, reason=f"unexpected: {e}")
        results.append(r)
        print(f"  {'OK  ' if r.ok else 'SKIP'} {d.store:<14} [{r.mode or '?':<5}] "
              f"{(r.path.name if r.ok else r.reason)}", flush=True)
    return results


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def _deals_from_spec(path: Path) -> list[Deal]:
    raw = json.loads(path.read_text())
    return [
        Deal(
            store=d["store"],
            photo=Path(d["photo"]).expanduser(),
            product=d["product"],
            price=str(d["price"]),
            retail=str(d["retail"]) if d.get("retail") else None,
            hook=d.get("hook"),
            address=d.get("address"),
        )
        for d in raw
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="Valley Pawn Deal Reel engine")
    ap.add_argument("--spec", type=Path, help="JSON spec file")
    ap.add_argument("--outdir", type=Path, default=ROOT / "reels")
    ap.add_argument("--selftest", action="store_true",
                    help="render from the newest deal photos on disk")
    a = ap.parse_args()

    if a.selftest:
        up = ROOT / "deal_of_week_uploads"
        latest = sorted(up.glob("2026*_deal_*"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        code = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington",
                "ROA": "Roanoke", "WAY": "Waynesboro"}
        demo = {
            "Lexington": ("Pulsar 12,000-Watt Dual-Fuel Generator", "849.99", "1399.00",
                          "Serious backup power that runs on gas or propane."),
            "Culpeper": ("Husqvarna 585 Chainsaw", "1149.00", "1539.99",
                         "Professional-grade power for big jobs."),
            "Roanoke": ("Samsung T5 EVO 4TB Portable SSD", "399.99", None,
                        "Four terabytes, sealed in the box."),
            "Harrisonburg": ("Apple iMac A3137 with Bluetooth Keyboard", "849.94", "949.94",
                             "Like-new condition. It'll run anything you need."),
            "Waynesboro": ("Cornwell 4-Drawer Rolling Tool Cart", "399.99", None,
                           "Comes with keys. These don't come up often."),
        }
        deals = []
        for p in latest:
            m = re.search(r"_(CUL|HAR|LEX|ROA|WAY)_", p.name)
            if not m:
                continue
            store = code[m.group(1)]
            if store not in demo:
                continue
            prod, price, retail, hook = demo.pop(store)
            deals.append(Deal(store=store, photo=p, product=prod, price=price,
                              retail=retail, hook=hook))
        if not deals:
            print("selftest: no deal photos found in deal_of_week_uploads/", file=sys.stderr)
            return 2
    elif a.spec:
        deals = _deals_from_spec(a.spec)
    else:
        ap.error("pass --spec or --selftest")
        return 2

    print(f"Rendering {len(deals)} Deal Reels -> {a.outdir}")
    results = render_batch(deals, a.outdir)
    ok = sum(1 for r in results if r.ok)
    print(f"\n{ok}/{len(results)} rendered.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
