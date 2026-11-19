#!/usr/bin/env python3
"""No-send dry plan on data already on disk (no Bravo touch): open-loan book pulled 10/7/2026 + the full
customer contact directory captured 9/29-9/30. Answers: how many open loans can be matched to exactly one
phone, how many of those customers have no app, and about how many loan texts a month that means per store."""
import sys, os, glob, csv, collections, datetime as dt
sys.path.insert(0, os.path.expanduser("~/mnt/Projects/Email Refinement/forfeiture_winback"))
sys.path.insert(0, os.path.expanduser("~/mnt/Projects/Loan Reminder Texts"))
import fwb_build as fb, reminder_core as rc
O = os.path.expanduser("~/mnt/Projects/Bravo Data Extraction/output")
SNAP = dt.date(2026, 10, 7)
tot = collections.Counter()
for s in ["CUL", "HAR", "LEX", "ROA", "WAY"]:
    rows = []
    for f in glob.glob(f"{O}/*_{s}_pm-loan-growth-p*.csv"):
        raw = list(csv.reader(open(f, encoding="utf-8-sig", errors="ignore")))
        hi = next((i for i, r in enumerate(raw) if "Ticket Number" in r), None)
        if hi is None: continue
        rows += [dict(zip(raw[hi], r)) for r in raw[hi + 1:] if len(r) >= len(raw[hi])]
    t = {}
    for r in rows:
        if (r.get("Disposition") or "").strip().upper() == "ON LOAN": t[r["Ticket Number"]] = r
    contacts = collections.defaultdict(set)
    for f in glob.glob(f"{O}/*_{s}_forfeiture-winback-comparison-contacts.csv"):
        for r in fb.read(f):
            p = rc.phone10(r.get("Phone"))
            if p: contacts[fb.kname(r.get("Name"))].add(p)
    c = collections.Counter(); custs = {}
    for tk, r in t.items():
        k = fb.kname(r.get("Customer")); ph = contacts.get(k, set())
        app = (r.get("MobilePawn") or "").strip() == "Activated"
        st = "one phone" if len(ph) == 1 else ("no phone found" if not ph else "name has 2+ phones")
        c["tickets"] += 1; c[st] += 1; c["app" if app else "no app"] += 1
        due = rc.parse_date(r.get("Due Date"))
        if st == "one phone" and not app:
            c["textable no-app tickets"] += 1
            if due:
                d = (due - SNAP).days
                if 1 <= d <= 30: c["courtesy texts next 30d (1 per customer per day)"] += 0; custs.setdefault(("c", k, due), 1)
                if d < 0:
                    c["already past due tickets"] += 1; custs.setdefault(("p", k), 1)
    court = sum(1 for x in custs if x[0] == "c"); pastc = sum(1 for x in custs if x[0] == "p")
    est = court + court * 0 + pastc * 4          # courtesy once; each past-due customer about 4 Fridays
    print(s, dict(c)); print("   est. loan texts/month to no-app customers: courtesy", court, "+ past-due customers", pastc, "x ~4 Fridays =", est)
    tot["tickets"] += c["tickets"]; tot["one"] += c["one phone"]; tot["none"] += c["no phone found"]; tot["multi"] += c["name has 2+ phones"]; tot["est"] += est; tot["noapp"] += c["no app"]
print("ALL", dict(tot), f"match {100*tot['one']/tot['tickets']:.1f}%")
