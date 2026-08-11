#!/usr/bin/env python3
"""Index Apple Reminders (Reminders.app) into the Unified Search index.

Extracts every reminder via AppleScript (run through the `osascript` CLI):
name, body/notes, container list name, due date, completed flag,
modification date. Processes ONE LIST AT A TIME, each in its own osascript
subprocess with its own timeout -- an earlier version tried to do all lists
in a single script and could hang indefinitely if one list was very large;
per-list isolation means one pathological list times out and gets skipped
(logged) rather than blocking every other list. Within each list, all
reminders' properties are bulk-fetched ("property of reminders of lst",
composed directly -- NOT via an intermediate variable, which breaks
AppleScript's bulk-elements resolution and forces a much slower per-item
round trip), so it's ~6 Apple Events per list rather than ~6 per reminder.

Adds/refreshes the `reminders` FTS5 table in index.db. Read-only against
Reminders.app (never edits or deletes reminders).
"""
import os, re, sqlite3, subprocess, time, sys, datetime

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
MAXTEXT = 60000

FS = "\x01"   # field separator
RS = "\x02"   # record separator

WS = re.compile(r"[ \t\r\f\v]+")

LISTS_SCRIPT = 'tell application "Reminders" to return name of lists'

LIST_SCRIPT_TMPL = '''
set FS to (ASCII character 1)
set RS to (ASCII character 2)
set outText to ""
tell application "Reminders"
    set lst to list "%s"
    set nms to {}
    try
        set nms to name of reminders of lst
    end try
    set bds to {}
    try
        set bds to body of reminders of lst
    end try
    set dues to {}
    try
        set dues to due date of reminders of lst
    end try
    set cmps to {}
    try
        set cmps to completed of reminders of lst
    end try
    set mods to {}
    try
        set mods to modification date of reminders of lst
    end try
    set ids to {}
    try
        set ids to id of reminders of lst
    end try
    set n to count of nms
    repeat with i from 1 to n
        set rName to item i of nms
        set rBody to ""
        try
            set bItem to item i of bds
            if bItem is not missing value then set rBody to bItem as string
        end try
        set rDue to ""
        try
            set dItem to item i of dues
            if dItem is not missing value then set rDue to (dItem as string)
        end try
        set rCompleted to "0"
        try
            if item i of cmps then set rCompleted to "1"
        end try
        set rModified to ""
        try
            set mItem to item i of mods
            if mItem is not missing value then set rModified to (mItem as string)
        end try
        set rId to ""
        try
            set rId to (item i of ids) as string
        end try
        set outText to outText & rName & FS & rBody & FS & "%s" & FS & rDue & FS & rCompleted & FS & rModified & FS & rId & RS
    end repeat
end tell
return outText
'''

PER_LIST_TIMEOUT = 2400  # seconds; a list that blows through this is skipped, not hung on forever.
# Generous on purpose -- Joshua's "PRIORITY" list alone has thousands of items and the earlier
# 638-item "Joshua" list took ~200s, so a several-thousand-item list can genuinely take 20-30+ min.


def _as_applescript_literal(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def list_names():
    r = subprocess.run(["osascript", "-e", LISTS_SCRIPT], capture_output=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("osascript (Reminders lists) failed: %s"
                            % r.stderr.decode("utf-8", "ignore")[:500])
    out = r.stdout.decode("utf-8", "ignore").strip()
    return [n.strip() for n in out.split(",") if n.strip()]


def fetch_list(name):
    lit = _as_applescript_literal(name)
    script = LIST_SCRIPT_TMPL % (lit, lit)
    try:
        r = subprocess.run(["osascript", "-e", script],
                            capture_output=True, timeout=PER_LIST_TIMEOUT)
    except subprocess.TimeoutExpired:
        print("  WARN: list %r timed out after %ds, skipping" % (name, PER_LIST_TIMEOUT), flush=True)
        return ""
    if r.returncode != 0:
        print("  WARN: list %r failed: %s" % (name, r.stderr.decode("utf-8", "ignore")[:300]), flush=True)
        return ""
    return r.stdout.decode("utf-8", "ignore")


def parse_applescript_date(s):
    """AppleScript 'date' coerced to string -> epoch seconds. 0 on failure/blank
    (Reminders with no due date coerce to empty string)."""
    try:
        s = s.strip()
        if not s:
            return 0
        if " at " in s:
            datepart, timepart = s.split(" at ", 1)
        else:
            datepart, timepart = s, "12:00:00 AM"
        datepart = datepart.split(", ", 1)[-1]
        dt = datetime.datetime.strptime(datepart + " " + timepart, "%B %d, %Y %I:%M:%S %p")
        return int(dt.timestamp())
    except Exception:
        return 0


def build():
    t0 = time.time()
    print("listing Reminders lists ...", flush=True)
    names = list_names()
    print("found %d lists: %s" % (len(names), ", ".join(names)), flush=True)

    c = sqlite3.connect(DB, timeout=180)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS reminders USING fts5(
        title, body, list_name,
        due UNINDEXED, completed UNINDEXED, mtime UNINDEXED, path_or_id UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    c.execute("DELETE FROM reminders")
    c.commit()

    n = 0
    for lname in names:
        t1 = time.time()
        print("  fetching list %r ..." % lname, flush=True)
        raw = fetch_list(lname)
        records = [rec for rec in raw.split(RS) if rec.strip()]
        batch = []
        for rec in records:
            fields = rec.split(FS)
            if len(fields) < 7:
                continue
            name, body, list_name, due_s, completed_s, modified_s, rid = fields[:7]
            body = WS.sub(" ", body).strip()[:MAXTEXT]
            due = parse_applescript_date(due_s)
            modified = parse_applescript_date(modified_s)
            completed = 1 if completed_s.strip() == "1" else 0
            batch.append((name[:1000], body, list_name[:300], due, completed, modified, rid))
        if batch:
            c.executemany("INSERT INTO reminders VALUES(?,?,?,?,?,?,?)", batch)
            c.commit()
            n += len(batch)
        print("    %d reminders in %ds" % (len(batch), time.time() - t1), flush=True)

    c.execute("INSERT OR REPLACE INTO meta VALUES('reminders_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('reminders_count',?)", (str(n),))
    c.commit()
    print("REMINDERS DONE: %d reminders indexed in %ds" % (n, time.time() - t0), flush=True)


if __name__ == "__main__":
    build()
