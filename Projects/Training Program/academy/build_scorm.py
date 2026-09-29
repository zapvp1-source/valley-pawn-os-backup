#!/usr/bin/env python3
"""
Valley Pawn Academy - SCORM 1.2 package builder.

Turns one lesson JSON (academy/lessons/L<level>/<nn>_<slug>.json, see LESSON_SPEC.md)
into a TalentLMS-ready SCORM 1.2 zip with a self-contained player.

Usage:
    python3 build_scorm.py lessons/L1/01_welcome.json      # one lesson
    python3 build_scorm.py --all                           # every lessons/*/*.json (L1-L8 and M)
    python3 build_scorm.py --all --skip-validate           # build without the checks
    python3 build_scorm.py --validate-only                 # re-check what's in dist/

Outputs (all under academy/dist/):
    <id>_<slug>.zip          SCORM 1.2 package (upload this to TalentLMS)
    preview/<id>/index.html  the same package unzipped, open in a browser to preview
    manifest_index.json      every package: file, title, level, question count, warnings

Never fails on missing media: a missing video falls back to narrated slides, a missing
call clip drops the Listen step. Call clips are transcoded to MP3 (needs ffmpeg/ffprobe).
Learner-visible text is cleaned of internal references at build time (see learner_text()).
Standard library only (plus `node` on PATH for the JS checks; skipped with a warning if absent).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone

ACADEMY = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ACADEMY, "lessons")
MEDIA_DIR = os.path.join(ACADEMY, "media")
DIST = os.path.join(ACADEMY, "dist")
PREVIEW = os.path.join(DIST, "preview")
INDEX_PATH = os.path.join(DIST, "manifest_index.json")

# Logo: academy/assets/tlms_logo.png (checked in next to the builder); brand folder as fallback.
LOGO_CANDIDATES = [
    os.path.join(ACADEMY, "assets", "tlms_logo.png"),
    os.path.join(os.path.dirname(ACADEMY), "..", "..", "outputs", "brand", "tlms_logo.png"),
    "/sessions/sleepy-awesome-knuth/mnt/outputs/brand/tlms_logo.png",
]

VALID_TYPES = {"scenario", "mc", "truefalse"}


# --------------------------------------------------------------------------- lint
def lint_lesson(lesson, path):
    """Return a list of human-readable warnings. Never raises for content problems."""
    w = []
    for key in ("id", "level", "title", "quiz"):
        if key not in lesson:
            w.append(f"missing required key '{key}'")
    if not isinstance(lesson.get("minutes"), (int, float)):
        w.append("'minutes' missing or not a number")
    v = lesson.get("video")
    if isinstance(v, dict) and v.get("file") and v.get("url"):
        w.append("video has both 'file' and 'url' (spec: exactly one); file wins")
    slides = lesson.get("slides") or []
    if not slides:
        w.append("no slides (needed as the fallback when there's no video)")
    for i, s in enumerate(slides, 1):
        if not s.get("heading"):
            w.append(f"slide {i}: no heading")
        if not s.get("say"):
            w.append(f"slide {i}: no 'say' narration")
    kp = lesson.get("key_points") or []
    if not (3 <= len(kp) <= 6):
        w.append(f"key_points has {len(kp)} items (spec: 3-6)")
    clip = lesson.get("call_clip")
    if isinstance(clip, dict):
        if not clip.get("listen_for"):
            w.append("call_clip has no listen_for checklist")
        if str(clip.get("caption", "")).strip().upper().startswith("TODO"):
            w.append("call_clip caption starts with 'TODO' (TODO text is hidden from learners)")
    quiz = lesson.get("quiz") or {}
    qs = quiz.get("questions") or []
    if not (6 <= len(qs) <= 8):
        w.append(f"quiz has {len(qs)} questions (spec: 6-8)")
    n_scen = sum(1 for q in qs if q.get("type") == "scenario")
    if n_scen < 4:
        w.append(f"only {n_scen} scenario questions (spec: at least 4)")
    for k, default in (("pass_percent", 80), ("max_attempts", 2), ("shuffle", True)):
        if k not in quiz:
            w.append(f"quiz.{k} missing (defaulting to {default})")
    for qi, q in enumerate(qs, 1):
        tag = f"Q{qi}"
        if q.get("type") not in VALID_TYPES:
            w.append(f"{tag}: type '{q.get('type')}' not one of scenario|mc|truefalse")
        if not q.get("prompt"):
            w.append(f"{tag}: empty prompt")
        opts = q.get("options") or []
        if len(opts) < 2:
            w.append(f"{tag}: fewer than 2 options")
        n_correct = sum(1 for o in opts if o.get("correct") is True)
        if n_correct == 0:
            w.append(f"{tag}: NO correct option - question is dropped from the package")
        elif n_correct > 1:
            w.append(f"{tag}: {n_correct} options marked correct (any of them scores as correct)")
        for oi, o in enumerate(opts, 1):
            if not str(o.get("text", "")).strip():
                w.append(f"{tag} option {oi}: empty text")
            if not str(o.get("why", "")).strip():
                w.append(f"{tag} option {oi}: missing 'why'")
            if "correct" not in o:
                w.append(f"{tag} option {oi}: no 'correct' flag (treated as false)")
        if q.get("type") == "truefalse" and len(opts) != 2:
            w.append(f"{tag}: truefalse with {len(opts)} options")
        texts = [str(o.get("text", "")).strip().lower() for o in opts]
        if len(set(texts)) != len(texts):
            w.append(f"{tag}: duplicate option text")
    return w


def usable_questions(lesson):
    return [q for q in (lesson.get("quiz") or {}).get("questions") or []
            if any(o.get("correct") is True for o in q.get("options") or [])]


# --------------------------------------------------------------------------- media
# Call clips ship as MP3 (TalentLMS's CDN would not stream the AAC/.m4a originals: the player sat
# at 0:00). Every clip is transcoded to mono 64 kbps 44.1 kHz MP3 with its metadata stripped and
# packaged under a neutral name, media/<lessonId>_call.mp3 (source names carry internal tags).
FFMPEG = shutil.which("ffmpeg") or ("/usr/bin/ffmpeg" if os.path.isfile("/usr/bin/ffmpeg") else None)
FFPROBE = shutil.which("ffprobe") or ("/usr/bin/ffprobe" if os.path.isfile("/usr/bin/ffprobe") else None)
AUDIO_CACHE = os.path.join(tempfile.gettempdir(), "vpa_audio_cache")
LONG_CLIP_SECONDS = 180


def media_duration(path):
    if FFPROBE:
        p = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                           capture_output=True, text=True)
        try:
            return float(p.stdout.strip())
        except ValueError:
            pass
    return None


def transcode_clip(src):
    """Returns (mp3_path, seconds) or (None, error_text). Cached by source path/size/mtime."""
    if not FFMPEG:
        return None, "ffmpeg not found"
    st = os.stat(src)
    key = hashlib.sha1(f"{os.path.abspath(src)}|{st.st_size}|{st.st_mtime_ns}|mp3-mono-64k-44100-v1".encode()).hexdigest()[:20]
    os.makedirs(AUDIO_CACHE, exist_ok=True)
    out = os.path.join(AUDIO_CACHE, key + ".mp3")
    if not os.path.isfile(out) or os.path.getsize(out) < 1024:
        tmp = out + ".part.mp3"
        p = subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-vn", "-map_metadata", "-1", "-ac", "1",
                            "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "64k", tmp],
                           capture_output=True, text=True)
        if p.returncode or not os.path.isfile(tmp):
            return None, "ffmpeg failed: " + (p.stderr.strip()[:300] or "unknown error")
        os.replace(tmp, out)
    return out, media_duration(out)


def resolve_media(lesson):
    """Returns (build_info, files_to_copy {pkg_path: src}, notes[])."""
    info = {"video": None, "video_kind": None, "clip": None, "clip_seconds": None, "clip_label": None,
            "clip_missing": False, "video_missing": False}
    copy, notes = {}, []
    lid = re.sub(r"[^A-Za-z0-9-]", "_", lesson["id"])
    v = lesson.get("video") or {}
    if isinstance(v, dict):
        vf, vu = v.get("file"), v.get("url")
        if vf:
            src = os.path.join(MEDIA_DIR, vf)
            if os.path.isfile(src):
                pkg = f"media/{lid}_video{os.path.splitext(vf)[1].lower()}"
                copy[pkg] = src
                info["video"], info["video_kind"] = pkg, "file"
            else:
                info["video_missing"] = True
                notes.append(f"video file not found: media/{vf} -> narrated slides used")
        elif vu:
            info["video"] = vu
            info["video_kind"] = "embed" if re.search(r"youtube\.com|youtu\.be|vimeo\.com", vu) else "url"
    clip = lesson.get("call_clip")
    if isinstance(clip, dict) and clip.get("file"):
        cf = clip["file"]
        cands = [os.path.join(MEDIA_DIR, cf), os.path.join(MEDIA_DIR, "clips", os.path.basename(cf))]
        src = next((c for c in cands if os.path.isfile(c)), None)
        if src:
            mp3, secs = transcode_clip(src)
            if mp3:
                pkg = f"media/{lid}_call.mp3"
                copy[pkg] = mp3
                info["clip"], info["clip_seconds"] = pkg, (round(secs, 1) if secs else None)
                info["clip_path"] = mp3
                if secs and secs > LONG_CLIP_SECONDS:
                    info["clip_label"] = f"{int(round(secs / 60))} min call"
            else:
                info["clip_missing"] = True
                notes.append(f"call clip could not be converted to MP3 ({secs}) -> Listen step skipped")
        else:
            info["clip_missing"] = True
            notes.append(f"call clip not found: media/{cf} -> Listen step skipped")
    return info, copy, notes


# --------------------------------------------------------------------------- manifest
def make_manifest(lesson, files):
    ident = re.sub(r"[^A-Za-z0-9_.-]", "_", f"VPA_{lesson['id']}")
    title = lesson.get("title", lesson["id"])
    mastery = int((lesson.get("quiz") or {}).get("pass_percent", 80))
    NS = "http://www.imsproject.org/xsd/imscp_rootv1p1p2"
    ADL = "http://www.adlnet.org/xsd/adlcp_rootv1p2"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    ET.register_namespace("", NS)
    ET.register_namespace("adlcp", ADL)
    ET.register_namespace("xsi", XSI)
    m = ET.Element(f"{{{NS}}}manifest", {
        "identifier": ident + "_MANIFEST", "version": "1.0",
        f"{{{XSI}}}schemaLocation": (
            "http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd "
            "http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd "
            "http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd"),
    })
    md = ET.SubElement(m, f"{{{NS}}}metadata")
    ET.SubElement(md, f"{{{NS}}}schema").text = "ADL SCORM"
    ET.SubElement(md, f"{{{NS}}}schemaversion").text = "1.2"
    orgs = ET.SubElement(m, f"{{{NS}}}organizations", {"default": "VPA_ORG"})
    org = ET.SubElement(orgs, f"{{{NS}}}organization", {"identifier": "VPA_ORG"})
    ET.SubElement(org, f"{{{NS}}}title").text = "Valley Pawn Academy"
    item = ET.SubElement(org, f"{{{NS}}}item", {"identifier": "ITEM_1", "identifierref": "RES_1", "isvisible": "true"})
    ET.SubElement(item, f"{{{NS}}}title").text = f"{lesson['id']} {title}"
    ET.SubElement(item, f"{{{ADL}}}masteryscore").text = str(mastery)
    res = ET.SubElement(ET.SubElement(m, f"{{{NS}}}resources"), f"{{{NS}}}resource", {
        "identifier": "RES_1", "type": "webcontent", f"{{{ADL}}}scormtype": "sco", "href": "index.html"})
    for f in files:
        ET.SubElement(res, f"{{{NS}}}file", {"href": f})
    ET.indent(m, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(m, encoding="unicode") + "\n"


# --------------------------------------------------------------------------- learner text
# Lesson JSONs carry citations for the people who build the course (Master Plan, KB ids, call
# numbers, POLICY_GAPS, OPEN items...). Learners must never see those. This runs at build time
# on every learner-visible string; the lesson JSONs themselves are left alone.
#  - Internal references are removed everywhere (whole parenthetical, or just that part of it).
#  - P&P / Handbook section numbers, HR/OB memo numbers and laws are kept inside the `why`
#    explanations (useful to staff) and dropped from parenthetical citations everywhere else.
#  - "Call 204"-style call numbers in running text become "a real call".
INTERNAL_ATOM = re.compile(
    r"Master\s*Plan|\bKB\b|POLICY_GAPS|\bOPEN\b|\bTODO\b|[Pp]roduction|\b[Cc]all\s?\d{2,3}\b|"
    r"TRAINING_PROGRAM|\.md\b|SKILL|_Audit\b|CONDUCT_REVIEW|FINDINGS|\b[A-Za-z]+_\w+\b|"
    r"^\s*[a-z0-9]+(?:-[a-z0-9]+){2,}\s*$|\bsee sources\b|\brun records\b|^\s*library:|build brief|\bqueue #\d|Hard Rule \d|\bSTATUS\b|\bcorrected in\b|"
    r"\b[a-z0-9]+(?:-[a-z0-9]+)+-[0-9a-f]{8}\b|^\s*[0-9a-f]{8}(?:\s*,\s*[0-9a-f]{8})*\s*$|\bv\d\b")
MEMO_ATOM = re.compile(r"\b(?:HR|OB)-\d{4}-\d{2}\b")
POLICY_ATOM = re.compile(r"§|P&P|Handbook|Va\. Code|U\.S\.C\.|\bCFR\b|Google UGC policy|^\s*L\d-\d\d\s*$")
CALL_REWRITES = [
    (re.compile(r"^Call \d{2,3}[.:]\s+"), "From a real call: "),
    (re.compile(r"\bThis is (?:the )?Call \d{2,3}(?: problem| trap| mistake)?\b"), "This happened on a real call"),
    (re.compile(r"\bthe Call \d{2,3} exemplar"), "the model call"),
    (re.compile(r"\bthe Call \d{2,3} (\w+)"), r"the real-call \1"),
    (re.compile(r"\bCall \d{2,3}'s seller"), "a real seller"),
    (re.compile(r"\bCall \d{2,3} at (\w+)"), r"the \1 call"),
    (re.compile(r"\bCall \d{2,3} [A-Z]{3}\b"), "On a real call"),
    (re.compile(r"\bIn Call \d{2,3}\b"), "On a real call"),
    (re.compile(r"\bin Call \d{2,3}\b"), "on a real call"),
    (re.compile(r"\bCall \d{2,3}'s\b"), "a real call's"),
    (re.compile(r"\b[Cc]all ?(?!911\b)\d{2,3}\b"), "a real call"),
]
# whole sentences that only make sense to the people building the course
DROP_SENTENCE = re.compile(r"[^.!?]*\b(?:OPEN|TODO|see sources)\b[^.!?]*[.!?]?")

# The validator greps every built index.html for these. Zero hits is required.
FORBIDDEN_PATTERNS = [
    ("Master Plan", re.compile(r"Master\s*Plan", re.I)),
    ("KB", re.compile(r"\bKB\b")),
    ("KB id", re.compile(r"\b[a-z0-9]+(?:-[a-z0-9]+)+-[0-9a-f]{8}\b")),
    ("POLICY_GAPS", re.compile(r"POLICY_GAPS")),
    ("OPEN", re.compile(r"\bOPEN\b")),
    ("TODO", re.compile(r"\bTODO\b")),
    ("production", re.compile(r"production", re.I)),
    ("Call NNN", re.compile(r"\b[Cc]all\s?(?!911\b)\d{2,3}\b")),
    ("v1/v2 numbering", re.compile(r"\bv\d\b|\bv\d{4}\.\d")),
    ("slug ref", re.compile(r"\([a-z0-9]+(?:-[a-z0-9]+){2,}\)")),
    ("internal doc", re.compile(r"TRAINING_PROGRAM|SKILL\.md|eBay_Channel_Audit|CONDUCT_REVIEW|FINDINGS_|"
                                r"BEST_CALLS|coaching_pack|\brun records\b|\(library:|see sources|production_notes|"
                                r"queue #\d|Hard Rule \d|\bSTATUS\b|corrected in\)")),
    ("coming soon", re.compile(r"coming soon", re.I)),
    ("sources key", re.compile(r"\bsources\b")),
]


def _paren_groups(s):
    out, depth, st = [], 0, None
    for i, ch in enumerate(s):
        if ch == "(":
            if depth == 0:
                st = i
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
            if depth == 0:
                out.append((st, i + 1))
    return out


def _paren_atoms(inner):
    parts, depth, cur = [], 0, ""
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _is_ref(a):
    return bool(INTERNAL_ATOM.search(a) or MEMO_ATOM.search(a) or POLICY_ATOM.search(a))


def _clean_atom(a, keep_policy):
    if INTERNAL_ATOM.search(a):
        sub = [x.strip() for x in a.split(",")]
        sub = [x for x in sub if x and not INTERNAL_ATOM.search(x)]
        if keep_policy and sub and all(POLICY_ATOM.search(x) or MEMO_ATOM.search(x) for x in sub):
            return ", ".join(sub)
        return None
    if not _is_ref(a):
        return a
    return a if keep_policy else None


def learner_text(s, keep_policy=False):
    """Strip internal references from one learner-visible string (see the block comment above)."""
    if not isinstance(s, str) or not s:
        return s
    for st, en in reversed(_paren_groups(s)):
        atoms = _paren_atoms(s[st + 1:en - 1])
        if not atoms or not any(_is_ref(a) for a in atoms):
            continue  # an ordinary parenthetical: "(1)", "(CEO)", "(dwt ÷ 20)"
        had_internal = any(INTERNAL_ATOM.search(a) for a in atoms)
        keep = [k for k in (_clean_atom(a, keep_policy) for a in atoms) if k]
        if had_internal:
            keep = [k for k in keep if _is_ref(k)]
        keep = [re.sub(r"\s*v\d{4}(?:\.\d+)?\b", "", k).strip() for k in keep]
        if keep:
            s = s[:st] + "(" + "; ".join(keep) + ")" + s[en:]
        else:
            s = s[:st].rstrip(" ") + s[en:]
    for rx, rep in CALL_REWRITES:
        s = rx.sub(rep, s)
    s = DROP_SENTENCE.sub("", s)
    s = re.sub(r"\s*v\d{4}\.\d+\b", "", s)            # "P&P v2026.8 §01.10" -> "P&P §01.10"
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    s = re.sub(r"([!?])(['’\"”])\.", r"\1\2", s)
    return s.strip()


def forbidden_hits(text):
    return [(name, m.group(0)) for name, rx in FORBIDDEN_PATTERNS for m in rx.finditer(text)]


# --------------------------------------------------------------------------- icons
# Simple line icons (24x24, stroke). Main strokes take the icon colour; parts drawn with the
# accent style take --acc (coral or blue). No firearm imagery anywhere, by design.
ACC = ' style="stroke:var(--acc)"'
ICONS = {
    "phone": '<path d="M5 3.5h3.5l2 5-2.6 1.6a11.5 11.5 0 0 0 6 6l1.6-2.6 5 2V19a2 2 0 0 1-2 2A17 17 0 0 1 3 5.5a2 2 0 0 1 2-2z"/><path' + ACC + ' d="M15 3.5a5.5 5.5 0 0 1 5.5 5.5M15 7a2 2 0 0 1 2 2"/>',
    "chat": '<path d="M4 4.5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H10l-5 4v-4H4a1 1 0 0 1-1-1v-10a1 1 0 0 1 1-1z"/><path' + ACC + ' d="M7.5 9h9M7.5 12.5h6"/>',
    "shield": '<path d="M12 2.5l8 3v6.2c0 4.9-3.4 8.6-8 9.8-4.6-1.2-8-4.9-8-9.8V5.5z"/><path' + ACC + ' d="M8.3 12l2.6 2.6 4.8-5"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><path' + ACC + ' d="M12 14.5v3"/>',
    "cash": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle' + ACC + ' cx="12" cy="12" r="2.8"/><path d="M6 9.5v.01M18 14.5v.01"/>',
    "register": '<path d="M6 11.5V4.5h12v7"/><rect x="3" y="11.5" width="18" height="8.5" rx="1.5"/><path' + ACC + ' d="M9 8h6"/><path d="M9.5 16h5"/>',
    "safe": '<rect x="3" y="3.5" width="18" height="16" rx="2"/><circle' + ACC + ' cx="12" cy="11.5" r="3.6"/><path d="M12 7.9v1M12 14.1v1M15.6 11.5h-1M9.4 11.5h-1M6.5 19.5v1.5M17.5 19.5v1.5"/>',
    "gold": '<path d="M1.5 20.5l1.6-5h6.8l1.6 5zM12.5 20.5l1.6-5h6.8l1.6 5z"/><path' + ACC + ' d="M7 13.5l1.6-5h6.8l1.6 5z"/><path d="M11 5.5l.6-1.8M14.5 5.8l1.2-1.4M8 6l-1-1.4"/>',
    "diamond": '<path d="M6.5 4h11l4 5.5L12 21 2.5 9.5z"/><path' + ACC + ' d="M2.5 9.5h19M9.5 4L8 9.5 12 21l4-11.5L14.5 4"/>',
    "clipboard": '<rect x="4.5" y="4" width="15" height="17.5" rx="2"/><rect x="8.5" y="2.5" width="7" height="3.5" rx="1"/><path' + ACC + ' d="M8 11.5l1.7 1.7 3.3-3.4M8 16.5h8"/>',
    "store": '<path d="M4.5 10v10.5h15V10"/><path d="M2.5 10L5 3.5h14l2.5 6.5z"/><path' + ACC + ' d="M10 20.5V15h4v5.5"/>',
    "handshake": '<path' + ACC + ' d="M11 17l2 2a1 1 0 1 0 3-3"/><path' + ACC + ' d="M14 14l2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="M21 3l1 11h-2M3 3L2 14l6.5 6.5a1 1 0 1 0 3-3M3 4h8"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path' + ACC + ' d="M12 7v5.2l3.3 2"/>',
    "warning": '<path d="M12 3.2L1.8 20.5h20.4z"/><path' + ACC + ' d="M12 9.5v5M12 17.4v.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path' + ACC + ' d="M7.8 12.4l2.8 2.8 5.6-5.8"/>',
    "box": '<path d="M3 7.5l9-4 9 4v9.5l-9 4-9-4z"/><path d="M3 7.5l9 4 9-4M12 11.5v9.5"/><path' + ACC + ' d="M7.5 5.5l9 4v3"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M10.7 12.3L20 3M16.5 6.5l3 3M14 9l2 2"/><circle' + ACC + ' cx="7.5" cy="15.5" r="1.4"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path' + ACC + ' d="M15.3 15.3L21 21"/><path d="M8 8.2a3.3 3.3 0 0 1 2.5-1.1"/>',
    "star": '<path d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2l-5.7 3.1 1.2-6.4-4.7-4.4 6.4-.8z"/><path' + ACC + ' d="M12 7.5v.01"/>',
    "scale": '<path d="M12 3.5v17M7.5 20.5h9M4.5 6.5h15"/><path' + ACC + ' d="M4.5 6.5l-3 6.5a3 3 0 0 0 6 0zM19.5 6.5l-3 6.5a3 3 0 0 0 6 0z"/>',
    "idcard": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><circle' + ACC + ' cx="8.5" cy="10.5" r="2.2"/><path' + ACC + ' d="M5.2 16c.6-1.7 1.8-2.6 3.3-2.6s2.7.9 3.3 2.6"/><path d="M14.5 10h4M14.5 13.5h4"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path' + ACC + ' d="M7.5 14h2M11 14h2M14.5 14h2M7.5 17.5h2M11 17.5h2"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20.5c.7-3.7 3.2-5.7 6.5-5.7s5.8 2 6.5 5.7"/><circle' + ACC + ' cx="17" cy="9" r="2.6"/><path' + ACC + ' d="M17.3 14.4c2.3.1 3.8 1.6 4.3 4.3"/>',
    "laptop": '<rect x="4" y="4.5" width="16" height="11.5" rx="1.5"/><path d="M2 19.5h20"/><path' + ACC + ' d="M8 8.5h8M8 12h5"/>',
    "tag": '<path d="M3 3.5h8.3l9.7 9.7-7.8 7.8L3.5 11.3z"/><circle' + ACC + ' cx="7.8" cy="8.3" r="1.7"/>',
    "book": '<path d="M4 19V5a2 2 0 0 1 2-2h13.5v14H6a2 2 0 0 0-2 2 2 2 0 0 0 2 2h13.5"/><path' + ACC + ' d="M8.5 7.5h7M8.5 11h5"/>',
    "heart": '<path d="M12 20.3S3.8 15.6 2.8 10.2C2.1 6.6 4.4 4 7.3 4c2 0 3.6 1.1 4.7 2.8C13.1 5.1 14.7 4 16.7 4c2.9 0 5.2 2.6 4.5 6.2-1 5.4-9.2 10.1-9.2 10.1z"/><path' + ACC + ' d="M6.5 9.2a2.3 2.3 0 0 1 2-1.9"/>',
    "car": '<path d="M3 16.5v-4.5l2.2-5.5h13.6L21 12v4.5z"/><path d="M3 12h18"/><circle' + ACC + ' cx="7.5" cy="16.8" r="1.9"/><circle' + ACC + ' cx="16.5" cy="16.8" r="1.9"/>',
    "watch": '<circle cx="12" cy="12" r="6"/><path d="M8.8 7.3L9.5 2.5h5l.7 4.8M8.8 16.7l.7 4.8h5l.7-4.8"/><path' + ACC + ' d="M12 9v3l2 1.5"/>',
    "headphones": '<path d="M3.5 15.5V12a8.5 8.5 0 0 1 17 0v3.5"/><rect x="2.5" y="14" width="5" height="7" rx="1.6"/><rect x="16.5" y="14" width="5" height="7" rx="1.6"/><path' + ACC + ' d="M10 13.5v4M12 12v7M14 13.5v4"/>',
    # UI glyphs
    "speaker": '<path d="M3.5 9h4l5-4v14l-5-4h-4z"/><path' + ACC + ' d="M16 8.5a5 5 0 0 1 0 7M18.8 5.8a9 9 0 0 1 0 12.4"/>',
    "mute": '<path d="M3.5 9h4l5-4v14l-5-4h-4z"/><path' + ACC + ' d="M16.5 9.5l5 5M21.5 9.5l-5 5"/>',
    "x": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    "tick": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
}

# First match in the heading wins; otherwise the icon with the most keyword hits in the bullets.
ICON_RULES = [
    ("car", r"\btitle pawn|vehicle|\bcars?\b|odometer|\bvin\b|read the title"),
    ("watch", r"\bwatches\b|smartwatch|rolex|\bwatch (brand|band|face)"),
    ("diamond", r"diamond|\bstones?\b|\bgem|carat|jewel"),
    ("gold", r"\bgold\b|silver|\bmetal|melt|\bspot\b|bullion|\bcoins?\b|\bbars?\b|scrap|karat|\bkee\b|sigma|magnet|platinum"),
    ("box", r"ebay|\bship|label|\bpack(ed|ing)?\b|the box arrives|transfer arrives"),
    ("chat", r"\btext(s|ing)?\b|message|slack|chekkit|\bsms\b|stop means stop|#ask|inbox"),
    ("phone", r"phone|\bcalls?\b|caller|voicemail|recorded|\bring(s)?\b(?! size)|\bdial"),
    ("people", r"harass|\beeo\b|accommodation|huddle|\bteam\b|coach|coworker|\bwho (you|may)|family|friends|hire|day 1|onboard|each other"),
    ("shield", r"firearm|\bguns?\b|\bffl\b|\batf\b|4473|nics|state police|denied|delayed|approved|safety|protect|rights|straw|prohibited|police|officer|law\b|legal"),
    ("idcard", r"\bid\b|identification|identity|license|pledgor|verify|verification|qualif"),
    ("lock", r"password|login|\block(ed)?\b|secure|security|privacy|private|disclose|shred|data\b|device"),
    ("safe", r"\bsafe\b|vault"),
    ("register", r"drawer|register|\btill\b|balanc|over or short|\bcount(s|ing|ed)?\b|start of day|end of day"),
    ("cash", r"\bcash\b|money|payment|\bpay\b|\bfees?\b|charge|principal|finance|\$\d|8300|redemption|redeem|extension|refinanc|loan"),
    ("tag", r"\bpric|markdown|clearance|\baged\b|discount|margin|\bsale\b|\blist\b|pull list"),
    ("scale", r"\bweigh|\bgrade|percentage|formula|\bmath\b|dwt|gram"),
    ("search", r"research|\bcomps?\b|\btest(ed|ing)?\b|inspect|\bfakes?\b|counterfeit|tells|\bcheck(ed)?\b|red flag|stolen|suspect|find it|read the"),
    ("clipboard", r"\bform\b|checklist|worksheet|ticket|paperwork|record|\bbook\b|report|statement|\bsign(ed|ing)?\b|contract|floor check|documented"),
    ("clock", r"\btime\b|clock|\bhour|deadline|minute|9:30|overnight|timeline|\blate\b|o'clock|same-hour|by noon"),
    ("calendar", r"\bdays?\b|\bweek|monthly|daily|annual|due date|15th|every day|twice a day|schedule"),
    ("warning", r"\bnever\b|\bstop\b|\bdon't\b|\bwrong\b|mistake|missing|trap|\bno\b|won't|can't"),
    ("handshake", r"customer|\bdeal\b|negotiat|\boffer|\bbuys?\b|\bsell|pitch|layaway|objection|pay (the )?most"),
    ("heart", r"\bvent\b|apolog|indifference|\bcare\b|promise|recovery|owning"),
    ("store", r"\bstores?\b|\bopen\b|\bclos(e|ing)\b|doors|lights|first impression|\bfloor\b"),
    ("laptop", r"computer|\bemail|system|bravo|online|website|zoom"),
    ("star", r"review|google|loyal|remember|certified|credential|academy|backbone|standard"),
    ("book", r"handbook|p&p|manual|\bpolicy|\brules?\b|learn|lesson|documents?"),
    ("key", r"\bkeys?\b|access"),
    ("check", r"\bpass\b|done|complete|every time|right"),
]
_ICON_RX = [(name, re.compile(rx, re.I)) for name, rx in ICON_RULES]
DEFAULT_ICON = "star"


def pick_icon(heading, bullets, avoid=None):
    """Keyword mapper: heading match first (rule order = priority), then the most hits in bullets."""
    heading = heading or ""
    body = " ".join(bullets or [])
    cands = [name for name, rx in _ICON_RX if rx.search(heading)]
    if not cands:
        scored = sorted(((len(rx.findall(body)), -i, name) for i, (name, rx) in enumerate(_ICON_RX)), reverse=True)
        cands = [n for c, _, n in scored if c > 0]
    for c in cands:
        if c != avoid:
            return c
    return cands[0] if cands else DEFAULT_ICON


def icon_sprite():
    syms = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">{syms}</svg>'


# --------------------------------------------------------------------------- player
PLAYER_CSS = r"""
.cplayer{display:flex;align-items:center;gap:14px;background:#f3f0f8;border:1px solid #e2dcee;border-radius:14px;padding:12px 16px;margin:14px 0}
.cpbtn{flex:none;width:52px;height:52px;border-radius:50%;border:0;background:#4B2F74;color:#fff;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.cpbtn:disabled{opacity:.45;cursor:default}
.cpbar{flex:1;height:10px;background:#dcd4ea;border-radius:6px;cursor:pointer;position:relative;overflow:hidden}
.cpfill{height:100%;width:0;background:#508DCE;border-radius:6px}
.cptime{flex:none;font-variant-numeric:tabular-nums;color:#4B2F74;font-weight:600;min-width:92px;text-align:right}
:root{--purple:#4B2F74;--purple2:#6a4a9c;--blue:#508DCE;--coral:#DB7971;--white:#fff;--ink:#231733;--muted:#62587a;--bg:#f4f1f8;--line:#e3ddee;--ok:#23845a;--okbg:#e7f6ee;--bad:#b8423a;--badbg:#fcecea;--acc:#DB7971;--shadow:0 2px 14px rgba(75,47,116,.09)}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
html,body{margin:0;padding:0;height:auto;min-height:100%}
/* only the root scrolls: an overflow on body would break the sticky button bar */
html{overflow-x:hidden;overflow-y:auto}
body{background:var(--bg);color:var(--ink);font:20px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
button{font:inherit}
.top{background:var(--white);border-bottom:3px solid var(--purple);padding:8px 16px;display:flex;align-items:center;gap:12px;justify-content:space-between}
.top img{height:30px;width:auto;max-width:55%}
.top .lid{font-size:14px;color:var(--muted);font-weight:600;white-space:nowrap}
.progress{background:var(--white);padding:8px 16px 10px;border-bottom:1px solid var(--line)}
.progress .in{max-width:960px;margin:0 auto}
.bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden}
.bar>i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--purple),var(--blue));transition:width .45s ease}
.steps{display:flex;gap:6px;margin-top:7px;font-size:13px;color:var(--muted);align-items:center}
.steps span{flex:1;text-align:center;white-space:nowrap;padding:2px 6px;border-radius:999px;transition:background .3s,color .3s}
.steps span.on{color:var(--white);background:var(--purple);font-weight:700}
.steps span.done{color:var(--purple);font-weight:600}
main{max-width:960px;margin:0 auto;padding:16px 16px 0}
.card{background:var(--white);border-radius:16px;box-shadow:var(--shadow);padding:28px 32px;margin-bottom:14px}
h1{color:var(--purple);font-size:32px;line-height:1.2;margin:4px 0 12px}
h2{color:var(--purple);font-size:28px;line-height:1.25;margin:0 0 14px}
h2:focus{outline:none}
.kicker{color:var(--blue);font-weight:700;text-transform:uppercase;letter-spacing:.06em;font-size:14px}
.meta{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.pill{display:inline-flex;align-items:center;gap:6px;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:5px 14px;font-size:16px;font-weight:600;color:var(--ink)}
.pill .ic{width:18px;height:18px;stroke-width:2}
.note{border-left:5px solid var(--coral);background:#fdf3f2;padding:14px 16px;border-radius:10px;margin:16px 0}
.note.blue{border-color:var(--blue);background:#eef4fb}
.note.purple{border-color:var(--purple);background:#f1ecf7}
.small{font-size:16px;color:var(--muted)}
.ic{fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;display:block;overflow:visible}
/* title */
.hero{display:grid;grid-template-columns:132px 1fr;gap:28px;align-items:start}
.iconwrap{width:132px;height:132px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 30% 25%,#fff 0,#f1ecf7 55%,#e6ddf1 100%);color:var(--purple);box-shadow:inset 0 0 0 2px #e3d8f0}
.iconwrap .ic{width:62%;height:62%}
.iconwrap.b{--acc:var(--blue);background:radial-gradient(circle at 30% 25%,#fff 0,#eaf2fb 55%,#d9e8f7 100%);box-shadow:inset 0 0 0 2px #cfe0f3}
.hero .iconwrap{animation:pop .5s ease both}
.ttsrow{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:6px}
/* slides */
.slidetop{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px}
.slidecount{color:var(--muted);font-size:15px;font-weight:600}
.tts{display:inline-flex;align-items:center;gap:8px;background:var(--white);color:var(--blue);border:2px solid var(--blue);border-radius:999px;padding:7px 16px;min-height:44px;font-size:16px;font-weight:700;cursor:pointer}
.tts .ic{width:22px;height:22px;stroke-width:2;--acc:currentColor}
.tts.on{background:var(--blue);color:var(--white)}
/* voiceover: "speaking" bars while the narration plays, then a gentle nudge on the Next button */
.vo-ind{display:none;align-items:center;gap:8px;color:var(--blue);font-size:14px;font-weight:700}
.vo-ind.on{display:inline-flex}
.vo-ind .eq{display:inline-flex;align-items:flex-end;gap:3px;height:18px}
.vo-ind .eq i{display:block;width:4px;height:100%;border-radius:2px;background:var(--blue);transform-origin:bottom;animation:eq 1s ease-in-out infinite}
.vo-ind .eq i:nth-child(2){animation-delay:.2s}.vo-ind .eq i:nth-child(3){animation-delay:.4s}.vo-ind .eq i:nth-child(4){animation-delay:.1s}
.slidetop .grp{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.btn.nudge{animation:nudge 1.6s ease-in-out 3}
@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}
@keyframes nudge{0%,100%{box-shadow:0 3px 10px rgba(75,47,116,.25);transform:scale(1)}50%{box-shadow:0 0 0 7px rgba(80,141,206,.35),0 3px 10px rgba(75,47,116,.25);transform:scale(1.04)}}
.slidebody{display:grid;grid-template-columns:150px 1fr;gap:32px;align-items:start;min-height:250px}
.slidebody .iconwrap{width:150px;height:150px}
ul.pts{padding-left:24px;margin:6px 0 0}
ul.pts li{margin:10px 0;font-size:20px}
ul.pts li::marker{color:var(--coral)}
.dots{display:flex;justify-content:center;gap:8px;margin-top:22px;flex-wrap:wrap}
.dots i{width:10px;height:10px;border-radius:50%;background:var(--line);transition:all .3s}
.dots i.seen{background:#b9a8d3}
.dots i.on{background:var(--purple);width:28px;border-radius:6px}
/* navigation: sticks to the bottom of the frame so the main button is always reachable */
.navbar{position:-webkit-sticky;position:sticky;bottom:0;z-index:20;margin:0 -16px;padding:10px 16px calc(12px + env(safe-area-inset-bottom,0px));background:linear-gradient(to bottom,rgba(244,241,248,0),rgba(244,241,248,.94) 18%,var(--bg) 40%)}
.navin{display:flex;align-items:center;gap:12px}
.navin .sp{flex:1}
.hint{flex:1;text-align:center;font-size:15px;color:var(--muted)}
.btn{font-weight:700;border:0;border-radius:12px;padding:14px 26px;cursor:pointer;min-height:54px;min-width:140px;background:var(--purple);color:var(--white);font-size:19px;box-shadow:0 3px 10px rgba(75,47,116,.25);transition:transform .12s,background .2s,opacity .2s}
.btn:hover:not(:disabled){background:var(--purple2)}
.btn:active:not(:disabled){transform:translateY(1px)}
.btn.sec{background:var(--white);color:var(--purple);border:2px solid var(--purple);box-shadow:none}
.btn:disabled{opacity:.4;cursor:not-allowed;box-shadow:none}
.btn:focus-visible,.tts:focus-visible,.opt:focus-visible,.check:focus-within{outline:3px solid var(--coral);outline-offset:2px}
/* listen */
.lhead{display:flex;align-items:center;gap:16px;margin-bottom:10px}
.lhead .iconwrap{width:64px;height:64px;flex:none}
.lhead h2{margin:0}
.caption{margin:8px 0 14px}
.caption p{margin:0 0 8px}
audio{width:100%;display:block;margin:6px 0 4px}
video{width:100%;border-radius:12px;background:#000;display:block}
.embed{position:relative;padding-top:56.25%}.embed iframe{position:absolute;inset:0;width:100%;height:100%;border:0;border-radius:12px}
.lf{margin-top:18px;font-weight:700}
.check{display:flex;gap:14px;align-items:center;padding:14px 16px;border:2px solid var(--line);border-radius:12px;margin:10px 0;cursor:pointer;transition:border-color .2s,background .2s}
.check input{width:26px;height:26px;margin:0;accent-color:var(--purple);flex:none}
.check.on{border-color:var(--ok);background:var(--okbg)}
/* key points */
.kps{display:grid;gap:12px}
.kp{display:flex;gap:14px;align-items:flex-start;background:#faf8fd;border:1px solid var(--line);border-radius:14px;padding:14px 18px;animation:rise .45s ease both}
.kp .tk{flex:none;width:34px;height:34px;border-radius:50%;background:var(--ok);color:#fff;display:flex;align-items:center;justify-content:center;margin-top:1px}
.kp .tk .ic{width:20px;height:20px;stroke-width:3}
/* test */
.qhead{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.qnum{font-weight:800;color:var(--purple);font-size:17px}
.tally{display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:16px;color:var(--ok);background:var(--okbg);border-radius:999px;padding:4px 12px}
.tally .ic{width:18px;height:18px;stroke-width:2;--acc:currentColor}
.segs{display:flex;gap:4px;margin:10px 0 14px}
.segs i{flex:1;height:6px;border-radius:4px;background:var(--line)}
.segs i.cur{background:#b9a8d3}.segs i.r{background:var(--ok)}.segs i.w{background:var(--coral)}
.qtype{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:700;margin-bottom:6px}
.prompt{font-size:24px;line-height:1.35;color:var(--ink);margin:0 0 12px}
.opt{display:flex;align-items:center;gap:14px;width:100%;text-align:left;background:var(--white);color:var(--ink);border:2px solid var(--line);border-radius:14px;padding:14px 16px;margin:10px 0;font-weight:500;font-size:19px;min-height:62px;cursor:pointer;transition:border-color .15s,background .15s,transform .15s,opacity .2s}
.opt .lt{flex:none;width:36px;height:36px;border-radius:50%;background:var(--bg);color:var(--purple);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:16px}
.opt .lt .ic{width:20px;height:20px;stroke-width:3}
.opt:hover:not(:disabled){border-color:var(--blue);background:#f7fafe}
.opt:disabled{cursor:default}
.opt.dim{opacity:.55}
.opt.right{border-color:var(--ok);background:var(--okbg);opacity:1}
.opt.right .lt{background:var(--ok);color:#fff}
.opt.wrong{border-color:var(--bad);background:var(--badbg);opacity:1;animation:shake .35s}
.opt.wrong .lt{background:var(--bad);color:#fff}
.opt.picked.right{animation:pulse .5s}
.fb{border-radius:12px;padding:14px 16px;margin-top:14px;animation:rise .3s ease both}
.fb.ok{background:var(--okbg);border:1px solid var(--ok)}
.fb.no{background:var(--badbg);border:1px solid var(--bad)}
.fb .h{display:block;font-weight:800;margin-bottom:4px;font-size:20px}
.fb.ok .h{color:var(--ok)}.fb.no .h{color:var(--bad)}
.fb p{margin:6px 0}
/* result */
.result{text-align:center}
.ring{width:170px;height:170px;margin:6px auto 4px;position:relative}
.ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:12}
.ring .trk{stroke:var(--line)}
.ring .val{stroke:var(--ok);stroke-linecap:round;transition:stroke-dashoffset 1.2s cubic-bezier(.2,.8,.2,1)}
.ring.fail .val{stroke:var(--coral)}
.ring b{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:44px;font-weight:800;color:var(--ok)}
.ring.fail b{color:var(--coral)}
.points{display:inline-flex;align-items:center;gap:10px;background:#fff7e3;border:1px solid #f1d58a;color:#6b4e00;border-radius:999px;padding:8px 18px;font-weight:700;margin:6px 0 4px;animation:pop .6s .5s ease both}
.points .ic{width:24px;height:24px;color:#d49a00;--acc:#d49a00}
.missed{border-top:1px solid var(--line);padding-top:14px;margin-top:14px;text-align:left}
.missed .q{font-weight:700;margin:0 0 8px}
.confetti{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:50}
.confetti i{position:absolute;top:-20px;width:10px;height:16px;border-radius:2px;opacity:.95;animation:fall linear forwards}
/* motion */
.in-fwd{animation:inR .35s ease both}.in-back{animation:inL .35s ease both}
@keyframes inR{from{opacity:0;transform:translateX(28px)}to{opacity:1;transform:none}}
@keyframes inL{from{opacity:0;transform:translateX(-28px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.7)}70%{transform:scale(1.06)}100%{opacity:1;transform:scale(1)}}
@keyframes pulse{0%{transform:scale(1)}40%{transform:scale(1.02)}100%{transform:scale(1)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
@keyframes fall{0%{transform:translateY(-20px) rotate(0)}100%{transform:translateY(110vh) rotate(720deg)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.confetti{display:none}}
@media (max-width:760px){.slidebody{grid-template-columns:110px 1fr;gap:20px}.slidebody .iconwrap{width:110px;height:110px}.hero{grid-template-columns:96px 1fr;gap:18px}.hero .iconwrap{width:96px;height:96px}}
@media (max-width:560px){
 body{font-size:18px}
 main{padding:12px 12px 0}
 .navbar{margin:0 -12px;padding-left:12px;padding-right:12px}
 .card{padding:20px 18px;border-radius:14px}
 h1{font-size:26px}h2{font-size:23px}
 .hero,.slidebody{display:block;min-height:0}
 .hero .iconwrap,.slidebody .iconwrap{width:84px;height:84px;margin:0 0 14px}
 ul.pts{padding-left:20px}ul.pts li{font-size:18px;margin:8px 0}
 .prompt{font-size:20px}.opt{font-size:17px;padding:12px 14px;min-height:58px}
 .btn{min-width:0;flex:1;padding:14px 16px;font-size:18px}
 .navin .sp,.hint{display:none}
 .steps span:not(.on){font-size:0;flex:0 0 9px;width:9px;height:9px;padding:0;border-radius:50%;background:var(--line)}
 .steps span.done{background:#b9a8d3}
 .steps span.on{flex:1}
 .ring{width:140px;height:140px}.ring b{font-size:36px}
 .tts{padding:6px 12px;font-size:15px}
 .kp{padding:12px 14px;gap:12px}.kp .tk{width:30px;height:30px}
}
"""

PLAYER_JS = r"""
(function (root) {
  'use strict';

  // ------------------------------------------------------------ helpers
  function shuffleArr(a, rng) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(rng() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function log() { try { if (root.console) root.console.log.apply(root.console, ['[VPA]'].concat([].slice.call(arguments))); } catch (e) {} }

  // ------------------------------------------------------------ SCORM 1.2
  function findAPI(win) {
    var tries = 0;
    try {
      while (win && win.API == null && win.parent != null && win.parent !== win && tries < 10) { tries++; win = win.parent; }
      return (win && win.API) ? win.API : null;
    } catch (e) { return null; }
  }
  function getAPI(w) {
    var api = findAPI(w);
    try { if (!api && w.opener) api = findAPI(w.opener); } catch (e) {}
    try { if (!api && w.top && w.top.opener) api = findAPI(w.top.opener); } catch (e) {}
    return api;
  }
  function pad(n, l) { n = String(n); while (n.length < l) n = '0' + n; return n; }
  function scormTime(ms) {
    var s = Math.max(0, ms) / 1000, h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    return pad(Math.min(h, 9999), 4) + ':' + pad(m, 2) + ':' + pad(sec.toFixed(2), 5);
  }

  function Scorm(win) {
    this.win = win; this.api = null; this.active = false; this.finished = false; this.start = Date.now();
  }
  Scorm.prototype.init = function () {
    this.api = getAPI(this.win);
    if (!this.api) { log('No LMS API found - standalone preview mode (nothing is recorded).'); return false; }
    var ok = String(this.api.LMSInitialize('')) === 'true';
    this.active = ok;
    log('LMSInitialize', ok);
    if (ok) {
      var st = this.get('cmi.core.lesson_status');
      if (st !== 'passed' && st !== 'completed') this.set('cmi.core.lesson_status', 'incomplete');
      this.set('cmi.core.exit', 'suspend');
      this.commit();
    }
    return ok;
  };
  Scorm.prototype.get = function (k) {
    if (!this.active) { log('get', k, '(standalone)'); return ''; }
    var v = this.api.LMSGetValue(k); return v == null ? '' : String(v);
  };
  Scorm.prototype.set = function (k, v) {
    log('set', k, '=', v);
    if (!this.active) return false;
    var ok = String(this.api.LMSSetValue(k, String(v))) === 'true';
    if (!ok) { try { log('LMSSetValue failed', k, this.api.LMSGetLastError()); } catch (e) {} }
    return ok;
  };
  Scorm.prototype.commit = function () { log('commit'); return this.active ? String(this.api.LMSCommit('')) === 'true' : false; };
  Scorm.prototype.finish = function () {
    if (this.finished) return;
    this.finished = true;
    this.set('cmi.core.session_time', scormTime(Date.now() - this.start));
    if (!this.active) { log('LMSFinish (standalone)'); return; }
    this.commit();
    this.api.LMSFinish('');
    this.active = false;
    log('LMSFinish');
  };

  // suspend_data: small JSON {"a":attempts,"b":bestScore,"p":everPassed}
  function readState(scorm) {
    var s = { a: 0, b: 0, p: false };
    try { var raw = scorm.get('cmi.suspend_data'); if (raw) { var o = JSON.parse(raw); s.a = +o.a || 0; s.b = +o.b || 0; s.p = !!o.p; } } catch (e) {}
    return s;
  }

  // ------------------------------------------------------------ quiz engine
  function Quiz(lesson, rng) {
    this.cfg = lesson.quiz || {};
    this.passPercent = this.cfg.pass_percent != null ? +this.cfg.pass_percent : 80;
    this.maxAttempts = this.cfg.max_attempts != null ? +this.cfg.max_attempts : 2;
    this.doShuffle = this.cfg.shuffle !== false;
    this.rng = rng || Math.random;
    this.source = (this.cfg.questions || []).filter(function (q) {
      return (q.options || []).some(function (o) { return o.correct === true; });
    });
    this.reset();
  }
  Quiz.prototype.reset = function () {
    var self = this;
    var items = this.source.map(function (q, qi) {
      var opts = (q.options || []).map(function (o, oi) {
        return { text: String(o.text || ''), correct: o.correct === true, why: String(o.why || ''), orig: oi };
      });
      if (self.doShuffle && q.type !== 'truefalse') opts = shuffleArr(opts, self.rng);
      return { prompt: String(q.prompt || ''), type: q.type || 'mc', orig: qi, options: opts };
    });
    this.items = this.doShuffle ? shuffleArr(items, this.rng) : items;
    this.pos = 0;
    this.answers = [];
  };
  Quiz.prototype.current = function () { return this.items[this.pos] || null; };
  Quiz.prototype.answer = function (optIndex) {
    var q = this.current(); if (!q || this.answers[this.pos] != null) return null;
    var chosen = q.options[optIndex];
    var correctIdx = -1;
    for (var i = 0; i < q.options.length; i++) if (q.options[i].correct) { correctIdx = i; break; }
    var r = { q: q, chosenIndex: optIndex, chosen: chosen, correct: !!(chosen && chosen.correct), correctIndex: correctIdx, correctOpt: q.options[correctIdx] };
    this.answers[this.pos] = r;
    return r;
  };
  Quiz.prototype.next = function () { this.pos++; return this.current(); };
  Quiz.prototype.done = function () { return this.answers.length === this.items.length && this.answers.every(function (a) { return a != null; }); };
  Quiz.prototype.result = function () {
    var total = this.items.length, right = 0, missed = [];
    for (var i = 0; i < total; i++) { var a = this.answers[i]; if (a && a.correct) right++; else missed.push(a || { q: this.items[i], chosen: null, correctOpt: null }); }
    var score = total ? Math.round(right / total * 100) : 0;
    return { right: right, total: total, score: score, passed: score >= this.passPercent, missed: missed };
  };

  // Records a finished attempt to the LMS. Used by the UI and by the node test.
  function recordAttempt(scorm, state, res) {
    state.a += 1;
    state.b = Math.max(state.b, res.score);
    if (res.passed) state.p = true;
    // Report this attempt's score; never downgrade a lesson already passed in this LMS record.
    var status = res.passed ? 'passed' : (state.p ? 'passed' : 'failed');
    var raw = state.p && !res.passed ? state.b : res.score;
    scorm.set('cmi.core.score.min', '0');
    scorm.set('cmi.core.score.max', '100');
    scorm.set('cmi.core.score.raw', String(raw));
    scorm.set('cmi.core.lesson_status', status);
    scorm.set('cmi.suspend_data', JSON.stringify(state));
    scorm.set('cmi.core.exit', '');
    scorm.commit();
    return status;
  }

  var VP = { Quiz: Quiz, Scorm: Scorm, readState: readState, recordAttempt: recordAttempt, shuffle: shuffleArr, scormTime: scormTime, getAPI: getAPI };  root.VP = VP;
  if (typeof module !== 'undefined' && module.exports) module.exports = VP;

  // ------------------------------------------------------------ UI
  if (typeof document === 'undefined') return;

  var LESSON = JSON.parse(document.getElementById('lesson-data').textContent);
  var MEDIA = LESSON.media || {};
  var scorm = new Scorm(root);
  scorm.init();
  var state = readState(scorm);
  var quiz = new Quiz(LESSON);
  var reduceMotion = false;
  try { reduceMotion = !!(root.matchMedia && root.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) {}

  // ---------------- read aloud (browser speech). On by default; the Start click unlocks audio.
  var synth = root.speechSynthesis;
  var hasTTS = !!(synth && root.SpeechSynthesisUtterance);
  var ttsOn = true;
  try { if (root.localStorage.getItem('vpa_tts') === '0') ttsOn = false; } catch (e) {}
  var voice = null;
  var VOICE_PREFS = [/samantha/i, /google us english/i, /microsoft aria/i, /microsoft jenny/i, /microsoft guy/i];
  function pickVoice() {
    if (!hasTTS) return;
    var vs = [];
    try { vs = synth.getVoices() || []; } catch (e) {}
    if (!vs.length) return;
    var i, p, lang = function (v) { return String(v.lang || '').replace('_', '-').toLowerCase(); };
    for (p = 0; p < VOICE_PREFS.length; p++) for (i = 0; i < vs.length; i++) if (VOICE_PREFS[p].test(vs[i].name) && lang(vs[i]).indexOf('en') === 0) { voice = vs[i]; return; }
    for (i = 0; i < vs.length; i++) if (lang(vs[i]) === 'en-us') { voice = vs[i]; return; }
    for (i = 0; i < vs.length; i++) if (lang(vs[i]).indexOf('en') === 0) { voice = vs[i]; return; }
  }
  if (hasTTS) {
    pickVoice();
    try { if (synth.addEventListener) synth.addEventListener('voiceschanged', pickVoice); else synth.onvoiceschanged = pickVoice; } catch (e) {}
  }
  function sentenceChunks(t) {
    var parts = String(t).match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g) || [String(t)], out = [], cur = '';
    parts.forEach(function (p) { if ((cur + p).length > 220 && cur) { out.push(cur); cur = p; } else cur += p; });
    if (cur.trim()) out.push(cur);
    return out;
  }
  // ---------------- voiceover (recorded narration, embedded as base64 MP3 in #voice-b64).
  // TalentLMS's SCORM frame will not load <audio> media, so narration is decoded with Web Audio and
  // played through one shared AudioContext (the call player uses the same context).
  var VOICE = {};
  try { var vEl = document.getElementById('voice-b64'); if (vEl) VOICE = JSON.parse(vEl.textContent || '{}') || {}; } catch (e) { VOICE = {}; }
  var AC = root.AudioContext || root.webkitAudioContext;
  var hasVoice = !!AC && Object.keys(VOICE).length > 0;
  var actx = null, voiceBufs = {}, voiceNode = null, voiceToken = 0;
  function getCtx() {
    if (!AC) return null;
    if (!actx) { try { actx = new AC(); } catch (e) { actx = null; } }
    return actx;
  }
  function unlockAudio() { var c = getCtx(); if (c && c.state === 'suspended') { try { c.resume(); } catch (e) {} } }
  function setSpeaking(on) {
    var ind = stage && stage.querySelector('.vo-ind');
    if (ind) ind.className = 'vo-ind' + (on ? ' on' : '');
  }
  function stopVoice() {
    voiceToken++;
    if (voiceNode) { try { voiceNode.onended = null; voiceNode.stop(); } catch (e) {} voiceNode = null; }
    setSpeaking(false);
  }
  function voiceBuffer(key, cb) {
    if (voiceBufs[key]) { cb(voiceBufs[key]); return; }
    var c = getCtx(), b64 = VOICE[key];
    if (!c || !b64) { cb(null); return; }
    try {
      var bin = atob(b64), arr = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      var ok = function (b) { voiceBufs[key] = b; cb(b); }, bad = function () { cb(null); };
      var pr = c.decodeAudioData(arr.buffer, ok, bad);
      if (pr && pr.catch) pr.catch(bad);
    } catch (e) { cb(null); }
  }
  // Plays the narration for `key`; returns false when there is none (caller may fall back to speech).
  function playVoice(key) {
    if (!hasVoice || !VOICE[key]) return false;
    stopVoice();
    var my = voiceToken, c = getCtx();
    if (!c) return false;
    if (c.state === 'suspended') { try { c.resume(); } catch (e) {} }
    voiceBuffer(key, function (buf) {
      if (!buf || my !== voiceToken || !ttsOn) return;
      try {
        var n = c.createBufferSource(); n.buffer = buf; n.connect(c.destination);
        n.onended = function () {
          if (my !== voiceToken) return;
          voiceNode = null; setSpeaking(false);
          if (ui.primary && !ui.primary.disabled) { ui.primary.classList.remove('nudge'); void ui.primary.offsetWidth; ui.primary.classList.add('nudge'); }
        };
        n.start(0); voiceNode = n; setSpeaking(true);
      } catch (e) { setSpeaking(false); }
    });
    return true;
  }
  function speakingIndicator() {
    return el('span', { cls: 'vo-ind', role: 'status' }, [el('span', { cls: 'eq', 'aria-hidden': 'true' }, [el('i'), el('i'), el('i'), el('i')]), 'Speaking']);
  }

  function stopSpeech() { stopVoice(); try { if (hasTTS) synth.cancel(); } catch (e) {} try { if (window.__vpStopCall) window.__vpStopCall(); } catch (e) {} }
  function speak(t) {
    if (!hasTTS || !t) return;
    stopSpeech();
    if (!voice) pickVoice();
    // Short utterances: some browsers cut a long one off after ~15 seconds.
    sentenceChunks(t).forEach(function (c) {
      try {
        var u = new root.SpeechSynthesisUtterance(c.trim());
        if (voice) u.voice = voice;
        u.lang = voice && voice.lang ? voice.lang : 'en-US';
        u.rate = 1; u.pitch = 1;
        synth.speak(u);
      } catch (e) {}
    });
    try { synth.resume(); } catch (e) {}
  }

  function onExit() { stopSpeech(); scorm.finish(); }
  root.addEventListener('pagehide', onExit);
  root.addEventListener('beforeunload', onExit);
  root.addEventListener('unload', onExit);

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'text') n.textContent = attrs[k];
      else if (k === 'cls') n.className = attrs[k];
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  var SVGNS = 'http://www.w3.org/2000/svg';
  function icon(name) {
    var s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('class', 'ic'); s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('aria-hidden', 'true'); s.setAttribute('focusable', 'false');
    var u = document.createElementNS(SVGNS, 'use');
    u.setAttribute('href', '#i-' + name);
    try { u.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', '#i-' + name); } catch (e) {}
    s.appendChild(u);
    return s;
  }
  function bigIcon(name, alt) { return el('div', { cls: 'iconwrap' + (alt ? ' b' : '') }, [icon(name || 'star')]); }

  // ---------------- steps
  var hasVideo = !!MEDIA.video;
  var slides = (LESSON.slides || []).filter(function (s) { return s && (s.heading || (s.bullets || []).length); });
  var clip = LESSON.call_clip || null;
  var hasClip = !!(clip && MEDIA.clip);
  var steps = [{ k: 'title', l: 'Start' }];
  if (hasVideo || slides.length) steps.push({ k: 'watch', l: hasVideo ? 'Watch' : 'Learn' });
  if (hasClip) steps.push({ k: 'listen', l: 'Listen' });
  steps.push({ k: 'recap', l: 'Key points' });
  if (LESSON.floor_check) steps.push({ k: 'floor', l: 'Floor Check' });
  steps.push({ k: 'test', l: 'Test' });
  steps.push({ k: 'result', l: 'Result' });
  function stepOf(k) { for (var i = 0; i < steps.length; i++) if (steps[i].k === k) return i; return -1; }

  var stepIdx = 0, slideIdx = 0, maxSlide = 0, dir = 1, lastResult = null;
  var stage = document.getElementById('stage');
  var barFill = document.getElementById('barfill');
  var stepsEl = document.getElementById('steps');
  var ui = { primary: null, back: null, keys: null };

  function drawProgress() {
    var pct = steps.length > 1 ? (stepIdx / (steps.length - 1)) * 100 : 100;
    if (steps[stepIdx].k === 'watch' && !hasVideo && slides.length) pct = ((stepIdx - 1 + (slideIdx + 1) / slides.length) / (steps.length - 1)) * 100;
    if (steps[stepIdx].k === 'test' && quiz.items.length) pct = ((stepIdx + quiz.answers.length / quiz.items.length) / (steps.length - 1)) * 100;
    barFill.style.width = Math.max(3, pct) + '%';
    stepsEl.innerHTML = '';
    steps.forEach(function (s, i) { stepsEl.appendChild(el('span', { cls: i === stepIdx ? 'on' : (i < stepIdx ? 'done' : ''), text: s.l, title: s.l })); });
  }
  function toTop() { try { root.scrollTo(0, 0); } catch (e) {} try { document.documentElement.scrollTop = 0; document.body.scrollTop = 0; } catch (e) {} try { stage.scrollTop = 0; } catch (e) {} }
  // Narrate the current screen: recorded voiceover when embedded, else browser speech (slides only).
  // The result screen is silent.
  function speakSlide() {
    if (!ttsOn) return;
    var k = steps[stepIdx].k;
    if (k === 'title') { playVoice('intro'); return; }
    if (k === 'recap') { playVoice('keypoints'); return; }
    if (k === 'watch' && !hasVideo && slides[slideIdx]) {
      if (playVoice(String(slideIdx))) return;
      speak(slides[slideIdx].say || [slides[slideIdx].heading].concat(slides[slideIdx].bullets || []).join('. '));
    }
  }
  var audioUnlocked = false;
  function go(i, d) {
    stopSpeech();
    audioUnlocked = true; unlockAudio();  // every go() runs inside a click or key press
    var n = Math.max(0, Math.min(steps.length - 1, i));
    dir = d || (n >= stepIdx ? 1 : -1);
    stepIdx = n;
    render();
    toTop();
    speakSlide();  // called inside the click that got us here, so browsers allow the audio
  }
  function navbar(o) {
    var b = o.back ? el('button', { cls: 'btn sec', type: 'button', text: o.backLabel || 'Back', onclick: o.back }) : null;
    var n = el('button', { cls: 'btn pri', type: 'button', text: o.nextLabel || 'Continue' });
    n.addEventListener('click', function () { if (!n.disabled) o.next(); });
    if (o.nextDisabled) n.disabled = true;
    var hint = el('span', { cls: o.hint != null ? 'hint' : 'sp', text: o.hint || '' });
    ui.primary = n; ui.back = b;
    var bar = el('div', { cls: 'navbar' }, [el('div', { cls: 'navin' }, [b, hint, n])]);
    stage.appendChild(bar);
    return { next: n, back: b, hint: hint };
  }
  function animateIn(node) { if (!reduceMotion && node) node.className += dir < 0 ? ' in-back' : ' in-fwd'; }
  function focusHeading() { var h = stage.querySelector('h1, h2'); if (h) { h.setAttribute('tabindex', '-1'); try { h.focus({ preventScroll: true }); } catch (e) {} } }

  function render() {
    drawProgress();
    stage.innerHTML = '';
    ui.primary = ui.back = ui.keys = null;
    ({ title: rTitle, watch: rWatch, listen: rListen, recap: rRecap, floor: rFloor, test: rTest, result: rResult })[steps[stepIdx].k]();
    animateIn(stage.querySelector('.card'));
  }

  function ttsButton(onToggle) {
    var b = el('button', { cls: 'tts', type: 'button' });
    function paint() {
      b.className = 'tts' + (ttsOn ? ' on' : '');
      b.setAttribute('aria-pressed', String(ttsOn));
      b.innerHTML = '';
      b.appendChild(icon(ttsOn ? 'speaker' : 'mute'));
      b.appendChild(document.createTextNode(ttsOn ? 'Voiceover: On' : 'Voiceover: Off'));
    }
    b.addEventListener('click', function () {
      ttsOn = !ttsOn;
      audioUnlocked = true; unlockAudio();
      try { root.localStorage.setItem('vpa_tts', ttsOn ? '1' : '0'); } catch (e) {}
      paint();
      if (onToggle) onToggle(); else if (!ttsOn) stopSpeech();
    });
    paint();
    return b;
  }

  // ---------------- screens
  function rTitle() {
    var pills = [
      el('span', { cls: 'pill' }, [icon('clock'), 'About ' + (LESSON.minutes || '?') + ' minutes']),
      el('span', { cls: 'pill' }, [icon('clipboard'), quiz.items.length + ' test questions']),
      el('span', { cls: 'pill' }, [icon('check'), quiz.passPercent + '% to pass'])
    ];
    var parts = [];
    if (hasVideo) parts.push('watch a short video'); else if (slides.length) parts.push('go through ' + slides.length + ' short slides');
    if (hasClip) parts.push('listen to a real call');
    parts.push('review the key points');
    var intro = 'You\'ll ' + parts.join(', ') + ', then take a short test. You can go back at any point before the test.';
    var text = el('div', {}, [
      el('div', { cls: 'kicker', text: 'Valley Pawn Academy · ' + (LESSON.level_label || '') }),
      el('h1', { text: LESSON.title }),
      el('div', { cls: 'meta' }, pills),
      LESSON.gate ? el('div', { cls: 'note purple' }, [el('b', { text: 'Deadline: ' }), LESSON.gate]) : null,
      state.p ? el('div', { cls: 'note blue', text: 'You have already passed this lesson. You can go through it again any time.' }) : null,
      el('p', { text: intro }),
      ((hasTTS || hasVoice) && !hasVideo && slides.length) ? el('div', { cls: 'ttsrow' }, [
        ttsButton(function () { if (ttsOn) speakSlide(); else stopSpeech(); }),
        el('span', { cls: 'small', text: 'Each slide is read to you. Turn it off any time.' }),
        hasVoice ? speakingIndicator() : null]) : null
    ]);
    stage.appendChild(el('div', { cls: 'card hero' }, [bigIcon(LESSON.icon || 'store'), text]));
    navbar({ nextLabel: 'Start lesson', next: function () { slideIdx = 0; go(1, 1); } });
    // Browsers only allow sound after the learner interacts. Once unlocked (they came back to
    // Start, or a first tap lands on this card) the intro plays; a tap on "Start lesson" moves on.
    if (hasVoice && VOICE.intro && ttsOn) {
      if (audioUnlocked) return;  // go() narrates after render
      var tryIntro = function () {
        document.removeEventListener('pointerdown', tryIntro, true);
        document.removeEventListener('keydown', tryIntro, true);
        audioUnlocked = true; unlockAudio();
        if (steps[stepIdx].k === 'title' && ttsOn && !voiceNode) playVoice('intro');
      };
      document.addEventListener('pointerdown', tryIntro, true);
      document.addEventListener('keydown', tryIntro, true);
    }
  }

  function rWatch() {
    var c = el('div', { cls: 'card' });
    if (hasVideo) {
      c.appendChild(el('h2', { text: 'Watch' }));
      if (MEDIA.video_kind === 'embed') c.appendChild(el('div', { cls: 'embed' }, [el('iframe', { src: MEDIA.video, allow: 'fullscreen; picture-in-picture', allowfullscreen: 'true', title: LESSON.title })]));
      else c.appendChild(el('video', { src: MEDIA.video, controls: 'controls', playsinline: 'playsinline', preload: 'metadata' }));
      stage.appendChild(c);
      navbar({ back: function () { go(stepIdx - 1, -1); }, next: function () { go(stepIdx + 1, 1); } });
      ui.keys = { left: function () { go(stepIdx - 1, -1); }, right: function () { go(stepIdx + 1, 1); } };
      return;
    }
    var s = slides[slideIdx] || {};
    maxSlide = Math.max(maxSlide, slideIdx);
    var dots = el('div', { cls: 'dots', 'aria-hidden': 'true' });
    slides.forEach(function (x, i) { dots.appendChild(el('i', { cls: i === slideIdx ? 'on' : (i <= maxSlide ? 'seen' : '') })); });
    c.appendChild(el('div', { cls: 'slidetop' }, [
      el('span', { cls: 'grp' }, [el('span', { cls: 'slidecount', text: 'Slide ' + (slideIdx + 1) + ' of ' + slides.length }), hasVoice ? speakingIndicator() : null]),
      (hasTTS || hasVoice) ? ttsButton(function () { if (ttsOn) speakSlide(); else stopSpeech(); }) : null
    ]));
    c.appendChild(el('div', { cls: 'slidebody' }, [
      bigIcon(s.icon, slideIdx % 2 === 1),
      el('div', { cls: 'slidetext' }, [el('h2', { text: s.heading || '' }), el('ul', { cls: 'pts' }, (s.bullets || []).map(function (b) { return el('li', { text: b }); }))])
    ]));
    c.appendChild(dots);
    stage.appendChild(c);
    var last = slideIdx >= slides.length - 1;
    function prev() { stopSpeech(); if (slideIdx > 0) { slideIdx--; dir = -1; render(); toTop(); speakSlide(); } else go(stepIdx - 1, -1); }
    function next() { stopSpeech(); if (!last) { slideIdx++; dir = 1; render(); toTop(); speakSlide(); } else go(stepIdx + 1, 1); }
    navbar({ back: prev, next: next, nextLabel: last ? 'Continue' : 'Next' });
    ui.keys = { left: prev, right: next };
  }

  function rListen() {
    var c = el('div', { cls: 'card' }, [el('div', { cls: 'lhead' }, [bigIcon('headphones', true), el('h2', { text: 'Listen: a real call' })])]);
    var cap = el('div', { cls: 'caption' });
    if (clip.caption) cap.appendChild(el('p', { text: String(clip.caption) }));
    if (MEDIA.clip_label) cap.appendChild(el('span', { cls: 'pill' }, [icon('clock'), MEDIA.clip_label]));
    c.appendChild(cap);
    // Call player on the Web Audio API. TalentLMS's SCORM frame will not load <audio> media
    // (verified live 2026-09-28: stuck at 0:00 for packaged .m4a, packaged .mp3 AND a blob URL).
    // Decoding the inline MP3 bytes into an AudioBuffer sidesteps media loading entirely.
    var player = el('div', { cls: 'cplayer' });
    var pbtn = el('button', { cls: 'cpbtn', type: 'button', 'aria-label': 'Play the call', text: '▶' });
    var bar = el('div', { cls: 'cpbar' }, [el('div', { cls: 'cpfill' })]);
    var tm = el('span', { cls: 'cptime', text: 'Loading call…' });
    player.appendChild(pbtn); player.appendChild(bar); player.appendChild(tm);
    var err = el('div', { cls: 'note', style: 'display:none' }, ['The call didn\'t load on this device. Tell your manager, then keep going — the ticks below still count.']);
    c.appendChild(player);
    c.appendChild(err);
    function fmt(t) { t = Math.max(0, Math.floor(t || 0)); return Math.floor(t / 60) + ':' + ('0' + (t % 60)).slice(-2); }
    var ctx = null, buf = null, srcNode = null;
    var playing = false, offset = 0, startedAt = 0, raf = null;
    function pos() { return playing ? Math.min(buf.duration, offset + (ctx.currentTime - startedAt)) : offset; }
    function paint() {
      if (!buf) return;
      var p = pos();
      bar.firstChild.style.width = (100 * p / buf.duration) + '%';
      tm.textContent = fmt(p) + ' / ' + fmt(buf.duration);
      if (playing) raf = requestAnimationFrame(paint);
    }
    function stopNode() { if (srcNode) { try { srcNode.onended = null; srcNode.stop(); } catch (e) {} srcNode = null; } }
    function pause() { if (!playing) return; offset = pos(); playing = false; stopNode(); pbtn.textContent = '▶'; pbtn.setAttribute('aria-label', 'Play the call'); cancelAnimationFrame(raf); paint(); }
    function play() {
      if (!buf) return;
      stopVoice();
      try { if (hasTTS) synth.cancel(); } catch (e) {}
      if (ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
      if (offset >= buf.duration - 0.05) offset = 0;
      srcNode = ctx.createBufferSource(); srcNode.buffer = buf; srcNode.connect(ctx.destination);
      srcNode.onended = function () { if (playing && pos() >= buf.duration - 0.1) { playing = false; offset = buf.duration; pbtn.textContent = '↻'; paint(); } };
      startedAt = ctx.currentTime; srcNode.start(0, offset); playing = true;
      pbtn.textContent = '❚❚'; pbtn.setAttribute('aria-label', 'Pause the call'); paint();
    }
    window.__vpStopCall = pause;
    pbtn.addEventListener('click', function () { if (!buf) return; playing ? pause() : play(); });
    bar.addEventListener('click', function (ev) {
      if (!buf) return;
      var r = bar.getBoundingClientRect(), f = Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width));
      var was = playing; if (was) { playing = false; stopNode(); }
      offset = f * buf.duration; if (was) play(); else paint();
    });
    (function load() {
      try {
        var b64el = document.getElementById('clip-b64');
        var b64 = b64el ? b64el.textContent.trim() : '';
        if (!AC || !b64) throw new Error('no audio');
        ctx = getCtx();  // one shared AudioContext for the call and the voiceover
        if (!ctx) throw new Error('no audio context');
        var bin = atob(b64), arr = new Uint8Array(bin.length);
        for (var bi = 0; bi < bin.length; bi++) arr[bi] = bin.charCodeAt(bi);
        var done = function (b) { buf = b; tm.textContent = '0:00 / ' + fmt(b.duration); pbtn.disabled = false; paint(); };
        var fail = function () { tm.textContent = ''; err.style.display = 'block'; };
        var pr = ctx.decodeAudioData(arr.buffer, done, fail);
        if (pr && pr.catch) pr.catch(fail);
      } catch (e) { tm.textContent = ''; err.style.display = 'block'; }
    })();
    pbtn.disabled = true;
    if (MEDIA.clip) { /* packaged file kept as a fallback reference for other LMSs */ var ref = 'audio/mpeg'; }
    var items = clip.listen_for || [];
    var boxes = [];
    if (items.length) {
      c.appendChild(el('p', { cls: 'lf', text: 'Listen for these. Tick each one when you hear it:' }));
      items.forEach(function (t, i) {
        var cb = el('input', { type: 'checkbox', id: 'lf' + i });
        var lab = el('label', { cls: 'check', 'for': 'lf' + i }, [cb, el('span', { text: t })]);
        cb.addEventListener('change', function () { lab.className = 'check' + (cb.checked ? ' on' : ''); update(); });
        boxes.push(cb);
        c.appendChild(lab);
      });
    }
    stage.appendChild(c);
    var n = navbar({ back: function () { go(stepIdx - 1, -1); }, next: function () { go(stepIdx + 1, 1); }, nextDisabled: items.length > 0, hint: items.length ? 'Tick all ' + items.length + ' to continue' : '' });
    function update() {
      var left = boxes.filter(function (b) { return !b.checked; }).length;
      n.next.disabled = left > 0;
      n.hint.textContent = left ? (left + ' left to tick') : '';
    }
    ui.keys = { left: function () { go(stepIdx - 1, -1); } };
  }

  function rRecap() {
    var list = el('div', { cls: 'kps' });
    (LESSON.key_points || []).forEach(function (p, i) {
      var card = el('div', { cls: 'kp' }, [el('span', { cls: 'tk' }, [icon('tick')]), el('span', { text: p })]);
      card.style.animationDelay = (0.08 + i * 0.12) + 's';
      list.appendChild(card);
    });
    var kpTop = (hasVoice && VOICE.keypoints)
      ? el('div', { cls: 'slidetop' }, [el('span', { cls: 'grp' }, [el('h2', { text: 'Key points', style: 'margin:0' }), speakingIndicator()]),
          ttsButton(function () { if (ttsOn) speakSlide(); else stopSpeech(); })])
      : el('h2', { text: 'Key points' });
    stage.appendChild(el('div', { cls: 'card' }, [kpTop, list]));
    navbar({ back: function () { go(stepIdx - 1, -1); }, next: function () { go(stepIdx + 1, 1); }, nextLabel: LESSON.floor_check ? 'Continue' : 'Start the test' });
    ui.keys = { left: function () { go(stepIdx - 1, -1); } };
  }

  function rFloor() {
    stage.appendChild(el('div', { cls: 'card' }, [
      el('div', { cls: 'lhead' }, [bigIcon('clipboard'), el('h2', { text: 'Floor Check' })]),
      el('div', { cls: 'note' }, [el('b', { text: 'Your manager will verify this on the floor: ' }), String(LESSON.floor_check)]),
      el('p', { cls: 'small', text: 'Passing the test plus your manager\'s Floor Check means you\'ve mastered this skill.' })]));
    navbar({ back: function () { go(stepIdx - 1, -1); }, next: function () { go(stepIdx + 1, 1); }, nextLabel: 'Start the test' });
    ui.keys = { left: function () { go(stepIdx - 1, -1); } };
  }

  var CHEERS = [
    'That\'s it. That\'s how we handle it here.',
    'Right call. You\'d handle that one fine at the counter.',
    'Exactly right. Keep going.',
    'Good. That one trips people up.',
    'Correct. Customers trust people who get that right.',
    'You\'ve got it. On to the next one.',
    'Spot on.',
    'Yes. That\'s the Valley Pawn way.'
  ];
  var cheerAt = Math.floor(Math.random() * CHEERS.length);
  function cheer() { cheerAt = (cheerAt + 1 + Math.floor(Math.random() * 2)) % CHEERS.length; return CHEERS[cheerAt]; }

  function rTest() {
    if (!quiz.items.length) {
      stage.appendChild(el('div', { cls: 'card' }, [el('h2', { text: 'Test' }), el('p', { text: 'This lesson has no test questions yet.' })]));
      navbar({ back: function () { go(stepIdx - 1, -1); }, next: function () { go(stepIdx - 1, -1); }, nextLabel: 'Back' });
      return;
    }
    if (!quiz.current() || lastResult) { quiz.reset(); lastResult = null; }
    var q = quiz.current();
    var total = quiz.items.length;
    function rightSoFar() { return quiz.answers.filter(function (a) { return a && a.correct; }).length; }
    var tally = el('span', { cls: 'tally' });
    function paintTally() {
      var answered = quiz.answers.filter(function (a) { return a; }).length;
      tally.innerHTML = '';
      tally.appendChild(icon('star'));
      tally.appendChild(document.createTextNode(answered ? ('Score: ' + rightSoFar() + ' of ' + answered) : 'Good luck'));
    }
    var segs = el('div', { cls: 'segs', 'aria-hidden': 'true' });
    function paintSegs() {
      segs.innerHTML = '';
      for (var i = 0; i < total; i++) { var a = quiz.answers[i]; segs.appendChild(el('i', { cls: a ? (a.correct ? 'r' : 'w') : (i === quiz.pos ? 'cur' : '') })); }
    }
    paintTally(); paintSegs();
    var c = el('div', { cls: 'card' }, [
      el('div', { cls: 'qhead' }, [el('span', { cls: 'qnum', text: 'Question ' + (quiz.pos + 1) + ' of ' + total }), tally]),
      segs,
      el('div', { cls: 'qtype', text: q.type === 'scenario' ? 'Scenario' : (q.type === 'truefalse' ? 'True or false' : 'Pick the best answer') }),
      el('h2', { cls: 'prompt', text: q.prompt })
    ]);
    var LETTERS = 'ABCDEFGH';
    var btns = q.options.map(function (o, i) {
      return el('button', { cls: 'opt', type: 'button', onclick: function () { choose(i); } }, [el('span', { cls: 'lt', text: LETTERS.charAt(i) }), el('span', { text: o.text })]);
    });
    btns.forEach(function (b) { c.appendChild(b); });
    var fbBox = el('div', { 'aria-live': 'polite' });
    c.appendChild(fbBox);
    stage.appendChild(c);
    var last = quiz.pos >= total - 1;
    var n = navbar({ next: function () {
      if (last) finishTest(); else { quiz.next(); dir = 1; render(); toTop(); }
    }, nextLabel: last ? 'See my score' : 'Next question', nextDisabled: true, hint: 'Pick an answer' });
    ui.keys = { pick: function (i) { if (i < btns.length && !btns[i].disabled) choose(i); } };

    function choose(i) {
      var r = quiz.answer(i); if (!r) return;
      btns.forEach(function (b, bi) {
        b.disabled = true;
        var lt = b.firstChild;
        if (q.options[bi].correct) { b.classList.add('right'); lt.textContent = ''; lt.appendChild(icon('tick')); }
        else if (bi !== i) b.classList.add('dim');
      });
      btns[i].classList.add('picked');
      if (!r.correct) { btns[i].classList.add('wrong'); btns[i].firstChild.textContent = ''; btns[i].firstChild.appendChild(icon('x')); }
      var box = el('div', { cls: 'fb ' + (r.correct ? 'ok' : 'no') }, [el('span', { cls: 'h', text: r.correct ? cheer() : 'Not quite.' })]);
      if (r.correct) { if (r.chosen.why) box.appendChild(el('p', { text: r.chosen.why })); }
      else {
        if (r.chosen.why) box.appendChild(el('p', {}, [el('strong', { text: 'Your answer: ' }), r.chosen.why]));
        if (r.correctOpt) {
          box.appendChild(el('p', {}, [el('strong', { text: 'The right answer: ' }), r.correctOpt.text]));
          if (r.correctOpt.why) box.appendChild(el('p', {}, [el('strong', { text: 'Why: ' }), r.correctOpt.why]));
        }
      }
      fbBox.appendChild(box);
      paintTally(); paintSegs();
      n.next.disabled = false;
      n.hint.textContent = '';
      drawProgress();
      try { n.next.focus({ preventScroll: true }); } catch (e) {}
      // bring the explanation into view above the sticky button bar (scrolls this frame only)
      try {
        var nb = stage.querySelector('.navbar'), navH = nb ? nb.offsetHeight : 0;
        var rc = box.getBoundingClientRect(), vh = root.innerHeight || document.documentElement.clientHeight;
        var over = rc.bottom - (vh - navH) + 12;
        if (over > 0) {
          var by = Math.min(over, Math.max(0, rc.top - 70));
          try { stage.scrollBy({ top: by, behavior: reduceMotion ? 'auto' : 'smooth' }); } catch (e2) { stage.scrollTop += by; }
        }
      } catch (e) {}
    }
  }

  function finishTest() {
    lastResult = quiz.result();
    recordAttempt(scorm, state, lastResult);
    go(steps.length - 1, 1);
  }

  function confetti() {
    if (reduceMotion) return;
    var box = el('div', { cls: 'confetti', 'aria-hidden': 'true' }), colors = ['#4B2F74', '#508DCE', '#DB7971', '#F4C95D', '#ffffff'];
    for (var i = 0; i < 110; i++) {
      var p = el('i');
      p.style.left = (Math.random() * 100) + 'vw';
      p.style.background = colors[i % colors.length];
      p.style.animationDuration = (2.2 + Math.random() * 2.4) + 's';
      p.style.animationDelay = (Math.random() * 0.9) + 's';
      p.style.transform = 'rotate(' + (Math.random() * 360) + 'deg)';
      if (i % 5 === 4) p.style.boxShadow = '0 0 0 1px #ddd';
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(function () { if (box.parentNode) box.parentNode.removeChild(box); }, 6000);
  }

  function scoreRing(score, passed) {
    var C = 2 * Math.PI * 52;
    var svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('viewBox', '0 0 120 120'); svg.setAttribute('aria-hidden', 'true');
    function circ(cls) { var ci = document.createElementNS(SVGNS, 'circle'); ci.setAttribute('cx', '60'); ci.setAttribute('cy', '60'); ci.setAttribute('r', '52'); ci.setAttribute('class', cls); return ci; }
    var val = circ('val');
    val.style.strokeDasharray = C.toFixed(1);
    val.style.strokeDashoffset = reduceMotion ? (C * (1 - score / 100)).toFixed(1) : C.toFixed(1);
    svg.appendChild(circ('trk')); svg.appendChild(val);
    var ring = el('div', { cls: 'ring' + (passed ? '' : ' fail'), role: 'img', 'aria-label': 'Score ' + score + ' percent' }, [svg, el('b', { text: score + '%' })]);
    setTimeout(function () { val.style.strokeDashoffset = (C * (1 - score / 100)).toFixed(1); }, 60);
    return ring;
  }

  function rResult() {
    var r = lastResult;
    if (!r) { go(stepOf('test'), -1); return; }
    var c = el('div', { cls: 'card result' }, [
      scoreRing(r.score, r.passed),
      el('div', { cls: 'kicker', text: r.passed ? 'You passed' : 'Not yet' }),
      el('h1', { text: r.passed ? 'Lesson complete' : 'Almost there' }),
      el('p', { text: r.right + ' of ' + r.total + ' correct · ' + quiz.passPercent + '% needed to pass' })
    ]);
    if (r.passed) {
      c.appendChild(el('div', {}, [el('span', { cls: 'points' }, [icon('star'), 'You earned points toward the leaderboard'])]));
      if (LESSON.floor_check) c.appendChild(el('p', { text: 'Screen test done. Next: your manager\'s Floor Check on the floor.' }));
      else c.appendChild(el('p', { text: 'Nice work. You\'re ready for the next lesson.' }));
      if (r.missed.length) c.appendChild(el('p', { cls: 'small', text: 'You missed ' + r.missed.length + '. ' + (r.missed.length === 1 ? 'It\'s' : 'They\'re') + ' below so you know the right answer.' }));
    } else {
      c.appendChild(el('p', { text: 'Go over what you missed below, then take it again. The questions come back in a new order.' }));
      if (state.a >= quiz.maxAttempts) c.appendChild(el('div', { cls: 'note', style: 'text-align:left' }, [el('b', { text: 'Ask your manager to go through this lesson with you. ' }), 'You can still retake the test any time.']));
    }
    c.appendChild(el('p', { cls: 'small', text: 'Attempts so far: ' + state.a + (scorm.active ? ' · Your result has been saved.' : ' · Preview mode: nothing is recorded.') }));
    stage.appendChild(c);
    if (r.missed.length) {
      var m = el('div', { cls: 'card' }, [el('h2', { text: r.passed ? 'Worth a second look' : 'What you missed' })]);
      r.missed.forEach(function (a) {
        var box = el('div', { cls: 'missed' }, [el('p', { cls: 'q', text: a.q.prompt })]);
        if (a.chosen) box.appendChild(el('div', { cls: 'fb no' }, [el('span', { cls: 'h', text: 'You answered: ' + a.chosen.text }), a.chosen.why ? el('p', { text: a.chosen.why }) : null]));
        if (a.correctOpt) box.appendChild(el('div', { cls: 'fb ok' }, [el('span', { cls: 'h', text: 'Right answer: ' + a.correctOpt.text }), a.correctOpt.why ? el('p', { text: a.correctOpt.why }) : null]));
        m.appendChild(box);
      });
      stage.appendChild(m);
    }
    navbar({
      back: function () { slideIdx = 0; go(1, -1); }, backLabel: 'Review lesson',
      next: function () { quiz.reset(); lastResult = null; go(stepOf('test'), 1); }, nextLabel: r.passed ? 'Take it again' : 'Retake the test'
    });
    if (r.passed) confetti();
  }

  // ---------------- keyboard: left/right move, Enter continues, 1-4 or A-D answer
  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target || {}, tag = (t.tagName || '').toUpperCase();
    var onControl = /^(BUTTON|INPUT|TEXTAREA|SELECT|A|AUDIO|VIDEO|LABEL)$/.test(tag) || t.isContentEditable;
    var k = e.key || '';
    var kind = steps[stepIdx].k;
    if (ui.keys && ui.keys.pick && !e.shiftKey) {
      var idx = /^[1-8]$/.test(k) ? (+k - 1) : ('abcdefgh'.indexOf(k.toLowerCase()) >= 0 && k.length === 1 ? 'abcdefgh'.indexOf(k.toLowerCase()) : -1);
      if (idx >= 0) { ui.keys.pick(idx); e.preventDefault(); return; }
    }
    if (k === 'ArrowRight' || k === 'ArrowLeft') {
      if (tag === 'AUDIO' || tag === 'VIDEO' || (tag === 'INPUT' && t.type === 'range')) return;
      if (k === 'ArrowLeft' && ui.keys && ui.keys.left) { ui.keys.left(); e.preventDefault(); }
      else if (k === 'ArrowRight' && kind !== 'result') {
        if (ui.keys && ui.keys.right) ui.keys.right();
        else if (ui.primary && !ui.primary.disabled) ui.primary.click();
        e.preventDefault();
      }
      return;
    }
    if (k === 'Enter' && !onControl && kind !== 'result' && ui.primary && !ui.primary.disabled) { ui.primary.click(); e.preventDefault(); }
  });

  render();
})(typeof window !== 'undefined' ? window : this);
"""

# TalentLMS hosts the SCO in a fixed-height frame that does not scroll (verified live 2026-09-28),
# so the lesson owns its scrolling: header + step bar fixed, #stage scrolls, button bar sticks to its bottom.
FRAME_FIT_CSS = """
html,body{height:100%;min-height:0;overflow:hidden}
body{display:flex;flex-direction:column}
header.top,.progress{flex:none}
#stage{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
"""

PLAYER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
__SPRITE__
<header class="top"><img src="logo.png" alt="Valley Pawn"><span class="lid">Academy · __ID__</span></header>
<div class="progress"><div class="in"><div class="bar"><i id="barfill"></i></div><div class="steps" id="steps"></div></div></div>
<main id="stage" aria-live="polite"><noscript><div class="card">This lesson needs JavaScript turned on.</div></noscript></main>
<script type="application/json" id="lesson-data">__LESSON__</script>
<script id="player">__JS__</script>
</body>
</html>
"""


def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def learner_payload(lesson, media):
    """Only what the learner sees. No sources, production notes, file names or build data."""
    T = learner_text
    slides, prev = [], None
    for s in lesson.get("slides") or []:
        if not isinstance(s, dict):
            continue
        heading = T(s.get("heading", ""))
        bullets = [T(b) for b in (s.get("bullets") or []) if str(b).strip()]
        ic = pick_icon(heading, bullets, avoid=prev)
        prev = ic
        slides.append({"heading": heading, "bullets": bullets, "say": T(s.get("say", "")), "icon": ic})
    quiz = lesson.get("quiz") or {}
    questions = []
    for q in usable_questions(lesson):
        questions.append({
            "type": q.get("type", "mc"),
            "prompt": T(q.get("prompt", "")),
            "options": [{"text": T(o.get("text", "")), "correct": o.get("correct") is True,
                         "why": T(o.get("why", ""), keep_policy=True)} for o in q.get("options") or []],
        })
    clip = lesson.get("call_clip") if isinstance(lesson.get("call_clip"), dict) else None
    cap = str((clip or {}).get("caption") or "")
    out = {
        "id": lesson["id"],
        "title": T(lesson.get("title", "")),
        "level_label": level_label(lesson.get("level")),
        "minutes": lesson.get("minutes"),
        "gate": T(lesson.get("gate") or "") or None,
        "icon": pick_icon(lesson.get("title", ""), [s["heading"] for s in slides]),
        "slides": slides,
        "call_clip": ({"caption": "" if cap.strip().upper().startswith("TODO") else T(cap),
                       "listen_for": [T(x) for x in clip.get("listen_for") or []]} if clip else None),
        "key_points": [T(k) for k in lesson.get("key_points") or []],
        "floor_check": T(lesson.get("floor_check") or "") or None,
        "quiz": {"pass_percent": quiz.get("pass_percent", 80), "max_attempts": quiz.get("max_attempts", 2),
                 "shuffle": quiz.get("shuffle", True), "questions": questions},
        "media": media,
    }
    return out


def resolve_voice(payload):
    """Voiceover MP3s already in the cache (made by voice.py) -> ({key: base64}, stats).
    Keys: "intro", slide indexes "0".."n-1" (slides the player shows), "keypoints".
    Nothing is ever generated or billed here; missing lines fall back to browser speech."""
    try:
        sys.path.insert(0, ACADEMY)
        import voice as V
    except Exception as e:  # noqa - voice.py missing/broken must not break builds
        return {}, {"lines": 0, "embedded": 0, "bytes": 0, "note": f"voice.py not loaded: {e}"}
    import base64 as _b64
    cfg = V.lesson_cfg(V.load_config(), payload.get("id"))
    items = V.narration_items(payload)
    out, size = {}, 0
    for key, text in items:
        f = V.cache_path(text, cfg)
        if os.path.isfile(f) and os.path.getsize(f) > 0:
            raw = open(f, "rb").read()
            if V.is_mp3(raw):
                out[key] = _b64.b64encode(raw).decode("ascii")
                size += len(raw)
    return out, {"lines": len(items), "embedded": len(out), "bytes": size}


def render_player(lesson, build_info):
    media = {"video": build_info.get("video"), "video_kind": build_info.get("video_kind"),
             "clip": build_info.get("clip"), "clip_label": build_info.get("clip_label")}
    data = learner_payload(lesson, media)
    build_info["voice_b64"], build_info["voice_stats"] = resolve_voice(data)
    blob = json.dumps(data, ensure_ascii=False)
    # Embed the call audio in the page itself: TalentLMS's SCORM CDN does not stream packaged audio
    # (verified live 2026-09-28 — the player sat at 0:00 with both .m4a and .mp3). A blob URL built from
    # this inline base64 always plays. The file stays in the zip as a fallback.
    clip_b64 = ""
    if build_info.get("clip_path") and os.path.isfile(build_info["clip_path"]):
        import base64 as _b64
        clip_b64 = _b64.b64encode(open(build_info["clip_path"], "rb").read()).decode("ascii")
    voice_json = json.dumps(build_info.get("voice_b64") or {}, separators=(",", ":"))
    # keep the JSON inert inside <script>
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\!--").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return (PLAYER_HTML
            .replace("__CSS__", PLAYER_CSS + FRAME_FIT_CSS)
            .replace("__SPRITE__", icon_sprite())
            .replace("__TITLE__", html_escape(f"{lesson['id']} {learner_text(lesson.get('title', ''))} | Valley Pawn Academy"))
            .replace("__ID__", html_escape(lesson["id"]))
            .replace("__LESSON__", blob + '</script>\n<script type="text/plain" id="clip-b64">' + clip_b64
                     + '</script>\n<script type="application/json" id="voice-b64">' + voice_json)
            .replace("__JS__", PLAYER_JS))


# --------------------------------------------------------------------------- build
def level_label(level):
    """Display name for a level: level 9 is the manager track."""
    return "Manager Track" if level == 9 else f"Level {level}"


def slug_for(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"^\d+_", "", stem)


def find_logo():
    for c in LOGO_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def build_one(path):
    with open(path, encoding="utf-8") as f:
        lesson = json.load(f)
    warnings = lint_lesson(lesson, path)
    info, copy, notes = resolve_media(lesson)
    logo = find_logo()
    if not logo:
        notes.append("logo not found - header shows alt text")
    lid = lesson["id"]
    name = f"{lid}_{slug_for(path)}"
    os.makedirs(DIST, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        files = ["index.html"]
        with open(os.path.join(tmp, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_player(lesson, info))
        if logo:
            shutil.copyfile(logo, os.path.join(tmp, "logo.png"))
            files.append("logo.png")
        for pkg, src in copy.items():
            dst = os.path.join(tmp, pkg)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            files.append(pkg)
        with open(os.path.join(tmp, "imsmanifest.xml"), "w", encoding="utf-8") as f:
            f.write(make_manifest(lesson, files))

        zpath = os.path.join(DIST, name + ".zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(os.path.join(tmp, "imsmanifest.xml"), "imsmanifest.xml")  # manifest at root, first
            for rel in files:
                ctype = zipfile.ZIP_STORED if rel.startswith("media/") else zipfile.ZIP_DEFLATED
                z.write(os.path.join(tmp, rel), rel, compress_type=ctype)

        # Preview: overwrite in place (some synced folders refuse directory deletes), then
        # best-effort removal of files that are no longer part of the package.
        pdir = os.path.join(PREVIEW, lid)
        keep = set(files) | {"imsmanifest.xml"}
        for rel in keep:
            dst = os.path.join(pdir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(os.path.join(tmp, rel), "rb") as s, open(dst, "wb") as d:
                shutil.copyfileobj(s, d)
        for dp, _, fns in os.walk(pdir):
            for fn in fns:
                rel = os.path.relpath(os.path.join(dp, fn), pdir).replace(os.sep, "/")
                if rel not in keep:
                    try:
                        os.remove(os.path.join(dp, fn))
                    except OSError:
                        notes.append(f"preview: stale file {rel} could not be removed")

    entry = {
        "id": lid, "title": lesson.get("title"), "level": lesson.get("level"), "level_label": level_label(lesson.get("level")), "order": lesson.get("order"),
        "package": os.path.basename(zpath), "preview": f"preview/{lid}/index.html", "source": os.path.relpath(path, ACADEMY),
        "minutes": lesson.get("minutes"), "question_count": len(usable_questions(lesson)),
        "pass_percent": (lesson.get("quiz") or {}).get("pass_percent", 80),
        "max_attempts": (lesson.get("quiz") or {}).get("max_attempts", 2),
        "has_video": bool(info["video"]), "has_call_clip": bool(info["clip"]), "call_clip": info["clip"],
        "call_clip_seconds": info["clip_seconds"], "floor_check": bool(lesson.get("floor_check")),
        "voiceover_lines": (info.get("voice_stats") or {}).get("embedded", 0),
        "narration_lines": (info.get("voice_stats") or {}).get("lines", 0),
        "package_bytes": os.path.getsize(zpath),
        "media_notes": notes, "spec_warnings": warnings,
    }
    vs = info.get("voice_stats") or {}
    if vs.get("note"):
        notes.append(vs["note"])
    elif vs.get("embedded"):
        missing = vs["lines"] - vs["embedded"]
        notes.append(f"voiceover: {vs['embedded']}/{vs['lines']} lines embedded ({vs['bytes'] // 1024} KB mp3)"
                     + (f"; {missing} not generated yet -> browser speech for those slides" if missing else ""))
    return entry


def write_index(entries, replace_all):
    existing = {}
    if not replace_all and os.path.isfile(INDEX_PATH):
        try:
            with open(INDEX_PATH, encoding="utf-8") as f:
                existing = {e["id"]: e for e in json.load(f).get("packages", [])}
        except Exception:
            existing = {}
    for e in entries:
        existing[e["id"]] = e
    pk = sorted(existing.values(), key=lambda e: (e.get("level") or 0, e.get("order") or 0, e["id"]))
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump({"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "scorm_version": "1.2", "count": len(pk), "packages": pk}, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- validate
NODE_TEST = r"""
const fs = require('fs'); const vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const js = html.match(/<script id="player">([\s\S]*?)<\/script>/)[1];
const lesson = JSON.parse(html.match(/<script type="application\/json" id="lesson-data">([\s\S]*?)<\/script>/)[1]);
function fakeAPI(initial) {
  const store = Object.assign({}, initial || {}); const calls = [];
  return { store, calls,
    LMSInitialize(){calls.push('init'); return 'true';}, LMSFinish(){calls.push('finish'); return 'true';},
    LMSGetValue(k){return store[k] || '';}, LMSSetValue(k,v){store[k]=v; return 'true';},
    LMSCommit(){calls.push('commit'); return 'true';}, LMSGetLastError(){return '0';}, LMSGetErrorString(){return '';}, LMSGetDiagnostic(){return '';} };
}
function load(api) {
  const win = { API: api, console: { log(){} } }; win.parent = win; win.window = win;
  const ctx = vm.createContext({ window: win, console: { log(){} }, Date, Math, JSON, String, Object });
  vm.runInContext(js, ctx);
  return win.VP;
}
function run(mode, initial) {
  const api = fakeAPI(initial); const VP = load(api);
  const s = new VP.Scorm(api ? { API: api, parent: null } : {}); s.init();
  if (api.store['cmi.core.lesson_status'] !== 'incomplete' && !(initial && initial['cmi.core.lesson_status'] === 'passed')) throw new Error('status not incomplete at start');
  const st = VP.readState(s); const q = new VP.Quiz(lesson);
  if (q.items.length !== lesson.quiz.questions.length) throw new Error('question count mismatch');
  for (let i = 0; i < q.items.length; i++) {
    const it = q.current(); let idx = it.options.findIndex(o => o.correct);
    if (mode === 'wrong') idx = it.options.findIndex(o => !o.correct);
    if (idx < 0) throw new Error('no option for mode ' + mode + ' on: ' + it.prompt);
    const r = q.answer(idx); if (r.correct !== (mode === 'right')) throw new Error('grading wrong');
    if (!r.correctOpt) throw new Error('missing correct option');
    q.next();
  }
  const res = q.result(); const status = VP.recordAttempt(s, st, res); s.finish();
  return { api, res, status };
}
const out = {};
let a = run('right');
if (a.res.score !== 100 || a.status !== 'passed' || a.api.store['cmi.core.lesson_status'] !== 'passed' || a.api.store['cmi.core.score.raw'] !== '100') throw new Error('all-correct did not pass: ' + JSON.stringify(a.api.store));
if (a.api.store['cmi.core.score.min'] !== '0' || a.api.store['cmi.core.score.max'] !== '100') throw new Error('min/max not set');
if (JSON.parse(a.api.store['cmi.suspend_data']).a !== 1) throw new Error('attempt count not in suspend_data');
if (!a.api.calls.includes('finish') || !a.api.calls.includes('commit')) throw new Error('commit/finish not called');
out.allCorrect = { score: a.res.score, status: a.status };
let b = run('wrong');
if (b.res.score !== 0 || b.status !== 'failed' || b.api.store['cmi.core.lesson_status'] !== 'failed' || b.api.store['cmi.core.score.raw'] !== '0') throw new Error('all-wrong did not fail: ' + JSON.stringify(b.api.store));
out.allWrong = { score: b.res.score, status: b.status };
let c = run('wrong', { 'cmi.suspend_data': JSON.stringify({ a: 2, b: 50, p: false }) });
if (JSON.parse(c.api.store['cmi.suspend_data']).a !== 3) throw new Error('attempts did not accumulate');
out.attemptsAccumulate = 3;
// shuffle sanity: every item keeps exactly its options and one correct answer
const VP = load(fakeAPI()); const q2 = new VP.Quiz(lesson);
q2.items.forEach(it => { if (!it.options.some(o => o.correct)) throw new Error('shuffle lost correct'); });
// standalone mode: no API anywhere -> no throw
const win = { console: { log(){} } }; win.parent = win;
const ctx = vm.createContext({ window: win, console: { log(){} }, Date, Math, JSON, String, Object }); vm.runInContext(js, ctx);
const s2 = new win.VP.Scorm(win); s2.init(); win.VP.recordAttempt(s2, win.VP.readState(s2), { score: 100, passed: true }); s2.finish();
out.standalone = 'ok';
console.log(JSON.stringify(out));
"""


LEARNER_KEYS = {"id", "title", "level_label", "minutes", "gate", "icon", "slides", "call_clip",
                "key_points", "floor_check", "quiz", "media"}


def validate(zips):
    node = shutil.which("node")
    results, all_ok = [], True
    ns = {"i": "http://www.imsproject.org/xsd/imscp_rootv1p1p2", "a": "http://www.adlnet.org/xsd/adlcp_rootv1p2"}
    with tempfile.TemporaryDirectory() as tmp:
        test_js = os.path.join(tmp, "quiz_test.js")
        with open(test_js, "w") as f:
            f.write(NODE_TEST)
        for zp in zips:
            errs, info = [], {}
            name = os.path.basename(zp)
            try:
                with zipfile.ZipFile(zp) as z:
                    names = set(z.namelist())
                    if "imsmanifest.xml" not in names:
                        raise ValueError("imsmanifest.xml not at zip root")
                    root = ET.fromstring(z.read("imsmanifest.xml"))
                    if root.tag != "{%s}manifest" % ns["i"]:
                        errs.append("root element is not IMS CP manifest")
                    if (root.findtext("i:metadata/i:schema", namespaces=ns) or "") != "ADL SCORM":
                        errs.append("metadata/schema != ADL SCORM")
                    if (root.findtext("i:metadata/i:schemaversion", namespaces=ns) or "") != "1.2":
                        errs.append("schemaversion != 1.2")
                    orgs = root.find("i:organizations", ns)
                    default = orgs.get("default") if orgs is not None else None
                    org = root.find(f"i:organizations/i:organization[@identifier='{default}']", ns)
                    if org is None:
                        errs.append("default organization not found")
                    items = org.findall(".//i:item", ns) if org is not None else []
                    if not items:
                        errs.append("no item")
                    reses = {r.get("identifier"): r for r in root.findall("i:resources/i:resource", ns)}
                    for it in items:
                        r = reses.get(it.get("identifierref"))
                        if r is None:
                            errs.append(f"item {it.get('identifier')} -> missing resource")
                            continue
                        if r.get("{%s}scormtype" % ns["a"]) != "sco":
                            errs.append("resource scormtype != sco")
                        if r.get("type") != "webcontent":
                            errs.append("resource type != webcontent")
                        href = r.get("href")
                        if href not in names:
                            errs.append(f"launch href {href} missing from zip")
                        for fe in r.findall("i:file", ns):
                            if fe.get("href") not in names:
                                errs.append(f"file {fe.get('href')} listed but not in zip")
                    html = z.read("index.html").decode("utf-8")
                    for ref in re.findall(r'(?:src|href)="([^"#:]+)"', html):
                        if ref not in names:
                            errs.append(f"index.html references {ref} not in zip")
                    lesson = json.loads(re.search(r'<script type="application/json" id="lesson-data">(.*?)</script>', html, re.S).group(1))
                    media = lesson.get("media") or {}
                    for key in ("video", "clip"):
                        p = media.get(key)
                        if p and not re.match(r"^https?://", p) and p not in names:
                            errs.append(f"{key} {p} not in zip")
                    if re.search(r'(src|href)="https?://', html):
                        errs.append("index.html loads a remote resource")
                    # call clip: MP3 only, neutral name, real MPEG audio, played as audio/mpeg
                    clip = media.get("clip")
                    if clip:
                        if not re.fullmatch(r"media/[A-Za-z0-9-]+_call\.mp3", clip):
                            errs.append(f"clip {clip} is not media/<lessonId>_call.mp3")
                        elif clip in names:
                            head = z.read(clip)[:4]
                            if not (head[:3] == b"ID3" or (len(head) > 1 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0)):
                                errs.append(f"clip {clip} is not MPEG audio")
                        if "'audio/mpeg'" not in html:
                            errs.append("player does not declare the clip as audio/mpeg")
                        info["clip"] = clip
                    for n in names:
                        if n.startswith("media/") and not re.fullmatch(r"media/[A-Za-z0-9-]+_(call\.mp3|video\.[a-z0-9]+)", n):
                            errs.append(f"media file with a non-neutral name: {n}")
                        if re.search(r"\.(m4a|aac)$", n, re.I):
                            errs.append(f"AAC/m4a audio shipped: {n}")
                    # voiceover: optional JSON map {key: base64 MP3}; every entry must decode to MP3 bytes
                    vm_ = re.search(r'<script type="application/json" id="voice-b64">(.*?)</script>', html, re.S)
                    if vm_:
                        import base64 as _b64
                        try:
                            vmap = json.loads(vm_.group(1) or "{}")
                            if not isinstance(vmap, dict):
                                raise ValueError("not an object")
                        except ValueError as ve:
                            errs.append(f"voice-b64 is not valid JSON: {ve}")
                            vmap = {}
                        n_slides = len([s for s in lesson.get("slides") or [] if s and (s.get("heading") or s.get("bullets"))])
                        for k, b in vmap.items():
                            if not (k in ("intro", "keypoints") or (k.isdigit() and int(k) < n_slides)):
                                errs.append(f"voice-b64 has an unexpected key {k!r}")
                            try:
                                raw = _b64.b64decode(b, validate=True)
                            except Exception:  # noqa
                                errs.append(f"voice-b64[{k}] is not valid base64")
                                continue
                            if not (raw[:3] == b"ID3" or (len(raw) > 1 and raw[0] == 0xFF and (raw[1] & 0xE0) == 0xE0)):
                                errs.append(f"voice-b64[{k}] is not MP3 audio")
                        info["voice_lines"] = len(vmap)
                    else:
                        info["voice_lines"] = "no voice-b64 block (older build)"
                    # learner-facing text: no internal references, no build data, no "coming soon"
                    scan = re.sub(r'<script type="text/plain" id="clip-b64">[A-Za-z0-9+/=\s]*', '', html)
                    scan = re.sub(r'<script type="application/json" id="voice-b64">.*?</script>', '', scan, flags=re.S)
                    for pname, hit in forbidden_hits(scan):
                        errs.append(f"forbidden text in index.html [{pname}]: {hit!r}")
                    for key in ("sources", "production_notes", "_build"):
                        if key in lesson or f'"{key}"' in html:
                            errs.append(f"index.html embeds '{key}'")
                    extra = set(lesson) - LEARNER_KEYS
                    if extra:
                        errs.append(f"non-learner fields embedded: {sorted(extra)}")
                    info["questions"] = len(lesson["quiz"]["questions"])
                    ex = os.path.join(tmp, name)
                    os.makedirs(ex, exist_ok=True)
                    z.extractall(ex)
                if node:
                    js = re.search(r'<script id="player">(.*?)</script>', html, re.S).group(1)
                    jsf = os.path.join(ex, "player.js")
                    with open(jsf, "w", encoding="utf-8") as f:
                        f.write(js)
                    p = subprocess.run([node, "--check", jsf], capture_output=True, text=True)
                    if p.returncode:
                        errs.append("node --check: " + p.stderr.strip()[:400])
                    else:
                        info["syntax"] = "ok"
                    p = subprocess.run([node, test_js, os.path.join(ex, "index.html")], capture_output=True, text=True)
                    if p.returncode:
                        errs.append("quiz test: " + (p.stderr.strip().splitlines() or ["?"])[0][:400])
                    else:
                        info["quiz_test"] = json.loads(p.stdout.strip().splitlines()[-1])
                else:
                    info["syntax"] = info["quiz_test"] = "skipped (node not found)"
            except Exception as e:  # noqa
                errs.append(f"{type(e).__name__}: {e}")
            ok = not errs
            all_ok &= ok
            results.append({"package": name, "ok": ok, "errors": errs, **info})
    return all_ok, results


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Build Valley Pawn Academy SCORM 1.2 packages")
    ap.add_argument("lesson", nargs="*", help="lesson JSON path(s)")
    ap.add_argument("--all", action="store_true", help="build every lessons/*/*.json (L1-L8 and M)")
    ap.add_argument("--skip-validate", action="store_true")
    ap.add_argument("--validate-only", action="store_true", help="validate the zips already in dist/")
    a = ap.parse_args()

    if a.validate_only:
        zips = sorted(glob.glob(os.path.join(DIST, "*.zip")))
    else:
        paths = sorted(glob.glob(os.path.join(LESSONS_DIR, "*", "*.json"))) if a.all else a.lesson
        if not paths:
            ap.error("give a lesson JSON path or --all")
        entries, zips, failed = [], [], []
        for p in paths:
            try:
                e = build_one(os.path.abspath(p))
            except Exception as ex:  # a broken JSON file must not stop the rest
                failed.append((p, f"{type(ex).__name__}: {ex}"))
                print(f"FAILED  {p}: {type(ex).__name__}: {ex}")
                continue
            entries.append(e)
            zips.append(os.path.join(DIST, e["package"]))
            flag = f"  [{len(e['spec_warnings'])} spec warnings]" if e["spec_warnings"] else ""
            print(f"built   {e['package']}  ({e['question_count']} Qs, {e['package_bytes'] / 1048576:.1f} MB){flag}")
            for n in e["media_notes"]:
                print(f"        media: {n}")
            for w in e["spec_warnings"]:
                print(f"        spec:  {w}")
        write_index(entries, replace_all=a.all)
        print(f"\n{len(entries)} package(s) -> {DIST}\nindex  -> {INDEX_PATH}")
        if entries:
            big = max(entries, key=lambda e: e["package_bytes"])
            print(f"largest package: {big['package']} {big['package_bytes'] / 1048576:.1f} MB")
        if failed:
            print(f"{len(failed)} lesson(s) could not be built")
        if a.skip_validate:
            return 1 if failed else 0

    ok, results = validate(zips)
    print("\nValidation:")
    for r in results:
        if r["ok"]:
            qt = r.get("quiz_test")
            qs = f"all-correct {qt['allCorrect']['status']} {qt['allCorrect']['score']} / all-wrong {qt['allWrong']['status']} {qt['allWrong']['score']}" if isinstance(qt, dict) else qt
            vl = r.get("voice_lines")
            vs = f", voiceover {vl} lines" if isinstance(vl, int) and vl else ""
            print(f"  PASS  {r['package']}  manifest ok, files ok, syntax {r.get('syntax')}, {qs}{vs}")
        else:
            print(f"  FAIL  {r['package']}")
            for e in r["errors"]:
                print(f"        - {e}")
    print("ALL GREEN" if ok else "VALIDATION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
