#!/usr/bin/env python3
"""reminders_export.py — READ-ONLY full export of Apple Reminders (all lists, open items + notes) via EventKit.

Built 2026-11-21 (Joshua: "handle most of my to-do list for me"). WHY: the Unified Search reminders corpus
is AppleScript-fed and sees only a SUBSET of lists (11 of ~46) — never use it as the to-do source of truth.
This calls Life OS/bin/ekrem (EventKit) for every list, and ekremnotes for notes (compiled on first use).
Writes Life OS/Reminders/export_latest.json (+ dated copy) and export_status.json. Never writes to Reminders.
Usage: python3 ".../bin/reminders_export.py" [--all]   (--all includes completed items)
NOT YET ALLOW-LISTED for the host queue — needs Joshua's OK (allow-list changes are his call).
"""
import json, os, subprocess, sys, datetime, shutil
ROOT = os.path.expanduser("~/Documents/Claude/Projects")
LBIN = os.path.join(ROOT, "Life OS/bin")
EKREM = os.path.join(LBIN, "ekrem")
EKN = os.path.join(LBIN, "ekremnotes")
OUT = os.path.join(ROOT, "Life OS/Reminders")
os.makedirs(OUT, exist_ok=True)
mode = "all" if "--all" in sys.argv else "open"

def run(args, t=120):
    p = subprocess.run(args, capture_output=True, text=True, timeout=t)
    return p.returncode, p.stdout, p.stderr

status = {"ok": False, "at": datetime.datetime.now().isoformat(timespec="seconds"), "mode": mode}
if not os.path.exists(EKN) and shutil.which("swiftc"):
    rc, o, e = run(["swiftc", "-O", "-o", EKN, EKN + ".swift"], 300)
    status["ekremnotes_build"] = rc
rc, o, e = run([EKREM, "lists"])
if rc != 0:
    status["error"] = (o + e).strip()[:500]
    json.dump(status, open(os.path.join(OUT, "export_status.json"), "w"), indent=1)
    print("FAIL", status["error"]); sys.exit(2)
lists = [l for l in o.splitlines() if l.strip()]
items = []
for L in lists:
    rc, o, e = run([EKREM, "dump", L, mode])
    notes = {}
    if os.path.exists(EKN):
        rc2, o2, e2 = run([EKN, L, mode])
        for line in o2.splitlines()[1:]:
            p = line.split("\t")
            if len(p) >= 4: notes[p[1]] = p[3]
    for line in o.splitlines()[1:]:
        try:
            left, title, rid = line.split(" :: ", 2)
            due, st, rec = left.split()
        except ValueError:
            continue
        items.append({"list": L, "title": title, "id": rid.strip(), "due": None if due.startswith("none") else due,
                      "done": st == "DONE", "recurring": rec == "REC", "notes": notes.get(rid.strip(), "")})
status.update(ok=True, lists=len(lists), items=len(items), open=sum(not i["done"] for i in items))
doc = {"status": status, "lists": lists, "items": items}
fn = os.path.join(OUT, "export_latest.json")
json.dump(doc, open(fn, "w"), ensure_ascii=False, indent=1)
shutil.copy(fn, os.path.join(OUT, "export_%s.json" % datetime.date.today().isoformat()))
json.dump(status, open(os.path.join(OUT, "export_status.json"), "w"), indent=1)
print("OK", status)
