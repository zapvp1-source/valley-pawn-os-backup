#!/usr/bin/env python3
"""monthly_analytics_report.py [YYYY-MM] [--render] [--no-sheet] — native `monthly-analytics-report`
(1st of month 01:45 ET; Mac-first wave 3, 2026-10-19). The SKILL's steps, nothing re-derived:
  1 six windows (same-month / ytd / t12m, current + prior) for the month that just ended
  2 inventory Bravo Data Extraction/output/monthly-analytics/<YYYY-MM>/<window>_<STORE>.xlsx (30 files, staged by the
    native monthly-prestage runner); every file must be >= 2 KB AND pass store_rankings.structure() (2026-10-12 rule)
  3 parse with bin/parse_eom.py (the verified parser; locked Net Revenue / PSC / Total Sales / Scrap Cost definitions)
  4 YoY per view (var $, var %, flags)
  5 Google Sheet "Monthly Analytics - <Month YYYY>" via the Sheets API (spreadsheets scope on the Mac token;
    3 views x 4 sub-tables x 6 metrics x GT+5 stores). Lands in My Drive root (no Drive write scope to file it into
    the Monthly Reports folder) — the link in the post is what matters.
  6 COMPLETENESS GATE (Rule 18): 30/30 files, all 5 stores real (non-zero loan AND sales) for the same-month windows,
    or nothing posts. Post = the 2026-08-03 condensed layout, same-month view only, to #company-performance.
  7 working file monthly-analytics/<YYYY-MM> Monthly Analytics.md — all technical detail lives there.
Silent on failure (the 07:00 watchdog is the one notification path). --render prints the post + writes the working
file under fleet/test_output/, creates no sheet (unless --sheet-too), posts nothing.
"""
import calendar
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_eom          # noqa: E402  (vendored copy of the verified parser)
import store_rankings     # noqa: E402  (structure())
import vp_slack           # noqa: E402

AGENT = "monthly-analytics-report"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
STAGE = os.path.join(BRAVO, "output", "monthly-analytics")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0B26GD8D2R"   # #company-performance
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
WINDOWS = ["same-month-current", "same-month-prior", "ytd-current", "ytd-prior", "t12m-current", "t12m-prior"]
METRICS = [("inventory_balance", "Inventory"), ("loan_balance", "Loans Out"), ("total_sales", "Total Sales"),
           ("scrap_cost", "Scrap Cost"), ("psc", "Service Charges"), ("net_revenue", "Net Revenue")]
VIEWS = [("Same Month vs Year Ago", "same-month-current", "same-month-prior"),
         ("Year to Date", "ytd-current", "ytd-prior"), ("Trailing 12 Months", "t12m-current", "t12m-prior")]
GOOGLE_AUTH = os.path.join(PROJ, "Website", "analytics", "bin")


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def windows(y, m):
    last = dt.date(y, m, calendar.monthrange(y, m)[1])
    lastp = dt.date(y - 1, m, calendar.monthrange(y - 1, m)[1])
    t12s = dt.date(y - 1, m, 1) + dt.timedelta(days=calendar.monthrange(y - 1, m)[1])  # first of the month after (m, y-1)
    return {"same-month-current": (dt.date(y, m, 1), last), "same-month-prior": (dt.date(y - 1, m, 1), lastp),
            "ytd-current": (dt.date(y, 1, 1), last), "ytd-prior": (dt.date(y - 1, 1, 1), lastp),
            "t12m-current": (t12s, last), "t12m-prior": (dt.date(t12s.year - 1, t12s.month, 1), lastp)}


def usd(v):
    return "$" + format(v, ",.2f")


def pct(cur, prior):
    if not prior:
        return None
    return (cur - prior) / abs(prior) * 100.0


def fpct(p):
    return "n/a" if p is None else ("%+.1f%%" % p)


def flag(p):
    if p is None:
        return ""
    return ":fire:" if p > 30 else (":white_check_mark:" if p >= 0 else ":warning:")


def gather(ym):
    """-> (data {window: {store: metrics}}, problems[], notes[])"""
    d, problems, notes = {}, [], []
    folder = os.path.join(STAGE, ym)
    for w in WINDOWS:
        d[w] = {}
        for s in STORES:
            p = os.path.join(folder, "%s_%s.xlsx" % (w, s))
            if not os.path.exists(p) or os.path.getsize(p) < 2048:
                problems.append("%s_%s: missing or < 2 KB" % (w, s)); continue
            why = store_rankings.structure(p)
            if why:
                problems.append("%s_%s: %s" % (w, s, why)); continue
            try:
                mtr = parse_eom.parse_store_xlsx(p)
            except Exception as e:   # noqa: BLE001
                problems.append("%s_%s: parse error %s" % (w, s, e)); continue
            if mtr.get("loan_balance", 0) == 0 and mtr.get("total_sales", 0) == 0:
                problems.append("%s_%s: all-zero parse (failed cell signature)" % (w, s)); continue
            d[w][s] = mtr
    return d, problems, notes


def totals(block):
    return {k: sum(block[s].get(k, 0.0) for s in block) for k, _ in METRICS}


def build_post(ym, data, sheet_url):
    y, m = map(int, ym.split("-"))
    month = dt.date(y, m, 1).strftime("%B %Y")
    cur, pri = totals(data["same-month-current"]), totals(data["same-month-prior"])
    nr = pct(cur["net_revenue"], pri["net_revenue"])
    L = [":bar_chart: *Monthly Business Update — %s*" % month, "",
         "Company net revenue: %s (%s vs %s)" % (usd(cur["net_revenue"]), fpct(nr), dt.date(y - 1, m, 1).strftime("%B %Y")), "",
         "| Metric | This Year | Last Year | Change |", "|---|---|---|---|"]
    for k, label in METRICS:
        L.append("| %s | %s | %s | %s |" % (label, usd(cur[k]), usd(pri[k]), fpct(pct(cur[k], pri[k]))))
    L += ["", "Full breakdown → [Monthly Analytics - %s spreadsheet](%s)" % (month, sheet_url or "https://docs.google.com/spreadsheets/")]
    return "\n".join(L), month


def sheet_rows(ym, data):
    y, m = map(int, ym.split("-"))
    rows = [["Monthly Analytics - %s" % dt.date(y, m, 1).strftime("%B %Y"), "generated %s" % dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")], []]
    for view, wc, wp in VIEWS:
        cur, pri = data[wc], data[wp]
        tc, tp = totals(cur), totals(pri)
        rng = lambda w: ", ".join(sorted({cur_[s].get("reporting_dates", "") for s in cur_} if (cur_ := data[w]) else []))
        rows.append([view, "current: %s" % rng(wc), "prior: %s" % rng(wp)])
        for sub in ("Current Actuals", "Prior Actuals", "Var $", "Var %"):
            rows.append([sub, "GT"] + STORES)
            for k, label in METRICS:
                r = [label]
                for col in ["GT"] + STORES:
                    c = tc[k] if col == "GT" else cur.get(col, {}).get(k, 0.0)
                    p = tp[k] if col == "GT" else pri.get(col, {}).get(k, 0.0)
                    if sub == "Current Actuals": r.append(round(c, 2))
                    elif sub == "Prior Actuals": r.append(round(p, 2))
                    elif sub == "Var $": r.append(round(c - p, 2))
                    else:
                        v = pct(c, p); r.append(round(v, 1) if v is not None else "")
                rows.append(r)
            rows.append([])
        rows.append([])
    return rows


def create_sheet(title, rows):
    sys.path.insert(0, GOOGLE_AUTH)
    import google_auth
    def cell(v):
        return {"userEnteredValue": ({"numberValue": v} if isinstance(v, (int, float)) and not isinstance(v, bool) else {"stringValue": str(v)})}
    body = {"properties": {"title": title},
            "sheets": [{"properties": {"title": "Monthly Analytics"},
                        "data": [{"startRow": 0, "startColumn": 0, "rowData": [{"values": [cell(v) for v in r]} if r else {} for r in rows]}]}]}
    j = google_auth.api_post("https://sheets.googleapis.com/v4/spreadsheets", body, "https://www.googleapis.com/auth/spreadsheets")
    return j.get("spreadsheetUrl"), j.get("spreadsheetId")


def guard_on(task):
    """2026-10-21 (Nov 1 rehearsal): True while the fleet publish guard (bin/vp_dryrun.py) covers this task. Used to keep
    a rehearsal from making REAL non-Slack writes the guard cannot divert. Fails open (False) like vp_slack."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import vp_dryrun
        return vp_dryrun.active_for(task)
    except Exception:   # noqa: BLE001
        return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    ym = args[0] if args else (today.replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    y, m = map(int, ym.split("-"))
    month = dt.date(y, m, 1).strftime("%B %Y")
    win = windows(y, m)
    data, problems, notes = gather(ym)
    out_dir = os.path.join(OS_DIR, "fleet", "test_output", "monthly_analytics_render") if render else os.path.join(OS_DIR, "monthly-analytics")
    os.makedirs(out_dir, exist_ok=True)
    wf = os.path.join(out_dir, "%s Monthly Analytics.md" % ym)
    W = ["# %s Monthly Analytics (native)" % month, "", "Generated: %s | %s" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), "RENDER" if render else "live"), "",
         "## Date windows", "", "| Window | Intended | On file |", "|---|---|---|"]
    for w in WINDOWS:
        rd = sorted({data[w][s].get("reporting_dates", "") for s in data[w]})
        W.append("| %s | %s - %s | %s |" % (w, win[w][0].strftime("%-m/%-d/%Y"), win[w][1].strftime("%-m/%-d/%Y"), ", ".join(rd) or "—"))
    n_ok = sum(len(data[w]) for w in WINDOWS)
    W += ["", "## Inventory: %d/30 usable files" % n_ok, ""] + (["- " + p for p in problems] or ["- all 30 present, >= 2 KB, structurally valid"])
    for w in WINDOWS:
        W += ["", "### %s" % w, "", "| Store | Inventory | Loan Bal | Total Sales | Scrap Cost | PSC | Net Revenue | Reporting Dates |", "|---|---|---|---|---|---|---|---|"]
        for s in STORES:
            mt = data[w].get(s)
            W.append("| %s | %s |" % (s, " | ".join(("%.2f" % mt[k]) for k, _ in METRICS) + " | " + mt.get("reporting_dates", "")) if mt else "| %s | missing |" % s)
        if len(data[w]) == 5:
            t = totals(data[w]); W.append("| **GT** | %s | |" % " | ".join("**%.2f**" % t[k] for k, _ in METRICS))
    gate_ok = not problems and all(len(data[w]) == 5 for w in WINDOWS)
    for view, wc, wp in VIEWS:
        if len(data[wc]) == 5 and len(data[wp]) == 5:
            tc, tp = totals(data[wc]), totals(data[wp])
            W += ["", "### YoY — %s (Grand Total)" % view, "", "| Metric | Current | Prior | Var $ | Var % | |", "|---|---|---|---|---|---|"]
            for k, label in METRICS:
                v = pct(tc[k], tp[k]); W.append("| %s | %s | %s | %s | %s | %s |" % (label, usd(tc[k]), usd(tp[k]), usd(tc[k] - tp[k]), fpct(v), flag(v)))
    if not gate_ok:
        W += ["", "## Result: HELD — completeness gate failed (Rule 18). Nothing posted; the 07:00 watchdog owns the notification."]
        open(wf, "w").write("\n".join(W) + "\n")
        print("HOLD — %d/30 usable; %s" % (n_ok, "; ".join(problems)[:400]))
        return 2
    sheet_url = None
    if not render and guard_on(AGENT) and "--sheet-too" not in sys.argv:   # rehearsal: a Sheet is a real Drive write
        sheet_url = "https://docs.google.com/spreadsheets/(dry-run: sheet not created)"
        W += ["", "## Google Sheet", "", "DRY RUN — not created (publish guard on)"]
    elif (not render and "--no-sheet" not in sys.argv) or "--sheet-too" in sys.argv:
        try:
            sheet_url, sid = create_sheet(("TEST (render) " if render else "") + "Monthly Analytics - %s" % month, sheet_rows(ym, data))
            W += ["", "## Google Sheet", "", "Created: %s" % sheet_url]
        except Exception as e:   # noqa: BLE001
            W += ["", "## Google Sheet", "", "NOT created: %s" % e]
            notes.append("sheet failed: %s" % e)
    post, _ = build_post(ym, data, sheet_url)
    W += ["", "## Slack post (same-month view only)", "", "```", post, "```"]
    if render:
        open(wf, "w").write("\n".join(W) + "\n")
        print("=== RENDER ONLY ===\n%s\n\nworking file: %s\n%s" % (post, wf, "\n".join(notes)))
        return 0
    if not sheet_url:
        # the post's whole value for Joshua is the link; without the sheet, hold (watchdog surfaces it)
        W += ["", "## Result: HELD — the Google Sheet could not be created, so the post (whose link is the breakdown) was not sent."]
        open(wf, "w").write("\n".join(W) + "\n")
        ledger("The %s company performance report was built but its spreadsheet could not be created, so nothing posted." % month)
        return 1
    os.environ["VP_TASK"] = AGENT
    if vp_slack.has(CH, "Monthly Business Update — %s" % month, 24 * 20):
        W.append("\nAlready posted this month — nothing sent."); open(wf, "w").write("\n".join(W) + "\n"); print("already posted", month); return 0
    tmp = "/tmp/monthly_analytics_%s.txt" % ym
    open(tmp, "w").write(post)
    p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "post", CH, "--file", tmp], capture_output=True, text=True,
                       timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    W += ["", "## Result: %s" % ("DRY RUN — diverted, not posted" if p.returncode == 0 and "DRY RUN" in p.stdout else "POSTED ts %s" % p.stdout.strip() if p.returncode == 0 else "post failed: %s" % p.stderr.strip()[:200])]
    open(wf, "w").write("\n".join(W) + "\n")
    if p.returncode != 0:
        ledger("The %s company performance report was built but did not post." % month)
        return 1
    print("posted", month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
