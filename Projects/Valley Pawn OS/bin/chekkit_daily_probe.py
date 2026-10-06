#!/usr/bin/env python3
"""chekkit_daily_probe.py FROM TO — READ-ONLY (GET /v1/leaderboard only): per store, reviews.total per single day
(from=to=day) across the range, plus the API's timezone field. Counts only, no customer data."""
import datetime as dt, json, subprocess, sys, time, urllib.request
a, b = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])
for code in ("CUL", "WAY", "HAR", "LEX", "ROA"):
    tok = subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"], capture_output=True, text=True).stdout.strip()
    out, tz, d = [], None, a
    while d <= b:
        req = urllib.request.Request("https://api.chekkit.io/v1/leaderboard?from=%s&to=%s" % (d, d),
              headers={"Authorization": "Bearer " + tok, "User-Agent": "ValleyPawnOps/1.0"})
        j = json.load(urllib.request.urlopen(req, timeout=30)); tz = j.get("timezone")
        out.append("%s:%s" % (d.strftime("%a%d"), j["location"]["reviews"]["total"])); d += dt.timedelta(days=1); time.sleep(0.3)
    print(code, "tz=%s" % tz, " ".join(out))
