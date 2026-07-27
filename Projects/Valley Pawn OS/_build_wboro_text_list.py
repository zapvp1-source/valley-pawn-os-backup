#!/usr/bin/env python3
"""Build the Waynesboro 6-day announcement text list from Bravo chekkit-invites-range CSVs.
Last ~12 months (files 2025-07-31 onward), dedupe by phone, exclude DNT and blank phones."""
import csv, glob, re
from pathlib import Path

OUT = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/waynesboro_6day_text_list_2026-07-23.csv")
files = sorted(glob.glob("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/*_WAY_chekkit-invites-range.csv"))
files = [f for f in files if Path(f).name >= "2025-07-31"]
print("files used:", len(files))

seen = {}
dnt_count = blank = 0
for f in files:
    with open(f, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            phone = re.sub(r"\D", "", row.get("phone") or "")
            if len(phone) == 11 and phone.startswith("1"):
                phone = phone[1:]
            if len(phone) != 10:
                blank += 1
                continue
            if (row.get("dnt") or "").strip().upper() == "DNT":
                dnt_count += 1
                seen[phone] = None  # DNT wins even if a later row lacks the flag
                continue
            if phone in seen and seen[phone] is None:
                continue  # already marked DNT
            first = (row.get("first_name") or "").strip().title()
            last = (row.get("last_name") or "").strip().title()
            lv = (row.get("last_visit") or "").strip()
            prev = seen.get(phone)
            if prev is None and phone in seen:
                continue
            if prev is None or (lv and lv > (prev.get("last_visit") or "")):
                seen[phone] = {"first_name": first, "last_name": last, "phone": phone, "last_visit": lv}

rows = [v for v in seen.values() if v]
rows.sort(key=lambda r: r["last_visit"], reverse=True)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["first_name", "last_name", "phone", "last_visit"])
    w.writeheader()
    w.writerows(rows)
print(f"unique sendable: {len(rows)} | DNT excluded: {dnt_count} | bad/blank phones: {blank}")
print("wrote:", OUT)
