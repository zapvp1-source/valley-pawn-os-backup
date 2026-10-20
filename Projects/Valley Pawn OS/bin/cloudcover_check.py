#!/usr/bin/env python3
"""cloudcover_check.py — native replacement for Cowork `daily-cloudcover-check` (Mon-Sat 10:25 ET ->
#general C03BETSS669; Wednesday = Culpeper + Roanoke only). Built 2026-10-14 (Mac-first).

WHY: the cloud copy (trig_017ef3AnQBKcnqSdKUztYWLA) has no Chrome on the Mac, so it posted 5 h late on
10/13 and nothing on 10/14. This reads the same data on the Mac.

HOW (no screen, never types a password):
  1 Opens the ONE shared automation profile ~/Library/Application Support/valleypawn/pw-vp in the installed
    Google Chrome through bin/vp_browser.py (2026-10-19: a real window parked off-screen, real keychain; the
    recipe whose sign-in persistence is proven in vp_browser.py's docstring). That profile is signed in ONCE
    by Joshua with bin/vp_signin_front.sh. Not signed in -> ONE ledger row, nothing posted, stop.
    CC_HEADLESS=1 forces headless for experiments.
  2 CloudCover status from CloudCover's own JSON API — the same two calls the zones dashboard makes
    (found 2026-10-14 from the dashboard's network calls): GET api.cloudcovermusic.com/streams/enhanced
    (zones, header Authorization = the session's "Authorization" cookie) and
    GET /device-state/device/list?ids=<deviceids> (now playing; header Authorization = "Token" cookie).
    The cookies are read from the profile in memory only — never logged, never written anywhere.
    Streaming = state "playing" AND the player reported within the last 20 min (the dashboard shows a
    zone whose last report is stale as not streaming: 10/14 Harrisonburg "playing" since 01:20 UTC =
    dashboard grey). The dashboard DOM is also read with the SKILL's own extractor as a cross-check;
    a disagreement is logged (the API value is used).
  3 Speaker volume: each store's Google Home devices page (fullcirclepawn@gmail.com, same profile),
    5 s wait, the SKILL's regex `Volume (\\d+)%`, no clicks. Missing -> "🔊 —" (the SKILL's rule). If
    Google is not signed in at all, the post still goes out with dashes and ONE ledger row asks for the
    one-time Google sign-in.
  4 Post the SKILL's exact format to #general (dedupe: today's header already there = no repost).
    After 13:25 ET (the scorecard's grace) it does NOT post a stale "10:00 AM" snapshot: ledger row.

  cloudcover_check.py --render [--date D] [--from-capture FILE]   prints the post, writes/posts nothing
  cloudcover_check.py --send                                       (launchd wrapper; gated by vp_live.sh)
Failure policy v3: one FAILURE_LEDGER row, never a DM, never a failure note in #general.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

AGENT = "daily-cloudcover-check"
ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "state", "cloudcover")
import vp_browser  # the one automation profile + launch recipe (2026-10-19)
PROFILE = vp_browser.PROFILE
CH = "C03BETSS669"
API = "https://api.cloudcovermusic.com"
ZONES_URL = "https://tune.cloudcovermusic.com/#/admin/zones"
STALE_MIN = 20
POST_CUTOFF = (13, 25)
# dashboard order (by CloudCover location username) — the order of every live post
ALL5 = [("Harrisonburg", "Harrisonburg"), ("Lexington1", "Lexington"), ("Roanoke1", "Roanoke"),
        ("SandiPepper", "Culpeper"), ("Waynesboro1", "Waynesboro")]
WED = [("SandiPepper", "Culpeper"), ("Roanoke1", "Roanoke"), ("Waynesboro1", "Waynesboro")]  # Wed: CUL, ROA + WAY (6-day week from 10/14, Joshua 10/14)
HOMES = {
    "Harrisonburg": "1-a4ed529501c13a26764e6df9f4d6508e4fc88e0bb25ec02a61d87597442fbba2",
    "Lexington": "1-f6f4392e095ca9169d3e5c4e8dfaec55b7587a28744cbf0af20b30009648bd3d",
    "Culpeper": "1-8567d747ce9987f177a24524772591264b3b242f5f709024934038bc65ce80e6",
    "Roanoke": "1-4dcee6f564dd8273f312795185b5653a829b69f2b13c1df0bd77e73864ab4d42",
    "Waynesboro": "1-db0b52f0fc4e4447696f44c382c5ab0664e57f19fee97ebdbb62f664236f85cc",
}
DOM_JS = """() => {
  const knownBrowsers = ['Chrome', 'MS-Edge-Chromium', 'Firefox', 'Safari'];
  return Array.from(document.querySelectorAll('app-zones-table-row')).map(row => {
    const locEl = row.querySelector('.location-username'); if (!locEl) return null;
    const k = locEl.innerText.trim();
    const lines = row.innerText.trim().split('\\n').map(l => l.trim()).filter(l => l.length > 0);
    const f = lines.filter(l => l !== k && l !== 'Zone 1' && !knownBrowsers.includes(l));
    return {location: k, streaming: !!row.querySelector('.text-success'), song: f[0] || null,
            artist: f[1] || null, playlist: f.slice(2).join(' ') || null};
  }).filter(Boolean);
}"""

RENDER = "--render" in sys.argv


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def log(*a):
    print(dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def ledger(sentence, needs="no"):
    if RENDER:
        log("[render] would write ledger row:", sentence, "| NEEDS_HUMAN:", needs)
        return
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, needs))
    log("LEDGER:", sentence)


def once_per_day(key):
    """True the first time `key` is seen today (so a sign-in ask is one ledger row a day, not one per run)."""
    if RENDER:
        return True
    os.makedirs(STATE, exist_ok=True)
    p = os.path.join(STATE, "%s-%s" % (key, dt.datetime.now(ET).date()))
    if os.path.exists(p):
        return False
    open(p, "w").close()
    return True


def stores_for(day):
    wd = day.weekday()
    if wd == 6:
        return []
    return WED if wd == 2 else ALL5


def api_get(path, auth):
    req = urllib.request.Request(API + path, headers={"Authorization": auth, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def parse_ts(s):
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def zones_from_api(streams, states, now_utc):
    """-> {location_username: {streaming, song, artist, playlist}} built from the two API payloads."""
    by_stream = {d.get("streamid"): d for d in states}
    out = {}
    for s in streams:
        d = by_stream.get(s.get("streamid")) or {}
        m = d.get("media") or {}
        last = parse_ts(d.get("lastUpdate") or "")
        fresh = last is not None and (now_utc - last) <= dt.timedelta(minutes=STALE_MIN)
        rotation = "Off" if not s.get("crossfade_enabled") else "On"
        pl = ("%s Rotation %s" % (m.get("playlist"), rotation)) if m.get("playlist") else None
        out[s.get("username")] = {"streaming": d.get("state") == "playing" and fresh,
                                  "song": m.get("title"), "artist": m.get("artist"), "playlist": pl,
                                  "last_update": d.get("lastUpdate"), "state": d.get("state")}
    return out


def build_post(day, stores, zones, vols):
    wed = day.weekday() == 2
    head = "🎵 *Cloud Cover Music Check — %s, %s %d, %d @ 10:00 AM*" % (
        day.strftime("%A"), day.strftime("%B"), day.day, day.year)
    lines, down = [], 0
    for key, name in stores:
        z = zones.get(key) or {}
        v = vols.get(name)
        spk = ("🔊 Speaker %s%%" % v) if v else "🔊 —"
        if z.get("streaming") and z.get("song"):
            pl = " _(%s)_" % z["playlist"] if z.get("playlist") else ""
            lines.append('🟢 *%s* — "%s" · %s%s | %s' % (name, z["song"], z.get("artist") or "", pl, spk))
        else:
            down += 1
            lines.append("🔴 *%s* — NOT STREAMING ⚠️ | %s" % (name, spk))
    if down == 0:
        status = "✅ All open stores streaming" if wed else "✅ All locations streaming"
    else:
        status = ("🚨 %d store(s) NOT streaming" if wed else "🚨 %d location(s) NOT streaming") % down
    return "%s\n\n%s\n\n%s" % (head, status, "\n".join(lines)), head


def read_live(day, stores):
    """Playwright pass over the dedicated profile. Returns (zones, vols, dom, notes) or raises SystemExit."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ledger("The Cloud Cover music check could not run because the automation browser is not installed on the Mac.",
               "no")
        sys.exit(3)
    notes, vols, dom = [], {}, []
    with sync_playwright() as p:
        try:
            ctx = vp_browser.launch(p, headless=vp_browser.headless_from_env("CC_HEADLESS"))
        except Exception as e:
            log("launch failed:", str(e)[:300])
            ledger("The Cloud Cover music check could not open its automation browser (it may be open for sign-in), so nothing was posted.")
            sys.exit(3)
        try:
            page = vp_browser.first_page(ctx)
            page.goto(ZONES_URL, wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_selector("app-zones-table-row, input[type=password]", timeout=30000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            if "--diag" in sys.argv:
                log("diag pre-check url:", page.url.split("?")[0], "| pw field:", bool(page.query_selector("input[type=password]")),
                    "| cookie domains:", sorted({c["domain"] for c in ctx.cookies()})[:20])
            if "/login" in page.url or page.query_selector("input[type=password]"):
                if once_per_day("signin-cloudcover"):
                    ledger("CloudCover needs a one-time sign-in in the automation browser",
                           "yes, run bin/vp_signin_front.sh and sign in to CloudCover once in that window, then quit it")
                sys.exit(4)
            ck = {c["name"]: c["value"] for c in ctx.cookies("https://tune.cloudcovermusic.com")}
            if "--diag" in sys.argv:   # names only, never values
                log("diag url:", page.url.split("?")[0], "| pw field:", bool(page.query_selector("input[type=password]")),
                    "| tune cookies:", sorted(ck), "| all cookie domains:",
                    sorted({c["domain"] for c in ctx.cookies()})[:15])
            auth, tok = ck.get("Authorization"), ck.get("Token")
            if auth:
                auth = urllib.parse.unquote(auth)
            if not auth or not tok:
                if once_per_day("signin-cloudcover"):
                    ledger("CloudCover needs a one-time sign-in in the automation browser",
                           "yes, run bin/vp_signin_front.sh and sign in to CloudCover once in that window, then quit it")
                sys.exit(4)
            try:
                dom = page.evaluate(DOM_JS)
            except Exception as e:
                notes.append("dom read failed: %s" % str(e)[:120])
            streams = api_get("/streams/enhanced?page=1", auth).get("streams") or []
            ids = [str(s["deviceid"]) for s in streams if s.get("deviceid")]
            states = api_get("/device-state/device/list?ids=" + ",".join(ids), urllib.parse.unquote(tok)).get("DeviceState") or []
            zones = zones_from_api(streams, states, dt.datetime.now(dt.timezone.utc))
            # Google Home speaker volumes (no clicks — the SKILL's rule)
            google_out = 0
            for _key, name in stores:
                v = None
                for u in ("1", "0"):
                    try:
                        page.goto("https://home.google.com/u/%s/home/%s/devices" % (u, HOMES[name]),
                                  wait_until="domcontentloaded", timeout=45000)
                        page.wait_for_timeout(5000)
                        if "accounts.google.com" in page.url:
                            google_out += 1
                            continue
                        m = re.search(r"Volume (\d+)%", page.inner_text("body"))
                        if m:
                            v = m.group(1)
                            break
                    except Exception as e:
                        notes.append("home %s u/%s: %s" % (name, u, str(e)[:80]))
                vols[name] = v
            if google_out >= 2 * len(stores) and once_per_day("signin-google"):
                ledger("The Cloud Cover music check posted without speaker volumes because Google Home needs a one-time sign-in in the automation browser",
                       "yes, run bin/vp_signin_front.sh and sign in to Google as fullcirclepawn@gmail.com once in that window, then quit it")
        finally:
            vp_browser.close(ctx)
    return zones, vols, dom, notes


def cross_check(dom, zones, stores):
    diffs = []
    dmap = {d.get("location"): d for d in dom or []}
    for key, name in stores:
        d, z = dmap.get(key), zones.get(key) or {}
        if d is None:
            continue
        if bool(d.get("streaming")) != bool(z.get("streaming")):
            diffs.append("%s streaming dom=%s api=%s (last report %s)" % (name, d.get("streaming"), z.get("streaming"), z.get("last_update")))
        elif d.get("streaming") and (d.get("song") != z.get("song") or d.get("playlist") != z.get("playlist")):
            diffs.append("%s now-playing dom=%r/%r api=%r/%r (song changed between reads?)"
                         % (name, d.get("song"), d.get("playlist"), z.get("song"), z.get("playlist")))
    return diffs


def main():
    now = dt.datetime.now(ET)
    day = dt.date.fromisoformat(arg("--date")) if arg("--date") else now.date()
    stores = stores_for(day)
    if not stores:
        log("Sunday — no stores open, nothing to check")
        return 0
    cap = arg("--from-capture")
    if cap:
        c = json.load(open(cap))
        at = parse_ts(c["captured_utc"])
        zones = zones_from_api(c["streams"], c["device_state"], at)
        vols, dom, notes = c.get("google_home_volume", {}), c.get("dashboard_dom", []), ["from capture %s" % c["captured_utc"]]
    else:
        if not RENDER and (now.hour, now.minute) > POST_CUTOFF and day == now.date():
            ledger("The Cloud Cover music check did not run until after %d:%02d, so the 10 AM post was skipped rather than sent late." % POST_CUTOFF)
            return 0
        zones, vols, dom, notes = read_live(day, stores)
    for d in cross_check(dom, zones, stores):
        log("CROSS-CHECK:", d)
    for n in notes:
        log("note:", n)
    post, head = build_post(day, stores, zones, vols)
    missing = [name for key, name in stores if key not in zones]
    if missing:
        ledger("The Cloud Cover music check could not find %s on the dashboard, so nothing was posted." % ", ".join(missing))
        print(post)
        return 2
    if RENDER:
        print(post)
        log("[render] nothing posted")
        return 0
    marker = head.replace("🎵 ", "").strip("*").split(" @ ")[0]   # "Cloud Cover Music Check — Wednesday, October 14, 2026"
    env = dict(os.environ, VP_TASK=AGENT)
    h = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, marker, "20"],
                       capture_output=True, text=True, env=env)
    if h.returncode == 0:
        log("already posted today — not posting again")
        return 0
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post],
                       capture_output=True, text=True, env=env)
    if p.returncode != 0:
        ledger("The Cloud Cover music check ran but its #general post did not go through.")
        log("FAIL post:", (p.stderr or p.stdout).strip()[:200])
        return 1
    log("posted", p.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
