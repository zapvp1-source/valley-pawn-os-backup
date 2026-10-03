#!/usr/bin/env python3
"""model_pin_report.py — READ-ONLY. (2026-10-02, scheduled-task model audit)
Writes fleet/model_audit/pins-<stamp>.tsv : task id, enabled, frontmatter model pin (or UNPINNED),
plus fleet/model_audit/logmodels-<stamp>.txt : every distinct model id the Claude app log mentions
in the last 3 days, with a sample line, so we can see which pinned IDs the app actually resolves.
Never edits anything."""
import os, re, json, glob, time, collections
HOME = os.path.expanduser("~")
SCHED = os.path.join(HOME, "Documents/Claude/Scheduled")
OUT = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/model_audit")
os.makedirs(OUT, exist_ok=True)
stamp = time.strftime("%Y%m%d-%H%M%S")

# registry (enabled flags)
en = {}
regs = glob.glob(os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json"))
regs.sort(key=os.path.getmtime, reverse=True)
if regs:
    d = json.load(open(regs[0]))
    ts = d.get("scheduledTasks", [])
    ts = ts if isinstance(ts, list) else list(ts.values())
    for t in ts:
        en[t["id"]] = bool(t.get("enabled"))

rows = []
for name in sorted(os.listdir(SCHED)):
    p = os.path.join(SCHED, name, "SKILL.md")
    if not os.path.isfile(p):
        continue
    lines = open(p, errors="replace").read().split("\n")
    pin, fm_ok = "UNPINNED", lines and lines[0].strip() == "---"
    if fm_ok:
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        except StopIteration:
            end = 0
            fm_ok = False
        for l in lines[1:end]:
            if re.match(r"^model:", l):
                pin = l.split(":", 1)[1].strip()
    # model lines outside frontmatter (malformed) in first 15 lines
    stray = [l.strip() for l in lines[(end + 1 if fm_ok else 0):15] if re.match(r"^model:", l)] if lines else []
    rows.append((name, {True: "on", False: "off"}.get(en.get(name), "unregistered"), pin,
                 "OK" if fm_ok else "NO_FRONTMATTER", ";".join(stray)))
with open(os.path.join(OUT, "pins-%s.tsv" % stamp), "w") as f:
    f.write("task\tenabled\tpin\tfrontmatter\tstray_model_lines\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

# app log: which model ids appear
LOGD = os.path.join(HOME, "Library/Logs/Claude")
pat = re.compile(r"claude-(?:opus|sonnet|haiku|fable)[-a-z0-9.]*")
seen = collections.OrderedDict()
cut = time.time() - 3 * 86400
for p in sorted(glob.glob(os.path.join(LOGD, "*.log"))):
    if os.path.getmtime(p) < cut:
        continue
    try:
        for line in open(p, errors="replace"):
            for m in pat.findall(line):
                c = seen.setdefault(m, [0, ""])
                c[0] += 1
                if "model" in line.lower() and (not c[1] or "scheduled" in line.lower()):
                    c[1] = os.path.basename(p) + ": " + line.strip()[:500]
    except OSError:
        pass
with open(os.path.join(OUT, "logmodels-%s.txt" % stamp), "w") as f:
    for k, (n, s) in seen.items():
        f.write("%s\t%d\t%s\n" % (k, n, s))
print("wrote", stamp, len(rows), "tasks;", len(seen), "model ids in logs")
