#!/usr/bin/env python3
"""w2_probe.py — READ-ONLY probes for the Mac-first wave 2 builds (2026-10-14). Never writes or posts.
  w2_probe.py xlsx <path> [rows]          sheet names, header + last N rows of every sheet (openpyxl, read-only)
  w2_probe.py hist <channel> <days>       bot conversations.history: ts, user, text[:200], files (name/mimetype)
  w2_probe.py ls <dir> [n]                newest n entries of a directory with mtimes
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def xlsx(path, rows=15):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    for ws in wb.worksheets:
        allr = list(ws.iter_rows(values_only=True))
        print("=== SHEET %s rows=%d" % (ws.title, len(allr)))
        for r in allr[:1] + allr[-rows:]:
            print(" | ".join("" if v is None else str(v) for v in r))


def hist(ch, days):
    import vp_slack
    import time
    cutoff = time.time() - float(days) * 86400
    cur, n = None, 0
    while True:
        p = {"channel": ch, "limit": 200}
        if cur:
            p["cursor"] = cur
        r = vp_slack.call("conversations.history", params=p)
        if not r.get("ok"):
            print("ERROR", r.get("error"))
            return
        for m in r.get("messages", []):
            if float(m["ts"]) < cutoff:
                return
            n += 1
            when = dt.datetime.fromtimestamp(float(m["ts"])).strftime("%Y-%m-%d %H:%M")
            files = ["%s(%s)" % (f.get("name"), f.get("mimetype")) for f in (m.get("files") or [])]
            print("%s ts=%s user=%s sub=%s reply_count=%s text=%r files=%s" % (when, m["ts"], m.get("user") or m.get("bot_id"),
                  m.get("subtype"), m.get("reply_count"), (m.get("text") or "")[:200], files))
        cur = r.get("response_metadata", {}).get("next_cursor")
        if not cur:
            return


def ls(d, n=30):
    ents = sorted(((os.path.getmtime(os.path.join(d, e)), e) for e in os.listdir(d)), reverse=True)[:int(n)]
    for t, e in ents:
        print(dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M"), e)


def publer(since, until, n=2):
    import json
    sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Projects/Refine Social Media"))
    from vp_social import config, reader
    p = reader._client()
    for key, v in list(config.load_accounts().items())[:2]:
        if not v.get("publer_id") or key == "BrandBlog":
            continue
        items = p.post_insights(v["publer_id"], since=since, until=until, limit=100)
        print("=== %s items=%d" % (key, len(items)))
        for it in items[:int(n)]:
            print(json.dumps({k: (val if not isinstance(val, str) else val[:80]) for k, val in it.items()}, default=str)[:2500])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "publer":
        publer(a[1], a[2])
    if a[0] == "xlsx":
        xlsx(a[1], int(a[2]) if len(a) > 2 else 15)
    elif a[0] == "hist":
        hist(a[1], a[2])
    elif a[0] == "ls":
        ls(a[1], a[2] if len(a) > 2 else 30)
