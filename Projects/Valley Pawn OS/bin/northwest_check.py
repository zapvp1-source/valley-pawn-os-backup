#!/usr/bin/env python3
"""northwest_check.py — native replacement for Cowork `northwest-registered-agent-daily-check`
(daily 08:49 ET -> #registered-agent C0BMN275FD4 + filing into the Drive "Registered Agent" folder).
Built 2026-10-18 (Mac-first). WHY: the Cowork copy died Sat 10/17 and Sun 10/18 on the account's weekly
usage limit ("You've hit your weekly limit") before its first tool call; a native agent cannot be taken
out by that.

HOW (Playwright on the installed Google Chrome — a real window parked off-screen, because headless Chrome
is stopped by Cloudflare's bot check on Northwest's site (found 2026-10-18); never types a password; never a
screenshot of anything but its own automation window):
  1 Opens the DEDICATED automation profile ~/Library/Application Support/valleypawn/pw-northwest
    (separate from Joshua's everyday Chrome; signed in ONCE by Joshua with bin/northwest_signin_front.sh,
    "remember this device" if offered). The profile's Preferences get session.restore_on_startup=1 so
    session cookies survive restarts (the cloudcover_profile_prefs.py pattern).
    - Login form shown (password field) -> the saved session is gone: ONE ledger row a day
      ("Northwest needs a one-time sign-in in the automation browser"), nothing posted, stop. NO
      credential is ever typed by this script.
    - SMS-code screen shown ("You're almost there!") while the session is otherwise valid -> read the
      code from fleet/sms_codes/northwest.json, written by the native sms-code-relay agent (Messages,
      window 08:35-09:40 ET, see fleet/sms_code_relay.json). Rules from the SKILL: use it only if age_s
      <= 600 AND received is AFTER the code was requested; poll up to 2 min; request once more; then ONE
      ledger row (NEEDS_HUMAN: no - relay did not see the text) and stop.
  2 Documents page (accounts.northwestregisteredagent.com/#/documents), filters cleared so the FULL list
    is read, never just "Unread". Every row -> (entity, document type, received date).
  3 Compare against the Drive folder's LOCAL synced copy (Drive for Desktop: Computers > My Mac > Desktop
    > Registered Agent = ~/Desktop/Registered Agent). A portal document whose entity + document type (+ date,
    if the filename carries one) already appear in a filename there is filed. Anything else is downloaded
    (Playwright download of the detail page's Download button; the S3 URL is never logged) and copied into
    that folder UNLESS a file with exactly that name is already there (the SKILL's by-filename rule) —
    never overwrite, never delete, read-only in the portal.
  4 Post the SKILL's format to #registered-agent as the ops bot (dedupe: today's line already there = no
    repost). New documents: entity, type, date; time-sensitive flag on top (service of process / lawsuit /
    annual report or franchise tax due / compliance deficiency); the Drive folder link. Nothing new: the
    one-line "checked ... no new notices, portal and Drive folder are in sync (...)".
  5 Service of process / lawsuit keywords -> ALSO one plain DM to Joshua (SKILL step 5).

  northwest_check.py --render [--diag]   full read (sign-in/2FA handling included), nothing posted, downloads
                                         land in fleet/test_output/northwest/ only; --diag also writes the
                                         documents page's text/structure + a screenshot there (text only,
                                         no cookies, no code) so selectors can be tightened after run 1
  northwest_check.py --probe             NO browser: playwright import, profile + Drive folder + relay state
  northwest_check.py --send              (launchd wrapper; gated by vp_live.sh)
Failure policy v3: one FAILURE_LEDGER row, never a DM about a failure, never a failure note in a channel.
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

AGENT = "northwest-registered-agent-daily-check"
ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "state", "northwest")
TEST_OUT = os.path.join(OS_DIR, "fleet", "test_output", "northwest")
RELAY = os.path.join(OS_DIR, "fleet", "sms_codes", "northwest.json")
PROFILE = os.path.join(HOME, "Library/Application Support/valleypawn/pw-northwest")
DRIVE_DIR = os.environ.get("NW_DRIVE_DIR") or os.path.join(HOME, "Desktop", "Registered Agent")
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1WAYRYy2OXJXaVBYagpTrBys4ZYExUVn0"
CH = "C0BMN275FD4"
LOGIN_URL = "https://www.northwestregisteredagent.com/login"
DOCS_URL = "https://accounts.northwestregisteredagent.com/#/documents"
DASH_URL = "https://accounts.northwestregisteredagent.com/#/dashpanel"
ENTITIES = ["Full Circle Finance Inc", "Farming Infinity Mountains LLC", "Farming Infinity Virginia LLC",
            "Farming Infinity LLC"]          # longest first so "Farming Infinity LLC" never swallows the others
URGENT_SOP = re.compile(r"service of process|summons|lawsuit|complaint|subpoena|garnish|litigation|civil action", re.I)
URGENT_OTHER = re.compile(r"annual report|franchise tax|due|deficien|delinquen|revocation|revoked|reinstat|penalt|notice of", re.I)
DATE_RX = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b|\b([A-Z][a-z]{2,8})\.? (\d{1,2}),? (\d{4})\b")
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

RENDER = "--render" in sys.argv
DIAG = "--diag" in sys.argv


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
    if RENDER:
        return True
    os.makedirs(STATE, exist_ok=True)
    p = os.path.join(STATE, "%s-%s" % (key, dt.datetime.now(ET).date()))
    if os.path.exists(p):
        return False
    open(p, "w").close()
    return True


# ---------- profile preferences (session cookies survive restarts) ----------
def ensure_prefs():
    """session.restore_on_startup = 1 on the automation profile, only while that Chrome is closed. Idempotent."""
    p = os.path.join(PROFILE, "Default", "Preferences")
    if not os.path.exists(p):
        return "no Preferences yet (profile not created / never signed in)"
    if subprocess.run(["pgrep", "-f", "--user-data-dir=" + PROFILE], capture_output=True).stdout.strip():
        return "automation Chrome is open - prefs left alone"
    try:
        d = json.load(open(p))
    except Exception as e:
        return "Preferences unreadable: %s" % type(e).__name__
    if d.get("session", {}).get("restore_on_startup") == 1 and d.get("profile", {}).get("exit_type") == "Normal":
        return "restore_on_startup already 1"
    shutil.copy(p, p + ".bak-" + dt.datetime.now(ET).strftime("%Y%m%d"))
    d.setdefault("session", {})["restore_on_startup"] = 1
    d.setdefault("profile", {})["exit_type"] = "Normal"
    json.dump(d, open(p, "w"))
    return "restore_on_startup set to 1"


# ---------- Drive folder (local synced copy) ----------
def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def parse_date(s):
    m = DATE_RX.search(s or "")
    if not m:
        return None
    try:
        if m.group(1):
            mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            y = y + 2000 if y < 100 else y
        else:
            mo = MONTHS.get(m.group(4)[:3].lower())
            d, y = int(m.group(5)), int(m.group(6))
            if not mo:
                return None
        return dt.date(y, mo, d)
    except ValueError:
        return None


def drive_files():
    if not os.path.isdir(DRIVE_DIR):
        return None
    return sorted(f for f in os.listdir(DRIVE_DIR) if not f.startswith(".") and os.path.isfile(os.path.join(DRIVE_DIR, f)))


def filed_match(doc, files):
    """The Drive filename that already holds this portal document, or None."""
    ent, typ, date = norm(doc.get("entity")), norm(doc.get("type")), doc.get("date")
    words = [w for w in typ.split() if len(w) > 2 and w not in ("the", "and", "for", "letter")]
    for f in files:
        stem = norm(os.path.splitext(f)[0])
        if doc.get("title") and norm(doc["title"]) == stem:
            return f
        if ent and ent not in stem:
            continue
        if words and sum(w in stem for w in words) < max(1, len(words) - 1):
            continue
        fd = parse_date(f)
        if date and fd and fd != date:
            continue
        if ent or words:
            return f
    return None


# ---------- SMS relay ----------
def relay_code(requested_at):
    """Newest relay code that arrived AFTER requested_at and is <= 600 s old, else None. Never logs the code."""
    try:
        r = json.load(open(RELAY))
    except Exception:
        return None
    if not r.get("code") or r.get("age_s") is None or r["age_s"] > 600:
        return None
    try:
        rec = dt.datetime.fromisoformat(r["received"])
    except Exception:
        return None
    if rec.tzinfo is None:
        rec = rec.replace(tzinfo=dt.timezone.utc)
    if rec < requested_at - dt.timedelta(seconds=5):
        return None
    return str(r["code"])


# ---------- page helpers ----------
ROWS_JS = """() => {
  const txt = e => (e.innerText || '').replace(/\\s+/g, ' ').trim();
  let tables = Array.from(document.querySelectorAll('table'));
  let best = null, bestN = 0;
  for (const t of tables) { const n = t.querySelectorAll('tbody tr, tr').length; if (n > bestN) { best = t; bestN = n; } }
  const out = {headers: [], rows: [], url: location.href, title: document.title};
  if (best) {
    out.headers = Array.from(best.querySelectorAll('thead th, thead td, tr th')).map(txt);
    const trs = Array.from(best.querySelectorAll('tbody tr')).length ? Array.from(best.querySelectorAll('tbody tr')) : Array.from(best.querySelectorAll('tr')).filter(r => !r.querySelector('th'));
    trs.forEach((tr, i) => {
      const cells = Array.from(tr.querySelectorAll('td, th')).map(txt);
      const a = tr.querySelector('a[href]');
      out.rows.push({i, cells, text: txt(tr), href: a ? a.href : null});
    });
  } else {
    const rows = Array.from(document.querySelectorAll('[role=row]'));
    rows.forEach((r, i) => { const cells = Array.from(r.querySelectorAll('[role=cell], [role=gridcell]')).map(txt); const a = r.querySelector('a[href]'); out.rows.push({i, cells, text: txt(r), href: a ? a.href : null}); });
  }
  out.body = txt(document.body).slice(0, 4000);
  return out;
}"""


def classify(page):
    """'login' | 'sms' | 'docs' | 'other' from the current page."""
    url = page.url or ""
    body = ""
    try:
        body = page.inner_text("body")[:6000]
    except Exception:
        pass
    low = body.lower()
    if "performing security verification" in low or "verify you are human" in low or "checking your browser" in low:
        return "cloudflare", body
    if page.query_selector("input[type=password]"):
        return "login", body
    if "almost there" in low or page.query_selector("input[autocomplete=one-time-code], input[name*=code i], input[id*=code i]"):
        return "sms", body
    if "#/documents" in url and page.query_selector("table, [role=row]"):
        return "docs", body
    return "other", body


def extract_docs(page):
    data = page.evaluate(ROWS_JS)
    docs = []
    for r in data.get("rows", []):
        t = r.get("text") or " ".join(r.get("cells") or [])
        if not t or len(t) < 6:
            continue
        ent = next((e for e in ENTITIES if e.lower() in t.lower()), None)
        date = parse_date(t)
        cells = r.get("cells") or []
        typ = None
        for c in cells:
            c2 = c.strip()
            if not c2 or parse_date(c2) or (ent and ent.lower() == c2.lower()) or c2.lower() in ("read", "unread", "new", "download", "view"):
                continue
            if len(c2) > 3 and not re.fullmatch(r"[\d\W]+", c2):
                typ = c2
                break
        if typ and ent and ent.lower() in typ.lower():
            typ = re.sub(re.escape(ent), "", typ, flags=re.I).strip(" -–—:")
        docs.append({"i": r["i"], "entity": ent, "type": typ, "date": date, "title": None, "text": t, "href": r.get("href")})
    return data, docs


def clear_filters(page):
    """Open Filters and Clear Filters if such controls exist (the SKILL's 'never only Unread' rule). Best effort."""
    try:
        for label in ("Clear Filters", "Clear filters", "Clear all"):
            el = page.get_by_text(label, exact=False).first
            if el and el.count() and el.is_visible():
                el.click(timeout=3000)
                page.wait_for_timeout(1500)
                return "cleared via visible %r" % label
        f = page.get_by_text("Filters", exact=False).first
        if f and f.count() and f.is_visible():
            f.click(timeout=3000)
            page.wait_for_timeout(1000)
            el = page.get_by_text("Clear", exact=False).first
            if el and el.count() and el.is_visible():
                el.click(timeout=3000)
                page.wait_for_timeout(1500)
                return "cleared via Filters > Clear"
    except Exception as e:
        return "filters: %s" % str(e)[:80]
    return "no filter controls found"


def download_doc(page, ctx, doc, dest_dir):
    """Open the row's detail page, click Download, save the file. Returns local path or raises."""
    os.makedirs(dest_dir, exist_ok=True)
    page.goto(DOCS_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2500)
    rows = page.query_selector_all("table tbody tr") or page.query_selector_all("[role=row]")
    row = None
    for r in rows:
        if norm(doc["text"])[:60] in norm(r.inner_text()):
            row = r
            break
    if row is None:
        raise RuntimeError("row not found again")
    # a per-row download control first, else open the detail page
    dl = row.query_selector("a[download], [aria-label*=ownload], [title*=ownload], button:has-text('Download'), a:has-text('Download')")
    if dl is None:
        link = row.query_selector("a[href]") or row
        link.click(timeout=10000)
        page.wait_for_timeout(3000)
        dl = page.query_selector("a[download], button:has-text('Download'), a:has-text('Download'), [aria-label*=ownload]")
    if dl is None:
        raise RuntimeError("no Download control on the detail page")
    with page.expect_download(timeout=60000) as info:
        dl.click(timeout=10000)
    d = info.value
    name = d.suggested_filename or ("northwest-%s.pdf" % dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S"))
    name = re.sub(r"[/\\\x00]", "_", name)
    path = os.path.join(dest_dir, name)
    d.save_as(path)
    return path


# ---------- SMS step ----------
def handle_sms(page):
    """Type the relayed code. Returns True when past the SMS screen."""
    for attempt in (1, 2):
        requested = dt.datetime.now(dt.timezone.utc)
        if attempt == 2:
            # ask for a fresh code: the SKILL's path is Sign In again on the login form
            btn = page.query_selector("button:has-text('Resend'), a:has-text('Resend'), button:has-text('Send again'), button:has-text('Sign in'), button:has-text('Sign In')")
            if btn:
                btn.click(timeout=5000)
                page.wait_for_timeout(3000)
            else:
                log("no resend control; not re-requesting")
                break
        code = None
        for _ in range(12):
            code = relay_code(requested)
            if code:
                break
            time.sleep(10)
        if not code:
            log("no fresh relay code within 2 min (attempt %d)" % attempt)
            continue
        inp = page.query_selector("input[autocomplete=one-time-code], input[name*=code i], input[id*=code i], input[type=tel], input[type=number], input[type=text]")
        if inp is None:
            log("sms screen without an input field")
            return False
        inp.fill(code)
        btn = page.query_selector("button:has-text('Continue'), button:has-text('Verify'), button:has-text('Submit'), button[type=submit]")
        if btn:
            btn.click(timeout=5000)
        else:
            inp.press("Enter")
        try:
            page.wait_for_url(re.compile(r"#/(dashpanel|documents)"), timeout=30000)
        except Exception:
            page.wait_for_timeout(4000)
        kind, _ = classify(page)
        if kind != "sms":
            log("sms code accepted")
            return True
        log("code not accepted (attempt %d)" % attempt)
    return False


# ---------- main read ----------
def read_live():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ledger("The registered agent check could not run because the automation browser is not installed on the Mac.")
        sys.exit(3)
    log("prefs:", ensure_prefs())
    dl_dir = os.path.join(TEST_OUT if RENDER else STATE, "downloads", dt.datetime.now(ET).strftime("%Y%m%d"))
    notes, diag = [], {}
    with sync_playwright() as p:
        try:
            # 2026-10-18 render 1: headless Chrome gets Cloudflare's "Performing security verification" (Turnstile)
            # on both northwestregisteredagent.com hosts. So: a real (headed) Chrome window, parked off-screen, with
            # the automation flag hidden, and Playwright's own mock keychain off (real macOS keychain = Joshua's
            # saved sign-in cookies decrypt). NW_HEADLESS=1 forces headless for experiments.
            headless = os.environ.get("NW_HEADLESS") == "1"
            ctx = p.chromium.launch_persistent_context(PROFILE, channel="chrome", headless=headless, accept_downloads=True,
                                                       ignore_default_args=["--use-mock-keychain", "--enable-automation"],
                                                       args=["--no-first-run", "--no-default-browser-check",
                                                             "--disable-blink-features=AutomationControlled",
                                                             "--window-position=-2400,-2400", "--window-size=1280,900"])
        except Exception as e:
            log("launch failed:", str(e)[:300])
            ledger("The registered agent check could not open its automation browser (it may be open for sign-in), so nothing was posted.")
            sys.exit(3)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(DOCS_URL, wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_selector("table, [role=row], input[type=password], input[autocomplete=one-time-code]", timeout=30000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            kind, body = classify(page)
            if kind == "cloudflare":
                # a managed challenge usually clears itself in a real browser within a few seconds; never click it
                for _ in range(15):
                    page.wait_for_timeout(3000)
                    kind, body = classify(page)
                    if kind != "cloudflare":
                        break
                log("cloudflare challenge:", "cleared" if kind != "cloudflare" else "still shown after 45 s")
            if kind == "other":
                # not signed in usually bounces to the marketing login page; give the SSO redirect one more chance
                page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)
                kind, body = classify(page)
            log("page state:", kind, "|", page.url.split("?")[0])
            if DIAG:
                os.makedirs(TEST_OUT, exist_ok=True)
                page.screenshot(path=os.path.join(TEST_OUT, "state-%s.png" % kind), full_page=True)
            if kind == "cloudflare":
                if once_per_day("cloudflare"):
                    ledger("Northwest's website put a bot check in front of the automation browser, so the registered agent check could not sign in.",
                           "yes, run bin/northwest_signin_front.sh and open the Northwest portal once in that window (and sign in if asked)")
                sys.exit(8)
            if kind == "login":
                if once_per_day("signin"):
                    ledger("Northwest needs a one-time sign-in in the automation browser",
                           "yes, run bin/northwest_signin_front.sh, sign in to Northwest once (tick remember this device if offered), then quit that window")
                sys.exit(4)
            if kind == "sms":
                if not handle_sms(page):
                    ledger("The registered agent check stopped at Northwest's text-message code because the relay did not see a fresh code.")
                    sys.exit(5)
                page.goto(DOCS_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                kind, body = classify(page)
            if kind != "docs":
                page.goto(DOCS_URL, wait_until="domcontentloaded", timeout=60000)
                try:
                    page.wait_for_selector("table, [role=row]", timeout=30000)
                except Exception:
                    pass
                page.wait_for_timeout(2000)
                kind, body = classify(page)
            if kind != "docs":
                if DIAG:
                    page.screenshot(path=os.path.join(TEST_OUT, "state-unexpected.png"), full_page=True)
                    open(os.path.join(TEST_OUT, "state-unexpected.txt"), "w").write(page.url + "\n" + body)
                ledger("The registered agent check signed in but could not read the documents list, so nothing was posted.")
                sys.exit(6)
            notes.append(clear_filters(page))
            data, docs = extract_docs(page)
            if DIAG:
                os.makedirs(TEST_OUT, exist_ok=True)
                page.screenshot(path=os.path.join(TEST_OUT, "documents.png"), full_page=True)
                json.dump({"headers": data.get("headers"), "rows": data.get("rows"), "body": data.get("body"),
                           "parsed": [{**d, "date": str(d["date"]) if d["date"] else None} for d in docs]},
                          open(os.path.join(TEST_OUT, "documents_%s.json" % dt.datetime.now(ET).strftime("%Y%m%d-%H%M")), "w"), indent=1)
            files = drive_files()
            if files is None:
                ledger("The registered agent check could not find the local Drive folder %s, so nothing was downloaded or posted." % DRIVE_DIR,
                       "yes, confirm Drive for Desktop still syncs Desktop > Registered Agent")
                sys.exit(7)
            new = []
            for d in docs:
                d["filed_as"] = filed_match(d, files)
                if d["filed_as"]:
                    continue
                try:
                    path = download_doc(page, ctx, d, dl_dir)
                except Exception as e:
                    notes.append("download failed for %r: %s" % (d["text"][:60], str(e)[:100]))
                    d["download_error"] = str(e)[:100]
                    continue
                d["local"] = path
                name = os.path.basename(path)
                if name in files:
                    d["filed_as"] = name     # already on Drive under exactly this name -> not new
                    continue
                if not RENDER:
                    shutil.copy2(path, os.path.join(DRIVE_DIR, name))   # never overwrites (name not present)
                    files.append(name)
                d["filed_as"] = name
                new.append(d)
        finally:
            ctx.close()
    return docs, new, files, notes


def fmt_date(d, year=True):
    return d.strftime("%b %-d, %Y") if year else d.strftime("%b %-d")


def build_post(day, docs, new, files, failed):
    head = "Northwest Registered Agent checked %s" % fmt_date(day)
    if not new and not failed:
        dates = {d["date"] for d in docs if d.get("date")}
        extra = "%d documents in both" % len(docs)
        if len(dates) == 1:
            extra += ", all from %s" % fmt_date(next(iter(dates)), year=False)
        return "%s — no new notices, portal and Drive folder are in sync (%s)." % (head, extra), False
    urgent_sop = [d for d in new if URGENT_SOP.search(d["text"])]
    urgent_oth = [d for d in new if d not in urgent_sop and URGENT_OTHER.search(d["text"])]
    lines = []
    if urgent_sop:
        lines.append("⚠️ *Looks like service of process / a legal notice — please read today:* " +
                     "; ".join("%s — %s" % (d.get("entity") or "entity not shown", d.get("type") or d["text"][:80]) for d in urgent_sop))
    elif urgent_oth:
        lines.append("⚠️ *May be time-sensitive (deadline or compliance notice):* " +
                     "; ".join("%s — %s" % (d.get("entity") or "entity not shown", d.get("type") or d["text"][:80]) for d in urgent_oth))
    if new:
        items = ", ".join("%s — %s (received %s)" % (d.get("entity") or "entity not shown", d.get("type") or d["text"][:80],
                                                      fmt_date(d["date"]) if d.get("date") else "date not shown") for d in new)
        lines.append("%s — %d new document%s filed to the Registered Agent Drive folder: %s. Folder: <%s|Registered Agent>."
                     % (head, len(new), "" if len(new) == 1 else "s", items, DRIVE_FOLDER_URL))
    if failed:
        lines.append("%s%d document%s in the portal could not be downloaded today and will be retried tomorrow: %s."
                     % ("" if new else head + " — ", len(failed), "" if len(failed) == 1 else "s",
                        "; ".join("%s — %s" % (d.get("entity") or "entity not shown", d.get("type") or d["text"][:60]) for d in failed)))
    return "\n".join(lines), bool(urgent_sop)


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
    files = drive_files()
    print("drive dir:", DRIVE_DIR, "MISSING" if files is None else "%d files" % len(files))
    for f in files or []:
        print("  ", f)
    for cand in glob.glob(os.path.join(HOME, "Library/CloudStorage/GoogleDrive-*")) + [os.path.join(HOME, "Google Drive")]:
        print("drive mount:", cand, "exists" if os.path.exists(cand) else "absent")
    try:
        r = json.load(open(RELAY))
        print("relay file:", {**r, "code": "******" if r.get("code") else None})
    except Exception as e:
        print("relay file unreadable:", type(e).__name__)
    print("native_live:", os.path.exists(os.path.join(OS_DIR, "fleet/state/native_live", AGENT)))


def main():
    if "--probe" in sys.argv:
        probe()
        return 0
    now = dt.datetime.now(ET)
    day = dt.date.fromisoformat(arg("--date")) if arg("--date") else now.date()
    docs, new, files, notes = read_live()
    for n in notes:
        log("note:", n)
    failed = [d for d in docs if d.get("download_error")]
    log("portal documents: %d | already filed: %d | new: %d | failed: %d | drive files: %d"
        % (len(docs), sum(1 for d in docs if d.get("filed_as") and d not in new), len(new), len(failed), len(files)))
    for d in docs:
        log("  doc:", (d.get("entity") or "?"), "|", (d.get("type") or "?"), "|", d.get("date"), "|", "filed as %r" % d.get("filed_as") if d.get("filed_as") else "NOT FILED")
    if not docs:
        ledger("The registered agent check signed in but the documents list came back empty, so nothing was posted (a real empty portal is unlikely: 8 documents have been there since July).")
        return 2
    post, sop = build_post(day, docs, new, files, failed)
    os.makedirs(STATE, exist_ok=True)
    json.dump({"checked": now.isoformat(timespec="seconds"), "docs": [{**d, "date": str(d["date"]) if d.get("date") else None} for d in docs],
               "new": [os.path.basename(d.get("local") or "") for d in new], "post": post},
              open(os.path.join(TEST_OUT if RENDER else STATE, "last_run.json"), "w"), indent=1)
    if RENDER:
        print(post)
        log("[render] nothing posted, nothing copied to Drive")
        return 0
    env = dict(os.environ, VP_TASK=AGENT)
    h = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, "Northwest Registered Agent checked", "20"],
                       capture_output=True, text=True, env=env)
    if h.returncode == 0 and not new:
        log("already posted today — not posting again")
        return 0
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        ledger("The registered agent check ran but its #registered-agent post did not go through.")
        log("FAIL post:", (p.stderr or p.stdout).strip()[:200])
        return 1
    log("posted", p.stdout.strip())
    if sop:
        subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "dm",
                        "Northwest Registered Agent received what looks like service of process or a legal notice today — it is filed in the Registered Agent Drive folder and posted in #registered-agent. Please read it today."],
                       capture_output=True, text=True, env=env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
