#!/usr/bin/env python3
"""
vp_comedy_reel.py — Valley Pawn comedy / story short-form video engine (Lane B3).

WHY THIS SHAPE
--------------
Joshua asked for "comedy AI generated videos just to keep engagement." The honest
constraint: there is no text-to-video model reachable from a headless scheduled run
on this Mac. Pretending otherwise would produce a task that fails every week.

What IS reachable, and what actually performs on Reels/TikTok:
  * ffmpeg 8.1.2                    -> assembly, motion, timed reveals
  * PIL + the locked brand fonts    -> typography we fully control
  * Midjourney via ~/.vp-studio     -> stills, when a scene needs one
  * macOS `say`                     -> optional voiceover, no network, no cost
  * real product photos             -> the funniest material we own is real

So this engine builds **beat-timed text video over stills** — the deadpan
card format that carries most successful short-form humor. Critically, it is
built to work MUTED, because Reels and TikTok autoplay muted and 85% of viewers
never turn sound on. The joke lands in the typography and the cut timing, and the
voiceover is a bonus rather than the delivery mechanism.

This is a real format, not a downgrade. "POV: the item" and deadpan counter
observations are exactly what this renders well.

HUMOR GUARDRAILS — enforced in code, not left to the caller
-----------------------------------------------------------
From PILLAR_OVERLAY, and these are Joshua's customers we are talking about:
  * never mock a customer
  * never joke about needing money, being broke, or hard times
  * never firearms
  * punch at objects, never at people
`check_script()` blocks a render outright on a violation. It is deliberately
blunt — a false positive costs one bit, a false negative costs the brand.

USAGE
-----
    python3 vp_comedy_reel.py --spec bit.json --outdir reels/
    python3 vp_comedy_reel.py --selftest

SPEC
----
    {
      "id": "hum_object_pov_20260822",
      "title": "POV: the toolbox",
      "image": "/abs/path.jpg",          # optional; omit for pure card video
      "voice": false,                     # optional macOS `say` voiceover
      "beats": [
        {"text": "POV: you are a Cornwell toolbox", "hold": 2.2},
        {"text": "You have been in the same garage since 1998", "hold": 2.6},
        {"text": "You have seen things", "hold": 2.0},
        {"text": "Mostly sockets", "hold": 2.4, "punch": true}
      ],
      "endcard_store": "Waynesboro"
    }
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Reuse the locked brand primitives — one source of truth for palette/type/end card.
from vp_deal_reel import (  # noqa: E402
    W, H, FPS, NAVY, GOLD, IVORY, CHARCOAL,
    _font, _wrap, _draw_text_block, _ffmpeg,
    F_DISPLAY, F_BODY, layer_endcard, layer_store_chip, ReelError,
)

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------
# Phrases that indicate the bit is joking about a customer's hardship, or about
# people rather than objects. Blunt on purpose — see module docstring.
BANNED_PATTERNS = [
    r"\bbroke\b", r"\bbroke-?ass\b", r"\bdesperate\b", r"\bdead\s*broke\b",
    r"\bcan'?t afford\b", r"\bpayday\b", r"\brent\s+money\b", r"\bevict",
    r"\bpawn\s+(?:your|their)\s+(?:wedding|kid|child|soul)",
    r"\bgun\b", r"\bfirearm", r"\bpistol\b", r"\brifle\b", r"\bshotgun\b",
    r"\bammo\b", r"\bglock\b", r"\bAR-?15\b",
    r"\bloser\b", r"\bidiot\b", r"\bstupid\s+(?:customer|guy|lady|people)\b",
    r"\bdrunk\b", r"\bjunkie\b", r"\baddict\b", r"\bhomeless\b",
    r"\bdivorce\b", r"\bex-?wife\b", r"\bex-?husband\b",
]

# Words that suggest the subject is a person rather than an object. Not banned
# outright — flagged, because "our team" content is legitimate. The caller must
# confirm the bit punches at the object.
PERSON_HINTS = [r"\bcustomer\b", r"\bguy who\b", r"\blady who\b", r"\bthis dude\b"]


def check_script(beats: list[dict], title: str = "") -> tuple[bool, list[str]]:
    """Return (ok, problems). A single hard hit blocks the render."""
    text = " ".join([title] + [b.get("text", "") for b in beats]).lower()
    problems = [f"banned pattern: /{p}/" for p in BANNED_PATTERNS if re.search(p, text)]
    warnings = [f"person-subject hint: /{p}/ — confirm the bit punches at the OBJECT"
                for p in PERSON_HINTS if re.search(p, text)]
    if not beats:
        problems.append("no beats")
    if any(not b.get("text", "").strip() for b in beats):
        problems.append("empty beat text — a silent card is not a joke")
    return (not problems), problems + warnings


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def build_backdrop(image: Path | None, out: Path) -> None:
    """Darkened, blurred still behind the cards — or a clean brand field."""
    cw, ch = int(W * 1.2), int(H * 1.2)
    if image and image.exists():
        try:
            src = Image.open(image).convert("RGB")
            scale = max(cw / src.width, ch / src.height)
            im = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
            left, top = (im.width - cw) // 2, (im.height - ch) // 2
            im = im.crop((left, top, left + cw, top + ch)).filter(ImageFilter.GaussianBlur(14))
            # Heavy navy wash: the still sets mood, the type carries the joke.
            im = Image.blend(im, Image.new("RGB", (cw, ch), NAVY), 0.62)
            im.save(out, "PNG")
            return
        except Exception:
            pass  # fall through to the clean field — never fail a bit over a backdrop
    field = Image.new("RGB", (cw, ch), NAVY)
    d = ImageDraw.Draw(field)
    for i in range(0, ch, 4):   # subtle vertical gradient so it isn't flat black
        a = int(18 * (i / ch))
        d.line([(0, i), (cw, i)], fill=(NAVY[0] + a, NAVY[1] + a, NAVY[2] + a))
    field.save(out, "PNG")


def layer_beat(text: str, punch: bool = False) -> Image.Image:
    """One centered card. The punchline gets the display serif and the gold."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if punch:
        size = 96 if len(text) <= 34 else (78 if len(text) <= 60 else 62)
        font, fill = _font(F_DISPLAY, size), (*GOLD, 255)
    else:
        size = 74 if len(text) <= 40 else (62 if len(text) <= 70 else 52)
        font, fill = _font(F_BODY, size), (*IVORY, 255)

    lines = _wrap(d, text, font, W - 170)[:5]
    block_h = int(font.size * 1.25) * len(lines)
    top = (H - block_h) // 2

    # Soft plate behind the type so it reads over any backdrop.
    pad = 56
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle(
        [70, top - pad, W - 70, top + block_h + pad], radius=36, fill=(*NAVY, 170)
    )
    img.alpha_composite(plate.filter(ImageFilter.GaussianBlur(18)))

    _draw_text_block(d, lines, font, fill, W // 2, top, leading=1.25)
    if punch:
        d.line([(W // 2 - 90, top + block_h + 30), (W // 2 + 90, top + block_h + 30)],
               fill=(*GOLD, 220), width=3)
    return img


def render_comedy(spec: dict, outdir: Path) -> tuple[bool, str, Path | None]:
    beats = spec.get("beats", [])
    ok, problems = check_script(beats, spec.get("title", ""))
    if not ok:
        return False, "GUARDRAIL BLOCK — " + "; ".join(problems), None

    outdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "", spec.get("id", "bit").lower())[:34] or "bit"
    out = outdir / f"{slug}.mp4"

    store = spec.get("endcard_store", "")
    END = 2.2          # end-card duration
    FADE = 0.30

    starts, t = [], 0.0
    for b in beats:
        hold = float(b.get("hold", 2.4))
        starts.append((t, t + hold))
        t += hold
    total = round(t + END, 2)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        img = spec.get("image")
        build_backdrop(Path(img).expanduser() if img else None, tmp / "bg.png")

        for i, b in enumerate(beats):
            layer_beat(b.get("text", ""), bool(b.get("punch"))).save(tmp / f"b{i}.png", "PNG")
        layer_endcard(store or "Valley Pawn", None).save(tmp / "end.png", "PNG")
        if store:
            layer_store_chip(store).save(tmp / "chip.png", "PNG")

        # Very slow drift on the backdrop so a static still never looks frozen.
        parts = [f"[0:v]zoompan=z='min(zoom+0.00022,1.18)':d={int(total*FPS)}:"
                 f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
                 f"format=rgba[base]"]
        prev, idx = "base", 0
        inputs = [tmp / "bg.png"]

        for i, (t0, t1) in enumerate(starts):
            idx += 1
            inputs.append(tmp / f"b{i}.png")
            parts.append(
                f"[{idx}:v]format=rgba,fade=t=in:st={t0}:d={FADE}:alpha=1,"
                f"fade=t=out:st={max(t0, t1 - FADE)}:d={FADE}:alpha=1[L{idx}]")
            parts.append(f"[{prev}][L{idx}]overlay=0:0:"
                         f"enable='between(t,{t0},{t1})':format=auto[v{idx}]")
            prev = f"v{idx}"

        if store:
            idx += 1
            inputs.append(tmp / "chip.png")
            chip_end = round(t, 2)
            parts.append(f"[{idx}:v]format=rgba,fade=t=in:st=0.2:d={FADE}:alpha=1,"
                         f"fade=t=out:st={max(0.2, chip_end - FADE)}:d={FADE}:alpha=1[L{idx}]")
            parts.append(f"[{prev}][L{idx}]overlay=0:0:"
                         f"enable='between(t,0.2,{chip_end})':format=auto[v{idx}]")
            prev = f"v{idx}"

        idx += 1
        inputs.append(tmp / "end.png")
        parts.append(f"[{idx}:v]format=rgba,fade=t=in:st={round(t,2)}:d={FADE}:alpha=1[L{idx}]")
        parts.append(f"[{prev}][L{idx}]overlay=0:0:"
                     f"enable='between(t,{round(t,2)},{total})':format=auto[v{idx}]")
        prev = f"v{idx}"
        parts.append(f"[{prev}]format=yuv420p[vout]")

        cmd = [_ffmpeg(), "-y", "-loglevel", "error"]
        for p in inputs:
            cmd += ["-loop", "1", "-t", str(total), "-i", str(p)]

        # Optional voiceover. Deliberately optional: the bit must land muted, and
        # a TTS failure must never cost us the video.
        audio_ok = False
        if spec.get("voice"):
            script = ". ".join(b.get("text", "") for b in beats)
            aiff, m4a = tmp / "vo.aiff", tmp / "vo.m4a"
            try:
                subprocess.run(["/usr/bin/say", "-v", "Evan", "-o", str(aiff), script],
                               capture_output=True, timeout=90, check=True)
                subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", str(aiff),
                                "-c:a", "aac", "-b:a", "128k", str(m4a)],
                               capture_output=True, timeout=90, check=True)
                cmd += ["-i", str(m4a)]
                audio_ok = True
            except Exception:
                audio_ok = False

        cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]"]
        if audio_ok:
            cmd += ["-map", f"{len(inputs)}:a", "-c:a", "aac", "-shortest"]
        staged = tmp / "out.mp4"
        cmd += [
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
            "-movflags", "+faststart", "-t", str(total), str(staged),
        ]

        # Encode to scratch, then move — same lesson as vp_deal_reel: writing
        # faststart output directly into ~/Documents races Drive/Spotlight and
        # can leave a truncated file that looks like a real deliverable.
        last = ""
        for _ in (1, 2):
            staged.unlink(missing_ok=True)
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0 and staged.exists() and staged.stat().st_size >= 150_000:
                out.unlink(missing_ok=True)
                shutil.move(str(staged), str(out))
                return True, f"{total:.1f}s, {len(beats)} beats" + (", VO" if audio_ok else ""), out
            last = (proc.stderr or "")[-300:]
        out.unlink(missing_ok=True)
        return False, f"ffmpeg failed after 2 attempts: {last}", None


# ---------------------------------------------------------------------------
SELFTEST = {
    "id": "hum_object_pov_selftest",
    "title": "POV: the toolbox",
    "voice": False,
    "endcard_store": "Waynesboro",
    "beats": [
        {"text": "POV: you're a Cornwell toolbox", "hold": 2.2},
        {"text": "Same garage since 1998", "hold": 2.4},
        {"text": "You've held every socket that ever went missing", "hold": 3.0},
        {"text": "You know exactly where they are", "hold": 2.4},
        {"text": "You're not telling", "hold": 2.6, "punch": True},
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Valley Pawn comedy reel engine")
    ap.add_argument("--spec", type=Path)
    ap.add_argument("--outdir", type=Path, default=ROOT / "reels")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-only", action="store_true",
                    help="run the humor guardrails against a spec and exit")
    a = ap.parse_args()

    specs = [SELFTEST] if a.selftest else json.loads(a.spec.read_text())
    if isinstance(specs, dict):
        specs = [specs]

    if a.check_only:
        for s in specs:
            ok, probs = check_script(s.get("beats", []), s.get("title", ""))
            print(f"{'PASS' if ok else 'BLOCK'}  {s.get('id')}")
            for p in probs:
                print(f"       {p}")
        return 0

    rc = 0
    for s in specs:
        ok, msg, path = render_comedy(s, a.outdir)
        print(f"  {'OK  ' if ok else 'FAIL'} {s.get('id','?'):<34} {msg}")
        if not ok:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
