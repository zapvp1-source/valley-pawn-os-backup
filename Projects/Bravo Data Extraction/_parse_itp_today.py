import csv, os, re
base = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
DATE = "2026-06-22"
logf = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/items-to-price-full-2026-06-22T09-49-32.log"

# integrity: scan log for any truncation signal
log = ""
try:
    log = open(logf, encoding="utf-8", errors="ignore").read()
except Exception:
    pass
gaveup = "GAVE UP" in log

tot_c = 0; tot_d = 0.0
for s in ["CUL", "HAR", "LEX", "ROA", "WAY"]:
    f = os.path.join(base, f"{DATE}_{s}_items-to-price.csv")
    if not os.path.exists(f):
        print(f"{s}\tMISSING"); continue
    cnt = 0; dsum = 0.0
    with open(f, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            cnt += 1
            v = (row.get("Cost") or "").replace("$", "").replace(",", "").strip()
            try: dsum += float(v)
            except: pass
    tot_c += cnt; tot_d += dsum
    print(f"{s}\t{cnt}\t{dsum:0.2f}")
print(f"TOTAL\t{tot_c}\t{tot_d:0.2f}")
print(f"GAVE_UP\t{gaveup}")
