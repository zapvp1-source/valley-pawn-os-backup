#!/usr/bin/env python3
"""dress_code_check.py — native replacement for Cowork `daily-dress-code-check` (Mon-Sat 10:30 ET ->
#general C03BETSS669; Wednesday = Culpeper + Roanoke + Waynesboro). Built 2026-10-18 (Mac-first).

WHY: the Cowork copy died Sat 10/17 on the account's weekly usage limit before its first tool call, and
before that it depended on the Claude-in-Chrome extension + a Google passkey prompt it could not clear
(ledger rows 10/7, 10/8). A native agent reads the cameras itself and cannot be taken out by that limit.

HOW (Playwright on the installed Google Chrome; never types a password; never a screenshot of anything but
its own automation window):
  1 Opens the ONE shared automation profile ~/Library/Application Support/valleypawn/pw-vp through
    bin/vp_browser.py (2026-10-19), where Joshua signed in ONCE as fullcirclepawn@gmail.com (the camera
    account) with bin/vp_signin_front.sh. A real Chrome window parked off-screen (headless Chrome is blocked
    on some Google surfaces and may not paint <video>); DC_HEADLESS=1 forces headless for experiments.
    - Google sign-in page instead of the home -> ONE ledger row a day
      ("Google Home needs a one-time sign-in in the automation browser"), nothing posted, stop.
  2 For each open store (bin/vp_lib.sh open_stores: Sun none, Wed CUL+ROA+WAY, else all 5): the store's
    Google Home camera page (home ids = the HOMES dict shared with cloudcover_check.py), waits for the live
    tiles to start, screenshots the grid + every camera tile -> fleet/state/dress_code/<date>/<store>.png
    (and <store>-cam<N>.png). Offline / "camera off" / no tile at all is recorded as NOT SEEN.
  3 Assesses each store's snapshots with Claude vision (bin/vp_ai.py, claude-sonnet-5-5) against the SKILL's
    rules: only people BEHIND the counter / at workstations are employees; any collared shirt, polo or
    jacket in ANY colour is compliant; outerwear over the shirt is compliant; unclear = compliant; nobody
    visible = compliant; flag only at >= 90 % confidence. The model is also asked whether it actually
    saw a live feed — a black, offline or loading tile never becomes "All in dress code".
  4 Posts the SKILL's exact format to #general (dedupe: today's header already there = no repost):
      :camera: Dress Code Check — Monday, October 19, 2026 @ 10:31 AM
      • Harrisonburg — :white_check_mark: All in dress code
      • Roanoke — :red_circle: <specific violation>
    A store whose cameras could not be seen gets a plain "cameras were not reachable at check time,
    not checked" line (never a status it did not see — Rule 18). No store seen at all = no post, one
    ledger row. After 14:30 ET the post is skipped (ledger row) rather than sent stale.

  dress_code_check.py --render [--date D] [--diag]   full capture + assessment, prints the would-be post,
                                                     posts nothing (snapshots are still saved)
  dress_code_check.py --probe                        NO browser: playwright, profile, key, native_live
  dress_code_check.py --send                         (launchd wrapper; gated by vp_live.sh)
Failure policy v3: one FAILURE_LEDGER row, never a DM, never a failure note in #general.
"""
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

AGENT = "daily-dress-code-check"
ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
sys.path.insert(0, BIN)
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "state", "dress_code")
TEST_OUT = os.path.join(OS_DIR, "fleet", "test_output", "dress_code")
import vp_browser  # the one automation profile + launch recipe (2026-10-19)
PROFILE = vp_browser.PROFILE
CH = "C03BETSS669"
POST_CUTOFF = (14, 30)
TILE_WAIT_S = 15          # let the live streams start before the screenshot
MODEL = "claude-sonnet-5-5"
# post order = the order every live post has used (10/6-10/16); Wednesday keeps that order minus HAR/LEX
ORDER = ["Harrisonburg", "Lexington", "Culpeper", "Roanoke", "Waynesboro"]
CODE = {"HAR": "Harrisonburg", "LEX": "Lexington", "CUL": "Culpeper", "ROA": "Roanoke", "WAY": "Waynesboro"}
# Google Home home ids (fullcirclepawn@gmail.com) — same dict as cloudcover_check.py
HOMES = {
    "Harrisonburg": "1-a4ed529501c13a26764e6df9f4d6508e4fc88e0bb25ec02a61d87597442fbba2",
    "Lexington": "1-f6f4392e095ca9169d3e5c4e8dfaec55b7587a28744cbf0af20b30009648bd3d",
    "Culpeper": "1-8567d747ce9987f177a24524772591264b3b242f5f709024934038bc65ce80e6",
    "Roanoke": "1-4dcee6f564dd8273f312795185b5653a829b69f2b13c1df0bd77e73864ab4d42",
    "Waynesboro": "1-db0b52f0fc4e4447696f44c382c5ab0664e57f19fee97ebdbb62f664236f85cc",
}
NOT_SEEN_LINE = "cameras were not reachable at check time, not checked"
OFFLINE_RX = re.compile(r"\b(offline|camera is off|camera off|no video|couldn.t load|can.t load|unavailable|not available|something went wrong|try again)\b", re.I)

RENDER = "--render" in sys.argv
DIAG = "--diag" in sys.argv

SYSTEM = """You review still frames from in-store security cameras at Valley Pawn (pawn shops) for employee dress code. Answer ONLY with one JSON object, no prose.

RULES (binding):
1. Valley Pawn branded clothing comes in MANY colours (green, orange, dark green and others). ANY collared shirt, polo, or jacket, in any colour, is COMPLIANT.
2. Only people BEHIND the counter, at a workstation, at a register, or in an employee-only/back area are employees. Anyone on the customer side of the counter or on the sales floor is a CUSTOMER — never flag a customer.
3. Jackets, hoodies or outerwear worn OVER the shirt are compliant; if the shirt underneath can't be seen, compliant.
4. Unclear angle, distance, blur, branding not confirmable -> COMPLIANT. Flag a violation only when you are at least 90% sure a person behind the counter is wearing clearly non-work attire (plain unbranded hoodie, casual t-shirt, tank top, etc.).
5. No employees visible (empty counter) -> COMPLIANT.
6. Do not try to identify anyone by name.
Also say honestly whether the frames actually show a LIVE camera picture of the store. A black, grey, blank, 'Offline', 'Camera off', loading spinner, or an error tile is NOT a live picture.

JSON shape: {"feed_visible": true|false, "feed_note": "<short>", "employees_visible": <int>, "violation": true|false, "violation_text": "<one plain sentence naming the specific clothing, only if violation>", "confidence": <0-100>}"""


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
    """True the first time `key` is seen today (a sign-in ask is one ledger row a day, not one per run)."""
    if RENDER:
        return True
    os.makedirs(STATE, exist_ok=True)
    p = os.path.join(STATE, "%s-%s" % (key, dt.datetime.now(ET).date()))
    if os.path.exists(p):
        return False
    open(p, "w").close()
    return True


def open_stores(day):
    """Store names for `day`, in post order, from bin/vp_lib.sh open_stores (the fleet's one calendar)."""
    codes = None
    try:
        r = subprocess.run(["/bin/bash", "-c", '. "%s/vp_lib.sh" >/dev/null 2>&1; open_stores %s' % (BIN, day.isoformat())],
                           capture_output=True, text=True, timeout=20)
        codes = r.stdout.strip().split()
    except Exception as e:
        log("open_stores via vp_lib.sh failed:", str(e)[:100])
    if codes is None:
        wd = day.weekday()
        codes = [] if wd == 6 else (["CUL", "ROA", "WAY"] if wd == 2 else list(CODE))
    names = [CODE[c] for c in codes if c in CODE]
    return [n for n in ORDER if n in names]


# ---------- capture ----------
TILE_JS = """() => {
  // camera tiles = the nearest sizeable ancestor of each <video>/<canvas>; fall back to elements named like a camera card
  const seen = new Set(), out = [];
  const push = (el) => { if (!el || seen.has(el)) return; const r = el.getBoundingClientRect();
    if (r.width < 120 || r.height < 80) return; seen.add(el); out.push(el); };
  document.querySelectorAll('video, canvas').forEach(v => {
    let el = v; for (let i = 0; i < 4 && el.parentElement; i++) { const p = el.parentElement;
      const r = p.getBoundingClientRect(); if (r.width > v.getBoundingClientRect().width * 1.6) break; el = p; }
    push(el); });
  if (!out.length) document.querySelectorAll('[class*="camera" i], [data-camera-id], [aria-label*="camera" i]').forEach(push);
  out.forEach((el, i) => el.setAttribute('data-vp-tile', String(i)));
  return out.map((el, i) => { const r = el.getBoundingClientRect();
    return {i, w: Math.round(r.width), h: Math.round(r.height), text: (el.innerText || '').trim().slice(0, 120)}; });
}"""


def page_state(page):
    url = page.url or ""
    if "accounts.google.com" in url or "signin" in url.lower() and "google" in url:
        return "signin"
    if "/welcome" in url:
        # home.google.com bounces an unauthenticated (or wrong /u/N/) request to its marketing page (ledger 10/8)
        return "welcome"
    try:
        body = page.inner_text("body")[:4000]
    except Exception:
        body = ""
    low = body.lower()
    if "creating a new home isn" in low:
        return "wrong-account"
    if "sign in" in low and "home.google.com" not in url:
        return "signin"
    return "home"


def follow_welcome(page):
    """On the marketing page: click 'Go to Google Home for web' once. -> 'signin' | 'u/N' | 'home-nouser' | 'welcome'"""
    try:
        href = ""
        loc = page.locator("text=Google Home for web").first
        if loc.count():
            href = loc.get_attribute("href") or loc.evaluate("el => (el.closest('a') || {}).href || ''") or ""
        log("welcome link href:", (href or "(none found)").split("?")[0][:120])
        if not href.startswith("http"):
            href = "https://home.google.com/home"           # what that button opens
        page.goto(href, wait_until="domcontentloaded", timeout=60000)   # same tab (the link may target a new one)
        page.wait_for_timeout(6000)
    except Exception as e:
        log("welcome link click failed:", str(e)[:80])
        return "welcome"
    st = page_state(page)
    if st == "signin":
        return "signin"
    m = re.search(r"home\.google\.com/u/(\d+)/", page.url or "")
    if m:
        return "u/" + m.group(1)
    if st == "home":
        return "home-nouser"
    return st


def goto_cameras(page, name, u):
    hid = HOMES[name]
    page.goto("https://home.google.com/u/%s/home/%s/cameras" % (u, hid), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    st = page_state(page)
    if st != "home":
        return st
    # the SKILL's path: land on Devices, click the "Cameras" tab in the left sidebar. Try it if the URL did not stick.
    if "/cameras" not in page.url:
        try:
            link = page.query_selector("a:has-text('Cameras'), [role=tab]:has-text('Cameras'), [role=link]:has-text('Cameras')")
            if link:
                link.click()
                page.wait_for_timeout(3000)
        except Exception as e:
            log("cameras tab click failed:", str(e)[:80])
    try:
        page.wait_for_selector("video, canvas", timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(TILE_WAIT_S * 1000)
    return "home"


def capture(page, name, out_dir):
    """-> dict(store, grid, tiles[], tile_meta[], text, offline_words)"""
    os.makedirs(out_dir, exist_ok=True)
    grid = os.path.join(out_dir, "%s.png" % name)
    page.screenshot(path=grid, full_page=False)
    try:
        meta = page.evaluate(TILE_JS)
    except Exception as e:
        log("tile scan failed:", str(e)[:80])
        meta = []
    tiles = []
    for m in meta[:8]:
        p = os.path.join(out_dir, "%s-cam%d.png" % (name, m["i"] + 1))
        try:
            el = page.query_selector("[data-vp-tile='%d']" % m["i"])
            if el:
                el.screenshot(path=p)
                tiles.append(p)
        except Exception as e:
            log("tile %d shot failed:" % m["i"], str(e)[:80])
    try:
        text = page.inner_text("body")[:6000]
    except Exception:
        text = ""
    words = sorted({w.lower() for w in OFFLINE_RX.findall(text)})
    return {"store": name, "grid": grid, "tiles": tiles, "tile_meta": meta, "text": text, "offline_words": words,
            "url": page.url.split("?")[0]}


def read_live(day, stores):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ledger("The dress code check could not run because the automation browser is not installed on the Mac.")
        sys.exit(3)
    out_dir = os.path.join(STATE, day.isoformat())
    caps, notes = {}, []
    with sync_playwright() as p:
        try:
            ctx = vp_browser.launch(p, headless=vp_browser.headless_from_env("DC_HEADLESS"), window_size=(1400, 1000),
                                    args=["--autoplay-policy=no-user-gesture-required"], viewport={"width": 1400, "height": 1000})
        except Exception as e:
            log("launch failed:", str(e)[:300])
            ledger("The dress code check could not open its automation browser (it may be open for sign-in), so nothing was posted.")
            sys.exit(3)
        try:
            page = vp_browser.first_page(ctx)
            if DIAG:   # cookie DOMAINS + names only, never values: is this profile signed in to Google at all?
                try:
                    g = [c for c in ctx.cookies() if "google.com" in c["domain"]]
                    log("diag: cookie domains:", sorted({c["domain"] for c in ctx.cookies()})[:20],
                        "| google.com cookie names:", sorted({c["name"] for c in g})[:25])
                except Exception as e:
                    log("diag: cookies unreadable:", str(e)[:80])
            user_idx = None
            for name in stores:
                st = None
                for u in ([user_idx] if user_idx is not None else ["1", "0"]):
                    try:
                        st = goto_cameras(page, name, u)
                    except Exception as e:
                        notes.append("%s u/%s: %s" % (name, u, str(e)[:100]))
                        st = "error"
                    if st == "home":
                        user_idx = u
                        break
                if st == "welcome" and user_idx is None:
                    # both /u/1 and /u/0 bounced to the marketing page: follow its own "Go to Google Home for web"
                    # link once. Signed in -> it lands on home.google.com/u/N/... (learn N, retry); not signed in ->
                    # accounts.google.com.
                    st = follow_welcome(page)
                    log("welcome link ->", st, page.url.split("?")[0])
                    if st.startswith("u/"):
                        user_idx = st[2:]
                        try:
                            st = goto_cameras(page, name, user_idx)
                        except Exception as e:
                            notes.append("%s u/%s: %s" % (name, user_idx, str(e)[:100]))
                            st = "error"
                    if st in ("welcome", "home-nouser"):
                        st = "signin"
                log("%s: state=%s u/%s url=%s" % (name, st, user_idx, page.url.split("?")[0]))
                if st == "home":
                    c = capture(page, name, out_dir)
                    log("  grid=%s tiles=%d offline_words=%s" % (os.path.basename(c["grid"]), len(c["tiles"]), c["offline_words"]))
                    caps[name] = c
                    if DIAG:
                        os.makedirs(TEST_OUT, exist_ok=True)
                        with open(os.path.join(TEST_OUT, "%s-%s.txt" % (day, name)), "w") as f:
                            f.write(c["url"] + "\n\n" + json.dumps(c["tile_meta"], indent=1) + "\n\n" + c["text"])
                elif st in ("signin", "wrong-account"):
                    if DIAG:
                        os.makedirs(TEST_OUT, exist_ok=True)
                        page.screenshot(path=os.path.join(TEST_OUT, "%s-%s-%s.png" % (day, name, st)))
                    if once_per_day("signin-google"):
                        ledger("Google Home needs a one-time sign-in in the automation browser",
                               "yes, run bin/vp_signin_front.sh and sign in to Google Home as fullcirclepawn@gmail.com once, then quit that window")
                    return None, notes
                else:
                    caps[name] = None
        finally:
            vp_browser.close(ctx)
    return caps, notes


# ---------- assessment ----------
def img_block(path):
    with open(path, "rb") as f:
        return {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                            "data": base64.b64encode(f.read()).decode()}}


def assess(cap):
    import vp_ai
    imgs = [cap["grid"]] + cap["tiles"][:6]
    content = []
    for i, p in enumerate(imgs):
        content.append({"type": "text", "text": "Image %d: %s" % (i + 1, "full camera page" if i == 0 else "camera tile %d" % i)})
        content.append(img_block(p))
    hint = ("The page text contains these words: %s." % ", ".join(cap["offline_words"])) if cap["offline_words"] else ""
    content.append({"type": "text", "text": "Store: %s. %s Assess per the rules and answer with the JSON object only." % (cap["store"], hint)})
    out = vp_ai.ask("", system=SYSTEM, model=MODEL, max_tokens=600, content=content)
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        raise ValueError("no JSON: " + out[:200])
    return json.loads(m.group(0), strict=False)


def judge(cap, a):
    """-> (line_status, detail) where line_status in {'ok','violation','unseen'}"""
    if cap is None:
        return "unseen", "no camera page"
    if not cap["tiles"] and not a.get("feed_visible"):
        return "unseen", "no live tile (%s)" % a.get("feed_note", "")
    if not a.get("feed_visible"):
        return "unseen", a.get("feed_note", "feed not visible")
    if a.get("violation") and int(a.get("confidence") or 0) >= 90 and a.get("violation_text"):
        return "violation", a["violation_text"].strip().rstrip(".")
    return "ok", "employees_visible=%s" % a.get("employees_visible")


def build_post(day, when, stores, results):
    head = ":camera: Dress Code Check — %s, %s %d, %d @ %s" % (
        day.strftime("%A"), day.strftime("%B"), day.day, day.year, when.strftime("%-I:%M %p"))
    lines = []
    for name in stores:
        st, detail = results[name]
        if st == "ok":
            lines.append("• %s — :white_check_mark: All in dress code" % name)
        elif st == "violation":
            lines.append("• %s — :red_circle: %s" % (name, detail))
        else:
            lines.append("• %s — %s" % (name, NOT_SEEN_LINE))
    return "%s\n%s" % (head, "\n".join(lines)), head


def probe():
    print("python:", sys.executable)
    try:
        from importlib.metadata import version
        import playwright.sync_api  # noqa
        print("playwright OK", version("playwright"))
    except Exception as e:
        print("playwright MISSING:", type(e).__name__, e)
    print("profile dir:", PROFILE, "exists" if os.path.isdir(PROFILE) else "MISSING")
    for f in ("Default/Preferences", "Default/Cookies", "Default/Network/Cookies"):
        p = os.path.join(PROFILE, f)
        print("  ", f, "%d bytes %s" % (os.path.getsize(p), dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M")) if os.path.exists(p) else "absent")
    print("automation Chrome running:", bool(subprocess.run(["pgrep", "-f", "--user-data-dir=" + PROFILE], capture_output=True).stdout.strip()))
    try:
        import vp_ai
        vp_ai.key()
        print("anthropic key: present (Keychain vp-agent-anthropic-key)")
    except Exception as e:
        print("anthropic key: MISSING", type(e).__name__)
    print("open_stores today:", open_stores(dt.datetime.now(ET).date()))
    print("native_live:", os.path.exists(os.path.join(OS_DIR, "fleet/state/native_live", AGENT)))


def main():
    if "--probe" in sys.argv:
        probe()
        return 0
    now = dt.datetime.now(ET)
    day = dt.date.fromisoformat(arg("--date")) if arg("--date") else now.date()
    stores = open_stores(day)
    if not stores:
        log("no stores open on", day, "- nothing to check")
        return 0
    log("stores:", stores, "| mode:", "headless" if os.environ.get("DC_HEADLESS") == "1" else "headed off-screen")
    if not RENDER and (now.hour, now.minute) > POST_CUTOFF and day == now.date():
        ledger("The dress code check did not run until after %d:%02d, so today's post was skipped rather than sent late." % POST_CUTOFF)
        return 0
    caps, notes = read_live(day, stores)
    for n in notes:
        log("note:", n)
    if caps is None:
        return 4
    if not any(caps.get(n) for n in stores):
        ledger("The dress code check could not open any store's camera page, so nothing was posted.")
        return 2
    when = dt.datetime.now(ET)
    results, assessments = {}, {}
    for name in stores:
        cap = caps.get(name)
        a = {}
        if cap is not None:
            try:
                a = assess(cap)
            except Exception as e:
                log("assess %s failed: %s %s" % (name, type(e).__name__, str(e)[:160]))
                a = {"feed_visible": False, "feed_note": "assessment failed"}
        results[name] = judge(cap, a)
        assessments[name] = a
        log("%s -> %s (%s)" % (name, results[name][0], results[name][1]))
    try:
        with open(os.path.join(STATE, day.isoformat(), "assessment.json"), "w") as f:
            json.dump({"captured": when.isoformat(), "results": results, "assessments": assessments}, f, indent=1)
    except Exception as e:
        log("assessment.json not written:", str(e)[:80])
    seen = [n for n in stores if results[n][0] != "unseen"]
    if not seen:
        ledger("The dress code check could not see a live picture from any store camera, so nothing was posted.")
        return 2
    post, head = build_post(day, when, stores, results)
    if RENDER:
        print(post)
        log("[render] nothing posted")
        return 0
    marker = head.split(" @ ")[0].replace(":camera: ", "")   # "Dress Code Check — Monday, October 19, 2026"
    env = dict(os.environ, VP_TASK=AGENT)
    h = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, marker, "20"],
                       capture_output=True, text=True, env=env)
    if h.returncode == 0:
        log("already posted today - not posting again")
        return 0
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post],
                       capture_output=True, text=True, env=env)
    if p.returncode != 0:
        ledger("The dress code check ran but its #general post did not go through.")
        log("FAIL post:", (p.stderr or p.stdout).strip()[:200])
        return 1
    log("posted", p.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
