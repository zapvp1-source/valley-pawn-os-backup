#!/usr/bin/env python3
"""bonus_month_close.py [YYYY-MM] [--render] — native `bonus-month-close` (10th 09:00 ET; wave 3 second pass, 2026-10-20).
DM to Joshua ONLY (bonus_rules.json field_posting is false — read every run; a true flag is NOT acted on here, it holds).

What runs natively (no Gusto):
  2  reviews -> Bonus Program/data/<M>/reviews.json from the Chekkit LEADERBOARD API (reviews_weekly.leaderboard — the
     same numbers the dashboard's Location Leaderboard shows; window = the rules' "1st through the 30th"). Never
     overwrites a reviews.json already there (a human/Cowork read wins).
  3  Facebook follower gains: the Aug-2026 regime's FB qualifier is null (never implemented — bonus_rules.json), so
     fb_gains.json is not needed; if a later regime turns it on, the close HOLDS (Publer analytics has no Mac path).
  5  targets.json must exist (seeded by bonus-month-close-pull)
  6  bonus_engine.py collect + close (exit 2 = HELD -> one plain sentence to Joshua, nothing else)
  7  DM = out/<M>/dm_payout.txt + the qualifier table in a code block + the SKILL's closing line
  8  RUN_LOG.md entry
  4  the roster (changed 2026-10-20, Joshua's rule: people no longer employed get no bonus, so eligibility = the
     CURRENTLY employed staff and no former-staff history is needed). Source changed 2026-10-21 (the Mac clock-in that
     wrote fleet/state/clockin/roster.json was retired): WHO is employed, their store, title and Gusto uuid all come from
     hr/ROSTER.json = Gusto list_employees(terminated=false), rewritten daily 06:15 by the cloud "Staff roster refresh
     (Gusto -> Slack)" task. Gusto active = employed. Older than 2 days at run time (its "generated_at", else its
     mtime) = HOLD: one ledger row, no DM, no payout. A titled Manager's hire date (manager full-month rule,
     unchanged) comes from the earlier Gusto pulls in Bonus Program/data/*/roster.json.
     HOLD (one ledger row) if: hr/ROSTER.json is unreadable, stale or lists too few store people; a store person has
     no Gusto uuid; a Manager has no known hire date; or (after collect) a Bravo seller with gross profit matches
     a current employee by LAST NAME ONLY — without former staff in the roster the engine's last-name fallback could
     otherwise pay a current employee for a former employee's sales. Sellers not on the current roster are not paid
     (the engine lists them under Gaps as "not on the current staff roster").
     The written file is data/<M>/roster.json (any earlier one is kept as roster.json.bak-<stamp>).
--render: runs `close` (not collect) on a COPY of Bonus Program (fleet/test_output/bonus_close_render_<M>/), so the real
out/<M> is never touched; prints the DM. For 2026-09 that reproduces the 10/15 close.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "bonus-month-close"
BONUS = os.path.join(L.PROJ, "Bonus Program")
ENGINE = os.path.join(BONUS, "bin", "bonus_engine.py")
CLOSING = "Nothing has gone to the team. Reply *approve* to load these into the payday payroll, or *hold*."
HOLD_LINE = "The bonus numbers for %s are on hold for now — I'll follow up once they're complete."


def reviews(month, ddir, render):
    p = os.path.join(ddir, "reviews.json")
    if os.path.exists(p):
        return "kept existing reviews.json"
    import reviews_weekly as rw
    _, first, last, _ = L.months(month)
    to = min(last, first + dt.timedelta(days=29))
    out = {}
    for s in L.STORES:
        tok = rw.token(s)
        _, loc = rw.leaderboard(tok, first.isoformat(), to.isoformat())
        out[s] = int((loc.get("reviews") or {}).get("total") or 0)
    out["_source"] = "Chekkit leaderboard API, %s..%s, read %s (native)" % (first, to, L.now().date())
    if not render:
        json.dump(out, open(p, "w"), indent=1)
    return "reviews %s" % {k: v for k, v in out.items() if k != "_source"}


HR_ROSTER = os.path.join(L.OS_DIR, "hr", "ROSTER.json")   # Gusto ACTIVE roster (cloud roster refresh, daily 06:15)
ROSTER_MAX_DAYS = 2
STORE_DEPTS = set(L.NAMES.values())


def _engine():
    sys.path.insert(0, os.path.join(BONUS, "bin"))
    import bonus_engine as E
    return E


def build_roster(ddir, rules):
    """Engine roster from the CURRENT staff only (Gusto active = employed). Returns (problem or None, note)."""
    now = L.now()
    try:
        hr = json.load(open(HR_ROSTER))
        emps = hr.get("employees") or []
    except Exception as e:
        return "the Gusto staff roster could not be read (%s)" % type(e).__name__, ""
    try:
        gen = dt.datetime.fromisoformat(hr["generated_at"])
        if gen.tzinfo is None:
            gen = gen.replace(tzinfo=dt.timezone.utc)
        asof = gen.astimezone(now.tzinfo).date() if now.tzinfo else gen.date()
    except Exception:
        asof = dt.date.fromtimestamp(os.path.getmtime(HR_ROSTER))
    age = (now.date() - asof).days
    if age > ROSTER_MAX_DAYS:
        return "the Gusto staff roster is from %s (%d days old, limit %d), so it held rather than guess who is employed" % (asof, age, ROSTER_MAX_DAYS), ""
    if sum(1 for e in emps if e.get("department") in STORE_DEPTS) < 5:
        return "the Gusto staff roster lists too few store people to trust", ""
    hire = {}
    for m in sorted(os.listdir(os.path.join(BONUS, "data"))):
        p = os.path.join(BONUS, "data", m, "roster.json")
        if len(m) == 7 and os.path.exists(p):
            try:
                for e in json.load(open(p)):
                    if e.get("uuid") and e.get("hire_date"):
                        hire[e["uuid"]] = e["hire_date"]
            except Exception:
                pass
    out, nouuid, nohire = [], [], []
    for e in sorted(emps, key=lambda x: x.get("name") or ""):
        parts = (e.get("name") or "").split()
        if not parts:
            continue
        first, last = parts[0], " ".join(parts[1:])
        dept = e.get("department") or ""
        display = "%s %s" % (e.get("preferred") or first, last)
        if not e.get("gusto_uuid"):
            if dept in STORE_DEPTS:
                nouuid.append("%s (%s)" % (display, dept))
            continue
        hd = hire.get(e["gusto_uuid"])
        if dept in STORE_DEPTS and e.get("title") in rules["eligibility"]["manager_titles"] and not hd:
            nohire.append(display)
        out.append({"uuid": e["gusto_uuid"], "first_name": first, "last_name": last,
                    "preferred_first_name": e.get("preferred") or "", "display": display, "department": dept,
                    "title": e.get("title") or "", "hire_date": hd, "terminated": False,
                    "termination_date": None, "_source": "hr/ROSTER.json (Gusto active) %s" % asof})
    if nouuid:
        return "store staff in the Gusto staff roster have no Gusto id: %s" % ", ".join(nouuid), ""
    if nohire:
        return "no hire date on file for manager(s) %s, so the full-month manager rule cannot be checked" % ", ".join(nohire), ""
    p = os.path.join(ddir, "roster.json")
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak-" + now.strftime("%Y%m%d-%H%M%S"))
    json.dump(out, open(p, "w"), indent=1)
    return None, "roster: %d current staff from the Gusto active roster dated %s" % (len(out), asof)


def lastname_only(ddir, rules):
    """Bravo sellers with GP > 0 whose only roster match is by last name (the engine's fallback)."""
    E = _engine()
    roster = json.load(open(os.path.join(ddir, "roster.json")))
    emap = rules.get("_employee_map", {})

    class C:
        pass
    ctx = C(); ctx.data = ddir; ctx.rules = rules
    bad = []
    for s in L.STORES:
        _, act = E.read_employee_activity(ctx, s)
        for code, a in (act or {}).items():
            if code in rules["bravo_ignore_codes"] or code in emap or a["retail_gp"] <= 0:
                continue
            parts = a["name"].replace(",", " ").split()
            if not parts:
                continue
            first, last = E.norm(parts[0]), E.norm(parts[-1])
            exact = any(E.norm(e["last_name"]) == last and (E.norm(e["first_name"]) == first or E.norm(e.get("preferred_first_name")) == first
                        or E.norm(e["first_name"]).startswith(first) or first.startswith(E.norm(e["first_name"]))) for e in roster)
            if not exact and any(E.norm(e["last_name"]) == last for e in roster):
                bad.append("%s %s (%s)" % (s, a["name"], code))
    return bad


def payout_people_check(dm, gusto_csv):
    """Fleet-wide rule 2026-10-21 (bin/vp_people.py): every PAYEE named in the payout DM / Gusto lines must be a
    current, non-Davis employee. Returns the offending names (empty = fine). Gap lines (unpaid former sellers) are
    not payees and are left as the engine writes them. RosterHold -> reported as a problem (= hold)."""
    import re
    import vp_people
    names = []
    for line in dm.splitlines():
        m = re.match(r"\s*[•\-]\s*(.+?)\s*\([^)]*\):\s*\$", line)
        if m and "×" in line:
            names.append(m.group(1))
    if os.path.exists(gusto_csv):
        import csv
        for r in csv.DictReader(open(gusto_csv, newline="", encoding="utf-8-sig")):
            n = " ".join(x for x in (r.get("first_name") or r.get("First Name") or "", r.get("last_name") or r.get("Last Name") or "") if x).strip() \
                or (r.get("name") or r.get("Name") or r.get("employee") or "").strip()
            if n:
                names.append(n)
    try:
        return sorted({n for n in names if not vp_people.is_reportable(n)})
    except vp_people.RosterHold as e:
        return ["(roster: %s)" % e]


def run(stage, month, root):
    return subprocess.run([sys.executable, ENGINE, stage, "--month", month, "--root", root], capture_output=True, text=True, timeout=1800)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    month = args[0] if args else L.prev_month()
    _, _, _, label = L.months(month)
    rules = json.load(open(os.path.join(BONUS, "bonus_rules.json")))
    fp = rules.get("field_posting")
    if (fp.get("enabled") if isinstance(fp, dict) else fp):
        print("HOLD: field_posting is enabled")
        L.ledger(TASK, "field_posting is on in the bonus rules; the native close only DMs Joshua, so it held", "yes, decide where the bonus close posts")
        return 3
    root = BONUS
    if render:
        root = os.path.join(L.TEST_OUT, "bonus_close_render_%s" % month)
        shutil.rmtree(root, ignore_errors=True)
        os.makedirs(os.path.join(root, "data"))
        shutil.copy2(os.path.join(BONUS, "bonus_rules.json"), root)
        shutil.copytree(os.path.join(BONUS, "data", month), os.path.join(root, "data", month))
        for f in ("history.json",):
            if os.path.exists(os.path.join(BONUS, "data", f)):
                shutil.copy2(os.path.join(BONUS, "data", f), os.path.join(root, "data", f))
    ddir = os.path.join(root, "data", month)
    notes = []
    problem, rnote = build_roster(ddir, rules)
    if problem:
        L.ledger(TASK, "the %s bonus close held: %s" % (label, problem), "yes") if not render else None
        print("HOLD (roster):", problem)
        return 3
    notes.append(rnote)
    if not os.path.exists(os.path.join(ddir, "targets.json")):
        L.ledger(TASK, "the %s bonus close has no targets file, so it held" % label) if not render else None
        print("HOLD: no targets.json")
        return 3
    try:
        notes.append(reviews(month, ddir, render))
    except Exception as e:
        notes.append("reviews not read (%s) — engine holds the reviews qualifier" % type(e).__name__)
    if not render:
        c = run("collect", month, root)
        notes.append("collect exit %d" % c.returncode)
        if c.returncode == 2:
            L.post(TASK, L.JOSHUA, HOLD_LINE % label, render, label="hold")
            return 2
    amb = lastname_only(ddir, rules)
    if amb:
        L.ledger(TASK, "the %s bonus close held: Bravo seller(s) %s match a current employee by last name only, so their sales could be paid to the wrong person" % (label, "; ".join(amb)), "yes") if not render else None
        print("HOLD (last-name-only match):", amb)
        return 3
    r = run("close", month, root)
    notes.append("close exit %d" % r.returncode)
    print("\n".join(notes))
    if r.returncode == 2:
        L.post(TASK, L.JOSHUA, HOLD_LINE % label, render, label="hold")
        return 2
    if r.returncode != 0:
        L.ledger(TASK, "the %s bonus close did not finish" % label) if not render else None
        print(r.stderr[-1500:])
        return 1
    odir = os.path.join(root, "out", month)
    dm = open(os.path.join(odir, "dm_payout.txt")).read().strip()
    bad = payout_people_check(dm, os.path.join(odir, "gusto_lines.csv"))
    if bad:
        # fleet-wide rule (Joshua 2026-10-21): never drop money silently — a Davis / non-current payee = HOLD
        L.ledger(TASK, "the %s bonus close held: payout line(s) for %s are not current non-Davis staff per vp_people" % (label, "; ".join(bad)), "yes") if not render else None
        print("HOLD (payee not reportable):", bad)
        return 3
    q = open(os.path.join(odir, "slack_qualifiers.txt")).read().strip()
    if "```" not in q:
        q = "```\n%s\n```" % q
    text = "%s\n\n%s\n\n%s" % (dm, q, CLOSING)
    ok = L.post(TASK, L.JOSHUA, text, render, label="joshua")
    if ok is True and not render:   # 'DRYRUN' = diverted by the publish guard, nothing logged as sent
        with open(os.path.join(BONUS, "RUN_LOG.md"), "a") as f:
            f.write("\n## %s — %s close (native bonus-month-close)\n%s\nDM sent to Joshua; nothing posted to the field.\n"
                    % (L.now().strftime("%Y-%m-%d %H:%M ET"), label, "\n".join("- " + n for n in notes)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
