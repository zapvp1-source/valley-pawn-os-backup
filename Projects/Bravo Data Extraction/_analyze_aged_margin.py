#!/usr/bin/env python3
"""Aged jewelry margin analysis — per-store stats from aged-jewelry-sales CSVs."""
import csv, glob, statistics, sys
from pathlib import Path

OUT = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output")

def money(s):
    try:
        return float(s.replace("$", "").replace(",", "").strip())
    except Exception:
        return None

def analyze(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            c, p = money(r.get("Cost", "")), money(r.get("Last Sold Price", ""))
            if c is None or p is None or p <= 0:
                continue
            rows.append({"num": r["Number"], "cat": r["Category"],
                         "type": (r.get("Type") or "").strip() or "UNKNOWN",
                         "cost": c, "price": p})
    if not rows:
        return None
    def agg(rs, label):
        tc = sum(r["cost"] for r in rs)
        tp = sum(r["price"] for r in rs)
        mults = [r["price"] / r["cost"] for r in rs if r["cost"] > 0]
        return {
            "label": label, "n": len(rs),
            "cost": round(tc, 2), "rev": round(tp, 2),
            "blended_mult": round(tp / tc, 2) if tc else None,
            "median_mult": round(statistics.median(mults), 2) if mults else None,
            "margin_pct": round(100 * (tp - tc) / tp, 1) if tp else None,
        }
    out = {"file": Path(path).name, "all": agg(rows, "ALL")}
    # outlier-trimmed (exclude cost >= 5000 single items e.g. the 3.8ct diamond)
    trimmed = [r for r in rows if r["cost"] < 5000]
    out["trimmed"] = agg(trimmed, "TRIMMED<5k")
    for t in sorted(set(r["type"] for r in rows)):
        out[t] = agg([r for r in rows if r["type"] == t], t)
    return out

for path in sorted(glob.glob(str(OUT / "2025-07-28_to_2026-07-27_*_aged-jewelry-sales.csv"))):
    res = analyze(path)
    if not res:
        continue
    print(f"\n=== {res['file']} ===")
    for k, v in res.items():
        if k == "file":
            continue
        print(f"  {v['label']:<14} n={v['n']:<4} cost=${v['cost']:>10,.2f} rev=${v['rev']:>10,.2f} "
              f"blended={v['blended_mult']}x median={v['median_mult']}x margin={v['margin_pct']}%")
