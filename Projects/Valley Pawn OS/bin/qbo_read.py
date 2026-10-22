#!/usr/bin/env python3
"""qbo_read.py — READ-ONLY QuickBooks API pulls for interactive sessions (2026-10-21). Never writes to QBO.
usage:
  qbo_read.py gl <Account Name> <start> <end> <tag>    General Ledger rows for one account -> _review_src/<tag>.json
  qbo_read.py query "<SELECT ...>" <tag>               any QBO query -> _review_src/<tag>.json
  qbo_read.py report <ReportName> <start> <end> <tag> [key=value ...]
Output folder: Quickbooks Set UP/_review_src/ (prints row counts only)."""
import json, os, sys
QBO_DIR = os.path.expanduser("~/Documents/Claude/Projects/Quickbooks Set UP")
sys.path.insert(0, QBO_DIR)
import qbo_api as q
OUT = os.path.join(QBO_DIR, "_review_src")
a = sys.argv[1:]
if a[0] == "gl":
    acc = q.account_by_name(a[1])
    j = q.report("GeneralLedger", a[2], a[3], account=acc["Id"], columns="tx_date,txn_type,doc_num,name,memo,split_acc,subt_nat_amount,rbal_nat_amount")
    tag = a[4]
elif a[0] == "query":
    j = q.query(a[1]); tag = a[2]
elif a[0] == "report":
    extra = dict(x.split("=", 1) for x in a[5:])
    j = q.report(a[1], a[2], a[3], **extra); tag = a[4]
else:
    sys.exit("bad mode")
p = os.path.join(OUT, tag + ".json")
json.dump(j, open(p, "w"), indent=1)
print("wrote", p, "bytes", os.path.getsize(p))
