#!/usr/bin/env python3
"""Win-back texts: before/after. Read-only on Bravo exports already on disk.
S0 = 9/29-9/30/2026 (full customer directory, captured just as the first texts went out) ; S1 = 11/15/2026.
A = same-age cohorts: fresh forfeiters measured after the same number of days, before vs after texting began.
B = natural return curve at S0 (nobody texted) -> how many of the texted cohort would be expected back anyway."""
import sys, os, glob, csv, collections, datetime as dt
sys.path.insert(0, os.path.expanduser("~/mnt/Projects/Email Refinement/forfeiture_winback"))
import fwb_build as fb
O = os.path.expanduser("~/mnt/Projects/Bravo Data Extraction/output")
ST = ["CUL", "HAR", "LEX", "ROA", "WAY"]
S0, S1 = dt.date(2026, 9, 29), dt.date(2026, 11, 15)

def forfeits(run):
    out = {}
    for s in ST:
        for r in fb.read(f"{O}/{run}_{s}_forfeiture-winback-addr.csv"):
            ds = [d for d in (fb.pdate(r.get("Pull Date")), fb.pdate(r.get("Disposition Date"))) if d]
            if not ds: continue
            k = (s, fb.kname(r.get("Customer")), fb.zip5(r.get("Address")))
            f = min(ds)
            if k not in out or f > out[k]: out[k] = f
    return out

def visits(files):
    L = {}
    for p in files:
        s = os.path.basename(p).split("_")[1]
        for r in fb.read(p):
            d = fb.pdate(r.get("Last Time In", ""))
            if not d: continue
            k = (s, fb.kname(r.get("Name")), (r.get("Zip Code") or "").strip()[:5])
            if k not in L or d > L[k]: L[k] = d
    return L

full = glob.glob(f"{O}/2024-08-30_*_forfeiture-winback-comparison-visits.csv")
weekly0 = [p for p in glob.glob(f"{O}/2026-09-2*_*_forfeiture-winback-comparison-visits.csv")]
weekly1 = [p for p in glob.glob(f"{O}/2026-1*_*_forfeiture-winback-comparison-visits.csv") if os.path.basename(p)[:10] <= "2026-11-15"]
L0 = visits(full + weekly0)
L0 = {k: min(v, S0 + dt.timedelta(days=1)) if v > S0 + dt.timedelta(days=1) else v for k, v in L0.items()}
L1 = visits(full + weekly0 + weekly1)
F0, F1 = forfeits("2026-09-29"), forfeits("2026-11-15")
print("forfeiters S0", len(F0), "matched to a visit record", sum(k in L0 for k in F0), "| S1", len(F1), sum(k in L1 for k in F1))

def back(F, L, k): return k in L and L[k] >= F[k]

# ---- A: same-age cohorts (49-107 days since forfeit)
def cohort(F, L, snap):
    ks = [k for k in F if k in L and 49 <= (snap - F[k]).days <= 107]
    b = sum(back(F, L, k) for k in ks); return len(ks), b
for name, F, L, snap in (("BEFORE texts (forfeited 6/14-8/11, checked 9/29)", F0, L0, S0), ("AFTER texts began (forfeited 7/31-9/27, checked 11/15)", F1, L1, S1)):
    n, b = cohort(F, L, snap); print("A", name, "| forfeiters", n, "| back", b, f"| {100*b/n:.1f}%")
for s in ST:
    a = cohort({k: v for k, v in F0.items() if k[0] == s}, L0, S0); c = cohort({k: v for k, v in F1.items() if k[0] == s}, L1, S1)
    print("  ", s, f"before {a[1]}/{a[0]} = {100*a[1]/max(a[0],1):.1f}% | after {c[1]}/{c[0]} = {100*c[1]/max(c[0],1):.1f}%")

# ---- B: natural curve at S0 by 48-day age bins -> expected returns of the not-back cohort over 48 days
W = 47
bins = collections.defaultdict(lambda: [0, 0])
for k, f in F0.items():
    if k not in L0: continue
    i = (S0 - f).days // W; bins[i][0] += 1; bins[i][1] += back(F0, L0, k)
C = {i: b / n for i, (n, b) in bins.items() if n >= 25}
exp = act = n_tot = 0
rows = []
for i in sorted(C):
    nb = [k for k, f in F0.items() if k in L0 and (S0 - f).days // W == i and not back(F0, L0, k)]
    h = max(0.0, (C.get(i + 1, C[i]) - C[i])) / max(1e-9, 1 - C[i])
    a = sum(1 for k in nb if k in L1 and L1[k] >= S0)
    exp += h * len(nb); act += a; n_tot += len(nb); rows.append((i, len(nb), round(100 * C[i], 1), round(h * len(nb), 1), a))
print("B not-back at 9/29:", n_tot, "| came in 9/29-11/15:", act, f"({100*act/n_tot:.1f}%) | expected with no texts (pre-text curve): {exp:.0f} ({100*exp/n_tot:.1f}%)")
print("  age bin (x47 days), not back, % back by that age before texts, expected, actual")
for r in rows: print("  ", r)
