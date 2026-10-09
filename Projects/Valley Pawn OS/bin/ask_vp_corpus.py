#!/usr/bin/env python3
"""
ask_vp_corpus.py — build ASK_VP_CORPUS.jsonl, the ONLY thing the Ask Valley Pawn responder may answer from.

WHY THIS EXISTS
    Same contract as Ask_Handbook/build_sources.py and Preston Knowledge Base/kb_build.py: the responder
    answers store staff from a corpus; a stale or hand-edited corpus produces a confident, cited, WRONG
    answer. So the corpus is GENERATED from the source systems, never hand-written, and rebuilt at the top
    of every responder run (cheap: it only rebuilds when an input changed).

LAYERS (each chunk carries layer, cite, trust)
    1 policy   — P&P Manual + Employee Handbook, via Ask_Handbook/build_sources.py -> SOURCES_CURRENT.md
                 (one chunk per numbered section; trust POLICY)
    2 preston  — Preston Knowledge Base/kb_build.py -> KB_CURRENT.md (one chunk per entry; trust = its tier:
                 VERIFIED / HIGH answerable, MEDIUM / LOW context-only, SUPERSEDED never)
    3 academy  — Training Program/academy/lessons/**.json (one chunk per lesson: key points + slide text;
                 trust ACADEMY; quiz answers and call-clip captions are NOT included)
    6 facts    — Ask Valley Pawn/facts/*.md (hand-maintained store & systems facts: hours, phones,
                 addresses, managers; trust FACT). Layers 4 (call-derived) and 5 (answer bank) enter
                 through the harvest -> verify loop as Preston KB entries, never as raw transcripts.

DESIGN NOTES (deliberate)
  * PURE STDLIB, runs on stock /usr/bin/python3 (3.9).
  * FAILS LOUDLY. If either upstream build exits non-zero or an input is missing, this exits non-zero and
    leaves the previous corpus untouched. The responder treats non-zero as "do not answer".
  * ATOMIC WRITE. Temp file then rename.
  * NO CUSTOMER DATA. Only the four generated/curated sources above are read. Nothing from Zoom
    out/customer, Chekkit, or mailboxes is ever read here.

USAGE
    python3 ask_vp_corpus.py            # rebuild if any input is newer than the corpus
    python3 ask_vp_corpus.py --force    # rebuild unconditionally
    python3 ask_vp_corpus.py --check    # report staleness + counts, write nothing
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects")
BASE = os.path.join(PROJ, "Ask Valley Pawn")
OUT = os.path.join(BASE, "corpus", "ASK_VP_CORPUS.jsonl")
STATUS = os.path.join(BASE, "corpus", "BUILD_STATUS.json")

HB_DIR = os.path.join(PROJ, "Human Resources", "Ask_Handbook")
HB_BUILD = os.path.join(HB_DIR, "build_sources.py")
HB_SRC = os.path.join(HB_DIR, "SOURCES_CURRENT.md")

KB_DIR = os.path.join(PROJ, "Preston Knowledge Base")
KB_BUILD = os.path.join(KB_DIR, "kb_build.py")
KB_SRC = os.path.join(KB_DIR, "KB_CURRENT.md")

ACADEMY = os.path.join(PROJ, "Training Program", "academy", "lessons")
FACTS = os.path.join(BASE, "facts")

PY = sys.executable or "/usr/bin/python3"


def log(msg):
    sys.stderr.write("[ask_vp_corpus] %s\n" % msg)


def run_upstream(script, cwd):
    """Run an upstream generator. Non-zero = we stop. Its own staleness check keeps this cheap."""
    r = subprocess.run([PY, script], cwd=cwd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        log("UPSTREAM FAILED %s rc=%s\n%s" % (os.path.basename(script), r.returncode, (r.stderr or r.stdout)[-800:]))
        sys.exit(2)


# ----------------------------------------------------------------------------- layer 1: policy
SRC_HDR = re.compile(r"^SOURCE: (.+?) — v([\d.]+)", re.M)
CITE_HDR = re.compile(r"^CITE ANSWERS FROM THIS DOCUMENT AS: (.+?), <section", re.M)
NUM_HDR = re.compile(r"^### (\d{1,2}[A-Z]?\.\d{2})\s+(.+)$")      # "### 01.11 Paid Time Off"
PART_HDR = re.compile(r"^## Section (\d{1,2}[A-Z]?):\s*(.+)$")        # "## Section 5A: Online Sales (eBay)"
SUB_HDR = re.compile(r"^#### (.+)$")
ANY_HDR = re.compile(r"^### (.+)$")                                   # Handbook headings carry no numbers
SKIP_TITLES = ("what’s new", "what's new", "changelog", "table of contents")


def _slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:48]


def parse_policy(text):
    chunks = []
    blocks = re.split(r"^={60,}\n(?=SOURCE: )", text, flags=re.M)
    for b in blocks:
        m = SRC_HDR.search(b)
        c = CITE_HDR.search(b)
        if not m or not c:
            continue
        doc_title, cite_prefix = m.group(1).strip(), c.group(1).strip()
        short = "pp" if "PROCEDURES" in doc_title.upper() else "hb"
        body = b[c.end():]
        cur = None      # (id, cite-fragment, title)
        buf = []
        part = ""       # current "## Section X: name" for unnumbered P&P headings

        def flush():
            if cur and buf:
                t = "\n".join(buf).strip()
                if len(t) > 40 and not cur[2].lower().startswith(SKIP_TITLES):
                    chunks.append({"id": cur[0], "layer": "policy", "trust": "POLICY",
                                   "cite": "%s, %s" % (cite_prefix, cur[1]),
                                   "title": cur[2], "text": t[:6000]})

        for ln in body.splitlines():
            st = ln.strip()
            pm = PART_HDR.match(st)
            if pm:
                flush(); cur = None; buf = []
                part = "Section %s %s" % (pm.group(1), pm.group(2).strip())
                continue
            nm = NUM_HDR.match(st)
            if nm:
                flush()
                num, title = nm.group(1), nm.group(2).strip()
                cur = ("%s:%s" % (short, num), "§%s %s" % (num, title), title)
                buf = []
                continue
            sm = SUB_HDR.match(st)
            if sm and cur is not None and short == "pp":
                # "#### Multiple Handgun Sales Protocol" inside "### 04.02 Firearms" -> its own passage
                flush()
                sub = sm.group(1).strip()
                base_id, base_cite, base_title = cur[0].split("/")[0], cur[1].split(" — ")[0], cur[2]
                cur = ("%s/%s" % (base_id, _slug(sub)), "%s — %s" % (base_cite, sub), "%s — %s" % (base_title.split(" — ")[0], sub))
                buf = []
                continue
            am = ANY_HDR.match(st)
            if am:
                flush()
                title = am.group(1).strip().strip("*").strip()
                if short == "pp":
                    cur = ("%s:%s" % (short, _slug(part + " " + title)), "%s — %s" % (part, title) if part else title, title)
                else:
                    cur = ("%s:%s" % (short, _slug(title)), "section \"%s\"" % title, title)
                buf = []
                continue
            if cur is not None:
                buf.append(ln)
        flush()
    return chunks


# ----------------------------------------------------------------------------- layer 2: preston
KB_ENTRY = re.compile(r"^### \[(VERIFIED|HIGH|MEDIUM|LOW|SUPERSEDED)\] (.+)$")


def parse_kb(text):
    chunks = []
    cur = None
    buf = []

    def flush():
        if not cur:
            return
        body = "\n".join(buf).strip()
        m = re.search(r"^id: (\S+)", body, re.M)
        eid = m.group(1) if m else cur[1]
        src = re.search(r"^SOURCE: (.+)$", body, re.M)
        date = ""
        if src:
            d = re.search(r"(20\d\d-\d\d-\d\d)", src.group(1))
            date = d.group(1) if d else ""
        trust = cur[0]
        who = "Preston"
        srcline = src.group(1) if src else ""
        mm = re.search(r"\(([^,()]+), ([A-Za-z]+ manager)\)", srcline)
        if mm:
            who = "%s (%s)" % (mm.group(1).strip(), mm.group(2))
        via = " on a recorded call" if srcline.startswith("zoom-call:") else ""
        cite = "%s's rule%s (%s%s)" % (who, via, trust.lower(), (", " + date) if date else "")
        if trust == "VERIFIED":
            cite = "%s (confirmed%s)" % (who, (", " + date) if date else "")
        chunks.append({
            "id": "kb:" + eid,
            "layer": "preston",
            "trust": trust,
            "cite": cite,
            "date": date,
            "title": cur[1],
            "text": body[:4000],
        })

    for ln in text.splitlines():
        m = KB_ENTRY.match(ln)
        if m:
            flush()
            cur = (m.group(1), m.group(2).strip())
            buf = []
        elif cur is not None:
            if ln.startswith("====") or ln.startswith("SECTION:") or ln.startswith("COVERAGE:"):
                flush()
                cur = None
                buf = []
            else:
                buf.append(ln)
    flush()
    return chunks


# ----------------------------------------------------------------------------- layer 3: academy
def parse_academy():
    chunks = []
    for p in sorted(glob.glob(os.path.join(ACADEMY, "*", "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            log("skip unreadable lesson %s: %s" % (p, e))
            continue
        lid = d.get("id") or os.path.basename(p)
        title = d.get("title", "")
        parts = []
        for kp in d.get("key_points") or []:
            parts.append("- " + kp)
        for s in d.get("slides") or []:
            h = s.get("heading", "")
            if h:
                parts.append("\n" + h)
            for b in s.get("bullets") or []:
                parts.append("  • " + b)
            if s.get("say"):
                parts.append("  " + s["say"])
        if d.get("floor_check"):
            parts.append("\nFloor check: " + str(d["floor_check"]))
        if d.get("gate"):
            parts.append("Gate: " + str(d["gate"]))
        srcs = [s for s in (d.get("sources") or []) if isinstance(s, str) and not s.upper().startswith("OPEN")]
        if srcs:
            parts.append("\nThis lesson is based on: " + "; ".join(s[:160] for s in srcs[:6]))
        text = "\n".join(parts).strip()
        if len(text) < 80:
            continue
        chunks.append({
            "id": "ac:" + lid,
            "layer": "academy",
            "trust": "ACADEMY",
            "cite": "Academy lesson %s — %s" % (lid, title),
            "title": title,
            "text": text[:7000],
        })
    return chunks


# ----------------------------------------------------------------------------- layer 6: facts
def parse_facts():
    chunks = []
    for p in sorted(glob.glob(os.path.join(FACTS, "*.md"))):
        text = open(p, encoding="utf-8").read()
        name = os.path.splitext(os.path.basename(p))[0]
        # split on '## ' headings; each heading is one fact chunk
        pieces = re.split(r"^## ", text, flags=re.M)
        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if i == 0 or not piece:      # text before the first "## " is the file header, not a fact
                continue
            lines = piece.splitlines()
            title = lines[0].strip("# ").strip()
            body = "\n".join(lines[1:]).strip()
            if len(body) < 20:
                continue
            chunks.append({
                "id": "fact:%s:%d" % (name, i),
                "layer": "facts",
                "trust": "FACT",
                "cite": "Store facts — " + title,
                "title": title,
                "text": body[:4000],
            })
    return chunks


# ----------------------------------------------------------------------------- main
def inputs():
    files = [HB_SRC, KB_SRC] + glob.glob(os.path.join(ACADEMY, "*", "*.json")) + glob.glob(os.path.join(FACTS, "*.md"))
    return [f for f in files if os.path.exists(f)]


def main():
    force = "--force" in sys.argv
    check = "--check" in sys.argv
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    # Upstream generators first (they do their own staleness checks and fail loudly).
    if not check:
        if not os.path.exists(HB_BUILD) or not os.path.exists(KB_BUILD):
            log("FATAL: upstream build scripts missing")
            return 2
        run_upstream(HB_BUILD, HB_DIR)
        run_upstream(KB_BUILD, KB_DIR)

    ins = inputs()
    if HB_SRC not in ins or KB_SRC not in ins:
        log("FATAL: SOURCES_CURRENT.md or KB_CURRENT.md missing")
        return 2
    newest = max(os.path.getmtime(p) for p in ins)
    out_m = os.path.getmtime(OUT) if os.path.exists(OUT) else 0
    stale = newest > out_m or not os.path.exists(OUT)
    if check:
        print(json.dumps({"stale": stale, "inputs": len(ins), "corpus": OUT,
                          "corpus_mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(out_m)) if out_m else None}))
        return 0
    if not stale and not force:
        return 0

    chunks = []
    chunks += parse_policy(open(HB_SRC, encoding="utf-8").read())
    n_policy = len(chunks)
    chunks += parse_kb(open(KB_SRC, encoding="utf-8").read())
    n_kb = len(chunks) - n_policy
    chunks += parse_academy()
    n_ac = len(chunks) - n_policy - n_kb
    chunks += parse_facts()
    n_f = len(chunks) - n_policy - n_kb - n_ac

    if n_policy < 20 or n_kb < 50:
        log("FATAL: suspiciously small layers (policy=%d, preston=%d) — refusing to publish" % (n_policy, n_kb))
        return 2

    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    os.replace(tmp, OUT)
    status = {"built_at": time.strftime("%Y-%m-%d %H:%M:%S"), "chunks": len(chunks),
              "policy": n_policy, "preston": n_kb, "academy": n_ac, "facts": n_f}
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1)
    print(json.dumps(status))
    return 0


if __name__ == "__main__":
    sys.exit(main())
