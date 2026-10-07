#!/usr/bin/env python3
"""weekly_canvases.py <loan|layaway|employee|aged|store> [--render] [--post-date D] [--pipeline-date D]
                     [--end D] [--force]

Native port (2026-10-06) of the five Cowork Monday canvas refreshes, now that the ops bot has
canvases:read + canvases:write:
  loan      weekly-loan-review-canvas-refresh      F0BH6BJ0PK7  #loan-review           Mon 09:20
  layaway   weekly-layaway-review-canvas-refresh   F0BJ48BMZGQ  #layaway-review        Mon 09:22
  employee  weekly-employee-perf-canvas-refresh    F0BH9UK284S  #employee-performance  Mon 09:24
  aged      weekly-aged-inventory-canvas-refresh   F0BHDL6AULU  #aged-inventory-review Mon 09:26
  store     weekly-store-perf-canvas-refresh       F0BH6S9U5FX  #store-performance     Mon 09:28

The Cowork versions read Google Drive copies (Loan_Layaway_Review_*.docx, employee-sales-rankings-*.xlsx,
*_store_kpis_msg*.txt). This reads the same numbers from the Mac files the native Monday jobs produce,
through the existing calculators — nothing is re-derived:
  loan / layaway   comms_engine.load_loans / load_loan_balances / load_layaways (the #loan-review and
                   #layaway-review posts' own loaders, same pipeline date rule as monday_compile.py)
  employee         comms_engine.render_employee_performance (current-employees-only filter, roster);
                   company total + store totals = each store's "Total Store" Retail Sales Excl. Fees row
  aged             the per-store *_aged-inventory-summary.csv "Subtotals:" row, exactly the SKILL's math
  store            Bravo Data Extraction/store_kpis_compile.py <D> (the weekly-store-kpis compile) -> msg1/msg2
Layout = the locked SKILL format as it reads back from the live canvases on 2026-10-06 (title line,
headings, captions, table shapes, footer), written with canvases.edit (whole-document replace — what the
Cowork loan/aged/store tasks did; the layaway canvas is composed from its two owners' parts, see below).

Rules kept: all 5 stores or nothing (hold = one FAILURE_LEDGER row, nothing written, no DM); no system
names on the canvas; Joshua gets the SKILL's one-line confirmation DM after a confirmed edit; publication
receipt via vp_slack.receipt; fleet dry-run guard honoured; a second run on the same data is a no-op.

Layaway canvas has two owners: this task (status + Layaway Review table) and layaway-yield-weekly (Layaway
Yield % section). Each writes the whole document from fleet/canvas_state/F0BJ48BMZGQ.json, which keeps the
part the OTHER task last published, so neither ever overwrites the other's numbers.
"""
import datetime as dt
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE_DIR = os.path.join(OS_DIR, "fleet", "canvas_state")
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
NAME = dict(STORES)
SEP = lambda n: "|" + "|".join(["  ---  "] * n) + "|"
FOOT = "*This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below.*"
SHEET = {
    "loan": "[Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)",
    "layaway": "[Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)",
    "employee": "[Employee Sales Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg/edit)",
    "aged": "[Aged Inventory — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM/edit)",
    "store": "[Store Performance Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1vpcnbR6V4YGHIrqP8GpHDL5LcciekDPA_Dq6FOHbCts/edit)",
}
TASK = {"loan": ("weekly-loan-review-canvas-refresh", "F0BH6BJ0PK7"),
        "layaway": ("weekly-layaway-review-canvas-refresh", "F0BJ48BMZGQ"),
        "employee": ("weekly-employee-perf-canvas-refresh", "F0BH9UK284S"),
        "aged": ("weekly-aged-inventory-canvas-refresh", "F0BHDL6AULU"),
        "store": ("weekly-store-perf-canvas-refresh", "F0BH6S9U5FX")}
LAYAWAY_CANVAS = "F0BJ48BMZGQ"


class Hold(Exception):
    """Data incomplete — write nothing."""


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def usd(v):
    return "$" + format(v, ",.2f")


def sdate(iso):
    """Canvas date as text. The canvas API rejects the date-chip markdown the connector reads back
    (![](slack_date:...) -> "Unsupported source for image", tested 2026-10-06 on a scratch canvas)."""
    return dt.date.fromisoformat(iso).strftime("%b %-d, %Y")


def whole(v):
    return "$" + format(int(Decimal(str(round(v, 2))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)), ",")


def full_details(kind):
    return ["# :page_facing_up: Full Details", "", ":arrow_right: " + SHEET[kind], "", FOOT]


def and_list(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def ledger(task, sentence):
    try:
        with open(LEDGER, "a") as fh:
            fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                     % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), task, sentence))
    except OSError:
        pass


def pipeline_date(post_date, render):
    """Same rule as monday_compile.py: the Monday 05:30 pull when its certificate says ALL CLEAN, else the
    Sunday pull. Copies D..D_<STORE>_<report>.csv -> D_<STORE>_<report>.csv when absent (never moves)."""
    cert = os.path.join(BRAVO, "logs", "_monday_pull_status_%s.txt" % post_date)
    fresh = os.path.exists(cert) and "ALL CLEAN" in open(cert, errors="replace").read()
    d = arg("--pipeline-date") or (post_date if fresh else
                                   (dt.date.fromisoformat(post_date) - dt.timedelta(days=1)).isoformat())
    if not render:
        for f in glob.glob(os.path.join(OUT, "%s..%s_*.csv" % (d, d))):
            c = os.path.join(OUT, d + "_" + os.path.basename(f).split("_", 1)[1])
            if not os.path.exists(c):
                shutil.copy2(f, c)
    return d


def engine():
    import comms_engine
    return comms_engine


def withhold_text(exc):
    a = exc.args[0] if exc.args else exc
    return "; ".join(a) if isinstance(a, list) else str(a)


# --------------------------------------------------------------------------- loan
def render_loan(post_date, render):
    ce = engine()
    pdate = pipeline_date(post_date, render)
    try:
        loans = ce.load_loans(OUT, pdate)
        lay = ce.load_layaways(OUT, pdate)
    except ce.Withhold as e:
        raise Hold(withhold_text(e))
    eom_date, bal = ce.load_loan_balances(OUT, post_date)
    if not bal:
        raise Hold("no complete 5-store month-end loan balance within %d days" % ce.EOM_MAX_AGE_DAYS)
    reliable = len([c for c, _ in STORES if loans[c]["count"] == ce.GRID_ROW_CAP]) < 2
    rows, over = [], []
    for code, name in STORES:
        pct = loans[code]["dollars"] / bal[code] * 100.0
        if pct > ce.LOAN_POLICY_PCT:
            over.append((name, pct))
        rows.append("|%s|%s|%s|%.2f%%|%s|" % (name, loans[code]["count"] if reliable else "—", usd(loans[code]["dollars"]),
                                              pct, ":white_check_mark:" if pct <= ce.LOAN_POLICY_PCT else ":red_circle:"))
    tot_d = sum(v["dollars"] for v in loans.values())
    tot_n = sum(v["count"] for v in loans.values())
    cpct = tot_d / sum(bal.values()) * 100.0
    rows.append("|**Company**|%s|**%s**|**%.2f%%**|%s|" % ("**%d**" % tot_n if reliable else "—", usd(tot_d), cpct,
                                                         ":white_check_mark:" if cpct <= ce.LOAN_POLICY_PCT else ":red_circle:"))
    locs = [(NAME[c], lay[c]["locate"]) for c, _ in STORES if lay[c]["locate"]]
    take = "%d of 5 stores within 5%% policy." % (5 - len(over))
    for name, pct in over:
        take += " :red_circle: %s is over at %.2f%%." % (name, pct)
    if locs:
        take += " Action: %s %s Locate Layaways requiring resolution." % (
            and_list(["%s (%d)" % l for l in locs]), "has" if len(locs) == 1 else "have")
    else:
        take += " No action items."
    lt = ["|%s|%d|%d|%d|%d|%d|" % ((name,) + tuple(lay[c][k] for k in ce.LAY_COLS)) for c, name in STORES]
    tots = [sum(lay[c][k] for c, _ in STORES) for k in ce.LAY_COLS]
    lt.append("|**Company**|" + "|".join("**%d**" % t for t in tots) + "|")
    md = ["# %s Status — Week of %s" % (":red_circle:" if over else ":large_green_circle:", sdate(post_date)), "",
          take, "", "# :bar_chart: Past-Due Loans (75-Day Rule)", "",
          "Policy cap: 5%% of store loan balance. Balances as of %s." % eom_date, "",
          "|Store|Items 75+d|$ Past Due|% of Loan Bal|Status|", SEP(5)] + rows + [
          "", "# :card_index_dividers: Layaway Review", "",
          "|Store|Overdue|Past Pmt Due|Contacted/No Act|30d No Pmt|Locate|", SEP(6)] + lt + [""] + full_details("loan")
    wk = dt.date.fromisoformat(post_date).strftime("%b %-d")
    dm = "Refreshed #loan-review Canvas for week of %s — %s" % (
        wk, "all 5 stores within policy" if not over else "%s over the 5%% policy" % and_list([n for n, _ in over]))
    if locs:
        dm += "; %d Locate layaway%s flagged (%s)." % (sum(n for _, n in locs), "" if sum(n for _, n in locs) == 1 else "s",
                                                     ", ".join("%s %d" % l for l in locs))
    return "\n".join(md), dm, post_date


# --------------------------------------------------------------------------- layaway
def layaway_part(post_date, render):
    ce = engine()
    pdate = pipeline_date(post_date, render)
    try:
        lay = ce.load_layaways(OUT, pdate)
    except ce.Withhold as e:
        raise Hold(withhold_text(e))
    tot = dict((k, sum(lay[c][k] for c, _ in STORES)) for k in ce.LAY_COLS)
    cell = lambda v, t: "%d (%d%%)" % (v, int(round(v / t * 100.0)) if t else 0)   # = comms_engine's cell()
    rows = ["|%s|%s|%d|" % (name, "|".join(cell(lay[c][k], tot[k]) for k in ce.LAY_COLS[:4]), lay[c]["locate"])
            for c, name in STORES]
    rows.append("|**Company**|" + "|".join("**%d**" % tot[k] for k in ce.LAY_COLS) + "|")
    locs = [(NAME[c], lay[c]["locate"]) for c, _ in STORES if lay[c]["locate"]]
    n = sum(x for _, x in locs)
    if locs:
        take = ":warning: **%d Locate layaway%s** — %s need%s resolution." % (
            n, "" if n == 1 else "s", and_list(["%s (%d)" % l for l in locs]), "s" if len(locs) == 1 else "")
    else:
        take = ":white_check_mark: No Locate layaways this week."
    head = ["# :large_green_circle: Status — Week of %s" % sdate(post_date), "", take, "",
            "# :card_index_dividers: Layaway Review", "",
            "Counts by category. Percentages = each store's share of the company total.", "",
            "|Store|Overdue|Past Pmt Due|Contacted/No Act|30d No Pmt|Locate|", SEP(6)] + rows
    dm = "Layaway Canvas updated for week of %s. %s" % (
        post_date, "%d Locate item%s flagged (%s)." % (n, "" if n == 1 else "s", ", ".join("%s %d" % l for l in locs))
        if locs else "No Locate items this week.")
    return "\n".join(head), dm


def yield_part_from_disk():
    """Fallback only (no state file yet): the newest layaway-yield JSON's canvas section."""
    import layaway_yield_weekly as ly
    js = sorted(glob.glob(os.path.join(OUT, "20??-??-??_layaway_yield.json")))
    if not js:
        return None
    d = os.path.basename(js[-1])[:10]
    return ly.canvas_section(d, json.load(open(js[-1])))


def load_state(cid):
    try:
        return json.load(open(os.path.join(STATE_DIR, cid + ".json")))
    except (OSError, ValueError):
        return {}


def save_state(cid, st):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = os.path.join(STATE_DIR, cid + ".json.tmp")
    json.dump(st, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, os.path.join(STATE_DIR, cid + ".json"))


def compose_layaway(lay_md, yield_md):
    parts = [lay_md, ""]
    if yield_md:
        parts += [yield_md, ""]
    return "\n".join(parts + full_details("layaway"))


def render_layaway(post_date, render):
    lay_md, dm = layaway_part(post_date, render)
    st = load_state(LAYAWAY_CANVAS)
    y = st.get("yield") or yield_part_from_disk()
    return compose_layaway(lay_md, y), dm, post_date, {"layaway": lay_md, "yield": y}


# --------------------------------------------------------------------------- employee
def ordinal(i):
    return {1: ":first_place_medal:", 2: ":second_place_medal:", 3: ":third_place_medal:"}.get(i) or \
        "%d%s" % (i, "th" if 10 <= i % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th"))


def employee_store_detail(first):
    """Per store: Total Store Retail Sales Excl. Fees, reporting dates, and each employee's own figure
    (read from the same first-of-month CSVs comms_engine ranks)."""
    ce = engine()
    totals, periods, per = {}, [], {}
    for code, name in STORES:
        rows = ce.read_csv_rows(ce.store_file(OUT, first, code, "employee-activity"))
        hdr_i = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Employee")
        col = [h.strip() for h in rows[hdr_i]].index("Retail Sales Excluding Fees")
        for r in rows[:hdr_i]:
            if "Reporting Dates:" in [c.strip() for c in r]:
                m = re.search(r"(\d+/\d+/\d{4})\s*-\s*(\d+/\d+/\d{4})", ",".join(r))
                if m:
                    periods.append((m.group(1), m.group(2)))
        for r in rows[hdr_i + 1:]:
            if not r or not r[0].strip():
                continue
            label = r[0].strip()
            v = ce.money(r[col]) if col < len(r) else 0.0
            if label.lower().startswith("total store"):
                totals[code] = v
            elif " - " in label:
                per.setdefault(label.split(" - ", 1)[1].strip().upper(), {})[code] = v
    if len(totals) != 5:
        raise Hold("a store's employee-activity file has no Total Store row")
    return totals, periods, per


def render_employee(post_date, render):
    ce = engine()
    pdate = pipeline_date(post_date, render)
    notes = []
    try:
        _, info = ce.render_employee_performance(OUT, pdate, post_date, notes)
    except ce.Withhold as e:
        raise Hold(withhold_text(e))
    ranked = info["ranked"]
    first = pdate[:8] + "01"
    totals, periods, per = employee_store_detail(first)
    if len(periods) != 5 or len(set(periods)) != 1:
        raise Hold("stores' employee-activity files cover different periods: %s" % sorted(set(periods)))
    p0, p1 = periods[0]
    order = [c for c, _ in STORES]
    rows = []
    for i, (k, v) in enumerate(ranked, 1):
        stores = "+".join(sorted(v["stores"], key=order.index))
        rows.append("|%s|%s|%s|%s|" % (ordinal(i), ce.title_name(k), stores, usd(v["total"])))
    lk, lv = ranked[0]
    lstore = max(per.get(lk, {}).items(), key=lambda kv: kv[1])[0] if per.get(lk) else (lv["stores"] or ["CUL"])[0]
    top = max(order, key=lambda c: totals[c])
    company = sum(totals.values())
    md = ["# :bar_chart: MTD Employee Sales — as of %s" % sdate(post_date), "",
          "Retail sales excluding fees. Period: %s–%s. :trophy: %s leads at %s (%s); %s strongest store at %s."
          % (p0, p1, ce.title_name(lk), usd(lv["total"]), NAME[lstore], NAME[top], usd(totals[top])), "",
          "# :1234: Ranked Leaderboard", "",
          "||Employee|Store|Retail Sales (excl. fees)|", SEP(4)] + rows + [
          "", "*Company total (all store sales): **%s***" % usd(company), ""] + full_details("employee")
    dm = "Refreshed #employee-performance Canvas — MTD as of %s (%s–%s): %s leads at %s; company total %s." % (
        post_date, p0, p1, ce.title_name(lk), usd(lv["total"]), usd(company))
    return "\n".join(md), dm, post_date


# --------------------------------------------------------------------------- aged
def render_aged(post_date, render):
    import csv
    pdate = pipeline_date(post_date, render)
    ce = engine()
    data, problems = {}, []
    for code, name in STORES:
        p = os.path.join(OUT, "%s_%s_aged-inventory-summary.csv" % (pdate, code))
        if not os.path.exists(p) or os.path.getsize(p) < 500:
            problems.append("%s aged-inventory file missing or empty for %s" % (name, pdate))
            continue
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig", errors="replace")))
        sub = next((r for r in rows if r and r[0].strip().rstrip(":").lower() == "subtotals"), None)
        if not sub or len(sub) < 10:
            problems.append("%s aged-inventory file has no Subtotals row" % name)
            continue
        price = ce.money(sub[3])
        if price <= 0:
            problems.append("%s aged-inventory Subtotals price is zero" % name)
            continue
        data[code] = {"price": price, "u6": ce.money(sub[4]), "u12": ce.money(sub[5]),
                      "aged": sum(ce.money(sub[i]) for i in (6, 7, 8, 9))}
    if problems:
        raise Hold("; ".join(problems))
    pct = dict((c, data[c]["aged"] / data[c]["price"] * 100.0) for c, _ in STORES)
    co = dict((k, sum(data[c][k] for c, _ in STORES)) for k in ("price", "u6", "u12", "aged"))
    cpct = co["aged"] / co["price"] * 100.0
    hi = max(pct, key=pct.get)
    lo = min(pct, key=pct.get)
    rows = ["|%s|%s|%s|%s|%s|%.1f%%|" % (c, whole(data[c]["price"]), whole(data[c]["u6"]), whole(data[c]["u12"]),
                                         whole(data[c]["aged"]), pct[c]) for c, _ in STORES]
    rows.append("|**Company**|**%s**|**%s**|**%s**|**%s**|**%.1f%%**|" % (whole(co["price"]), whole(co["u6"]),
                                                                          whole(co["u12"]), whole(co["aged"]), cpct))
    md = ["# :large_green_circle: Status — as of %s" % sdate(pdate), "",
          "Company aged inventory (1yr+) is **%.1f%%** of on-hand retail value. :warning: %s (%.1f%% aged); %s (%.1f%% aged)"
          % (cpct, hi, pct[hi], lo, pct[lo]), "",
          "# :bar_chart: Aged Inventory by Store", "",
          "Retail value by age. \"Aged 1yr+\" = everything older than one year.", "",
          "|Store|Total Inv (Price)|<6mo|6mo–1yr|Aged 1yr+|% Aged|", SEP(6)] + rows + [""] + full_details("aged")
    dm = "Aged inventory canvas refreshed: %.1f%% company-wide (1yr+); %s highest at %.1f%%, %s leanest at %.1f%%." % (
        cpct, hi, pct[hi], lo, pct[lo])
    return "\n".join(md), dm, pdate


# --------------------------------------------------------------------------- store
def render_store(post_date, render):
    keep = os.environ.get("VP_TASK")
    import store_kpis_weekly as skw     # (its import sets VP_TASK=weekly-store-kpis — put ours back)
    os.environ["VP_TASK"] = keep
    end = dt.date.fromisoformat(arg("--end") or (dt.date.fromisoformat(post_date) - dt.timedelta(days=1)).isoformat())
    d = skw.complete_set(end)
    if d is None:
        raise Hold("no complete 5-store month-end set dated %s or up to 2 days before" % end)
    p = subprocess.run(["/usr/bin/python3", skw.COMPILE, d], capture_output=True, text=True, timeout=300)
    if not (p.stdout or "").startswith("OK"):
        raise Hold("store KPI compile said: %s" % ((p.stdout or "") + (p.stderr or "")).strip()[:200])
    m1 = open(os.path.join(OUT, "%s_store_kpis_msg1.txt" % d), encoding="utf-8").read()
    m2 = open(os.path.join(OUT, "%s_store_kpis_msg2.txt" % d), encoding="utf-8").read()
    overall = re.findall(r"^(🥇|🥈|🥉|4th|5th) \*(\w+)\* — Avg Rank ([\d.]+) \| (\d+) category wins out of 8$", m1, re.M)
    if len(overall) != 5:
        raise Hold("store KPI summary did not list 5 stores")
    summ = m1.split("Quick Summary:*", 1)[1].strip().split("\n")[0]
    cats, cur = {}, None
    for line in m2.splitlines():
        h = re.fullmatch(r"\*(.+)\*", line.strip())
        if h:
            cur = h.group(1)
            cats[cur] = []
            continue
        m = re.match(r"^(?:🥇|🥈|🥉|4th|5th) (\w+) — \$([\d,.\-]+)$", line.strip())
        if m and cur:
            cats[cur].append((m.group(1), float(m.group(2).replace(",", ""))))
    need = {"Loan Balance": "Loan Bal", "Inventory Balance": "Inv Bal", "Retail Sales Total Amt": "Retail Sales",
            "Pawn Service Charges": "PSC", "Layaway Balance": "Layaway Bal", "Net Revenue MTD": "Net Rev MTD"}
    val = {}
    for k in need:
        if len(cats.get(k, [])) != 5:
            raise Hold("store KPI breakdown is missing %s for a store" % k)
        val[k] = dict(cats[k])
    scrap_zero = "All stores at $0.00" in m2
    medal = {"🥇": ":1st_place_medal:", "🥈": ":2nd_place_medal:", "🥉": ":3rd_place_medal:", "4th": "4th", "5th": "5th"}
    rank_line = " ".join("%s **%s** — Avg Rank %s | %s category wins" % (medal[m], s, a, w) for m, s, a, w in overall)
    summary = re.sub(r"_(\w+)_", r"\1", summ)
    summary = re.sub(r"\$([\d,]+\.\d\d)", lambda m: whole(float(m.group(1).replace(",", ""))), summary)
    summary = summary.replace("pushed hardest on", "pushed hard on").replace(
        "finished 5th across the board — the focus for the week.", "is the focus for the week.")
    order = [s for _, s, _, _ in overall]
    rows = ["|%s|%s|" % (s, "|".join(whole(val[k][s]) for k in need)) for s in order]
    rows.append("|**Company**|%s|" % "|".join("**%s**" % whole(sum(val[k].values())) for k in need))
    lead = lambda k: cats[k][0][0]
    groups = [("Retail Sales", lead("Retail Sales Total Amt"))]
    psc, nr = lead("Pawn Service Charges"), lead("Net Revenue MTD")
    groups += [("PSC & Net Rev", psc)] if psc == nr else [("PSC", psc), ("Net Rev", nr)]
    tail = []
    for lbl, k in (("Loan", "Loan Balance"), ("Inv", "Inventory Balance"), ("Layaway", "Layaway Balance")):
        if tail and tail[-1][1] == lead(k):
            tail[-1] = (tail[-1][0] + "/" + lbl, lead(k))
        else:
            tail.append((lbl, lead(k)))
    leaders = " · ".join("%s → %s" % g for g in groups + tail) + "."
    if scrap_zero:
        leaders += " Note: Scrap $0."
    md = ["# :trophy: Overall Rankings — MTD as of %s" % sdate(d), "", rank_line, "", ":bulb: " + summary, "",
          "# :bar_chart: Key Metrics by Store", "",
          "|Store|Loan Bal|Inv Bal|Retail Sales|PSC|Layaway Bal|Net Rev MTD|", SEP(7)] + rows + [
          "", "*Category leaders: %s*" % leaders, ""] + full_details("store")
    dm = "Refreshed #store-performance Canvas — MTD as of %s: %s 1st (avg rank %s), %s 5th." % (
        d, overall[0][1], overall[0][2], overall[4][1])
    return "\n".join(md), dm, d


# --------------------------------------------------------------------------- publish
def canvas_write(task, cid, md):
    """Whole-document replace. Returns True on a confirmed edit (or a dry-run diversion -> 'dry')."""
    if vp_slack.dryrun_intercept("canvas", cid, md):
        return "dry"
    r = vp_slack.call("canvases.edit", {"canvas_id": cid, "changes": [
        {"operation": "replace", "document_content": {"type": "markdown", "markdown": md}}]})
    if not r.get("ok"):
        vp_slack.receipt("canvas", cid, False, len(md.encode()), "canvases.edit: %s" % r.get("error"))
        return "canvases.edit: %s" % r.get("error")
    # confirm: the status heading of what we just wrote must be findable
    first_h = [l for l in md.splitlines() if l.startswith("# ")][0]
    probe = re.sub(r":[a-z0-9_]+:|#", "", first_h).strip().split(" — ")[0]
    chk = vp_slack.call("canvases.sections.lookup", {"canvas_id": cid, "criteria": {"contains_text": probe}})
    if not chk.get("ok") or not chk.get("sections"):
        vp_slack.receipt("canvas", cid, False, len(md.encode()), "edit not confirmed by lookup")
        return "edit not confirmed (lookup %s)" % chk.get("error", "found nothing")
    vp_slack.receipt("canvas", cid, True, len(md.encode()), first_h[:120])
    return True


def main():
    kinds = {"loan": render_loan, "layaway": render_layaway, "employee": render_employee,
             "aged": render_aged, "store": render_store}
    if len(sys.argv) < 2 or sys.argv[1] not in kinds:
        sys.exit(__doc__)
    kind = sys.argv[1]
    task, cid = TASK[kind]
    os.environ["VP_TASK"] = task
    render = "--render" in sys.argv
    post_date = arg("--post-date") or dt.datetime.now(ET).date().isoformat()
    try:
        res = kinds[kind](post_date, render)
    except Hold as e:
        print("HOLD —", e)
        if not render:
            ledger(task, "The %s canvas was not refreshed for %s because a store's data was incomplete (%s)."
                   % (kind, post_date, str(e)[:200]))
        return 2
    md, dm, data_date = res[0], res[1], res[2]
    if render:
        print("=== RENDER ONLY — canvas %s (%s), data %s ===\n%s\n\n=== DM to Joshua ===\n%s" % (cid, task, data_date, md, dm))
        return 0
    os.makedirs(STATE_DIR, exist_ok=True)
    sig = hashlib.sha256(md.encode()).hexdigest()
    done = os.path.join(STATE_DIR, "%s.last" % task)
    if not "--force" in sys.argv and os.path.exists(done) and open(done).read().strip() == sig:
        print("canvas already shows this content — nothing to do")
        return 0
    ok = canvas_write(task, cid, md)
    if ok is not True and ok != "dry":
        ledger(task, "The %s canvas was built but Slack did not accept the update (%s)." % (kind, ok))
        print("FAILED —", ok)
        return 1
    if ok is True:
        open(done, "w").write(sig)
        if kind == "layaway":
            st = load_state(LAYAWAY_CANVAS)
            st.update({"layaway": res[3]["layaway"], "yield": res[3]["yield"], "updated": dt.datetime.now(ET).isoformat()})
            save_state(LAYAWAY_CANVAS, st)
    vp_slack.post(vp_slack.dm_channel(vp_slack.JOSHUA), dm)
    print("updated canvas", cid, "data", data_date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
