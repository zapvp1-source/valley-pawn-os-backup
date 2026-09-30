#!/usr/bin/env python3
"""Render the MobilePawn download graphics (1080x1080): one Brand + one per store (store-named,
so no identical image is reused across physical stores — vp_social_publisher image gate)."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
HERE = Path(__file__).parent; OUT = HERE / "graphics"
PURPLE, CORAL, GOLD, WHITE, LAV = "#2D1A5E", "#F58C8A", "#c97b3a", "#FFFFFF", "#E6DEF7"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def f(p, s): return ImageFont.truetype(p, s)
def center(d, y, text, font, fill, W=1080):
    w = d.textbbox((0, 0), text, font=font)[2]; d.text(((W - w) / 2, y), text, font=font, fill=fill)
def render(label, fname):
    im = Image.new("RGB", (1080, 1080), PURPLE); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 60, 1020, 250), 28, fill=WHITE)
    logo = Image.open(OUT / "vp_logo.png").convert("RGBA"); logo.thumbnail((860, 150))
    im.paste(logo, ((1080 - logo.width) // 2, 155 - logo.height // 2), logo)
    center(d, 300, "GET THE FREE APP", f(B, 40), GOLD)
    center(d, 370, "Pay your loan", f(B, 92), WHITE)
    center(d, 475, "from your phone", f(B, 92), WHITE)
    for i, line in enumerate(["Extend or pay loans  •  Layaway payments", "Check due dates anytime"]):
        center(d, 620 + i * 56, line, f(R, 40), LAV)
    d.rounded_rectangle((200, 780, 880, 890), 55, fill=CORAL)
    center(d, 805, "Download MobilePawn", f(B, 50), PURPLE)
    lines = label.split("\n")
    for i, line in enumerate(lines):
        center(d, (935 if len(lines) == 1 else 920) + i * 52, line, f(B, 40 if i == 0 else 34), WHITE if i == 0 else LAV)
    im.save(OUT / fname, quality=92)
render("thevalleypawn.com/app", "mobilepawn_brand.png")
for s in ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]:
    render(f"Valley Pawn {s}\nthevalleypawn.com/app", f"mobilepawn_{s.lower()}.png")
print("ok")
