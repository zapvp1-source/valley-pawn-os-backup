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
     CURRENTLY employed staff and no former-staff history is needed). WHO is employed + their store = the active roster
     the Mac writes daily, fleet/state/clockin/roster.json (bin/clockin_check.py, Gusto time-tracking Departments page).
     Older than 2 days at run time (its "date", else its mtime) = HOLD: one ledger row, no DM, no payout. The engine
     also needs a title (Manager / associate / Market Manager / excluded) and the Gusto uuid for the payroll lines;
     those are joined by name from hr/ROSTER.json (Gusto active roster, roster-refresh). A titled Manager's hire date
     (manager full-month rule, unchanged) comes from the earlier Gusto pulls in Bonus Program/data/*/roster.json.
     HOLD (one ledger row) if: a store person on the clock-in roster has no title/uuid in hr/ROSTER.json; hr/ROSTER.json
     is older than 7 days; a Manager has no known hire date; or (after collect) a Bravo seller with gross profit matches
     a current employee by LAST NAME ONLY — without former staff in the roster the engine's last-name fallback could
     otherwise pay a current employee for a former employee's sales. Sellers not on the current roster are not paid
     (the engine lists them under Gaps as "not in Gusto roster").
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


CLOCKIN_ROSTER = os.path.join(L.OS_DIR, "fleet", "state", "clockin", "roster.json")
HR_ROSTER = os.path.join(L.OS_DIR, "hr", "ROSTER.json")
STORE_DEPTS = set(L.NAMES.values())


def _n(s):
    return "".join(c for c in (s or "").lower() if c.isalpha())


def _engine():
    sys.path.insert(0, os.path.join(BONUS, "bin"))
    import bonus_engine as E
    return E


def build_roster(ddir, rules):
    """Engine roster from the CURRENT staff only. Returns (problem or None, note)."""
    today = L.now().date()
    try:
        ck = json.load(open(CLOCKIN_ROSTER))
        people = ck.get("people") or {}
    except Exception as e:
        return "the clock-in staff roster could not be read (%s)" % type(e).__name__, ""
    try:
        asof = dt.date.fromisoformat(ck.get("date"))
    except Exception:
        asof = dt.date.fromtimestamp(os.path.getmtime(CLOCKIN_ROSTER))
    age = (today - asof).days
    if age > 2:
        return "the clock-in staff roster is from %s (%d days old, limit 2), so it held rather than guess who is employed" % (asof, age), ""
    if sum(1 for d in people.values() if d in STORE_DEPTS) < 5:
        return "the clock-in staff roster lists too few store people to trust", ""
    try:
        hr = json.load(open(HR_ROSTER))
        hr_age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(hr["generated_at"])).days
    except Exception as e:
        return "the staff titles file could not be read (%s)" % type(e).__name__, ""
    if hr_age > 7:
        return "the staff titles file is %d days old (limit 7)" % hr_age, ""
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
    idx = {}
    for e in hr.get("employees", []):
        parts = e["name"].split()
        first, last = parts[0], " ".join(parts[1:])
        for k in {_n(e["name"]), _n((e.get("preferred") or first) + last)}:
            idx[k] = (e, first, last)
    out, missing, nohire, notes = [], [], [], []
    for name, dept in sorted(people.items()):
        hit = idx.get(_n(name))
        if not hit:
            if dept in STORE_DEPTS:
                missing.append("%s (%s)" % (name, dept))
            else:
                notes.append("%s (%s) not in the titles file — skipped" % (name, dept))
            continue
        e, first, last = hit
        if e.get("department") != dept:
            notes.append("%s: clock-in store %s, titles file %s — clock-in used" % (name, dept, e.get("department")))
        hd = hire.get(e["gusto_uuid"])
        if dept in STORE_DEPTS and e.get("title") in rules["eligibility"]["manager_titles"] and not hd:
            nohire.append(name)
        out.append({"uuid": e["gusto_uuid"], "first_name": first, "last_name": last,
                    "preferred_first_name": e.get("preferred") or "", "display": name, "department": dept,
                    "title": e.get("title") or "", "hire_date": hd, "terminated": False,
                    "termination_date": None, "_source": "clock-in roster %s + hr/ROSTER.json title" % asof})
    if missing:
        return "store staff on the clock-in roster have no title in the staff titles file: %s" % ", ".join(missing), ""
    if nohire:
        return "no hire date on file for manager(s) %s, so the full-month manager rule cannot be checked" % ", ".join(nohire), ""
    p = os.path.join(ddir, "roster.json")
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak-" + L.now().strftime("%Y%m%d-%H%M%S"))
    json.dump(out, open(p, "w"), indent=1)
    return None, "roster: %d current staff from the clock-in roster dated %s%s" % (len(out), asof, ("; " + "; ".join(notes)) if notes else "")


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
    q = open(os.path.join(odir, "slack_qualifiers.txt")).read().strip()
    if "```" not in q:
        q = "```\n%s\n```" % q
    text = "%s\n\n%s\n\n%s" % (dm, q, CLOSING)
    ok = L.post(TASK, L.JOSHUA, text, render, label="joshua")
    if ok and not render:
        with open(os.path.join(BONUS, "RUN_LOG.md"), "a") as f:
            f.write("\n## %s — %s close (native bonus-month-close)\n%s\nDM sent to Joshua; nothing posted to the field.\n"
                    % (L.now().strftime("%Y-%m-%d %H:%M ET"), label, "\n".join("- " + n for n in notes)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
