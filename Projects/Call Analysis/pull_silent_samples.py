#!/usr/bin/env python3
"""Save a few of the 'silent' recordings so a human can identify what the audio actually is.

The audio is not silent — it measures around -20 dB mean with peaks near 0 dB and almost no
detected silence, i.e. loud and continuous. Whisper transcribes none of it as speech. That
combination is what music or a repeating tone looks like. Rather than keep inferring, hand three
of them to someone who will recognise their own hold music instantly.
"""
import os, re, sys, json, glob, shutil, urllib.request

sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline"))
from zoom_ingest import token, api_get, BASE  # noqa: E402

TX = os.path.join(BASE, "out", "transcripts")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Call Analysis/audio")
AN = re.compile(r"this call may be recorded for quality assurance and training purposes\.?", re.I)

rows = []
for p in glob.glob(TX + "/*/*.json"):
    d = os.path.basename(os.path.dirname(p))
    if not ("2026-08-31" <= d <= "2026-09-06"):
        continue
    r = json.load(open(p, encoding="utf-8"))
    t = r.get("transcript") or ""
    if len(re.sub(r"[\[\(].*?[\]\)]", "", AN.sub("", t)).strip()) < 25:
        rows.append(r)

# one short, one medium, one long — in case they are different phenomena
rows.sort(key=lambda r: r["duration_s"])
picks = [rows[len(rows) // 8], rows[len(rows) // 2], rows[-1]]

os.makedirs(OUT, exist_ok=True)
for r in picks:
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
    name = "%s_%s_SILENT_SAMPLE_%ds.mp3" % (r["date"], r.get("store"), r["duration_s"])
    dest = os.path.join(OUT, name)
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + token())
    with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)
    print("saved", dest)
