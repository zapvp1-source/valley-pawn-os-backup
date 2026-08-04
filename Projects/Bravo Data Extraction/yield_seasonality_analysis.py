"""
Seasonal yield analysis for Valley Pawn bonus targets.
ADDITIVE - reads only; modifies nothing.
Yield(M) = NetRevenue(M) / EndingAssets(M-1)
"""
import subprocess, json, sys, statistics

EXTRACT = "/usr/bin/python3"
SCRIPT  = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bonus_kpis_extract.py"
STORES  = ["CUL","HAR","LEX","ROA","WAY"]
NAME    = {"CUL":"Culpeper","HAR":"Harrisonburg","LEX":"Lexington","ROA":"Roanoke","WAY":"Waynesboro"}
M       = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
LAST25  = ["2025-01-31","2025-02-28","2025-03-31","2025-04-30","2025-05-31","2025-06-30",
           "2025-07-31","2025-08-31","2025-09-30","2025-10-31","2025-11-30","2025-12-31"]

# 2025 revenue as recorded in VP BONUS FINAL col B (independent cross-check)
SHEET25 = {
 "Culpeper":[38142,44377,43842,41009,43967,37538,51013,50164,43685,73807,55742,65775],
 "Harrisonburg":[34965,39690,34907,33301,34744,40365,44202,39769,45435,47173,44887,48057],
 "Roanoke":[28001,29924,27236,26797,32471,31824,32158,32867,34202,42737,30926,40807],
 "Lexington":[18364,20554,22318,22318,24602,23134,22618,21270,23256,27957,21955,23712],
 "Waynesboro":[24576,34119,29656,26717,34005,31514,25380,31240,30192,27617,36388,34737],
}
# 2026 actuals already verified in the workbook: revenue (D) and ending assets (G), Jan..Jul
REV26 = {
 "Culpeper":[69042,61825,72821,59585,74327.94,74594.07,61751.95],
 "Harrisonburg":[52537,45876,49281,58540,38507.50,71550.31,42881.84],
 "Roanoke":[30267,40889,50192,39799,39050,42193.38,48831.78],
 "Lexington":[25967,25867,32468,24206,21419.43,24977.23,21701.62],
 "Waynesboro":[37416,35640,37554,41397,35140.72,48931.66,40329.99],
}
EA26 = {
 "Culpeper":[360000,355000,338000,355152,371923.16,388739.87,394927.16],
 "Harrisonburg":[317000,309000,309000,291120,326705.38,331636.89,338634.38],
 "Roanoke":[265000,258300,257000,259770,277107.47,289076.71,285614.87],
 "Lexington":[171000,161000,155000,145950,159075.85,164492.43,169803.34],
 "Waynesboro":[177000,181000,189000,185064,219126.24,227057.24,246154.17],
}

def pull(enddate):
    r = subprocess.run([EXTRACT, SCRIPT, enddate], capture_output=True, text=True)
    try: d = json.loads(r.stdout)
    except Exception: return None
    if "error" in d: return None
    return d["data"]

def main():
    print("=" * 78)
    print("STEP 1 - PULL 2025 MONTHLY EOM DATA + Dec-2024 opening assets")
    print("=" * 78)
    raw = {}
    dec24 = pull("2024-12-31")
    if dec24: print("  2024-12-31 opening assets OK")
    else: print("  !! 2024-12-31 MISSING - Jan-2025 yield cannot be computed")
    missing = []
    for i, ed in enumerate(LAST25):
        d = pull(ed)
        if d is None:
            missing.append(ed); print("  %s  MISSING" % ed); continue
        raw[i] = d
        print("  %s  ok" % ed)
    if missing:
        print("\nMISSING MONTHS: %s" % ", ".join(missing))

    print()
    print("=" * 78)
    print("STEP 2 - VALIDATE pulled revenue vs workbook col B (2025)")
    print("=" * 78)
    print("%-14s %-5s %12s %12s %9s" % ("Store","Mon","Bravo","Workbook","Diff%"))
    bad = 0
    for s in STORES:
        for i in range(12):
            if i not in raw or s not in raw[i]: continue
            b = raw[i][s]["net_revenue"]; w = SHEET25[NAME[s]][i]
            dp = (b - w) / w * 100 if w else 0
            flag = "" if abs(dp) < 2.0 else "   <== MISMATCH"
            if flag: bad += 1
            if flag or i == 0:
                print("%-14s %-5s %12.2f %12.0f %8.1f%%%s" % (NAME[s], M[i], b, w, dp, flag))
    print("\nMismatches (>2%%): %d of %d" % (bad, len(raw) * 5))

    print()
    print("=" * 78)
    print("STEP 3 - MONTHLY YIELD  =  Revenue(M) / EndingAssets(M-1)")
    print("=" * 78)
    y25 = {}
    for s in STORES:
        y25[s] = []
        for i in range(12):
            if i == 0:
                prev = dec24[s] if dec24 and s in dec24 else None
            else:
                prev = raw[i-1][s] if (i-1) in raw and s in raw[i-1] else None
            cur = raw[i][s] if i in raw and s in raw[i] else None
            if not prev or not cur: y25[s].append(None); continue
            ea = prev["loan_balance"] + prev["inventory_balance"]
            y25[s].append(cur["net_revenue"] / ea if ea else None)
    hdr = "%-14s" % "Store" + "".join("%8s" % m for m in M)
    print("2025 YIELD"); print(hdr)
    for s in STORES:
        print("%-14s" % NAME[s] + "".join(("%7.2f%%" % (v*100)) if v else "      --" for v in y25[s]))

    y26 = {}
    for s in STORES:
        n = NAME[s]; y26[s] = []
        for i in range(7):
            if i == 0:
                prev = dec24 and None
                ea = None
                if 11 in raw and s in raw[11]:
                    ea = raw[11][s]["loan_balance"] + raw[11][s]["inventory_balance"]
            else:
                ea = EA26[n][i-1]
            y26[s].append(REV26[n][i] / ea if ea else None)
    print("\n2026 YIELD (Jan-Jul)"); print("%-14s" % "Store" + "".join("%8s" % m for m in M[:7]))
    for s in STORES:
        print("%-14s" % NAME[s] + "".join(("%7.2f%%" % (v*100)) if v else "      --" for v in y26[s]))

    print()
    print("=" * 78)
    print("STEP 4 - SEASONAL YIELD INDEX (month yield / store's own annual avg yield)")
    print("=" * 78)
    print("%-6s %10s %10s %10s   %s" % ("Month","2025 idx","2026 idx","agree?","per-store 2025 idx"))
    idx25 = {}
    for i in range(12):
        vals = []
        for s in STORES:
            good = [v for v in y25[s] if v]
            if not good or not y25[s][i]: continue
            vals.append(y25[s][i] / (sum(good)/len(good)))
        idx25[i] = (sum(vals)/len(vals)) if vals else None
    idx26 = {}
    for i in range(7):
        vals = []
        for s in STORES:
            good = [v for v in y26[s] if v]
            if not good or not y26[s][i]: continue
            vals.append(y26[s][i] / (sum(good)/len(good)))
        idx26[i] = (sum(vals)/len(vals)) if vals else None
    for i in range(12):
        a = idx25.get(i); b = idx26.get(i)
        ps = ""
        agree = ""
        if a and b:
            agree = "yes" if (a-1)*(b-1) > 0 or abs(a-b) < 0.05 else "NO"
        print("%-6s %10s %10s %10s" % (M[i],
              ("%.3f"%a) if a else "--", ("%.3f"%b) if b else "--", agree))

    print()
    print("=" * 78)
    print("STEP 5 - AUGUST READ")
    print("=" * 78)
    a = idx25.get(7)
    if a:
        print("August 2025 yield index: %.3f  (1.000 = that store's annual average yield)" % a)
        print("=> Using a flat YTD-average yield for an August target is")
        print("   %s by roughly %.1f%%." % ("TOO HIGH" if a < 1 else "TOO LOW", abs(1-a)*100))
    ytd = [idx25[i] for i in range(1,7) if idx25.get(i)]
    if ytd and a:
        base = sum(ytd)/len(ytd)
        print("\nFeb-Jul 2025 avg index (the window Option B averages): %.3f" % base)
        print("August index / that window: %.3f" % (a/base))
        print("=> seasonal correction factor to apply to an Aug target: x%.3f" % (a/base))

main()
