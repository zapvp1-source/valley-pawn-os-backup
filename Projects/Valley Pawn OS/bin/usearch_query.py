#!/usr/bin/env python3
"""usearch_query.py — READ-ONLY Unified Search query runner for cloud sessions (2026-11-12, Joshua approved).

WHY: since 11/7 index.db lives in ~/.vp-studio/offsync/unified-search (moved out of Drive sync),
which cloud Cowork sessions cannot mount, and vpfind needs a host shell. A session drops a host-queue
job calling this script; it runs on the Mac via vp-runner and writes JSON results back inside the
Projects folder (Unified Search/_query_results/), where any session can read them.
Opens the index with mode=ro&immutable=1 — never writes to index.db.

  python3 ".../bin/usearch_query.py" --tag NAME --corpus msgs --match "fireplace OR todd" --since 2026-06-01
  python3 ".../bin/usearch_query.py" --tag NAME --corpus msgs --handle 9045319315 --since 2026-06-01
"""
import argparse, json, os, sqlite3, sys, time, datetime, re
HOME = os.path.expanduser("~")
DB = os.path.join(HOME, ".vp-studio/offsync/unified-search/index.db")
OUT = os.path.join(HOME, "Documents/Claude/Projects/Unified Search/_query_results")
COLS = {"msgs": ["body", "person", "chatname", "handle", "service", "ts", "from_me"],
        "mail": ["subject", "sender", "recipients", "body", "path", "mailbox", "ts"],
        "files": ["name", "folder", "body", "path", "mtime"],
        "notes": None, "reminders": None, "photos": None, "doc_photos": None, "gdrive": None}
TS = {"msgs": "ts", "mail": "ts", "files": "mtime"}
p = argparse.ArgumentParser()
p.add_argument("--tag", required=True); p.add_argument("--corpus", required=True, choices=sorted(COLS))
p.add_argument("--match", default=""); p.add_argument("--handle", default="")
p.add_argument("--since", default=""); p.add_argument("--until", default="")
p.add_argument("--limit", type=int, default=300); p.add_argument("--bodychars", type=int, default=4000)
a = p.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", a.tag): sys.exit("bad tag")
os.makedirs(OUT, exist_ok=True)
con = sqlite3.connect("file:%s?mode=ro&immutable=1" % DB, uri=True)
cols = COLS[a.corpus] or [r[1] for r in con.execute("pragma table_info(%s)" % a.corpus)]
where, args = [], []
if a.match: where.append("%s MATCH ?" % a.corpus); args.append(a.match)
if a.handle and a.corpus == "msgs":
    where.append("(handle LIKE ? OR person LIKE ? OR chatname LIKE ?)"); args += ["%" + a.handle + "%"] * 3
tcol = TS.get(a.corpus)
def ep(d): return int(time.mktime(datetime.datetime.strptime(d, "%Y-%m-%d").timetuple()))
if tcol and a.since: where.append("CAST(%s AS INTEGER) >= ?" % tcol); args.append(ep(a.since))
if tcol and a.until: where.append("CAST(%s AS INTEGER) < ?" % tcol); args.append(ep(a.until))
sql = "select %s from %s" % (", ".join(cols), a.corpus) + (" where " + " and ".join(where) if where else "")
if tcol: sql += " order by CAST(%s AS INTEGER)" % tcol
sql += " limit %d" % a.limit
t0 = time.time(); rows = []
for r in con.execute(sql, args):
    d = dict(zip(cols, r))
    if isinstance(d.get("body"), str) and len(d["body"]) > a.bodychars: d["body"] = d["body"][:a.bodychars] + " …[cut]"
    if tcol and d.get(tcol) not in (None, ""):
        try: d["when"] = datetime.datetime.fromtimestamp(int(float(d[tcol]))).strftime("%Y-%m-%d %H:%M")
        except Exception: pass
    rows.append(d)
n = len([f for f in os.listdir(OUT) if f.startswith(a.tag + "__")])
fn = os.path.join(OUT, "%s__%s__%d.json" % (a.tag, a.corpus, n))
json.dump({"args": vars(a), "sql": sql, "count": len(rows), "secs": round(time.time() - t0, 1), "rows": rows},
          open(fn, "w"), ensure_ascii=False, indent=1, default=str)
with open(os.path.join(OUT, a.tag + ".index.txt"), "a") as f:
    f.write("%s\t%s\t%d rows\t%s\n" % (os.path.basename(fn), a.corpus, len(rows), a.match or a.handle))
print("wrote", fn, len(rows), "rows")
