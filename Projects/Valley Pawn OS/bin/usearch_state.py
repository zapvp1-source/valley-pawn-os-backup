#!/usr/bin/env python3
"""usearch_state.py — is the search index actually current, per table?

The hardened log reported success at 11:14 today, but success of the RUN is not the same as the
MAIL step having ingested anything — the shrink guard aborts mail alone and lets the run continue.
Check the corpus itself (Rule 12: verify against output).
"""
import datetime as dt, os, re, sqlite3
H = os.path.expanduser("~")
db = os.path.join(H, "Documents/Claude/Projects/Unified Search/index.db")
print("index.db modified: %s" % dt.datetime.fromtimestamp(os.path.getmtime(db)).strftime("%Y-%m-%d %H:%M"))
c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
for t in ("mail", "msgs", "files"):
    try:
        n = c.execute("select count(*) from %s" % t).fetchone()[0]
        print("%-6s rows: %d" % (t, n))
    except Exception as e:
        print("%-6s error: %s" % (t, e))
try:
    newest = c.execute("select max(ts) from mail").fetchone()[0]
    if newest:
        v = float(newest)
        if v > 1e11: v /= 1000.0
        print("newest mail ts: %s" % dt.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M"))
except Exception as e:
    print("newest mail ts: %s" % e)
log = os.path.join(H, "Documents/Claude/Projects/Unified Search/refresh_hardened.log")
txt = open(log, errors="replace").read().splitlines()
print("\n--- MAIL-related lines from today's run ---")
hits = [l for l in txt[-1200:] if re.search(r"mail|shrink|abort|refus|skip", l, re.I)]
for l in hits[-18:]:
    print("  " + l[:190])
