#!/usr/bin/env python3
"""email_test_loop.py — closed-loop A/B testing for the Thursday weekly email.

WHY (2026-11-17, Joshua: "you give feedback but never follow or execute your recommendations"):
the Friday report recommended changes that nothing ever applied. This script makes every
recommendation a real test on the next send, grades it, and promotes winners automatically.

  apply  [--thursday YYYY-MM-DD] [--render]   Mon 13:15 after the deal picker (retry Tue/Wed):
         1. applies every PROMOTED winner to this Thursday's queued weekly (the control)
         2. if a test is active: splits the weekly audience (lists 7 + 13) into two random halves,
            control -> half A, a cloned variant "<name> [B]" -> half B, same send time, both + seeds (list 10)
         Safety: the variant is created only after the control is verified on half A; any failure after
         that deletes the variant and restores the control to [7, 10, 13]. Never both to everyone.
  grade  [--render]                           Fri 03:45 after email_analytics_weekly: scores the active test,
         decides WIN / LOSE / NO DIFFERENCE, promotes winners, starts the next queued test.
  status                                      one line for the Friday report (also used by compose()).
  probe                                       read-only dump of the next weekly campaign + list sizes.

Metric: store actions per 1,000 delivered = call + text + directions clicks (UTM buckets *_call, *_text,
*_map / deal_of_week_*), the same buckets email_analytics_weekly.py counts.
Decision (2026-11-21): counts UNIQUE PEOPLE with a store action, mail-scanner clicks removed (human_clicks).
Needs >=2 sends and >=8 such people across both halves; WIN/LOSE by exact binomial test at 90% confidence;
after 6 sends with no clear result -> NO DIFFERENCE, the control stays. A variant whose unsubscribe rate
runs 0.3 points above control (3+ unsubs) loses regardless.
Levers it may touch: top strips, preview text, subject. Never offers, discounts, loan/legal copy, audiences.
No Slack. Failures -> fleet/FAILURE_LEDGER.md (one plain row) and the run log; next run retries.
"""
import datetime as dt, hashlib, json, math, os, re, subprocess, sys, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HOME = os.path.expanduser("~")
ER = os.path.join(HOME, "Documents/Claude/Projects/Email Refinement")
ROOT = os.environ.get("VP_TESTLOOP_DIR") or os.path.join(ER, "test_loop")
STATE = os.path.join(ROOT, "state.json")
BACKLOG = os.path.join(ROOT, "backlog.json")
LOG_MD = os.path.join(ROOT, "RESULTS.md")
PREFLIGHT = os.path.join(ER, "brevo_preflight.py")
LEDGER = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
AUDIENCE = [7, 13]          # weekly audience since the 2026-10-20 audit (Engaged + new store contacts)
SEEDS = 10
STORES = ["culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"]
MIN_SENDS, MIN_ACTIONS, MAX_SENDS, ALPHA = 2, 8, 6, 0.10
TASK = "email-test-loop"
_K = None


# ---------------------------------------------------------------- plumbing
def key():
    global _K
    if _K is None:
        _K = open(os.path.join(HOME, ".config/valley-pawn/brevo_api_key")).read().strip()
    return _K


def b(path, payload=None, method=None):
    r = urllib.request.Request("https://api.brevo.com/v3" + path, data=json.dumps(payload).encode() if payload is not None else None,
                               method=method or ("POST" if payload is not None else "GET"),
                               headers={"api-key": key(), "accept": "application/json", "content-type": "application/json"})
    with urllib.request.urlopen(r, timeout=90) as x:
        d = x.read()
        return json.loads(d) if d else {}


def load(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def save(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, default=str)
    os.replace(tmp, path)


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (
            dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))
    except OSError:
        pass


def label_for(thu):
    return "%s %d, %d" % (thu.strftime("%B"), thu.day, thu.year)


def lists_of(c):
    return [l["id"] if isinstance(l, dict) else l for l in ((c.get("recipients") or {}).get("lists") or [])]


# ---------------------------------------------------------------- state
def state():
    s = load(STATE, {})
    s.setdefault("active", None)          # test id
    s.setdefault("weeks", {})             # thursday iso -> {test, control_id, variant_id, status}
    s.setdefault("promoted", [])          # test ids whose transforms are now applied to every control
    s.setdefault("results", {})           # test id -> decision record
    s.setdefault("lists", {})             # {"A": id, "B": id}
    return s


def backlog():
    return load(BACKLOG, {"tests": []})


def test_by_id(tid):
    for t in backlog()["tests"]:
        if t["id"] == tid:
            return t
    return None


def next_test(s):
    done = set(s["results"]) | set(s["promoted"])
    for t in backlog()["tests"]:
        if t.get("status", "queued") == "queued" and t["id"] not in done:
            return t["id"]
    return None


# ---------------------------------------------------------------- transforms
def own_links(html, kind):
    """kind: text|call|map -> {store: href} taken from the email's own tracked links (no guessed URLs)."""
    out = {}
    for href in re.findall(r'href="([^"]+)"', html):
        h = href.replace("&amp;", "&")
        for s in STORES:
            if s in out:
                continue
            if kind == "text" and re.search(r"/t/%s\b" % s, h):
                out[s] = href
            elif kind == "call" and re.search(r"/c/%s\b" % s, h):
                out[s] = href
            elif kind == "map" and s in h.lower() and re.search(r"utm_content=[^&\"]*_map\b", h):
                out[s] = href
    return out


def retag(href, store, suffix, tid):
    """same destination, utm_content=loop_<test>_<store>_<suffix> (still ends _text/_call/_map, so the report counts it)."""
    tag = "loop_%s_%s_%s" % (re.sub(r"[^a-z0-9]", "", tid.lower())[:12], store, suffix)
    if "utm_content=" in href:
        return re.sub(r"utm_content=[^&\"]*", "utm_content=" + tag, href)
    return href + ("&amp;" if "?" in href else "?") + "utm_content=" + tag


def link_row(html, kind, suffix, tid):
    links = own_links(html, kind)
    if len(links) < 5:
        return None
    a = ['<a href="%s" style="color:inherit;text-decoration:underline;">%s</a>' % (retag(links[s], s, suffix, tid), s.title())
         for s in STORES]
    return " &middot; ".join(a)


def apply_transforms(html, subject, tid, transforms):
    """-> (html, subject) or raises ValueError (test cannot apply to this email)."""
    marker = "<!-- loop:%s -->" % tid
    if marker in html:
        return html, subject
    for t in transforms:
        if t["type"] == "subject":
            subject = t["value"].replace("{{SUBJECT}}", subject or "")
        elif t["type"] == "insert_after_body":
            snip = t["html"]
            for ph, kind, suf in (("{{TEXT_LINKS}}", "text", "text"), ("{{CALL_LINKS}}", "call", "call"), ("{{MAP_LINKS}}", "map", "map")):
                if ph in snip:
                    row = link_row(html, kind, suf, tid)
                    if not row:
                        raise ValueError("email has fewer than 5 %s links" % kind)
                    snip = snip.replace(ph, row)
            snip = marker + snip
            m = re.search(r"<body[^>]*>", html)
            at = m.end() if m else 0
            if "display:none" not in t["html"]:
                # a visible strip goes AFTER the email's own hidden preview text, so the inbox preview is unchanged
                pre = re.match(r"\s*(?:<!--.*?-->\s*)?<div[^>]*display:\s*none[^>]*>.*?</div>", html[at:], re.S)
                if pre:
                    at += pre.end()
            html = html[:at] + snip + html[at:]
        elif t["type"] == "replace":
            new, n = re.subn(t["pattern"], t["value"], html)
            if not n:
                raise ValueError("pattern not found: %s" % t["pattern"][:60])
            html = new.replace("</body>", marker + "</body>", 1) if "</body>" in new else new + marker
        else:
            raise ValueError("unknown transform %s" % t["type"])
    return html, subject


# ---------------------------------------------------------------- audience split
def list_emails(lid):
    out, off = [], 0
    while True:
        d = b("/contacts/lists/%d/contacts?limit=500&offset=%d" % (lid, off))
        cs = d.get("contacts") or []
        out += [c["email"].lower() for c in cs if c.get("email") and not c.get("emailBlacklisted")]
        if len(cs) < 500:
            return out
        off += 500


def bucket(email, tid):
    return "B" if int(hashlib.sha256((tid + "|" + email).encode()).hexdigest(), 16) % 2 else "A"


def ensure_lists(s):
    names = {"A": "Weekly test loop - half A (auto)", "B": "Weekly test loop - half B (auto)"}
    have = {l.get("name"): l["id"] for l in b("/contacts/lists?limit=50").get("lists", [])}
    folder = None
    for side in ("A", "B"):
        if s["lists"].get(side) and s["lists"][side] in have.values():
            continue
        if names[side] in have:
            s["lists"][side] = have[names[side]]
            continue
        if folder is None:
            fs = b("/contacts/folders?limit=50").get("folders", [])
            folder = fs[0]["id"] if fs else b("/contacts/folders", {"name": "Automation"})["id"]
        s["lists"][side] = b("/contacts/lists", {"name": names[side], "folderId": folder})["id"]
    return s["lists"]


def fill_split(s, tid):
    ids = ensure_lists(s)
    emails = sorted(set(e for lid in AUDIENCE for e in list_emails(lid)))
    halves = {"A": [e for e in emails if bucket(e, tid) == "A"], "B": [e for e in emails if bucket(e, tid) == "B"]}
    for side in ("A", "B"):
        lid = ids[side]
        try:
            b("/contacts/lists/%d/contacts/remove" % lid, {"all": True})
        except urllib.error.HTTPError as e:
            if e.code != 400:      # 400 = list already empty
                raise
        for i in range(0, len(halves[side]), 150):
            b("/contacts/lists/%d/contacts/add" % lid, {"emails": halves[side][i:i + 150]})
    return len(emails), len(halves["A"]), len(halves["B"])


# ---------------------------------------------------------------- apply
def preflight(cid):
    p = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(cid)], capture_output=True, text=True, timeout=300)
    return p.returncode == 0, (p.stdout + p.stderr)[-600:]


def apply(render=False):
    s = state()
    now = dt.datetime.now(ET)
    thu = dt.date.fromisoformat(sys.argv[sys.argv.index("--thursday") + 1]) if "--thursday" in sys.argv \
        else now.date() + dt.timedelta(days=(3 - now.weekday()) % 7)
    lab, wk = label_for(thu), thu.isoformat()
    queued = [c for c in b("/emailCampaigns?status=queued&limit=50&sort=desc&excludeHtmlContent=true").get("campaigns", [])
              if lab in (c.get("name") or "") and "[B]" not in (c.get("name") or "")]
    if not queued:
        print("no queued weekly for %s yet — nothing to do (the picker/watchdog own scheduling)" % lab)
        return 0
    ctl = b("/emailCampaigns/%d" % queued[0]["id"])
    html, subject = ctl.get("htmlContent") or "", ctl.get("subject") or ""
    skip = (backlog().get("skip_weeks") or {}).get(wk)
    closed = re.search(r"closed\s+today", re.sub(r"<[^>]+>", " ", html), re.I)
    if skip or closed:
        # 2026-11-21: no test on a day the stores are closed ("a real person answers" would be false) — full audience, unsplit
        print("week %s not tested (%s) — #%d goes to everyone as is" % (wk, skip or "email says the stores are closed", ctl["id"]))
        return 0
    if "/t/" not in html or "/c/" not in html:
        print("#%d has no call/text buttons (community-only send) — excluded from testing" % ctl["id"])
        return 0

    # 1. promoted winners -> the control, every week
    new_html, new_subj = html, subject
    for tid in s["promoted"]:
        t = test_by_id(tid)
        if not t:
            continue
        try:
            new_html, new_subj = apply_transforms(new_html, new_subj, tid, t["transforms"])
        except ValueError as e:
            print("promoted %s skipped on #%d: %s" % (tid, ctl["id"], e))
    if (new_html, new_subj) != (html, subject):
        print("control #%d: applying promoted winners %s" % (ctl["id"], s["promoted"]))
        if not render:
            b("/emailCampaigns/%d" % ctl["id"], {"htmlContent": new_html, "subject": new_subj}, "PUT")
            ok, out = preflight(ctl["id"])
            if not ok:
                b("/emailCampaigns/%d" % ctl["id"], {"htmlContent": html, "subject": subject}, "PUT")
                ledger("Weekly email %s: a promoted test winner failed the pre-send check, so the email went back to its original version." % lab)
                print("preflight failed, reverted:", out)
                new_html, new_subj = html, subject
        html, subject = new_html, new_subj

    # 2. the active test
    if not s["active"]:
        s["active"] = next_test(s)
    tid = s["active"]
    w = s["weeks"].get(wk)
    if not tid:
        print("no test queued — control only"); save(STATE, s) if not render else None; return 0
    if w and w.get("status") == "applied":
        print("week %s already split for %s (#%s / #%s)" % (wk, w["test"], w["control_id"], w["variant_id"])); return 0
    t = test_by_id(tid)
    try:
        v_html, v_subj = apply_transforms(html, subject, tid, t["transforms"])
    except ValueError as e:
        s["results"][tid] = {"decision": "SKIPPED", "why": str(e), "at": now.isoformat()}
        s["active"] = next_test(s)
        print("test %s cannot apply (%s) — retired, next: %s" % (tid, e, s["active"]))
        if not render:
            save(STATE, s)
        return 0
    if render:
        open(os.path.join(ROOT, "render_variant_%s.html" % wk), "w").write(v_html)
        print("RENDER: would split #%d for %s, variant subject=%r, html +%d chars" % (ctl["id"], tid, v_subj, len(v_html) - len(html)))
        return 0

    orig_lists = lists_of(ctl)
    n, na, nb = fill_split(s, tid)
    A, B = s["lists"]["A"], s["lists"]["B"]
    variant = None
    try:
        b("/emailCampaigns/%d" % ctl["id"], {"recipients": {"listIds": [A, SEEDS]}}, "PUT")
        if sorted(lists_of(b("/emailCampaigns/%d" % ctl["id"]))) != sorted([A, SEEDS]):
            raise RuntimeError("control recipients did not take")
        variant = b("/emailCampaigns", {"name": (ctl.get("name") or lab) + " [B]", "subject": v_subj,
                                         "sender": {"name": ctl["sender"]["name"], "email": ctl["sender"]["email"]},
                                         "replyTo": ctl.get("replyTo"), "htmlContent": v_html,
                                         "recipients": {"listIds": [B, SEEDS]}})["id"]
        ok, out = preflight(variant)
        if not ok:
            raise RuntimeError("variant failed the pre-send check: " + out[-200:])
        b("/emailCampaigns/%d" % variant, {"scheduledAt": ctl["scheduledAt"]}, "PUT")
        v = b("/emailCampaigns/%d" % variant)
        if v.get("status") not in ("queued", "inProcess") or sorted(lists_of(v)) != sorted([B, SEEDS]):
            raise RuntimeError("variant not queued (status %s)" % v.get("status"))
    except Exception as e:
        if variant:
            try:
                b("/emailCampaigns/%d" % variant, method="DELETE")
            except Exception:
                pass
        b("/emailCampaigns/%d" % ctl["id"], {"recipients": {"listIds": orig_lists or [7, SEEDS, 13]}}, "PUT")
        ledger("Weekly email %s: the A/B split for test %s did not set up, so the email goes out normally to everyone; it retries next run." % (lab, tid))
        print("split failed, restored control:", type(e).__name__, e)
        return 1
    s["weeks"][wk] = {"test": tid, "control_id": ctl["id"], "variant_id": variant, "status": "applied",
                      "audience": n, "A": na, "B": nb, "at": now.isoformat()}
    save(STATE, s)
    md("%s | %s | split #%d (A, %d) vs #%d (B, %d)" % (wk, tid, ctl["id"], na, variant, nb))
    print("split ok: #%d -> A (%d) / #%d -> B (%d), test %s" % (ctl["id"], na, variant, nb, tid))
    return 0


# ---------------------------------------------------------------- grade
def is_action(tag):
    return tag.endswith("_call") or tag.endswith("_text") or tag.endswith("_map") or tag.startswith("deal_of_week_")


def _ts(v):
    try:
        return dt.datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def is_scanner(links):
    """A mail-security scanner opens many links at once; a person does not.
    2026-11-21: on the 11/19 send Brevo's totals showed 134 clicks; contact-level data showed 6 clickers, 2 of them
    scanners (5 strip links in 2 s; 4 links of one store block in 2 s). Rule: 3+ different links inside 30 s, or
    2+ different links inside 3 s."""
    t = sorted(_ts(l.get("eventTime")) for l in links)
    n = len(t)
    for i in range(n):
        if i + 2 < n and t[i + 2] - t[i] <= 30:
            return True
        if i + 1 < n and t[i + 1] - t[i] <= 3:
            return True
    return False


CLICK_CACHE = os.path.join(ROOT, "clicks_cache.json")


def human_clicks(cids, max_age_h=6):
    """{cid: {"actors", "callers", "texters", "mappers", "clickers", "scanners"}} — UNIQUE PEOPLE, scanners removed.
    Reads every weekly-audience contact's own click history (lists 7 + 13; the internal seed list is never counted).
    ~15 min for ~900 contacts, cached for 6 h so the Friday report and the grade share one pull."""
    import time
    cids = sorted(set(int(c) for c in cids))
    cache = load(CLICK_CACHE, {})
    if cache.get("at") and (dt.datetime.now(ET) - dt.datetime.fromisoformat(cache["at"])).total_seconds() < max_age_h * 3600 \
            and set(cids) <= set(cache.get("cids", [])):
        return {int(k): v for k, v in cache["data"].items() if int(k) in cids}
    data = {c: {"actors": 0, "callers": 0, "texters": 0, "mappers": 0, "clickers": 0, "scanners": 0} for c in cids}
    emails = sorted(set(e for lid in AUDIENCE for e in list_emails(lid)))
    for e in emails:
        c = None
        for attempt in range(4):
            try:
                c = b("/contacts/" + urllib.parse.quote(e)); break
            except urllib.error.HTTPError as ex:
                if ex.code == 404:
                    break
                time.sleep(2 + 3 * attempt)
            except Exception:
                time.sleep(2 + 3 * attempt)
        else:
            raise RuntimeError("contact history unavailable")
        for ev in ((c or {}).get("statistics") or {}).get("clicked") or []:
            cid = int(ev.get("campaignId", 0))
            if cid not in data:
                continue
            links = ev.get("links") or []
            if is_scanner(links):
                data[cid]["scanners"] += 1
                continue
            tags = [(re.search(r"utm_content=([^&#]+)", urllib.parse.unquote(l.get("url", "").replace("&amp;", "&"))) or [None, ""])[1] for l in links]
            data[cid]["clickers"] += 1
            data[cid]["callers"] += any(t.endswith("_call") for t in tags)
            data[cid]["texters"] += any(t.endswith("_text") for t in tags)
            data[cid]["mappers"] += any(t.endswith("_map") or t.startswith("deal_of_week_") for t in tags)
            data[cid]["actors"] += any(is_action(t) for t in tags)
        time.sleep(0.05)
    save(CLICK_CACHE, {"at": dt.datetime.now(ET).isoformat(), "cids": cids, "contacts": len(emails), "data": data})
    return data


def delivered_unsubs(cid):
    st = (b("/emailCampaigns/%d" % cid).get("statistics") or {})
    rows = st.get("campaignStats") or []
    return (sum(int(x.get("delivered") or x.get("sent") or 0) for x in rows), sum(int(x.get("unsubscriptions") or 0) for x in rows))


def binom_tail(k, n, p):
    """P(X >= k), X ~ Binomial(n, p) — exact; the counts here are far too small for a z-test."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def decide(A, Bv, sends):
    """A/Bv = (delivered, people who took a store action, unsubs). -> (decision or None, confidence, why)."""
    (na, xa, ua), (nb, xb, ub) = A, Bv
    if na == 0 or nb == 0:
        return None, 0.0, "no delivered counts yet"
    if ub >= 3 and (ub / nb - ua / na) * 100 >= 0.3:
        return "LOSE", 0.0, "variant drove extra unsubscribes"
    k, share = xa + xb, nb / float(na + nb)
    p_win = binom_tail(xb, k, share) if k else 1.0          # chance of the variant doing this well by luck
    p_lose = binom_tail(xa, k, 1 - share) if k else 1.0
    conf = round(1 - min(p_win, p_lose), 3)
    if sends < MIN_SENDS or k < MIN_ACTIONS:
        if sends >= MAX_SENDS:
            return "NO DIFFERENCE", conf, "too few store actions after %d sends" % sends
        return None, conf, "needs %d sends and %d people taking a store action (has %d, %d)" % (MIN_SENDS, MIN_ACTIONS, sends, k)
    if p_win <= ALPHA:
        return "WIN", conf, ""
    if p_lose <= ALPHA:
        return "LOSE", conf, ""
    if sends >= MAX_SENDS:
        return "NO DIFFERENCE", conf, ""
    return None, conf, "too close to call yet"


def tally(s, tid, today):
    A, Bv, sends, pairs = [0, 0, 0], [0, 0, 0], 0, []
    for wk, w in sorted(s["weeks"].items()):
        if w.get("test") != tid or w.get("status") != "applied":
            continue
        if (today - dt.date.fromisoformat(wk)).days < 3:
            continue
        pairs.append((w["control_id"], w["variant_id"]))
    if pairs:
        hc = human_clicks([c for p in pairs for c in p])
        for ctl, var in pairs:
            for tot, cid in ((A, ctl), (Bv, var)):
                d, u = delivered_unsubs(cid)
                tot[0] += d; tot[1] += hc[cid]["actors"]; tot[2] += u
            sends += 1
    return tuple(A), tuple(Bv), sends


def grade(render=False):
    s = state()
    today = dt.datetime.now(ET).date()
    tid = s["active"]
    if not tid:
        s["active"] = next_test(s)
        print("no active test; next:", s["active"])
        if not render:
            save(STATE, s)
        return 0
    A, Bv, sends = tally(s, tid, today)
    dec, z, why = decide(A, Bv, sends)
    rate = lambda t: (1000.0 * t[1] / t[0]) if t[0] else 0.0
    s["last_grade"] = {"test": tid, "at": today.isoformat(), "sends": sends, "A": A, "B": Bv, "confidence": z,
                       "decision": dec, "why": why, "rate_A": round(rate(A), 2), "rate_B": round(rate(Bv), 2)}
    print("grade %s: sends=%d A=%s B=%s confidence=%.2f -> %s %s" % (tid, sends, A, Bv, z, dec or "RUNNING", why))
    if dec and not render:
        s["results"][tid] = dict(s["last_grade"])
        if dec == "WIN":
            s["promoted"].append(tid)
        s["active"] = next_test(s)
        md("%s | %s | %s — control %.1f vs variant %.1f store actions per 1,000 over %d sends (%d vs %d people, confidence %.0f%%). Next: %s" % (
            today.isoformat(), tid, dec, rate(A), rate(Bv), sends, A[1], Bv[1], 100 * z, s["active"] or "backlog empty"))
    if not render:
        save(STATE, s)
    return 0


def status_line(s=None):
    s = s or state()
    g = s.get("last_grade") or {}
    names = {t["id"]: t.get("hypothesis", t["id"]) for t in backlog()["tests"]}
    if g.get("decision"):
        res = {"WIN": "won — it is now on every weekly", "LOSE": "lost — dropped", "NO DIFFERENCE": "made no difference — dropped",
               "SKIPPED": "could not run — dropped"}[g["decision"]]
        head = "Test result: %s %s (%.1f vs %.1f store actions per 1,000 over %d sends)." % (
            g["test"], res, g.get("rate_B", 0), g.get("rate_A", 0), g.get("sends", 0))
        return head + (" Next test: %s, starts Thursday." % s["active"] if s.get("active") else " Backlog empty.")
    if s.get("active") and g.get("test") == s["active"] and g.get("sends"):
        return "Test running: %s — %d people took a store action from the new version vs %d from the current one after %d send%s (%s)." % (
            s["active"], g["B"][1], g["A"][1], g["sends"], "" if g["sends"] == 1 else "s", g.get("why") or "close")
    if s.get("active"):
        ran = sorted(wk for wk, w in s.get("weeks", {}).items() if w.get("test") == s["active"] and w.get("status") == "applied")
        if ran and ran[-1] <= dt.datetime.now(ET).date().isoformat():
            return "Test running: %s — half the list got it on %s; scored once 2 sends are in." % (
                s["active"], ", ".join(ran))
        return "Test starting Thursday: %s — %s" % (s["active"], names.get(s["active"], ""))
    return None


def md(line):
    new = not os.path.exists(LOG_MD)
    with open(LOG_MD, "a") as f:
        if new:
            f.write("# Weekly email test loop — results log\n\nWritten by bin/email_test_loop.py. Newest last.\n\n")
        f.write("- " + line + "\n")


# ---------------------------------------------------------------- probe
def probe():
    out = os.path.join(ROOT, "probe")
    os.makedirs(out, exist_ok=True)
    summ = {"at": dt.datetime.now(ET).isoformat(), "campaigns": [], "lists": {}}
    for st in ("queued", "draft", "sent"):
        for c in b("/emailCampaigns?status=%s&limit=30&sort=desc&excludeHtmlContent=true" % st).get("campaigns", [])[:12]:
            summ["campaigns"].append({"id": c["id"], "name": c.get("name"), "status": st, "subject": c.get("subject"),
                                      "scheduledAt": c.get("scheduledAt"), "lists": lists_of(c)})
    for c in [c for c in summ["campaigns"] if c["status"] == "queued"][:2]:
        open(os.path.join(out, "camp_%d.html" % c["id"]), "w").write(b("/emailCampaigns/%d" % c["id"]).get("htmlContent") or "")
    for l in b("/contacts/lists?limit=50").get("lists", []):
        summ["lists"][l["id"]] = {"name": l.get("name"), "n": l.get("uniqueSubscribers", l.get("totalSubscribers"))}
    save(os.path.join(out, "summary.json"), summ)
    print("probe ok:", len(summ["campaigns"]), "campaigns")


def clickdump(cids):
    """read-only: per-contact click events for the two test halves on the given campaigns -> probe/clicks_<ids>.json"""
    import time
    st = state()
    emails = sorted(set(e for side in ("A", "B") for e in list_emails(st["lists"][side])))
    out = []
    for e in emails:
        try:
            c = b("/contacts/" + urllib.parse.quote(e))
        except Exception as ex:
            out.append({"email": e, "error": type(ex).__name__}); continue
        ev = [x for x in ((c.get("statistics") or {}).get("clicked") or []) if int(x.get("campaignId", 0)) in cids]
        if ev:
            out.append({"id": c.get("id"), "lists": c.get("listIds"), "clicked": ev})
        time.sleep(0.12)
    save(os.path.join(ROOT, "probe", "clicks_%s.json" % "_".join(map(str, cids))), {"n_contacts": len(emails), "clickers": out})
    print("clickdump ok: %d contacts, %d with clicks" % (len(emails), len(out)))


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    render = "--render" in sys.argv
    try:
        if cmd == "apply":
            sys.exit(apply(render))
        if cmd == "grade":
            sys.exit(grade(render))
        if cmd == "status":
            print(status_line() or "(no test)"); sys.exit(0)
        if cmd == "probe":
            probe(); sys.exit(0)
        if cmd == "clickdump":
            clickdump([int(x) for x in sys.argv[2:] if x.isdigit()]); sys.exit(0)
        print(__doc__); sys.exit(2)
    except Exception as e:
        print("ERROR", type(e).__name__, e)
        if not render and cmd in ("apply", "grade"):
            ledger("The weekly email test loop (%s) did not complete (%s); it retries on its next run." % (cmd, type(e).__name__))
        sys.exit(1)
