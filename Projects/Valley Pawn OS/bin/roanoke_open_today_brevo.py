#!/usr/bin/env python3
"""
roanoke_open_today_brevo.py — "Roanoke open today" same-day reminder (Joshua 2026-10-07). Cloned from roanoke_wed_brevo.py (untouched).
  --verify78   read-only: status + stats of the 10/2 announcement #78
  --go         build (lists 21+10) -> preflight -> test -> schedule 11:00 ET -> re-GET verify
  --sent       read-only: status/stats of the new campaign
Original doc follows.
 Host only; stdlib.

Precedent: Valley Pawn OS/_brevo_hours_inspect.py / _brevo_hours_patch.py / _brevo_announce_build.py (2026-07-23).

  --inspect              read-only. Templates + every NOT-SENT campaign: hours contexts. Lists, segments,
                         attributes, STORE=Roanoke counts. Saves ORIGINAL html (first run only) to
                         Valley Pawn OS/brevo_backups_2026-10-01_roanokewed/ + inspect_report.json.
  --patch                Roanoke store block -> "Roanoke · Mon–Sat 10am–6pm"; old footer hours line -> new
                         canonical line. ACTIVE templates + draft/queued/scheduled/suspended campaigns only.
                         Never touches sent / in_process. Pre-patch copy saved; re-GET verifies.
  --build                Create (or update, idempotent by name) the announcement campaign from
                         Email Refinement/roanoke_open_wednesdays_2026-10-02.html, recipients = --lists.
                         Runs Email Refinement/brevo_preflight.py, then sends a TEST to jdavis@fcfpawn.com.
  --schedule             Re-runs preflight; schedules for 2026-10-02 10:00 America/New_York; re-GET verifies.
  --roanoke-list         Builds list "Roanoke customers (STORE=Roanoke) 2026-10" from STORE attribute.
  --lists 3,10           list ids for --build
"""
import functools, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
print = functools.partial(print, flush=True)

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents", "Claude", "Projects")
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
BK = os.path.join(OS_DIR, "brevo_backups_2026-10-07_roanoketoday")
HTML_FILE = os.path.join(PROJ, "Email Refinement", "roanoke_open_today_2026-10-07.html")
PREFLIGHT = os.path.join(PROJ, "Email Refinement", "brevo_preflight.py")
API = "https://api.brevo.com/v3"
KEY = open(os.path.join(HOME, ".config", "valley-pawn", "brevo_api_key")).read().strip()

CAMPAIGN_NAME = "Roanoke Open Today — Wednesday Reminder — 2026-10-07"
SUBJECT = "Roanoke, we're open today (yes, Wednesday)"
PREVIEW = "Open today 10am–6pm at 2362 Peters Creek Road — and every Wednesday from now on."
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
TEST_TO = ["jdavis@fcfpawn.com"]
SCHEDULE_AT = "2026-10-07T11:00:00-04:00"
ROANOKE_LIST_NAME = "Roanoke customers (STORE=Roanoke) — 2026-10"

os.makedirs(BK, exist_ok=True)


def req(method, path, body=None, tries=12):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for a in range(tries):
        r = urllib.request.Request(API + path, data=data, method=method,
                                   headers={"api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw.strip() else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # honour Brevo's reset header (2026-10-01: blind 3..96s backoff lost 3 calls to a long window)
                reset = e.headers.get("x-sib-ratelimit-reset") or e.headers.get("Retry-After") or ""
                try: wait = min(max(float(reset), 1.0) + 1, 600)
                except ValueError: wait = 5 * (2 ** min(a, 6))
                print(f"  429 on {method} {path[:60]} — waiting {wait:.0f}s (limit={e.headers.get('x-sib-ratelimit-limit')}, try {a+1})", flush=True)
                time.sleep(wait); continue
            return e.code, e.read().decode(errors="replace")
        except Exception as e:
            last = str(e); time.sleep(3)
    return 599, last or "rate-limited"


# ---------------------------------------------------------------- patterns
DASH = r"(?:–|&ndash;|&#8211;|-)"
AMP = r"(?:&amp;|&)"
# Roanoke store block: "Roanoke &middot; Mon, Tue, Thu, Fri & Sat 10am–6pm"
RE_ROA = re.compile(r"(Roanoke\s*(?:&middot;|·|&#183;)\s*)Mon,\s*Tue,\s*Thu,\s*Fri\s*" + AMP + r"\s*Sat(\s*10am)(" + DASH + r")(6pm)")
# footer line (any entity style)
RE_FOOT = re.compile(r"Culpeper:\s*Mon(" + DASH + r")Sat\s*10am" + DASH + r"6pm\.\s*All other stores:\s*Mon,\s*Tue,\s*Thu,\s*Fri\s*("
                     + AMP + r")\s*Sat\s*10am" + DASH + r"6pm\s*\(closed Wed\s*" + AMP + r"\s*Sun\)\.?")
NEW_FOOT_MARK = "Harrisonburg, Waynesboro"
# staged-draft CTA sub-line (build_calendar drafts 55-70): "Mon, Tue, Thu, Fri & Sat 10am–6pm. Closed Wed & Sun."
RE_CTA = re.compile(r"(<p[^>]*>)\s*Mon,\s*Tue,\s*Thu,\s*Fri\s*(" + AMP + r")\s*Sat\s*10am(" + DASH + r")6pm\.\s*Closed Wed\s*" + AMP + r"\s*Sun\.\s*(</p>)")
MASTER_TEMPLATES = (11, 48)   # inactive in Brevo but read by pipelines (forfeiture win-back reads 11; 48 = weekly standard)


def new_footer(m):
    d, a = m.group(1), m.group(2)
    return (f"Culpeper {a} Roanoke: Mon{d}Sat 10am{d}6pm. Harrisonburg, Waynesboro {a} Lexington: "
            f"Mon, Tue, Thu, Fri {a} Sat 10am{d}6pm (closed Wed {a} Sun).")


def patch_html(h):
    h2, n1 = RE_ROA.subn(lambda m: f"{m.group(1)}Mon{m.group(3)}Sat{m.group(2)}{m.group(3)}{m.group(4)}", h)
    h3, n2 = RE_FOOT.subn(new_footer, h2)
    h4, n3 = RE_CTA.subn(lambda m: m.group(1) + new_footer_from(m.group(3), m.group(2)) + m.group(4), h3)
    h5, n4 = re.subn(r"Open Mon(?:–|&ndash;)Sat\. Culpeper also open Wednesday\.", new_footer_from("&ndash;", "&amp;"), h4)
    return h5, n1, n2 + n3 + n4


def new_footer_from(d, a):
    return (f"Culpeper {a} Roanoke: Mon{d}Sat 10am{d}6pm. Harrisonburg, Waynesboro {a} Lexington: "
            f"Mon, Tue, Thu, Fri {a} Sat 10am{d}6pm (closed Wed {a} Sun).")


def contexts(h, pats=(r"[Cc]losed\s*Wed", r"All other stores", r"Wednesday", r"Roanoke\s*(?:&middot;|·)[^<]{0,60}",
                      r"Mon,\s*Tue,\s*Thu[^<]{0,40}", NEW_FOOT_MARK)):
    out = []
    no_c = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    for p in pats:
        for m in re.finditer(p, no_c):
            s = max(0, m.start() - 90)
            out.append(f"[{p[:18]}] …{no_c[s:m.end() + 60]}…".replace("\n", " "))
    return out


def save(name, text, overwrite=False):
    p = os.path.join(BK, name)
    if overwrite or not os.path.exists(p):
        open(p, "w").write(text)
    return p


# ---------------------------------------------------------------- collect
def all_templates():
    out, off = [], 0
    while True:
        st, r = req("GET", f"/smtp/templates?limit=100&offset={off}")
        if st != 200:
            print("templates list error", st, str(r)[:200]); break
        ts = r.get("templates", [])
        out += ts
        if len(ts) < 100: break
        off += 100
    return out


def unsent_campaigns():
    out = []
    for status in ("draft", "queued", "suspended", "in_process"):
        off = 0
        while True:
            st, r = req("GET", f"/emailCampaigns?status={status}&limit=100&offset={off}&excludeHtmlContent=true")
            if st != 200:
                print("campaign list error", status, st, str(r)[:200]); break
            cs = r.get("campaigns", []) or []
            out += cs
            if len(cs) < 100: break
            off += 100
    # Brevo has no "scheduled" filter value in some API versions; queued covers scheduled. Try anyway.
    st, r = req("GET", "/emailCampaigns?status=scheduled&limit=100&excludeHtmlContent=true")
    if st == 200:
        seen = {c["id"] for c in out}
        out += [c for c in (r.get("campaigns") or []) if c["id"] not in seen]
    return out


def store_count(store):
    f = urllib.parse.quote(f'equals(STORE,"{store}")')
    st, r = req("GET", f"/contacts?limit=1&filter={f}")
    return r.get("count") if st == 200 else f"err {st} {str(r)[:120]}"


# ---------------------------------------------------------------- modes
def do_inspect():
    rep = {"templates": [], "campaigns": [], "lists": [], "segments": None, "attributes": [], "store_counts": {}}
    print("===== TEMPLATES =====")
    for t in all_templates():
        st, full = req("GET", f"/smtp/templates/{t['id']}")
        h = full.get("htmlContent", "") if st == 200 else ""
        _, n1, n2 = patch_html(h)
        hit = bool(n1 or n2 or re.search(r"[Cc]losed\s*Wed|All other stores", h))
        print(f"T{t['id']} active={t.get('isActive')} '{t.get('name')}' len={len(h)} roanoke_block={n1} old_footer={n2} new_footer={NEW_FOOT_MARK in h}")
        if hit or t["id"] in (11, 48):
            save(f"template_{t['id']}.orig.html", h)
            for c in contexts(h): print("    ", c[:260])
        rep["templates"].append({"id": t["id"], "name": t.get("name"), "active": t.get("isActive"), "roanoke_block": n1,
                                 "old_footer": n2, "tokens": sorted(set(re.findall(r"\[\[([A-Z_]+)\]\]", h)))})
    print("\n===== NOT-SENT CAMPAIGNS =====")
    for c in unsent_campaigns():
        st, full = req("GET", f"/emailCampaigns/{c['id']}")
        h = full.get("htmlContent", "") if st == 200 else ""
        _, n1, n2 = patch_html(h)
        lists = (full.get("recipients") or {}).get("lists")
        print(f"C{c['id']} [{full.get('status')}] '{full.get('name')}' sched={full.get('scheduledAt')} lists={lists} roanoke_block={n1} old_footer={n2} new_footer={NEW_FOOT_MARK in h}")
        save(f"campaign_{c['id']}.orig.html", h)
        for x in contexts(h): print("    ", x[:260])
        rep["campaigns"].append({"id": c["id"], "name": full.get("name"), "status": full.get("status"),
                                 "scheduledAt": full.get("scheduledAt"), "lists": lists, "roanoke_block": n1, "old_footer": n2,
                                 "subject": full.get("subject"), "sender": full.get("sender")})
    print("\n===== LISTS =====")
    off = 0
    while True:
        st, r = req("GET", f"/contacts/lists?limit=50&offset={off}")
        if st != 200: print("lists err", st, r); break
        for l in r.get("lists", []):
            print(f"  list {l['id']} '{l['name']}' subs={l.get('totalSubscribers')} blacklisted={l.get('totalBlacklisted')} folder={l.get('folderId')}")
            rep["lists"].append(l)
        if len(r.get("lists", [])) < 50: break
        off += 50
    print("\n===== SEGMENTS =====")
    st, r = req("GET", "/contacts/segments?limit=50")
    print(" ", st, json.dumps(r)[:1500])
    rep["segments"] = r
    print("\n===== ATTRIBUTES =====")
    st, r = req("GET", "/contacts/attributes")
    for a in (r.get("attributes", []) if st == 200 else []):
        if a.get("category") in ("normal", "category"):
            enum = a.get("enumeration")
            print(f"  {a['name']} type={a.get('type')} cat={a.get('category')}" + (f" enum={enum}" if enum else ""))
            rep["attributes"].append(a)
    print("\n===== STORE attribute counts (all contacts) =====")
    for s in ("Roanoke", "Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "roanoke", "ROANOKE"):
        n = store_count(s); rep["store_counts"][s] = n
        print(f"  STORE={s}: {n}")
    st, r = req("GET", "/contacts?limit=1")
    print("  total contacts:", r.get("count") if st == 200 else st)
    st, r = req("GET", "/senders")
    print("\n===== SENDERS =====\n ", json.dumps(r)[:600])
    save("inspect_report.json", json.dumps(rep, indent=1, default=str), overwrite=True)
    print("\nINSPECT DONE — originals in", BK)


ONLY_IDS = []


def do_patch():
    log = []
    print("===== PATCH TEMPLATES (active + masters 11/48) =====")
    for t in ([] if ONLY_IDS else all_templates()):
        st, full = req("GET", f"/smtp/templates/{t['id']}")
        if st != 200: continue
        h = full.get("htmlContent", "")
        h2, n1, n2 = patch_html(h)
        if h2 == h: continue
        if not t.get("isActive") and t["id"] not in MASTER_TEMPLATES:
            print(f"T{t['id']} '{t.get('name')}' INACTIVE — has old hours (roanoke={n1} footer={n2}) — NOT patched"); continue
        save(f"template_{t['id']}.orig.html", h)
        save(f"template_{t['id']}.prepatch.html", h, overwrite=True)
        st, r = req("PUT", f"/smtp/templates/{t['id']}", {"htmlContent": h2})
        st2, chk = req("GET", f"/smtp/templates/{t['id']}")
        h3 = chk.get("htmlContent", "")
        _, r1, r2 = patch_html(h3)
        ok = st in (200, 204) and h3 == h2 and r1 == 0 and r2 == 0
        save(f"template_{t['id']}.new.html", h3, overwrite=True)
        print(f"T{t['id']} '{t.get('name')}' PUT {st} roanoke={n1} footer={n2} -> verify {'OK' if ok else 'MISMATCH ' + str(r)[:200]}")
        for c in contexts(h3): print("    ", c[:260])
        log.append({"kind": "template", "id": t["id"], "put": st, "roanoke": n1, "footer": n2, "verified": ok})
    print("\n===== PATCH NOT-SENT CAMPAIGNS =====")
    cands = [{"id": i} for i in ONLY_IDS] if ONLY_IDS else unsent_campaigns()
    for c in cands:
        st, full = req("GET", f"/emailCampaigns/{c['id']}")
        if st != 200:
            print(f"C{c['id']}: GET FAILED {st} {str(full)[:150]} — NOT patched", flush=True); continue
        status = full.get("status")
        if status in ("sent", "in_process", "archive") or (full.get("name") or "").startswith("CANCELLED"):
            print(f"C{c['id']} [{status}] skipped"); continue
        h = full.get("htmlContent", "")
        h2, n1, n2 = patch_html(h)
        if h2 == h:
            continue
        save(f"campaign_{c['id']}.orig.html", h)
        save(f"campaign_{c['id']}.prepatch.html", h, overwrite=True)
        st, r = req("PUT", f"/emailCampaigns/{c['id']}", {"htmlContent": h2})
        st2, chk = req("GET", f"/emailCampaigns/{c['id']}")
        if status == "queued" and chk.get("status") != "queued" and full.get("scheduledAt"):
            rs, rr = req("PUT", f"/emailCampaigns/{c['id']}", {"scheduledAt": full["scheduledAt"]})
            print(f"  C{c['id']} status changed to {chk.get('status')} by the edit — re-scheduled to {full['scheduledAt']}: HTTP {rs} {str(rr)[:150]}")
            st2, chk = req("GET", f"/emailCampaigns/{c['id']}")
        h3 = chk.get("htmlContent", "")
        _, r1, r2 = patch_html(h3)
        ok = st in (200, 204) and r1 == 0 and r2 == 0
        save(f"campaign_{c['id']}.new.html", h3, overwrite=True)
        print(f"C{c['id']} [{status}->{chk.get('status')}] '{full.get('name')}' sched={chk.get('scheduledAt')} PUT {st} roanoke={n1} footer={n2} -> verify {'OK' if ok else 'FAIL ' + str(r)[:200]}")
        for x in contexts(h3): print("    ", x[:260])
        log.append({"kind": "campaign", "id": c["id"], "name": full.get("name"), "status_before": status,
                    "status_after": chk.get("status"), "sched": chk.get("scheduledAt"), "put": st, "roanoke": n1, "footer": n2, "verified": ok})
    save("patch_log.json" if not ONLY_IDS else "patch_log_ids.json", json.dumps(log, indent=1), overwrite=True)
    print("PATCH DONE")


def find_campaign_by_name(name):
    for status in ("draft", "queued", "suspended"):
        st, r = req("GET", f"/emailCampaigns?status={status}&limit=100&excludeHtmlContent=true")
        for c in (r.get("campaigns") or []) if st == 200 else []:
            if c.get("name") == name:
                return c["id"]
    return None


def preflight(cid):
    pf = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(cid)], capture_output=True, text=True)
    print(f"preflight C{cid}: rc={pf.returncode}\n{pf.stdout}{pf.stderr[-800:]}")
    return pf.returncode


def do_build(lists):
    if lists == "roanoke":
        lists = [int(open(os.path.join(BK, "roanoke_list_id.txt")).read().strip()), 10]
    html = open(HTML_FILE).read()
    left = sorted(set(re.findall(r"\[\[[A-Z_]+\]\]", html)))
    if left: raise SystemExit(f"unfilled markers: {left}")
    body = {"name": CAMPAIGN_NAME, "subject": SUBJECT, "previewText": PREVIEW, "sender": SENDER, "replyTo": REPLY_TO,
            "htmlContent": html, "recipients": {"listIds": lists}, "inlineImageActivation": False, "mirrorActive": True}
    cid = find_campaign_by_name(CAMPAIGN_NAME)
    if cid:
        st, r = req("PUT", f"/emailCampaigns/{cid}", body); print(f"UPDATED existing campaign {cid}: {st} {str(r)[:200]}")
    else:
        st, r = req("POST", "/emailCampaigns", body)
        if st >= 300: raise SystemExit(f"create failed {st} {r}")
        cid = r["id"]; print(f"CREATED campaign {cid}")
    save("announce_campaign_id.txt", str(cid), overwrite=True)
    st, c = req("GET", f"/emailCampaigns/{cid}")
    print(f"  name={c.get('name')!r} status={c.get('status')} subject={c.get('subject')!r} preview={c.get('previewText')!r}")
    print(f"  sender={c.get('sender')} replyTo={c.get('replyTo')} lists={(c.get('recipients') or {}).get('lists')}")
    rc = preflight(cid)
    if rc != 0: raise SystemExit("PREFLIGHT FAILED — no test, not scheduled")
    st, r = req("POST", f"/emailCampaigns/{cid}/sendTest", {"emailTo": TEST_TO})
    print(f"TEST SEND to {TEST_TO}: HTTP {st} {str(r)[:300]}")
    st, c = req("GET", f"/emailCampaigns/{cid}")
    save("announce_campaign.live.html", c.get("htmlContent", ""), overwrite=True)


def do_schedule():
    cid = int(open(os.path.join(BK, "announce_campaign_id.txt")).read().strip())
    if preflight(cid) != 0: raise SystemExit("PREFLIGHT FAILED — not scheduled")
    st, r = req("PUT", f"/emailCampaigns/{cid}", {"scheduledAt": SCHEDULE_AT})
    print(f"SCHEDULE PUT {st} {str(r)[:300]}")
    st, c = req("GET", f"/emailCampaigns/{cid}")
    print(f"VERIFY C{cid}: status={c.get('status')} scheduledAt={c.get('scheduledAt')} lists={(c.get('recipients') or {}).get('lists')}")
    for l in (c.get("recipients") or {}).get("lists") or []:
        st, li = req("GET", f"/contacts/lists/{l}")
        print(f"  list {l} '{li.get('name')}' subs={li.get('totalSubscribers')} blacklisted={li.get('totalBlacklisted')}")


def do_roanoke_list():
    f = urllib.parse.quote('equals(STORE,"Roanoke")')
    emails, off = [], 0
    while True:
        st, r = req("GET", f"/contacts?limit=1000&offset={off}&filter={f}")
        if st != 200: raise SystemExit(f"contacts err {st} {r}")
        cs = r.get("contacts", [])
        emails += [c["email"] for c in cs if c.get("email") and not c.get("emailBlacklisted")]
        if len(cs) < 1000: break
        off += 1000
    print(f"STORE=Roanoke deliverable contacts: {len(emails)}")
    st, r = req("GET", "/contacts/lists?limit=50")
    lid = next((l["id"] for l in r.get("lists", []) if l["name"] == ROANOKE_LIST_NAME), None)
    if not lid:
        st, r = req("POST", "/contacts/lists", {"name": ROANOKE_LIST_NAME, "folderId": 1})
        if st >= 300: raise SystemExit(f"list create {st} {r}")
        lid = r["id"]
    for i in range(0, len(emails), 150):
        req("POST", f"/contacts/lists/{lid}/contacts/add", {"emails": emails[i:i + 150]})
    time.sleep(30)
    st, li = req("GET", f"/contacts/lists/{lid}")
    print(f"ROANOKE LIST id={lid} subs={li.get('totalSubscribers')} blacklisted={li.get('totalBlacklisted')}")
    save("roanoke_list_id.txt", str(lid), overwrite=True)


ROA_LIST = 21   # "Roanoke customers (STORE=Roanoke) — 2026-10" built 10/1
SEED_LIST = 10


def camp_report(cid):
    st, c = req("GET", f"/emailCampaigns/{cid}?statistics=globalStats&excludeHtmlContent=true")
    if st != 200:
        print(f"C{cid}: HTTP {st} {str(c)[:300]}"); return
    g = ((c.get("statistics") or {}).get("globalStats")) or {}
    print(f"C{cid} {c.get('name')!r}: status={c.get('status')} sentDate={c.get('sentDate')} scheduledAt={c.get('scheduledAt')} lists={(c.get('recipients') or {}).get('lists')}")
    print(f"   sent={g.get('sent')} delivered={g.get('delivered')} uniqueViews={g.get('uniqueViews')} uniqueClicks={g.get('uniqueClicks')} unsub={g.get('unsubscriptions')} hardBounces={g.get('hardBounces')}")


def do_go():
    st, li = req("GET", f"/contacts/lists/{ROA_LIST}")
    print(f"list {ROA_LIST} {li.get('name')!r} subs={li.get('totalSubscribers')}")
    if st != 200 or "Roanoke" not in (li.get("name") or ""):
        raise SystemExit("list 21 is not the Roanoke list — STOP")
    do_build([ROA_LIST, SEED_LIST])
    do_schedule()


AREA_LIST_NAME = "Roanoke-area customers (no STORE, ZIP 240/241) — 2026-10-07"
AREA_CITIES = {"roanoke", "salem", "vinton", "cave spring", "hollins", "daleville", "troutville", "cloverdale",
               "fincastle", "buchanan", "bedford", "moneta", "boones mill", "rocky mount", "christiansburg",
               "blacksburg", "radford", "bent mountain", "catawba", "goodview", "hardy", "thaxton", "blue ridge"}


def do_area():
    st, a = req("GET", "/contacts/attributes")
    names = [x.get("name") for x in a.get("attributes", [])] if st == 200 else []
    print("attributes:", names)
    zipk = next((n for n in names if n.upper() in ("ZIP", "ZIPCODE", "ZIP_CODE", "POSTAL_CODE", "POSTCODE")), None)
    cityk = next((n for n in names if n.upper() in ("CITY", "TOWN")), None)
    print("zip attr:", zipk, " city attr:", cityk)
    if not (zipk or cityk):
        print("no ZIP/CITY attribute — area expansion not possible"); return
    st, r = req("GET", f"/contacts/lists/{ROA_LIST}/contacts?limit=500")
    in21 = set()
    off = 0
    while True:
        st, r = req("GET", f"/contacts/lists/{ROA_LIST}/contacts?limit=500&offset={off}")
        cs = r.get("contacts", []) if st == 200 else []
        in21 |= {c["email"].lower() for c in cs if c.get("email")}
        if len(cs) < 500: break
        off += 500
    picked, off, total = [], 0, 0
    while True:
        st, r = req("GET", f"/contacts?limit=1000&offset={off}")
        if st != 200: raise SystemExit(f"contacts err {st} {r}")
        cs = r.get("contacts", [])
        total += len(cs)
        for c in cs:
            e = (c.get("email") or "").lower(); at = c.get("attributes") or {}
            if not e or c.get("emailBlacklisted") or e in in21: continue
            if str(at.get("STORE") or "").strip(): continue
            z = str(at.get(zipk) or "").strip() if zipk else ""
            city = str(at.get(cityk) or "").strip().lower() if cityk else ""
            if z[:3] in ("240", "241") or city in AREA_CITIES:
                picked.append(e)
        if len(cs) < 1000: break
        off += 1000
    print(f"scanned={total} already-in-21={len(in21)} picked(no STORE, Roanoke-area)={len(picked)}")
    if not picked: return
    if len(picked) > 3000: raise SystemExit("sanity stop: >3000 picked")
    st, r = req("GET", "/contacts/lists?limit=50")
    lid = next((l["id"] for l in r.get("lists", []) if l["name"] == AREA_LIST_NAME), None)
    if not lid:
        st, fl = req("GET", "/contacts/folders?limit=10")
        fid = (fl.get("folders") or [{}])[0].get("id", 1)
        st, r = req("POST", "/contacts/lists", {"name": AREA_LIST_NAME, "folderId": fid})
        lid = r.get("id"); print("created list", lid, st)
    for i in range(0, len(picked), 150):
        st, r = req("POST", f"/contacts/lists/{lid}/contacts/add", {"emails": picked[i:i+150]})
        if st >= 300: print("add err", st, str(r)[:200])
    time.sleep(5)
    st, li = req("GET", f"/contacts/lists/{lid}")
    print(f"list {lid} {li.get('name')!r} subs={li.get('totalSubscribers')}")
    save("area_list_id.txt", str(lid), overwrite=True)
    cid = int(open(os.path.join(BK, "announce_campaign_id.txt")).read().strip())
    st, c = req("GET", f"/emailCampaigns/{cid}?excludeHtmlContent=true")
    if c.get("status") != "queued": print("campaign not queued — not attaching:", c.get("status")); return
    st, r = req("PUT", f"/emailCampaigns/{cid}", {"recipients": {"listIds": [ROA_LIST, SEED_LIST, lid]}})
    print("attach PUT", st, str(r)[:200])
    st, c = req("GET", f"/emailCampaigns/{cid}?excludeHtmlContent=true")
    print(f"VERIFY C{cid}: status={c.get('status')} scheduledAt={c.get('scheduledAt')} lists={(c.get('recipients') or {}).get('lists')}")
    if c.get("status") != "queued" or not str(c.get("scheduledAt","")).startswith("2026-10-07T11:00"):
        st, r = req("PUT", f"/emailCampaigns/{cid}", {"scheduledAt": SCHEDULE_AT}); print("re-schedule", st)
        st, c = req("GET", f"/emailCampaigns/{cid}?excludeHtmlContent=true")
        print(f"RE-VERIFY C{cid}: status={c.get('status')} scheduledAt={c.get('scheduledAt')}")
    preflight(cid)


if __name__ == "__main__":
    a = sys.argv[1:]
    lists = [3, 10]
    if "--lists" in a:
        v = a[a.index("--lists") + 1]
        if v == "roanoke":
            lists = "roanoke"   # resolved inside do_build (after --roanoke-list has run)
        else:
            lists = [int(x) for x in v.split(",")]
    if "--patch-ids" in a:
        ONLY_IDS[:] = [int(x) for x in a[a.index("--patch-ids") + 1].split(",")]
    if "--inspect" in a: do_inspect()
    if "--patch" in a or "--patch-ids" in a: do_patch()
    if "--roanoke-list" in a: do_roanoke_list()
    if "--lists-info" in a:
        for lid in (3, 7, 10, 14, 15, 16, 17, 18, 19):
            st, li = req("GET", f"/contacts/lists/{lid}")
            print(f"  list {lid} '{li.get('name')}' subs={li.get('totalSubscribers')} uniq={li.get('uniqueSubscribers')} blacklisted={li.get('totalBlacklisted')}")
    if "--verify78" in a: camp_report(78)
    if "--go" in a: do_go()
    if "--area" in a: do_area()
    if "--sent" in a: camp_report(int(open(os.path.join(BK, "announce_campaign_id.txt")).read().strip()))
    if "--build" in a: do_build(lists)
    if "--schedule" in a: do_schedule()
    if not any(x in a for x in ("--inspect", "--patch", "--patch-ids", "--build", "--schedule", "--roanoke-list", "--lists-info", "--verify78", "--go", "--sent", "--area")):
        sys.exit(__doc__)
