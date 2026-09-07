#!/usr/bin/env python3
"""Compliance Brief — Valley Pawn (native, additive, 2026-09-06).

Runs OUTSIDE Claude (pure stdlib Python via launchd) so it keeps working when the
Cowork fleet is saturated — the same pattern as ffl_guardian.py and the fleet
health sentinel. Zero new Cowork scheduled tasks (the fleet is at ~148 enabled
tasks with thousands of queue-wait skips a week).

WHAT IT OWNS
  The dates nobody was watching: surety bonds, local precious-metals and
  pawnbroker permits, business licenses (BPOL), tax filings, lease notice
  windows, entity/SCC, HR-compliance filings, and the "unknown annual" rows
  recovered from Apple Reminders. Source of truth:
      Projects/Compliance/OBLIGATIONS.json   (rendered by Compliance/bin/render_calendar.py)

WHAT IT DELIBERATELY DOES NOT OWN (no duplicate warnings)
  - FFL expirations / vendor copies / directory listings -> ffl_guardian.py
    (its own 120/90/60/30/14 ladder). This brief only ECHOES ffl_status.json.
  - Insurance renewals -> the insurance department's own registry + runner.
    This brief only echoes the next renewal from INSURANCE_REGISTRY.json.

OUTPUT
  ONE plain-language Slack DM to Joshua, Mondays 7:30 AM ET. Rule 16: no
  technical words, no failure notices, nothing about this script. Rule 18: a
  section is omitted entirely rather than shown partial. If nothing is due and
  nothing is past due, it sends nothing at all.
  Full detail (including integrity problems) goes to the run file, never Slack:
      Projects/Compliance/state/brief_YYYY-MM-DD.md

Run manually:  python3 compliance_brief.py [--dry-run] [--force]
                 --dry-run  print the DM instead of sending
                 --force    send even when there is nothing notable
"""

import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

HOME = os.path.expanduser("~")
COMPLIANCE = os.path.join(HOME, "Documents/Claude/Projects/Compliance")
REGISTER = os.path.join(COMPLIANCE, "OBLIGATIONS.json")
RENDERER = os.path.join(COMPLIANCE, "bin/render_calendar.py")
STATE_DIR = os.path.join(COMPLIANCE, "state")
FFL_STATUS = os.path.join(COMPLIANCE, "ffl_status.json")
INSURANCE = os.path.join(HOME, "Documents/Claude/Projects/Life OS/Insurance/INSURANCE_REGISTRY.json")
LOG = os.path.join(HOME, "Library/Logs/valleypawn/compliance-brief.log")

JOSHUA_DM = "D03BHQH5VGT"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"

DRY = "--dry-run" in sys.argv
FORCE = "--force" in sys.argv
TODAY = dt.date.today()

STORE = {"culpeper": "Culpeper", "waynesboro": "Waynesboro", "harrisonburg": "Harrisonburg",
         "lexington": "Lexington", "roanoke": "Roanoke", "all": "All stores", "entity": "The company"}

# Classes this brief warns on. FFL and insurance are owned elsewhere (echo only).
OWNED = {"bond", "local-permit", "business-license", "tax", "lease", "entity", "hr",
         "records-control", "unknown-annual", "state-firearms"}

# Rows the FFL department owns (ffl_guardian.py warns on these) — never warned on twice.
def ffl_owned(rid):
    return rid.startswith("ffl-")

# Rule 16: nothing technical ever reaches Slack. Any line containing one of these
# is replaced by the row's plain `ask`/`label`, or dropped.
BANNED = ("chrome", "password", "bravo", "cowork", "gusto", "chekkit", "brevo", "qbo",
          "pipeline", "handler", "watchdog", "csv", "export", "blocked", "failed",
          "error", "task ", "script", "json", "api", "sync", "pull ")


def clean(text):
    low = (text or "").lower()
    return not any(b in low for b in BANNED)


def log(msg):
    line = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str(msg)
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        log("could not read %s (%s)" % (path, e))
        return default


def get_token():
    try:
        return subprocess.check_output(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            text=True).strip()
    except Exception as e:
        log("slack token unavailable: %s" % e)
        return None


def slack_dm(text):
    token = get_token()
    if not token:
        return False
    payload = json.dumps({"channel": JOSHUA_DM, "text": text}).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage", data=payload,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json; charset=utf-8"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        if not r.get("ok"):
            log("slack refused: %s" % r.get("error"))
        return bool(r.get("ok"))
    except Exception as e:
        log("slack send failed: %s" % e)
        return False


def days_to(d):
    try:
        return (dt.date.fromisoformat(d) - TODAY).days
    except Exception:
        return None


def render():
    """Re-render the calendar so the brief and the file can never disagree."""
    try:
        subprocess.run([sys.executable, RENDERER], check=False,
                       capture_output=True, timeout=120)
    except Exception as e:
        log("renderer did not run: %s" % e)


def classify(rows):
    past, soon, ahead, unknown, joshua, problems = [], [], [], [], [], []
    for r in rows:
        cls = r.get("class")
        d = days_to(r.get("due"))
        st = r.get("status")
        if st == "current" and not r.get("evidence"):
            problems.append("%s: marked current with nothing on file to prove it" % r["id"])
        if cls not in OWNED or ffl_owned(r.get("id", "")):
            continue
        if st == "closed":
            continue
        if d is None:
            if st == "unknown":
                unknown.append(r)
            continue
        if d < 0 and st not in ("in-progress",):
            past.append((d, r))
        elif d <= 30:
            soon.append((d, r))
        elif d <= r.get("lead_days", 30):
            ahead.append((d, r))
        if r.get("owner") == "joshua" and (d is not None and d <= 30):
            joshua.append((d, r))
    past.sort(key=lambda x: x[0]); soon.sort(key=lambda x: x[0])
    ahead.sort(key=lambda x: x[0]); joshua.sort(key=lambda x: x[0])
    return past, soon, ahead, unknown, joshua, problems


def phrase(r, d):
    when = ("%d days overdue" % abs(d)) if d < 0 else ("due today" if d == 0 else "in %d days" % d)
    what = r.get("label") or r.get("authority") or r["id"]
    if not clean(what):
        what = r.get("label") or r["id"].replace("-", " ")
    return "• %s — %s (%s)" % (STORE.get(r.get("store"), r.get("store")), what, when)


def build(rows):
    past, soon, ahead, unknown, joshua, problems = classify(rows)
    out = ["*Compliance — week of %s*" % TODAY.strftime("%B %-d")]

    if past:
        out.append("")
        out.append("*Overdue*")
        out += [phrase(r, d) for d, r in past[:10]]
    if soon:
        out.append("")
        out.append("*Coming up in the next 30 days*")
        out += [phrase(r, d) for d, r in soon[:12]]
    if ahead:
        out.append("")
        out.append("*On the horizon*")
        out += [phrase(r, d) for d, r in ahead[:8]]

    if joshua:
        out.append("")
        out.append("*Needs you* (payment, signature, or a decision)")
        for d, r in joshua[:8]:
            ask = r.get("ask")
            if not ask:
                step = (r.get("next_step") or "").split(".")[0]
                ask = step if clean(step) else (r.get("label") or r["id"].replace("-", " "))
            out.append("• %s — %s" % (STORE.get(r.get("store"), r.get("store")), ask))

    # Echo-only sections: owned by other departments, shown so Monday is one view.
    ffl = load(FFL_STATUS)
    if isinstance(ffl, dict) and ffl.get("next_expiration"):
        n = ffl["next_expiration"]
        out.append("")
        out.append("*Firearms licenses* — next renewal is %s, %s days out." %
                   (STORE.get(str(n.get("store", "")).lower(), n.get("store")), n.get("days")))

    if unknown:
        out.append("")
        out.append("*Still unidentified* — %d yearly items came off your old reminder list without a "
                   "label. When you have a minute, tell me what these are and I'll file them: %s." %
                   (len(unknown), ", ".join(sorted({STORE.get(r.get("store"), r.get("store")) for r in unknown}))))

    body = "\n".join(out)
    notable = bool(past or soon or joshua)
    return body, notable, {"past": past, "soon": soon, "ahead": ahead,
                           "unknown": unknown, "joshua": joshua, "problems": problems}


def write_run_file(body, detail):
    os.makedirs(STATE_DIR, exist_ok=True)
    p = os.path.join(STATE_DIR, "brief_%s.md" % TODAY.isoformat())
    with open(p, "w") as f:
        f.write("# Compliance brief — %s\n\n## Sent to Joshua\n\n%s\n" % (TODAY.isoformat(), body))
        f.write("\n## Detail (never sent to Slack)\n\n")
        for k in ("past", "soon", "ahead", "joshua"):
            f.write("### %s\n" % k)
            for d, r in detail[k]:
                f.write("- `%s` due %s (%+d d) owner=%s — %s\n" %
                        (r["id"], r.get("due"), d, r.get("owner"), r.get("next_step")))
            f.write("\n")
        f.write("### unknown\n")
        for r in detail["unknown"]:
            f.write("- `%s` — %s\n" % (r["id"], r.get("next_step")))
        f.write("\n### integrity problems\n")
        for p2 in detail["problems"]:
            f.write("- %s\n" % p2)
    return p


def main():
    reg = load(REGISTER)
    if not reg or "obligations" not in reg:
        log("register unreadable — nothing sent (Rule 18)")
        return 2
    render()
    body, notable, detail = build(reg["obligations"])
    path = write_run_file(body, detail)
    log("run file: %s" % path)
    if DRY:
        print("\n----- DM preview -----\n" + body)
        return 0
    if not notable and not FORCE:
        log("nothing overdue or due inside 30 days — no DM sent")
        return 0
    ok = slack_dm(body)
    log("DM sent" if ok else "DM not sent (detail in this log only, never Slack)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
