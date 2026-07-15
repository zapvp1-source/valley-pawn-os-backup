#!/usr/bin/env python3
"""
daily-loan-inventory-text :: compute engine (deterministic, no LLM).

Parses a Bravo "Company KPI / Company Performance" xlsx (all 5 stores in one
file), extracts the standing Loan Balance and Inventory Balance (both reported
"as of yesterday's close"), compares them to the last-day-of-previous-month
baseline, and prints an SMS-ready message to stdout.

Baseline is self-owned and auto-seeding:
  baseline/baseline_<YYYY-MM>.json  holds the month-end balances that the whole
  of that calendar month is measured against. On the 1st of a new month the
  morning pull IS the prior month-end reading, so if the file is missing we seed
  it from today's reading (growth = 0 that day) -- correct on normal cadence.
  A mid-month first deployment is seeded manually from verified data.

Usage:
  compute.py --xlsx <path> --asof YYYY-MM-DD [--json-out <path>]
Exit codes: 0 ok, 2 parse failure.
"""
import sys, os, json, argparse, datetime, glob

STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(TASK_DIR, "baseline")


def money(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace("$", "").replace(",", "").replace("%", "")
    if s in ("", "-", "--"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
        return -v if neg else v
    except ValueError:
        return None


def extract_metric(rows, label):
    """Return (grand_total, [per-store 5]) for a metric-matrix row whose label
    cell matches `label` exactly and is followed by >=6 numeric cells."""
    want = label.strip().lower()
    for vals in rows:
        idx = None
        for i, c in enumerate(vals):
            if c is not None and str(c).strip().lower() == want:
                idx = i
                break
        if idx is None:
            continue
        nums = [money(c) for c in vals[idx + 1:]]
        nums = [n for n in nums if n is not None]
        if len(nums) >= 6:
            return nums[0], nums[1:6]
    return None, None


def parse_company_kpis(xlsx_path):
    import openpyxl
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    loan_gt, loan_st = extract_metric(rows, "Loan Balance")
    inv_gt, inv_st = extract_metric(rows, "Inventory Balance")
    if loan_gt is None or inv_gt is None:
        raise ValueError("Could not locate Loan Balance / Inventory Balance rows")
    return {
        "loan": {"company": round(loan_gt, 2),
                 "stores": {s: round(v, 2) for s, v in zip(STORES, loan_st)}},
        "inventory": {"company": round(inv_gt, 2),
                      "stores": {s: round(v, 2) for s, v in zip(STORES, inv_st)}},
    }


def load_or_seed_baseline(asof, today_reading):
    os.makedirs(BASE_DIR, exist_ok=True)
    key = asof.strftime("%Y-%m")
    path = os.path.join(BASE_DIR, "baseline_%s.json" % key)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f), False
    # month-end of previous month = last day before the 1st of this month
    prev_end = asof.replace(day=1) - datetime.timedelta(days=1)
    seed = {
        "as_of_month_end": prev_end.strftime("%Y-%m-%d"),
        "seeded_from": "first-run-of-month-reading",
        "loan_company": today_reading["loan"]["company"],
        "inventory_company": today_reading["inventory"]["company"],
        "loan_stores": today_reading["loan"]["stores"],
        "inventory_stores": today_reading["inventory"]["stores"],
    }
    with open(path, "w") as f:
        json.dump(seed, f, indent=2)
    return seed, True


def fmt_money(v):
    return "${:,.0f}".format(round(v))


def growth_line(label, today_v, base_v):
    delta = today_v - base_v
    pct = (delta / base_v * 100.0) if base_v else 0.0
    arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "▬")
    sign = "+" if delta >= 0 else "-"
    return "{lab}: {now}  {arr}{sign}{amt} ({sign}{pct:.1f}%)".format(
        lab=label, now=fmt_money(today_v), arr=arrow, sign=sign,
        amt=fmt_money(abs(delta)).lstrip("$"), pct=abs(pct))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--asof", required=True, help="YYYY-MM-DD of the run day")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    asof = datetime.datetime.strptime(a.asof, "%Y-%m-%d").date()
    yest = asof - datetime.timedelta(days=1)

    try:
        reading = parse_company_kpis(a.xlsx)
    except Exception as e:
        sys.stderr.write("PARSE_FAIL: %s\n" % e)
        return 2

    base, seeded = load_or_seed_baseline(asof, reading)
    me_label = datetime.datetime.strptime(
        base["as_of_month_end"], "%Y-%m-%d").strftime("%-m/%-d")

    lines = []
    lines.append("Valley Pawn — Daily numbers")
    lines.append("(balances as of %s close)" % yest.strftime("%-m/%-d"))
    lines.append("")
    lines.append(growth_line("Loan Balance", reading["loan"]["company"],
                             base["loan_company"]))
    lines.append(growth_line("Inventory", reading["inventory"]["company"],
                             base["inventory_company"]))
    lines.append("")
    lines.append("Growth vs %s month-end." % me_label)
    if seeded:
        lines.append("(baseline seeded today — growth shows from tomorrow)")
    msg = "\n".join(lines)
    sys.stdout.write(msg + "\n")

    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump({"asof": a.asof, "reading": reading, "baseline": base,
                       "message": msg}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
