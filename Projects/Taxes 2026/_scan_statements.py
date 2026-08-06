#!/usr/bin/env python3
"""Scan DuPont / bank statement PDFs for check payments and vendor withdrawals.
Writes a CSV of every transaction line plus a summary. Read-only on the originals."""
import os, re, subprocess, csv, sys, collections

HOME = os.path.expanduser("~")
ICLOUD = os.path.join(HOME, "Library/Mobile Documents/com~apple~CloudDocs")
TAXDIR = os.path.join(HOME, "Documents/Claude/Projects/Taxes 2026")
DROPBOX = os.path.join(TAXDIR, "Bank Statements")   # <- drop new statements here
OUTDIR = os.path.join(TAXDIR, "_raw")
os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(DROPBOX, exist_ok=True)
PDFTOTEXT = "/opt/homebrew/bin/pdftotext"

# Scan iCloud (existing archive) AND the drop folder above. Anything dropped into
# "Taxes 2026/Bank Statements" is picked up regardless of filename.
pdfs = []
for base in (ICLOUD, DROPBOX):
    if not os.path.isdir(base):
        continue
    for root, dirs, fs in os.walk(base):
        low = root.lower()
        for f in fs:
            if not f.lower().endswith(".pdf"):
                continue
            fl = f.lower()
            if base == DROPBOX or "statement" in fl or "statement" in low \
                    or "dupont" in low or "dccu" in low:
                pdfs.append(os.path.join(root, f))
pdfs = sorted(set(pdfs))
print("candidate statement PDFs:", len(pdfs))

# transaction line: MM/DD  -1,234.56  99,999.99  Description
LINE = re.compile(r"^\s*(\d{2}/\d{2})\s+(-?[\d,]+\.\d{2})\s+(-?[\d,]+\.\d{2})\s+(.*\S)\s*$")
ACCT = re.compile(r"Account Number\s+x*(\d+)")
PERIOD = re.compile(r"Statement For\s+(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})")

rows = []
for p in pdfs:
    try:
        r = subprocess.run([PDFTOTEXT, "-layout", "-q", p, "-"],
                           capture_output=True, timeout=120)
        txt = r.stdout.decode("utf-8", "ignore")
    except Exception:
        continue
    if "Transaction Description" not in txt and "Withdrawal" not in txt:
        continue
    acct = ACCT.search(txt)
    acct = acct.group(1) if acct else "?"
    per = PERIOD.search(txt)
    per = per.group(1) + "-" + per.group(2) if per else ""
    year = per[6:10] if per else ""
    for ln in txt.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        md, amt, bal, desc = m.groups()
        try:
            a = float(amt.replace(",", ""))
        except ValueError:
            continue
        rows.append({
            "file": os.path.basename(p), "period": per, "acct": acct,
            "date": (md + "/" + year) if year else md,
            "amount": a, "balance": bal, "desc": desc.strip(),
        })

print("transaction lines parsed:", len(rows))

csvp = os.path.join(OUTDIR, "dupont_transactions.csv")
with open(csvp, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["file", "period", "acct", "date", "amount", "balance", "desc"])
    w.writeheader()
    w.writerows(rows)
print("wrote", csvp)

# ---- checks ----
CHECK = re.compile(r"\b(?:check|draft|share draft)\b", re.I)
CHECKNO = re.compile(r"#?\s*(\d{3,6})\b")
checks = [r for r in rows if CHECK.search(r["desc"]) and r["amount"] < 0]
print("\n=== CHECK-LIKE DEBITS: %d, total $%.2f ===" %
      (len(checks), sum(-r["amount"] for r in checks)))
for r in sorted(checks, key=lambda x: x["amount"])[:40]:
    print("  %s  %10.2f  %s" % (r["date"], r["amount"], r["desc"][:70]))

# ---- large non-transfer debits (candidate contractor payments) ----
SKIP = re.compile(r"transfer to share|transfer from share|online banking transfer|"
                  r"dividend|interest|service charge|loan payment|payroll|"
                  r"withdrawal by cash", re.I)
big = [r for r in rows if r["amount"] < -500 and not SKIP.search(r["desc"])]
big.sort(key=lambda x: x["amount"])
print("\n=== LARGE NON-TRANSFER DEBITS >$500: %d, total $%.2f ===" %
      (len(big), sum(-r["amount"] for r in big)))
for r in big[:60]:
    print("  %s  %10.2f  %s" % (r["date"], r["amount"], r["desc"][:75]))

# ---- payee frequency on big debits ----
print("\n=== TOP PAYEES (large debits) ===")
cnt = collections.Counter()
for r in big:
    key = re.sub(r"[\d#*]+", "", r["desc"])[:45].strip()
    cnt[key] += -r["amount"]
for k, v in cnt.most_common(30):
    print("  %10.2f  %s" % (v, k))
