#!/usr/bin/env python3
"""
gun_audit_format.py — deterministic Slack body for the monthly gun audit summary.

WHY: the summary was re-rendered as free text by the model every month. That drifted (missing
header rows, mis-mapped columns, a Drive link posted into a staff channel) and on 2026-08-16 the
run produced nothing at all. This file owns the message. The task extracts the numbers; this
prints the post.

INPUT  (stdin or --file): JSON
{
  "period": "August 2026",          # the AUDIT period the forms cover
  "deadline": "2026-09-15",         # submissions on/before this date are on time
  "stores": [
    {"store": "Culpeper", "person": "Bree", "submitted": "2026-09-03",
     "forms_checked": 133, "errors_found": 4, "errors_corrected": 0}
    ...5 rows...
  ]
}
A store that did not submit: {"store": "...", "person": "...", "submitted": null}

OUTPUT: the exact Slack message on stdout, exit 0.
On ANY validation failure: prints NOTHING to stdout, reason to stderr, exit 2 (WITHHOLD — Rule 18).

Gates (all must pass):
  - exactly the 5 known stores, no duplicates
  - every submitted store has non-negative integers for the three counts
  - forms_checked > 0 where a submission exists
  - errors_found <= forms_checked   (the mis-mapped-column class of bug)
  - errors_corrected <= errors_found
  - period and deadline parse
Rule 13: never emits a Drive/Sheets/Docs link — the channel has store staff in it.
Rule 16: never emits pipeline/tool words or failure text.
"""
import json, sys, datetime as dt

STORES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
BANNED = ("docs.google.com", "drive.google.com", "spreadsheets", "Bravo", "Cowork", "Chekkit",
          "Gusto", "pipeline", "handler", "watchdog", "CSV", "export", "task")


def fail(msg):
    sys.stderr.write("WITHHOLD: %s\n" % msg)
    sys.exit(2)


def load():
    raw = sys.stdin.read() if len(sys.argv) < 3 else open(sys.argv[2]).read()
    if "--file" in sys.argv and len(sys.argv) > sys.argv.index("--file") + 1:
        raw = open(sys.argv[sys.argv.index("--file") + 1]).read()
    try:
        return json.loads(raw)
    except Exception as e:
        fail("input is not valid JSON (%s)" % e)


def main():
    d = load()
    try:
        deadline = dt.date.fromisoformat(d["deadline"])
    except Exception:
        fail("deadline missing or not YYYY-MM-DD")
    period = str(d.get("period", "")).strip()
    if not period:
        fail("period missing")

    rows = d.get("stores") or []
    names = [r.get("store") for r in rows]
    if sorted(names) != sorted(STORES):
        fail("expected exactly these 5 stores, got %r" % names)

    clean = []
    for r in rows:
        s = r["store"]
        sub = r.get("submitted")
        if not sub:
            clean.append({"store": s, "person": r.get("person", ""), "sub": None})
            continue
        try:
            subd = dt.date.fromisoformat(sub)
        except Exception:
            fail("%s: submitted date not YYYY-MM-DD (%r)" % (s, sub))
        try:
            fc = int(r["forms_checked"]); ef = int(r["errors_found"]); ec = int(r["errors_corrected"])
        except Exception:
            fail("%s: forms_checked / errors_found / errors_corrected must be integers" % s)
        if min(fc, ef, ec) < 0:
            fail("%s: negative count" % s)
        if fc == 0:
            fail("%s: submitted but forms_checked is 0" % s)
        if ef > fc:
            fail("%s: errors_found (%d) exceeds forms_checked (%d) — columns look mis-mapped" % (s, ef, fc))
        if ec > ef:
            fail("%s: errors_corrected (%d) exceeds errors_found (%d)" % (s, ec, ef))
        clean.append({"store": s, "person": r.get("person", ""), "sub": subd,
                      "fc": fc, "ef": ef, "ec": ec, "rate": (ef / fc) * 100})

    order = {s: i for i, s in enumerate(STORES)}
    clean.sort(key=lambda r: order[r["store"]])
    submitted = [r for r in clean if r["sub"]]
    missing = [r for r in clean if not r["sub"]]
    ontime = [r for r in submitted if r["sub"] <= deadline]

    out = []
    out.append("*Monthly Gun Audit Summary — %s*" % period)
    out.append("")
    if missing:
        out.append("%d of 5 stores submitted. Still needed: %s." %
                   (len(submitted), ", ".join(r["store"] for r in missing)))
    else:
        out.append("All 5 stores submitted%s." % ("" if len(ontime) == 5 else ", %d on time" % len(ontime)))
    out.append("")
    out.append("*Submissions*")
    for r in clean:
        if not r["sub"]:
            out.append("• %s (%s) — not submitted" % (r["store"], r["person"]))
        else:
            tag = "on time" if r["sub"] <= deadline else "late"
            out.append("• %s (%s) — %s, %s" % (r["store"], r["person"], r["sub"].strftime("%b %-d"), tag))
    out.append("")
    out.append("*Error rates*")
    for r in sorted(submitted, key=lambda r: r["rate"]):
        out.append("• %s — %d forms checked, %d errors, %d corrected (%.2f%%)" %
                   (r["store"], r["fc"], r["ef"], r["ec"], r["rate"]))

    open_err = [r for r in submitted if r["ef"] > r["ec"]]
    if open_err:
        out.append("")
        out.append("*Still to fix*")
        for r in open_err:
            out.append("• %s — %d of %d errors not yet corrected" % (r["store"], r["ef"] - r["ec"], r["ef"]))

    body = "\n".join(out)
    low = body.lower()
    for b in BANNED:
        if b.lower() in low:
            fail("output contains a banned term (%r) — Rule 13/16" % b)
    print(body)


if __name__ == "__main__":
    main()
