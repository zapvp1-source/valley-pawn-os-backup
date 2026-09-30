#!/usr/bin/env python3
"""mobilepawn_monthly.py <YYYY-MM> [out_dir] — MobilePawn participation by store for one full month.

Deterministic formatter for the `monthly-mobilepawn-participation` scheduled task (built 2026-09-29).
Reads Bravo End-of-Month XLSX that ALREADY exist — never touches Bravo:
  1. <BDE>/output/monthly-analytics/<YM>/same-month-current_<STORE>.xlsx   (staged by monthly-analytics-prestage)
  2. fallback: <BDE>/output/<YYYY-MM-DD>_<STORE>_end-of-month.xlsx whose Reporting Dates = that full month
Year-ago month: same-month-prior_<STORE>.xlsx, then the same fallback for (Y-1, M).

Exit 0 -> stdout is the Slack post, verbatim (also written to <out_dir>/slack_post.txt).
Exit 2 -> HOLD: <out_dir>/HOLD.txt says what is missing. Publish NOTHING (Rule 18).
Also writes <out_dir>/mobilepawn_<YM>.json (all numbers) and appends/refreshes the project history CSV.

Metric (locked 2026-09-29):
  % of loan payments made in the app = MobilePawn "Loan Payments" qty /
      (that + In-Store Renewals + Partial Payments + Extensions qty). Redemptions excluded (pickup is in-store).
  Active app customers = MobilePawn "Customers Active".
"""
import calendar, csv, datetime as dt, glob, json, os, sys

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects")
BDE_OUT = os.path.join(PROJ, "Bravo Data Extraction/output")
MPP = os.path.join(PROJ, "MobilePawn Participation")
sys.path.insert(0, MPP)
import mobilepawn_participation as mpp  # parse(), month_ok(), metrics()

STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAME = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}


def load(store, y, m, staged_key):
    """Return metrics dict for a FULL calendar month, or (None, reason)."""
    want = (y, m)
    cands = [os.path.join(BDE_OUT, "monthly-analytics", "%04d-%02d" % (y, m) if staged_key == "same-month-current"
                          else "%04d-%02d" % (y + 1, m), "%s_%s.xlsx" % (staged_key, store))]
    cands += sorted(glob.glob(os.path.join(BDE_OUT, "%04d-%02d-*_%s_end-of-month.xlsx" % (y, m, store))), reverse=True)
    reasons = []
    for f in cands:
        if not os.path.isfile(f) or os.path.getsize(f) < 2048:
            continue
        try:
            d = mpp.parse(f)
        except Exception as e:
            reasons.append("%s unreadable (%s)" % (os.path.basename(f), e)); continue
        if d["store"] != store:
            reasons.append("%s is for store %s" % (os.path.basename(f), d["store"])); continue
        mo = mpp.month_ok(d["range"])
        if not mo or (mo[0].year, mo[0].month) != want or not mo[2]:
            reasons.append("%s covers %s, not the full month" % (os.path.basename(f), d["range"])); continue
        if not d["mp"] or "pay_qty" not in d["mp"] or "cust" not in d["mp"]:
            reasons.append("%s has no MobilePawn section" % os.path.basename(f)); continue
        r = mpp.metrics(d, os.path.basename(f), want, mo[1], True)
        if (r["mp_loan_pmts"] + r["instore_pmts"]) == 0:
            reasons.append("%s shows zero loan payments (parse failure signature)" % os.path.basename(f)); continue
        return r, None
    return None, "; ".join(reasons) or "no full-month report on file"


def pct(a, b):
    return 100.0 * a / b if b else None


def main():
    ym = sys.argv[1]
    y, m = map(int, ym.split("-"))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(MPP, "out", ym)
    os.makedirs(out, exist_ok=True)
    cur, prior, hold = {}, {}, []
    for s in STORES:
        r, why = load(s, y, m, "same-month-current")
        if r: cur[s] = r
        else: hold.append("%s %s: %s" % (s, ym, why))
        p, why = load(s, y - 1, m, "same-month-prior")
        if p: prior[s] = p
        else: hold.append("%s %04d-%02d (year-ago): %s" % (s, y - 1, m, why))
    if hold:
        open(os.path.join(out, "HOLD.txt"), "w").write("HOLD %s\n" % ym + "\n".join(hold) + "\n")
        print("HOLD — see %s" % os.path.join(out, "HOLD.txt"), file=sys.stderr)
        sys.exit(2)
    if os.path.exists(os.path.join(out, "HOLD.txt")):
        os.remove(os.path.join(out, "HOLD.txt"))

    # Reconciliation checks — any failure is a HOLD
    checks = []
    for s in STORES:
        c = cur[s]
        checks.append((s + " pct in 0-100", 0 <= c["pct_pmts_mobile"] <= 100))
        checks.append((s + " customers <= payments+layaway", c["mp_customers_active"] <= c["mp_loan_pmts"] + c["mp_layaway_pmts"] + 1))
        checks.append((s + " month label", c["month"] == ym))
    bad = [n for n, ok in checks if not ok]
    if bad:
        open(os.path.join(out, "HOLD.txt"), "w").write("HOLD %s — checks failed:\n" % ym + "\n".join(bad) + "\n")
        sys.exit(2)

    tot = lambda D, k: sum(D[s][k] for s in STORES)
    co = pct(tot(cur, "mp_loan_pmts"), tot(cur, "mp_loan_pmts") + tot(cur, "instore_pmts"))
    co_ly = pct(tot(prior, "mp_loan_pmts"), tot(prior, "mp_loan_pmts") + tot(prior, "instore_pmts"))
    rows = []
    for s in STORES:
        c, p = cur[s]["pct_pmts_mobile"], prior[s]["pct_pmts_mobile"]
        rows.append((NAME[s], c, c - p, int(cur[s]["mp_customers_active"])))
    rows.sort(key=lambda r: -r[1])
    mon = "%s %d" % (calendar.month_name[m], y)
    ly = "%s %d" % (calendar.month_abbr[m], y - 1)
    sgn = lambda v: ("+%.1f" % v) if v >= 0.05 else ("%.1f" % v if v <= -0.05 else "0.0")
    lines = [
        ":iphone: *MobilePawn Participation — %s*" % mon,
        "",
        "Company: *%.1f%%* of loan payments were made in the app (%s pts vs %s). %d customers active in the app."
        % (co, sgn(co - co_ly), ly, int(tot(cur, "mp_customers_active"))),
        "",
        "| Store | Payments in App | vs %s | Active App Customers |" % ly,
        "|---|---|---|---|",
    ]
    for n, c, d, cu in rows:
        lines.append("| %s | %.1f%% | %s pts | %d |" % (n, c, sgn(d), cu))
    lines.append("| *Company* | *%.1f%%* | *%s pts* | *%d* |" % (co, sgn(co - co_ly), int(tot(cur, "mp_customers_active"))))
    lines += ["", "Customers who pay in the app can keep their loan current without a trip to the store — "
              "keep offering MobilePawn at every new loan and extension."]
    post = "\n".join(lines)
    open(os.path.join(out, "slack_post.txt"), "w").write(post + "\n")
    json.dump({"month": ym, "company_pct": round(co, 1), "company_pct_ly": round(co_ly, 1),
               "current": cur, "year_ago": prior}, open(os.path.join(out, "mobilepawn_%s.json" % ym), "w"), indent=1, default=str)
    # refresh project history CSV (full rebuild from everything on file — idempotent)
    try:
        hist = mpp.history(BDE_OUT, quiet=True)
        full = {(D[s]["store"], D[s]["month"]): D[s] for D in (cur, prior) for s in STORES}
        hist = [r for r in hist if (r["store"], r["month"]) not in full] + list(full.values())
        hist.sort(key=lambda r: (r["store"], r["month"]))
        with open(os.path.join(MPP, "mobilepawn_participation_by_store_month.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(hist[0].keys())); w.writeheader(); w.writerows(hist)
    except Exception as e:
        print("history refresh skipped: %s" % e, file=sys.stderr)
    print(post)


if __name__ == "__main__":
    main()
