#!/usr/bin/env python3
"""vp_browser.py — ONE automation Chrome profile for every native browser script (2026-10-19).

WHY: until today each native check had its own profile (pw-cloudcover, pw-gusto, pw-northwest) and its own
copy of the launcher / prefs helpers, and Joshua was asked to sign in to CloudCover three times because the
session cookies set in the sign-in window did not reliably survive into the scripts' Playwright context.
Now there is ONE profile, ONE launch recipe and ONE sign-in window, and the persistence of a session cookie
across a normal quit is PROVEN by `vp_browser.py persist-set` / `persist-get` (see RECIPE below).

PROFILE  ~/Library/Application Support/valleypawn/pw-vp   (the former pw-cloudcover directory, renamed by
         `vp_browser.py migrate`; backup copy pw-cloudcover.bak-20261019 kept beside it)

USED BY  cloudcover_check.py, dress_code_check.py, clockin_check.py, northwest_check.py
         (each does `import vp_browser` and calls `vp_browser.launch(p, ...)`)

SIGN-IN  bin/vp_signin_front.sh  — ONE Chrome window in front with the four sign-in tabs; Joshua signs in,
         then quits that window (Cmd-Q) or runs bin/vp_signin_close.sh. Nothing here types a password.

ROOT CAUSE (found 2026-10-19, host jobs 20261019T1025-vp-profile-proof / T1030-vp-profile-diag):
  Chrome keeps session cookies (no expiry = every "logged in" cookie) across a restart ONLY when the startup
  setting is "Continue where you left off" (session.restore_on_startup = 1). Every earlier helper
  (cloudcover/gusto/northwest_profile_prefs.py, ensure_prefs()) wrote that key into Default/Preferences —
  but it is a TRACKED (MAC-protected) pref that Chrome reads from Default/Secure Preferences; the copy in
  Preferences is ignored and stripped on quit. So the setting was never in effect: the sign-in cookie was
  written to Default/Cookies at quit (is_persistent=0 row, verified with `cookie-db`) and DELETED by Chrome at
  the next launch. That is why CloudCover asked for a sign-in three times — not the keychain, not the quit.
  (Control: forcing profile.exit_type="Crashed" made the cookie come back, which is Chrome's crash-recovery
  rule and confirmed the cookie was on disk all along.)

RECIPE (the exact combination that passed BOTH persistence proofs on 2026-10-19, host job
        20261019T1040-vp-profile-proof2; do not change one piece without re-running the proofs):
  1. Startup setting, set ONCE through Chrome's own settings page so Chrome writes it (with its MAC) into
     Secure Preferences itself: `vp_browser.py set-startup` = a short headed session on pw-vp that opens
     chrome://settings/onStartup and calls chrome.settingsPrivate.setPref('session.restore_on_startup', 1).
     launch() self-heals: if startup_pref() (read from Secure Preferences) is not 1 it runs this first.
     Verified: Secure Preferences session.restore_on_startup = 1 survives every launch/quit since.
  2. Before EVERY launch, while that Chrome is closed (prefs()): profile.exit_type = "Normal" and
     profile.exited_cleanly = true in Preferences (not tracked; keeps Chrome from treating the next start as
     a crash). The sign-in launcher runs the same `vp_browser.py prefs` first.
  3. Launch (Playwright 1.60 on the INSTALLED Google Chrome — the same binary as the sign-in window, so the
     cookie store is encrypted with the same macOS keychain key "Chrome Safe Storage"):
        p.chromium.launch_persistent_context(PROFILE, channel="chrome", headless=False,
            ignore_default_args=["--use-mock-keychain", "--enable-automation"],
            args=["--no-first-run", "--no-default-browser-check",
                  "--disable-blink-features=AutomationControlled",
                  "--window-position=-2400,-2400", "--window-size=1280,900"])
        - ignore --use-mock-keychain: Playwright's default mock keychain cannot decrypt cookies the real
          Chrome wrote (and vice versa) — this flag is what lets the two Chromes share one login.
        - headed, parked off-screen: headless Chrome is blocked by Cloudflare Turnstile (Northwest) and by
          some Google surfaces; a real window at -2400,-2400 never shows on screen.
        - --enable-automation off + AutomationControlled off: no "controlled by automated software" bar,
          navigator.webdriver false (Keycloak / Cloudflare / Google treat the window as a normal browser).
  4. Close NORMALLY: ctx.close() (CDP Browser.close = Chrome's own graceful shutdown; the cookie DB is
     flushed, exit_type written "Normal"). Never SIGKILL the automation Chrome. The sign-in window is quit
     with Cmd-Q, or by ONE SIGTERM to its main process (vp_signin_close.sh) — Chrome records that as
     exit_type "SessionEnded" with exited_cleanly=true; proven equivalent (cookies flushed, restored next launch).
  5. The sign-in window and the scripts never run at the same time (launch() refuses while a copy of the
     profile is open; the launcher quits any copy first).
  6. Restored tabs: with "Continue where you left off" Chrome reopens the last session's tabs on every
     launch; first_page() closes the extras so a script always starts on ONE page.

PROOF RESULTS 2026-10-19 (job 20261019T1040-vp-profile-proof2, no human):
  1a persist-set: headed context, example.com, document.cookie "vp_persist_test=1" (expires -1) + localStorage,
     closed normally -> Default/Cookies row (example.com, vp_persist_test, is_persistent=0).
  1b persist-get (the scripts' exact launch): document.cookie 'vp_persist_test=1' | localStorage '1' -> PASS/PASS.
  2a real quit path: `open -na "Google Chrome" --args --user-data-dir=pw-vp ...` (the launcher's command, test
     tabs httpbin.org + postman-echo.com /cookies/set?vp_quit_test=1 = server-set SESSION cookies), 40 s,
     vp_signin_close.sh (SIGTERM) -> rows for example.com, httpbin.org AND postman-echo.com on disk.
  2b persist-get after that quit: example.com PASS/PASS, httpbin.org ['vp_quit_test=1'],
     postman-echo.com [... 'sails.sid=...', 'vp_quit_test=1']; a second restart: identical.
  Before the fix (job T1025): 1b FAIL, 2b FAIL, localStorage PASS both times.

CLI
  vp_browser.py probe          no browser: profile, cookie/pref files, running copy, prefs state
  vp_browser.py prefs          exit_type Normal (only while that Chrome is closed); prints the startup pref
  vp_browser.py set-startup    "Continue where you left off" via Chrome's settings page (idempotent)
  vp_browser.py pref-dump      what Secure Preferences says (restore_on_startup, MAC keys), exit_type
  vp_browser.py cookie-db      the TEST cookie rows straight from Default/Cookies (is_persistent 0 = session)
  vp_browser.py migrate        pw-cloudcover -> pw-vp (backup copy first); idempotent
  vp_browser.py persist-set    PROOF 1a: headed context on pw-vp, example.com, sets a SESSION cookie
                               (vp_persist_test=1, no expiry) + localStorage key, closes normally
  vp_browser.py persist-get    PROOF 1b / 2b: the scripts' exact launch, reads the cookie + localStorage on
                               example.com (and any cookies on httpbin.org / postman-echo.com, which the
                               real-quit test sets through the `open -na` sign-in window). Prints PASS/FAIL.
  vp_browser.py persist-get --crashed   experiment only: forces exit_type Crashed first (crash-recovery rule)
  vp_browser.py exit-type      prints (profile.exit_type, Secure Preferences restore_on_startup)
Failure policy v3: these helpers never post to Slack; they only print.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
APP_SUPPORT = os.path.join(HOME, "Library/Application Support/valleypawn")
PROFILE = os.path.join(APP_SUPPORT, "pw-vp")
LEGACY_SOURCE = os.path.join(APP_SUPPORT, "pw-cloudcover")      # renamed into PROFILE by `migrate`
LEGACY_OTHERS = [os.path.join(APP_SUPPORT, "pw-gusto"), os.path.join(APP_SUPPORT, "pw-northwest")]
STAMP = "20261019"

CHANNEL = "chrome"
IGNORE_DEFAULT_ARGS = ["--use-mock-keychain", "--enable-automation"]
CHROME_ARGS = ["--no-first-run", "--no-default-browser-check", "--disable-blink-features=AutomationControlled",
               "--window-position=-2400,-2400", "--window-size=1280,900"]
# the one sign-in window (bin/vp_signin_front.sh) — kept here so the tab list has a single home
SIGNIN_TABS = [
    "https://tune.cloudcovermusic.com/#/admin/zones",      # CloudCover (zones dashboard)
    "https://home.google.com/",                            # Google Home — fullcirclepawn@gmail.com (cameras + speakers)
    "https://app.gusto.com/",                              # Gusto — jdavis@fcfpawn.com, tick "Remember this device for 30 days"
    "https://app.northwestregisteredagent.com/",           # Northwest Registered Agent
]


# ---------- process helpers ----------
def running_pids(profile=PROFILE):
    out = subprocess.run(["pgrep", "-f", "--", "--user-data-dir=" + profile], capture_output=True, text=True).stdout
    return [int(x) for x in out.split()]


def is_running(profile=PROFILE):
    return bool(running_pids(profile))


def main_pid(profile=PROFILE):
    out = subprocess.run(["pgrep", "-f", "--", "Google Chrome --user-data-dir=" + profile],
                         capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None


def wait_closed(profile=PROFILE, timeout=25):
    for _ in range(int(timeout)):
        if not is_running(profile):
            return True
        time.sleep(1)
    return not is_running(profile)


# ---------- preferences ----------
def _pref_path(profile=PROFILE):
    return os.path.join(profile, "Default", "Preferences")


def read_prefs(profile=PROFILE):
    p = _pref_path(profile)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p))
    except Exception:
        return None


def prefs(profile=PROFILE):
    """profile.exit_type=Normal + exited_cleanly=true in Default/Preferences — only while closed. Idempotent.
    NOTE (2026-10-19 finding): session.restore_on_startup is a TRACKED pref that lives in Default/Secure
    Preferences with a MAC; a value written into Preferences is ignored by Chrome (and stripped on quit). It is
    set the legitimate way by set_startup_pref() (Chrome's own settings page) and read back by startup_pref()."""
    p = _pref_path(profile)
    if not os.path.exists(p):
        return "no Preferences yet (profile never opened) - nothing to set"
    if is_running(profile):
        return "automation Chrome is open - prefs left alone"
    d = read_prefs(profile)
    if d is None:
        return "Preferences unreadable - left alone"
    if d.get("profile", {}).get("exit_type") == "Normal" and d.get("profile", {}).get("exited_cleanly") is True:
        return "exit_type already Normal | startup pref (Secure Preferences): %s" % startup_pref(profile)
    shutil.copy(p, p + ".bak-" + dt.datetime.now().strftime("%Y%m%d"))
    d.setdefault("profile", {})["exit_type"] = "Normal"
    d["profile"]["exited_cleanly"] = True
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w"))
    os.replace(tmp, p)
    return "exit_type set to Normal | startup pref (Secure Preferences): %s" % startup_pref(profile)


def startup_pref(profile=PROFILE):
    """session.restore_on_startup as Chrome actually honours it (Default/Secure Preferences). 1 = 'Continue where
    you left off' = session cookies survive a restart. None = Chrome default (session cookies dropped at launch)."""
    sp = os.path.join(profile, "Default", "Secure Preferences")
    try:
        return json.load(open(sp)).get("session", {}).get("restore_on_startup")
    except Exception:
        return None


def exit_type(profile=PROFILE):
    d = read_prefs(profile) or {}
    return d.get("profile", {}).get("exit_type"), startup_pref(profile)


SETPREF_JS = """async () => {
  const sp = chrome.settingsPrivate;
  await new Promise(r => sp.setPref('session.restore_on_startup', 1, '', r));
  const p = await new Promise(r => sp.getPref('session.restore_on_startup', r));
  return p && p.value;
}"""


def set_startup_pref(p, profile=PROFILE):
    """ONE short headed session that sets 'Continue where you left off' through Chrome's own settings page
    (chrome://settings/onStartup -> chrome.settingsPrivate.setPref), so Chrome writes the tracked pref + its MAC
    into Secure Preferences itself. Returns the value Chrome reports. `p` = a started sync_playwright."""
    if is_running(profile):
        raise RuntimeError("automation Chrome is already open on %s" % profile)
    ctx = p.chromium.launch_persistent_context(profile, channel=CHANNEL, headless=False,
                                               ignore_default_args=IGNORE_DEFAULT_ARGS, args=list(CHROME_ARGS))
    try:
        page = first_page(ctx)
        page.goto("chrome://settings/onStartup", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        val = None
        try:
            val = page.evaluate(SETPREF_JS)
        except Exception as e:
            print("settingsPrivate failed (%s) - clicking the radio instead" % str(e)[:100])
            page.click('controlled-radio-button[name="1"]', timeout=10000)
            page.wait_for_timeout(1000)
            val = page.evaluate("() => new Promise(r => chrome.settingsPrivate.getPref('session.restore_on_startup', p => r(p && p.value)))")
        page.wait_for_timeout(1500)
    finally:
        close(ctx)
        prefs(profile)
    return val


def ensure_startup_pref(p, profile=PROFILE):
    """Self-heal: if Secure Preferences does not say 1, set it through the settings page once. Returns the state."""
    if startup_pref(profile) == 1:
        return "startup pref already 1"
    v = set_startup_pref(p, profile)
    return "startup pref set via settings page -> chrome reports %r, Secure Preferences now %r" % (v, startup_pref(profile))


# ---------- launch ----------
def headless_from_env(*names):
    """True when any of the named env vars is "1" (per-script escape hatch, e.g. NW_HEADLESS)."""
    return any(os.environ.get(n) == "1" for n in names + ("VP_HEADLESS",))


def launch(p, headless=False, args=(), window_size=None, **kw):
    """The scripts' launch. `p` is a started sync_playwright. Raises RuntimeError when the profile is open."""
    if is_running():
        raise RuntimeError("automation Chrome is already open on %s (sign-in window?)" % PROFILE)
    os.makedirs(PROFILE, exist_ok=True)
    try:
        os.chmod(PROFILE, 0o700)
    except OSError:
        pass
    prefs()
    if startup_pref() != 1:
        print("vp_browser:", ensure_startup_pref(p))
    a = list(CHROME_ARGS)
    if window_size:
        a = [x for x in a if not x.startswith("--window-size=")] + ["--window-size=%d,%d" % tuple(window_size)]
    a += [x for x in args if x not in a]
    return p.chromium.launch_persistent_context(PROFILE, channel=CHANNEL, headless=headless,
                                               ignore_default_args=IGNORE_DEFAULT_ARGS, args=a, **kw)


def first_page(ctx):
    """One page to work on: closes tabs Chrome restored from the last session (restore_on_startup=1)."""
    pages = list(ctx.pages)
    if not pages:
        return ctx.new_page()
    for extra in pages[1:]:
        try:
            extra.close()
        except Exception:
            pass
    return pages[0]


def close(ctx, timeout=25):
    """Normal close (cookies flushed, exit_type Normal), then wait until no process holds the profile."""
    try:
        ctx.close()
    except Exception:
        pass
    return wait_closed(timeout=timeout)


# ---------- CLI ----------
def _sizes(profile=PROFILE):
    out = []
    for f in ("Default/Preferences", "Default/Secure Preferences", "Default/Cookies", "Default/Network/Cookies", "Default/Local Storage/leveldb"):
        q = os.path.join(profile, f)
        if os.path.isdir(q):
            n = sum(os.path.getsize(os.path.join(q, x)) for x in os.listdir(q))
            out.append("  %s  dir %d bytes" % (f, n))
        elif os.path.exists(q):
            out.append("  %s  %d bytes  %s" % (f, os.path.getsize(q), dt.datetime.fromtimestamp(os.path.getmtime(q)).strftime("%m-%d %H:%M:%S")))
        else:
            out.append("  %s  absent" % f)
    return "\n".join(out)


def cmd_probe():
    print("python:", sys.executable)
    try:
        from importlib.metadata import version
        import playwright.sync_api  # noqa
        print("playwright OK", version("playwright"))
    except Exception as e:
        print("playwright MISSING:", type(e).__name__, e)
    for prof in [PROFILE, LEGACY_SOURCE] + LEGACY_OTHERS:
        print("profile:", prof, "exists" if os.path.isdir(prof) else "ABSENT")
        if os.path.isdir(prof):
            print(_sizes(prof))
            print("  exit_type/restore:", exit_type(prof), "| running:", is_running(prof))
    bak = LEGACY_SOURCE + ".bak-" + STAMP
    print("backup copy:", bak, "exists" if os.path.isdir(bak) else "ABSENT")
    return 0


def cmd_migrate():
    """pw-cloudcover -> pw-vp (copy backup first, then rename). Idempotent; refuses while either is open."""
    os.makedirs(APP_SUPPORT, exist_ok=True)
    if is_running(PROFILE) or is_running(LEGACY_SOURCE):
        print("REFUSED: an automation Chrome is open on pw-vp or pw-cloudcover - close it first")
        return 2
    if os.path.isdir(PROFILE):
        print("pw-vp already exists - nothing to migrate")
    elif os.path.isdir(LEGACY_SOURCE):
        bak = LEGACY_SOURCE + ".bak-" + STAMP
        if not os.path.isdir(bak):
            shutil.copytree(LEGACY_SOURCE, bak, symlinks=True)
            print("backup copy:", bak)
        else:
            print("backup copy already present:", bak)
        os.rename(LEGACY_SOURCE, PROFILE)
        print("renamed", LEGACY_SOURCE, "->", PROFILE)
    else:
        os.makedirs(PROFILE, exist_ok=True)
        print("no pw-cloudcover to reuse - created an empty pw-vp")
    os.chmod(PROFILE, 0o700)
    # stale singleton files from a crashed run would make the next Chrome think the profile is in use
    for f in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
        q = os.path.join(PROFILE, f)
        if os.path.islink(q) or os.path.exists(q):
            os.remove(q)
            print("removed stale", f)
    print("prefs:", prefs())
    print(_sizes())
    for prof in LEGACY_OTHERS:
        if os.path.isdir(prof):
            ck = os.path.join(prof, "Default", "Cookies")
            print("legacy", os.path.basename(prof), "left in place (not used any more); Cookies",
                  "%d bytes" % os.path.getsize(ck) if os.path.exists(ck) else "absent")
    return 0


TEST_URL = "https://example.com/"
SET_JS = "() => { document.cookie = 'vp_persist_test=1; path=/'; localStorage.setItem('vp_persist_test', '1'); return [document.cookie, localStorage.getItem('vp_persist_test')]; }"
GET_JS = "() => [document.cookie, localStorage.getItem('vp_persist_test')]"


def _pw():
    from playwright.sync_api import sync_playwright
    return sync_playwright()


def cmd_persist_set():
    print("exit_type/restore before:", exit_type())
    with _pw() as p:
        ctx = launch(p)
        page = first_page(ctx)
        page.goto(TEST_URL, wait_until="domcontentloaded", timeout=60000)
        print("in-page after set:", page.evaluate(SET_JS))
        ck = [c for c in ctx.cookies(TEST_URL) if c["name"] == "vp_persist_test"]
        print("ctx.cookies example.com:", [(c["name"], c["value"], "expires", c.get("expires")) for c in ck])
        page.wait_for_timeout(3000)
        print("closed normally:", close(ctx))
    print("exit_type/restore after:", exit_type())
    print(_sizes())
    return 0


def cmd_pref_dump(profile=PROFILE):
    """What Chrome's tracked-pref protection thinks of session.restore_on_startup (no values of anything else)."""
    d = read_prefs(profile) or {}
    sp = os.path.join(profile, "Default", "Secure Preferences")
    print("Secure Preferences:", "%d bytes" % os.path.getsize(sp) if os.path.exists(sp) else "absent")
    prot = d.get("protection", {})
    macs = prot.get("macs", {})
    print("exit_type/restore:", exit_type(profile), "| exited_cleanly:", d.get("profile", {}).get("exited_cleanly"))
    print("protection.super_mac:", "present" if prot.get("super_mac") else "absent",
          "| macs keys:", sorted(macs.keys())[:12], "| macs.session:", sorted(macs.get("session", {}).keys()) if isinstance(macs.get("session"), dict) else macs.get("session"))
    if os.path.exists(sp):
        try:
            sd = json.load(open(sp))
            sprot = sd.get("protection", {})
            smacs = sprot.get("macs", {})
            print("secure: super_mac", "present" if sprot.get("super_mac") else "absent", "| macs keys:", sorted(smacs.keys())[:12],
                  "| session:", sorted(smacs.get("session", {}).keys()) if isinstance(smacs.get("session"), dict) else smacs.get("session"),
                  "| secure session.restore_on_startup:", sd.get("session", {}).get("restore_on_startup"))
        except Exception as e:
            print("secure prefs unreadable:", type(e).__name__)
    return 0


def cmd_cookie_db(profile=PROFILE):
    """Rows for the TEST cookies only, straight from Default/Cookies (SQLite) — is the session cookie on disk?"""
    import sqlite3
    if is_running(profile):
        print("automation Chrome is open - not reading the DB")
        return 2
    db = os.path.join(profile, "Default", "Cookies")
    if not os.path.exists(db):
        print("no Cookies DB")
        return 1
    tmp = os.path.join(os.path.dirname(db), "Cookies.vpread")
    shutil.copy(db, tmp)
    try:
        con = sqlite3.connect(tmp)
        cols = [r[1] for r in con.execute("PRAGMA table_info(cookies)")]
        want = [c for c in ("host_key", "name", "is_persistent", "has_expires", "expires_utc", "is_secure", "samesite") if c in cols]
        rows = con.execute("SELECT %s FROM cookies WHERE name IN ('vp_persist_test','vp_quit_test') OR host_key LIKE '%%example.com%%'" % ",".join(want)).fetchall()
        n = con.execute("SELECT count(*), sum(is_persistent=0) FROM cookies").fetchone() if "is_persistent" in cols else con.execute("SELECT count(*) FROM cookies").fetchone()
        print("cookie rows total / session-only:", n)
        print("test rows", want, ":", rows)
        con.close()
    finally:
        os.remove(tmp)
    return 0


def cmd_persist_get(crashed=False):
    print("exit_type/restore before:", exit_type())
    ok_cookie = ok_ls = False
    with _pw() as p:
        if crashed:   # experiment: a "Crashed" last exit makes Chrome restore old session cookies regardless of the startup pref
            pp = _pref_path()
            d = read_prefs()
            d.setdefault("profile", {})["exit_type"] = "Crashed"
            d["profile"]["exited_cleanly"] = False
            json.dump(d, open(pp, "w"))
            print("forced exit_type Crashed:", exit_type())
            ctx = p.chromium.launch_persistent_context(PROFILE, channel=CHANNEL, headless=False,
                                                       ignore_default_args=IGNORE_DEFAULT_ARGS, args=list(CHROME_ARGS))
        else:
            ctx = launch(p)
        page = first_page(ctx)
        print("pages at launch (after first_page):", len(ctx.pages))
        page.goto(TEST_URL, wait_until="domcontentloaded", timeout=60000)
        doc_cookie, ls = page.evaluate(GET_JS)
        print("document.cookie:", repr(doc_cookie), "| localStorage:", repr(ls))
        ok_cookie = "vp_persist_test=1" in (doc_cookie or "")
        ok_ls = ls == "1"
        for origin in ("https://httpbin.org/", "https://postman-echo.com/"):
            names = sorted(c["name"] + "=" + c["value"] for c in ctx.cookies(origin))
            print("ctx.cookies", origin, names)
        close(ctx)
    print("RESULT cookie:", "PASS" if ok_cookie else "FAIL", "| localStorage:", "PASS" if ok_ls else "FAIL")
    return 0 if (ok_cookie and ok_ls) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "probe"
    if cmd == "probe":
        return cmd_probe()
    if cmd == "prefs":
        print(prefs())
        return 0
    if cmd == "migrate":
        return cmd_migrate()
    if cmd == "persist-set":
        return cmd_persist_set()
    if cmd == "persist-get":
        return cmd_persist_get(crashed="--crashed" in argv)
    if cmd == "set-startup":
        with _pw() as p:
            print(ensure_startup_pref(p))
        print("exit_type/restore:", exit_type())
        return 0 if startup_pref() == 1 else 1
    if cmd == "pref-dump":
        return cmd_pref_dump()
    if cmd == "cookie-db":
        return cmd_cookie_db()
    if cmd == "exit-type":
        print("exit_type/restore:", exit_type())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
