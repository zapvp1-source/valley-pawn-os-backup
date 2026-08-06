#!/usr/bin/env python3
"""_merge_scrap_weights.py -- additively restore a scrap year-file from backup
while KEEPING any newly-read weight the interrupted pull managed to capture.

WHY THIS EXISTS (2026-08-04): a targeted pull calls ResetOutputFile, which
truncates the store's whole year file before writing. If the run is then cut
off partway (Bravo wedging, EnsureStore failure, watcher timeout), the file is
left holding only the handful of rows written before the cut -- silently
destroying the rest of the year. That happened twice in one day.

This merges backup (base, complete) with current (partial, but may contain
genuinely NEW weights for buckets that were previously blank):
  - every row in the backup is preserved
  - where the backup's weight is blank and the partial has one, fill it in
  - rows present only in the partial are appended
Nothing is ever overwritten with a blank, and no row is dropped.

Key is (Store, BucketName) within a single store-year file, which is unique --
the cross-year collision problem does not apply inside one year's file.
"""
import csv, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")
BAK = os.path.join(OUT, "_backups_20260804")
HDR = ["Store", "Month", "BucketName", "CreatedOn", "Status", "StatusDate",
       "CombinedMetalWeightDwt"]


def load(path):
    """-> (ordered list of rows, dict keyed by (store,bucket)->row)"""
    rows = []
    if not os.path.exists(path):
        return rows, {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.reader(fh):
            if not r or r[0] == "Store":
                continue
            while len(r) < 7:
                r.append("")
            rows.append(r)
    idx = {}
    for r in rows:
        idx.setdefault((r[0], r[2]), r)
    return rows, idx


def merge(store, year="2026"):
    cur_path = os.path.join(OUT, f"{year}_{store}_scrap-refining-gold.csv")
    bak_path = os.path.join(BAK, f"{year}_{store}_scrap-refining-gold.csv")
    if not os.path.exists(bak_path):
        print(f"  {store}: no backup, skipping")
        return
    cur_rows, cur_idx = load(cur_path)
    bak_rows, bak_idx = load(bak_path)

    if len(cur_rows) >= len(bak_rows):
        print(f"  {store}: current ({len(cur_rows)}) >= backup ({len(bak_rows)}) - leaving as is")
        return

    filled, added = [], 0
    # start from the backup (complete), overlay newly-read weights
    for r in bak_rows:
        new = cur_idx.get((r[0], r[2]))
        if new and not r[6].strip() and new[6].strip():
            r[6] = new[6]
            filled.append(f"{r[2]} = {new[6]}")
    # append anything the partial saw that the backup never had
    for r in cur_rows:
        if (r[0], r[2]) not in bak_idx:
            bak_rows.append(r)
            added += 1

    with open(cur_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(HDR)
        w.writerows(bak_rows)

    print(f"  {store}: restored {len(bak_rows)} rows "
          f"({len(filled)} blank weights filled, {added} new buckets)")
    for f in filled:
        print(f"      + {f}")


if __name__ == "__main__":
    stores = sys.argv[1:] or ["CUL", "HAR", "LEX", "ROA", "WAY"]
    print("merging partial pull results back onto backups:")
    for s in stores:
        merge(s)
