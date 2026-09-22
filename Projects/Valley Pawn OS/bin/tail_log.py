#!/usr/bin/env python3
"""tail_log.py — show the real failure point of the unified-search rebuild.

The FDA theory is disproven (Mail AND Messages readable) and discovery is fine (349,588 .emlx found).
So the rebuild dies somewhere in processing. Read its own logs rather than theorising again.
"""
import glob, os
H = os.path.expanduser("~")
for p in ["Library/Logs/valleypawn/usearch-refresh.log",
          "Library/Logs/valleypawn/usearch-verify.log",
          "Documents/Claude/Projects/Unified Search/refresh_hardened.log",
          "Documents/Claude/Projects/Unified Search/refresh.log"]:
    f = os.path.join(H, p)
    print("\n" + "="*70); print(f.replace(H, "~"))
    if not os.path.isfile(f):
        print("  (absent)"); continue
    try:
        lines = open(f, errors="replace").read().splitlines()
    except Exception as e:
        print("  unreadable:", e); continue
    print("  %d lines, last modified %s" % (len(lines),
          __import__("datetime").datetime.fromtimestamp(os.path.getmtime(f)).strftime("%m/%d %H:%M")))
    for l in lines[-22:]:
        print("   " + l[:200])
