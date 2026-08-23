#!/usr/bin/env python3
"""Engagement-lane question cards. Brand palette locked per vp-brand-studio."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = Path(__file__).resolve().parent / "2026-08-22"
OUT.mkdir(parents=True, exist_ok=True)

NAVY  = (0x0F, 0x1A, 0x2E)
GOLD  = (0xB0, 0x8A, 0x3E)
IVORY = (0xF4, 0xED, 0xE0)

PLAYFAIR = str(ROOT / "fonts" / "PlayfairDisplay.ttf")
INTER    = str(ROOT / "fonts" / "Inter.ttf")
LOGO     = ROOT / "brand_assets" / "valley_pawn_landscape_transparent.png"

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def card(name, kicker, headline, sub):
    S = 1080
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)

    # thin gold frame
    d.rectangle([46, 46, S-46, S-46], outline=GOLD, width=2)

    f_kick = ImageFont.truetype(INTER, 30)
    f_head = ImageFont.truetype(PLAYFAIR, 78)
    f_sub  = ImageFont.truetype(INTER, 34)

    margin = 110
    maxw = S - margin*2

    # measure block
    head_lines = wrap(d, headline, f_head, maxw)
    sub_lines  = wrap(d, sub, f_sub, maxw)
    h = 44 + 40 + len(head_lines)*96 + 30 + len(sub_lines)*50
    y = (S - h)//2 - 30

    d.text((margin, y), kicker.upper(), font=f_kick, fill=GOLD)
    y += 44
    d.line([margin, y+14, margin+90, y+14], fill=GOLD, width=3)
    y += 40

    for ln in head_lines:
        d.text((margin, y), ln, font=f_head, fill=IVORY)
        y += 96
    y += 30
    for ln in sub_lines:
        d.text((margin, y), ln, font=f_sub, fill=(0xC9, 0xC2, 0xB6))
        y += 50

    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        lw = 300
        logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
        img.paste(logo, ((S-lw)//2, S - 46 - 40 - logo.height), logo)

    p = OUT / name
    img.save(p, "PNG")
    print(p)
    return p

card("eng_stock_poll_1080.png",
     "Your call",
     "What should we stock more of?",
     "Tools? Instruments? Jewelry? Electronics? Outdoor gear? Tell us in the comments and we will actually go buy it.")

card("hum_overheard_1080.png",
     "Overheard at the counter",
     "“It comes with the keys.”",
     "“It comes with the KEYS?”  — Waynesboro, this month.")
