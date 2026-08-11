#!/usr/bin/env python3
"""Index Apple Notes (Notes.app) into the Unified Search index.

Extracts every note via AppleScript (run through the `osascript` CLI):
title, HTML body (stripped to plaintext), container folder, note id,
creation date, modification date.

EXCLUSION (do not remove this section without Joshua's sign-off):
Some notes are deliberately never indexed. Their content is never read,
never printed, never logged, never written to index.db or anywhere else.
Add more titles to EXCLUDED_TITLES below to exclude further notes -- match
is case-insensitive and exact on the note's title. Currently excludes:
  - "Back Up Credetials" (sic) -- Joshua's credentials/password store.
    Decision made 2026-08-09: index all other Notes normally, but skip
    this one entirely.
The AppleScript below fetches note TITLES in bulk first (titles are not
sensitive -- they're the match key), then only fetches the body/folder/id/
dates of a note if its title does NOT match an excluded title. An excluded
note's body property is never requested from Notes.app at all, so its
content never crosses the Apple Event boundary into this script.

Adds/refreshes the `notes` FTS5 table in index.db. Read-only against
Notes.app (never edits or deletes notes).
"""
import os, re, sqlite3, subprocess, time, sys, html, datetime

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects/Unified Search")
DB = os.path.join(PROJ, "index.db")
MAXTEXT = 60000

# ---- exclusion list: add more titles here to exclude more notes ----
EXCLUDED_TITLES = [
    "Back Up Credetials",   # credentials/password store -- never index (Joshua, 2026-08-09)
]

FS = "\x01"   # field separator
RS = "\x02"   # record separator

TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
TAG2 = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\r\f\v]+")
NL = re.compile(r"\n{3,}")


def detag(s):
    s = TAG.sub(" ", s)
    s = TAG2.sub("\n", s)
    s = html.unescape(s)
    return NL.sub("\n\n", WS.sub(" ", s)).strip()


def _as_literal(items):
    return ", ".join('"%s"' % t.replace("\\", "\\\\").replace('"', '\\"') for t in items)


def build_applescript():
    excl = _as_literal(EXCLUDED_TITLES)
    # Each note is handled inside its own try block: some notes (locked notes,
    # items in Recently Deleted, etc.) throw on property access, and one bad
    # note shouldn't abort the whole run. Title is fetched per-note (not in
    # bulk) so the exclusion check always happens before body is requested.
    return '''
    set FS to (ASCII character 1)
    set RS to (ASCII character 2)
    set excludedTitles to {%s}
    set outText to ""
    tell application "Notes"
        set allNotes to notes
        set nCount to count of allNotes
        repeat with i from 1 to nCount
            try
                set theNote to item i of allNotes
                set noteTitle to (name of theNote) as string
                set isExcluded to false
                repeat with ex in excludedTitles
                    set exStr to (ex as string)
                    ignoring case
                        if noteTitle is equal to exStr then set isExcluded to true
                    end ignoring
                end repeat
                if not isExcluded then
                    set noteBody to ""
                    try
                        set noteBody to (body of theNote) as string
                    end try
                    set folderName to ""
                    try
                        set folderName to (name of container of theNote) as string
                    end try
                    set noteId to ""
                    try
                        set noteId to (id of theNote) as string
                    end try
                    set noteCreated to ""
                    try
                        set noteCreated to ((creation date of theNote) as string)
                    end try
                    set noteModified to ""
                    try
                        set noteModified to ((modification date of theNote) as string)
                    end try
                    set outText to outText & noteTitle & FS & noteBody & FS & folderName & FS & noteId & FS & noteCreated & FS & noteModified & RS
                end if
            end try
        end repeat
    end tell
    return outText
    ''' % excl


def parse_applescript_date(s):
    """AppleScript 'date' coerced to string, e.g.
    'Sunday, August 9, 2026 at 3:04:12 PM' -> epoch seconds. 0 on failure."""
    try:
        s = s.strip()
        if " at " in s:
            datepart, timepart = s.split(" at ", 1)
        else:
            datepart, timepart = s, "12:00:00 AM"
        datepart = datepart.split(", ", 1)[-1]   # drop leading weekday
        dt = datetime.datetime.strptime(datepart + " " + timepart, "%B %d, %Y %I:%M:%S %p")
        return int(dt.timestamp())
    except Exception:
        return 0


def fetch():
    r = subprocess.run(["osascript", "-e", build_applescript()],
                        capture_output=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError("osascript (Notes) failed: %s"
                            % r.stderr.decode("utf-8", "ignore")[:500])
    return r.stdout.decode("utf-8", "ignore")


def build():
    t0 = time.time()
    print("fetching notes via AppleScript (excluded titles skipped before body is read) ...",
          flush=True)
    raw = fetch()
    records = [rec for rec in raw.split(RS) if rec.strip()]
    print("received %d non-excluded notes from Notes.app" % len(records), flush=True)

    c = sqlite3.connect(DB, timeout=180)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS notes USING fts5(
        title, body, folder,
        path_or_id UNINDEXED, mtime UNINDEXED, created UNINDEXED,
        tokenize="porter unicode61")""")
    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    c.execute("DELETE FROM notes")
    c.commit()

    n = 0
    caught_excluded = 0   # belt-and-suspenders re-check; should always be 0
    batch = []
    for rec in records:
        fields = rec.split(FS)
        if len(fields) < 6:
            continue
        title, body_html, folder, note_id, created_s, modified_s = fields[:6]
        if any(title.strip().lower() == ex.lower() for ex in EXCLUDED_TITLES):
            caught_excluded += 1
            continue
        body = detag(body_html)[:MAXTEXT]
        created = parse_applescript_date(created_s)
        modified = parse_applescript_date(modified_s)
        batch.append((title[:1000], body, folder[:300], note_id, modified, created))
        if len(batch) >= 300:
            c.executemany("INSERT INTO notes VALUES(?,?,?,?,?,?)", batch)
            c.commit()
            n += len(batch)
            batch = []
    if batch:
        c.executemany("INSERT INTO notes VALUES(?,?,?,?,?,?)", batch)
        n += len(batch)
    c.commit()
    c.execute("INSERT OR REPLACE INTO meta VALUES('notes_indexed_at',?)", (str(int(time.time())),))
    c.execute("INSERT OR REPLACE INTO meta VALUES('notes_count',?)", (str(n),))
    c.commit()
    print("NOTES DONE: %d notes indexed in %ds (excluded-title matches caught post-fetch: %d, "
          "expected 0 since they're filtered before body is ever read)"
          % (n, time.time() - t0, caught_excluded), flush=True)


if __name__ == "__main__":
    build()
