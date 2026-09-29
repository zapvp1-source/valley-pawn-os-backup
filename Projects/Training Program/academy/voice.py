#!/usr/bin/env python3
"""
Valley Pawn Academy - ElevenLabs voiceover generator (standard library only).

Narration for each lesson = the Start card intro line, every slide's `say` (after the builder's
learner-text cleaner), and the key points. MP3s are cached under academy/media/voice/ by a hash of
voice + model + settings + the exact text sent, so only new or changed text is ever billed.
build_scorm.py embeds whatever is in the cache; anything missing falls back to browser speech.

Setup: academy/.elevenlabs.json (never commit or share it; see BUILD_README.md)
    {"api_key": "...", "voice_id": "...", "model_id": "eleven_multilingual_v2"}

Commands:
    python3 voice.py voices                                  # list voices on the account
    python3 voice.py estimate                                # billable (uncached) characters per lesson
    python3 voice.py sample --text "..." --out media/voice/sample.mp3
    python3 voice.py generate --lesson L1-01                 # one lesson
    python3 voice.py generate --all                          # everything not yet cached

API (verified 2026-09-28 against https://elevenlabs.io/docs/api-reference/text-to-speech/convert):
    POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_64
    header xi-api-key; JSON {"text", "model_id", "voice_settings": {...}}; 200 = audio bytes.
    Voices: GET https://api.elevenlabs.io/v2/voices?page_size=100[&next_page_token=...]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ACADEMY = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ACADEMY, ".elevenlabs.json")
VOICE_DIR = os.path.join(ACADEMY, "media", "voice")
LESSONS_DIR = os.path.join(ACADEMY, "lessons")

API_BASE = "https://api.elevenlabs.io"
OUTPUT_FORMAT = "mp3_44100_64"          # 64 kbps keeps packages small (the audio is base64-embedded)
DEFAULT_MODEL = "eleven_multilingual_v2"
# Used only when .elevenlabs.json has no voice_id ("George", the voice in ElevenLabs' own API examples).
# Pick your own with `python3 voice.py voices`; changing voices re-bills every line (new cache keys).
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True}
MAX_CHARS_PER_REQUEST = 9500             # multilingual v2 accepts 10,000 per request

# Pronunciation fixes, applied ONLY to the text sent to ElevenLabs (never to what learners read).
# Applied in this order. Keys made of letters/digits match whole words only. Tune freely: a change
# here changes the cache key of every line it touches, so only those lines are re-billed.
PRONUNCIATION = {
    "Va. Code": "Virginia Code",
    "e.g.": "for example",
    "P&P": "P and P",
    "A&D": "A and D",
    "§§": "sections ",
    "§": "section ",
    "4473": "forty-four seventy-three",
    "FFLs": "F F Ls",
    "FFL": "F F L",
    "TCPA": "T C P A",
    "GLBA": "G L B A",
    "dwt": "pennyweight",
    # "Bravo" and "eBay" are read correctly as written; dollar amounts are left to ElevenLabs.
}


def _pron_rx(key):
    esc = re.escape(key)
    if re.match(r"\w", key):
        esc = r"\b" + esc
    if re.search(r"\w$", key):
        esc = esc + r"\b"
    return re.compile(esc)


_PRON = [(_pron_rx(k), v) for k, v in PRONUNCIATION.items()]


def tts_text(text):
    """Display text -> the text actually sent to ElevenLabs."""
    s = str(text or "")
    for rx, rep in _PRON:
        s = rx.sub(rep, s)
    return re.sub(r"\s{2,}", " ", s).strip()


# --------------------------------------------------------------------------- config / cache
def load_config(require_key=False):
    cfg = {}
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg = json.load(f) or {}
        except (OSError, ValueError) as e:
            sys.exit(f"Could not read {CONFIG_PATH}: {e}")
    key = str(cfg.get("api_key") or os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if require_key and not key:
        sys.exit("No ElevenLabs API key. Create academy/.elevenlabs.json with "
                 '{"api_key": "...", "voice_id": "...", "model_id": "eleven_multilingual_v2"} (see BUILD_README.md).')
    rot = [str(v).strip() for v in (cfg.get("voice_rotation") or []) if str(v).strip()]
    return {"api_key": key,
            "voice_id": str(cfg.get("voice_id") or (rot[0] if rot else "") or DEFAULT_VOICE).strip(),
            "model_id": str(cfg.get("model_id") or DEFAULT_MODEL).strip(),
            "voice_rotation": rot}


def level_order(lesson_id):
    """'L3-05' -> (3, 5); 'M-02' -> (9, 2)."""
    m = re.match(r"^(?:L(\d+)|M)-(\d+)$", str(lesson_id))
    if not m:
        return 0, 0
    return (int(m.group(1)) if m.group(1) else 9), int(m.group(2))


def lesson_cfg(cfg, lesson_id):
    """Joshua 2026-09-28: rotate narrators across lessons for engagement. One voice per lesson
    (consistent within a lesson); the voice is chosen from level+order so adding a lesson never
    changes another lesson's narrator (which would re-bill it)."""
    rot = cfg.get("voice_rotation") or []
    if not rot:
        return cfg
    lv, od = level_order(lesson_id)
    c = dict(cfg)
    c["voice_id"] = rot[(lv + od) % len(rot)]
    return c


def cache_key(sent_text, voice_id, model_id):
    settings = json.dumps(VOICE_SETTINGS, sort_keys=True) + "|" + OUTPUT_FORMAT
    return hashlib.sha1((voice_id + "|" + model_id + "|" + settings + "|" + sent_text).encode("utf-8")).hexdigest()


def cache_path(display_text, cfg=None):
    """Where the MP3 for this (display) text lives, for the configured voice/model."""
    cfg = cfg or load_config()
    return os.path.join(VOICE_DIR, cache_key(tts_text(display_text), cfg["voice_id"], cfg["model_id"]) + ".mp3")


def is_mp3(data):
    return bool(data) and (data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0))


# --------------------------------------------------------------------------- narration text
def _sentence(t):
    t = str(t or "").strip()
    return t if not t or t[-1] in ".!?" else t + "."


def intro_line(title, minutes):
    m = f"about {minutes} minutes" if minutes else "a few minutes"
    title = str(title or "").strip().rstrip(".")
    lead = f"{title}." if re.match(r"welcome\b", title, re.I) else f"Welcome to {title}."  # "Welcome to Valley Pawn"
    return f"{lead} This takes {m}, and there's a short test at the end."


def narration_items(payload):
    """The narration plan for one lesson, from the builder's learner payload (already cleaned).
    Returns an ordered list of (key, display_text): "intro", slide indexes "0".."n-1", "keypoints".
    Slide keys index the slides the player shows (slides with a heading or bullets).
    Slides are skipped when the lesson plays a video instead. The result screen is silent."""
    items = [("intro", intro_line(payload.get("title") or payload.get("id"), payload.get("minutes")))]
    if not (payload.get("media") or {}).get("video"):
        shown = [s for s in payload.get("slides") or [] if s and (s.get("heading") or s.get("bullets"))]
        for i, s in enumerate(shown):
            t = s.get("say") or ". ".join([s.get("heading") or ""] + list(s.get("bullets") or []))
            if str(t).strip():
                items.append((str(i), str(t).strip()))
    kps = [k for k in payload.get("key_points") or [] if str(k).strip()]
    if kps:
        items.append(("keypoints", "Here are the key points. " + " ".join(_sentence(k) for k in kps)))
    return items


def lesson_payload(path):
    """Build the same learner payload the builder embeds (so narration always matches the slides)."""
    sys.path.insert(0, ACADEMY)
    import build_scorm as B
    with open(path, encoding="utf-8") as f:
        lesson = json.load(f)
    info, _, _ = B.resolve_media(lesson)
    media = {"video": info.get("video"), "video_kind": info.get("video_kind"),
             "clip": info.get("clip"), "clip_label": info.get("clip_label")}
    return lesson, B.learner_payload(lesson, media)


def all_lesson_paths():
    return sorted(glob.glob(os.path.join(LESSONS_DIR, "*", "*.json")))


def find_lesson(lid):
    for p in all_lesson_paths():
        try:
            with open(p, encoding="utf-8") as f:
                if json.load(f).get("id") == lid:
                    return p
        except (OSError, ValueError):
            continue
    sys.exit(f"No lesson with id {lid} under lessons/")


# --------------------------------------------------------------------------- HTTP
class StopBilling(Exception):
    """Auth / payment / quota problem: retrying will not help."""


def _detail(body):
    try:
        d = json.loads(body.decode("utf-8", "replace")).get("detail")
    except (ValueError, AttributeError):
        return body[:300].decode("utf-8", "replace")
    if isinstance(d, dict):
        return " / ".join(str(d.get(k)) for k in ("code", "status", "message") if d.get(k))
    return str(d)[:300]


def _request(method, url, api_key, payload=None, accept="application/json", tries=6):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    delay = 2.0
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(url, data=data, method=method, headers={
            "xi-api-key": api_key, "Content-Type": "application/json", "Accept": accept})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read() or b""
            det = _detail(body)
            quota = re.search(r"quota|credits|payment|insufficient", det, re.I)
            if e.code in (401, 402, 403) or quota:
                why = {401: "the API key was rejected (or the account's quota is used up)",
                       402: "the account is out of credits / payment is required",
                       403: "the key doesn't have permission for this"}.get(e.code, "quota problem")
                raise StopBilling(f"ElevenLabs HTTP {e.code}: {why}. Detail: {det}. Nothing more will be sent.")
            if e.code == 429 or e.code >= 500:
                if attempt == tries:
                    raise RuntimeError(f"ElevenLabs HTTP {e.code} after {tries} tries: {det}")
                wait = delay
                ra = e.headers.get("Retry-After") if e.headers else None
                if ra and ra.isdigit():
                    wait = max(wait, float(ra))
                print(f"    HTTP {e.code} ({det or 'busy'}), retrying in {wait:.0f}s")
                time.sleep(wait)
                delay = min(delay * 2, 60)
                continue
            raise RuntimeError(f"ElevenLabs HTTP {e.code}: {det}")
        except urllib.error.URLError as e:
            if attempt == tries:
                raise RuntimeError(f"network error: {e.reason}")
            print(f"    network error ({e.reason}), retrying in {delay:.0f}s")
            time.sleep(delay)
            delay = min(delay * 2, 60)


def synthesize(sent_text, cfg):
    if len(sent_text) > MAX_CHARS_PER_REQUEST:
        raise RuntimeError(f"text is {len(sent_text)} characters; the per-request limit is {MAX_CHARS_PER_REQUEST}")
    url = (f"{API_BASE}/v1/text-to-speech/{urllib.parse.quote(cfg['voice_id'])}"
           f"?output_format={OUTPUT_FORMAT}")
    audio = _request("POST", url, cfg["api_key"], {
        "text": sent_text, "model_id": cfg["model_id"], "voice_settings": VOICE_SETTINGS}, accept="audio/mpeg")
    if not is_mp3(audio):
        raise RuntimeError("ElevenLabs returned something that is not MP3 audio")
    return audio


def _write_atomic(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


# --------------------------------------------------------------------------- commands
def plan(paths, cfg):
    """[(lesson_id, [(key, display, sent, cache_file, cached)])]"""
    out = []
    for p in paths:
        try:
            lesson, payload = lesson_payload(p)
        except Exception as e:  # noqa - a broken lesson must not stop the rest
            print(f"  skip {os.path.relpath(p, ACADEMY)}: {type(e).__name__}: {e}")
            continue
        rows = []
        lcfg = lesson_cfg(cfg, lesson["id"])
        for key, display in narration_items(payload):
            sent = tts_text(display)
            f = os.path.join(VOICE_DIR, cache_key(sent, lcfg["voice_id"], lcfg["model_id"]) + ".mp3")
            rows.append((key, display, sent, f, os.path.isfile(f) and os.path.getsize(f) > 0))
        out.append((lesson["id"], rows))
    return out


def cmd_estimate(a):
    cfg = load_config()
    paths = [find_lesson(a.lesson)] if a.lesson else all_lesson_paths()
    total_new = total_all = lines_new = 0
    print(f"voice {cfg['voice_id']}{' (default)' if cfg['voice_id'] == DEFAULT_VOICE else ''}, model {cfg['model_id']}, {OUTPUT_FORMAT}")
    print(f"{'lesson':<8} {'lines':>5} {'uncached':>8} {'billable chars':>15} {'all chars':>10}")
    for lid, rows in plan(paths, cfg):
        new = [r for r in rows if not r[4]]
        c_new = sum(len(r[2]) for r in new)
        c_all = sum(len(r[2]) for r in rows)
        total_new += c_new
        total_all += c_all
        lines_new += len(new)
        print(f"{lid:<8} {len(rows):>5} {len(new):>8} {c_new:>15,} {c_all:>10,}")
    print(f"{'TOTAL':<8} {'':>5} {lines_new:>8} {total_new:>15,} {total_all:>10,}")
    print(f"\nBillable now (uncached only): {total_new:,} characters. Cached lines cost nothing to rebuild.")
    return 0


def cmd_generate(a):
    if not (a.lesson or a.all):
        sys.exit("generate needs --lesson L1-01 or --all")
    cfg = load_config(require_key=True)
    paths = [find_lesson(a.lesson)] if a.lesson else all_lesson_paths()
    made = skipped = chars = 0
    try:
        for lid, rows in plan(paths, cfg):
            todo = [r for r in rows if not r[4]]
            skipped += len(rows) - len(todo)
            if not todo:
                print(f"{lid}: all {len(rows)} lines cached")
                continue
            print(f"{lid}: generating {len(todo)} of {len(rows)} lines")
            for key, _, sent, f, _ in todo:
                audio = synthesize(sent, lesson_cfg(cfg, lid))
                _write_atomic(f, audio)
                made += 1
                chars += len(sent)
                print(f"    {key:<10} {len(sent):>5} chars -> {os.path.basename(f)} ({len(audio) // 1024} KB)")
    except StopBilling as e:
        print(f"\nSTOPPED: {e}")
        print(f"Generated before stopping: {made} lines, {chars:,} characters.")
        return 2
    print(f"\nDone: {made} new lines ({chars:,} characters billed), {skipped} already cached.")
    print("Next: python3 build_scorm.py <lesson json> (or --all) to embed the voiceover.")
    return 0


def cmd_sample(a):
    cfg = load_config(require_key=True)
    sent = tts_text(a.text)
    out = a.out if os.path.isabs(a.out) else os.path.join(os.getcwd(), a.out)
    try:
        audio = synthesize(sent, cfg)
    except StopBilling as e:
        print(f"STOPPED: {e}")
        return 2
    _write_atomic(out, audio)
    print(f"{len(sent)} characters -> {out} ({len(audio) // 1024} KB), voice {cfg['voice_id']}")
    if sent != a.text:
        print(f"sent as: {sent}")
    return 0


def cmd_voices(a):
    cfg = load_config(require_key=True)
    voices, token = [], None
    try:
        while True:
            q = {"page_size": 100}
            if token:
                q["next_page_token"] = token
            if a.search:
                q["search"] = a.search
            d = json.loads(_request("GET", f"{API_BASE}/v2/voices?{urllib.parse.urlencode(q)}", cfg["api_key"]))
            voices += d.get("voices") or []
            token = d.get("next_page_token")
            if not d.get("has_more") or not token:
                break
    except StopBilling as e:
        print(f"STOPPED: {e}")
        return 2
    print(f"{len(voices)} voices (current: {cfg['voice_id']})\n")
    print(f"{'name':<28} {'voice_id':<24} {'category':<12} labels")
    for v in sorted(voices, key=lambda v: (v.get("category") or "", v.get("name") or "")):
        labels = ", ".join(f"{k}={val}" for k, val in sorted((v.get("labels") or {}).items()) if val)
        mark = " *" if v.get("voice_id") == cfg["voice_id"] else ""
        print(f"{(v.get('name') or '')[:27]:<28} {v.get('voice_id', ''):<24} {(v.get('category') or ''):<12} {labels}{mark}")
    print('\nPut the chosen voice_id in .elevenlabs.json, then try it: python3 voice.py sample --text "..." --out media/voice/sample.mp3')
    return 0


def main():
    ap = argparse.ArgumentParser(description="ElevenLabs voiceover for Valley Pawn Academy")
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("estimate", help="billable (uncached) characters per lesson")
    e.add_argument("--lesson", help="one lesson id, e.g. L1-01")
    s = sp.add_parser("sample", help="speak one line to a file (billed)")
    s.add_argument("--text", required=True)
    s.add_argument("--out", default=os.path.join(VOICE_DIR, "sample.mp3"))
    g = sp.add_parser("generate", help="generate and cache narration (billed for uncached lines only)")
    g.add_argument("--lesson", help="one lesson id, e.g. L1-01")
    g.add_argument("--all", action="store_true")
    v = sp.add_parser("voices", help="list voices on the account")
    v.add_argument("--search", help="filter by name/labels")
    a = ap.parse_args()
    return {"estimate": cmd_estimate, "sample": cmd_sample, "generate": cmd_generate, "voices": cmd_voices}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
