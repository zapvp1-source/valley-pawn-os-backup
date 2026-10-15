#!/usr/bin/env python3
"""model_audit_weekly.py [--render] [--send]

Native replacement (Mac-first wave 2, 2026-10-14) for the Cowork task `scheduled-task-model-audit-weekly` (Mon 05:00 ET).
Silent by design (Rule 16): no Slack, no DM. Same scripts the Cowork run dropped on the host queue:
  1 bin/model_pin_report.py -> fleet/model_audit/pins-<stamp>.tsv + logmodels-<stamp>.txt
  2 every ENABLED task that is UNPINNED, pinned to Fable, pinned to the deprecated claude-opus-4-8, or has bad
    frontmatter -> bin/pin_task_model.py <task> <model> (opus-4-8 -> claude-opus-5; everything else -> the SKILL's
    default tier claude-sonnet-5; an existing valid pin is kept on a frontmatter repair). "Clearly mis-tiered"
    judgment calls are NOT made here — they are listed in the register row for a human session.
  3 re-run the report and confirm every enabled task now has a valid non-Fable pin; else one FAILURE_LEDGER row
  4 one row in Life OS/OPEN_ITEMS_REGISTER.md (count audited, id -> old -> new, Fable usage seen in the app log)
--render runs the read-only report and prints the plan; changes nothing. --send applies it.
Retire this agent when the last Cowork scheduled task is gone (the plan classes it R for that reason).
"""
import datetime as dt
import glob
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = "scheduled-task-model-audit-weekly"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
OUT = os.path.join(OS_DIR, "fleet", "model_audit")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
OPEN_ITEMS = os.path.expanduser("~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md")
VALID = {"claude-haiku-4-5", "claude-sonnet-5", "claude-opus-5"}
PY = "/usr/bin/python3"


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def report():
    p = subprocess.run([PY, os.path.join(HERE, "model_pin_report.py")], capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError("model_pin_report failed: " + (p.stdout + p.stderr)[-300:])
    tsv = max(glob.glob(os.path.join(OUT, "pins-*.tsv")), key=os.path.getmtime)
    logm = max(glob.glob(os.path.join(OUT, "logmodels-*.txt")), key=os.path.getmtime)
    rows = []
    for i, line in enumerate(open(tsv)):
        c = line.rstrip("\n").split("\t")
        if i == 0 or len(c) < 4:
            continue
        rows.append({"task": c[0], "enabled": c[1] == "on", "pin": c[2], "fm": c[3], "stray": c[4] if len(c) > 4 else ""})
    return rows, open(logm, errors="replace").read()


def plan(rows):
    fixes = []
    for r in rows:
        if not r["enabled"]:
            continue
        pin, ok_fm = r["pin"], r["fm"] == "OK"
        if pin == "claude-opus-4-8":
            fixes.append((r["task"], pin, "claude-opus-5"))
        elif pin not in VALID or pin.startswith("claude-fable"):
            fixes.append((r["task"], pin, "claude-sonnet-5"))
        elif not ok_fm or r["stray"]:
            fixes.append((r["task"], pin + " (frontmatter %s)" % r["fm"], pin))
    return fixes


def main():
    send = "--send" in sys.argv and "--render" not in sys.argv
    rows, logm = report()
    enabled = [r for r in rows if r["enabled"]]
    fixes = plan(rows)
    fable = sorted({w for w in logm.split() if w.startswith("claude-fable")})
    print("audited %d folders, %d enabled; fixes: %s; fable in app log: %s" % (len(rows), len(enabled), fixes or "none", fable or "none"))
    if not send:
        return 0
    done = []
    for task, old, new in fixes:
        p = subprocess.run([PY, os.path.join(HERE, "pin_task_model.py"), task, new], capture_output=True, text=True, timeout=120)
        done.append((task, old, new, p.returncode == 0))
        print(task, old, "->", new, "rc", p.returncode, (p.stdout + p.stderr).strip()[-200:])
    if fixes:
        rows2, _ = report()
        bad = [r["task"] for r in rows2 if r["enabled"] and (r["pin"] not in VALID or r["fm"] != "OK")]
        if bad:
            ledger("Model audit could not pin every enabled scheduled task to a valid model: %s." % ", ".join(bad))
    day = dt.datetime.now(ET).date()
    item = ("**scheduled-task-model-audit-weekly (native):** audited %d task folders, %d enabled. %s%s" % (
        len(rows), len(enabled),
        ("Changes: " + "; ".join("%s %s → %s%s" % (t, o, n, "" if ok else " (FAILED)") for t, o, n, ok in done) + ".") if done else "No changes — every enabled task already pinned to a valid model.",
        (" Fable seen in the app log (interactive or unpinned use): %s." % ", ".join(fable)) if fable else ""))
    with open(OPEN_ITEMS, "a") as f:
        f.write("| %s | 1 — Valley Pawn | %s | %s | %s |\n" % (day, item, "DONE" if not done or all(d[3] for d in done) else "OPEN",
                                                              "none" if not done else "spot-check the re-pinned tasks' next runs"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        if "--send" in sys.argv:
            ledger("Weekly model audit did not complete (%s)." % type(e).__name__)
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
