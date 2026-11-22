#!/usr/bin/env python3
"""vp_browser_host.py — the ALWAYS-ON automation Chrome (2026-11-21, Sign-in Agent project, Joshua approved).

WHY: see the "ALWAYS-ON HOST" block in bin/vp_browser.py. One Chrome on the shared profile
(~/Library/Application Support/valleypawn/pw-vp) stays running off-screen with DevTools on 127.0.0.1:9333,
so checks plug into it instead of fighting over the profile lock, and a sign-in never knocks them out.
It is started the same proven way as the sign-in window (`open -na "Google Chrome" --args --user-data-dir=...`,
the real Chrome binary and keychain = the 10/19 cookie-persistence recipe). Bravo is not involved in any way.

  vp_browser_host.py run          the launchd loop (com.valleypawn.browser-host, KeepAlive). Every 20 s:
                                  lease held by an exclusive run -> stay down; host up -> health check;
                                  3 failed checks in a row -> graceful restart; nothing running -> start.
  vp_browser_host.py ensure       start now (if no exclusive run holds the profile) and wait until it answers
  vp_browser_host.py status       one-line JSON status
  vp_browser_host.py enabled      exit 0 when fleet/state/browser_host/config.json says enabled
  vp_browser_host.py signin URL…  sign-in window: opens the URLs in ONE new window of the host, on screen, in
                                  front. Joshua signs in and closes that window (or Cmd-Q; the loop restarts it).
  vp_browser_host.py selftest     proof, no real site: attach round trip, session cookie survives a host
                                  restart, exclusive (old-style) launch round trip, host comes back. PASS/FAIL.
  vp_browser_host.py sessions     nightly read-only signed-in check (com.valleypawn.browser-sessions, 02:40)
  vp_browser_host.py stop         graceful stop (the loop starts it again unless disabled or leased)

Failure policy v3: never posts to Slack or anywhere; prints, and writes fleet/state/browser_host/status.json
(only when the state changes, or every 15 min).
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_browser as vb  # noqa: E402

STATUS = os.path.join(vb.HOST_STATE_DIR, "status.json")
LOOP_SECONDS = 20
HUNG_AFTER = 3
STATUS_EVERY = 900


def log(*a):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def write_status(**kw):
    kw["at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        os.makedirs(vb.HOST_STATE_DIR, exist_ok=True)
        tmp = STATUS + ".tmp"
        with open(tmp, "w") as f:
            json.dump(kw, f, indent=1)
        os.replace(tmp, STATUS)
    except Exception as e:
        log("status write failed:", e)
    return kw


def _get(path, method="GET", timeout=5):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (vb.DEBUG_PORT, path), method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode() or "null"
    try:
        return json.loads(body)
    except ValueError:
        return body


def tidy():
    """Right after the host starts: close the tabs Chrome restored from its last session, keep one."""
    try:
        pages = [t for t in _get("/json/list") if t.get("type") == "page"]
    except Exception:
        return 0
    n = 0
    for t in pages[1:]:
        try:
            _get("/json/close/%s" % t["id"])
            n += 1
        except Exception:
            pass
    return n


def start():
    if vb.lease_active():
        return "LEASED"
    if vb.is_running():
        return "BUSY"
    vb.prefs()
    if vb.startup_pref() != 1:
        subprocess.run([sys.executable, vb.__file__, "set-startup"], timeout=180)
    if vb.lease_active() or vb.is_running():
        return "BUSY"
    subprocess.run(["open", "-na", "Google Chrome", "--args", "--user-data-dir=" + vb.PROFILE,
                    "--remote-debugging-port=%d" % vb.DEBUG_PORT] + vb.HOST_ARGS + ["about:blank"], timeout=60)
    for _ in range(45):
        if vb.host_alive():
            time.sleep(2)
            log("host started; closed %d restored tab(s)" % tidy())
            return "STARTED"
        time.sleep(1)
    return "NO_ANSWER"


def stop():
    """Graceful: CDP Browser.close (Cmd-Q path). Fallback ONE SIGTERM (SessionEnded, cookies kept)."""
    if not vb.host_pids():
        return "NOT_RUNNING"
    r = vb.cdp_close()
    if r in ("CLOSED", "NOT_RUNNING"):
        return r
    for pid in vb.host_pids():
        try:
            os.kill(pid, 15)
        except OSError:
            pass
    return "CLOSED" if vb.wait_closed(timeout=60) else "STILL_RUNNING"


def restart():
    r = stop()
    if r == "STILL_RUNNING":
        # hung for 60+ s after a SIGTERM: last resort, only the host's own processes on PROFILE
        for pid in vb.running_pids():
            try:
                os.kill(pid, 9)
            except OSError:
                pass
        vb.wait_closed(timeout=20)
        log("host was hung; force-stopped")
    time.sleep(2)
    return start()


def ensure(wait_lease=300):
    t0 = time.time()
    while vb.lease_active() and time.time() - t0 < wait_lease:
        time.sleep(5)
    if vb.host_alive():
        return "UP"
    r = start()
    return "UP" if vb.host_alive() else r


def run():
    log("browser host loop starting (pid %d)" % os.getpid())
    fails, last, last_write = 0, None, 0
    while True:
        try:
            if not vb.host_config().get("enabled"):
                st = "DISABLED"
            elif vb.lease_active():
                st, fails = "PAUSED_FOR_EXCLUSIVE_RUN", 0
            elif vb.host_pids():
                if vb.host_alive():
                    st, fails = "UP", 0
                else:
                    fails += 1
                    st = "NOT_ANSWERING"
                    if fails >= HUNG_AFTER:
                        st, fails = "RESTARTED:" + restart(), 0
            elif vb.is_running():
                st = "BUSY_OTHER_COPY"
            else:
                st = "START:" + start()
        except Exception as e:
            st = "LOOP_ERROR:" + type(e).__name__
            log("loop error:", repr(e)[:300])
        if st != last or time.time() - last_write > STATUS_EVERY:
            if st != last:
                log(st)
            write_status(state=st, host_pids=vb.host_pids(), lease=vb.lease_active())
            last, last_write = st, time.time()
        time.sleep(LOOP_SECONDS)


def signin(urls):
    r = ensure()
    if r != "UP":
        print("host not up:", r)
        return 1
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % vb.DEBUG_PORT, timeout=20000)
        s = b.new_browser_cdp_session()
        first = s.send("Target.createTarget", {"url": urls[0], "newWindow": True})
        try:
            w = s.send("Browser.getWindowForTarget", {"targetId": first["targetId"]})
            s.send("Browser.setWindowBounds", {"windowId": w["windowId"], "bounds": {"windowState": "normal"}})
            s.send("Browser.setWindowBounds", {"windowId": w["windowId"],
                                               "bounds": {"left": 80, "top": 60, "width": 1400, "height": 950}})
        except Exception as e:
            print("window placement:", type(e).__name__)
        for u in urls[1:]:
            s.send("Target.createTarget", {"url": u})     # into the window just created (it has focus)
        s.send("Target.activateTarget", {"targetId": first["targetId"]})
        b.close()
    for pid in vb.host_pids():
        subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of '
                        '(first process whose unix id is %d) to true' % pid], capture_output=True)
    print("sign-in window open in the always-on automation browser (%d tab(s)). Sign in, then close that "
          "window; the checks keep running the whole time." % len(urls))
    return 0


def selftest():
    """No real site. Forces the host on for the test only (config untouched), then puts things back."""
    results = []
    enabled_before = bool(vb.host_config().get("enabled"))
    vb.host_config = lambda: {"enabled": True, "attach": [os.path.basename(sys.argv[0])]}
    from playwright.sync_api import sync_playwright

    def ok(name, cond, detail=""):
        results.append((name, bool(cond)))
        print("%-34s %s %s" % (name, "PASS" if cond else "FAIL", detail), flush=True)

    r = ensure()
    ok("1 host starts / answers", r == "UP", r)
    with sync_playwright() as p:
        try:
            ctx = vb.launch(p, window_size=(1400, 1000))
            pg = vb.first_page(ctx)
            pg.goto("https://example.com/", timeout=30000)
            pg.evaluate("document.cookie='vp_host_test=1; path=/'")
            ok("2 attach + page", getattr(ctx, "shared", False) and "Example" in pg.title(), pg.title())
            vb.close(ctx)
            ok("3 detach leaves host up", vb.host_alive())
        except Exception as e:
            ok("2 attach + page", False, repr(e)[:200])
    ok("4 graceful host stop", stop() in ("CLOSED", "NOT_RUNNING"))
    ok("5 host restarts", start() == "STARTED")
    with sync_playwright() as p:
        try:
            ctx = vb.launch(p)
            pg = vb.first_page(ctx)
            pg.goto("https://example.com/", timeout=30000)
            ck = pg.evaluate("document.cookie")
            ok("6 session cookie survived restart", "vp_host_test=1" in ck, ck)
            vb.close(ctx)
        except Exception as e:
            ok("6 session cookie survived restart", False, repr(e)[:200])
    vb.host_config = lambda: {"enabled": True, "attach": []}        # now behave like a non-listed script
    with sync_playwright() as p:
        try:
            ctx = vb.launch(p)
            excl = not getattr(ctx, "shared", False) and not vb.host_alive() and vb.lease_active()
            pg = vb.first_page(ctx)
            pg.goto("https://example.com/", timeout=30000)
            ck = pg.evaluate("document.cookie")
            ok("7 exclusive run (old-style launch)", excl and "vp_host_test=1" in ck, ck)
            vb.close(ctx)
            ok("8 lease handed back", not vb.lease_active())
        except Exception as e:
            ok("7 exclusive run (old-style launch)", False, repr(e)[:200])
    if enabled_before:
        ok("9 host back up", ensure() == "UP")
    else:
        ok("9 host stopped again (config disabled)", stop() in ("CLOSED", "NOT_RUNNING") and not vb.is_running())
    bad = [n for n, good in results if not good]
    print("SELFTEST", "PASS" if not bad else "FAIL: " + ", ".join(bad))
    return 0 if not bad else 1


# ---------- nightly session check (2026-11-21) ----------
LEDGER = os.path.join(vb.HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
SESSIONS = os.path.join(vb.HOST_STATE_DIR, "sessions.json")
DEFAULT_SITES = [
    {"name": "Cloud Cover", "url": "https://tune.cloudcovermusic.com/#/admin/zones"},
    {"name": "Google Home (fullcirclepawn@gmail.com)", "url": "https://home.google.com/"},
    {"name": "Chekkit", "url": "https://dashboard.chekkit.io/reviews"},
]
_OUT = re.compile(r"(/login|/signin|sign-in|accounts\.google\.com|/auth/|#/login)", re.I)


def sessions():
    """Read-only: load each site's signed-in page in the host and record whether it is still signed in.
    A site that flips to signed-out gets ONE [SIGN-IN] failure-ledger row (fleet-guardian holds it for Login
    Day). Loading the page also keeps sliding sessions fresh. Never types anything, never clicks."""
    sites = vb.host_config().get("sessions") or DEFAULT_SITES
    try:
        prev = json.load(open(SESSIONS))
    except Exception:
        prev = {}
    if ensure() != "UP":
        print("host not up; nothing checked")
        return 1
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        ctx = vb.attach(p)
        pg = ctx.new_page()
        for s in sites:
            try:
                pg.goto(s["url"], timeout=45000, wait_until="domcontentloaded")
                pg.wait_for_timeout(8000)
                r = pg.evaluate("() => ({url: location.href, pw: [...document.querySelectorAll("
                                "'input[type=password]')].some(e => e.offsetParent !== null)})")
                signed_in = not (r["pw"] or _OUT.search(r["url"]))
                out[s["name"]] = {"signed_in": signed_in, "url": r["url"][:200]}
            except Exception as e:
                out[s["name"]] = {"signed_in": None, "error": type(e).__name__}
            print("%-40s %s" % (s["name"], out[s["name"]]), flush=True)
        ctx.close()
    now = time.strftime("%Y-%m-%d %H:%M")
    for name, r in out.items():
        was = (prev.get(name) or {}).get("signed_in")
        if r.get("signed_in") is False and was is not False:
            row = ("| %s ET (native) | browser-sessions | [SIGN-IN] %s is signed out in the always-on automation "
                   "browser (found by the nightly session check, before any task failed). Sign in once with "
                   "bin/vp_signin_front.sh and tick remember this device. | NEEDS_HUMAN: yes | OPEN |\n" % (now, name))
            try:
                with open(LEDGER, "a") as f:
                    f.write(row)
            except Exception as e:
                print("ledger write failed:", e)
        r["checked"] = now
    tmp = SESSIONS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
    os.replace(tmp, SESSIONS)
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "run":
        run()
        return 0
    if cmd == "ensure":
        r = ensure()
        print(r)
        return 0 if r == "UP" else 1
    if cmd == "status":
        print(json.dumps({"enabled": bool(vb.host_config().get("enabled")), "alive": vb.host_alive(),
                          "host_pids": vb.host_pids(), "lease": vb.lease_active(),
                          "attach": vb.host_config().get("attach", [])}))
        return 0
    if cmd == "enabled":
        return 0 if vb.host_config().get("enabled") else 1
    if cmd == "signin":
        return signin(argv[2:] or vb.SIGNIN_TABS)
    if cmd == "selftest":
        return selftest()
    if cmd == "sessions":
        return sessions()
    if cmd == "stop":
        print(stop())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
