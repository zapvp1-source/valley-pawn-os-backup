#!/usr/bin/env python3
"""
daily-loan-inventory-text :: compute engine (deterministic, no LLM).

Source: Bravo "End of Month" report, one xlsx per store
(<END>_<STORE>_end-of-month.xlsx). Each carries "Ending Loan Base" and
"Ending Inventory Base" (dollar) for that store — the SAME metric basis as the
Company KPI Loan Balance / Inventory Balance, so the 6/30 baseline is unchanged.
Company total = sum of the 5 stores.

Compares today's company Loan Balance and Inventory Balance to the last-day-of-
previous-month baseline and prints an SMS-ready message to stdout.

Baseline (self-owned, auto-seeding): baseline/baseline_<YYYY-MM>.json. If missing,
seed from the run's own reading (correct on the 1st, when the pull already reflects
the prior month-end). July 2026 pre-seeded from the penny-verified 6/30 reading.

Usage: compute.py --outdir <bravo output dir> --end YYYY-MM-DD --asof YYYY-MM-DD [--json-out P]
Exit: 0 ok, 2 missing/parse failure.
"""
import sys, os, json, argparse, datetime

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


def ending_value(rows, label):
    """In an EOM store xlsx, find the row whose first cell starts with `label`
    (e.g. 'Ending Loan Base 7/14/2026'). The cells after it are Qty, $, Qty, $ —
    return the first DOLLAR figure (the 2nd numeric)."""
    want = label.strip().lower()
    for vals in rows:
        for i, c in enumerate(vals):
            if c is not None and str(c).strip().lower().startswith(want):
                nums = [money(x) for x in vals[i + 1:]]
                nums = [n for n in nums if n is not None]
                if len(nums) >= 2:
                    return nums[1]        # nums[0]=Qty, nums[1]=$ (dollar)
                if nums:
                    return nums[0]
    return None


def parse_store_eom(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    loan = ending_value(rows, "Ending Loan Base")
    inv = ending_value(rows, "Ending Inventory Base")
    if loan is None or inv is None:
        raise ValueError("missing Ending Loan/Inventory Base in %s" % os.path.basename(path))
    return round(loan, 2), round(inv, 2)


def read_company(outdir, end):
    loan_st, inv_st, missing = {}, {}, []
    for s in STORES:
        p = os.path.join(outdir, "%s_%s_end-of-month.xlsx" % (end, s))
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            missing.append(s); continue
        l, i = parse_store_eom(p)
        loan_st[s], inv_st[s] = l, i
    if missing:
        raise FileNotFoundError("missing EOM files for: %s" % ",".join(missing))
    return {
        "loan": {"company": round(sum(loan_st.values()), 2), "stores": loan_st},
        "inventory": {"company": round(sum(inv_st.values()), 2), "stores": inv_st},
    }


def load_or_seed_baseline(asof, reading):
    os.makedirs(BASE_DIR, exist_ok=True)
    path = os.path.join(BASE_DIR, "baseline_%s.json" % asof.strftime("%Y-%m"))
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f), False
    prev_end = asof.replace(day=1) - datetime.timedelta(days=1)
    seed = {
        "as_of_month_end": prev_end.strftime("%Y-%m-%d"),
        "seeded_from": "first-run-of-month EOM reading",
        "loan_company": reading["loan"]["company"],
        "inventory_company": reading["inventory"]["company"],
        "loan_stores": reading["loan"]["stores"],
        "inventory_stores": reading["inventory"]["stores"],
    }
    with open(path, "w") as f:
        json.dump(seed, f, indent=2)
    return seed, True


def fmt_money(v):
    return "${:,.0f}".format(round(v))


def growth_line(label, today_v, base_v):
    d = today_v - base_v
    pct = (d / base_v * 100.0) if base_v else 0.0
    arrow = "▲" if d > 0 else ("▼" if d < 0 else "▬")
    sign = "+" if d >= 0 else "-"
    return "{lab}: {now}  {arr}{sign}{amt} ({sign}{pct:.1f}%)".format(
        lab=label, now=fmt_money(today_v), arr=arrow, sign=sign,
        amt=fmt_money(abs(d)), pct=abs(pct))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--end", required=True, help="END date of the EOM files (yesterday)")
    ap.add_argument("--asof", required=True, help="run day YYYY-MM-DD")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    asof = datetime.datetime.strptime(a.asof, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(a.end, "%Y-%m-%d").date()

    try:
        reading = read_company(a.outdir, a.end)
    except Exception as e:
        sys.stderr.write("READ_FAIL: %s\n" % e)
        return 2

    base, seeded = load_or_seed_baseline(asof, reading)
    me_label = datetime.datetime.strptime(base["as_of_month_end"], "%Y-%m-%d").strftime("%-m/%-d")

    lines = [
        "Valley Pawn — Daily numbers",
        "(balances as of %s close)" % end.strftime("%-m/%-d"),
        "",
        growth_line("Loan Balance", reading["loan"]["company"], base["loan_company"]),
        growth_line("Inventory", reading["inventory"]["company"], base["inventory_company"]),
        "",
        "Growth vs %s month-end." % me_label,
    ]
    if seeded:
        lines.append("(baseline seeded today — growth shows from tomorrow)")
    msg = "\n".join(lines)
    sys.stdout.write(msg + "\n")

    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump({"asof": a.asof, "end": a.end, "reading": reading,
                       "baseline": base, "message": msg}, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
