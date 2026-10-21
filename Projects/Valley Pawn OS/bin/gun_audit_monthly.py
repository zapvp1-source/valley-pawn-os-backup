#!/usr/bin/env python3
"""gun_audit_monthly.py [--period YYYY-MM] [--render] [--no-sheet] — native `monthly-gun-audit-report`
(16th of month 02:30 ET; Mac-first wave 3 second pass, 2026-10-20). The SKILL's steps:
  1  read #monthly-gun-audit (C07CPN020G0) as the ops bot from the 20th of the audited month through now; every
     message with an image/PDF attachment is a candidate form (files:read)
  2  each form is read ONCE by bin/vp_ai.py (claude-sonnet-5-5, vision; PDFs as document blocks): store, date, auditor,
     forms checked, errors found, errors corrected, the month audited. Cached per Slack file id in
     fleet/state/gun_audit/<period>.json, so a re-run never re-reads (and never re-bills) a form. The store comes from
     the FORM; if the form has no readable store, from the poster's roster store. One form per store — the newest post
     wins. submitted = the Slack post date (ET); on or before the 15th of the run month = on time.
  3  the "Valley Pawn Trends" sheet (Sheets API, Website/analytics/bin/google_auth spreadsheets scope): Submission
     Tracker / Audit Metrics / Location Summary / Key Takeaways — rolling 12 months (see sheet_update()). --render
     prints the planned writes and changes nothing; --no-sheet skips it.
  4  Compliance/bin/gun_audit_format.py owns the message: exit 0 -> post stdout VERBATIM to the channel; exit 2 -> post
     nothing, one ledger row (failure policy v3; the SKILL's old "one line to Joshua" is void).
  5  "Still to fix" non-empty -> ONE DM per affected store manager (hr/ROSTER.json title Manager + department = store;
     none -> Preston) asking for the correction status of those forms. Never in the channel.
Duplicate guard: "Monthly Gun Audit Summary — <Month Year>" already in the channel in the last 25 days = stop.
"""
import base64
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "monthly-gun-audit-report"
CH = "C07CPN020G0"
FORMATTER = os.path.join(L.PROJ, "Compliance", "bin", "gun_audit_format.py")
STATE = os.path.join(L.OS_DIR, "fleet", "state", "gun_audit")
ROSTER = os.path.join(L.OS_DIR, "hr", "ROSTER.json")
TRENDS = "1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s"
ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
DEFAULT_PERSON = {"Waynesboro": "Chad", "Harrisonburg": "Andrew Clark", "Culpeper": "Martin D. / Bree Grayson",
                  "Roanoke": "Benjie Moore", "Lexington": "Uriah"}
PRESTON = "U03BWMEM9GR"
SYSTEM = ("You read photographed or scanned monthly firearm-form audit sheets from a pawn shop. Read only what is "
          "written on the form. Never guess a number you cannot read — use null.")
PROMPT = """This is one store's monthly gun audit form (Valley Pawn; stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke).
Return ONLY a JSON object:
{"is_audit_form": true/false, "store": "<one of the five store names, or null if not written>",
 "form_date": "<the date written on the form, YYYY-MM-DD, or null>", "audit_month": "<the month the audit covers, YYYY-MM, or null>",
 "auditor": "<auditor name exactly as written, or null>", "forms_checked": <int or null>, "errors_found": <int or null>,
 "errors_corrected": <int or null>, "notes": "<short notes text or empty>", "confidence": "high|medium|low"}"""


def run_month(period):
    y, m = map(int, period.split("-"))
    return dt.date(y + (m == 12), m % 12 + 1, 1)


def roster():
    try:
        return json.load(open(ROSTER)).get("employees", [])
    except (OSError, ValueError):
        return []


def store_of_user(uid):
    for e in roster():
        if e.get("slack_id") == uid and e.get("department") in ORDER:
            return e["department"]
    return None


def manager_of(store):
    for e in roster():
        if e.get("department") == store and "manager" in (e.get("title") or "").lower() and e.get("slack_id"):
            return e["slack_id"], e.get("preferred") or (e.get("name") or "").split()[0]
    return PRESTON, None


def read_form(f):
    mime = f.get("mimetype") or ""
    data = base64.b64encode(L.download(f)).decode()
    if mime == "application/pdf":
        block = {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}
    elif mime in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        block = {"type": "image", "source": {"type": "base64", "media_type": mime, "data": data}}
    else:
        return {"is_audit_form": False, "skip": "unsupported type %s" % mime}
    return L.ask_json(PROMPT, system=SYSTEM, max_tokens=800, content=[block, {"type": "text", "text": PROMPT}])


def collect(period, render):
    rm = run_month(period)
    _, first, last, label = L.months(period)
    oldest = L.ts_of(dt.date(first.year, first.month, 20))
    latest = "%.6f" % L.now().timestamp()
    if rm < L.now().date().replace(day=1):          # a past cycle (render/parity): stop at the 16th of the run month
        latest = L.ts_of(rm.replace(day=16), end=True)
    os.makedirs(STATE, exist_ok=True)
    cpath = os.path.join(STATE, "%s.json" % period)
    cache = json.load(open(cpath)) if os.path.exists(cpath) else {}
    msgs = L.history(CH, oldest, latest)
    names = L.users()
    by_store = {}
    for m in msgs:
        for f in m.get("files") or []:
            fid = f.get("id")
            if fid not in cache:
                try:
                    cache[fid] = read_form(f)
                except Exception as e:                  # one unreadable file never sinks the run; it is simply not counted
                    cache[fid] = {"is_audit_form": False, "error": "%s: %s" % (type(e).__name__, str(e)[:120])}
                cache[fid]["_name"] = f.get("name")
                json.dump(cache, open(cpath, "w"), indent=1)
            r = dict(cache[fid])
            if not r.get("is_audit_form"):
                continue
            posted = dt.datetime.fromtimestamp(float(m["ts"]), L.ET).date()
            # Stores post the audited month's forms in the first half of the run month (Sept forms: Oct 5-13). A form
            # posted from the 1st of the run month counts for this cycle; one posted late in the audited month counts
            # only when the form itself says it covers that month (an early submission).
            if posted < rm and r.get("audit_month") != period:
                continue
            store = r.get("store") if r.get("store") in ORDER else store_of_user(m.get("user"))
            if not store:
                continue
            r.update({"store": store, "posted": posted.isoformat(), "poster": names.get(m.get("user"), ""), "ts": m["ts"]})
            if store not in by_store or float(m["ts"]) > float(by_store[store]["ts"]):
                by_store[store] = r
    return by_store, label, rm


def person(r):
    """The name in the post = the submitter as the team knows them. Parity with the 10/16 live post: handwriting is
    misread ("Martin Dowder", "Walker Topley"), the Slack name is not. When the form's auditor and the poster share a
    first name, the shorter wins (ties -> the Slack name): Martin D., Walker Tapley, Uriah, Benjie."""
    a = (r.get("auditor") or "").strip()
    p = (r.get("poster") or "").strip()
    if a and p and a.split()[0].lower() == p.split()[0].lower():
        return a if len(a) < len(p) else p
    return p or a or DEFAULT_PERSON.get(r.get("store"), "")


def fmt_input(period, by_store, label, rm):
    stores = []
    for s in ORDER:
        r = by_store.get(s)
        if not r:
            stores.append({"store": s, "person": DEFAULT_PERSON[s], "submitted": None})
        else:
            stores.append({"store": s, "person": person(r), "submitted": r["posted"], "forms_checked": r.get("forms_checked"),
                           "errors_found": r.get("errors_found"), "errors_corrected": r.get("errors_corrected")})
    return {"period": label, "deadline": rm.replace(day=15).isoformat(), "stores": stores}


def sheet_update(period, inp, render):
    """Rolling-12 update of the Trends sheet through the Sheets API. Additive: reads every tab first, writes only the
    cells the SKILL names. Any API failure = a ledger row, never a reason to hold the post."""
    import gun_audit_sheet
    return gun_audit_sheet.update(TRENDS, period, inp, render)


def main():
    render = "--render" in sys.argv
    period = sys.argv[sys.argv.index("--period") + 1] if "--period" in sys.argv else L.prev_month()
    _, _, _, label = L.months(period)
    marker = "Monthly Gun Audit Summary — %s" % label
    if not render and L.already(CH, marker, 24 * 25):
        print("already posted:", marker)
        return 0
    by_store, label, rm = collect(period, render)
    inp = fmt_input(period, by_store, label, rm)
    print("FORMS:", json.dumps({s: {k: by_store[s].get(k) for k in ("posted", "auditor", "poster", "forms_checked",
                                                                         "errors_found", "errors_corrected", "audit_month", "confidence")}
                                for s in by_store}, indent=1))
    low = [s for s, r in by_store.items() if r.get("confidence") == "low" or any(r.get(k) is None for k in ("forms_checked", "errors_found", "errors_corrected"))]
    if low:
        L.ledger(TASK, "the %s gun audit form could not be read clearly, so the %s summary was held" % (", ".join(low), label))
        print("HELD (unreadable):", low)
        return 3
    fp = os.path.join(STATE, "%s_format_input.json" % period)
    json.dump(inp, open(fp, "w"), indent=1)
    r = subprocess.run(["/usr/bin/python3", FORMATTER, "--file", fp], capture_output=True, text=True)
    if r.returncode != 0:
        L.ledger(TASK, "the %s gun audit summary was held because the numbers did not check out" % label)
        print("FORMATTER exit", r.returncode, r.stderr.strip())
        return 2
    body = r.stdout.strip()
    if "--no-sheet" not in sys.argv:
        try:
            for line in sheet_update(period, inp, render):
                print("SHEET", line)
        except Exception as e:
            if not render:
                L.ledger(TASK, "the Trends sheet was not updated for %s (the post still went out)" % label,
                         "yes, share the Valley Pawn Trends sheet with jdavis@fcfpawn.com as Editor" if isinstance(e, PermissionError) else "no")
            print("SHEET ERROR", type(e).__name__, str(e)[:300])
    ok = L.post(TASK, CH, body, render)
    for s in inp["stores"]:
        if s.get("submitted") and (s.get("errors_found") or 0) > (s.get("errors_corrected") or 0):
            uid, first = manager_of(s["store"])
            open_n = s["errors_found"] - s["errors_corrected"]
            who = "Hey %s" % first if first else "Hey Preston"
            where = "" if first else " for %s" % s["store"]
            txt = ("%s, quick one on the %s gun audit%s: %d of the %d errors found are not marked corrected yet. "
                   "Can you get those forms fixed and let me know when they're done?" % (who, label.split()[0], where, open_n, s["errors_found"]))
            L.post(TASK, uid, txt, render, label="chase-%s" % s["store"].lower())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
