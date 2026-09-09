#!/usr/bin/env python3
"""
pull_flagged.py — bulk-pull audio for the calls a weekly reading pass flagged, and convert each
to AAC (.m4a) so it opens in QuickTime Player.

WHY THIS EXISTS (additive to pull_calls.py, which is unchanged)
    pull_calls.py re-lists an entire day's Zoom recordings once per requested call. That is fine
    for three calls and wasteful for a hundred. The weekly pipeline flags ~100 calls a week, so
    this caches the per-day recording listing and does one lookup per DAY instead of one per CALL.
    It reuses pull_calls.ordered_calls() so CALL numbers map identically — there is exactly one
    numbering authority and it stays in pull_calls.py.

    Music's importer has repeatedly failed on Zoom's native mp3s, so every file is transcoded to
    AAC (-ar 44100 -ac 1 -c:a aac -b:a 96k). Both files are kept; the .m4a is the one to play.

USAGE
    python3 pull_flagged.py --since 2026-08-31 --until 2026-09-06 \
        --out ~/Documents/Claude/Projects/Call\\ Analysis/audio/2026-08-31_2026-09-06 \
        --map flagged_2026-08-31.json

    --map is {"<call number>": "<label>"} — label carries store, subject and severity.
Resumable: a call whose .m4a already exists is skipped.
"""

import os
import re
import sys
import json
import shutil
import argparse
import datetime
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))

from pull_calls import ordered_calls, safe  # noqa: E402 — single numbering authority
from zoom_ingest import token, api_get  # noqa: E402


def day_index(day):
    """All recordings for one day, keyed by call id. One listing per day, not per call."""
    out, page = {}, None
    while True:
        params = {"from": day, "to": day, "page_size": 300}
        if page:
            params["next_page_token"] = page
        res = api_get("/phone/recordings", params)
        for rec in res.get("recordings", []):
            out[rec.get("id")] = rec
        page = res.get("next_page_token")
        if not page:
            return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until)
    labels = json.load(open(os.path.join(HERE, a.map), encoding="utf-8"))
    out = os.path.expanduser(a.out)
    os.makedirs(out, exist_ok=True)

    idx = ordered_calls(since, until)
    wanted = sorted(int(k) for k in labels)

    by_day = {}
    for n in wanted:
        r = idx.get(n)
        if not r:
            print("CALL %d: not in range" % n)
            continue
        by_day.setdefault(r["date"], []).append((n, r))

    ok = fail = skip = 0
    for day in sorted(by_day):
        recs = day_index(day)
        for n, r in by_day[day]:
            label = labels[str(n)]
            stem = "%s_%s_call%03d_%s" % (r["date"], r.get("store", "UNK"), n, safe(label))
            mp3 = os.path.join(out, stem + ".mp3")
            m4a = os.path.join(out, stem + ".m4a")
            if os.path.exists(m4a):
                skip += 1
                continue
            rec = recs.get(r["call_id"])
            url = rec.get("download_url") if rec else None
            if not url:
                print("CALL %d: no download url" % n)
                fail += 1
                continue
            try:
                req = urllib.request.Request(url)
                req.add_header("Authorization", "Bearer " + token())
                with urllib.request.urlopen(req, timeout=180) as resp, open(mp3, "wb") as f:
                    shutil.copyfileobj(resp, f)
                subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error", "-i", mp3,
                     "-ar", "44100", "-ac", "1", "-c:a", "aac", "-b:a", "96k", m4a],
                    check=True)
                ok += 1
            except Exception as e:
                print("CALL %d: FAILED %s" % (n, e))
                fail += 1
    print("pulled=%d skipped=%d failed=%d out=%s" % (ok, skip, fail, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
