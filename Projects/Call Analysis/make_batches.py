#!/usr/bin/env python3
"""
make_batches.py — chunk a date range of saved call transcripts into batch files sized for a
reading pass (an analyst agent, or a human).

Exists because the actionable questions — what did the customer actually want, did we have it,
did we get the loan or the sale, where did the call go wrong — are not keyword questions. They
need the call read. Keyword classification stays useful for counting; this is for understanding.

USAGE
    python3 make_batches.py --since 2026-08-31 --until 2026-09-06 [--per-batch 40] [--customer-only]

Writes batches/<since>_<until>/batch_NN.txt, each a plain-text run of calls:

    ### CALL 12 | 2026-09-03 | HAR | inbound | 94s
    <transcript>

Every call carries its index so a finding can be traced back to the call it came from.
"""

import os
import sys
import glob
import json
import argparse
import datetime

BASE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline/out/transcripts")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Call Analysis/batches")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--per-batch", type=int, default=40)
    ap.add_argument("--customer-only", action="store_true", default=True)
    ap.add_argument("--min-duration", type=int, default=20,
                    help="skip calls shorter than this many seconds (hangups, wrong numbers)")
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until)

    recs = []
    for path in sorted(glob.glob(os.path.join(BASE, "*", "*.json"))):
        day = os.path.basename(os.path.dirname(path))
        try:
            d = datetime.date.fromisoformat(day)
        except ValueError:
            continue
        if not (since <= d <= until):
            continue
        r = json.load(open(path, encoding="utf-8"))
        if a.customer_only and r.get("kind") != "CUSTOMER":
            continue
        if r.get("duration_s", 0) < a.min_duration:
            continue
        if not (r.get("transcript") or "").strip():
            continue
        recs.append(r)

    recs.sort(key=lambda r: (r["date"], r.get("store", ""), r.get("call_id", "")))

    outdir = os.path.join(OUT, "%s_%s" % (a.since, a.until))
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "batch_*.txt")):
        os.remove(f)

    n_batches = 0
    for i in range(0, len(recs), a.per_batch):
        chunk = recs[i:i + a.per_batch]
        n_batches += 1
        lines = []
        for j, r in enumerate(chunk, start=i + 1):
            lines.append("### CALL %d | %s | %s | %s | %ss" % (
                j, r["date"], r.get("store", "UNK"), r.get("direction", "?"),
                r.get("duration_s", 0)))
            lines.append((r.get("transcript") or "").strip())
            lines.append("")
        with open(os.path.join(outdir, "batch_%02d.txt" % n_batches), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(lines))

    print("calls=%d batches=%d dir=%s" % (len(recs), n_batches, outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
