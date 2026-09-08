#!/usr/bin/env python3
"""
reclassify_customer.py — re-run the CUSTOMER classifier over already-ingested calls with the
2026-09-07 expanded CATEGORIES/INTENTS/QUALIFIERS (see zoom_ingest.py), without changing the
EMPLOYEE/CUSTOMER split itself.

WHY THIS EXISTS
    The first real weekly read showed 68% of real calls landing in category "other" and 64% in
    intent "other". Checked against duration/direction (not content — no transcript survives) that
    was NOT a spam/junk artifact: those calls average 78s and are 90% inbound, i.e. real
    conversations the original keyword lists were too narrow to tag. The fix is a wider keyword
    set (already applied to zoom_ingest.py) — this script re-applies it to calls already pulled.

WHY RE-DOWNLOAD AND RE-TRANSCRIBE RATHER THAN JUST RE-RUNNING THE OLD TEXT
    The whole point of the ephemeral-transcript design is that transcript text is never persisted
    anywhere once a call's structured record is written — there is nothing on disk to re-classify.
    Zoom's own recording retention is indefinite, so the audio still exists there; re-pulling it
    and re-transcribing is the only way to improve a past week's read, and it follows the exact
    same discard-after-this-run rule as the normal ingest path. Nothing new is retained.

SCOPE
    Only CUSTOMER calls are touched. The single EMPLOYEE call already has its transcript saved
    (that pipeline doesn't use CATEGORIES/INTENTS at all) and is left alone. Re-classification does
    NOT re-run the EMPLOYEE/CUSTOMER split — the roster hasn't changed since the backfill, so a
    call classified CUSTOMER before is still CUSTOMER now. If the roster ever changes, re-run the
    normal backfill instead, not this script.

USAGE
    python3 reclassify_customer.py --since 2026-08-21 --until 2026-09-07 [--limit N] [--dry-run]

    For each day in range: pull recordings from Zoom (same query the normal ingest uses), skip
    anything the roster resolves to EMPLOYEE, re-download + re-transcribe CUSTOMER calls, and
    replace that day's out/customer/<date>.jsonl with the freshly classified records — written to
    a temp file and atomically renamed only once the whole day is done, so a killed run never
    leaves a half-written day file in place of a good one.
"""

import os
import sys
import json
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_ingest import (  # noqa: E402 — must follow sys.path insert
    token, api_get, classify, load_roster, transcribe, reduce_customer,
    EXT_TO_STORE, TMP, OUT_CUS, daterange,
)

import glob
import shutil
import urllib.request


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until) if a.until else datetime.date.today()

    os.makedirs(OUT_CUS, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for stale in glob.glob(os.path.join(TMP, "*")):
        try:
            os.remove(stale)
        except OSError:
            pass

    roster = load_roster()
    n_done = n_emp_skip = n_fail = 0

    for day in daterange(since, until):
        day_records = []
        day_cut_short = False
        page = None
        while True:
            params = {"from": day, "to": day, "page_size": 300}
            if page:
                params["next_page_token"] = page
            try:
                res = api_get("/phone/recordings", params)
            except Exception as e:
                sys.stderr.write("WARN: recordings pull failed for %s: %s\n" % (day, e))
                break

            for rec in res.get("recordings", []):
                if a.limit and n_done >= a.limit:
                    day_cut_short = True
                    break
                accepted_ext = str((rec.get("accepted_by") or {}).get("extension_number", ""))
                owner_ext = str((rec.get("owner") or {}).get("extension_number", ""))
                store = (EXT_TO_STORE.get(accepted_ext)
                         or EXT_TO_STORE.get(owner_ext) or "UNK")
                direction = (rec.get("direction") or "").lower()
                other = rec.get("callee_number") if direction == "outbound" else rec.get("caller_number")

                kind, _ = classify(other, roster)
                if kind == "EMPLOYEE":
                    n_emp_skip += 1
                    continue

                meta = {"date": day, "store": store, "direction": direction or "unknown",
                        "duration_s": int(rec.get("duration") or 0)}

                if a.dry_run:
                    day_records.append(reduce_customer("", meta))
                    n_done += 1
                    continue

                url = rec.get("download_url")
                if not url:
                    continue
                rid = rec.get("id") or "unknown"
                audio = os.path.join(TMP, rid + ".mp3")
                try:
                    req = urllib.request.Request(url)
                    req.add_header("Authorization", "Bearer " + token())
                    with urllib.request.urlopen(req, timeout=180) as r, open(audio, "wb") as f:
                        shutil.copyfileobj(r, f)
                    text = transcribe(audio)
                except RuntimeError:
                    raise  # local-whisper failure is fatal, same rule as normal ingest
                except Exception as e:
                    sys.stderr.write("WARN: %s failed (%s)\n" % (rid, e))
                    n_fail += 1
                    continue
                finally:
                    if os.path.exists(audio):
                        os.remove(audio)

                day_records.append(reduce_customer(text, meta))
                del text
                n_done += 1

            page = res.get("next_page_token")
            if not page or (a.limit and n_done >= a.limit):
                break
        if day_cut_short:
            # --limit cut this day off partway through. Writing what we collected so far
            # would PERMANENTLY replace the day's real (larger) record set with a partial
            # one — there is no transcript left to regenerate the rest from later. Skip the
            # write entirely; the existing file (old or not-yet-reclassified) stays in place,
            # and a later invocation covering this day with no --limit will redo it cleanly.
            sys.stderr.write("%s: cut short by --limit, NOT writing (re-run this day whole)\n" % day)
        elif not a.dry_run and day_records:
            out_path = os.path.join(OUT_CUS, day + ".jsonl")
            tmp_path = out_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                for rec_out in day_records:
                    f.write(json.dumps(rec_out) + "\n")
            os.replace(tmp_path, out_path)
            print("%s: wrote %d records" % (day, len(day_records)))

        if a.limit and n_done >= a.limit:
            break

    print("reclassified=%d employee_skipped=%d failed=%d" % (n_done, n_emp_skip, n_fail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
