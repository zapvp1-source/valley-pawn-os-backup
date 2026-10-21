#!/usr/bin/env python3
"""vp_new_customer_report.py [YYYY-MM] [--render] [--no-pull] — native `vp-new-customer-report`
(3rd of month 07:00 ET; Mac-first wave 3 second pass, 2026-10-20). The SKILL's steps, nothing re-derived:
  1  target = the full prior calendar month
  2  Bravo Data Extraction/output/new_customers_monthly_rollup.json — a store already in it for the month is not re-pulled
  3  missing stores: ONE chekkit-invites-range trigger for <first>..<last> (bin/bravo_pull.sh); a CSV only counts when a
     result JSON says it covers exactly <first>..<last> (a daily review-invite pull can share the file name)
  4  count data rows per store CSV; append {"store","month","count"} rows to the rollup (additive, backup first)
  5  MoM / YoY per store from the rollup; company total DEDUPED by email (case-insensitive), else phone, from the raw
     month CSVs — for this month, last month and the same month last year (the 10/3 post used raw-file dedupe for all
     three: 410 vs 448 = -8%, vs 312 = +31%)
  6  post to #new-customers (C0BHF9NM0BH), ranked highest first, ties share rank + medal; duplicate guard on
     "New Customers — <Month Year>" (30 d). A store whose pull failed is NOT mentioned in the post — one ledger row
     (failure policy v3) instead of the SKILL's old DM.
  7  the claude.ai artifact refresh is best-effort in the SKILL and has no Mac path — skipped, logged.
--render: steps 2,4,5 on files already on disk (no pull, no rollup write), prints the post, sends nothing.
"""
import csv
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "vp-new-customer-report"
CH = "C0BHF9NM0BH"
BRAVO = os.path.join(L.PROJ, "Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
ROLLUP = os.path.join(OUT, "new_customers_monthly_rollup.json")
LOG = os.path.join(L.OS_DIR, "monthly-analytics", "logs")


def covering_csv(store, first, last):
    """The CSV a successful chekkit-invites-range cell wrote for exactly first..last (newest result wins)."""
    want = "%s..%s" % (first.isoformat(), last.isoformat())
    best = None
    for rp in glob.glob(os.path.join(BRAVO, "results", "*.result.json")):
        try:
            res = json.load(open(rp, encoding="utf-8-sig"))
        except Exception:
            continue
        for c in res.get("cells", []):
            if (c.get("report") == "chekkit-invites-range" and c.get("store") == store and c.get("status") == "success"
                    and str(c.get("date", "")) == want):
                p = os.path.join(OUT, str(c.get("output_path", "")).replace("\\", "/").split("/")[-1])
                if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(rp) - 600 and (best is None or os.path.getmtime(rp) > best[0]):
                    best = (os.path.getmtime(rp), p)
    if best:
        return best[1]
    # Older month files (backfills before result JSONs were kept) — only for PAST comparisons, never the target month.
    p = os.path.join(OUT, "%s_%s_chekkit-invites-range.csv" % (last.isoformat(), store))
    return p if os.path.exists(p) else None


def rows(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return [r for r in csv.DictReader(fh)]


def dedup(paths):
    seen, n = set(), 0
    for p in paths:
        for r in rows(p):
            n += 1
            k = (r.get("email") or "").strip().lower() or (r.get("phone") or "").strip() or ("row", p, n)
            seen.add(k)
    return len(seen)


def pct(cur, prev):
    if prev in (None, 0):
        return "n/a"
    v = round((cur - prev) * 100.0 / prev)
    return "%+d%%" % v if v != 0 else "+0%"


def month_paths(period, strict):
    _, first, last, _ = L.months(period)
    ps = {}
    for s in L.STORES:
        p = covering_csv(s, first, last) if strict else None
        if not p:
            cand = os.path.join(OUT, "%s_%s_chekkit-invites-range.csv" % (last.isoformat(), s))
            p = cand if (not strict and os.path.exists(cand)) else p
        if p:
            ps[s] = p
    return ps


def shift(period, months_back):
    y, m = map(int, period.split("-"))
    m -= months_back
    while m <= 0:
        m += 12; y -= 1
    return "%04d-%02d" % (y, m)


def build(period, counts, roll):
    _, first, last, label = L.months(period)
    pm, py = shift(period, 1), shift(period, 12)
    rc = {(r["store"], r["month"]): r["count"] for r in roll if "month" in r}
    lines = []
    ranked = sorted(L.STORES, key=lambda s: -counts[s])
    rank, prev_val = 0, None
    for i, s in enumerate(ranked):
        if counts[s] != prev_val:
            rank, prev_val = i + 1, counts[s]
        medal = ":first_place_medal: " if rank == 1 else ""
        lines.append("%d. %s%s: %d (MoM %s, YoY %s)" % (rank, medal, L.NAMES[s], counts[s],
                                                        pct(counts[s], rc.get((s, pm))), pct(counts[s], rc.get((s, py)))))
    cur_paths = month_paths(period, True)
    tot = dedup([cur_paths[s] for s in L.STORES])
    mp, yp = month_paths(pm, False), month_paths(py, False)
    tot_m = dedup([mp[s] for s in L.STORES]) if len(mp) == 5 else None
    tot_y = dedup([yp[s] for s in L.STORES]) if len(yp) == 5 else None
    body = ":bar_chart: New Customers — %s (ranked)\n%s\n\nCompany total (deduped): %d (MoM %s, YoY %s)" % (
        label, "\n".join(lines), tot, pct(tot, tot_m), pct(tot, tot_y))
    return body, label


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    period = args[0] if args else L.prev_month()
    _, first, last, label = L.months(period)
    roll = json.load(open(ROLLUP))
    have = {r["store"]: r["count"] for r in roll if r.get("month") == period}
    missing = [s for s in L.STORES if s not in have]
    notes = []
    if missing and not render and "--no-pull" not in sys.argv:
        tid = "new-customers-monthly-native-%s" % L.now().strftime("%Y%m%dT%H%M%S")
        subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), "chekkit-invites-range",
                        "%s..%s" % (first, last), ",".join(missing), tid], capture_output=True, text=True, timeout=7500)
    counts, failed = {}, []
    for s in L.STORES:
        p = covering_csv(s, first, last)
        if p:
            counts[s] = len(rows(p))
            if s in have and have[s] != counts[s]:
                notes.append("%s: rollup %d vs file %d (rollup kept — already published)" % (s, have[s], counts[s]))
                counts[s] = have[s]
        elif s in have:
            counts[s] = have[s]
        else:
            failed.append(s)
    if failed:
        L.ledger(TASK, "%s new-customer numbers for %s are missing, so the report was held" % (", ".join(failed), label))
        print("HELD: no covering pull for", failed)
        return 3
    new_rows = [{"store": s, "month": period, "count": counts[s]} for s in L.STORES if s not in have]
    if new_rows and not render:
        shutil.copy2(ROLLUP, ROLLUP + ".bak-%s" % L.now().strftime("%Y%m%d-%H%M%S"))
        json.dump(roll + new_rows, open(ROLLUP, "w"), indent=1)
        roll = roll + new_rows
    elif new_rows:
        roll = roll + new_rows
    body, label = build(period, counts, roll)
    for n in notes:
        print("NOTE", n)
    marker = "New Customers — %s" % label
    if not render and L.already(CH, marker, 24 * 30):
        print("already posted:", marker)
        return 0
    ok = L.post(TASK, CH, body, render)
    os.makedirs(LOG, exist_ok=True)
    if not render:
        open(os.path.join(LOG, "new-customers.log"), "a").write("%s %s posted=%s artifact=skipped(no Mac path)\n" % (L.now().isoformat(), period, ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
