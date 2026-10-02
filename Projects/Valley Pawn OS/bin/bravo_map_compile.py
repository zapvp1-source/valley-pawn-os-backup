#!/usr/bin/env python3
"""bravo_map_compile.py -- turn BravoMapper raw dumps into one readable reference.

Additive 2026-09-30. Reads  Bravo Data Extraction/output/bravo_map/  (screens/*.txt, lists/*.txt,
cand_*.txt, index.tsv, _done.txt, _fail.txt, RUN_LOG.md) and writes
Bravo Data Extraction/BRAVO_MAP.md. Pure file work: never touches Bravo. Safe to re-run any time.
"""
import os, re, glob, datetime, collections

BDE = os.environ.get("BDE_OVERRIDE") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
MAP = os.path.join(BDE, "output", "bravo_map")
OUT = os.path.join(BDE, "BRAVO_MAP.md")
LINE = re.compile(r"^( *)\[(.*?)\] N=(.*?) \| A=(.*?) \| C=(.*?) \| (\S+)( off)? \| R=([^|]*?)(?: \| V=(.*))?$")
INTERESTING = {
    "button": "Buttons", "hyperlink": "Links", "tab item": "Tabs", "edit": "Fields",
    "combo box": "Dropdowns", "check box": "Checkboxes", "radio button": "Options",
    "header item": "Grid columns", "tree item": "Tree items", "menu item": "Menu items",
    "split button": "Buttons", "text": "Labels",
}


def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def lines(p):
    return [l.strip() for l in read(p).splitlines() if l.strip()]


def parse(path):
    meta, els = {}, []
    for raw in read(path).splitlines():
        if raw.startswith("# "):
            k, _, v = raw[2:].partition(": ")
            meta[k] = v
            continue
        m = LINE.match(raw.rstrip("\r"))
        if m:
            els.append({"depth": len(m.group(1)) // 2, "type": m.group(2).lower(), "name": m.group(3).strip(),
                        "aid": m.group(4).strip(), "enabled": m.group(6) == "E", "value": (m.group(9) or "").strip()})
    return meta, els


def sig(e):
    return (e["type"], e["name"], e["aid"])


def controls(els, baseline):
    groups = collections.OrderedDict()
    seen = set()
    for e in els:
        g = INTERESTING.get(e["type"])
        if not g or sig(e) in baseline or sig(e) in seen:
            continue
        if not e["name"] and not e["aid"]:
            continue
        if e["name"].startswith("ZTI.") and not e["aid"]:
            continue
        if g == "Labels" and (len(e["name"]) < 2 or len(e["name"]) > 60):
            continue
        seen.add(sig(e))
        label = e["name"] or "(no label)"
        if e["aid"] and e["aid"] != e["name"]:
            label += " `" + e["aid"] + "`"
        groups.setdefault(g, []).append(label)
    return groups


def render_screen(key, baseline, depth=3):
    meta, els = parse(os.path.join(MAP, "screens", key + ".txt"))
    out = ["%s %s" % ("#" * depth, meta.get("note", key)),
           "_key `%s` · captured %s · %s_" % (key, meta.get("captured", "?"), meta.get("title", "").strip()),
           "Screenshot: `output/bravo_map/shots/%s.png`" % key, ""]
    g = controls(els, baseline)
    if not g:
        out.append("(no screen-specific controls captured)")
    for name, items in g.items():
        cap = 60 if name != "Labels" else 40
        more = "" if len(items) <= cap else " … +%d more" % (len(items) - cap)
        out.append("- **%s:** %s%s" % (name, "; ".join(items[:cap]), more))
    out.append("")
    return out


def main():
    if not os.path.isdir(MAP):
        print("no bravo_map output yet")
        return
    done = lines(os.path.join(MAP, "_done.txt"))
    fails = collections.Counter(lines(os.path.join(MAP, "_fail.txt")))
    failed_final = sorted(k for k, n in fails.items() if k not in done)
    status = read(os.path.join(MAP, "_status.txt")).strip()
    complete = os.path.exists(os.path.join(MAP, "_COMPLETE"))
    screens = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(MAP, "screens", "*.txt"))}
    _, dash = parse(os.path.join(MAP, "screens", "D_dashboard.txt"))
    baseline = {sig(e) for e in dash}

    o = ["# Bravo POS — Complete Screen & Report Map",
         "",
         "_Generated %s by `bravo_map_compile.py` from BravoMapper's read-only crawl. Do not hand-edit; "
         "add human notes to the `bravo-context` skill instead._" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
         "",
         "**Status:** %s · %d steps mapped · %d steps could not be mapped · last crawler state: `%s`"
         % ("COMPLETE" if complete else "IN PROGRESS (resumes nightly)", len(done), len(failed_final), status),
         "",
         "Raw data: `output/bravo_map/` — `screens/` (full UI tree per screen), `shots/` (screenshots), `lists/` "
         "(report lists, Custom Reports criteria / columns / saved reports), `index.tsv`, `RUN_LOG.md`.",
         "",
         "Store mapped: screens and reports are identical at all 5 stores (one Bravo build, one login).",
         ""]

    if "D_dashboard" in screens:
        o += ["## Dashboard", ""] + render_screen("D_dashboard", set(), 3)

    o += ["## Modules (right sidebar)", ""]
    mods = sorted(k for k in screens if k.startswith("M_"))
    for mk in mods:
        slug = mk[2:]
        o += render_screen(mk, baseline, 3)
        subs = sorted(k for k in screens if k.startswith("S_%s__" % slug))
        for sk in subs:
            o += render_screen(sk, baseline, 4)
            for f in sorted(glob.glob(os.path.join(MAP, "lists", sk + "_*.txt"))):
                what = os.path.basename(f)[len(sk) + 1:-4]
                vals = lines(f)
                label = {"BoxSelectCriteria": "Filter criteria available", "BoxColumns": "Columns available",
                         "SavedReports": "Saved reports"}.get(what, what)
                o.append("- **%s (%d):** %s" % (label, len(vals), "; ".join(vals) if vals else "(none captured)"))
            if subs:
                o.append("")
        nc = lines(os.path.join(MAP, "lists", "notclicked_%s.txt" % slug))
        if nc:
            o.append("- **Action controls recorded but deliberately NOT clicked (write/transaction actions):** "
                     + "; ".join(l.split("\t")[1] for l in nc if "\t" in l))
            o.append("")

    o += ["## Reports", ""]
    reps = lines(os.path.join(MAP, "lists", "reports.txt"))
    # categories + reports straight from the Reports-tree dump (works even before the per-report pass)
    tree = read(os.path.join(MAP, "screens", "R__tree.txt")).splitlines()
    bycat, cat, pend = collections.OrderedDict(), None, []
    for i, raw in enumerate(tree):
        if "[tree view item] N=Item: (ZTI.Bravo.ReportManager.ReportTree." in raw and ("Configurable" in raw or "Printable" in raw):
            if i + 1 < len(tree):
                m = re.search(r"\[text\] N=(.*?) \|", tree[i + 1])
                if m and m.group(1).strip():
                    pend.append(m.group(1).strip())
        m = re.match(r"^ {8}\[text\] N=(.*?) \|", raw)      # category caption closes its block
        if m and pend:
            bycat[m.group(1).strip()] = pend
            pend = []
    for c, rs in bycat.items():
        o.append("- **%s (%d):** %s" % (c, len(rs), "; ".join(rs)))
    if not reps:
        reps = [r for rs in bycat.values() for r in rs]
    o.append("All reports (%d): %s" % (len(reps), "; ".join(reps)))
    o.append("")
    for r in reps:
        k = "R_" + re.sub(r"[^A-Za-z0-9]+", "_", r).strip("_")[:60]
        if k in screens:
            o += render_screen(k, baseline, 3)

    tiles = sorted(k for k in screens if k.startswith("T_"))
    if tiles:
        o += ["## Dashboard task tiles", ""]
        for t in tiles:
            o += render_screen(t, baseline, 3)

    if failed_final:
        o += ["## Could not be mapped automatically (needs one supervised look)", ""]
        o += ["- `%s` (failed %dx)" % (k, fails[k]) for k in failed_final]
        o.append("")

    o += ["## Run history", ""] + lines(os.path.join(MAP, "RUN_LOG.md"))
    open(OUT, "w", encoding="utf-8").write("\n".join(o) + "\n")
    print("wrote", OUT, "screens=%d done=%d failed=%d" % (len(screens), len(done), len(failed_final)))


if __name__ == "__main__":
    main()
