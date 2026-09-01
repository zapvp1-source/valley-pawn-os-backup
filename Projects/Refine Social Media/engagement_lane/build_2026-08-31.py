#!/usr/bin/env python3
"""Lane D assets, run 2026-08-31. Runs on HOST python3 (sandbox PIL SIGBUSes).
Builds:
  eng_this_or_that_1080.png  - two real Harrisonburg items side by side
  hum_seasonal_arrival_1080.png - text card, late-summer arrivals
The guess-the-price post uses the raw counter photo, unedited, no card.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "2026-08-31"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = (0x0F, 0x1A, 0x2E)
GOLD = (0xB0, 0x8A, 0x3E)
IVORY = (0xF4, 0xED, 0xE0)

PLAYFAIR = str(ROOT / "fonts" / "PlayfairDisplay.ttf")
INTER = str(ROOT / "fonts" / "Inter.ttf")


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(src, box_w, box_h):
    """Cover-crop src into box_w x box_h."""
    im = Image.open(src).convert("RGB")
    sr, br = im.width / im.height, box_w / box_h
    if sr > br:
        nh = im.height
        nw = int(nh * br)
    else:
        nw = im.width
        nh = int(nw / br)
    left = (im.width - nw) // 2
    top = (im.height - nh) // 2
    return im.crop((left, top, left + nw, top + nh)).resize((box_w, box_h), Image.LANCZOS)


def this_or_that(left_img, right_img, left_label, right_label):
    S = 1080
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)

    pad = 46
    header_h = 172
    footer_h = 150
    panel_h = S - header_h - footer_h
    panel_w = (S - pad * 2 - 14) // 2

    img.paste(fit(left_img, panel_w, panel_h), (pad, header_h))
    img.paste(fit(right_img, panel_w, panel_h), (pad + panel_w + 14, header_h))

    f_kick = ImageFont.truetype(INTER, 30)
    f_head = ImageFont.truetype(PLAYFAIR, 58)
    f_lbl = ImageFont.truetype(INTER, 30)

    d.text((pad, 44), "SAME COUNTER, SAME WEEK", font=f_kick, fill=GOLD)
    d.text((pad, 84), "Which one goes home with you?", font=f_head, fill=IVORY)

    y = S - footer_h + 24
    d.text((pad, y), left_label, font=f_lbl, fill=IVORY)
    d.text((pad + panel_w + 14, y), right_label, font=f_lbl, fill=IVORY)
    d.text((pad, y + 46), "Valley Pawn — Harrisonburg", font=f_lbl, fill=GOLD)

    d.rectangle([pad - 8, header_h - 8, S - pad + 8, header_h + panel_h + 8], outline=GOLD, width=2)

    p = OUT / "eng_this_or_that_1080.png"
    img.save(p)
    return p


def card(name, kicker, headline, sub):
    S = 1080
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([46, 46, S - 46, S - 46], outline=GOLD, width=2)

    f_kick = ImageFont.truetype(INTER, 30)
    f_head = ImageFont.truetype(PLAYFAIR, 74)
    f_sub = ImageFont.truetype(INTER, 34)

    margin = 110
    maxw = S - margin * 2
    head_lines = wrap(d, headline, f_head, maxw)
    sub_lines = wrap(d, sub, f_sub, maxw)
    h = 44 + 40 + len(head_lines) * 92 + 30 + len(sub_lines) * 50
    y = (S - h) // 2 - 20

    d.text((margin, y), kicker.upper(), font=f_kick, fill=GOLD)
    y += 44
    d.line([margin, y + 14, margin + 90, y + 14], fill=GOLD, width=3)
    y += 40
    for ln in head_lines:
        d.text((margin, y), ln, font=f_head, fill=IVORY)
        y += 92
    y += 30
    for ln in sub_lines:
        d.text((margin, y), ln, font=f_sub, fill=IVORY)
        y += 50

    p = OUT / name
    img.save(p)
    return p


if __name__ == "__main__":
    u = ROOT / "deal_of_week_uploads"
    print(this_or_that(
        u / "deal_harrisonburg_martin_0831.jpg",
        u / "deal_harrisonburg_laptop_0824.jpg",
        "Martin 000-18",
        "Gaming laptop",
    ))
    print(card(
        "hum_seasonal_arrival_1080.png",
        "the counter knows what month it is",
        "Late August walks in holding a tiller.",
        "Ten chainsaws, two tillers, a 12,000-watt generator and a truck inverter, all in three weeks. Nobody plans this. The calendar just shows up.",
    ))
