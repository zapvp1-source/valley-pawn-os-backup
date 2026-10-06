#!/usr/bin/env python3
"""bonus_pace.py [--render] [--today YYYY-MM-DD] — native `bonus-pace-monday` (2026-10-05).

Mondays 09:35. DM to Joshua ONLY (bonus_rules.json field_posting is false — never a team channel, never a
manager). Type B: reads files the Monday pull already produced; never drops a Bravo trigger.

Numbers come from the bonus engine's own code, never re-derived here:
  revenue  bonus_engine.parse_eom()  (in-store Interest + Fees + Misc + Sales Revenue (Profit)) on the newest
           output/<date>_<STORE>_end-of-month.xlsx whose Reporting Dates read "<M>/1/<YYYY> - ..." for this month
  gold     bonus_engine.read_gold()  (CLOSED buckets whose StatusDate is in this month)
  email %  bonus_engine.read_email_pct() on a chekkit-invites-range pull whose result JSON says it covers
           <month>-01..  (a 7-day review-invite pull is NOT month-to-date and is never used)
  reviews  Chekkit leaderboard, from the 1st to today (same API reviews_weekly.py reads)
  Facebook not readable without the Publer dashboard -> dash
Targets: Bonus Program/data/<YYYY-MM>/targets.json. All 5 stores' revenue or nothing: a missing store =
withhold + one FAILURE_LEDGER row (Joshua's all-or-nothing rule).
"""
import calendar, datetime as dt, glob, json, os, sys, tempfile, time, types
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BONUS = os.path.expanduser("~/Documents/Claude/Projects/Bonus Program")
sys.path.insert(0, os.path.join(BONUS, "bin"))
import bonus_engine as be  # noqa: E402

TASK = "bonus-pace-monday"
ET = ZoneInfo("America/New_York")
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
JOSHUA = "U03BB52MDSA"
ORDER = ["CUL", "HAR", "ROA", "LEX", "WAY"]          # the order the pace DM has always used (targets.json)
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}


def ledger(sentence):
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def month_eom(store, month):
    """Newest month-to-date EOM for this month -> (path, reporting_dates, through_date) or None."""
    y, m = int(month[:4]), int(month[5:7])
    best = None
    for p in glob.glob(os.path.join(OUT, "%s-*_%s_end-of-month.xlsx" % (month, store))):
        if os.path.getsize(p) < 500:
            continue
        try:
            rd = be.eom_reporting_dates(p) or ""
        except Exception:
            continue
        a, _, b = rd.partition(" - ")
        try:
            s = dt.datetime.strptime(a.strip(), "%m/%d/%Y").date(); e = dt.datetime.strptime(b.strip(), "%m/%d/%Y").date()
        except ValueError:
            continue
        if s != dt.date(y, m, 1) or (e.year, e.month) != (y, m):
            continue                      # trailing-12 / YTD / prior-month file under a month name — the trap
        k = (e, os.path.getmtime(p))
        if best is None or k > best[0]:
            best = (k, p, rd, e)
    return (best[1], best[2], best[3]) if best else None


def email_file(store, month):
    """A chekkit-invites-range pull that covers <month>-01 onward, per its result JSON."""
    best = None
    for rp in glob.glob(os.path.join(BRAVO, "results", "*.result.json")):
        try:
            res = json.load(open(rp, encoding="utf-8-sig"))
        except Exception:
            continue
        for c in res.get("cells", []):
            if (c.get("report") == "chekkit-invites-range" and c.get("store") == store and c.get("status") == "success"
                    and str(c.get("date", "")).startswith(month + "-01..")):
                p = os.path.join(OUT, str(c.get("output_path", "")).replace("\\", "/").split("/")[-1])
                if os.path.exists(p) and (best is None or os.path.getmtime(rp) > best[0]):
                    best = (os.path.getmtime(rp), p)
    return best[1] if best else None


def reviews_mtd(store, month, today):
    try:
        import reviews_weekly as rw
        tok = rw.token(store)
        if not tok:
            return None
        _, loc = rw.leaderboard(tok, month + "-01", today.isoformat())
        return int((loc.get("reviews") or {}).get("total") or 0)
    except Exception:
        return None


def main():
    a = sys.argv[1:]
    render = "--render" in a
    today = dt.date.fromisoformat(a[a.index("--today") + 1]) if "--today" in a else dt.datetime.now(ET).date()
    month = today.strftime("%Y-%m") if today.day > 1 else (today.replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    y, m = int(month[:4]), int(month[5:7])
    dim = calendar.monthrange(y, m)[1]
    mname = calendar.month_name[m]
    tp = os.path.join(BONUS, "data", month, "targets.json")
    if not os.path.exists(tp):
        if not render:
            ledger("Bonus pace DM withheld: no %s targets on file yet." % mname)
        print("WITHHELD: no targets", tp); return 2
    targets = json.load(open(tp))["targets"]
    rules = json.load(open(os.path.join(BONUS, "bonus_rules.json")))
    if (rules.get("field_posting") or {}).get("enabled"):
        pass                                    # still DM-only by SKILL; field posting is a separate task's job

    rev, missing = {}, []
    for s in ORDER:
        f = month_eom(s, month)
        if not f:
            missing.append(NAMES[s]); continue
        rev[s] = (be.parse_eom(f[0])["net_revenue"], f[2], f[0])
    if missing:
        msg = "Bonus pace DM withheld: no %s month-to-date revenue file for %s." % (mname, ", ".join(missing))
        if not render:
            ledger(msg)
        print("WITHHELD:", msg); return 2
    through = min(v[1] for v in rev.values())
    days = through.day
    el = days / dim

    # qualifiers via the engine's own readers
    tmp = tempfile.mkdtemp(prefix="bonuspace-")
    ctx = types.SimpleNamespace(data=tmp, month=month, gaps=[], holds=[])
    gold, email, revs = {}, {}, {}
    for s in ORDER:
        g = os.path.join(OUT, "%s_%s_scrap-refining-gold.csv" % (month[:4], s))
        # the yearly gold file only speaks for this month if it was pulled after the month began
        if os.path.exists(g) and dt.datetime.fromtimestamp(os.path.getmtime(g)).date() > dt.date(y, m, 1):
            os.symlink(g, os.path.join(tmp, "gold_%s.csv" % s))
            try:
                gold[s] = be.read_gold(ctx, s)[0]
            except Exception:
                gold[s] = None
        e = email_file(s, month)
        if e:
            os.symlink(e, os.path.join(tmp, "chekkit_invites_%s.csv" % s))
            pct, cap, tot = be.read_email_pct(ctx, s)
            email[s] = pct
        revs[s] = reviews_mtd(s, month, today)
        time.sleep(0.3)

    lag = (today - through).days
    head = "Bonus pace check — %s, through %d/%d (%d of %d days, %.1f%% of month elapsed). All 5 stores have usable data." % (
        mname, m, through.day, days, dim, el * 100)
    if lag > 3:
        head += " Revenue data is only current through %d/%d (%d days behind today)." % (m, through.day, lag)
    rows = ["Store  MTD Revenue   Target     % of Target   Pace"]
    ratio = {}
    for s in ORDER:
        r, t = rev[s][0], float(targets[s])
        pct = r / t if t else 0
        ratio[s] = pct / el if el else 0
        rows.append("%-6s %-13s %-10s %-13s %s" % (s, "${:,.2f}".format(r), "${:,.0f}".format(t), "%.1f%%" % (pct * 100),
                                                   "Ahead" if pct >= el else "Behind"))
    dash = "—"
    def line(vals, f):
        return " · ".join("%s %s" % (s, f(vals[s]) if vals.get(s) is not None else dash) for s in ORDER)
    rv = line(revs, lambda v: str(v))
    gd = line(gold, lambda v: "{:g}".format(v)) if any(v is not None for v in gold.values()) else None
    em = line(email, lambda v: "%.0f%%" % (v * 100)) if any(v is not None for v in email.values()) else None
    ql = ["Qualifiers so far this month:",
          "• New Google reviews (goal 15): " + rv,
          "• Gold dwt (goal 100): " + (gd or "— no %s numbers on file yet" % mname),
          "• Email capture (goal 50%): " + (em or "— no %s numbers on file yet" % mname),
          "• Facebook new followers (goal +15): —"]
    # closing sentence: most at risk = furthest behind straight-line pace; clean sweep = ahead on revenue and
    # on pace for the most qualifiers we can see (reviews/gold/email vs goal x elapsed), tie -> revenue pace.
    risk = min(ORDER, key=lambda s: ratio[s])
    def onpace(s):
        n = 0
        n += 1 if revs.get(s) is not None and revs[s] >= 15 * el else 0
        n += 1 if gold.get(s) is not None and gold[s] >= 100 * el else 0
        n += 1 if email.get(s) is not None and email[s] >= 0.5 else 0
        return n
    sweep = max(ORDER, key=lambda s: (ratio[s] >= 1, onpace(s), ratio[s]))
    allahead = all(ratio[s] >= 1 for s in ORDER)
    lead = "Every store is ahead of straight-line pace right now." if allahead else (
        "All five stores are behind straight-line pace." if all(ratio[s] < 1 for s in ORDER) else
        "%d of 5 stores are ahead of straight-line pace." % sum(ratio[s] >= 1 for s in ORDER))
    close = "%s %s is the one most at risk of missing (%.0f%% of target with %.0f%% of the month gone); %s is closest to a clean sweep so far." % (
        lead, NAMES[risk], rev[risk][0] / float(targets[risk]) * 100, el * 100, NAMES[sweep])
    text = "\n".join([head, "", "```" + "\n".join(rows) + "```", ""] + ql + ["", close])

    if render:
        print(text)
        for s in ORDER:
            print("src %s: %s (%s) gold=%s email=%s reviews=%s" % (s, os.path.basename(rev[s][2]), rev[s][1], gold.get(s), email.get(s), revs.get(s)))
        return 0
    os.environ.setdefault("VP_TASK", TASK)
    import vp_slack
    vp_slack.post(vp_slack.dm_channel(JOSHUA), text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
