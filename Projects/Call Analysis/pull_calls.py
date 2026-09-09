#!/usr/bin/env python3
"""
pull_calls.py — download specific call recordings by their batch CALL number, named so you can
tell what you're listening to before you press play.

The batch files number calls 1..N in a fixed order (make_batches.py sorts by date, then store,
then call_id). This reproduces that ordering to map a CALL number back to its Zoom recording,
then downloads the audio.

USAGE
    python3 pull_calls.py --since 2026-08-31 --until 2026-09-06 --calls 63,93,223 --out ~/Desktop
    python3 pull_calls.py --since ... --until ... --calls 63 --label "HAR drug talk"   # one file
    python3 pull_calls.py --since ... --until ... --calls 63 --info                    # no download

Labels can also come from a labels.json next to this script: {"63": "HAR drug talk", ...}
"""

import os
import re
import sys
import json
import glob
import shutil
import argparse
import datetime
import urllib.request

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))
from zoom_ingest import token, api_get, BASE, daterange  # noqa: E402

TX = os.path.join(BASE, "out", "transcripts")


def ordered_calls(since, until, min_duration=20):
    """Reproduce make_batches.py's ordering exactly, so CALL numbers line up."""
    recs = []
    for path in glob.glob(os.path.join(TX, "*", "*.json")):
        day = os.path.basename(os.path.dirname(path))
        try:
            d = datetime.date.fromisoformat(day)
        except ValueError:
            continue
        if not (since <= d <= until):
            continue
        r = json.load(open(path, encoding="utf-8"))
        if r.get("kind") != "CUSTOMER":
            continue
        if r.get("duration_s", 0) < min_duration:
            continue
        if not (r.get("transcript") or "").strip():
            continue
        recs.append(r)
    recs.sort(key=lambda r: (r["date"], r.get("store", ""), r.get("call_id", "")))
    return {i: r for i, r in enumerate(recs, start=1)}


def find_download_url(day, call_id):
    page = None
    while True:
        params = {"from": day, "to": day, "page_size": 300}
        if page:
            params["next_page_token"] = page
        res = api_get("/phone/recordings", params)
        for rec in res.get("recordings", []):
            if rec.get("id") == call_id:
                return rec.get("download_url"), rec.get("date_time")
        page = res.get("next_page_token")
        if not page:
            return None, None


def safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--calls", required=True, help="comma-separated CALL numbers")
    ap.add_argument("--out", default="~/Documents/Claude/Projects/Call Analysis/audio")
    ap.add_argument("--label")
    ap.add_argument("--info", action="store_true", help="print metadata, download nothing")
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until)
    wanted = [int(x) for x in a.calls.split(",") if x.strip()]

    labels = {}
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "labels.json")
    if os.path.exists(lp):
        labels = json.load(open(lp, encoding="utf-8"))
    if a.label and len(wanted) == 1:
        labels[str(wanted[0])] = a.label

    idx = ordered_calls(since, until)
    out = os.path.expanduser(a.out)
    if not a.info:
        os.makedirs(out, exist_ok=True)

    for n in wanted:
        r = idx.get(n)
        if not r:
            print("CALL %d: not found in range" % n)
            continue
        url, when = find_download_url(r["date"], r["call_id"])
        label = labels.get(str(n), "")
        print("CALL %-4d %s  %s  %-8s %4ss  %s" % (
            n, r["date"], r.get("store"), r.get("direction"), r.get("duration_s"), label))
        print("         zoom time: %s   call id: %s" % (when or "?", r["call_id"]))
        if a.info:
            continue
        if not url:
            print("         NO DOWNLOAD URL")
            continue
        fname = "%s_%s_call%03d%s.mp3" % (
            r["date"], r.get("store", "UNK"), n, "_" + safe(label) if label else "")
        dest = os.path.join(out, fname)
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + token())
        try:
            with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)
            print("         saved: %s" % dest)
        except Exception as e:
            print("         FAILED: %s" % e)

    return 0


if __name__ == "__main__":
    sys.exit(main())
