#!/usr/bin/env python3
"""vp_people.py — the ONE shared "who may be named in a report" filter (fleet-wide rule, Joshua 2026-10-21).

RULE: every ranking / employee-naming report mentions ONLY current employees, and NEVER any Davis family
member (last name Davis — Joshua, Hillary, Audrey, Kennedy, Madison, Savannah, or any future Davis).
Report-specific exclusions that already exist (e.g. clock-in: Preston Peters + Sandi Cole as salaried,
rankings: Preston Peters as ownership) stay in THOSE reports; this module does not add them anywhere.

  current_staff()            -> list of roster dicts from hr/ROSTER.json (Gusto ACTIVE, refreshed daily by the
                                cloud "Staff roster refresh" task). Raises RosterHold if missing/empty/>2 days old.
  resolve(name, store=None)  -> the roster dict this Bravo / Gusto / Slack / display name refers to, or None.
                                Handles "LAST, FIRST", "STORE - Name" labels, "(Manager)" suffixes, middle
                                initials, logins ("SANDI", "WTAPLEY", "ADAVIS" via hr/BRAVO_USERS.json, store-aware),
                                initial+last ("J DAVIS", "W. Tapley"), preferred names and display overrides
                                (Benjie = George Moore, Bree = Bridgett Grayson, Sandi = Sandra Cole, ...).
  is_davis(name)             -> True if the name / login carries the Davis surname (case-insensitive).
  is_reportable(name, store=None) -> current in Gusto AND not Davis. Unknown / unmatched = NOT reportable.
  filter_rows(rows, name_key, store_key=None, source=None) -> (kept, dropped)
                                name_key: dict key, tuple index, or callable(row)->name. dropped = [(name, reason)]
                                FOR LOGS ONLY — never print dropped names in a post. Also appended to
                                fleet/state/vp_people/dropped.log (local, never posted).
  filter_names(names, ...)   -> (kept_names, dropped)
  mentions_davis(text)       -> True if free text names a Davis (for prose-style reports / AI answers).
  display_name(name)         -> the name the field knows ("Benjie Moore", "Sandi Cole", "Bree Grayson").

CLI: vp_people.py --self-test | --check "NAME" [STORE] | --staff
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
ROSTER_PATH = os.environ.get("VP_ROSTER_PATH") or os.path.join(OS_DIR, "hr", "ROSTER.json")
BRAVO_USERS_PATH = os.path.join(OS_DIR, "hr", "BRAVO_USERS.json")
DROP_LOG = os.path.join(OS_DIR, "fleet", "state", "vp_people", "dropped.log")
ROSTER_MAX_AGE_DAYS = 2
DAVIS = "DAVIS"

# Display / nickname crosswalk (Bravo or field name -> Gusto legal name). Union of comms_engine.NAME_ALIASES,
# clockin_check.OVERRIDES, BRAVO_USERS.json "aliases" and chekkit_ops' Sandra/Sandi + George/Benjie.
ALIASES = {
    "BENJIE MOORE": "GEORGE MOORE",
    "GEORGE B MOORE": "GEORGE MOORE",
    "SANDI COLE": "SANDRA COLE",
    "STEVE BURCH": "STEVEN BURCH",
    "BREE GRAYSON": "BRIDGETT GRAYSON",
    "JOEY EPPERLY": "JOSEPH EPPERLY",
    "CHAD MCCLINTIC": "CHADD MCCLINTIC",
}
DISPLAY = {"GEORGE MOORE": "Benjie Moore", "SANDRA COLE": "Sandi Cole", "BRIDGETT GRAYSON": "Bree Grayson"}
STORE_CODES = {"CUL": "CUL", "CULPEPER": "CUL", "HAR": "HAR", "HARRISONBURG": "HAR", "LEX": "LEX",
               "LEXINGTON": "LEX", "ROA": "ROA", "ROANOKE": "ROA", "WAY": "WAY", "WAYNESBORO": "WAY"}
SERVICE_PREFIXES = ("FREE1", "SYSTEM", "BACKUP", "APPROVAL")
_ROLE_WORDS = {"MANAGER", "STORE", "ASSOCIATE", "REP", "SALES", "LOAN", "REPRESENTATIVE", "JR", "SR", "II", "III"}


class RosterHold(Exception):
    """The active roster can't be trusted (missing / empty / stale). Callers must NOT publish unfiltered."""


_cache = {}


def _tokens(s):
    s = re.sub(r"\(.*?\)", " ", s or "")
    return re.sub(r"[^A-Z ]", " ", s.upper()).split()


def _clean(name):
    """-> list of upper tokens in FIRST ... LAST order."""
    s = (name or "").strip()
    if not s:
        return []
    s = re.sub(r"<@[^>]+>", " ", s)
    if " - " in s:                                   # Bravo "CUL - SANDRA COLE" / "123 - NAME" labels
        head, tail = s.split(" - ", 1)
        if head.strip().upper() in STORE_CODES or re.fullmatch(r"[\w]{1,6}", head.strip()):
            s = tail
    s = re.sub(r"\(.*?\)", " ", s)
    if s.count(",") == 1:                            # "LAST, FIRST [M]"
        last, first = [x.strip() for x in s.split(",")]
        if last and first:
            s = "%s %s" % (first, last)
    toks = [t for t in _tokens(s) if t not in _ROLE_WORDS]
    # leading avatar initials badge "UT Uriah Tiglao"
    if len(toks) >= 3 and len(toks[0]) == 2 and toks[0] == (toks[1][:1] + toks[-1][:1]):
        toks = toks[1:]
    return toks


def is_davis(name):
    """Davis surname anywhere: 'Joshua Davis', 'DAVIS, AUDREY', 'J DAVIS', login 'ADAVIS' / 'KDAVIS2', email 'adavis@'."""
    raw = (name or "").upper()
    for t in re.split(r"[^A-Z0-9]+", raw):
        t = re.sub(r"\d+$", "", t)
        if t == DAVIS or re.fullmatch(r"[A-Z]{1,2}DAVIS", t) or re.fullmatch(r"DAVIS[A-Z]", t):
            return True
    return False


def mentions_davis(text):
    return bool(re.search(r"(?i)\b[a-z]{0,2}davis\b", text or ""))


def _load_roster():
    if "roster" in _cache:
        return _cache["roster"]
    if not os.path.exists(ROSTER_PATH):
        raise RosterHold("active roster file not found — cannot filter to current employees")
    try:
        d = json.load(open(ROSTER_PATH))
    except (OSError, ValueError) as e:
        raise RosterHold("active roster unreadable (%s)" % e.__class__.__name__)
    gen = (d.get("generated_at") or "")[:10]
    try:
        age = (dt.date.today() - dt.date.fromisoformat(gen)).days
    except ValueError:
        age = 999
    if age > ROSTER_MAX_AGE_DAYS:
        raise RosterHold("active roster is %s days old — cannot filter to current employees" % age)
    emps = [e for e in d.get("employees", []) if len(_tokens(e.get("name"))) >= 2]
    if not emps:
        raise RosterHold("active roster is empty — cannot filter to current employees")
    for e in emps:
        t = _tokens(e["name"])
        e["_first"], e["_last"], e["_lastfull"] = t[0], t[-1], " ".join(t[1:])
        e["_pref"] = (_tokens(e.get("preferred")) or [t[0]])[0]
    _cache["roster"] = emps
    return emps


def _load_logins():
    if "logins" in _cache:
        return _cache["logins"]
    out = {}
    try:
        d = json.load(open(BRAVO_USERS_PATH))
        for u in d.get("users", []):
            lg = (u.get("login") or "").strip().upper()
            if lg:
                out.setdefault(lg, []).append((u.get("store") or "", u.get("name") or ""))
        for k, v in (d.get("aliases") or {}).items():
            a, b = " ".join(_tokens(k)), " ".join(_tokens(v))
            if a and b and a != b:
                ALIASES.setdefault(a, b)
    except (OSError, ValueError):
        pass
    _cache["logins"] = out
    return out


def current_staff():
    return list(_load_roster())


def _store(store):
    return STORE_CODES.get((store or "").strip().upper()) if store else None


def resolve(name, store=None, _depth=0):
    roster = _load_roster()
    logins = _load_logins()
    if (name or "").strip().upper().startswith(SERVICE_PREFIXES):
        return None
    toks = _clean(name)
    if not toks:
        return None
    full = " ".join(toks)
    if full in ALIASES:
        toks = ALIASES[full].split()
    first, last = toks[0], toks[-1]
    if len(toks) == 1:                                # a Bravo login or a bare first name
        hits = logins.get(first, [])
        st = _store(store)
        if not st and any(first in (e["_first"], e["_pref"]) for e in roster if e["_last"] == DAVIS):
            return None                               # bare "JOSHUA"/"HILLARY" with no store: could be a Davis

        if st:
            hits = [h for h in hits if h[0] == st] or ([] if len(hits) != 1 else hits)
        names = {h[1].upper() for h in hits}
        if len(names) == 1 and _depth == 0:
            return resolve(names.pop(), store, 1)
        m = re.fullmatch(r"([A-Z])([A-Z]{3,})", first)   # login shape FLAST, e.g. WTAPLEY
        if m and not hits:
            c = [e for e in roster if e["_last"] == m.group(2) and e["_first"].startswith(m.group(1))]
            if len(c) == 1:
                return c[0]
        return None
    # exact first(legal|preferred) + last (or full multi-word last)
    c = [e for e in roster if (last == e["_last"] or " ".join(toks[1:]) == e["_lastfull"])
         and first in (e["_first"], e["_pref"])]
    if len(c) == 1:
        return c[0]
    # initial + last ("J DAVIS", "W TAPLEY") or prefix first ("JOE EPPERLY" / "STEVE")
    c = [e for e in roster if e["_last"] == last and
         ((len(first) == 1 and (e["_first"].startswith(first) or e["_pref"].startswith(first))) or
          (len(first) >= 3 and (e["_first"].startswith(first) or first.startswith(e["_first"]) or e["_pref"].startswith(first))))]
    if len(c) == 1:
        return c[0]
    return None


def is_reportable(name, store=None):
    if is_davis(name):
        return False
    e = resolve(name, store)
    return bool(e) and e["_last"] != DAVIS and not is_davis(e.get("name")) and not is_davis(e.get("email"))


def reason(name, store=None):
    """None if reportable, else a short log-only reason."""
    if is_davis(name):
        return "Davis family"
    if (name or "").strip().upper().startswith(SERVICE_PREFIXES):
        return "shared / service login"
    e = resolve(name, store)
    if not e:
        return "not on the current Gusto roster (or unmatched)"
    if e["_last"] == DAVIS or is_davis(e.get("email")):
        return "Davis family"
    return None


def display_name(name, store=None):
    e = resolve(name, store)
    if not e:
        return name
    legal = " ".join(_tokens(e["name"]))
    if legal in DISPLAY:
        return DISPLAY[legal]
    return " ".join(w.capitalize() for w in (e["_pref"] + " " + e["_lastfull"]).lower().split())


def _get(row, key):
    if callable(key):
        return key(row)
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return None


def _log(source, dropped):
    if not dropped:
        return
    try:
        os.makedirs(os.path.dirname(DROP_LOG), exist_ok=True)
        with open(DROP_LOG, "a") as f:
            ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
            for n, r in dropped:
                f.write("%s\t%s\t%s\t%s\n" % (ts, source or "?", n, r))
    except OSError:
        pass


def filter_rows(rows, name_key, store_key=None, source=None):
    """Drop rows whose person is not reportable. Returns (kept, dropped[(name, reason)]) — dropped is LOG-ONLY."""
    kept, dropped = [], []
    for row in rows:
        n = _get(row, name_key)
        st = _get(row, store_key) if store_key is not None else None
        r = reason(str(n or ""), st)
        if r:
            dropped.append((str(n or ""), r))
        else:
            kept.append(row)
    _log(source or (sys.argv[0] and os.path.basename(sys.argv[0])), dropped)
    return kept, dropped


def filter_names(names, store=None, source=None):
    k, d = filter_rows([(n, store) for n in names], 0, 1, source)
    return [x[0] for x in k], d


def _self_test():
    cases = [
        ("Joshua Davis", None, False), ("DAVIS, AUDREY", None, False), ("ADavis", None, False),
        ("J DAVIS", None, False), ("Savannah Davis", None, False), ("kdavis@fcfpawn.com", None, False),
        ("Hillary", None, False),
        ("SANDRA COLE", None, True), ("Sandi Cole", None, True), ("COLE, SANDRA", None, True),
        ("SANDI", "CUL", True), ("JOSHUA", "CUL", True), ("JOSHUA", None, False), ("Joshua Burnett", None, True),
        ("Benjie Moore", None, True), ("George B Moore", None, True), ("BENJIE", "ROA", True),
        ("WTAPLEY", "HAR", True), ("Walker Tapley (Manager)", None, True), ("CUL - ROBERT SWAGGER", None, True),
        ("JACOB COX", None, False), ("JACOB", "ROA", False), ("Andrew Clark", None, False),
        ("Lee Cornelison", None, False), ("FREE1 VALLEY PAWN", None, False), ("APPROVAL SANDI", None, False),
        ("Nobody Known", None, False), ("", None, False), ("Preston Peters", None, True),
        ("UT Uriah Tiglao", None, True), ("Chadd McClintic", None, True), ("Joey Epperly", None, True),
    ]
    bad = 0
    for n, st, want in cases:
        got = is_reportable(n, st)
        flag = "ok " if got == want else "BAD"
        bad += got != want
        print("%s %-28s %-4s -> %s (%s)" % (flag, n, st or "", got, reason(n, st) or "reportable"))
    print("FAILED %d" % bad if bad else "ALL PASS (%d)" % len(cases))
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--self-test"]:
        sys.exit(1 if _self_test() else 0)
    if a[:1] == ["--staff"]:
        for e in current_staff():
            print(("x " if not is_reportable(e["name"]) else "  ") + e["name"])
        sys.exit(0)
    if a[:1] == ["--check"] and len(a) >= 2:
        print(is_reportable(a[1], a[2] if len(a) > 2 else None), reason(a[1], a[2] if len(a) > 2 else None) or "")
        sys.exit(0)
    print(__doc__)
