#!/usr/bin/env python3
"""
diagnose_silence.py — work out WHY ~40% of recordings contain no conversation.

Competing explanations, all testable against the audio itself:
  (a) whisper failed on them          -> audio has real speech, transcript is empty. Data bug.
  (b) the file is genuinely near-silent -> recording captured dead air. Phone-system behaviour.
  (c) the audio is much shorter than the call -> recording stopped at answer (queue leg only).
  (d) the audio is greeting + hold      -> caller waited. Real business problem.

(c) vs (d) is the important fork: (c) means the "silence" is a recording artifact and the calls
were fine, (d) means customers really are sitting there.

USAGE
    python3 diagnose_silence.py --since 2026-08-31 --until 2026-09-06 --sample 8
"""

import os
import re
import sys
import json
import glob
import shutil
import argparse
import datetime
import subprocess
import urllib.request

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))
from zoom_ingest import token, api_get, BASE, daterange  # noqa: E402

TX = os.path.join(BASE, "out", "transcripts")
TMP = "/tmp/vp_silence_probe"
ANNOUNCE = re.compile(
    r"this call may be recorded for quality assurance and training purposes\.?", re.I)


def speech_len(text):
    t = ANNOUNCE.sub("", text or "")
    t = re.sub(r"[\[\(].*?[\]\)]", "", t)
    return len(t.strip())


def probe(path):
    """Return (audio_seconds, mean_dB, max_dB, silent_seconds)."""
    out = subprocess.run(
        ["/opt/homebrew/bin/ffmpeg", "-i", path, "-af",
         "volumedetect,silencedetect=noise=-45dB:d=2", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    mean = re.search(r"mean_volume: ([\-\d.]+) dB", out)
    peak = re.search(r"max_volume: ([\-\d.]+) dB", out)
    silence = sum(float(x) for x in re.findall(r"silence_duration: ([\d.]+)", out))
    return dur, (mean.group(1) if mean else "?"), (peak.group(1) if peak else "?"), silence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--sample", type=int, default=8)
    a = ap.parse_args()

    since = datetime.date.fromisoformat(a.since)
    until = datetime.date.fromisoformat(a.until)

    silent, spoken = [], []
    for p in glob.glob(os.path.join(TX, "*", "*.json")):
        day = os.path.basename(os.path.dirname(p))
        try:
            d = datetime.date.fromisoformat(day)
        except ValueError:
            continue
        if not (since <= d <= until):
            continue
        r = json.load(open(p, encoding="utf-8"))
        (silent if speech_len(r.get("transcript")) < 25 else spoken).append(r)

    print("silent: %d   with speech: %d" % (len(silent), len(spoken)))
    silent.sort(key=lambda r: -r.get("duration_s", 0))

    os.makedirs(TMP, exist_ok=True)
    print("\nProbing the %d LONGEST silent recordings (worst case for 'it was just a hangup'):\n"
          % a.sample)
    print("%-11s %-4s %-9s %8s %8s %9s %9s %9s" % (
        "date", "st", "dir", "zoom_s", "audio_s", "mean_dB", "peak_dB", "silence_s"))

    for r in silent[:a.sample]:
        url = None
        page = None
        while True:
            params = {"from": r["date"], "to": r["date"], "page_size": 300}
            if page:
                params["next_page_token"] = page
            res = api_get("/phone/recordings", params)
            for rec in res.get("recordings", []):
                if rec.get("id") == r["call_id"]:
                    url = rec.get("download_url")
            page = res.get("next_page_token")
            if not page or url:
                break
        if not url:
            continue
        dest = os.path.join(TMP, r["call_id"] + ".mp3")
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + token())
        with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
        dur, mean, peak, sil = probe(dest)
        print("%-11s %-4s %-9s %8d %8.1f %9s %9s %9.1f" % (
            r["date"], r.get("store"), r.get("direction"),
            r.get("duration_s", 0), dur, mean, peak, sil))
        os.remove(dest)

    # Control group: same probe on calls that DID transcribe, for comparison.
    print("\nControl — same probe on recordings that DID contain speech:\n")
    print("%-11s %-4s %-9s %8s %8s %9s %9s %9s" % (
        "date", "st", "dir", "zoom_s", "audio_s", "mean_dB", "peak_dB", "silence_s"))
    spoken.sort(key=lambda r: -r.get("duration_s", 0))
    for r in spoken[:3]:
        url = None
        page = None
        while True:
            params = {"from": r["date"], "to": r["date"], "page_size": 300}
            if page:
                params["next_page_token"] = page
            res = api_get("/phone/recordings", params)
            for rec in res.get("recordings", []):
                if rec.get("id") == r["call_id"]:
                    url = rec.get("download_url")
            page = res.get("next_page_token")
            if not page or url:
                break
        if not url:
            continue
        dest = os.path.join(TMP, r["call_id"] + ".mp3")
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + token())
        with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as f:
            shutil.copyfileobj(resp, f)
        dur, mean, peak, sil = probe(dest)
        print("%-11s %-4s %-9s %8d %8.1f %9s %9s %9.1f" % (
            r["date"], r.get("store"), r.get("direction"),
            r.get("duration_s", 0), dur, mean, peak, sil))
        os.remove(dest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
