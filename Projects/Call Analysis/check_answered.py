#!/usr/bin/env python3
"""
check_answered.py — settle the biggest open question in the call data: the ~40% of calls whose
recording contains nothing but the "this call may be recorded" announcement.

Two very different explanations, opposite responses:
  (a) recording/transcription defect  -> a data problem, fix the pipeline
  (b) nobody ever picked up           -> a business problem, and a large one

Zoom's recording metadata distinguishes them. `accepted_by` is populated only when a user
actually answered the call; an unanswered call has no `accepted_by` at all. So joining that
field against whether the transcript captured any speech answers it definitively.

USAGE
    python3 check_answered.py --since 2026-08-31 --until 2026-09-06
"""

import os
import re
import sys
import json
import glob
import argparse
import datetime

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))
from zoom_ingest import api_get, EXT_TO_STORE, BASE, daterange  # noqa: E402

TX = os.path.join(BASE, "out", "transcripts")

# Every recording opens with this. Strip it before asking whether anyone actually spoke.
ANNOUNCE = re.compile(
    r"this call may be recorded for quality assurance and training purposes\.?", re.I)


def has_speech(text):
    t = ANNOUNCE.sub("", text or "").strip()
    t = re.sub(r"[\[\(].*?[\]\)]", "", t).strip()   # [BLANK_AUDIO], (silence), etc.
    return len(t) > 25          # more than a stray word or two


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until)

    # transcript text by call id
    tx = {}
    for p in glob.glob(os.path.join(TX, "*", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        tx[d.get("call_id")] = d.get("transcript") or ""

    rows = []
    for day in daterange(since, until):
        page = None
        while True:
            params = {"from": day, "to": day, "page_size": 300}
            if page:
                params["next_page_token"] = page
            res = api_get("/phone/recordings", params)
            for rec in res.get("recordings", []):
                rid = rec.get("id")
                accepted = (rec.get("accepted_by") or {}).get("extension_number")
                owner = (rec.get("owner") or {}).get("extension_number")
                store = (EXT_TO_STORE.get(str(accepted or ""))
                         or EXT_TO_STORE.get(str(owner or "")) or "UNK")
                rows.append({
                    "id": rid, "day": day, "store": store,
                    "direction": (rec.get("direction") or "").lower(),
                    "duration_s": int(rec.get("duration") or 0),
                    "answered": bool(accepted),
                    "speech": has_speech(tx.get(rid, "")),
                    "have_tx": rid in tx,
                })
            page = res.get("next_page_token")
            if not page:
                break

    n = len(rows)
    inbound = [r for r in rows if r["direction"] == "inbound"]
    silent = [r for r in rows if r["have_tx"] and not r["speech"]]
    unanswered = [r for r in rows if not r["answered"]]

    print("calls in range: %d  (inbound %d / outbound %d)"
          % (n, len(inbound), n - len(inbound)))
    print("no speech captured: %d (%.0f%%)" % (len(silent), 100.0 * len(silent) / n))
    print("no accepted_by (never answered): %d (%.0f%%)"
          % (len(unanswered), 100.0 * len(unanswered) / n))
    print()

    # The crux: of the silent recordings, how many were never answered?
    s_unans = [r for r in silent if not r["answered"]]
    print("OF THE SILENT RECORDINGS:")
    print("  never answered : %d (%.0f%%)"
          % (len(s_unans), 100.0 * len(s_unans) / len(silent) if silent else 0))
    print("  answered but no speech captured: %d" % (len(silent) - len(s_unans)))
    print()

    print("UNANSWERED INBOUND BY STORE (the number that matters):")
    for st in ("HAR", "WAY", "LEX", "UNK"):
        ins = [r for r in inbound if r["store"] == st]
        if not ins:
            continue
        miss = [r for r in ins if not r["answered"]]
        print("  %s: %d of %d inbound went unanswered (%.0f%%)"
              % (st, len(miss), len(ins), 100.0 * len(miss) / len(ins)))

    print()
    print("UNANSWERED INBOUND BY DAY:")
    for day in daterange(since, until):
        ins = [r for r in inbound if r["day"] == day]
        if not ins:
            continue
        miss = [r for r in ins if not r["answered"]]
        print("  %s: %2d of %2d (%.0f%%)"
              % (day, len(miss), len(ins), 100.0 * len(miss) / len(ins)))

    long_miss = [r for r in unanswered if r["direction"] == "inbound" and r["duration_s"] >= 60]
    print()
    print("inbound calls that rang 60s+ and were never answered: %d" % len(long_miss))
    return 0


if __name__ == "__main__":
    sys.exit(main())
