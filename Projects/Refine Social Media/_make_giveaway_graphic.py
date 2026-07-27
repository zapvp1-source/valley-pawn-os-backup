#!/usr/bin/env python3
"""Generate a 1080x1080 on-brand $100/month giveaway social graphic."""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PURPLE = (45, 26, 94)
CYAN = (0, 153, 221)
SKY = (61, 184, 232)
CORAL = (245, 140, 138)
WHITE = (255, 255, 255)
LILAC = (230, 222, 247)

W = H = 1080
img = Image.new("RGB", (W, H), PURPLE)
d = ImageDraw.Draw(img)

# subtle top/bottom bands
d.rectangle([0, 0, W, 12], fill=CORAL)
d.rectangle([0, H - 12, W, H], fill=CYAN)

def font(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", name), size)

playfair = lambda s: font("PlayfairDisplay.ttf", s)
inter = lambda s: font("Inter.ttf", s)

def ctext(y, text, fnt, fill, ls=0):
    if ls:
        # letter-spaced draw
        total = sum(d.textlength(ch, font=fnt) + ls for ch in text) - ls
        x = (W - total) / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill)
            x += d.textlength(ch, font=fnt) + ls
    else:
        w = d.textlength(text, font=fnt)
        d.text(((W - w) / 2, y), text, font=fnt, fill=fill)

# eyebrow
ctext(150, "VALLEY PAWN GIVEAWAY", inter(34), SKY, ls=8)

# big $100
ctext(250, "$100", playfair(300), WHITE)

# every month
ctext(590, "every month", playfair(84), CORAL)

# divider
d.rectangle([(W/2 - 110), 720, (W/2 + 110), 724], fill=CYAN)

# subline
ctext(770, "One customer wins. No purchase.", inter(40), WHITE)
ctext(828, "Follow + enter free:", inter(40), LILAC)

# url pill
url = "thevalleypawn.com/follow"
uf = inter(44)
uw = d.textlength(url, font=uf)
pad = 34
pill = [(W - uw) / 2 - pad, 900, (W + uw) / 2 + pad, 986]
d.rounded_rectangle(pill, radius=43, fill=CORAL)
d.text(((W - uw) / 2, 918), url, font=uf, fill=PURPLE)

# logo bottom
try:
    logo = Image.open(os.path.join(ROOT, "brand_assets", "valley_pawn_landscape_transparent.png")).convert("RGBA")
    lw = 300
    lh = int(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh))
    img.paste(logo, (int((W - lw) / 2), 1010 - lh if 1010 - lh > 0 else 1010), logo)
except Exception as e:
    print("logo skip:", e)

out = os.path.join(ROOT, "giveaway_100_1080.png")
img.save(out, "PNG")
print("SAVED", out)
