"""
formats.py — canonical Slack format renderers, one function per report.

BUILD_SPEC.md §6 + Joshua's global CLAUDE.md standing rules: each renderer
must reproduce its established format EXACTLY. Golden tests compare output
against the most recent real Slack post in each channel — never "improve"
these without an explicit ask.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from . import xlsxmin

# Slack shortcode form, matching the actual live posting history in
# #store-performance exactly (verified 2026-07-26 against real posts on
# 7/20, 7/13, 7/06, 7/01) — NOT unicode emoji chars, which render the same
# in Slack's client but don't match the raw message text byte-for-byte.
MEDALS = [":first_place_medal:", ":second_place_medal:", ":third_place_medal:", "4th", "5th"]

STORE_FULL = {
    "CUL": "Culpeper",
    "HAR": "Harrisonburg",
    "LEX": "Lexington",
    "ROA": "Roanoke",
    "WAY": "Waynesboro",
}

METRICS = [
    "Loan Balance",
    "Inventory Balance",
    "Total Assets",
    "Retail Sales Total Amt",
    "Pawn Service Charges",
    "Scrap Sales",
    "Layaway Balance",
    "Net Revenue MTD",
]

_METRIC_LABEL_OVERRIDE = {"Total Assets": "Total Assets (Inventory + Loan)"}


def _num(v) -> float | None:
    """Parses Bravo's '$1,234.56' / '(999.99)' formatted strings, or passes
    through an already-numeric value from xlsxmin."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("$", "").replace(",", "")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        f = float(s)
        return -f if neg else f
    except ValueError:
        return None


def _dollar(x: float) -> str:
    return "$" + format(x, ",.2f")


def extract_store_eom_metrics(xlsx_path) -> dict:
    """Ports the verified-to-the-penny extraction from
    Bravo Data Extraction/store_kpis_compile.py (2026-07-02, checked against
    Bravo Company Performance for all 5 stores) onto the stdlib xlsxmin
    reader instead of openpyxl."""
    ws = xlsxmin.load_active_sheet(xlsx_path)
    mc = ws.max_column

    def row_values(r: int) -> list:
        return [x for x in (ws.get(r, c) for c in range(1, mc + 1)) if x is not None]

    def find_row(label: str, col: int = 1, after: int = 0, exact: bool = False) -> int:
        for r in range(after + 1, ws.max_row + 1):
            v = ws.get(r, col)
            if v is None:
                continue
            sv = str(v).strip()
            if (sv == label) if exact else sv.startswith(label):
                return r
        return 0

    loan_row = row_values(find_row("Ending Loan Base"))
    inv_row = row_values(find_row("Ending Inventory Base"))
    loan = _num(loan_row[2]) if len(loan_row) > 2 else 0
    inv = _num(inv_row[2]) if len(inv_row) > 2 else 0

    sub = row_values(find_row("In-Store Subtotal"))
    is_int = (_num(sub[4]) or 0) if len(sub) > 4 else 0
    is_fee = (_num(sub[5]) or 0) if len(sub) > 5 else 0
    is_misc = (_num(sub[6]) or 0) if len(sub) > 6 else 0

    sa_row = find_row("Sales Activity", exact=True)
    tx = row_values(find_row("Taxable Sales", after=sa_row, exact=True))
    ntx = row_values(find_row("Nontaxable Sales", after=sa_row, exact=True))
    tax_total = (_num(tx[-1]) or 0) if tx else 0
    ntax_total = (_num(ntx[-1]) or 0) if ntx else 0

    rev = row_values(find_row("Sales Revenue (Profit)"))
    profit = (_num(rev[-1]) or 0) if rev else 0

    ref = row_values(find_row("Refined", col=2))
    scrap = abs(_num(ref[-1])) if ref and _num(ref[-1]) else 0

    conv = row_values(find_row("MobilePawn Convenience Fees"))
    # Kept for parity with the source script; NOT part of Net Revenue MTD
    # (Bravo's own Net Revenue excludes mobile int/fee/misc + conv fees).
    _conv_value = (_num(conv[-1]) or 0) if conv else 0

    layaway_balance = 0
    for r in range(1, ws.max_row + 1):
        if any(str(ws.get(r, c) or "").strip().startswith("Ending Balance") for c in range(2, mc + 1)):
            for x in row_values(r):
                xv = _num(x)
                if xv is not None and abs(xv - round(xv)) > 0.001:
                    layaway_balance = xv
                    break
            break

    psc = is_int + is_fee + is_misc
    net_revenue = psc + profit

    return {
        "Loan Balance": loan or 0,
        "Inventory Balance": inv or 0,
        "Total Assets": (loan or 0) + (inv or 0),
        "Retail Sales Total Amt": tax_total + ntax_total,
        "Pawn Service Charges": psc,
        "Scrap Sales": scrap,
        "Layaway Balance": layaway_balance,
        "Net Revenue MTD": net_revenue,
    }


def compute_rankings(data: dict) -> tuple[dict, dict, list]:
    """data: {store: {metric: value}}. Returns (avg_rank, wins, catrank)."""
    stores = list(data.keys())
    avg = {s: 0.0 for s in stores}
    wins = {s: 0 for s in stores}
    catrank = {}
    for m in METRICS:
        order = sorted(stores, key=lambda s: -data[s][m])
        catrank[m] = order
        for i, s in enumerate(order):
            avg[s] += i + 1
        if data[order[0]][m] != data[order[1]][m]:
            wins[order[0]] += 1
    for s in stores:
        avg[s] = avg[s] / len(METRICS)
    return avg, wins, catrank


def render_store_rankings(data: dict, enddate: str) -> tuple[str, str]:
    """Renders the locked 'Full Category Rankings' two-message format.

    Verified byte-for-byte against the actual #store-performance Slack
    history (2026-07-20, -07-13, -07-06, -07-01 posts) on 2026-07-26 — NOT
    against either store_kpis_compile.py's or monday-store-rankings
    SKILL.md's own documented examples, which both use bold+unicode-emoji
    and don't match what's actually live (italic + Slack emoji shortcodes).
    Returns (msg1_parent, msg2_thread_reply). Deliberately excludes the
    "*Sent using* Claude" footer Claude's own posts carry — this is a
    native script, not Claude, and shouldn't claim to be.
    """
    stores = list(data.keys())
    avg, wins, catrank = compute_rankings(data)
    overall = sorted(stores, key=lambda s: avg[s])
    winner, second, last = overall[0], overall[1], overall[-1]

    second_cats = [m for m in METRICS if catrank[m][0] == second]
    narrative = (
        f"_{STORE_FULL[winner]}_ led the month with {wins[winner]} of {len(METRICS)} category wins, "
        f"anchored by the top loan book ({_dollar(data[winner]['Loan Balance'])}) and inventory. "
        f"_{STORE_FULL[second]}_ pushed hardest on "
        f"{' and '.join(second_cats) if second_cats else 'the sales floor'} for 2nd. "
        f"_{STORE_FULL[last]}_ finished {len(stores)}th across the board — the focus for the week."
    )

    m1 = []
    m1.append("_Valley Pawn — Weekly Store Performance Rankings_")
    m1.append(f":bar_chart: _Report Period: {enddate} (month-to-date)_")
    m1.append("")
    m1.append(":trophy: _Overall Store Rankings:_")
    for i, s in enumerate(overall):
        m1.append(f"{MEDALS[i]} _{STORE_FULL[s]}_ — Avg Rank {avg[s]:.2f} | {wins[s]} category wins out of {len(METRICS)}")
    m1.append("")
    m1.append(":bulb: _Quick Summary:_")
    m1.append(narrative)
    m1.append("")
    m1.append("Full ranked breakdown in thread :point_down:")
    msg1 = "\n".join(m1)

    m2 = [":bar_chart: _Full Category Rankings_", ""]
    for m in METRICS:
        m2.append(f"_{_METRIC_LABEL_OVERRIDE.get(m, m)}_")
        if m == "Scrap Sales" and all(abs(data[s][m]) < 0.005 for s in stores):
            m2.append("All stores at $0.00 (no scrap activity for the period)")
            m2.append("")
            continue
        for i, s in enumerate(catrank[m]):
            m2.append(f"{MEDALS[i]} {STORE_FULL[s]} — {_dollar(data[s][m])}")
        m2.append("")

    def total(m: str) -> float:
        return sum(data[s][m] for s in stores)

    m2.append("_Company Totals_")
    m2.append(
        f"Loan Balance: {_dollar(total('Loan Balance'))} | "
        f"Inventory Balance: {_dollar(total('Inventory Balance'))} | "
        f"Layaway Balance: {_dollar(total('Layaway Balance'))} | "
        f"Net Revenue MTD: {_dollar(total('Net Revenue MTD'))}"
    )
    msg2 = "\n".join(m2)

    return msg1, msg2


# ---------------------------------------------------------------------
# B. Aged Inventory Review -> #aged-inventory-review
#
# Built against Joshua's global CLAUDE.md standing spec, NOT any single
# historical Slack post: the real posting history (7/13, 7/06 x2, 6/29,
# 6/22, 6/15 - checked 2026-07-26) uses at least 5 different column
# orders/decimal conventions across those posts and NONE of them include
# the Total-$-aged column, the company TOTAL row, or the Sheets-link +
# Source footer the standing spec requires - i.e. this canonical format
# genuinely has never been posted as specified, matching BUILD_SPEC's own
# claim. The $ aged-jewelry/aged-merch/subtotals-cost figures below were
# verified against the 2026-07-13 Roanoke post's numbers to confirm the
# CSV column mapping is right, even though that post's layout differs.
# ---------------------------------------------------------------------

AGED_OVER_1YR_COLUMNS = ["1yr-18mo", "18mo-2yr", "2yr-3yr", ">3yr"]

_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def _format_review_date(date_str: str) -> str:
    y, m, d = date_str.split("-")
    return f"{_MONTHS[int(m) - 1]} {int(d)}, {y}"


def _parse_money(s: str) -> float:
    return _num(s) or 0.0


def extract_aged_inventory_metrics(csv_path) -> dict:
    """Parses a Bravo aged-inventory-summary.csv (plain CSV, not XLSX).
    Aged-over-1-year = sum of the 1yr-18mo/18mo-2yr/2yr-3yr/>3yr columns
    (BUILD_SPEC.md §1 'Known context quirks'). Subtotals cost is the
    denominator for J%/GM% per the standing CLAUDE.md rule."""
    import csv as csv_mod

    # latin-1 tolerates every byte value (the report footer's copyright
    # symbol isn't valid UTF-8) and the data we read is plain ASCII anyway.
    with open(csv_path, newline="", encoding="latin-1") as f:
        rows = list(csv_mod.reader(f))

    header_idx = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Category")
    header = [h.strip() for h in rows[header_idx]]
    col_idx = {h: i for i, h in enumerate(header)}
    aged_cols = [col_idx[c] for c in AGED_OVER_1YR_COLUMNS]
    cost_col = col_idx["Cost"]

    def find_row(label: str) -> list:
        return next(r for r in rows[header_idx + 1:] if r and r[0].strip() == label)

    jewelry = find_row("Jewelry:")
    mfg = find_row("Mfg. Goods:")
    subtotals = find_row("Subtotals:")

    jewelry_aged = sum(_parse_money(jewelry[c]) for c in aged_cols)
    genmerch_aged = sum(_parse_money(mfg[c]) for c in aged_cols)
    subtotal_cost = _parse_money(subtotals[cost_col])

    return {
        "jewelry_aged": jewelry_aged,
        "genmerch_aged": genmerch_aged,
        "subtotal_cost": subtotal_cost,
    }


def render_aged_inventory(data: dict, date_str: str) -> str:
    """data: {store: {jewelry_aged, genmerch_aged, subtotal_cost}}."""
    stores = list(data.keys())

    def pct_row(d: dict) -> dict:
        total_aged = d["jewelry_aged"] + d["genmerch_aged"]
        j_pct = (d["jewelry_aged"] / d["subtotal_cost"] * 100) if d["subtotal_cost"] else 0.0
        gm_pct = (d["genmerch_aged"] / d["subtotal_cost"] * 100) if d["subtotal_cost"] else 0.0
        return {
            "jewelry": d["jewelry_aged"], "j_pct": j_pct,
            "genmerch": d["genmerch_aged"], "gm_pct": gm_pct,
            "total": total_aged, "tot_pct": j_pct + gm_pct,
        }

    rows = {s: pct_row(data[s]) for s in stores}
    ranked = sorted(stores, key=lambda s: -rows[s]["tot_pct"])

    company = {
        "jewelry_aged": sum(data[s]["jewelry_aged"] for s in stores),
        "genmerch_aged": sum(data[s]["genmerch_aged"] for s in stores),
        "subtotal_cost": sum(data[s]["subtotal_cost"] for s in stores),
    }
    company_row = pct_row(company)

    def fmt_money(v: float) -> str:
        return f"${v:,.2f}"

    def fmt_pct(v: float) -> str:
        return f"{v:.2f}%"

    col_w = {"store": 13, "money": 14, "pct": 8}
    header_cells = [
        "Store".ljust(col_w["store"]),
        "Jewelry".rjust(col_w["money"]),
        "J%".rjust(col_w["pct"]),
        "Gen Merch".rjust(col_w["money"]),
        "GM%".rjust(col_w["pct"]),
        "Total".rjust(col_w["money"]),
        "Tot%".rjust(col_w["pct"]),
    ]
    sep_cells = [
        "-" * col_w["store"], "-" * col_w["money"], "-" * col_w["pct"],
        "-" * col_w["money"], "-" * col_w["pct"], "-" * col_w["money"], "-" * col_w["pct"],
    ]

    def data_cells(label: str, r: dict) -> list:
        return [
            label.ljust(col_w["store"]),
            fmt_money(r["jewelry"]).rjust(col_w["money"]),
            fmt_pct(r["j_pct"]).rjust(col_w["pct"]),
            fmt_money(r["genmerch"]).rjust(col_w["money"]),
            fmt_pct(r["gm_pct"]).rjust(col_w["pct"]),
            fmt_money(r["total"]).rjust(col_w["money"]),
            fmt_pct(r["tot_pct"]).rjust(col_w["pct"]),
        ]

    table_lines = [" ".join(header_cells), " ".join(sep_cells)]
    for s in ranked:
        table_lines.append(" ".join(data_cells(STORE_FULL[s], rows[s])))
    table_lines.append(" ".join(sep_cells))
    table_lines.append(" ".join(data_cells("TOTAL", company_row)))

    cleanest = ranked[-1]
    worst = ranked[0]

    lines = []
    lines.append(f":bar_chart: _Aged Inventory Review — {_format_review_date(date_str)}_")
    lines.append("_Inventory Aged Over 1 Year (Cost Basis)_")
    lines.append("_Ranked by Total Aged % of Inventory_")
    lines.append("")
    lines.append("```" + "\n".join(table_lines) + "```")
    lines.append(
        f":trophy: Cleanest book: {STORE_FULL[cleanest]} ({fmt_pct(rows[cleanest]['tot_pct'])}).  "
        f":hammer_and_wrench: Needs the most attention: {STORE_FULL[worst]} ({fmt_pct(rows[worst]['tot_pct'])})."
    )
    lines.append(bravo_module.GOOGLE_SHEETS_LINKS["aged-inventory"])
    lines.append("_Source: Bravo POS · Aged Inventory Summary report_")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# C. Employee Sales Rankings -> #employee-performance
#
# Verified 2026-07-26 against the real 2026-07-13 13:26 post (all 12
# ranked employees + exact per-store $ figures reconcile, e.g. Martin
# Dowden LEX $396.00 + ROA $256.70 + WAY $3,683.36 = $4,336.06). One
# addition beyond every historical post found: a Company Total line,
# which the standing CLAUDE.md rule requires but no real post includes.
# ---------------------------------------------------------------------

def extract_employee_activity(csv_path) -> dict:
    """Returns {'period_start', 'period_end', 'total_store', 'employees':
    {code: {'name', 'retail_sales'}}} for one store's employee-activity.csv.
    'Total Store' is that store's own Retail Sales Excl Fees total (used for
    the Company Total line). SYSTEM rows are excluded here; Preston Peters
    is NOT excluded here (his revenue must still count toward totals) - the
    ranked-list exclusion happens in render_employee_rankings."""
    import csv as csv_mod

    with open(csv_path, newline="", encoding="latin-1") as f:
        rows = list(csv_mod.reader(f))

    date_row = next(r for r in rows if any("Reporting Dates:" in (c or "") for c in r))
    range_str = next(c for c in reversed(date_row) if c and "Reporting Dates:" not in c)
    period_start, period_end = [p.strip() for p in range_str.split(" - ")]

    header_idx = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Employee")
    header = [h.strip() for h in rows[header_idx]]
    retail_col = header.index("Retail Sales Excluding Fees")

    total_store = 0.0
    employees = {}
    for r in rows[header_idx + 1:]:
        if not r or not r[0].strip():
            continue
        label = r[0].strip()
        if label.startswith("Report printed on"):
            break
        if label == "Total Store":
            total_store = _parse_money(r[retail_col])
            continue
        if label.upper().startswith("SYSTEM - "):
            continue
        code, _, name = label.partition(" - ")
        # .title() normalizes whatever casing Bravo's export used this time
        # (confirmed 2026-07-26: some pulls come back ALL CAPS, e.g.
        # "PRESTON PETERS" / "BRIDGETT GRAYSON") to match the established
        # Slack format's title case — and matches historical data's own
        # McClintic -> "Mcclintic" quirk exactly, since that's what naive
        # .title() produces too.
        employees[code.strip().upper()] = {"name": name.strip().title(), "retail_sales": _parse_money(r[retail_col])}

    return {"period_start": period_start, "period_end": period_end, "total_store": total_store, "employees": employees}


def aggregate_employee_rankings(store_data: dict) -> tuple[dict, float]:
    """store_data: {store_code: extract_employee_activity(...) result}.
    Returns ({employee_code: {'name', 'stores': [codes], 'retail_sales'}},
    company_total)."""
    by_code: dict = {}
    company_total = 0.0
    for store in bravo_module.STORES:
        d = store_data.get(store)
        if not d:
            continue
        company_total += d["total_store"]
        for code, info in d["employees"].items():
            entry = by_code.setdefault(code, {"name": info["name"], "stores": [], "retail_sales": 0.0})
            entry["stores"].append(store)
            entry["retail_sales"] += info["retail_sales"]
    return by_code, company_total


# Hard Rule (BUILD_SPEC.md, CLAUDE.md): "NEVER publish Preston Peters."
# Excluded by employee CODE (stable across stores/casing — confirmed
# "PMONEY" in every store's export) as the primary check, with a
# case-insensitive name match as a second layer — this rule is severe
# enough to warrant defense in depth rather than a single string match.
PRESTON_CODE = "PMONEY"
PRESTON_NAME = "preston peters"


def render_employee_rankings(store_data: dict) -> str:
    by_code, company_total = aggregate_employee_rankings(store_data)

    ranked = [
        (code, e) for code, e in by_code.items()
        if code != PRESTON_CODE and e["name"].lower() != PRESTON_NAME and e["retail_sales"] > 0
    ]
    ranked.sort(key=lambda kv: -kv[1]["retail_sales"])

    any_store = next(iter(store_data.values()))
    period = f"{any_store['period_start']}–{any_store['period_end']}"

    lines = []
    lines.append("_MTD Employee Sales Rankings — Retail Sales Excluding Fees (Bravo POS)_")
    lines.append(f":bar_chart: Period: {period}")
    lines.append("")
    for i, (code, e) in enumerate(ranked):
        rank_label = MEDALS[i] if i < 3 else f"{i + 1}th"
        stores_str = "+".join(e["stores"])
        lines.append(f"{rank_label} _{e['name']}_ ({stores_str}) — {_dollar(e['retail_sales'])}")
    lines.append("")
    lines.append(f"Company Total: {_dollar(company_total)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# D. Past-Due Loan Review -> #loan-review
#
# Verified 2026-07-26: the 5 loans-75-days-past-due.csv counts/$ figures
# match the real 2026-07-13 09:28 post exactly. That post's loan balances
# were dated 2026-06-21 (stale even at the time); this job always uses the
# freshest available EOM Loan Balance instead, so %s will differ from any
# specific historical post but are computed identically and more current.
# CLAUDE.md's "closest to threshold" fallback line is absent from every
# real post found (same drift pattern as Jobs B/C) - added per spec.
# ---------------------------------------------------------------------

def extract_loan_past_due(csv_path) -> dict:
    import csv as csv_mod
    with open(csv_path, newline="", encoding="latin-1") as f:
        rows = list(csv_mod.reader(f))
    header = [h.strip() for h in rows[0]]
    data_row = rows[1]
    d = dict(zip(header, data_row))
    return {"count": int(d["count"]), "dollar_sum": float(d["dollar_sum"])}


def render_past_due_loan_review(past_due: dict, loan_balances: dict, date_str: str) -> str:
    """past_due: {store: {count, dollar_sum}}. loan_balances: {store: $}."""
    stores = list(past_due.keys())
    pct = {s: (past_due[s]["dollar_sum"] / loan_balances[s] * 100) if loan_balances[s] else 0.0 for s in stores}

    total_count = sum(past_due[s]["count"] for s in stores)
    total_dollars = sum(past_due[s]["dollar_sum"] for s in stores)
    total_loan_balance = sum(loan_balances[s] for s in stores)
    total_pct = (total_dollars / total_loan_balance * 100) if total_loan_balance else 0.0

    lines = []
    lines.append(f":clipboard: _Weekly Past-Due Loan Review — {_format_review_date(date_str)}_")
    lines.append("")
    lines.append("_PAST DUE LOANS (75-day rule — cap 5% of loan balance)_")
    over_5pct = [s for s in stores if pct[s] > 5.0]
    for s in stores:
        mark = ":red_circle:" if pct[s] > 5.0 else ":white_check_mark:"
        lines.append(f"• _{s}_ — {past_due[s]['count']} items / {_dollar(past_due[s]['dollar_sum'])} / {pct[s]:.2f}% {mark}")
    lines.append(f"_Total past 75d:_ {total_count} items / {_dollar(total_dollars)} ({total_pct:.2f}% of {_dollar(total_loan_balance)} company loan balance)")

    if over_5pct:
        names = ", ".join(over_5pct)
        lines.append(f":red_circle: _{names}_ {'is' if len(over_5pct) == 1 else 'are'} over the 5% policy cap — needs attention.")
    else:
        closest = max(stores, key=lambda s: pct[s])
        lines.append(f"All 5 stores within the 5% policy. Closest to the threshold: _{closest}_ ({pct[closest]:.2f}%).")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# E. Layaway Review -> #layaway-review
#
# Verified 2026-07-26: all 5 stores' overdue/past_pmt_due/contacted_no_
# activity/no_pmt_30d/locate counts match the real 2026-07-13 13:26 post
# exactly. Built to mirror that post's layout (BUILD_SPEC.md §6 explicit
# instruction), using a clean fixed-width table rather than replicating
# that post's slightly inconsistent hand-spaced columns.
# ---------------------------------------------------------------------

LAYAWAY_METRICS = [
    ("overdue", "Overdue"),
    ("past_pmt_due", "Past Pmt Due"),
    ("contacted_no_activity", "Contacted/No Act"),
    ("no_pmt_30d", "30d-No-Pmt"),
    ("locate", "Locate"),
]


def extract_layaways(csv_path) -> dict:
    import csv as csv_mod
    with open(csv_path, newline="", encoding="latin-1") as f:
        rows = list(csv_mod.reader(f))
    header = [h.strip() for h in rows[0]]
    data_row = rows[1]
    d = dict(zip(header, data_row))
    return {k: int(d[k]) for k, _ in LAYAWAY_METRICS}


def render_layaway_review(data: dict, date_str: str) -> str:
    """data: {store: {overdue, past_pmt_due, contacted_no_activity, no_pmt_30d, locate}}."""
    stores = list(data.keys())
    company = {key: sum(data[s][key] for s in stores) for key, _ in LAYAWAY_METRICS}

    def cell(key: str, value: int, total: int) -> str:
        if key == "locate":
            return str(value)
        pct = round(value / total * 100) if total else 0
        return f"{value} ({pct}%)"

    store_col_w = max(len("Store"), max(len(STORE_FULL[s]) for s in stores), len("Company")) + 2
    company_locate_str = f":red_circle:{company['locate']}" if company["locate"] > 0 else "0"
    metric_col_w = {}
    for key, label in LAYAWAY_METRICS:
        widest_data = max(len(cell(key, data[s][key], company[key])) for s in stores)
        widest_company = len(company_locate_str) if key == "locate" else len(str(company[key]))
        metric_col_w[key] = max(len(label), widest_data, widest_company) + 2

    header_cells = ["Store".ljust(store_col_w)] + [label.ljust(metric_col_w[key]) for key, label in LAYAWAY_METRICS]
    sep_cells = ["-" * store_col_w] + ["-" * metric_col_w[key] for key, _ in LAYAWAY_METRICS]

    def data_row_cells(label: str, d: dict) -> list:
        cells = [label.ljust(store_col_w)]
        for key, _ in LAYAWAY_METRICS:
            cells.append(cell(key, d[key], company[key]).ljust(metric_col_w[key]))
        return cells

    table_lines = [" ".join(header_cells).rstrip(), " ".join(sep_cells)]
    for s in stores:
        table_lines.append(" ".join(data_row_cells(STORE_FULL[s], data[s])).rstrip())
    table_lines.append(" ".join(sep_cells))

    company_cells = ["Company".ljust(store_col_w)]
    for key, _ in LAYAWAY_METRICS:
        val = company_locate_str if key == "locate" else str(company[key])
        company_cells.append(val.ljust(metric_col_w[key]))
    table_lines.append(" ".join(company_cells).rstrip())

    lines = []
    lines.append(f":clipboard: _Weekly Layaway Review — {date_str}_")
    lines.append("_(% = store's share of the company total for that metric)_")
    lines.append("")
    lines.append("```" + "\n".join(table_lines) + "```")

    locate_stores = [s for s in stores if data[s]["locate"] > 0]
    if locate_stores:
        for s in locate_stores:
            n = data[s]["locate"]
            lines.append(f":red_circle: _{STORE_FULL[s]} has {n} Locate Layaway(s)_ — must be physically located and resolved")
    else:
        lines.append("_No Locate layaways this week._")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# H. Weekly FPD Ranking -> #first-payment-default (BUILD_SPEC_WAVE2.md §2)
#
# Verified 2026-07-27 against the real 2026-07-22 post: extraction counts
# and $ exposure match exactly for all 5 stores (e.g. Culpeper 36 loans /
# $2,772.00). Store ranking = count ASC (best=fewest defaults=rank 1),
# ties broken by $ ASC (Wave2 Rule #11). Category rankings run the
# opposite direction (count DESC = worst/most-prone first, since that's
# what "top default-prone" means), ties broken by $ DESC.
# ---------------------------------------------------------------------

def extract_fpd_cohort(csv_path) -> list:
    """Returns [{'ticket_number', 'category', 'full_description',
    'loan_amount'}, ...] for one store's fpd-cohort.csv. A header-only file
    (0 data rows) is a legitimate clean store, not a failure."""
    import csv as csv_mod
    with open(csv_path, newline="", encoding="latin-1") as f:
        rows = list(csv_mod.DictReader(f))
    out = []
    for r in rows:
        out.append({
            "ticket_number": r["Ticket Number"].strip(),
            "category": r["Category"].strip(),
            "full_description": r["Full Description"].strip(),
            "loan_amount": _num(r["Loan Amount"]) or 0.0,
        })
    return out


def render_fpd_ranking(cohorts: dict, date_str: str, archive: list, failed_stores: list = None) -> str:
    """cohorts: {store: [ticket dicts]} for stores that succeeded this run.
    archive: full FPD archive (list of dicts) INCLUDING this week's newly
    appended rows, for the chronic-risk (trailing 365d) category calc."""
    failed_stores = failed_stores or []
    stores = list(cohorts.keys())

    per_store = {s: {"count": len(cohorts[s]), "dollars": sum(t["loan_amount"] for t in cohorts[s])} for s in stores}
    ranked = sorted(stores, key=lambda s: (per_store[s]["count"], per_store[s]["dollars"]))

    company_count = sum(per_store[s]["count"] for s in stores)
    company_dollars = sum(per_store[s]["dollars"] for s in stores)

    this_week_cats: dict = {}
    for s in stores:
        for t in cohorts[s]:
            c = this_week_cats.setdefault(t["category"], {"count": 0, "dollars": 0.0})
            c["count"] += 1
            c["dollars"] += t["loan_amount"]
    top_this_week = sorted(this_week_cats.items(), key=lambda kv: (-kv[1]["count"], -kv[1]["dollars"]))[:3]

    cutoff = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    chronic_cats: dict = {}
    for row in archive:
        if row["first_seen_date"] >= cutoff:
            c = chronic_cats.setdefault(row["category"], {"count": 0, "dollars": 0.0})
            c["count"] += 1
            c["dollars"] += _num(row["loan_amount"]) or 0.0
    top_chronic = sorted(chronic_cats.items(), key=lambda kv: (-kv[1]["count"], -kv[1]["dollars"]))[:3]

    lines = []
    lines.append(f":dart: _Weekly First-Payment-Default Ranking — {date_str}_")
    lines.append('_Source: Bravo saved report "Claude First Payment Default" · cohort = loans originated 60–90 days ago with no customer payment activity_')
    lines.append("")
    lines.append("_Store ranking — best to worst_")
    for i, s in enumerate(ranked, start=1):
        lines.append(f"{i}. _{STORE_FULL[s]}_ — {per_store[s]['count']} FPD loans - {_dollar(per_store[s]['dollars'])} exposure")
    lines.append(f"_Company:_ {company_count} FPD loans - {_dollar(company_dollars)} total exposure")
    lines.append("")
    lines.append("_Top default-prone categories (this week)_")
    for i, (cat, d) in enumerate(top_this_week, start=1):
        lines.append(f"{i}. {cat} — {d['count']} loans - {_dollar(d['dollars'])}")
    lines.append("_Chronic-risk categories (last 12 months)_")
    for i, (cat, d) in enumerate(top_chronic, start=1):
        lines.append(f"{i}. {cat} — {d['count']} total FPD loans - {_dollar(d['dollars'])}")

    if failed_stores:
        names = ", ".join(STORE_FULL[s] for s in failed_stores)
        plural = "s" if len(failed_stores) > 1 else ""
        lines.append(f"_Note: {names} not included — pipeline cell{plural} failed._")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Job I — Monthly Analytics (BUILD_SPEC_WAVE2.md §3)
# ---------------------------------------------------------------------

MONTHLY_KPI_COLS = ("GT", "CUL", "HAR", "LEX", "ROA", "WAY")
MONTHLY_METRICS = ["Inventory Balance", "Loan Balance", "Retail Sales", "Scrap Sales", "PSC", "Net Revenue"]


def extract_company_kpis(xlsx_path) -> dict:
    """Parses the Bravo 'Company KPI Report' (company-kpis cell) — a single
    ALL-store workbook with a Grand Total column + one column per store,
    unlike the per-store end-of-month cell. This is Job I's data source per
    BUILD_SPEC_WAVE2.md I-0 (the Jul 3 canonical post's source line reads
    "Bravo Company Performance (KPI) report", superseding the EOM-based
    formula in the legacy monthly-analytics-report/SKILL.md).

    Net Revenue = Retail Sales Gross Profit Amt + Scrap Sales Gross Profit Amt
    + Pawn Service Charges — verified against Bravo's own dashboard "Net
    Revenue MTD" card in the real 2026-06-30 company-kpis.xlsx: GT Retail GP
    $100,243.04 + Scrap GP $52,690.45 + PSC $77,160.79 = $230,094.28, matching
    the card's $230.09K to the penny (card is rounded to the nearest $10)."""
    ws = xlsxmin.load_active_sheet(xlsx_path)
    mc = ws.max_column

    def row_values(r: int) -> dict:
        return {c: ws.get(r, c) for c in range(1, mc + 1) if ws.get(r, c) is not None}

    def find_row(label: str, after: int = 0, exact: bool = True) -> int:
        for r in range(after + 1, ws.max_row + 1):
            for c in range(1, mc + 1):
                v = ws.get(r, c)
                if v is None:
                    continue
                sv = str(v).strip()
                if (sv == label) if exact else sv.startswith(label):
                    return r
        return 0

    gt_row = find_row("* Grand Total")
    if not gt_row:
        raise ValueError(f"Could not find '* Grand Total' header row in {xlsx_path}")
    header = row_values(gt_row)

    def find_col(prefix: str) -> int:
        for c, v in header.items():
            if str(v).strip().startswith(prefix):
                return c
        raise ValueError(f"Could not find a column starting with {prefix!r} in {xlsx_path}")

    cols = {
        "GT": find_col("* Grand Total"),
        "CUL": find_col("Cul -"),
        "HAR": find_col("Har -"),
        "LEX": find_col("Lex -"),
        "ROA": find_col("Roa -"),
        "WAY": find_col("Way -"),
    }

    def metric_row(label: str) -> dict:
        r = find_row(label, after=gt_row, exact=True)
        return row_values(r) if r else {}

    inv_row = metric_row("Inventory Balance")
    loan_row = metric_row("Loan Balance")
    retail_row = metric_row("Retail Sales Total Amt")
    retail_gp_row = metric_row("Retail Sales Gross Profit Amt")
    scrap_row = metric_row("Scrap Sales")
    scrap_gp_row = metric_row("Scrap Sales Gross Profit Amt")
    psc_row = metric_row("Pawn Service Charges")

    out = {}
    for key, col in cols.items():
        retail_gp = _num(retail_gp_row.get(col)) or 0
        scrap_gp = _num(scrap_gp_row.get(col)) or 0
        psc = _num(psc_row.get(col)) or 0
        out[key] = {
            "Inventory Balance": _num(inv_row.get(col)) or 0,
            "Loan Balance": _num(loan_row.get(col)) or 0,
            "Retail Sales": _num(retail_row.get(col)) or 0,
            "Scrap Sales": _num(scrap_row.get(col)) or 0,
            "PSC": psc,
            "Net Revenue": retail_gp + scrap_gp + psc,
        }
    return out


def compute_yoy(current: dict, prior: dict) -> dict:
    """current/prior: {key: {metric: value}} (key = GT or store code).
    Returns {key: {metric: {'current','prior','var_dollar','var_pct'}}}."""
    out = {}
    for key in current:
        out[key] = {}
        for metric in current[key]:
            cur = current[key][metric]
            pri = prior.get(key, {}).get(metric, 0)
            var_d = cur - pri
            var_p = (var_d / pri * 100) if pri else 0.0
            out[key][metric] = {"current": cur, "prior": pri, "var_dollar": var_d, "var_pct": var_p}
    return out


def _yoy_flag(var_pct: float) -> str:
    if var_pct > 30:
        return ":fire:"
    if var_pct < 0:
        return ":warning:"
    return ":white_check_mark:"


def _render_yoy_table(key_yoy: dict) -> str:
    """key_yoy: {metric: {'current','prior','var_dollar','var_pct'}} for ONE
    key (a store code or GT). Renders a monospace ASCII table, NOT a markdown
    pipe table — Slack's raw chat.postMessage mrkdwn does not convert `|`
    syntax into real tables (only the Slack MCP's own send-message tool and
    Canvases do that conversion). Matches the proven ASCII-table style
    already used by render_aged_inventory/render_layaway_review."""
    headers = ["Metric", "Current", "Prior", "$ Chg", "YoY"]
    rows = []
    for m in MONTHLY_METRICS:
        d = key_yoy[m]
        rows.append([
            m, _dollar(d["current"]), _dollar(d["prior"]), _dollar(d["var_dollar"]),
            f"{d['var_pct']:.1f}% {_yoy_flag(d['var_pct'])}",
        ])
    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) for i in range(len(headers))]

    def fmt_row(cells):
        return "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

    lines = [fmt_row(headers), "  ".join("-" * w for w in widths)]
    lines += [fmt_row(r) for r in rows]
    return "```" + "\n".join(lines) + "```"


def render_monthly_analytics_company(windows: dict, month_label: str, prior_month_label: str,
                                      view_ranges: dict, t12m_prior_note: str = "") -> str:
    """windows: {'same_month': {'current': company_kpis, 'prior': company_kpis},
    'ytd': {...}, 't12m': {...}} — each company_kpis is extract_company_kpis()'s
    output (keyed GT/CUL/HAR/.../WAY). Grand-Total-only post, per
    BUILD_SPEC_WAVE2.md's canonical Jul 3 framing (table bodies recovered
    from the company-kpis data — no byte-exact historical Slack post was
    recoverable, per I-0; shadow-test against the real channel before live)."""
    lines = [
        f":bar_chart: _Monthly Analytics - {month_label} | Company-Wide — Retail vs Scrap channel split_",
        "_Source: Bravo Company Performance (KPI) report, all 6 windows | matches Bravo to the penny_",
        "",
    ]
    view_titles = {
        "same_month": f"_VIEW 1 - Same Month: {month_label} vs {prior_month_label}_",
        "ytd": f"_VIEW 2 - YTD: {view_ranges['ytd']}_",
        "t12m": f"_VIEW 3 - T12M: {view_ranges['t12m']}_",
    }
    for view_key in ("same_month", "ytd", "t12m"):
        yoy = compute_yoy(windows[view_key]["current"], windows[view_key]["prior"])
        lines.append(view_titles[view_key])
        lines.append(_render_yoy_table(yoy["GT"]))
    if t12m_prior_note:
        lines.append(f"_{t12m_prior_note}_")
    return "\n".join(lines)


def render_monthly_analytics_store(windows: dict, month_label: str, prior_month_label: str,
                                    view_ranges: dict) -> str:
    """5-store companion post, NO Grand Total, same 3 views."""
    lines = [
        f":bar_chart: _Monthly Analytics - {month_label} | Store Breakdown — Retail vs Scrap channel split_",
        "_Source: Bravo Company Performance (KPI) report, all 6 windows | matches Bravo to the penny_",
        "",
    ]
    view_titles = {
        "same_month": f"_VIEW 1 - Same Month: {month_label} vs {prior_month_label}_",
        "ytd": f"_VIEW 2 - YTD: {view_ranges['ytd']}_",
        "t12m": f"_VIEW 3 - T12M: {view_ranges['t12m']}_",
    }
    for view_key in ("same_month", "ytd", "t12m"):
        yoy = compute_yoy(windows[view_key]["current"], windows[view_key]["prior"])
        lines.append(view_titles[view_key])
        for store in ("CUL", "HAR", "LEX", "ROA", "WAY"):
            lines.append(f"_{STORE_FULL[store]}_")
            lines.append(_render_yoy_table(yoy[store]))
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Job J — Monthly Gold Trend (BUILD_SPEC_WAVE2.md §4)
# ---------------------------------------------------------------------

def extract_scrap_refining_gold(csv_path) -> dict:
    """Returns {year_month: dwt} for one store-year's scrap-refining-gold.csv,
    summing CombinedMetalWeightDwt across all CLOSED buckets per month.
    Bravo's Scrap Refining Process screen splits each month's gold refining
    into separate 'with stones' / 'without stones' buckets, but not always —
    some months only have one combined bucket. That's real month-to-month
    variation in how the store closed the batch, not a data gap."""
    import csv as csv_mod
    out: dict = {}
    with open(csv_path, newline="", encoding="latin-1") as f:
        for r in csv_mod.DictReader(f):
            # Some rows carry a Status column (OPEN/CLOSED) -- an OPEN bucket
            # is still accumulating and must not be counted as a final month
            # total (confirmed live 2026-07-27: a real OPEN CUL July-2026
            # bucket appeared in the raw file mid-session). Older per-store
            # CSVs have no Status column at all -- those were only ever
            # pulled as closed-only historical snapshots, so absence of the
            # column means "include it."
            status = (r.get("Status") or "").strip().upper()
            if status and status != "CLOSED":
                continue
            month = r["Month"].strip()
            dwt = _num(r.get("CombinedMetalWeightDwt")) or 0.0
            out[month] = out.get(month, 0.0) + dwt
    return out


def render_gold_trend(current_month: dict, prior_month: dict, ytd_current: float, ytd_prior: float,
                       best_month_t12m: tuple, month_label: str, prior_month_label: str) -> str:
    """current_month/prior_month: {store: dwt} for GT... actually {store: dwt}
    for the 5 stores (no GT key — company total computed here). best_month_t12m:
    (month_label, dwt) for the best T12M month."""
    lines = [f":coin: _Gold Trend — {month_label} (dwt purchased)_",
             "_Source: Bravo Scrap Refining Process · YoY by store_", ""]
    lines.append(f"_{month_label} vs {prior_month_label}_")
    company_cur = 0.0
    company_pri = 0.0
    for store in ("CUL", "HAR", "LEX", "ROA", "WAY"):
        cur = current_month.get(store, 0.0)
        pri = prior_month.get(store, 0.0)
        company_cur += cur
        company_pri += pri
        pct = f"{((cur - pri) / pri * 100):+.0f}%" if pri else "n/a"
        lines.append(f"• _{STORE_FULL[store]}_ — {cur:.2f} dwt (vs {pri:.2f} — {pct})")
    company_pct = f"{((company_cur - company_pri) / company_pri * 100):+.0f}%" if company_pri else "n/a"
    lines.append(f"_Company:_ {company_cur:.2f} dwt (vs {company_pri:.2f} — {company_pct})")
    lines.append("")
    ytd_pct = f"{((ytd_current - ytd_prior) / ytd_prior * 100):+.0f}%" if ytd_prior else "n/a"
    lines.append(f"_YTD:_ {ytd_current:.2f} dwt vs {ytd_prior:.2f} prior — {ytd_pct}")
    lines.append(f"_Best month T12M:_ {best_month_t12m[0]} ({best_month_t12m[1]:.2f} dwt)")
    return "\n".join(lines)


from . import bravo as bravo_module  # noqa: E402  (avoids circular import at module load)
