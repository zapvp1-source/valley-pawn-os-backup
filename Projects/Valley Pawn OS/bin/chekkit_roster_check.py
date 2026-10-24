#!/usr/bin/env python3
"""chekkit_roster_check.py — monthly Gusto-roster vs Chekkit-users check (comms review build #3, 2026-10-23).

Reads only. Never adds or removes anyone in Chekkit (the API cannot), never messages staff.

Inputs   hr/ROSTER.json (Gusto ACTIVE, refreshed daily) via bin/vp_people.py
         GET /v1/team-members per store (Chekkit API, Keychain token per store)
Findings
  A. STILL HAS ACCESS: a Chekkit user at a store who is not on the active Gusto roster (left the company).
  B. NOT SET UP: a store employee on the Gusto roster with no Chekkit login at their own store.
  Info (file only): someone with access at a second store (covering), corporate staff, owners.
Davis family members are owners and are never listed. Corporate Support staff may have access anywhere.

  chekkit_roster_check.py [--send]
    writes hr/chekkit_roster_check/<YYYY-MM>.json + .mrkdwn.txt; --send drops ONE outbox envelope to
    Joshua's DM only when A or B is non-empty, once per month (marker). Plain business language.
Prints: MONTH=.. STILL_HAS_ACCESS=n NOT_SET_UP=n FILE=.. [SENT=..|ALREADY_SENT|SENT=none(clean)]
"""
import datetime as dt, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_ops as co  # noqa: E402
import vp_people  # noqa: E402

OS_DIR = os.path.dirname(HERE)
OUT = os.path.join(OS_DIR, "hr", "chekkit_roster_check")
OUTBOX = os.path.join(OS_DIR, "fleet", "outbox")
HOST_PROJECTS = "/Users/joshuadavis/Documents/Claude/Projects"
JOSHUA = "U03BB52MDSA"


def host_path(p):
    i = p.find("/mnt/Projects/")
    return HOST_PROJECTS + p[i + len("/mnt/Projects"):] if p.startswith("/sessions/") and i >= 0 else p


def store_of(emp):
    d = (emp.get("department") or "").strip().lower()
    return next((c for c, n in co.NAMES.items() if n.lower() == d), None)


def main(a):
    send = "--send" in a
    month = dt.date.today().strftime("%Y-%m")
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, month)
    try:
        staff = vp_people.current_staff()
    except vp_people.RosterHold as e:
        co.ledger_once("chekkit-roster-check", "The monthly Chekkit logins check was skipped: staff list not current.")
        print("HOLD", e); return 1

    members, errors = {}, {}
    for code in co.STORES:
        try:
            members[code] = co.team(code)
        except Exception as e:  # noqa: BLE001
            errors[code] = str(e)[:160]
        time.sleep(1.2)
    if errors:
        co.ledger_once("chekkit-roster-check", "The monthly Chekkit logins check could not read %s." % ", ".join(sorted(errors)))
        print("ERRORS", errors); return 1

    still, info, have = [], [], {c: set() for c in co.STORES}
    for code, ms in members.items():
        for t in ms:
            name = (t.get("name") or "").strip()
            login = co.tm_login(t)
            if vp_people.is_davis(name) or vp_people.is_davis(login) or (t.get("accessLevel") == "owner"):
                continue
            e = vp_people.resolve(name, code)
            if not e:
                still.append({"store": code, "name": name, "access": t.get("accessLevel")})
                continue
            have[code].add(e["gusto_uuid"] if e.get("gusto_uuid") else e["name"])
            home = store_of(e)
            if home is None:
                info.append("%s: %s (corporate, %s)" % (code, vp_people.display_name(name), t.get("accessLevel")))
            elif home != code:
                info.append("%s: %s also has access (home store %s)" % (code, vp_people.display_name(name), home))

    missing = []
    for e in staff:
        code = store_of(e)
        if not code or e.get("_last") == vp_people.DAVIS:
            continue
        key = e["gusto_uuid"] if e.get("gusto_uuid") else e["name"]
        if key not in have[code]:
            missing.append({"store": code, "name": vp_people.display_name(e["name"]), "title": e.get("title")})

    lines = ["*Chekkit logins check — %s*" % dt.date.today().strftime("%B %Y")]
    if still:
        lines.append("\n*Still has Chekkit access but is no longer on payroll* (remove in Chekkit → Settings → Team):")
        lines += ["• %s — %s" % (co.NAMES[s["store"]], s["name"]) for s in still]
    if missing:
        lines.append("\n*On payroll but not set up in Chekkit at their store* (add in Chekkit → Settings → Team):")
        lines += ["• %s — %s (%s)" % (co.NAMES[m["store"]], m["name"], m["title"] or "staff") for m in missing]
    if not still and not missing:
        lines.append("Every store's Chekkit users match the current staff list.")
    msg = "\n".join(lines) + "\n"
    report = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "month": month,
              "still_has_access": still, "not_set_up": missing, "info": info,
              "counts": {c: len(v) for c, v in members.items()}}
    json.dump(report, open(base + ".json", "w"), indent=1)
    open(base + ".mrkdwn.txt", "w").write(msg)
    with open(os.path.join(OUT, "RUN_LOG.md"), "a") as lg:
        lg.write("- %s still=%d not_set_up=%d\n" % (report["generated"], len(still), len(missing)))

    extra = ""
    if send:
        sent = base + ".sent"
        if not still and not missing:
            extra = " SENT=none(clean)"
        elif os.path.exists(sent):
            extra = " ALREADY_SENT"
        else:
            env = os.path.join(OUTBOX, "chekkit-roster-check-joshua-%s.json" % dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
            json.dump({"channel": JOSHUA, "file": host_path(base + ".mrkdwn.txt")}, open(env, "w"))
            open(sent, "w").write("%s %s %s via outbox\n" % (dt.datetime.now().isoformat(timespec="seconds"), JOSHUA, os.path.basename(env)))
            extra = " SENT=" + os.path.basename(env)
    print("MONTH=%s STILL_HAS_ACCESS=%d NOT_SET_UP=%d FILE=%s.mrkdwn.txt%s" % (month, len(still), len(missing), base, extra))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
