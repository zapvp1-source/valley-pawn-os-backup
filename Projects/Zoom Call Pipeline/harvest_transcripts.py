#!/usr/bin/env python3
"""
harvest_transcripts.py — pull every Zoom Phone call recording in a date range, transcribe it
locally, and SAVE the transcript to disk.

WHY THIS REPLACED THE EPHEMERAL-TRANSCRIPT DESIGN (2026-09-07, Joshua's call)
    The original pipeline destroyed each customer transcript the moment it produced a structured
    record. That was a deliberate privacy stance, and it had a hard cost: every time the classifier
    improved, the ONLY way to re-apply it to past calls was to re-download and re-transcribe all
    ~800 recordings — roughly an hour of compute to answer one question. Joshua lifted the
    constraint ("we are covered"), so transcripts now persist. Classification becomes a free local
    re-run over saved text, and the calls can actually be READ for what customers said rather than
    guessed at with keyword lists.

    The audio still is never kept — it lives in Zoom, which is the system of record for it.

RESUMABLE BY CONSTRUCTION
    One JSON file per call, written the moment that call is transcribed. A killed run loses at most
    the call in flight; a re-run skips everything already on disk. Progress is directly observable
    by counting files, which the ephemeral design could not do.

LAYOUT
    out/transcripts/<YYYY-MM-DD>/<call_id>.json
        {call_id, date, store, direction, duration_s, kind, participant, transcript}

    `kind` is EMPLOYEE or CUSTOMER per internal_roster.json, preserved so the two consumers can
    still filter. Nothing about that split changes here.

USAGE
    python3 harvest_transcripts.py --since 2026-08-21 [--until 2026-09-07] [--limit N]
    python3 harvest_transcripts.py --since 2026-08-21 --status    # count what's done, pull nothing
"""

import os
import sys
import glob
import json
import shutil
import argparse
import datetime
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_ingest import (  # noqa: E402 — must follow sys.path insert
    token, api_get, classify, load_roster, transcribe,
    EXT_TO_STORE, TMP, BASE, daterange,
)

OUT_TX = os.path.join(BASE, "out", "transcripts")


def tx_path(day, rid):
    return os.path.join(OUT_TX, day, rid + ".json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until) if a.until else datetime.date.today()

    if a.status:
        n = len(glob.glob(os.path.join(OUT_TX, "*", "*.json")))
        print("transcripts on disk: %d" % n)
        return 0

    os.makedirs(OUT_TX, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for stale in glob.glob(os.path.join(TMP, "*")):
        try:
            os.remove(stale)
        except OSError:
            pass

    roster = load_roster()
    n_new = n_skip = n_fail = 0

    for day in daterange(since, until):
        os.makedirs(os.path.join(OUT_TX, day), exist_ok=True)
        page = None
        while True:
            params = {"from": day, "to": day, "page_size": 300}
            if page:
                params["next_page_token"] = page
            try:
                res = api_get("/phone/recordings", params)
            except Exception as e:
                sys.stderr.write("WARN: pull failed for %s: %s\n" % (day, e))
                break

            for rec in res.get("recordings", []):
                if a.limit and n_new >= a.limit:
                    break
                rid = rec.get("id")
                if not rid:
                    continue
                dest = tx_path(day, rid)
                if os.path.exists(dest):
                    n_skip += 1
                    continue

                accepted_ext = str((rec.get("accepted_by") or {}).get("extension_number", ""))
                owner_ext = str((rec.get("owner") or {}).get("extension_number", ""))
                store = (EXT_TO_STORE.get(accepted_ext)
                         or EXT_TO_STORE.get(owner_ext) or "UNK")
                direction = (rec.get("direction") or "").lower()
                other = rec.get("callee_number") if direction == "outbound" else rec.get("caller_number")
                kind, who = classify(other, roster)

                url = rec.get("download_url")
                if not url:
                    continue
                audio = os.path.join(TMP, rid + ".mp3")
                try:
                    req = urllib.request.Request(url)
                    req.add_header("Authorization", "Bearer " + token())
                    with urllib.request.urlopen(req, timeout=180) as r, open(audio, "wb") as f:
                        shutil.copyfileobj(r, f)
                    text = transcribe(audio)
                except RuntimeError:
                    raise  # local whisper unavailable — stop, never degrade to a cloud API
                except Exception as e:
                    sys.stderr.write("WARN: %s failed (%s)\n" % (rid, e))
                    n_fail += 1
                    continue
                finally:
                    if os.path.exists(audio):
                        os.remove(audio)   # audio is never kept; Zoom is its system of record

                # Write immediately — this is the checkpoint. See RESUMABLE above.
                tmp_dest = dest + ".tmp"
                with open(tmp_dest, "w", encoding="utf-8") as f:
                    json.dump({"call_id": rid, "date": day, "store": store,
                               "direction": direction or "unknown",
                               "duration_s": int(rec.get("duration") or 0),
                               "kind": kind, "participant": who,
                               "transcript": text}, f, indent=2)
                os.replace(tmp_dest, dest)
                n_new += 1

            page = res.get("next_page_token")
            if not page or (a.limit and n_new >= a.limit):
                break
        if a.limit and n_new >= a.limit:
            break

    print("harvested=%d already_had=%d failed=%d" % (n_new, n_skip, n_fail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
