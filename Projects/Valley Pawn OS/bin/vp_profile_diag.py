#!/usr/bin/env python3
"""vp_profile_diag.py — READ-ONLY look at the shared automation Chrome profile (pw-vp) for one site.
Built 2026-10-20 to diagnose why Northwest's sign-in did not persist. NO browser is opened.

Prints, for every host that contains the given site string (default northwestregisteredagent.com):
  cookies   host, name, path, is_persistent, expires (UTC), created (ET), last access (ET), secure/httponly/samesite
            — NAMES AND FLAGS ONLY. Cookie VALUES are never selected (the column is not in the query).
  logins    origin_url, action_url, username, date_created, date_last_used from Login Data
            — the password column is never selected.
  history   visits in the last N hours (default 4) to that site: time (ET), host + path (+ fragment only
            when it carries no '='; the query string is always dropped) — so the sign-in timeline is visible
            without any token.
  storage   whether the site's origins appear in Local Storage / Session Storage leveldb files (counts only;
            no keys, no values).
  prefs     profile.exit_type / exited_cleanly, Secure Preferences session.restore_on_startup,
            password_manager-related pref NAMES present (credentials_enable_service etc.) with their values.
Reads copies of the SQLite files (Chrome keeps them locked while open). Exit 0 always; prints what it finds.

  vp_profile_diag.py [--site northwestregisteredagent.com] [--hours 4]
"""
import datetime as dt
import glob
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
PROFILE = os.path.join(HOME, "Library/Application Support/valleypawn/pw-vp")
DEFAULT = os.path.join(PROFILE, "Default")
WIN_EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def chrome_time(us):
    """Chrome timestamp (microseconds since 1601-01-01 UTC) -> ET string, or '-' when 0/None."""
    if not us:
        return "-"
    try:
        return (WIN_EPOCH + dt.timedelta(microseconds=int(us))).astimezone(ET).strftime("%m-%d %H:%M:%S")
    except (OverflowError, ValueError):
        return "?"


def chrome_time_utc(us):
    if not us:
        return "-"
    try:
        return (WIN_EPOCH + dt.timedelta(microseconds=int(us))).strftime("%Y-%m-%d %H:%MZ")
    except (OverflowError, ValueError):
        return "?"


def copy_db(path):
    """Copy a SQLite file (and its -journal/-wal if present) to a temp dir and return the copy path, or None."""
    if not os.path.exists(path):
        return None
    d = tempfile.mkdtemp(prefix="vpdiag-")
    dst = os.path.join(d, os.path.basename(path).replace(" ", "_"))
    shutil.copy(path, dst)
    for suf in ("-journal", "-wal"):
        if os.path.exists(path + suf):
            shutil.copy(path + suf, dst + suf)
    return dst


def cookies(site):
    src = os.path.join(DEFAULT, "Cookies")
    if not os.path.exists(src):
        src = os.path.join(DEFAULT, "Network", "Cookies")
    p = copy_db(src)
    print("== cookies (%s)" % (src if p else "no Cookies DB"))
    if not p:
        return
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(cookies)")]
        want = [c for c in ("host_key", "name", "path", "is_persistent", "has_expires", "expires_utc", "creation_utc",
                            "last_access_utc", "is_secure", "is_httponly", "samesite") if c in cols]
        rows = con.execute("SELECT %s FROM cookies WHERE host_key LIKE ? ORDER BY host_key, name" % ",".join(want),
                           ("%" + site,)).fetchall()
        total = con.execute("SELECT count(*), sum(is_persistent=0) FROM cookies").fetchone()
        print("   all cookies: %s rows, %s session-only" % total)
        for r in rows:
            d = dict(zip(want, r))
            print("   %-38s %-28s path=%-45s persistent=%s expires=%s created=%s last=%s sec=%s http=%s ss=%s" % (
                d.get("host_key"), d.get("name"), d.get("path"), d.get("is_persistent"), chrome_time_utc(d.get("expires_utc")),
                chrome_time(d.get("creation_utc")), chrome_time(d.get("last_access_utc")), d.get("is_secure"), d.get("is_httponly"), d.get("samesite")))
        if not rows:
            print("   (no cookies for *%s)" % site)
        con.close()
    except Exception as e:
        print("   cookies unreadable:", type(e).__name__, str(e)[:100])
    finally:
        shutil.rmtree(os.path.dirname(p), ignore_errors=True)


def logins(site):
    src = os.path.join(DEFAULT, "Login Data")
    p = copy_db(src)
    print("== logins (%s)" % (src if p else "no Login Data DB"))
    if not p:
        return
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(logins)")]
        want = [c for c in ("origin_url", "action_url", "username_value", "date_created", "date_last_used", "times_used", "blacklisted_by_user") if c in cols]
        n = con.execute("SELECT count(*) FROM logins").fetchone()[0]
        print("   saved logins in the profile: %d" % n)
        rows = con.execute("SELECT %s FROM logins WHERE origin_url LIKE ? OR action_url LIKE ?" % ",".join(want),
                           ("%" + site + "%", "%" + site + "%")).fetchall()
        for r in rows:
            d = dict(zip(want, r))
            print("   origin=%s action=%s user=%s created=%s last_used=%s times=%s blacklisted=%s" % (
                d.get("origin_url"), d.get("action_url"), d.get("username_value"), chrome_time(d.get("date_created")),
                chrome_time(d.get("date_last_used")), d.get("times_used"), d.get("blacklisted_by_user")))
        if not rows:
            print("   (no saved login for *%s*)" % site)
        con.close()
    except Exception as e:
        print("   logins unreadable:", type(e).__name__, str(e)[:100])
    finally:
        shutil.rmtree(os.path.dirname(p), ignore_errors=True)


def safe_url(u):
    """host + path (+ fragment only when it carries no '='); query dropped."""
    from urllib.parse import urlsplit
    s = urlsplit(u)
    out = s.netloc + s.path
    if s.fragment and "=" not in s.fragment:
        out += "#" + s.fragment[:60]
    if s.query:
        out += "?<%d chars dropped>" % len(s.query)
    return out


def history(site, hours):
    src = os.path.join(DEFAULT, "History")
    p = copy_db(src)
    print("== history (last %s h, %s)" % (hours, src if p else "no History DB"))
    if not p:
        return
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        since = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=float(hours)) - WIN_EPOCH).total_seconds() * 1e6)
        rows = con.execute("SELECT v.visit_time, u.url, v.transition FROM visits v JOIN urls u ON u.id = v.url "
                           "WHERE v.visit_time > ? AND u.url LIKE ? ORDER BY v.visit_time", (since, "%" + site + "%")).fetchall()
        for t, u, tr in rows:
            print("   %s  %s  (transition %s)" % (chrome_time(t), safe_url(u), tr & 0xff))
        if not rows:
            print("   (no visits to *%s* in the window)" % site)
        con.close()
    except Exception as e:
        print("   history unreadable:", type(e).__name__, str(e)[:100])
    finally:
        shutil.rmtree(os.path.dirname(p), ignore_errors=True)


def storage(site):
    print("== storage (origin presence only)")
    for sub in ("Local Storage/leveldb", "Session Storage"):
        d = os.path.join(DEFAULT, sub)
        if not os.path.isdir(d):
            print("   %s: absent" % sub)
            continue
        hits = 0
        files = 0
        for f in glob.glob(os.path.join(d, "*")):
            if not os.path.isfile(f):
                continue
            files += 1
            try:
                b = open(f, "rb").read()
            except Exception:
                continue
            hits += b.count(site.encode())
        print("   %s: %d files, %d occurrences of %r" % (sub, files, hits, site))


def prefs():
    print("== prefs")
    try:
        d = json.load(open(os.path.join(DEFAULT, "Preferences")))
        prof = d.get("profile", {})
        print("   exit_type=%r exited_cleanly=%r" % (prof.get("exit_type"), prof.get("exited_cleanly")))
        pm = {k: v for k, v in d.items() if "password" in k.lower() or "credentials" in k.lower()}
        print("   password-manager prefs:", json.dumps(pm)[:300] if pm else "(none set = Chrome defaults: saving + autofill on)")
        print("   autofill prefs:", json.dumps(d.get("autofill", {}))[:200])
    except Exception as e:
        print("   Preferences unreadable:", type(e).__name__)
    try:
        s = json.load(open(os.path.join(DEFAULT, "Secure Preferences")))
        print("   Secure Preferences session.restore_on_startup=%r" % s.get("session", {}).get("restore_on_startup"))
    except Exception as e:
        print("   Secure Preferences unreadable:", type(e).__name__)
    for f in ("Preferences", "Secure Preferences", "Cookies", "Login Data", "History"):
        q = os.path.join(DEFAULT, f)
        if os.path.exists(q):
            print("   %-18s %8d bytes  mtime %s" % (f, os.path.getsize(q), dt.datetime.fromtimestamp(os.path.getmtime(q)).strftime("%m-%d %H:%M:%S")))


def main():
    site = arg("--site", "northwestregisteredagent.com")
    hours = arg("--hours", "4")
    print("vp_profile_diag", dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"), "profile:", PROFILE)
    import subprocess
    running = subprocess.run(["pgrep", "-f", "--", "--user-data-dir=" + PROFILE], capture_output=True, text=True).stdout.split()
    print("automation Chrome running:", bool(running), running[:3])
    prefs()
    cookies(site)
    logins(site)
    history(site, hours)
    storage(site)
    return 0


if __name__ == "__main__":
    sys.exit(main())
