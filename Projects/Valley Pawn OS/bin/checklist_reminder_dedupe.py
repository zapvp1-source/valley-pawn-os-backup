#!/usr/bin/env python3
"""checklist_reminder_dedupe.py — duplicate guard for the `sunday-checklist-summary` scheduled task.

Built 2026-09-30. WHY: the 8/10-8/15 store-checklist TO-DOs were created in Apple Reminders TWICE —
once by the 8/21 fix session's manual backfill (12:58 PM) and again by the Sun 8/23 8 PM scheduled
run — with differently worded titles, because nothing checked for an existing reminder from the same
week + same checklist photo before creating one. This script is that check. It matches on the SOURCE
(week + photo filename / Slack message) found in the reminder NOTES, never on title wording.

Usage (python3 3.9-compatible; macOS system python is fine):
  checklist_reminder_dedupe.py check  --week YYYY-MM-DD --source IMG_2990 [--source ...]
  checklist_reminder_dedupe.py record --week YYYY-MM-DD --source IMG_2990 --list Harrisonburg \
                                      --title "..." [--id <reminder id>]
  checklist_reminder_dedupe.py key    --week YYYY-MM-DD --source IMG_2990      # prints the notes key line

--week is the MONDAY of the Mon-Sat window. --source is the photo filename (IMG_2990, IMG_2990.jpg and
img_2990.JPG all normalise to IMG_2990), or for a typed Slack message `slack-ts-<ts>`.

`check` prints one line per source:  LOGGED <source> via=<state|live|index> evidence=<...>
                                  or NEW <source>
and a final line  CHECKS state=<ok|missing|error> live=<ok|unavailable> index=<ok|unavailable>.
Exit code 0 if at least one of live/index worked (safe to create the NEW ones), 3 if neither did
(do NOT create anything — list the TO-DOs in the report instead).

Evidence sources, in order:
  1. State ledger  Valley Pawn OS/fleet/state/sunday-checklist-summary_created.json
  2. Live Reminders notes via Life OS/bin/ekremnotes (EventKit; compiled from ekremnotes.swift on first
     use). NEVER AppleScript — AppleScript sees only a subset of lists on this Mac.
  3. Unified Search index (Reminders snapshot, refreshed nightly ~4 AM) — fallback if (2) unavailable.
Open AND completed reminders both count: a photo already logged and since completed is not re-logged.
Read-only against Reminders. Only `record` writes, and only to the state ledger.
"""
import argparse, datetime, json, os, re, sqlite3, subprocess, sys

ROOT = "/Users/joshuadavis/Documents/Claude/Projects"
STATE = os.path.join(ROOT, "Valley Pawn OS/fleet/state/sunday-checklist-summary_created.json")
BIN = os.path.join(ROOT, "Life OS/bin")
EKREMNOTES = os.path.join(BIN, "ekremnotes")
EKREMNOTES_SRC = os.path.join(BIN, "ekremnotes.swift")
INDEX = os.path.join(ROOT, "Unified Search/index.db")
LISTS = ["Preston Joshua", "Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]


def norm_source(s):
    s = s.strip()
    m = re.search(r"IMG_(\d+)", s, re.I)
    if m:
        return "IMG_" + m.group(1)
    return s


def week_patterns(week):
    """Regexes that identify the week in a reminder's notes: new key line + legacy prose forms."""
    d = datetime.date.fromisoformat(week)
    md = "%d/%d" % (d.month, d.day)
    return [
        re.compile(r"wk=" + re.escape(week)),
        re.compile(r"week of\s+(Mon\s+)?" + re.escape(md) + r"\b", re.I),
        re.compile(r"Mon\s+" + re.escape(md) + r"\s*[-–]", re.I),
    ]


def source_pattern(src):
    if src.upper().startswith("IMG_"):
        return re.compile(r"\bIMG_" + src[4:] + r"\b", re.I)
    return re.compile(re.escape(src))


def load_state():
    if not os.path.exists(STATE):
        return {"weeks": {}}, "missing"
    try:
        with open(STATE) as f:
            return json.load(f), "ok"
    except Exception as e:  # corrupt ledger: treat as error, never overwrite silently
        sys.stderr.write("state read error: %s\n" % e)
        return None, "error"


def live_rows():
    """[(status, id, title, notes, list)] from EventKit, or None if unavailable."""
    if not os.path.exists(EKREMNOTES) and os.path.exists(EKREMNOTES_SRC):
        try:
            subprocess.run(["swiftc", "-O", "-o", EKREMNOTES, EKREMNOTES_SRC],
                           capture_output=True, timeout=180)
        except Exception:
            pass
    if not os.path.exists(EKREMNOTES):
        return None
    rows = []
    for lst in LISTS:
        try:
            p = subprocess.run([EKREMNOTES, lst, "all"], capture_output=True, text=True, timeout=60)
        except Exception:
            return None
        out = p.stdout.splitlines()
        if not out:
            return None
        if out[0].startswith("ERROR"):
            return None
        if out[0].strip() == "list not found":
            continue  # a missing list simply has nothing in it
        for line in out[1:]:
            parts = line.split("\t")
            if len(parts) >= 4:
                rows.append((parts[0], parts[1], parts[2], parts[3], lst))
    return rows


def index_rows():
    if not os.path.exists(INDEX):
        return None
    try:
        c = sqlite3.connect("file:%s?mode=ro" % INDEX, uri=True, timeout=10)
        q = "SELECT completed, path_or_id, title, body, list_name FROM reminders WHERE list_name IN (%s)" % (
            ",".join("?" * len(LISTS)))
        rows = [("DONE" if r[0] else "OPEN", r[1], r[2], r[3] or "", r[4]) for r in c.execute(q, LISTS)]
        c.close()
        return rows
    except Exception as e:
        sys.stderr.write("index read error: %s\n" % e)
        return None


def find(rows, week, src):
    wp = week_patterns(week)
    sp = source_pattern(src)
    for st, rid, title, notes, lst in rows:
        if sp.search(notes) and any(p.search(notes) for p in wp):
            return "%s:%s:%s" % (lst, st, title[:70])
    return None


def cmd_check(a):
    state, sstat = load_state()
    live = live_rows()
    idx = index_rows() if live is None else None
    for raw in a.source:
        src = norm_source(raw)
        hit = None
        if state:
            wk = state.get("weeks", {}).get(a.week, {})
            if src in wk.get("sources_logged", []):
                hit = ("state", "ledger week %s" % a.week)
        if not hit and live is not None:
            e = find(live, a.week, src)
            if e:
                hit = ("live", e)
        if not hit and idx is not None:
            e = find(idx, a.week, src)
            if e:
                hit = ("index", e)
        if hit:
            print("LOGGED %s via=%s evidence=%s" % (src, hit[0], hit[1]))
        else:
            print("NEW %s" % src)
    print("CHECKS state=%s live=%s index=%s" % (
        sstat, "ok" if live is not None else "unavailable",
        "ok" if idx is not None else ("skipped" if live is not None else "unavailable")))
    if live is None and idx is None:
        sys.exit(3)


def cmd_record(a):
    state, sstat = load_state()
    if state is None:
        sys.stderr.write("refusing to write: state ledger unreadable\n")
        sys.exit(4)
    src = norm_source(a.source[0])
    wk = state.setdefault("weeks", {}).setdefault(a.week, {
        "window": "Mon %s - Sat %s" % (a.week, (datetime.date.fromisoformat(a.week)
                                               + datetime.timedelta(days=5)).isoformat()),
        "status": "logged", "sources_logged": [], "items": []})
    if src not in wk["sources_logged"]:
        wk["sources_logged"].append(src)
    wk.setdefault("items", []).append({
        "list": a.list, "title": a.title, "source": src, "id": a.id or "",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET"),
        "batch": "sunday-checklist-summary run"})
    tmp = STATE + ".tmp"
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE)
    print("RECORDED %s %s %s" % (a.week, src, a.list))


def cmd_key(a):
    print("Dedupe key: wk=%s src=%s" % (a.week, norm_source(a.source[0])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "record", "key"])
    ap.add_argument("--week", required=True)
    ap.add_argument("--source", action="append", required=True)
    ap.add_argument("--list")
    ap.add_argument("--title", default="")
    ap.add_argument("--id")
    a = ap.parse_args()
    datetime.date.fromisoformat(a.week)
    if a.cmd == "check":
        cmd_check(a)
    elif a.cmd == "record":
        if not a.list:
            ap.error("record needs --list")
        cmd_record(a)
    else:
        cmd_key(a)


if __name__ == "__main__":
    main()
