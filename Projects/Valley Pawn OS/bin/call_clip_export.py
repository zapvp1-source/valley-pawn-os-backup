#!/usr/bin/env python3
"""call_clip_export.py — download specific Zoom Phone call recordings as MP3 for a training playlist.

Added 2026-10-24 (additive) for the November staff meeting: Joshua asked for 10 great-service and 10 bad
calls "in a format where I can just play them". The transcripts pipeline never keeps audio (Zoom is the
system of record), so this pulls ONLY the recordings named in a manifest. Read-only Zoom S2S
(/phone/recordings list + download_url). Changes nothing in Zoom, posts nothing anywhere.

USAGE (host queue):
    python3 ".../bin/call_clip_export.py" --manifest "<path>/clips_manifest.json"
Manifest: {"out_dir": "<abs dir>", "clips": [{"zoom_id": "...", "date": "YYYY-MM-DD", "file": "Good 01 - ....mp3"}]}
Writes each MP3 into out_dir and <out_dir>/export_status.json ({file: ok|missing|error}). Resumable: a clip
already on disk with size > 0 is skipped.
"""
import os, sys, json, shutil, argparse, datetime, urllib.request
PIPE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline")
sys.path.insert(0, PIPE)
from zoom_ingest import api_get, token  # noqa: E402


def recs_for(day):
    d = datetime.date.fromisoformat(day)
    out = {}
    for off in (-1, 0, 1):
        q = (d + datetime.timedelta(days=off)).isoformat()
        npt = None
        for _ in range(20):
            p = {"from": q, "to": q, "page_size": 300}
            if npt:
                p["next_page_token"] = npt
            res = api_get("/phone/recordings", p)
            for r in res.get("recordings") or []:
                if r.get("id"):
                    out[r["id"]] = r
            npt = res.get("next_page_token")
            if not npt:
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args()
    m = json.load(open(a.manifest))
    out_dir = m["out_dir"]
    os.makedirs(out_dir, exist_ok=True)
    status, cache = {}, {}
    for c in m["clips"]:
        dest = os.path.join(out_dir, c["file"])
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            status[c["file"]] = "ok"; continue
        try:
            if c["date"] not in cache:
                cache[c["date"]] = recs_for(c["date"])
            r = cache[c["date"]].get(c["zoom_id"])
            if not r or not r.get("download_url"):
                status[c["file"]] = "missing"; print("MISSING", c["zoom_id"]); continue
            req = urllib.request.Request(r["download_url"])
            req.add_header("Authorization", "Bearer " + token())
            tmp = dest + ".part"
            with urllib.request.urlopen(req, timeout=300) as resp, open(tmp, "wb") as f:
                shutil.copyfileobj(resp, f)
            os.replace(tmp, dest)
            status[c["file"]] = "ok"; print("OK", c["file"], os.path.getsize(dest))
        except Exception as e:
            status[c["file"]] = "error: %s" % str(e)[:200]; print("ERROR", c["file"], e)
    json.dump(status, open(os.path.join(out_dir, "export_status.json"), "w"), indent=1)
    bad = [k for k, v in status.items() if v != "ok"]
    print("done ok=%d bad=%d" % (len(status) - len(bad), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
