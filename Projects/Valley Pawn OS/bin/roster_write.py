#!/usr/bin/env python3
"""roster_write.py — validated writer for hr/ROSTER.json, the single staff roster every task reads.

WHY (2026-09-25): at least five hand-typed staff lists lived inside task prompts and drifted from
Gusto (departed staff still messaged, new hires missed, one person on the wrong store). ROSTER.json
is regenerated from Gusto (active employees) + Slack (user IDs matched by the Gusto email) by the
`roster-refresh` scheduled task, which hands its candidate file to this script. This script is the
only thing that writes ROSTER.json, and it refuses anything that looks like a bad pull.

    roster_write.py <candidate.json>      validate + write (prints a one-line diff)
    roster_write.py --check               exit 0 if ROSTER.json is present, valid and < 72 h old

Candidate format: {"source": "...", "employees": [ {"name","preferred","department","title",
  "email","phone","gusto_uuid","slack_id"} ... ]}   (phone = 10 digits or null; slack_id or null)

Refuses (exit 2, nothing written) when: fewer than 8 employees; any store with zero people; duplicate
gusto_uuid; a malformed slack_id; or more than 30% of the previous roster missing (a partial pull).
Keeps the previous file as ROSTER.prev.json and appends every change to hr/ROSTER_CHANGES.md.
Sensitive fields (pay, SSN, date of birth) are never accepted — unknown keys are dropped.
"""
import datetime as dt, json, os, re, sys, tempfile
OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HR = os.path.join(OS_DIR, "hr")
OUT = os.path.join(HR, "ROSTER.json")
PREV = os.path.join(HR, "ROSTER.prev.json")
LOG = os.path.join(HR, "ROSTER_CHANGES.md")
STORES = ["Culpeper", "Harrisonburg", "Lexington", "Roanoke", "Waynesboro"]
KEYS = ["name", "preferred", "department", "title", "email", "phone", "gusto_uuid", "slack_id"]

def fail(msg):
    print("REFUSED: " + msg); sys.exit(2)

def check():
    try:
        r = json.load(open(OUT))
        age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(r["generated_at"])).total_seconds() / 3600
        ok = age < 72 and len(r["employees"]) >= 8
        print("ok" if ok else "stale", "age_h=%.1f" % age, "employees=%d" % len(r["employees"]))
        sys.exit(0 if ok else 1)
    except Exception as e:
        print("missing/invalid:", type(e).__name__); sys.exit(1)

def main():
    if sys.argv[1:] == ["--check"]:
        check()
    cand = json.load(open(sys.argv[1]))
    emps = []
    for e in cand.get("employees", []):
        e = {k: e.get(k) for k in KEYS}
        if not e["gusto_uuid"] or not e["name"] or not e["department"]:
            fail("employee missing name/department/gusto_uuid: %r" % e.get("name"))
        if e["slack_id"] and not re.fullmatch(r"U[A-Z0-9]{8,11}", e["slack_id"]):
            fail("bad slack_id for %s" % e["name"])
        p = re.sub(r"\D", "", e["phone"] or "")
        e["phone"] = ("+1" + p[-10:]) if len(p) >= 10 else None
        emps.append(e)
    if len(emps) < 8:
        fail("only %d employees" % len(emps))
    ids = [e["gusto_uuid"] for e in emps]
    if len(ids) != len(set(ids)):
        fail("duplicate gusto_uuid")
    for s in STORES:
        if not any(e["department"] == s for e in emps):
            fail("no one at %s" % s)
    old = {}
    if os.path.exists(OUT):
        old = {e["gusto_uuid"]: e for e in json.load(open(OUT))["employees"]}
        missing = [u for u in old if u not in ids]
        if old and len(missing) / len(old) > 0.30:
            fail("%d of %d previous employees missing — looks like a partial pull" % (len(missing), len(old)))
    new = {e["gusto_uuid"]: e for e in emps}
    changes = []
    for u, e in new.items():
        if u not in old:
            changes.append("added %s (%s)" % (e["name"], e["department"]))
        else:
            for k in ("department", "title", "slack_id", "phone", "email"):
                if old[u].get(k) != e.get(k):
                    changes.append("%s: %s changed" % (e["name"], k))
    for u, e in old.items():
        if u not in new:
            changes.append("removed %s (%s)" % (e["name"], e["department"]))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    doc = {"generated_at": now, "source": cand.get("source", "gusto list_employees(terminated=false) + slack email match"),
           "stores": STORES, "employees": sorted(emps, key=lambda e: (e["department"], e["name"]))}
    os.makedirs(HR, exist_ok=True)
    if os.path.exists(OUT):
        os.replace(OUT, PREV)
    fd, tmp = tempfile.mkstemp(dir=HR, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(doc, f, indent=1)
    os.replace(tmp, OUT)
    if changes:
        with open(LOG, "a") as f:
            f.write("- %s: %s\n" % (now[:16].replace("T", " "), "; ".join(changes)))
    print("written: %d employees, %d on Slack, %d changes%s" % (
        len(emps), sum(1 for e in emps if e["slack_id"]), len(changes), (": " + "; ".join(changes)) if changes else ""))

if __name__ == "__main__":
    main()
