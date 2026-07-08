#!/usr/bin/env python3
"""
Valley Pawn — Casual Video Processor (Part 3 of the 2026-07-06 strategic build)

Watches casual-video-inbox/ for phone-shot clips, then per new file:
  1. Transcribe via Whisper (openai-whisper, faster-whisper, or whisper CLI — first found)
  2. Burn captions (brand spec: Inter/ivory on navy pill, bottom third)
  3. Lower-third title (first 3s) from sidecar .txt line 1 or transcript
  4. Normalize to 1080x1920 9:16 (navy pads if horizontal)
  5. Append 1.5s brand end-card (auto-generated navy card if none exists)
  6. Auto-schedule to Publer: Brand FB + IG + TikTok at next evening slot,
     plus a second Publer job for X with a <=270-char compressed caption.
     (Joshua's 2026-07-06 decision: auto-schedule, no approval gate.)

Publer media: tries direct API upload (POST /media). If Publer rejects it, the
processed file is left in outbox/ and status "needs_ui_upload" is reported so the
scheduled-task session can fall back to the Chrome composer flow (droparea[5]).

Usage:
  python3 casual_video_processor.py                 # process everything new
  python3 casual_video_processor.py --dry-run       # process but don't schedule
  python3 casual_video_processor.py --file X.mp4    # one file

Exit: prints one JSON status line per file + a final summary JSON line.
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from publer_client import PublerClient, PublerError  # noqa: E402

ET = ZoneInfo("America/New_York")
INBOX = Path.home() / "Documents/Claude/Projects/Valley Pawn Studios/casual-video-inbox"
PROCESSED = INBOX / "processed"
OUTBOX = INBOX / "outbox"          # finished MP4s awaiting/after scheduling
FAILED_LOG = INBOX / "failed.log"
ENDCARD = INBOX / "endcard_1080x1920.png"
BRAND_ASSETS = Path(__file__).parent / "brand_assets"

NAVY = "0x0F1A2E"
IVORY = "0xF4EDE0"
BRASS = "#B08A3E"
VIDEO_EXT = {".mp4", ".mov", ".m4v"}

STORE_FOOTER = (
    "\U0001F4CD 125 Walker St, Lexington\n"
    "\U0001F4CD 1321 W Broad St, Waynesboro\n"
    "\U0001F4CD 1790 E Market St, Ste 22, Harrisonburg\n"
    "\U0001F4CD 571 James Madison Hwy, Culpeper\n"
    "\U0001F4CD 2362 Peters Creek Rd Ste C, Roanoke"
)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def which(name: str) -> str | None:
    return shutil.which(name)


# ---------------- transcription ----------------

def transcribe(video: Path, workdir: Path) -> tuple[str, Path | None]:
    """Return (plain_text, segments list of {start,end,text}). Tries faster-whisper, openai-whisper."""
    # 1) faster-whisper (installed 2026-07-06)
    try:
        from faster_whisper import WhisperModel  # type: ignore
        model = WhisperModel("base", compute_type="int8")
        segments, _ = model.transcribe(str(video))
        segs = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
        return " ".join(s["text"] for s in segs), segs
    except ImportError:
        pass
    except Exception as e:
        print(json.dumps({"warn": f"faster-whisper failed: {e}"}))
    # 2) openai-whisper python
    try:
        import whisper  # type: ignore
        model = whisper.load_model("base")
        result = model.transcribe(str(video))
        segs = [{"start": s["start"], "end": s["end"], "text": s["text"].strip()}
                for s in result.get("segments", [])]
        return result["text"].strip(), segs
    except ImportError:
        pass
    except Exception as e:
        print(json.dumps({"warn": f"openai-whisper failed: {e}"}))
    return "", []


def _brand_font(size: int):
    """Inter Bold if present, else best system fallback (this ffmpeg build has no
    drawtext/subtitles filters, so ALL text is rendered via Pillow → overlay)."""
    from PIL import ImageFont
    for f in [str(Path.home() / ".vp-studio/fonts/Inter-Bold.ttf"),
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_text_png(text: str, out: Path, fontsize: int = 48, max_width: int = 940) -> Path:
    """Brand caption pill: ivory Inter on navy @75%, rounded rect, transparent canvas."""
    from PIL import Image, ImageDraw
    font = _brand_font(fontsize)
    # word-wrap
    words, lines, cur = text.split(), [], ""
    probe_img = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(probe_img)
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_width - 48:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:3] or [""]
    line_h = fontsize + 14
    pad = 24
    box_w = min(max_width, int(max(d.textlength(l, font=font) for l in lines)) + pad * 2)
    box_h = line_h * len(lines) + pad * 2 - 8
    img = Image.new("RGBA", (1080, box_h + 8), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    x0 = (1080 - box_w) // 2
    dr.rounded_rectangle([x0, 4, x0 + box_w, 4 + box_h], radius=22,
                         fill=(15, 26, 46, 191))  # navy @75%
    y = 4 + pad - 4
    for l in lines:
        dr.text((540, y), l, font=font, fill=(244, 237, 224, 255), anchor="ma")
        y += line_h
    img.save(out)
    return out


# ---------------- end-card ----------------

def ensure_endcard() -> Path:
    """Return path to the 1080x1920 end-card PNG, generating a brand-floor one if missing."""
    if ENDCARD.exists():
        return ENDCARD
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1080, 1920), "#0F1A2E")
    d = ImageDraw.Draw(img)
    logo = None
    for cand in ["valley_pawn_profile_1080.png"]:
        p = BRAND_ASSETS / cand
        if p.exists():
            logo = Image.open(p).convert("RGBA").resize((420, 420))
            break
    if logo is not None:
        img.paste(logo, ((1080 - 420) // 2, 480), logo)

    def font(size):
        for f in ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                  str(Path.home() / ".vp-studio/fonts/Inter-Bold.ttf"),
                  "/System/Library/Fonts/Helvetica.ttc"]:
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue
        return ImageFont.load_default()

    d.text((540, 1050), "VALLEY PAWN", font=font(72), fill=BRASS, anchor="mm")
    d.text((540, 1160), "What's right is right.", font=font(44), fill="#F4EDE0", anchor="mm")
    d.text((540, 1420), "Lexington • Waynesboro • Harrisonburg", font=font(30),
           fill="#F4EDE0", anchor="mm")
    d.text((540, 1475), "Culpeper • Roanoke", font=font(30), fill="#F4EDE0", anchor="mm")
    ENDCARD.parent.mkdir(parents=True, exist_ok=True)
    img.save(ENDCARD)
    return ENDCARD


# ---------------- video processing ----------------

def probe(video: Path) -> dict:
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams",
             "-show_format", str(video)])
    return json.loads(r.stdout or "{}")


def process_video(video: Path, title: str, segments: list[dict], workdir: Path) -> Path:
    """Normalize to 1080x1920, overlay Pillow-rendered captions + lower-third, append end-card.

    NOTE: the local ffmpeg build has NO drawtext/subtitles filters — all text is
    pre-rendered to PNGs (brand spec) and composited with the `overlay` filter.
    """
    out = OUTBOX / (video.stem + "_final.mp4")
    OUTBOX.mkdir(parents=True, exist_ok=True)

    # Build overlay inputs: [1]=title, [2..]=caption segments (cap at 24 overlays)
    inputs: list[str] = ["-i", str(video)]
    overlays: list[tuple[int, float, float, str]] = []  # (input_idx, start, end, y_expr)
    idx = 1
    if title:
        p = render_text_png(title, workdir / "title.png", fontsize=52)
        inputs += ["-i", str(p)]
        overlays.append((idx, 0.4, 3.5, "180"))
        idx += 1
    for i, seg in enumerate(segments[:24]):
        text = seg["text"].strip()
        if not text:
            continue
        p = render_text_png(text, workdir / f"cap{i}.png", fontsize=44)
        inputs += ["-i", str(p)]
        overlays.append((idx, float(seg["start"]), float(seg["end"]) + 0.15, "main_h*0.72"))
        idx += 1

    chain = ("[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
             f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color={NAVY}[v0]")
    cur = "v0"
    for n, (inp, s, e, y) in enumerate(overlays):
        nxt = f"v{n + 1}"
        chain += (f";[{cur}][{inp}:v]overlay=x=(main_w-overlay_w)/2:y={y}"
                  f":enable='between(t\\,{s:.2f}\\,{e:.2f})'[{nxt}]")
        cur = nxt

    main = workdir / "main.mp4"
    r = run(["ffmpeg", "-y", *inputs, "-filter_complex", chain,
             "-map", f"[{cur}]", "-map", "0:a?",
             "-r", "24", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", str(main)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg main pass failed: {r.stderr[-400:]}")

    # end-card 1.5s (silent audio track so concat keeps streams aligned)
    card = ensure_endcard()
    cardclip = workdir / "card.mp4"
    r = run(["ffmpeg", "-y", "-loop", "1", "-t", "1.5", "-i", str(card),
             "-f", "lavfi", "-t", "1.5", "-i", "anullsrc=r=44100:cl=stereo",
             "-r", "24", "-c:v", "libx264", "-crf", "20", "-c:a", "aac",
             "-pix_fmt", "yuv420p", "-shortest", str(cardclip)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg end-card failed: {r.stderr[-400:]}")

    concat_list = workdir / "concat.txt"
    concat_list.write_text(f"file '{main}'\nfile '{cardclip}'\n")
    r = run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(out)])
    if r.returncode != 0:
        # fallback: re-encode concat
        r = run(["ffmpeg", "-y", "-i", str(main), "-i", str(cardclip),
                 "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                 "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20",
                 "-c:a", "aac", "-pix_fmt", "yuv420p", str(out)])
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {r.stderr[-400:]}")
    return out


# ---------------- captions & scheduling ----------------

def build_captions(title: str, transcript: str, sidecar_caption: str) -> tuple[str, str]:
    """Return (main_caption for FB/IG/TikTok, x_caption <=270 chars)."""
    if sidecar_caption:
        body = sidecar_caption.strip()
    else:
        snippet = " ".join(transcript.split()[:28]).strip()
        body = (title or "Straight from the counter.")
        if snippet and snippet.lower() not in body.lower():
            body += f"\n\n“{snippet}…”"
    main = f"{body}\n\n{STORE_FOOTER}"
    x = body.split("\n")[0][:250] + " #ValleyPawn"
    return main, x[:270]


def next_evening_slot(now: datetime | None = None) -> datetime:
    """Next 5-8 PM ET slot: today 18:00 if >45 min away, else tomorrow 18:00."""
    now = now or datetime.now(ET)
    slot = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if slot <= now + timedelta(minutes=45):
        slot += timedelta(days=1)
    return slot


def publer_upload_media(p: PublerClient, path: Path) -> str | None:
    """Try Publer direct media upload. Returns hosted URL or None."""
    import requests
    for endpoint in ("/media", "/media/upload"):
        try:
            with open(path, "rb") as fh:
                r = requests.post(
                    p.api_base + endpoint,
                    headers={"Authorization": f"Bearer-API {p.api_key}",
                             "Publer-Workspace-Id": p.workspace_id or ""},
                    files={"file": (path.name, fh, "video/mp4")},
                    timeout=300,
                )
            if r.ok:
                data = r.json() if r.text.strip() else {}
                for k in ("url", "media_url", "path", "location"):
                    v = data.get(k) if isinstance(data, dict) else None
                    if isinstance(v, str) and v.startswith("http"):
                        return v
                if isinstance(data, dict) and isinstance(data.get("media"), dict):
                    v = data["media"].get("url")
                    if isinstance(v, str) and v.startswith("http"):
                        return v
        except Exception as e:
            print(json.dumps({"warn": f"publer upload {endpoint}: {e}"}))
    return None


def schedule(p: PublerClient, video_url: str, main_caption: str, x_caption: str,
             when: datetime) -> dict:
    iso = when.isoformat()
    j1 = p.schedule_post(text=main_caption,
                         store_keys=["Brand", "BrandIG", "BrandTikTok"],
                         scheduled_at=iso, video_url=video_url)
    j2 = p.schedule_post(text=x_caption, store_keys=["BrandTwitter"],
                         scheduled_at=iso, video_url=video_url)
    return {"main_job": j1, "x_job": j2, "scheduled_at": iso}


# ---------------- main ----------------

def process_one(video: Path, p: PublerClient | None, dry_run: bool) -> dict:
    status: dict = {"file": video.name}
    workdir = Path(tempfile.mkdtemp(prefix="vpcv_"))
    try:
        sidecar = video.with_suffix(".txt")
        title, sidecar_caption = "", ""
        if sidecar.exists():
            lines = sidecar.read_text().strip().splitlines()
            title = lines[0].strip() if lines else ""
            sidecar_caption = "\n".join(lines[1:]).strip()

        transcript, segments = transcribe(video, workdir)
        if not title:
            words = transcript.split()
            title = " ".join(words[:7]) if words else ""
        status["transcribed"] = bool(transcript)

        final = process_video(video, title, segments, workdir)
        status["output"] = str(final)
        (OUTBOX / (video.stem + "_meta.json")).write_text(json.dumps({
            "source": video.name, "title": title, "transcript": transcript,
            "processed_at": datetime.now(ET).isoformat()}, indent=2))

        main_caption, x_caption = build_captions(title, transcript, sidecar_caption)
        status["caption"] = main_caption[:120]

        if dry_run or p is None:
            status["scheduled"] = False
            status["status"] = "processed_only"
        else:
            url = publer_upload_media(p, final)
            if url:
                res = schedule(p, url, main_caption, x_caption, next_evening_slot())
                status.update({"scheduled": True, "status": "scheduled", **res})
            else:
                status.update({"scheduled": False, "status": "needs_ui_upload",
                               "main_caption": main_caption, "x_caption": x_caption,
                               "target_slot": next_evening_slot().isoformat()})

        PROCESSED.mkdir(parents=True, exist_ok=True)
        shutil.move(str(video), PROCESSED / video.name)
        if sidecar.exists():
            shutil.move(str(sidecar), PROCESSED / sidecar.name)
    except Exception as e:
        status["status"] = "failed"
        status["error"] = str(e)[:400]
        with open(FAILED_LOG, "a") as fh:
            fh.write(f"{datetime.now(ET).isoformat()} {video.name}: {e}\n")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return status


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--file", help="process only this file (name or path)")
    args = ap.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    if not which("ffmpeg") or not which("ffprobe"):
        print(json.dumps({"status": "fatal", "error": "ffmpeg/ffprobe not on PATH"}))
        sys.exit(2)

    if args.file:
        f = Path(args.file)
        candidates = [f if f.exists() else INBOX / f.name]
    else:
        candidates = sorted(x for x in INBOX.iterdir()
                            if x.suffix.lower() in VIDEO_EXT and x.is_file())
    if not candidates:
        print(json.dumps({"status": "empty", "inbox": str(INBOX)}))
        return

    p = None
    if not args.dry_run:
        try:
            p = PublerClient()
        except PublerError as e:
            print(json.dumps({"warn": f"Publer client unavailable: {e}"}))

    results = [process_one(v, p, args.dry_run) for v in candidates]
    for r in results:
        print(json.dumps(r))
    ok = sum(1 for r in results if r.get("status") in ("scheduled", "processed_only"))
    print(json.dumps({"status": "done", "processed": ok, "total": len(results),
                      "needs_ui_upload": [r["file"] for r in results
                                          if r.get("status") == "needs_ui_upload"],
                      "failed": [r["file"] for r in results if r.get("status") == "failed"]}))


if __name__ == "__main__":
    main()
