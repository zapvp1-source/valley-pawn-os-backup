#!/usr/bin/env python3
"""eod_photo_fetch.py [YYYY-MM-DD] [--render] — download the day's #end-of-day image uploads to disk so
the jewelry-count task can read the managers' PM count sheets with its own Read tool.

WHY (2026-09-29): the 9/28 jewelry run found all five managers' count-sheet photos in #end-of-day but
could not open them — its Slack connector returns file metadata only, no image bytes. The ops bot's
token can download files directly. This writes:
  fleet/eod_photos/<date>/<HHMM>_<poster-name>_<n>.<ext>
  fleet/eod_photos/<date>/index.json   [{file, poster, poster_id, ts, text}]
Read-only against Slack. Overwrites nothing that already exists. Keeps 14 days; older days pruned.
"""
import datetime as dt
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

CH = "C03C7HV8L48"  # #end-of-day
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
ROOT = os.path.join(OS_DIR, "fleet", "eod_photos")


def api(tok, method, **params):
    req = urllib.request.Request("https://slack.com/api/%s?%s" % (method, urllib.parse.urlencode(params)),
                                 headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    day = dt.date.fromisoformat(args[0]) if args else dt.datetime.now(ET).date()
    start = dt.datetime.combine(day, dt.time(0, 0), ET)
    end = start + dt.timedelta(days=1)
    tok = vp_slack.token()
    r = api(tok, "conversations.history", channel=CH, oldest=str(start.timestamp()),
            latest=str(end.timestamp()), limit="200")
    if not r.get("ok"):
        print("history failed:", r.get("error")); return 1
    names = {}
    out_dir = os.path.join(ROOT, day.isoformat())
    index, n = [], 0
    for m in sorted(r.get("messages", []), key=lambda m: float(m.get("ts", 0))):
        files = [f for f in (m.get("files") or []) if str(f.get("mimetype", "")).startswith("image/")]
        if not files:
            continue
        uid = m.get("user", "?")
        if uid not in names:
            u = api(tok, "users.info", user=uid)
            prof = (u.get("user") or {}).get("profile", {}) if u.get("ok") else {}
            names[uid] = re.sub(r"[^A-Za-z0-9]+", "-", prof.get("real_name") or prof.get("display_name") or uid).strip("-")
        t = dt.datetime.fromtimestamp(float(m["ts"]), ET)
        for i, f in enumerate(files, 1):
            ext = (f.get("filetype") or "jpg").lower()
            fn = "%s_%s_%d.%s" % (t.strftime("%H%M"), names[uid], i, ext)
            index.append({"file": fn, "poster": names[uid], "poster_id": uid, "ts": t.isoformat(timespec="seconds"),
                          "text": (m.get("text") or "")[:300]})
            n += 1
            if render:
                continue
            os.makedirs(out_dir, exist_ok=True)
            dst = os.path.join(out_dir, fn)
            if os.path.exists(dst):
                continue
            url = f.get("url_private_download") or f.get("url_private")
            req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if data[:15].lower().startswith(b"<!doctype html") or data[:5] == b"<html":
                print("download returned a login page for %s — the bot token lacks files:read" % fn)
                return 2
            with open(dst, "wb") as fh:
                fh.write(data)
    if not render and index:
        json.dump(index, open(os.path.join(out_dir, "index.json"), "w"), indent=1)
        # prune days older than 14
        cut = (day - dt.timedelta(days=14)).isoformat()
        for d in os.listdir(ROOT):
            if re.match(r"\d{4}-\d{2}-\d{2}$", d) and d < cut:
                shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    print("%s: %d image(s) from %d poster(s)%s" % (day, n, len(names), " (render only)" if render else " -> " + out_dir))
    for e in index:
        print("  %s  %s" % (e["file"], e["text"][:60].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
