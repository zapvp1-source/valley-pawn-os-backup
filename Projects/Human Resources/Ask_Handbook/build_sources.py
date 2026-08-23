#!/usr/bin/env python3
"""
build_sources.py — regenerate SOURCES_CURRENT.md for the #ask-handbook responder.

WHY THIS EXISTS
    The ask-handbook responder answers employees ONLY from SOURCES_CURRENT.md.
    If a policy changes in the master .docx files and this file isn't rebuilt,
    employees keep getting the OLD answer — with a confident citation. That is
    the single worst failure this system can produce.

    So regeneration must never depend on a human remembering. The responder runs
    this script at the start of every run (every 30 min during store hours).
    A policy change is therefore live to employees within 30 minutes, automatically.

DESIGN NOTES (deliberate, don't "simplify" these away)
  * PURE STDLIB. No python-docx, no pip. A .docx is a zip of XML; zipfile +
    xml.etree parse it fine. This must run on the Mac's stock /usr/bin/python3
    where installing packages is a failure surface we don't want.
  * VERSION-AGNOSTIC. It globs for the HIGHEST-numbered version of each document
    rather than hardcoding a filename. When v2026.4 is published, this picks it
    up with no edit here and no edit in the scheduled task. That is the whole
    point — the next version bump must not require anyone to remember this file.
  * ATOMIC WRITE. Writes to a temp file and renames, so the responder can never
    read a half-written sources file mid-regeneration.
  * FAILS LOUDLY, NEVER SILENTLY. If a source doc is missing or unreadable it
    exits non-zero and leaves the previous good file untouched. Stale-but-valid
    beats truncated. The responder treats a non-zero exit as a hard stop.

USAGE
    python3 build_sources.py            # rebuild if sources are newer (normal)
    python3 build_sources.py --force    # rebuild unconditionally
    python3 build_sources.py --check    # report staleness only, write nothing
"""

import os
import re
import sys
import glob
import zipfile
import xml.etree.ElementTree as ET

HR = os.path.expanduser("~/Documents/Claude/Projects/Human Resources")
OUT = os.path.join(HR, "Ask_Handbook", "SOURCES_CURRENT.md")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Each entry: (glob pattern, human label for citations, how to describe it)
DOCS = [
    {
        "glob": "Valley_Pawn_PP_Manual_v*_FINAL.docx",
        "title": "VALLEY PAWN POLICIES & PROCEDURES MANUAL",
        "cite": "P&P Manual {ver}",
        "note": "Operational policy — how the stores run.",
    },
    {
        "glob": "Employee_Handbook_v*_FINAL.docx",
        "title": "VALLEY PAWN EMPLOYEE HANDBOOK",
        "cite": "Employee Handbook {ver}",
        "note": "HR / employment policy — pay, leave, conduct, benefits.",
    },
]


def version_key(path):
    """Sort key from a filename like ..._v2026.3_FINAL.docx -> (2026, 3)."""
    m = re.search(r"_v(\d+)\.(\d+)_", os.path.basename(path))
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def version_str(path):
    m = re.search(r"_v(\d+\.\d+)_", os.path.basename(path))
    return "v" + m.group(1) if m else "v?"


def newest(pattern):
    """Highest-versioned matching FINAL doc, or None."""
    hits = glob.glob(os.path.join(HR, pattern))
    if not hits:
        return None
    return sorted(hits, key=version_key)[-1]


def docx_paragraphs(path):
    """Yield (style_id, text) for each paragraph. Pure stdlib."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text:
            continue
        style = ""
        pPr = p.find(W + "pPr")
        if pPr is not None:
            pStyle = pPr.find(W + "pStyle")
            if pStyle is not None:
                style = pStyle.get(W + "val") or ""
        yield style, text


def render(path, spec):
    ver = version_str(path)
    cite = spec["cite"].format(ver=ver)
    mtime = os.path.getmtime(path)
    import datetime
    stamp = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    lines = []
    lines.append("=" * 80)
    lines.append("SOURCE: %s — %s (document last modified %s)" % (spec["title"], ver, stamp))
    lines.append(spec["note"])
    lines.append("CITE ANSWERS FROM THIS DOCUMENT AS: %s, <section number and name>" % cite)
    lines.append("=" * 80)

    for style, text in docx_paragraphs(path):
        s = style.lower()
        if s.startswith("heading1"):
            lines.append("\n## " + text)
        elif s.startswith("heading2"):
            lines.append("\n### " + text)
        elif s.startswith("heading3"):
            lines.append("\n#### " + text)
        elif s.startswith("listparagraph"):
            lines.append("- " + text)
        else:
            lines.append(text)
    return "\n".join(lines)


def main():
    force = "--force" in sys.argv
    check_only = "--check" in sys.argv

    resolved = []
    for spec in DOCS:
        path = newest(spec["glob"])
        if not path:
            sys.stderr.write("FATAL: no file matching %s in %s\n" % (spec["glob"], HR))
            return 2
        resolved.append((path, spec))

    newest_src = max(os.path.getmtime(p) for p, _ in resolved)
    out_mtime = os.path.getmtime(OUT) if os.path.exists(OUT) else 0
    stale = newest_src > out_mtime

    for p, _ in resolved:
        print("SOURCE: %s (%s)" % (os.path.basename(p), version_str(p)))

    if check_only:
        print("STATUS: " + ("STALE - rebuild needed" if stale else "CURRENT"))
        return 0

    if not stale and not force:
        print("STATUS: CURRENT - no rebuild needed")
        return 0

    import datetime
    header = [
        "# ASK-HANDBOOK SOURCES — Full Circle Finance Inc DBA Valley Pawn",
        "",
        "AUTO-GENERATED %s by build_sources.py. Do not hand-edit — edits are overwritten."
        % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "",
        "This file is the ONLY thing the #ask-handbook responder may answer employees from.",
        "If a policy is not in here, the correct answer is 'not covered — ask your Store Manager',",
        "never a guess and never an answer from general knowledge.",
        "",
    ]
    body = "\n".join(header) + "\n" + "\n\n".join(render(p, s) for p, s in resolved) + "\n"

    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        f.write(body)
    os.replace(tmp, OUT)  # atomic

    print("REBUILT: %s (%d chars, ~%d tokens)" % (OUT, len(body), len(body) // 4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
