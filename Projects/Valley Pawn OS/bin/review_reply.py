#!/usr/bin/env python3
"""review_reply.py — nightly Google/Facebook review replies, native (comms review 2026-10-20).

WHY: `nightly-chekkit-review-responses` (Cowork, 19:30, "auto-respond to 4-5 star reviews") has been OFF since
2026-09-15 with no replacement. On 2026-10-20 Waynesboro alone showed 19 reviews "Awaiting response"; a 1-star
Culpeper review (10/16) and a 3-star Waynesboro review got no reply and no one was told. Reviews are the
channel with the most customer trust, and the loop was open.

HOW (Playwright on the installed Google Chrome, the ONE shared automation profile pw-vp via bin/vp_browser.py —
signed in to dashboard.chekkit.io ONCE by Joshua through bin/vp_signin_front.sh; never types a password):
  1 ratings + review text come from the Chekkit API (GET /v1/reviews per store token, read-only); the dashboard
    is used only to find "Respond to <name>" buttons and post.
  2 for every review still awaiting a response:
      4-5 stars  -> draft with vp_ai (2-3 warm sentences, first name, the store's city, one specific thing
                    they mentioned, invite back; no prices, no promises, no policy) and POST it
                    (Respond -> textarea -> Post), then verify the Respond button for that reviewer is gone.
      1-3 stars  -> NEVER posted. Draft + the review text go to Joshua in one plain DM (his reply, his words).
      stars unknown (not in the API, e.g. stars-only review the API omits) -> treated as 1-3 (DM only).
  3 state: fleet/state/review_reply/done.json (reviewer+store+date) so a reply is never attempted twice even
    if the dashboard still shows the button; dedupe on the DM too.
  4 output: fleet/state/review_reply/<date>.json; one CHANGELOG line per run that posted something.
  review_reply.py --render        read + draft everything, post nothing, DM nothing (prints with initials)
  review_reply.py --send          the launchd wrapper (gated by vp_live.sh: fleet/state/native_live/nightly-chekkit-review-responses)
  review_reply.py --probe         no browser: playwright import, profile, API tokens, config
Config fleet/review_reply_config.json: min_stars_auto (4), max_per_store (12), stores order, signature.
Failure policy v3: login page = one ledger row naming vp_signin_front.sh --only chekkit, nothing posted.
Logs: reviewer initials only.
"""
import datetime as dt, json, os, re, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OS_DIR = os.path.dirname(HERE)
FLEET = os.path.join(OS_DIR, "fleet")
STATE_DIR = os.path.join(FLEET, "state", "review_reply")
CONFIG = os.path.join(FLEET, "review_reply_config.json")
ET = ZoneInfo("America/New_York")
JOSHUA = "U03BB52MDSA"
TASK = "nightly-chekkit-review-responses"
STORES = ["CUL", "WAY", "HAR", "LEX", "ROA"]
NAMES = {"CUL": "Culpeper", "WAY": "Waynesboro", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke"}
URL = "https://dashboard.chekkit.io/reviews"
DEFAULT_CFG = {"min_stars_auto": 4, "max_per_store": 12, "signature": "— The Valley Pawn team",
               "_about": "review_reply.py: 4-5 star reviews get an AI-drafted reply posted through the Chekkit dashboard; 1-3 star reviews are drafted to Joshua only (comms review 2026-10-20, same policy as the retired Cowork task nightly-chekkit-review-responses)."}


def log(*a):
    print(dt.datetime.now(ET).strftime("%H:%M:%S"), *a, flush=True)


def ledger(sentence, needs="no"):
    with open(os.path.join(FLEET, "FAILURE_LEDGER.md"), "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence, needs))


def initials(n):
    return "".join(w[0].upper() + "." for w in (n or "?").split() if w) or "?"


def cfg():
    try:
        c = json.load(open(CONFIG))
    except Exception:
        c = dict(DEFAULT_CFG); os.makedirs(FLEET, exist_ok=True); json.dump(c, open(CONFIG, "w"), indent=1)
    return c


def state():
    try:
        return json.load(open(os.path.join(STATE_DIR, "done.json")))
    except Exception:
        return {"done": {}, "dm": {}}


def save_state(st):
    os.makedirs(STATE_DIR, exist_ok=True)
    json.dump(st, open(os.path.join(STATE_DIR, "done.json"), "w"), indent=1)


def api_reviews(code, days=60):
    """Newest reviews for a store from the Chekkit API: {name.lower(): {rating, text, created}}."""
    import chekkit_api as ck
    out, cutoff = {}, dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    for page in range(1, 8):
        try:
            b = ck.get(code, "/v1/reviews?page=%d" % page, retries=2)
        except Exception as e:
            log(code, "API reviews page %d failed: %s" % (page, str(e)[:80])); break
        rs = b.get("reviews") or []
        for r in rs:
            t = ck.ts(r.get("createdAt"))
            if t and t < cutoff:
                continue
            name = (r.get("reviewerName") or "").strip()
            if name and name.lower() not in out:
                out[name.lower()] = {"rating": r.get("rating"), "text": (r.get("comment") or r.get("text") or r.get("reviewText") or "").strip(),
                                     "created": r.get("createdAt"), "site": r.get("site") or r.get("source") or ""}
        time.sleep(1.1)
        if not b.get("hasMore"):
            break
    return out


def draft(code, name, stars, text, c):
    import vp_ai
    first = (name.split() or ["there"])[0]
    system = ("You write short public replies to customer reviews for Valley Pawn, a family pawn shop with five stores in Virginia. "
              "Plain, warm, specific, 2-3 sentences, no emojis, no hashtags, no prices, no promises, no policy statements, no mention of "
              "AI. For 4-5 stars: thank them by first name, mention one specific thing from their review if there is one, name the store "
              "city, invite them back. For 1-3 stars: apologize sincerely without admitting fault on specifics, say the manager wants to "
              "make it right, and ask them to call the store or stop by — never argue, never explain policy. End with the signature given. "
              "Return ONLY the reply text.")
    prompt = "Store: Valley Pawn %s. Reviewer first name: %s. Stars: %s. Review text: %s\nSignature: %s" % (
        NAMES[code], first, stars if stars else "unknown", text or "(no text, stars only)", c.get("signature", ""))
    try:
        r = vp_ai.ask(prompt, system=system, max_tokens=400).strip().strip('"')
        return r if 20 < len(r) < 700 else ""
    except Exception as e:
        log("draft failed:", str(e)[:100]); return ""


JS_PENDING = """
() => {
  const out = [];
  for (const b of document.querySelectorAll('button')) {
    const t = (b.innerText || '').trim();
    const m = t.match(/^Respond to (.+)$/);
    if (!m) continue;
    let card = b.closest('div');
    for (let i = 0; i < 6 && card && !/ago/.test(card.innerText || ''); i++) card = card.parentElement;
    const txt = card ? (card.innerText || '') : '';
    out.push({name: m[1].trim(), card: txt.slice(0, 1200)});
  }
  return out;
}
"""


def switch_store(page, code):
    """Top-left 'Select account' combobox -> option whose text starts with 'Valley Pawn - <City>'."""
    page.get_by_role("combobox", name=re.compile("Select account", re.I)).first.click(timeout=15000)
    page.get_by_role("option", name=re.compile(r"^Valley Pawn - %s" % NAMES[code], re.I)).first.click(timeout=15000)
    page.wait_for_timeout(2500)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    head = page.locator("body").inner_text(timeout=15000)
    if "Valley Pawn - %s" % NAMES[code] not in head[:400]:
        raise RuntimeError("store switch did not land on %s" % NAMES[code])
    return head


def post_reply(page, name, text):
    page.get_by_role("button", name="Respond to %s" % name, exact=True).first.click(timeout=15000)
    page.wait_for_timeout(1200)
    box = page.locator("[role=dialog] textarea, textarea").first
    box.click(timeout=10000); box.fill(text, timeout=10000)
    page.get_by_role("button", name=re.compile(r"^Post$")).first.click(timeout=10000)
    page.wait_for_timeout(3000)
    body = page.locator("body").inner_text(timeout=10000)
    if "Request failed" in body or "failed" in body.lower()[:3000]:
        return False, "dashboard reported a failure"
    page.goto(URL, wait_until="domcontentloaded", timeout=60000); page.wait_for_timeout(3500)
    still = page.get_by_role("button", name="Respond to %s" % name, exact=True).count()
    return still == 0, ("" if still == 0 else "Respond button still present after posting")


def main():
    a = sys.argv[1:]
    render, send, probe = "--render" in a, "--send" in a, "--probe" in a
    c = cfg(); st = state(); today = dt.datetime.now(ET).date().isoformat()
    if probe:
        try:
            import playwright.sync_api  # noqa
            print("playwright OK")
        except Exception as e:
            print("playwright MISSING", e)
        import vp_browser, chekkit_api as ck
        print("profile", vp_browser.PROFILE, "exists" if os.path.isdir(vp_browser.PROFILE) else "MISSING")
        print("tokens", {s: bool(ck.token(s)) for s in STORES}); print("config", c); return 0
    if not (render or send):
        print(__doc__); return 2
    import vp_browser
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ledger("The review-reply agent could not run because the automation browser is not installed on the Mac."); return 3
    results = {"date": today, "render": render, "stores": {}, "posted": 0, "dm": 0}
    low_star_dm = []
    with sync_playwright() as p:
        try:
            ctx = vp_browser.launch(p, headless=vp_browser.headless_from_env("RR_HEADLESS"))
        except Exception as e:
            log("launch failed:", str(e)[:200])
            if send:
                ledger("The review-reply agent could not open its automation browser (it may be open for sign-in), so no reviews were answered.")
            return 3
        try:
            page = vp_browser.first_page(ctx)
            page.goto(URL, wait_until="domcontentloaded", timeout=60000); page.wait_for_timeout(4000)
            body = page.locator("body").inner_text(timeout=15000)
            if page.locator("input[type=password]").count() or "/login" in page.url or "Sign in" in body[:600]:
                if send:
                    ledger("Chekkit needs a one-time sign-in in the automation browser (run bin/vp_signin_front.sh --only chekkit, sign in as jdavis@fcfpawn.com, then quit that window) before reviews can be answered automatically.", "yes")
                log("login page — stop"); return 4
            for code in STORES:
                r = {"pending": 0, "posted": [], "dm": [], "skipped": [], "error": ""}
                try:
                    switch_store(page, code)
                    pend = page.evaluate(JS_PENDING)
                    r["pending"] = len(pend)
                    api = api_reviews(code)
                    for item in pend[: int(c.get("max_per_store", 12))]:
                        name = item["name"]; key = "%s|%s" % (code, name.lower())
                        if key in st["done"]:
                            r["skipped"].append(initials(name) + " (done)"); continue
                        info = api.get(name.lower()) or {}
                        stars = info.get("rating")
                        if stars is None:  # fall back to the card: count of filled star icons is not reliable; look for "N star"
                            m = re.search(r"(\d)\s*star", item["card"], re.I); stars = int(m.group(1)) if m else None
                        text = info.get("text") or ""
                        if not text:
                            lines = [l.strip() for l in item["card"].splitlines() if l.strip() and "Respond to" not in l and "ago" not in l and l.strip() != name]
                            text = " ".join(lines)[:600]
                        reply = draft(code, name, stars, text, c)
                        if not reply:
                            r["skipped"].append(initials(name) + " (no draft)"); continue
                        if stars is not None and int(stars) >= int(c.get("min_stars_auto", 4)):
                            if render:
                                log("WOULD POST %s %s %s*: %s" % (code, initials(name), stars, reply[:160]))
                                r["posted"].append({"name": initials(name), "stars": stars, "render": True}); continue
                            ok, why = post_reply(page, name, reply)
                            if ok:
                                st["done"][key] = {"at": dt.datetime.now(ET).isoformat(), "stars": stars}; save_state(st)
                                r["posted"].append({"name": initials(name), "stars": stars}); results["posted"] += 1
                                log("posted %s %s %s*" % (code, initials(name), stars))
                            else:
                                r["skipped"].append("%s (post failed: %s)" % (initials(name), why))
                                log("post failed %s %s: %s" % (code, initials(name), why))
                            time.sleep(2)
                        else:
                            dkey = key + "|" + (str(stars) if stars is not None else "?")
                            if dkey in st["dm"]:
                                r["skipped"].append(initials(name) + " (already sent to Joshua)"); continue
                            low_star_dm.append((code, name, stars, text, reply, dkey))
                            r["dm"].append({"name": initials(name), "stars": stars})
                except Exception as e:
                    r["error"] = "%s: %s" % (type(e).__name__, str(e)[:160]); log(code, "ERROR", r["error"])
                results["stores"][code] = r
        finally:
            vp_browser.close(ctx)
    if low_star_dm:
        lines = ["Reviews that need your reply (not posted — your words, your call):"]
        for code, name, stars, text, reply, dkey in low_star_dm[:8]:
            lines.append("• %s — %s star(s) from %s: \"%s\"\n  Draft: %s" % (NAMES[code], stars if stars is not None else "?", name, (text or "(stars only)")[:260], reply))
        msg = "\n".join(lines)
        if render:
            print("=== DM Joshua\n" + re.sub(r"from ([A-Z][a-z]+ ?[A-Za-z.]*)", lambda m: "from " + initials(m.group(1)), msg))
        else:
            import vp_slack
            vp_slack.post(vp_slack.dm_channel(JOSHUA), msg)
            for code, name, stars, text, reply, dkey in low_star_dm:
                st["dm"][dkey] = dt.datetime.now(ET).isoformat()
            save_state(st); results["dm"] = len(low_star_dm)
    os.makedirs(STATE_DIR, exist_ok=True)
    json.dump(results, open(os.path.join(STATE_DIR, today + ("-render" if render else "") + ".json"), "w"), indent=1)
    if send and results["posted"]:
        with open(os.path.join(OS_DIR, "CHANGELOG.md"), "r+") as f:
            body = f.read(); f.seek(0)
            f.write("## %s (review replies, native)\n\n- nightly-chekkit-review-responses (native review_reply.py): %d replies posted (%s); %d low-star review(s) sent to Joshua as drafts.\n\n%s" % (
                today, results["posted"], ", ".join("%s %d" % (s, len(results["stores"].get(s, {}).get("posted", []))) for s in STORES), results["dm"], body))
    log("done", json.dumps({s: (len(v["posted"]), len(v["dm"]), v["pending"], v["error"][:40]) for s, v in results["stores"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
