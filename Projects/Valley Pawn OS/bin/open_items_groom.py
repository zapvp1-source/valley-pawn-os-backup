#!/usr/bin/env python3
"""open_items_groom.py [--apply] [--projects DIR]   (2026-10-23, Joshua "go")

WHY: Life OS/OPEN_ITEMS_REGISTER.md is read by every session ("did we already do this") and had grown to
~1 MB (target well under 100 KB) because nothing ever archived closed rows or old narrative sections.
Every session paid for that in time and context. This keeps it short WITHOUT losing anything: whatever
leaves the register is appended verbatim to Life OS/OPEN_ITEMS_ARCHIVE.md first.

RULES (nothing is ever deleted):
  * OPEN table: a row whose Status starts DONE/CLOSED/RESOLVED/SUPERSEDED (bold ok) and was logged 7+ days
    ago -> archive. An open row logged 7+ days ago that is longer than 600 chars -> full row archived,
    a trimmed copy (item/next-action cut to ~220 chars + pointer) stays in the OPEN table.
  * RECENTLY CLOSED rows logged 14+ days ago -> archive.
  * Free-form "## <date> ..." sections after "## How to log a new item" dated 7+ days ago -> archive.
  * Header, table headers, "How to log", and anything recent stay exactly as they are.
SAFETY: dry run unless --apply; refuses to write if the register changed while it worked (mtime check);
backup of the pre-groom file to Life OS/_backups/; atomic replace. Silent; prints a one-line summary.
"""
import datetime as dt, os, re, shutil, sys
args = sys.argv[1:]
proj = os.path.expanduser("~/Documents/Claude/Projects")
if "--projects" in args: proj = args[args.index("--projects") + 1]
LIFE = os.path.join(proj, "Life OS"); REG = os.path.join(LIFE, "OPEN_ITEMS_REGISTER.md")
ARC = os.path.join(LIFE, "OPEN_ITEMS_ARCHIVE.md"); BK = os.path.join(LIFE, "_backups")
APPLY = "--apply" in args
today = dt.date.today()
DATE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
CLOSED = re.compile(r"^\**\s*(DONE|CLOSED|RESOLVED|SUPERSEDED|ITEM SIDE FULLY CLOSED)", re.I)

def age(text):
    m = DATE.search(text or "")
    if not m: return None
    try: return (today - dt.date(*map(int, m.groups()))).days
    except ValueError: return None

def cut(s, n=220):
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + " … (full text in OPEN_ITEMS_ARCHIVE.md)"

mtime = os.path.getmtime(REG)
src = open(REG, encoding="utf-8").read()
lines = src.split("\n")
out, arc = [], []
section = "head"; block = []; block_hdr = None
n_closed = n_trim = n_rc = n_sec = 0

def flush_block():
    global n_sec
    if block_hdr is None: return
    a = age(block_hdr)
    if a is not None and a >= 7:
        arc.extend(block); n_sec += 1
    else:
        out.extend(block)

for ln in lines:
    if ln.startswith("## "):
        if section == "free": flush_block()
        h = ln.lower()
        if h.startswith("## open"): section = "open"
        elif h.startswith("## recently closed"): section = "rc"
        elif h.startswith("## how to log"): section = "howto"
        elif section in ("howto", "free"):
            section = "free"; block = [ln]; block_hdr = ln; continue
        out.append(ln); continue
    if section == "free":
        block.append(ln); continue
    is_row = ln.startswith("|") and not re.match(r"^\|\s*-", ln) and not ln.startswith("| Date")
    if section == "open" and is_row:
        cells = ln.split("|")
        a = age(cells[1] if len(cells) > 1 else "")
        status = cells[4].strip() if len(cells) > 5 else ""
        if a is not None and a >= 7 and CLOSED.match(status):
            arc.append(ln); n_closed += 1; continue
        if a is not None and a >= 7 and len(ln) > 600 and len(cells) > 5 and "full text in OPEN_ITEMS_ARCHIVE.md" not in ln:
            t = list(cells)
            t[3] = " " + cut(t[3]) + " "
            if len(t) > 6: t[5] = " " + cut(t[5]) + " "
            short = "|".join(t)
            if len(short) < len(ln):
                arc.append(ln); n_trim += 1; ln = short
        out.append(ln); continue
    if section == "rc" and is_row:
        a = age(ln.split("|")[1] if "|" in ln else "")
        if a is not None and a >= 14:
            arc.append(ln); n_rc += 1; continue
    out.append(ln)
if section == "free": flush_block()

new = "\n".join(out)
summary = "register %d -> %d bytes; archived: %d closed rows, %d long rows trimmed, %d old closed-list rows, %d old sections" % (
    len(src.encode()), len(new.encode()), n_closed, n_trim, n_rc, n_sec)
if not APPLY or not arc:
    print(("DRY RUN " if not APPLY else "NOTHING TO DO ") + summary); sys.exit(0)
if os.path.getmtime(REG) != mtime:
    print("REFUSED: register changed while grooming; next run will retry"); sys.exit(0)
os.makedirs(BK, exist_ok=True)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
shutil.copy2(REG, os.path.join(BK, "OPEN_ITEMS_REGISTER.md.bak-groom-" + stamp))
if not os.path.exists(ARC):
    open(ARC, "w", encoding="utf-8").write("# Open Items Archive\n\nEverything groomed out of OPEN_ITEMS_REGISTER.md, verbatim, newest batch last. Search here before concluding something was never done.\n")
with open(ARC, "a", encoding="utf-8") as f:
    f.write("\n\n## Archived %s by open_items_groom\n\n" % today.isoformat() + "\n".join(arc) + "\n")
tmp = REG + ".tmp-groom"
open(tmp, "w", encoding="utf-8").write(new)
os.replace(tmp, REG)
print("APPLIED " + summary)
