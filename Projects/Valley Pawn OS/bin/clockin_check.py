#!/usr/bin/env python3
"""clockin_check.py — native replacement for the Cowork/cloud `daily-clockin-check`
(Mon–Sat 10:15 ET -> #general C03BETSS669). Built 2026-10-18 (Mac-first). WHY: the cloud copy posts through
the Claude account and died Sat 10/17 on the account's weekly usage limit; a native agent cannot be taken
out by that. Authoritative instructions + exact post format: fleet/task_prompts/daily-clockin-check.md
(v2 2026-10-15: Wednesday = Culpeper + Roanoke + Waynesboro; store staff only; crosswalk; three formats).

HOW (Playwright on the installed Google Chrome — a real window parked off-screen, the northwest_check.py
pattern; NO Gusto API token exists on this Mac and this script never looks for credentials or types a
password; never a screenshot of anything but its own automation window):
  1 Opens the ONE shared automation profile ~/Library/Application Support/valleypawn/pw-vp through
    bin/vp_browser.py (2026-10-19; separate from Joshua's everyday Chrome; signed in ONCE by Joshua with
    bin/vp_signin_front.sh, ticking "Remember this device for 30 days"). vp_browser.prefs() sets
    session.restore_on_startup=1 + exit_type Normal before every launch so session cookies survive restarts
    (proof in vp_browser.py).
    - Sign-in / verification screen shown -> ONE ledger row a day ("Gusto needs a one-time sign-in in the
      automation browser — tick Remember this device for 30 days"), nothing posted, stop.
  2 https://app.gusto.com/payroll_admin/time_tracking -> the active pay period's Review -> reads the
    [aria-label="Clocked in"] / "On Break" / "Clocked out" status elements (PATH B of the task file),
    paginating, plus each clocked-in / on-break person's earliest clock-in time today (row text, else that
    person's timesheet page). A 12:00 AM clock-in = a rollover: use the next real clock-in and append
    _(shift rolled over from previous night)_.
    2026-10-20 (first signed-in render) fixes: the Legend above the table carries the same aria-labels and
    was read as three people — only elements inside a table row count now; the Review table shows 10 rows
    a page — "Items per page" is set to 50 before reading (and a one-page read of a paginated table with
    roster people missing = ledger row, no post); the Review row holds only pay-period totals, so the
    clock-in time comes from the person's timesheet page (name link -> today's date block -> earliest time).
  3 Store filter ("Who can appear"): each person's Gusto DEPARTMENT from the People list (same profile),
    cached daily in fleet/state/clockin/roster.json (yesterday's cache is used if today's read fails).
    Department must be Culpeper / Harrisonburg / Lexington / Roanoke / Waynesboro; last name Davis,
    Preston Peters and Sandi (Sandra) Cole never appear. Wednesday: Culpeper, Roanoke, Waynesboro only.
    Display overrides: Bridgett Grayson -> Bree Grayson; George (B) Moore -> Benjie Moore.
  4 Step 0 duplicate guard: a "Daily Clock-In Check" already in #general today -> post nothing (Wednesday:
    post only the Waynesboro supplement if the existing post covers Culpeper & Roanoke only).
  5 Posts the task file's exact format to #general as the ops bot (vp_slack.py: fleet publish guard +
    receipt are inside it). Never after 12:30 ET (a "10:15 AM" snapshot posted at lunch is wrong).

  clockin_check.py --render [--diag]   full read, prints the would-be post, NEVER posts; --diag also saves
                                       the pages' text/structure + screenshots to fleet/test_output/clockin/
                                       (no cookies) so selectors can be tightened after the first signed-in run
  clockin_check.py --probe             NO browser: playwright import, profile, roster cache, native_live
  clockin_check.py --send              (launchd wrapper; gated by vp_live.sh)
Failure policy v3: one FAILURE_LEDGER row, never a DM about a failure, never a failure note in a channel.
Rule 18: a post is built only from data this run actually read (or a same-week roster cache); otherwise
nothing is posted and the ledger says what was not read.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

AGENT = "daily-clockin-check"
ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE = os.path.join(OS_DIR, "fleet", "state", "clockin")
ROSTER = os.path.join(STATE, "roster.json")
TEST_OUT = os.path.join(OS_DIR, "fleet", "test_output", "clockin")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_people  # fleet-wide current-staff / no-Davis filter (2026-10-21)
import vp_browser  # the one automation profile + launch recipe (2026-10-19)
PROFILE = vp_browser.PROFILE
CH = "C03BETSS669"
MARKER = "Daily Clock-In Check"
TT_URL = "https://app.gusto.com/payroll_admin/time_tracking"
PEOPLE_URLS = ["https://app.gusto.com/payroll_admin/people",
               "https://app.gusto.com/payroll_admin/team_members",
               "https://app.gusto.com/payroll_admin/employees"]
DEPT_URL = "https://app.gusto.com/payroll_admin/departments"
STORES = ["Culpeper", "Harrisonburg", "Lexington", "Roanoke", "Waynesboro"]
WED_STORES = ["Culpeper", "Roanoke", "Waynesboro"]
NEVER = {"preston peters", "sandi cole", "sandra cole"}
OVERRIDES = {"bridgett grayson": "Bree Grayson", "george b moore": "Benjie Moore", "george moore": "Benjie Moore"}
STATUS_LABELS = {"Clocked in": "in", "On Break": "break", "Clocked out": "out"}
TIME_RX = re.compile(r"\b(\d{1,2}):(\d{2})\s*([AaPp])\.?[Mm]\.?")
SIGNIN_HINT = "yes, run bin/vp_signin_front.sh, sign in to Gusto once in that window (tick Remember this device for 30 days), then quit that window"
LATEST_SEND = dt.time(12, 30)

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
    """session.restore_on_startup = 1 + exit_type Normal on the shared profile (vp_browser.prefs; also run by launch())."""
    return vp_browser.prefs()
    return "restore_on_startup set to 1"


# ---------- names ----------
def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())).strip()


def clean_name(s):
    """'Tiglao, Uriah' / 'Uriah Tiglao (Store Manager)' / 'UT Uriah Tiglao' -> 'Uriah Tiglao'."""
    s = re.sub(r"\(.*?\)", " ", s or "")
    s = re.sub(r"[••|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,-")
    if "," in s and len(s.split(",")) == 2:
        last, first = [x.strip() for x in s.split(",")]
        s = "%s %s" % (first, last)
    parts = s.split()
    # a leading 2-letter all-caps token is an avatar initials badge (e.g. "UT Uriah Tiglao")
    if len(parts) >= 3 and re.fullmatch(r"[A-Z]{2}", parts[0]) and parts[0] == (parts[1][:1] + parts[-1][:1]).upper():
        parts = parts[1:]
    return " ".join(parts)


def nkey(name):
    """Match key: first + last token, so 'George B Moore' (People list) == 'George Moore' (timesheet)."""
    parts = norm(name).split()
    return (parts[0] + " " + parts[-1]) if len(parts) >= 2 else " ".join(parts)


def display_name(name):
    n = norm(name)
    for k, v in OVERRIDES.items():
        if n == k or n.startswith(k + " ") or n.endswith(" " + k):
            return v
    return name


def excluded(name):
    n = norm(name)
    parts = n.split()
    if not parts:
        return "empty"
    if parts[-1] == "davis":
        return "Davis family"
    if n in NEVER or any(n.startswith(x) for x in NEVER):
        return "never-listed (salaried manager / Preston)"
    return None


def _vp_reason(name):
    """Fleet-wide rule (Joshua 2026-10-21): current Gusto staff only, never a Davis — shared bin/vp_people.py,
    an ADDITIONAL filter on top of excluded(). Stale/missing roster = nobody passes -> the existing
    'no store employee matched' ledger path, nothing posted."""
    try:
        return vp_people.reason(name)
    except vp_people.RosterHold as e:
        return "roster hold: %s" % e


def store_of(dept):
    d = norm(dept)
    for s in STORES:
        if s.lower() in d:
            return s
    return None


def fmt_time(t):
    """'8:03 am' -> '8:03 AM'; returns None if not a time."""
    m = TIME_RX.search(t or "")
    if not m:
        return None
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3).upper()
    return "%d:%s %sM" % (h, mi, ap)


def time_key(t):
    m = TIME_RX.search(t or "")
    h, mi, ap = int(m.group(1)) % 12, int(m.group(2)), m.group(3).upper()
    return (h + (12 if ap == "P" else 0)) * 60 + mi


# ---------- page helpers ----------
STATUS_JS = """(labels) => {
  // 2026-10-20 (first signed-in render): the Legend above the table ("Clocked in / On Break / Clocked out")
  // carries the same aria-labels as the row dots and was read as three people. Only elements INSIDE a
  // table row count now; the legend has no row.
  const txt = e => (e.innerText || e.textContent || '').replace(/\\s+/g, ' ').trim();
  const out = [];
  for (const label of labels) {
    for (const el of document.querySelectorAll('[aria-label="' + label + '"]')) {
      const row = el.closest('tbody tr, tr, [role=row]');
      if (!row) continue;                                   // legend / anything outside the table
      const cells = Array.from(row.querySelectorAll('td, th, [role=cell], [role=gridcell]')).map(txt).filter(Boolean);
      // the person's name is the row's link/button whose text has 2+ words (Gusto renders it as a link)
      let nameEl = null;
      for (const c of row.querySelectorAll('a, button, [role=link], [role=button]')) {
        const t = txt(c); if (/[A-Za-z]{2,} [A-Za-z]/.test(t) && !/^(Clocked|On Break|Approved|Approve)/i.test(t)) { nameEl = c; break; }
      }
      const a = row.querySelector('a[href]');
      out.push({label, text: txt(row), cells, href: a ? a.href : null, self: txt(el),
                name_el: nameEl ? txt(nameEl) : null, name_tag: nameEl ? nameEl.tagName.toLowerCase() : null});
    }
  }
  return out;
}"""

PAGE_SIZE_RX = re.compile(r"Items per page", re.I)


def set_page_size(page, size="50"):
    """The Review table shows 10 rows a page (10 / 25 / 50 'Items per page'); pick 50 so one read holds everyone.
    Returns a short note of what worked (or None)."""
    if not PAGE_SIZE_RX.search(body_text(page, 20000)):
        return None
    for kind in ("radio", "button", "option", "link", "tab", "menuitemradio"):
        try:
            el = page.get_by_role(kind, name=re.compile(r"^\s*%s\s*$" % size)).first
            if el.count() and el.is_visible():
                el.click(timeout=4000)
                page.wait_for_timeout(2500)
                return "%s '%s'" % (kind, size)
        except Exception:
            pass
    try:
        sel = page.query_selector("select")
        if sel and sel.is_visible():
            sel.select_option(size)
            page.wait_for_timeout(2500)
            return "select '%s'" % size
    except Exception:
        pass
    try:
        el = page.get_by_text(size, exact=True).first
        if el.count() and el.is_visible():
            el.click(timeout=4000)
            page.wait_for_timeout(2500)
            return "text '%s'" % size
    except Exception:
        pass
    return None


# the Legend above the table matches the bare aria-label selector, so waits/checks use the ROW version
STATUS_SEL = "tbody tr [aria-label='Clocked in'], tbody tr [aria-label='Clocked out'], tbody tr [aria-label='On Break']"


def on_review(page):
    """True only on the Review TABLE: a person's timesheet page (…/timesheets/<id>) also shows a status dot
    (10/20 render 4), so the URL is checked too."""
    try:
        url = page.url or ""
        if "/timesheets/" in url or "time_tracking" not in url:
            return False
        return page.query_selector(STATUS_SEL) is not None
    except Exception:
        return False


def open_review(page, review_url):
    """Back to the Review table (direct URL), with the 50-per-page setting re-applied (it resets on reload).
    10/20 render 3: Gusto took > 20 s to paint the table once and three timesheets were skipped — so wait
    longer, and fall back to the Time tracking page -> 'Review' click. Returns True when the table is up."""
    for attempt in range(2):
        try:
            page.goto(review_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector(STATUS_SEL, timeout=45000)
        except Exception:
            try:
                page.goto(TT_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                if click_text(page, ["Review", "Review hours", "Review time", "Review timesheets"]):
                    page.wait_for_selector(STATUS_SEL, timeout=45000)
            except Exception:
                pass
        page.wait_for_timeout(1500)
        if on_review(page):
            set_page_size(page)
            return True
        log("review table not up after attempt %d (url %s)" % (attempt + 1, page.url.split("?")[0][:100]))
    return False

TABLE_JS = """() => {
  const txt = e => (e.innerText || '').replace(/\\s+/g, ' ').trim();
  const tables = Array.from(document.querySelectorAll('table'));
  const out = {url: location.href, title: document.title, tables: []};
  for (const t of tables) {
    const headers = Array.from(t.querySelectorAll('thead th, thead td')).map(txt);
    const rows = Array.from(t.querySelectorAll('tbody tr')).map(tr => {
      const cells = Array.from(tr.querySelectorAll('td, th')).map(txt);
      const a = tr.querySelector('a[href]');
      return {cells, text: txt(tr), href: a ? a.href : null};
    });
    out.tables.push({headers, rows});
  }
  if (!tables.length) {
    const rows = Array.from(document.querySelectorAll('[role=row]')).map(r => ({cells: Array.from(r.querySelectorAll('[role=cell], [role=gridcell], [role=columnheader]')).map(txt), text: txt(r), href: (r.querySelector('a[href]')||{}).href || null}));
    out.tables.push({headers: rows.length ? rows[0].cells : [], rows: rows.slice(1)});
  }
  out.body = txt(document.body).slice(0, 6000);
  return out;
}"""


def body_text(page, n=8000):
    try:
        return page.inner_text("body")[:n]
    except Exception:
        return ""


def classify(page):
    """'login' | 'verify' | 'tt' | 'other' from the current page."""
    url = (page.url or "").lower()
    body = body_text(page)
    low = body.lower()
    try:
        if page.query_selector("input[type=password]"):
            return "login", body
    except Exception:
        pass
    # 2026-10-18 render 1: signed-out app.gusto.com bounces to login.gusto.com (Keycloak, email-first page)
    if "login.gusto.com" in url or "accounts.gusto.com" in url or "/login" in url or "/signin" in url or "/sign_in" in url:
        return "login", body
    if page.query_selector("input[autocomplete=one-time-code]") or re.search(r"(verification|security|one-time) code|two-step|two-factor|verify (it's|its) you|remember this device", low):
        return "verify", body
    if "time_tracking" in url and ("time" in low):
        return "tt", body
    if "app.gusto.com" in url and re.search(r"\bsign in\b|\blog in\b", low) and not re.search(r"\bsign out\b|\blog out\b", low):
        return "login", body
    return "other", body


def save_diag(page, name, extra=None):
    if not DIAG:
        return
    os.makedirs(TEST_OUT, exist_ok=True)
    try:
        page.screenshot(path=os.path.join(TEST_OUT, "%s.png" % name), full_page=True)
    except Exception:
        pass
    try:
        d = page.evaluate(TABLE_JS)
        if extra:
            d["extra"] = extra
        json.dump(d, open(os.path.join(TEST_OUT, "%s.json" % name), "w"), indent=1)
    except Exception as e:
        open(os.path.join(TEST_OUT, "%s.txt" % name), "w").write(page.url + "\n" + body_text(page) + "\n[diag error %s]" % e)


def click_text(page, labels, timeout=4000):
    for label in labels:
        try:
            el = page.get_by_role("link", name=re.compile(r"^\s*%s\s*$" % re.escape(label), re.I)).first
            if el.count() and el.is_visible():
                el.click(timeout=timeout)
                return label
        except Exception:
            pass
        try:
            el = page.get_by_role("button", name=re.compile(r"^\s*%s\s*$" % re.escape(label), re.I)).first
            if el.count() and el.is_visible():
                el.click(timeout=timeout)
                return label
        except Exception:
            pass
    return None


def next_page(page):
    """Click a 'next page' control if it exists and is enabled. Returns True if clicked."""
    for sel in ("button[aria-label*='next' i]:not([disabled])", "a[aria-label*='next' i]", "[data-testid*='next' i]:not([disabled])",
                "button:has-text('Next'):not([disabled])", "li.next a", "a[rel=next]"):
        try:
            el = page.query_selector(sel)
            if el and el.is_visible() and el.is_enabled() and (el.get_attribute("aria-disabled") or "false") != "true":
                el.click(timeout=4000)
                page.wait_for_timeout(2500)
                return True
        except Exception:
            continue
    return False


def read_statuses(page):
    """All status rows on the Review page, across pages. [{name, status, time, href, text}]"""
    out, seen = [], set()
    note = set_page_size(page)
    if note:
        log("review table: items per page ->", note)
    for pg in range(25):
        rows = page.evaluate(STATUS_JS, list(STATUS_LABELS))
        if DIAG:
            log("review page %d: %d status rows" % (pg + 1, len(rows)))
        for r in rows:
            cells = r.get("cells") or []
            # the name: the row's link/button text first, else the first cell that reads like a name
            cand = clean_name(r.get("name_el") or "")
            if not (cand and re.search(r"[A-Za-z]{2,} [A-Za-z]", cand)):
                cand = None
                for c in (cells or [r.get("text", "")]):
                    c2 = re.sub(r"\b(Clocked in|On Break|Clocked out)\b", " ", c, flags=re.I).strip()
                    c2 = clean_name(c2)
                    if c2 and re.search(r"[A-Za-z]{2,} [A-Za-z]", c2) and not TIME_RX.search(c2) and not re.search(r"\d", c2):
                        cand = c2
                        break
            if not cand:
                continue                      # a row with no person's name in it (never a status word as a name)
            name = re.split(r"\s{2,}", cand)[0][:60]
            key = (norm(name), r["label"])
            if key in seen:
                continue
            seen.add(key)
            times = [fmt_time(m.group(0)) for m in TIME_RX.finditer(r.get("text", ""))]
            out.append({"name": name, "status": STATUS_LABELS[r["label"]], "times_in_row": times,
                        "href": r.get("href"), "name_tag": r.get("name_tag"), "text": r.get("text", "")[:200]})
        if not next_page(page):
            break
    return out


DATE_LABEL_RX = re.compile(
    r"(?:(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})(?!\d)"
    r"|(?<![\d/])(\d{1,2})/(\d{1,2})(?:/\d{2,4})?(?![\d/])")
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def today_segment(body, today):
    """The slice of a timesheet page's text that belongs to today: from today's date label to the next
    different date label. Pay-period range labels ("Oct 19 - Oct 25") are skipped. None if no label."""
    marks = []
    for m in DATE_LABEL_RX.finditer(body):
        if m.group(1):
            mo, d = MONTHS.get(m.group(1).lower()[:3]), int(m.group(2))
        else:
            mo, d = int(m.group(3)), int(m.group(4))
        if not mo or not (1 <= d <= 31):
            continue
        before, after = body[max(0, m.start() - 3):m.start()], body[m.end():m.end() + 3]
        if before.strip().endswith("-") or after.strip().startswith("-"):
            continue                                  # half of a "Oct 19 - Oct 25" range
        marks.append((m.start(), m.end(), (mo, d)))
    want = (today.month, today.day)
    for i, (s, e, md) in enumerate(marks):
        if md != want:
            continue
        end = len(body)
        for s2, e2, md2 in marks[i + 1:]:
            if md2 != want:
                end = s2
                break
        seg = body[e:end]
        if TIME_RX.search(seg):
            return seg[:4000]
    return None


def open_timesheet(page, person, review_url=None):
    """Open one person's timesheet from the Review table (name link/button). True if the page changed."""
    before = page.url
    name = person["name"]
    rx = re.compile(r"^\s*%s\s*$" % re.escape(name), re.I)
    if person.get("href"):
        try:
            page.goto(person["href"], wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2500)
            return page.url != before
        except Exception:
            pass
    def visible_name():
        for kind in ("link", "button"):
            try:
                el = page.get_by_role(kind, name=rx).first
                if el.count() and el.is_visible():
                    return el
            except Exception:
                pass
        try:
            el = page.get_by_text(name, exact=True).first
            if el.count() and el.is_visible():
                return el
        except Exception:
            pass
        return None

    el = visible_name()
    if el is None:
        # 10/20 render: the table paginates (10 rows) — the person may be on another page. Filter with the
        # table's own "Search team members" box first (poll up to 12 s: render 5 showed 2.5 s is too short),
        # else reload the table at page 1 and page forward until the name shows.
        try:
            box = page.get_by_placeholder(re.compile(r"search team members", re.I)).first
            if box.count() and box.is_visible():
                box.fill(name)
                for _ in range(12):
                    page.wait_for_timeout(1000)
                    el = visible_name()
                    if el is not None:
                        break
        except Exception:
            pass
    if el is None and review_url:
        try:
            open_review(page, review_url)
        except Exception:
            pass
        el = visible_name()
        for _ in range(10):
            if el is not None or not next_page(page):
                break
            el = visible_name()
    if el is None:
        return False
    try:
        el.click(timeout=5000)
        page.wait_for_timeout(3500)
        return page.url != before
    except Exception:
        return False


def earliest_today(page, person, today, review_url=None):
    """Earliest clock-in today for one person: from the Review row text, else from their timesheet page.
    Returns (time_str or None, rolled_over bool)."""
    times = list(person.get("times_in_row") or [])
    if not times:
        # the Review row carries only pay-period totals (10/20 render) — the time is on the timesheet page
        try:
            if open_timesheet(page, person, review_url):
                if DIAG:
                    save_diag(page, "timesheet-%s" % norm(person["name"]).replace(" ", "_"))
                body = body_text(page, 30000)
                seg = today_segment(body, today)
                if seg is None:
                    log("timesheet for %s: no block for today's date found (url %s)" % (person["name"], page.url.split("?")[0][:100]))
                else:
                    times = [fmt_time(m.group(0)) for m in TIME_RX.finditer(seg)]
                    log("timesheet for %s: today's times %s" % (person["name"], times))
            else:
                log("timesheet for %s: could not open it from the Review table" % person["name"])
        except Exception as e:
            log("timesheet read failed for %s: %s" % (person["name"], str(e)[:80]))
    times = [t for t in times if t]
    if not times:
        return None, False
    times.sort(key=time_key)
    if times[0] == "12:00 AM":
        real = [t for t in times if t != "12:00 AM"]
        return (real[0] if real else None), True
    return times[0], False


def read_roster(page):
    """{name -> department} from the People list (then the Departments page), or None if nothing readable."""
    found = {}
    for url in PEOPLE_URLS:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # 10/20 render 3: a 3 s wait read an EMPTY table on a slow load and the run fell through to the
            # Departments page, which produced a one-name garbage roster. Wait for real rows first.
            try:
                page.wait_for_selector("table tbody tr td", timeout=45000)
            except Exception:
                pass
            page.wait_for_timeout(2000)
        except Exception:
            continue
        if "login" in (page.url or "").lower():
            return None
        for _ in range(15):
            d = page.evaluate(TABLE_JS)
            if not any(t.get("rows") for t in d.get("tables", [])):
                page.wait_for_timeout(5000)              # one more chance for a slow paint
                d = page.evaluate(TABLE_JS)
            if DIAG:
                save_diag(page, "people-%d" % _)
            for t in d.get("tables", []):
                hdr = [h.lower() for h in t.get("headers", [])]
                di = next((i for i, h in enumerate(hdr) if "department" in h), None)
                ni = next((i for i, h in enumerate(hdr) if "name" in h or "employee" in h or "person" in h), 0)
                if di is None:
                    continue
                for r in t.get("rows", []):
                    c = r.get("cells") or []
                    if len(c) > max(di, ni):
                        nm = clean_name(c[ni])
                        if nm and re.search(r"[A-Za-z]{2,} [A-Za-z]", nm):
                            found[nm] = c[di].strip()
            if not next_page(page):
                break
        if found:
            log("roster: %d people with a department from %s" % (len(found), url.rsplit("/", 1)[-1]))
            return found
    # Departments page: each department's member list
    try:
        page.goto(DEPT_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        if DIAG:
            save_diag(page, "departments")
        body = body_text(page, 30000)
        for s in STORES:
            m = re.search(r"\b%s\b(.{0,2500}?)(?=\b(?:%s)\b|$)" % (s, "|".join(x for x in STORES if x != s) + "|Corporate|Marketing"), body, re.S)
            if not m:
                continue
            for nm in re.findall(r"\b([A-Z][a-zA-Z'\-]+(?: [A-Z]\.?)? [A-Z][a-zA-Z'\-]+)\b", m.group(1)):
                found.setdefault(clean_name(nm), s)
    except Exception as e:
        log("departments page failed:", str(e)[:80])
    if found:
        log("roster: %d people from the Departments page" % len(found))
        return found
    return None


MIN_ROSTER_STORE_PEOPLE = 5


def roster_sane(roster, statuses):
    """A roster is trusted (and cached) only if it names at least MIN_ROSTER_STORE_PEOPLE store people AND
    covers most of the people the Review table listed. Render 3 (10/20) produced {'Social Media': 'Roanoke'}."""
    if not roster:
        return False
    store_people = sum(1 for nm, d in roster.items() if store_of(d))
    if store_people < MIN_ROSTER_STORE_PEOPLE:
        return False
    keys = {nkey(k) for k in roster}
    names = [s["name"] for s in statuses]
    if names:
        covered = sum(1 for n in names if nkey(n) in keys)
        if covered < 0.6 * len(names):
            return False
    return True


def load_cache(today):
    try:
        c = json.load(open(ROSTER))
        d = dt.date.fromisoformat(c["date"])
        if (today - d).days <= 7:
            return c["people"], d
    except Exception:
        pass
    return None, None


def save_cache(today, people):
    os.makedirs(STATE, exist_ok=True)
    json.dump({"date": today.isoformat(), "people": people}, open(ROSTER, "w"), indent=1)


# ---------- main read ----------
def read_live(today):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ledger("The clock-in check could not run because the automation browser is not installed on the Mac.")
        sys.exit(3)
    log("prefs:", ensure_prefs())
    statuses, roster, notes = [], None, []
    with sync_playwright() as p:
        try:
            ctx = vp_browser.launch(p, headless=vp_browser.headless_from_env("GUSTO_HEADLESS"))
        except Exception as e:
            log("launch failed:", str(e)[:300])
            ledger("The clock-in check could not open its automation browser (it may be open for sign-in), so nothing was posted.")
            sys.exit(3)
        try:
            page = vp_browser.first_page(ctx)
            page.goto(TT_URL, wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_selector("input[type=password], input[type=email], [aria-label='Clocked in'], [aria-label='Clocked out'], [aria-label='On Break'], table", timeout=30000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            kind, body = classify(page)
            log("page state:", kind, "|", page.url.split("?")[0])
            save_diag(page, "state-%s" % kind)
            if kind in ("login", "verify"):
                if once_per_day("signin"):
                    ledger("Gusto needs a one-time sign-in in the automation browser — tick Remember this device for 30 days", SIGNIN_HINT)
                sys.exit(4)
            if kind != "tt":
                page.goto(TT_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
                kind, body = classify(page)
                if kind != "tt":
                    save_diag(page, "state-unexpected")
                    ledger("The clock-in check signed in but could not open the time tracking page, so nothing was posted.")
                    sys.exit(6)
            # the active pay period's Review
            statuses = read_statuses(page)
            if not statuses:
                clicked = click_text(page, ["Review", "Review hours", "Review time", "Review timesheets"])
                if clicked:
                    page.wait_for_timeout(4000)
                    notes.append("opened %r" % clicked)
                    try:
                        page.wait_for_selector("[aria-label='Clocked in'], [aria-label='Clocked out'], [aria-label='On Break']", timeout=20000)
                    except Exception:
                        pass
                    save_diag(page, "review")
                    statuses = read_statuses(page)
            if not statuses:
                save_diag(page, "review-empty")
                ledger("The clock-in check opened the time tracking page but found no clock-in status entries on it, so nothing was posted.")
                sys.exit(7)
            review_url = page.url
            # pagination guard (Rule 18): if the table paginates and the read stopped at one page's worth,
            # the people on later pages were never read — say so instead of listing them as not clocked in
            paginated = bool(PAGE_SIZE_RX.search(body_text(page, 20000)))
            if paginated and len(statuses) in (10, 25):
                notes.append("WARNING: review table paginates and exactly %d rows were read — later pages may be unread" % len(statuses))
            for s in statuses:
                if s["status"] in ("in", "break"):
                    if not on_review(page):
                        try:
                            open_review(page, review_url)
                        except Exception as e:
                            log("open_review failed:", str(e)[:80])
                    s["time"], s["rolled"] = earliest_today(page, s, today, review_url)
            roster = read_roster(page)
        finally:
            vp_browser.close(ctx)
    return statuses, roster, notes


# ---------- build ----------
def build(today, statuses, roster, wed, supplement_only=False):
    """Returns (post_text, rows) applying Who-can-appear. roster = {name: department}."""
    stores = WED_STORES if wed else STORES
    if supplement_only:
        stores = ["Waynesboro"]
    rmap = {nkey(k): v for k, v in roster.items()}
    allowed, dropped = {}, []
    for nm, dept in roster.items():
        why = excluded(nm) or _vp_reason(nm)
        st = store_of(dept)
        if why:
            dropped.append((nm, why))
        elif not st:
            dropped.append((nm, "department %r is not a store" % dept))
        elif st not in stores:
            dropped.append((nm, "%s is closed today" % st))
        else:
            allowed[nkey(nm)] = (nm, st)
    by_name = {}
    for s in statuses:
        k = nkey(s["name"])
        if k not in allowed:
            if k not in rmap:
                dropped.append((s["name"], "not in the roster read (no department)"))
            continue
        by_name[k] = s
    cin, brk, out, unread = [], [], [], []
    for k, (nm, st) in sorted(allowed.items(), key=lambda kv: kv[1][0].split()[-1] + kv[1][0]):
        s = by_name.get(k)
        disp = display_name(nm)
        if s and s["status"] == "in":
            cin.append((disp, s.get("time"), s.get("rolled")))
        elif s and s["status"] == "break":
            brk.append((disp, s.get("time"), s.get("rolled")))
        else:
            if s is None:
                unread.append(disp)       # on the roster but no status row read for them (not on time tracking, or an unread page)
            out.append(disp)

    def line(d, t, rolled):
        l = "• %s — clocked in at %s" % (d, t) if t else "• %s — clocked in" % d
        return l + (" _(shift rolled over from previous night)_" if rolled else "")

    date = today.strftime("%A, %B %-d, %Y")
    if supplement_only:
        head = "🕙 *Valley Pawn — Daily Clock-In Check (Waynesboro)* | %s @ 10:15 AM" % date
    elif wed:
        head = "🕙 *Valley Pawn — Daily Clock-In Check (Culpeper, Roanoke & Waynesboro)* | %s @ 10:15 AM" % date
    else:
        head = "🕙 *Valley Pawn — Daily Clock-In Check* | %s @ 10:15 AM" % date
    parts = [head]
    if wed and not supplement_only:
        parts.append("_Harrisonburg and Lexington are closed on Wednesdays._")
    total = len(cin) + len(brk) + len(out)
    if cin and not brk and not out:
        parts.append("✅ All %d employees are clocked in. Great start to the day!" % total)
    if cin:
        parts.append("")
        parts.append("🟢 *Clocked In (%d)*" % len(cin))
        parts.extend(line(*x) for x in cin)
    if brk:
        parts.append("")
        parts.append("🟡 *On Break (%d)*" % len(brk))
        parts.extend(line(*x) for x in brk)
    if out:
        parts.append("")
        parts.append("🔴 *Not Clocked In (%d)*" % len(out))
        parts.extend("• %s" % d for d in out)
    return "\n".join(parts), {"in": cin, "break": brk, "out": out, "dropped": dropped, "unread": unread}


def slack_has(marker, hours=14):
    env = dict(os.environ, VP_TASK=AGENT)
    r = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "has", CH, marker, str(hours)],
                       capture_output=True, text=True, env=env)
    if r.returncode not in (0, 1):
        log("slack has failed:", (r.stderr or r.stdout).strip()[:120])
        return None
    return r.returncode == 0


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
    people, d = load_cache(dt.datetime.now(ET).date())
    print("roster cache:", ("%d people, dated %s" % (len(people), d)) if people else "none")
    print("native_live:", os.path.exists(os.path.join(OS_DIR, "fleet/state/native_live", AGENT)))


def main():
    if "--probe" in sys.argv:
        probe()
        return 0
    now = dt.datetime.now(ET)
    today = dt.date.fromisoformat(arg("--date")) if arg("--date") else now.date()
    wed = today.weekday() == 2
    if today.weekday() == 6 and not RENDER:
        log("Sunday — stores closed, nothing to check")
        return 0
    if not RENDER and now.time() > LATEST_SEND and "--force" not in sys.argv:
        if once_per_day("late"):
            ledger("The clock-in check did not run in its morning window today, so no clock-in summary was posted (a late snapshot would be wrong).")
        return 0
    # Step 0 — duplicate guard
    supplement = False
    if not RENDER:
        found = slack_has(MARKER)
        if found:
            if not wed or slack_has("Clock-In Check (Culpeper, Roanoke & Waynesboro)") or slack_has("Clock-In Check (Waynesboro)"):
                log("already posted today — not posting again")
                return 0
            supplement = True
            log("Wednesday: today's post covers Culpeper & Roanoke only — Waynesboro supplement")
    statuses, roster, notes = read_live(today)
    for n in notes:
        log("note:", n)
    log("status entries read: %d (in %d, break %d, out %d)" % (len(statuses), sum(s["status"] == "in" for s in statuses),
                                                                  sum(s["status"] == "break" for s in statuses), sum(s["status"] == "out" for s in statuses)))
    cache_note = ""
    if roster and not roster_sane(roster, statuses):
        log("roster: live read looks wrong (%d entries: %s) — not trusted, not cached" % (len(roster), ", ".join(list(roster)[:5])))
        roster = None
    if roster:
        save_cache(today, roster)
    else:
        roster, d = load_cache(today)
        if roster and not roster_sane(roster, statuses):
            log("roster: cache dated %s looks wrong too — ignored" % d)
            roster = None
        if roster:
            cache_note = "roster from cache dated %s" % d
            log("roster: live read failed —", cache_note)
        else:
            ledger("The clock-in check read the time tracking page but could not read which store each employee belongs to (no roster today and no recent cache), so nothing was posted.")
            return 2
    post, rows = build(today, statuses, roster, wed, supplement_only=supplement)
    for nm, why in rows["dropped"]:
        log("  dropped:", nm, "—", why)
    if rows["unread"]:
        log("  no status row read for (listed as not clocked in):", ", ".join(rows["unread"]))
        if any(n.startswith("WARNING") for n in notes):
            # Rule 18: a paginated table read one page's worth and people are missing — their status was never seen
            ledger("The clock-in check could only read the first page of the time tracking table, so some employees' status was not seen and nothing was posted.")
            return 2
    for s in statuses:
        if s["status"] in ("in", "break") and not s.get("time"):
            log("  no clock-in time read for", s["name"])
    os.makedirs(STATE, exist_ok=True)
    json.dump({"checked": now.isoformat(timespec="seconds"), "statuses": statuses, "roster_note": cache_note, "post": post, "rows": rows},
              open(os.path.join(TEST_OUT if RENDER else STATE, "last_run.json"), "w"), indent=1, default=str)
    if not (rows["in"] or rows["break"] or rows["out"]):
        ledger("The clock-in check ran but no store employee matched today's roster filter, so nothing was posted.")
        return 2
    if RENDER:
        print(post)
        log("[render] nothing posted")
        return 0
    env = dict(os.environ, VP_TASK=AGENT)
    r = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CH, post], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        ledger("The clock-in check ran but its #general post did not go through.")
        log("FAIL post:", (r.stderr or r.stdout).strip()[:200])
        return 1
    log("posted", r.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
