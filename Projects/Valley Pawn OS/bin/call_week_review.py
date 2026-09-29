#!/usr/bin/env python3
"""
call_week_review.py — one-shot pull for a weekly phone review (added 2026-09-28, additive).

Joshua 2026-09-28: "listen to all the calls last week and give me a summary — how many, how many
missed, texts, what we turned down, what the calls were about, customer-service issues, weird
conversations." This script gathers the raw material on the HOST (where the Zoom creds and local
whisper live). It changes nothing in Zoom (read-only S2S scopes) and posts nothing anywhere.

WHAT IT WRITES (all under Projects/Call Analysis/week_<since>/):
    call_history.json     every call-history row for the range (caller/callee CNAM names stripped)
    recordings_index.json one row per recording: id, start time, direction, store, other party, duration
    status.json           phase + counts, updated as it goes; "phase":"done" when finished
    run.log               progress / warnings
Transcripts go through the EXISTING harvester (Zoom Call Pipeline/harvest_transcripts.py) so they
land in the standard out/transcripts/<day>/<id>.json layout. Local whisper only — the harvester
stops rather than fall back to any cloud API.

USAGE (host queue):  python3 ".../bin/call_week_review.py" --since 2026-09-21 --until 2026-09-27 --detach
--detach relaunches itself in a new session and returns at once, so a long transcription run never
holds the host-queue lock.
"""
import os
import sys
import json
import time
import argparse
import datetime
import subprocess

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))
# launchd/host-queue runs with a bare PATH, so shutil.which() cannot see Homebrew's whisper-cli or
# ffmpeg (first run 2026-09-28 failed "whisper unavailable" for exactly this reason).
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "/usr/bin:/bin")

PIPE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline")
OUTROOT = os.path.expanduser("~/Documents/Claude/Projects/Call Analysis")
STRIP = ("caller_name", "callee_name")  # carrier CNAM — never stored (PIPELINE_ARCHITECTURE.md)


def outdir(since):
    d = os.path.join(OUTROOT, "week_" + since)
    os.makedirs(d, exist_ok=True)
    return d


def log(d, msg):
    with open(os.path.join(d, "run.log"), "a") as f:
        f.write("%s %s\n" % (datetime.datetime.now().strftime("%F %T"), msg))


def status(d, **kw):
    p = os.path.join(d, "status.json")
    cur = {}
    if os.path.exists(p):
        try:
            cur = json.load(open(p))
        except Exception:
            cur = {}
    cur.update(kw)
    cur["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    tmp = p + ".tmp"
    json.dump(cur, open(tmp, "w"), indent=2)
    os.replace(tmp, p)


def scrub(row):
    if isinstance(row, dict):
        return {k: scrub(v) for k, v in row.items() if k not in STRIP}
    if isinstance(row, list):
        return [scrub(x) for x in row]
    return row


def paged(api_get, path, key, since, until):
    rows, npt = [], None
    for _ in range(50):
        p = {"from": since, "to": until, "page_size": 300}
        if npt:
            p["next_page_token"] = npt
        res = api_get(path, p)
        rows.extend(res.get(key) or [])
        npt = res.get("next_page_token")
        if not npt:
            break
    return rows


def work(since, until):
    d = outdir(since)
    status(d, phase="starting", since=since, until=until)
    log(d, "start %s..%s" % (since, until))
    from zoom_ingest import api_get, EXT_TO_STORE  # noqa: E402

    # 1. call history (every call, answered or not)
    try:
        ch = paged(api_get, "/phone/call_history", "call_logs", since, until)
        json.dump(scrub(ch), open(os.path.join(d, "call_history.json"), "w"), indent=1)
        status(d, phase="call_history_done", call_history_rows=len(ch))
        log(d, "call_history rows=%d" % len(ch))
    except Exception as e:
        status(d, call_history_error=str(e)[:300])
        log(d, "call_history FAILED: %s" % e)

    # 2. recordings index (metadata only)
    try:
        recs = paged(api_get, "/phone/recordings", "recordings", since, until)
        idx = []
        for r in recs:
            acc = str((r.get("accepted_by") or {}).get("extension_number", ""))
            own = str((r.get("owner") or {}).get("extension_number", ""))
            direction = (r.get("direction") or "").lower()
            idx.append({
                "id": r.get("id"),
                "call_log_id": r.get("call_log_id"),
                "call_history_id": r.get("call_history_id"),
                "call_id": r.get("call_id"),
                "date_time": r.get("date_time"),
                "direction": direction,
                "duration_s": int(r.get("duration") or 0),
                "store": EXT_TO_STORE.get(acc) or EXT_TO_STORE.get(own) or "UNK",
                "accepted_ext": acc, "owner_ext": own,
                "other_number": r.get("callee_number") if direction == "outbound" else r.get("caller_number"),
            })
        json.dump(idx, open(os.path.join(d, "recordings_index.json"), "w"), indent=1)
        status(d, phase="recordings_index_done", recordings=len(idx))
        log(d, "recordings=%d" % len(idx))
    except Exception as e:
        status(d, recordings_error=str(e)[:300])
        log(d, "recordings index FAILED: %s" % e)

    # 3. transcripts via the existing harvester (resumable; skips anything already on disk)
    status(d, phase="transcribing")
    log(d, "harvest start")
    with open(os.path.join(d, "harvest.log"), "a") as hl:
        rc = subprocess.call([sys.executable, os.path.join(PIPE, "harvest_transcripts.py"),
                              "--since", since, "--until", until], stdout=hl, stderr=hl, cwd=PIPE)
    log(d, "harvest rc=%s" % rc)
    status(d, phase="done" if rc == 0 else "harvest_failed", harvest_rc=rc,
           finished=datetime.datetime.now().isoformat(timespec="seconds"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--detach", action="store_true")
    a = ap.parse_args()
    datetime.date.fromisoformat(a.since)
    datetime.date.fromisoformat(a.until)
    if a.detach:
        d = outdir(a.since)
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--since", a.since, "--until", a.until],
                         start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=open(os.path.join(d, "detached.out"), "a"), stderr=subprocess.STDOUT)
        print("detached; progress in", os.path.join(d, "status.json"))
        return 0
    work(a.since, a.until)
    return 0


if __name__ == "__main__":
    sys.exit(main())
