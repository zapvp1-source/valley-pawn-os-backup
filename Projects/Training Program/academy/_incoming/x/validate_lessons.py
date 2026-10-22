#!/usr/bin/env python3
"""
Valley Pawn Academy - lesson JSON validator (review board, seat C).

Checks every lessons/L*/*.json against LESSON_SPEC.md plus the stricter rules the board asked for.
Also runs every learner-facing string through build_scorm.learner_text() and reports what would
still leak into the package (citations, dates, attributions, employee names).

    python3 -I validate_lessons.py [--academy /path/to/academy] [--json out.json]

Exit code 0 when there are no violations (warnings do not fail).
"""
import argparse
import glob
import json
import os
import re
import sys

ap = argparse.ArgumentParser()
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ACADEMY = _HERE if os.path.isdir(os.path.join(_HERE, "lessons")) else os.path.dirname(_HERE)
ap.add_argument("--academy", default=_DEFAULT_ACADEMY)
ap.add_argument("--json", help="write the full violation list as JSON here")
ap.add_argument("--quiet", action="store_true")
A = ap.parse_args()

ACADEMY = os.path.abspath(A.academy)
sys.path.insert(0, ACADEMY)
try:
    import build_scorm as B
    learner_text = B.learner_text
    forbidden_hits = B.forbidden_hits
except Exception as e:  # noqa
    print(f"WARN build_scorm.py not importable ({e}); post-filter leak checks skipped")
    learner_text = lambda s, keep_policy=False: s  # noqa
    forbidden_hits = lambda s: []  # noqa

VALID_TYPES = {"scenario", "mc", "truefalse"}
LEVEL_DIR_RX = re.compile(r"^(?:L(\d+)|M)$")
FILE_RX = re.compile(r"^(\d\d)_[a-z0-9_]+\.json$")

# ---- learner-facing text rules
ATTRIBUTION_RX = re.compile(r"\b(?:Preston|Joshua|Hillary|Sandi|Lainie|the CEO|the Market Manager)(?: [A-Z][a-z]+)? (?:says|said|told us|wants|asked for|decided|ruled|confirmed|announced)\b", re.I)
# hard: ISO dates anywhere; rule-dating phrases anywhere; "last week/month" in narration, bullets, key points and why
DATE_HARD_RX = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\bstarting (?:in |on )?(?:January|February|March|April|May|June|July|August|September|October|November|December)\b|\b(?:as of|since|from) (?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d{1,2})?\b|\bOctober 1(?:st)?\b|\bOct\.? 1\b|\bin October\b|\bnew (?:rule|policy) (?:as of|since)\b", re.I)
DATE_SOFT_RX = re.compile(r"\b(?:last (?:week|month|year)|earlier this (?:week|month|year)|recently (?:changed|decided|announced))\b", re.I)
YEAR_RX = re.compile(r"\b20[2-3]\d\b")
# names appearing in OPEN_ITEMS / HUDDLE_INPUTS / review notes as employees or coaching-call subjects
EMPLOYEE_NAMES = ["Burnett", "Benjie", "Jacob Cox", "Camden", "Ahern", "Logan", "Chadd", "Epperly", "Sandi", "Cole", "Lainie"]
# people who are legitimately "the one to call" (spec): reported as notes, never violations
CALL_CHAIN_NAMES = re.compile(r"\bHillary\b")
NAME_RX = re.compile(r"\b(?:" + "|".join(re.escape(n) for n in EMPLOYEE_NAMES) + r")\b")
# names allowed only as "the person to call / approver" (spec). We still report every hit so a human can judge.
APPROVER_NAMES = re.compile(r"\b(?:Preston|Joshua)\b")
# bare "Handbook" / "P&P" are legitimate learner words (the documents are taught); section marks and memo ids are citations
CITATION_RX = re.compile(r"§|P&P v|Handbook v|\bKB\b|zoom-call|[Hh]uddle \d|\d+/\d+ huddle|[Hh]uddle(?:s)? (?:were|was|said|decided|input)|\bHR-\d{4}-\d{2}\b|\bOB-\d{4}-\d{2}\b|Master Plan|\bCall ?\d{2,3}\b|\bv20\d\d\.\d\b|POLICY_GAPS|\bOPEN\b|\bTODO\b|see sources|\bCEO greeting script\b|coaching call|Preston-to-")
BULLET_RX = re.compile(r"^\s*[-*•·]|\n\s*[-*•·]|[•·]|\*\*|^#+\s|`|\[[^\]]*\]\([^)]*\)")
CHANNEL_RX = re.compile(r"#[a-z][a-z0-9-]+")
MONEY_RX = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")
URL_RX = re.compile(r"https?://\S+|\b[a-z0-9-]+\.(?:com|net|org|io)\b", re.I)

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")


def sentences(t):
    t = str(t or "").strip()
    if not t:
        return []
    return [s for s in SENT_SPLIT.split(t) if s.strip()]


def n_sentences(t):
    # count terminal punctuation groups; abbreviations like "P&P §01.06." inflate slightly, so we also cap by splitter
    return len(sentences(t))


violations, warnings, notes = [], [], []
n_shortest = n_nontf = 0
channels, money, urls, clips = {}, {}, {}, []
level_ids = {}


def V(lid, field, msg):
    violations.append((lid, field, msg))


def W(lid, field, msg):
    warnings.append((lid, field, msg))


paths = sorted(glob.glob(os.path.join(ACADEMY, "lessons", "*", "*.json")))
if not paths:
    sys.exit(f"no lessons under {ACADEMY}/lessons")

all_ids = {}
for path in paths:
    rel = os.path.relpath(path, ACADEMY)
    folder = os.path.basename(os.path.dirname(path))
    fname = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:  # noqa
        V(rel, "file", f"JSON does not parse: {e}")
        continue
    lid = d.get("id") or rel

    # ---- ids / numbering
    m = LEVEL_DIR_RX.match(folder)
    fm = FILE_RX.match(fname)
    if not m:
        V(lid, "folder", f"folder {folder!r} is not L<n> or M")
    if not fm:
        V(lid, "file", f"filename {fname!r} is not nn_slug.json")
    want_level = (int(m.group(1)) if m and m.group(1) else 9) if m else None
    want_order = int(fm.group(1)) if fm else None
    want_id = (f"L{want_level}-{want_order:02d}" if want_level != 9 else f"M-{want_order:02d}") if (m and fm) else None
    if want_id and lid != want_id:
        V(lid, "id", f"id {lid!r} but folder/file say {want_id!r}")
    if d.get("level") != want_level:
        V(lid, "level", f"level={d.get('level')!r} but folder {folder} => {want_level}")
    if d.get("order") != want_order:
        V(lid, "order", f"order={d.get('order')!r} but file prefix => {want_order}")
    if lid in all_ids:
        V(lid, "id", f"duplicate id (also {all_ids[lid]})")
    all_ids[lid] = rel
    level_ids.setdefault(want_level, []).append(want_order)

    # ---- required fields
    for k in ("id", "level", "order", "title", "minutes", "sources", "objectives", "video", "slides", "key_points", "quiz"):
        if k not in d:
            V(lid, k, "missing required field")
    if not isinstance(d.get("minutes"), (int, float)) or not d.get("minutes"):
        V(lid, "minutes", f"minutes={d.get('minutes')!r} (must be a positive number)")
    obj = str(d.get("objectives") or "").strip()
    if not obj:
        V(lid, "objectives", "empty")
    else:
        ns = n_sentences(obj)
        if ns != 1:
            V(lid, "objectives", f"{ns} sentences (spec: one sentence): {obj[:90]!r}")
        if len(obj) > 260:
            W(lid, "objectives", f"{len(obj)} chars; long for the Start card and the spoken intro")
    src = d.get("sources")
    if not isinstance(src, list) or not src or not all(str(s).strip() for s in src):
        V(lid, "sources", "must be a non-empty list of non-empty strings")

    # ---- media: exactly one of video.file / video.url / slides
    v = d.get("video")
    vf = vu = None
    if isinstance(v, dict):
        vf, vu = v.get("file"), v.get("url")
    elif v not in (None,):
        V(lid, "video", f"video must be an object or null, got {type(v).__name__}")
    slides = d.get("slides") or []
    n_media = int(bool(vf)) + int(bool(vu)) + int(bool(slides))
    if n_media == 0:
        V(lid, "video/slides", "no video.file, no video.url and no slides")
    if vf and vu:
        V(lid, "video", "both video.file and video.url set (spec: exactly one)")
    if (vf or vu) and slides:
        W(lid, "video", "video set AND slides present (builder uses the video; slides are then never shown or narrated)")

    # ---- slides
    if not slides:
        V(lid, "slides", "no slides")
    for i, s in enumerate(slides, 1):
        tag = f"slide {i}"
        if not isinstance(s, dict):
            V(lid, tag, "not an object")
            continue
        if not str(s.get("heading") or "").strip():
            V(lid, tag, "no heading")
        bl = s.get("bullets") or []
        if len(bl) > 6:
            V(lid, tag, f"{len(bl)} bullets (max 6)")
        if len(bl) == 0:
            W(lid, tag, "no bullets")
        say = str(s.get("say") or "").strip()
        if not say:
            V(lid, tag + ".say", "empty narration")
        else:
            ns = n_sentences(say)
            if ns > 4:
                W(lid, tag + ".say", f"{ns} sentences (spec: 2-4)")
            if ns < 2:
                W(lid, tag + ".say", f"{ns} sentence (spec: 2-4)")
            if BULLET_RX.search(say):
                V(lid, tag + ".say", f"bullet/markdown character in narration: {say[:80]!r}")
            if "\n" in say:
                V(lid, tag + ".say", "line break in narration")

    # ---- key points
    kp = d.get("key_points") or []
    if not (3 <= len(kp) <= 7):
        V(lid, "key_points", f"{len(kp)} items (board rule 3-7; builder lint 3-6)")
    elif len(kp) == 7:
        W(lid, "key_points", "7 items (builder lint warns above 6)")

    # ---- call clip
    clip = d.get("call_clip")
    if isinstance(clip, dict) and clip.get("file"):
        clips.append((lid, clip["file"]))
        if not clip.get("listen_for"):
            V(lid, "call_clip", "no listen_for")
        if not str(clip.get("caption") or "").strip():
            W(lid, "call_clip", "no caption")

    # ---- quiz
    q = d.get("quiz") or {}
    qs = q.get("questions") or []
    is_intro = d.get("order") == 0
    pp = q.get("pass_percent")
    if is_intro:
        if pp != 0:
            V(lid, "quiz.pass_percent", f"{pp!r} (intros must be 0)")
        if not (2 <= len(qs) <= 5):
            V(lid, "quiz", f"{len(qs)} questions (intros: 2-5)")
    else:
        if pp != 80:
            V(lid, "quiz.pass_percent", f"{pp!r} (must be 80)")
        if not (6 <= len(qs) <= 9):
            V(lid, "quiz", f"{len(qs)} questions (6-9)")
        n_scen = sum(1 for x in qs if x.get("type") == "scenario")
        if n_scen < 4:
            V(lid, "quiz", f"only {n_scen} scenario questions (min 4)")
        if len(qs) == 9 and not any(x.get("goldilocks") for x in qs):
            W(lid, "quiz", "9 questions but none marked goldilocks:true (spec allows 9 only with the tie-in)")
    if q.get("max_attempts") != 2:
        V(lid, "quiz.max_attempts", f"{q.get('max_attempts')!r} (must be 2)")
    if q.get("shuffle") is not True:
        V(lid, "quiz.shuffle", f"{q.get('shuffle')!r} (must be true)")
    seen_prompts = set()
    for qi, x in enumerate(qs, 1):
        tag = f"Q{qi}"
        if x.get("type") not in VALID_TYPES:
            V(lid, tag, f"type {x.get('type')!r}")
        prompt = str(x.get("prompt") or "").strip()
        if not prompt:
            V(lid, tag, "empty prompt")
        if prompt.lower() in seen_prompts:
            V(lid, tag, "duplicate prompt within lesson")
        seen_prompts.add(prompt.lower())
        opts = x.get("options") or []
        if len(opts) < 2:
            V(lid, tag, f"{len(opts)} options")
        nc = [o for o in opts if o.get("correct") is True]
        if len(nc) != 1:
            V(lid, tag, f"{len(nc)} options marked correct (must be exactly 1)")
        if x.get("type") == "truefalse" and len(opts) != 2:
            V(lid, tag, f"truefalse with {len(opts)} options")
        texts = []
        for oi, o in enumerate(opts, 1):
            t = str(o.get("text") or "").strip()
            if not t:
                V(lid, f"{tag} opt{oi}", "empty text")
            if not str(o.get("why") or "").strip():
                V(lid, f"{tag} opt{oi}", "empty why")
            if "correct" not in o:
                V(lid, f"{tag} opt{oi}", "no 'correct' flag")
            texts.append(t.lower())
        if len(set(texts)) != len(texts):
            V(lid, tag, "duplicate option text")
        if len(nc) == 1 and x.get("type") != "truefalse" and opts:
            L = [len(str(o.get("text") or "")) for o in opts]
            ci = opts.index(nc[0])
            if L[ci] == max(L) and L.count(max(L)) == 1:
                V(lid, tag, f"correct option is the longest ({L[ci]} chars vs {sorted(L)[-2]})")
            n_nontf += 1
            if L[ci] == min(L) and L.count(min(L)) == 1:
                n_shortest += 1

    # ---- learner-facing text scan (pre- and post-filter)
    fields = [("title", d.get("title")), ("objectives", d.get("objectives")), ("gate", d.get("gate")), ("floor_check", d.get("floor_check"))]
    for i, s in enumerate(slides, 1):
        if isinstance(s, dict):
            fields.append((f"slide {i}.heading", s.get("heading")))
            fields.append((f"slide {i}.say", s.get("say")))
            for bi, b in enumerate(s.get("bullets") or [], 1):
                fields.append((f"slide {i}.bullet {bi}", b))
    for ki, k in enumerate(kp, 1):
        fields.append((f"key_point {ki}", k))
    if isinstance(clip, dict):
        fields.append(("call_clip.caption", clip.get("caption")))
        for li, l in enumerate(clip.get("listen_for") or [], 1):
            fields.append((f"call_clip.listen_for {li}", l))
    for qi, x in enumerate(qs, 1):
        fields.append((f"Q{qi}.prompt", x.get("prompt")))
        for oi, o in enumerate(x.get("options") or [], 1):
            fields.append((f"Q{qi} opt{oi}.text", o.get("text")))
            fields.append((f"Q{qi} opt{oi}.why", o.get("why")))
    for fname_, raw in fields:
        if not isinstance(raw, str) or not raw.strip():
            continue
        is_why = fname_.endswith(".why")
        shipped = learner_text(raw, keep_policy=is_why)
        narr = fname_.endswith((".say", ".why")) or ".bullet" in fname_ or fname_.startswith("key_point") or fname_ in ("objectives", "gate", "floor_check")
        for mm in ATTRIBUTION_RX.finditer(shipped):
            if re.search(r"Joshua confirmed '?Sent", shipped):
                notes.append((lid, fname_, "accepted: 'Joshua confirmed Sent' describes the Slack reply, not an attribution"))
                continue
            V(lid, fname_, f"attribution {mm.group(0)!r} ships (spec: company voice, never 'X says')")
        for mm in DATE_HARD_RX.finditer(shipped):
            V(lid, fname_, f"dated text ships: {mm.group(0)!r} in {shipped[:110]!r}")
        if narr:
            for mm in DATE_SOFT_RX.finditer(shipped):
                # accepted by the board 2026-10-20: "last month's interest", "numbers vs last week" are arithmetic/periodic, not dated rules
                notes.append((lid, fname_, f"relative-time phrase {mm.group(0)!r} (accepted; re-check if it dates a rule): {shipped[:90]!r}"))
            for mm in YEAR_RX.finditer(shipped):
                W(lid, fname_, f"year {mm.group(0)!r} in explanatory text (will rot): {shipped[:100]!r}")
        for mm in NAME_RX.finditer(shipped):
            V(lid, fname_, f"employee/family name ships: {mm.group(0)!r} in {shipped[:100]!r}")
        for mm in CALL_CHAIN_NAMES.finditer(shipped):
            notes.append((lid, fname_, f"call-chain name {mm.group(0)!r} (accepted: the person to call)"))
        for mm in CITATION_RX.finditer(shipped):
            if is_why and re.match(r"§|P&P v|Handbook v|HR-|OB-", mm.group(0)):
                notes.append((lid, fname_, f"citation kept in why (by design): {mm.group(0)!r}"))
            else:
                V(lid, fname_, f"SHIPS to learner after filter: {mm.group(0)!r} in {shipped[:110]!r}")
        for name, hit in forbidden_hits(shipped):
            V(lid, fname_, f"builder FORBIDDEN_PATTERN [{name}] would fail the package: {hit!r}")
        for mm in CHANNEL_RX.finditer(shipped):
            channels.setdefault(mm.group(0), set()).add(lid)
        for mm in MONEY_RX.finditer(shipped):
            money.setdefault(mm.group(0), set()).add(lid)
        for mm in URL_RX.finditer(shipped):
            urls.setdefault(mm.group(0), set()).add(lid)
        if fname_.endswith(".say") and shipped != raw.strip():
            notes.append((lid, fname_, "narration text differs from JSON after filter (TTS cache keyed on the filtered text)"))

# ---- ordering within each level
for lv, orders in level_ids.items():
    orders = sorted(orders)
    want = list(range(0, len(orders)))
    if orders != want:
        V(f"L{lv}" if lv != 9 else "M", "numbering", f"orders present {orders}; expected contiguous 0..{len(orders) - 1}")

# ---- report
print(f"Lessons checked: {len(all_ids)} files under {ACADEMY}/lessons")
print(f"VIOLATIONS: {len(violations)}   warnings: {len(warnings)}   notes: {len(notes)}")
print(f"note: correct option is strictly the SHORTEST on {n_shortest} of {n_nontf} non-true/false questions ({100 * n_shortest / max(n_nontf, 1):.0f}%)")
by_kind = {}
for lid, f, msg in violations:
    k = msg.split(" ")[0] if not msg.startswith("SHIPS") else "SHIPS"
    by_kind[k] = by_kind.get(k, 0) + 1
if not A.quiet:
    print("\n== VIOLATIONS ==")
    for lid, f, msg in violations:
        print(f"  {lid:<6} {f:<28} {msg}")
    print("\n== WARNINGS ==")
    for lid, f, msg in warnings:
        print(f"  {lid:<6} {f:<28} {msg}")
    print("\n== Channel names in learner text ==")
    for k, v in sorted(channels.items()):
        print(f"  {k:<28} {len(v)} lessons: {', '.join(sorted(v))}")
    print("\n== Dollar figures in learner text ==")
    for k, v in sorted(money.items(), key=lambda kv: -len(kv[1]))[:40]:
        print(f"  {k:<12} {len(v)} lessons: {', '.join(sorted(v)[:12])}")
    print("\n== URLs / domains in learner text ==")
    for k, v in sorted(urls.items()):
        print(f"  {k:<36} {', '.join(sorted(v))}")
    print("\n== call_clip files referenced ==")
    for lid, f in clips:
        print(f"  {lid:<6} {f}")
if A.json:
    with open(A.json, "w", encoding="utf-8") as fh:
        json.dump({"violations": violations, "warnings": warnings, "notes": notes,
                   "channels": {k: sorted(v) for k, v in channels.items()},
                   "money": {k: sorted(v) for k, v in money.items()},
                   "urls": {k: sorted(v) for k, v in urls.items()}, "clips": clips}, fh, indent=1)
sys.exit(1 if violations else 0)
