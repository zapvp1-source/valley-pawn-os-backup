#!/usr/bin/env python3
"""
vp_deal_compilation.py — Lane B1 companion to vp_deal_reel.py.

Builds ONE 20-25s Valley Pawn brand compilation Reel that strings the week's
store Deal Reels together (one segment each), plus a brand intro and end card.
Also produces publish-ready copies of the individual store reels with a silent
AAC audio track attached.

WHY THE SILENT AUDIO TRACK
--------------------------
vp_deal_reel.py renders video-only mp4s (no music bed — no license, and Reels
autoplay muted). Instagram Reels and TikTok both accept silent video in theory,
but a container with NO audio stream at all is a well-known source of ingest
rejections on both. Attaching a silent AAC track costs ~10 KB and removes an
entire class of publish failure. Originals in reels/ are left untouched
(additive-only); publish copies land in reels/publish/.

WHY SEGMENTS ARE CUT FROM THE RENDERED REELS
--------------------------------------------
Re-deriving cards from the source photos would duplicate vp_deal_reel's layout
logic and drift from it. Cutting a window out of the already-rendered reel
guarantees the compilation looks exactly like the store reels — and it works
identically for the PHOTO treatment and the FLYER treatment, which is the whole
point of classify_source() living in one place.

USAGE
    python3 vp_deal_compilation.py --reels reels/ --out reels/publish/
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from vp_deal_reel import (  # noqa: E402
    NAVY, GOLD, IVORY, W, H, FPS, LOGO_PATH,
    F_DISPLAY, F_BODY, _font, _draw_text_block, _wrap, _ffmpeg,
)

SEG_LEN = 3.6      # seconds taken from each store reel
SEG_START = 6.6    # by which point every treatment has its type fully up
INTRO_LEN = 2.4
OUTRO_LEN = 2.6
# 2.4 + (5 x 3.6) + 2.6 = 23.0s -> inside the 20-25s target


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------
def intro_card(n_items: int) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    y = 640
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        tw = 640
        logo = logo.resize((tw, max(1, int(logo.height * tw / logo.width))), Image.LANCZOS)
        img.paste(logo, ((W - tw) // 2, y), logo)
        y += logo.height + 80
    d.line([(W // 2 - 110, y), (W // 2 + 110, y)], fill=GOLD, width=3)
    y += 54
    y = _draw_text_block(d, ["This Week's Deals"], _font(F_DISPLAY, 92), IVORY, W // 2, y, shadow=False)
    y += 34
    _draw_text_block(
        d,
        [f"{n_items} stores. {n_items} real prices.", "Every one under retail."],
        _font(F_BODY, 44), (*GOLD,) if isinstance(GOLD, tuple) else GOLD, W // 2, y, shadow=False,
    )
    return img


def outro_card(stores: list[str]) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    y = 560
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        tw = 700
        logo = logo.resize((tw, max(1, int(logo.height * tw / logo.width))), Image.LANCZOS)
        img.paste(logo, ((W - tw) // 2, y), logo)
        y += logo.height + 70
    d.line([(W // 2 - 120, y), (W // 2 + 120, y)], fill=GOLD, width=3)
    y += 46
    y = _draw_text_block(d, ['"What\'s Right Is Right"'], _font(F_DISPLAY, 54), GOLD, W // 2, y, shadow=False)
    y += 46
    fs = _font(F_BODY, 40)
    y = _draw_text_block(d, [" · ".join(stores[:3])], fs, IVORY, W // 2, y, shadow=False)
    if len(stores) > 3:
        y = _draw_text_block(d, [" · ".join(stores[3:])], fs, IVORY, W // 2, y + 6, shadow=False)
    y += 30
    y = _draw_text_block(d, ["30-day warranty. Free layaway."], _font(F_BODY, 38), (230, 224, 212), W // 2, y, shadow=False)
    _draw_text_block(d, ["thevalleypawn.com"], _font(F_BODY, 36), GOLD, W // 2, y + 26, shadow=False)
    return img


# ---------------------------------------------------------------------------
# ffmpeg helpers
# ---------------------------------------------------------------------------
def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{' '.join(cmd[:12])}...\n{r.stderr[-1500:]}")


VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-g", str(FPS * 2), "-profile:v", "high", "-level", "4.0"]
AENC = ["-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-ac", "2"]


def still_to_clip(img: Image.Image, seconds: float, out: Path, ff: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "card.png"
        img.save(png)
        _run([ff, "-y", "-loglevel", "error",
              "-loop", "1", "-t", f"{seconds}", "-i", str(png),
              "-f", "lavfi", "-t", f"{seconds}", "-i", "anullsrc=r=44100:cl=stereo",
              *VENC, *AENC, "-shortest", "-movflags", "+faststart", str(out)])


def cut_segment(src: Path, out: Path, ff: str) -> None:
    _run([ff, "-y", "-loglevel", "error",
          "-ss", f"{SEG_START}", "-t", f"{SEG_LEN}", "-i", str(src),
          "-f", "lavfi", "-t", f"{SEG_LEN}", "-i", "anullsrc=r=44100:cl=stereo",
          "-map", "0:v:0", "-map", "1:a:0",
          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0F1A2E,setsar=1",
          *VENC, *AENC, "-movflags", "+faststart", str(out)])


def add_silent_audio(src: Path, out: Path, ff: str) -> None:
    """Publish-ready copy of a store reel with a silent AAC track (video stream copied)."""
    _run([ff, "-y", "-loglevel", "error",
          "-i", str(src),
          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
          "-map", "0:v:0", "-map", "1:a:0",
          "-c:v", "copy", *AENC, "-shortest", "-movflags", "+faststart", str(out)])


def atomic_render(fn, final: Path) -> Path:
    """Render to scratch, then atomically move — the 2026-08-22 truncated-mp4 fix."""
    final.parent.mkdir(parents=True, exist_ok=True)
    for attempt in (1, 2):
        with tempfile.TemporaryDirectory() as td:
            scratch = Path(td) / final.name
            try:
                fn(scratch)
                if not scratch.exists() or scratch.stat().st_size < 50_000:
                    raise RuntimeError(f"output too small: {scratch.stat().st_size if scratch.exists() else 0} bytes")
                shutil.move(str(scratch), str(final))
                return final
            except Exception as e:
                if final.exists():
                    final.unlink()
                if attempt == 2:
                    raise
                print(f"  retry after: {e}")
    raise RuntimeError("unreachable")


# ---------------------------------------------------------------------------
def build_compilation(reels: list[tuple[str, Path]], out: Path) -> Path:
    """reels: ordered [(store, mp4path), ...]"""
    ff = _ffmpeg()
    stores = [s for s, _ in reels]

    def _do(dest: Path) -> None:
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            parts: list[Path] = []
            p = tdp / "00_intro.mp4"
            still_to_clip(intro_card(len(reels)), INTRO_LEN, p, ff)
            parts.append(p)
            for i, (store, src) in enumerate(reels, start=1):
                p = tdp / f"{i:02d}_{store}.mp4"
                cut_segment(src, p, ff)
                parts.append(p)
            p = tdp / "99_outro.mp4"
            still_to_clip(outro_card(stores), OUTRO_LEN, p, ff)
            parts.append(p)

            lst = tdp / "concat.txt"
            lst.write_text("".join(f"file '{q}'\n" for q in parts))
            _run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                  "-c", "copy", "-movflags", "+faststart", str(dest)])

    return atomic_render(_do, out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reels", type=Path, default=ROOT / "reels")
    ap.add_argument("--out", type=Path, default=ROOT / "reels" / "publish")
    ap.add_argument("--order", default="Culpeper,Waynesboro,Harrisonburg,Lexington,Roanoke")
    args = ap.parse_args()

    ff = _ffmpeg()
    code = {"Culpeper": "CUL", "Waynesboro": "WAY", "Harrisonburg": "HAR",
            "Lexington": "LEX", "Roanoke": "ROA"}
    today = date.today().strftime("%Y%m%d")

    found: list[tuple[str, Path]] = []
    for store in args.order.split(","):
        cands = sorted(args.reels.glob(f"*_{code[store]}_dealreel_*.mp4"))
        if cands:
            found.append((store, cands[-1]))
        else:
            print(f"MISSING store reel: {store}")

    args.out.mkdir(parents=True, exist_ok=True)
    result = {"built_at": date.today().isoformat(), "store_reels": {}, "compilation": None}

    for store, src in found:
        dest = args.out / src.name
        try:
            atomic_render(lambda d, s=src: add_silent_audio(s, d, ff), dest)
            result["store_reels"][store] = str(dest)
            print(f"OK  publish-ready: {store} -> {dest.name}")
        except Exception as e:
            print(f"ERR {store}: {e}")

    if len(found) >= 3:
        dest = args.out / f"{today}_BRAND_dealreel_weekcompilation.mp4"
        try:
            build_compilation(found, dest)
            result["compilation"] = str(dest)
            print(f"OK  compilation -> {dest.name}")
        except Exception as e:
            print(f"ERR compilation: {e}")
    else:
        print(f"SKIP compilation: only {len(found)} store reels (<3) — not worth the slot")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
