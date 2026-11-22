
# ---------- ALWAYS-ON HOST (2026-11-21, Sign-in Agent project; Joshua approved the build 2026-11-21) ----------
# WHY: 60 of the 97 "sign-in" failures 10/15-11/20 were not logouts. They were a check refusing to start because
# another copy of this profile was already open (the sign-in window, another check, or a hung Chrome) — launch()
# below raises "already open". bin/vp_browser_host.py now keeps ONE Chrome on PROFILE running all the time
# (launchd agent com.valleypawn.browser-host, off-screen, DevTools on 127.0.0.1:DEBUG_PORT, restarts itself).
#   * Scripts named in fleet/state/browser_host/config.json "attach" plug into that Chrome (attach()) and get
#     their own off-screen window — no profile lock, any number at once, sign-in window never knocks them out.
#   * Every other script (money scripts, downloads, special flags) runs EXACTLY as before, in "exclusive" mode:
#     it takes the lease file (the host stays down while the lease's pid is alive), closes the host gracefully
#     (CDP Browser.close = Cmd-Q path, cookies flushed), launches its own copy, and close() hands the profile
#     back. Same Chrome binary, same profile, same recipe as the 10/19 persistence proofs.
#   * config "enabled": false (or no config file) = this whole block is inert and launch() is the old launch().
#   * VP_BROWSER_LEGACY=1 forces the old path for one run.
HOST_STATE_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/state/browser_host")
HOST_CONFIG = os.path.join(HOST_STATE_DIR, "config.json")
HOST_LEASE = os.path.join(APP_SUPPORT, "pw-vp.lease")
LEASE_MAX_AGE = 3 * 3600
# flags the host Chrome runs with (bin/vp_browser_host.py); an attaching script may ask for these and no others
HOST_ARGS = CHROME_ARGS[:2] + ["--disable-blink-features=AutomationControlled",
             "--disable-background-timer-throttling", "--disable-backgrounding-occluded-windows",
             "--disable-renderer-backgrounding", "--disable-ipc-flooding-protection", "--disable-hang-monitor",
             "--disable-popup-blocking", "--disable-prompt-on-repost", "--disable-search-engine-choice-screen",
             "--autoplay-policy=no-user-gesture-required", "--mute-audio",
             "--window-position=-2400,-2400", "--window-size=1400,1000"]
_LEASE_MINE = False


def host_config():
    try:
        with open(HOST_CONFIG) as f:
            c = json.load(f)
        return c if isinstance(c, dict) else {}
    except Exception:
        return {}


def host_pids(profile=PROFILE, port=DEBUG_PORT):
    """Main Chrome process on PROFILE that has the DevTools port open (the host, or the old sign-in window)."""
    out = subprocess.run(["pgrep", "-f", "--", "--user-data-dir=" + profile], capture_output=True, text=True).stdout
    pids = []
    for pid in out.split():
        cmd = subprocess.run(["ps", "-o", "command=", "-p", pid], capture_output=True, text=True).stdout
        if "--type=" not in cmd and ("--remote-debugging-port=%d" % port) in cmd:
            pids.append(int(pid))
    return pids


def host_alive(port=DEBUG_PORT, timeout=3):
    """True when the DevTools endpoint answers AND it belongs to Chrome on PROFILE (never Joshua's own Chrome)."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=timeout) as r:
            ok = r.status == 200 and "Browser" in json.loads(r.read().decode() or "{}")
    except Exception:
        return False
    return ok and bool(host_pids(port=port))


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


def lease_active():
    """Someone is running the profile in exclusive mode: host must stay down."""
    try:
        with open(HOST_LEASE) as f:
            d = json.load(f)
    except Exception:
        return False
    if time.time() - float(d.get("since", 0)) > LEASE_MAX_AGE or not _pid_alive(d.get("pid")):
        return False
    return True


def lease_take(who=None):
    global _LEASE_MINE
    os.makedirs(APP_SUPPORT, exist_ok=True)
    tmp = HOST_LEASE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"pid": os.getpid(), "since": time.time(),
                   "who": who or os.path.basename(sys.argv[0] or "?")}, f)
    os.replace(tmp, HOST_LEASE)
    if not _LEASE_MINE:
        import atexit
        atexit.register(lease_release)
    _LEASE_MINE = True


def lease_release():
    """Only removes the lease if it is ours (another exclusive run may have taken it since)."""
    global _LEASE_MINE
    if not _LEASE_MINE:
        return
    try:
        with open(HOST_LEASE) as f:
            d = json.load(f)
        if int(d.get("pid", -1)) == os.getpid():
            os.remove(HOST_LEASE)
    except Exception:
        pass
    _LEASE_MINE = False


def _make_room_for_exclusive():
    """Exclusive mode: hold the lease, then close the host gracefully so the old launch can have the profile."""
    lease_take()
    if host_pids():
        r = cdp_close()
        print("vp_browser: host stepped aside for exclusive run:", r)
        if r not in ("CLOSED", "NOT_RUNNING"):
            for pid in host_pids():
                try:
                    os.kill(pid, 15)        # ONE SIGTERM = "SessionEnded", cookies kept (10/19 proof)
                except OSError:
                    pass
            wait_closed(timeout=30)
    time.sleep(1)


class SharedContext:
    """What attach() returns. Looks like the BrowserContext the scripts already use, but only ever shows and
    closes the pages THIS script opened; close() just disconnects (the host Chrome keeps running)."""
    shared = True

    def __init__(self, browser, ctx, window_size=None, viewport=None):
        self._browser, self._ctx, self._own = browser, ctx, []
        self._size = tuple(window_size) if window_size else (1400, 1000)
        self._viewport = viewport

    @property
    def pages(self):
        return [pg for pg in self._own if not pg.is_closed()]

    def new_page(self):
        pg = None
        try:        # own window, parked off-screen, so the tab is never a throttled background tab
            s = self._browser.new_browser_cdp_session()
            with self._ctx.expect_page(timeout=15000) as info:
                t = s.send("Target.createTarget", {"url": "about:blank", "newWindow": True, "background": True})
            pg = info.value
            try:
                w = s.send("Browser.getWindowForTarget", {"targetId": t["targetId"]})
                s.send("Browser.setWindowBounds", {"windowId": w["windowId"], "bounds": {
                    "left": -2400, "top": -2400, "width": self._size[0], "height": self._size[1]}})
            except Exception:
                pass
            try:
                s.detach()
            except Exception:
                pass
        except Exception as e:
            print("vp_browser: own-window page failed (%s); using a tab" % type(e).__name__)
            pg = self._ctx.new_page()
        if self._viewport:
            try:
                pg.set_viewport_size(self._viewport)
            except Exception:
                pass
        self._own.append(pg)
        return pg

    def close(self):
        for pg in self._own:
            try:
                if not pg.is_closed():
                    pg.close()
            except Exception:
                pass
        try:
            self._browser.close()     # connect_over_cdp: disconnects only; the host Chrome stays up
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._ctx, name)


def attach(p, window_size=None, viewport=None, wait=45):
    """Connect to the always-on host Chrome. Raises if it is not there within `wait` seconds."""
    t0 = time.time()
    while not host_alive():
        if time.time() - t0 > wait:
            raise RuntimeError("browser host not answering on 127.0.0.1:%d" % DEBUG_PORT)
        time.sleep(3)
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % DEBUG_PORT, timeout=20000)
    if not browser.contexts:
        browser.close()
        raise RuntimeError("browser host has no default context")
    print("vp_browser: attached to browser host")
    return SharedContext(browser, browser.contexts[0], window_size, viewport)


def _attach_allowed(cfg, args, kw):
    me = os.path.basename(sys.argv[0] or "")
    if os.environ.get("VP_BROWSER_LEGACY") == "1" or me not in (cfg.get("attach") or []):
        return False
    if any(a not in HOST_ARGS for a in args):
        return False
    return set(kw) <= {"viewport"}
