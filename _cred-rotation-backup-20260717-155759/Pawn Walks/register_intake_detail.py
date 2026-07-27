#!/usr/bin/env python3
# Additively register the intake-detail cell in bravo_watcher.ahk:
#   1) #Include reports\IntakeDetail.ahk   (after the BuysFromPublic include)
#   2) REPORT_HANDLERS["intake-detail"] := PullIntakeDetail  (after the buys-from-public dispatch)
# New lines only. Idempotent. Backs up first. Original lines untouched.
import shutil, datetime, sys

W = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_watcher.ahk"
ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
shutil.copy(W, W + f".bak-pre-intake-detail-{ts}")

lines = open(W).read().split("\n")
inc_anchor  = "#Include reports\\BuysFromPublic.ahk"
inc_new     = "#Include reports\\IntakeDetail.ahk"
disp_anchor = 'REPORT_HANDLERS["buys-from-public"]'
disp_new    = '    REPORT_HANDLERS["intake-detail"]           := PullIntakeDetail'

if inc_new in "\n".join(lines):
    print("include already present — skipping")
else:
    out = []
    for ln in lines:
        out.append(ln)
        if inc_anchor in ln:
            out.append(inc_new)
    lines = out
    print("inserted #Include reports\\IntakeDetail.ahk")

if disp_new.strip() in "\n".join(lines):
    print("dispatch already present — skipping")
else:
    out = []
    for ln in lines:
        out.append(ln)
        if disp_anchor in ln and "PullBuysFromPublic" in ln:
            out.append(disp_new)
    lines = out
    print("inserted intake-detail dispatch")

open(W, "w").write("\n".join(lines))

# verify
txt = open(W).read()
print("=== verify ===")
print("includes IntakeDetail:", txt.count(inc_new))
print("dispatch intake-detail:", txt.count('REPORT_HANDLERS["intake-detail"]'))
print("buys-from-public still present (untouched):", txt.count('REPORT_HANDLERS["buys-from-public"]'))
for ln in txt.split("\n"):
    if "IntakeDetail" in ln or 'intake-detail' in ln:
        print("  >>", ln)
