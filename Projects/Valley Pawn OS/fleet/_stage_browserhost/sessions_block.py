

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
