#!/usr/bin/env python3
"""
sat5_brevo.py — Culpeper & Roanoke close 5:00 PM Saturdays (Joshua 2026-10-01, effective now). Brevo lane.
Host only; stdlib. Cloned from bin/roanoke_wed_brevo.py (same req()/429 handling).

Canonical:
  Culpeper & Roanoke: Mon–Fri 10am–6pm, Sat 10am–5pm, closed Sunday.
  Harrisonburg, Waynesboro, Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm, closed Wed & Sun (unchanged).
  Footer: "Culpeper & Roanoke: Mon–Fri 10am–6pm, Sat 10am–5pm. Harrisonburg, Waynesboro & Lexington:
           Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
  Store blocks: "Culpeper · Mon–Fri 10am–6pm, Sat 10am–5pm" (same for Roanoke).

  --patch      Phase 1: GET templates 11/48 (+ any template with Culpeper/Roanoke hours) and EVERY not-sent
               campaign (draft/queued/suspended); save current HTML to brevo_backups_2026-10-01_sat5/ BEFORE
               any write. Phase 2: patch + PUT + re-GET verify. Never touches sent / in_process / #52 /
               names starting "CANCELLED". Queued campaigns are re-scheduled to their original time if an edit
               changes status. #78 also gets its previewText corrected.
  --finalize   Waits for the rate-limit window, runs Email Refinement/brevo_preflight.py on 78 and 76,
               verifies #78 has zero old-hours strings, sends #78 TEST to jdavis@fcfpawn.com, verifies
               #78 scheduledAt 2026-10-02T10:00-04:00 and #76 its original time (queued).
               SAFETY: if #78 fails any of these, #78 is SUSPENDED (never allowed to send wrong hours).
  --verify     read-only: status/scheduledAt/residuals for 78 and 76.
"""
import functools, json, os, re, subprocess, sys, time, urllib.error, urllib.request
print = functools.partial(print, flush=True)

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents", "Claude", "Projects")
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
BK = os.path.join(OS_DIR, "brevo_backups_2026-10-01_sat5")
PREFLIGHT = os.path.join(PROJ, "Email Refinement", "brevo_preflight.py")
API = "https://api.brevo.com/v3"
KEY = open(os.path.join(HOME, ".config", "valley-pawn", "brevo_api_key")).read().strip()

ANNOUNCE_ID = 78
ANNOUNCE_SCHED = "2026-10-02T10:00:00-04:00"
ANNOUNCE_PREVIEW = "Our Roanoke store is now open Wednesdays: Monday–Friday 10am–6pm, Saturday 10am–5pm."
SHOP_ID = 76
NEVER_TOUCH = {52}
MASTER_TEMPLATES = (11, 48)
TEST_TO = ["jdavis@fcfpawn.com"]

os.makedirs(BK, exist_ok=True)
RL = {"remaining": None, "reset": None}


def req(method, path, body=None, tries=12):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for a in range(tries):
        r = urllib.request.Request(API + path, data=data, method=method,
                                   headers={"api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                RL["remaining"] = resp.headers.get("x-sib-ratelimit-remaining")
                RL["reset"] = resp.headers.get("x-sib-ratelimit-reset")
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw.strip() else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                reset = e.headers.get("x-sib-ratelimit-reset") or e.headers.get("Retry-After") or ""
                try: wait = min(max(float(reset), 1.0) + 1, 600)
                except ValueError: wait = 5 * (2 ** min(a, 6))
                print(f"  429 on {method} {path[:60]} — waiting {wait:.0f}s (try {a+1})")
                time.sleep(wait); continue
            return e.code, e.read().decode(errors="replace")
        except Exception as e:
            last = str(e); time.sleep(3)
    return 599, last or "rate-limited"


def wait_for_window(need=25):
    """Before handing off to preflight (which has its own short 429 backoff), make sure the
    /emailCampaigns window has room."""
    st, _ = req("GET", "/emailCampaigns?limit=1&excludeHtmlContent=true")
    try:
        rem = int(RL["remaining"]) if RL["remaining"] is not None else None
        rst = float(RL["reset"]) if RL["reset"] is not None else 0
    except ValueError:
        rem, rst = None, 0
    print(f"  rate window: remaining={rem} reset={rst}s")
    if rem is not None and rem < need:
        print(f"  waiting {rst + 2:.0f}s for the campaign rate window to reset")
        time.sleep(min(rst + 2, 600))


# ---------------------------------------------------------------- patterns
DASH = r"(–|&ndash;|&#8211;|–|-)"
AMP = r"(&amp;|&)"
NEW_FOOTER = ("Culpeper {a} Roanoke: Mon{d}Fri 10am{d}6pm, Sat 10am{d}5pm. Harrisonburg, Waynesboro {a} Lexington: "
              "Mon, Tue, Thu, Fri {a} Sat 10am{d}6pm (closed Wed {a} Sun).")
# pre-10/1 footer (Culpeper-only) — whole line
RE_FOOT_OLD = re.compile(r"Culpeper:\s*Mon" + DASH + r"Sat\s*10am" + DASH + r"6pm\.\s*All other stores:\s*Mon,\s*Tue,\s*Thu,\s*Fri\s*"
                         + AMP + r"\s*Sat\s*10am" + DASH + r"6pm\s*\(closed Wed\s*" + AMP + r"\s*Sun\)\.?")
# 10/1 footer head "Culpeper & Roanoke: Mon–Sat 10am–6pm."
RE_FOOT = re.compile(r"Culpeper\s*" + AMP + r"\s*Roanoke:\s*Mon" + DASH + r"Sat\s*10am" + DASH + r"6pm\.")
# store blocks: "Culpeper · Mon–Sat 10am–6pm", "Roanoke, VA 24017 &middot; Mon&ndash;Sat 10am&ndash;6pm"
RE_BLOCK = re.compile(r"((?:Culpeper|Roanoke)(?:,\s*VA\s*\d{5})?\s*(?:&middot;|·|&#183;)\s*)Mon" + DASH + r"Sat\s*10am" + DASH + r"6pm")
# pre-10/1 Roanoke block "Roanoke · Mon, Tue, Thu, Fri & Sat 10am–6pm"
RE_BLOCK_ROA_OLD = re.compile(r"(Roanoke(?:,\s*VA\s*\d{5})?\s*(?:&middot;|·|&#183;)\s*)Mon,\s*Tue,\s*Thu,\s*Fri\s*" + AMP + r"\s*Sat\s*10am" + DASH + r"6pm")
RE_PROSE_TO = re.compile(r"Monday through Saturday, 10am to 6pm")
RE_PROSE_DASH = re.compile(r"Monday through Saturday, 10am" + DASH + r"6pm")

# residual detectors (comment-stripped)
RESIDUAL = [r"Mon(?:–|&ndash;|&#8211;|-)Sat\b", r"Monday through Saturday", r"Monday(?:–|&ndash;|-)Saturday",
            r"All other stores", r"Culpeper:\s*Mon", r"Culpeper also open", r"[Nn]o store closes",
            r"[Cc]los(?:e|es|ing) at 5", r"Roanoke\s*(?:&middot;|·)\s*Mon,\s*Tue"]


def patch_html(h):
    n = {}
    h, n["foot_old"] = RE_FOOT_OLD.subn(lambda m: NEW_FOOTER.format(a=m.group(2), d=m.group(1)), h)
    h, n["footer"] = RE_FOOT.subn(lambda m: f"Culpeper {m.group(1)} Roanoke: Mon{m.group(2)}Fri 10am{m.group(2)}6pm, Sat 10am{m.group(2)}5pm.", h)
    h, n["block"] = RE_BLOCK.subn(lambda m: f"{m.group(1)}Mon{m.group(2)}Fri 10am{m.group(2)}6pm, Sat 10am{m.group(2)}5pm", h)
    h, n["block_roa_old"] = RE_BLOCK_ROA_OLD.subn(lambda m: f"{m.group(1)}Mon{m.group(3)}Fri 10am{m.group(3)}6pm, Sat 10am{m.group(3)}5pm", h)
    h, n["prose_to"] = RE_PROSE_TO.subn("Monday through Friday, 10am to 6pm, and Saturday, 10am to 5pm", h)
    h, n["prose_dash"] = RE_PROSE_DASH.subn(lambda m: f"Monday{m.group(1)}Friday 10am{m.group(1)}6pm, Saturday 10am{m.group(1)}5pm", h)
    return h, {k: v for k, v in n.items() if v}


def strip_comments(h):
    return re.sub(r"<!--.*?-->", "", h, flags=re.S)


def residuals(h):
    no_c = strip_comments(h)
    out = []
    for p in RESIDUAL:
        for m in re.finditer(p, no_c):
            s = max(0, m.start() - 80)
            out.append(re.sub(r"\s+", " ", no_c[s:m.end() + 60]))
    # any 5pm that is not the Culpeper/Roanoke Saturday close
    for m in re.finditer(r"\b5\s?(?:pm|PM)\b|\b5:00\s?(?:pm|PM)\b", no_c):
        pre = no_c[max(0, m.start() - 30):m.start()]
        if not re.search(r"Sat(?:urday)?,?\s*10am(?:\s*to\s*|–|&ndash;|&#8211;|-)$", pre):
            out.append("UNEXPECTED 5pm: " + re.sub(r"\s+", " ", no_c[max(0, m.start() - 140):m.end()]))
    return out


def contexts(h):
    no_c = strip_comments(h)
    return [re.sub(r"\s+", " ", no_c[max(0, m.start() - 70):m.end() + 10])
            for m in re.finditer(r"10am(?:–|&ndash;|-)5pm|10am to 5pm", no_c)]


def save(name, text, overwrite=False):
    p = os.path.join(BK, name)
    if overwrite or not os.path.exists(p):
        open(p, "w").write(text if isinstance(text, str) else json.dumps(text, indent=1))
    return p


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
    out, seen = [], set()
    for status in ("draft", "queued", "suspended"):
        off = 0
        while True:
            st, r = req("GET", f"/emailCampaigns?status={status}&limit=100&offset={off}&excludeHtmlContent=true")
            if st != 200:
                print("campaign list error", status, st, str(r)[:200]); break
            cs = r.get("campaigns", []) or []
            out += [c for c in cs if c["id"] not in seen]; seen |= {c["id"] for c in cs}
            if len(cs) < 100: break
            off += 100
    return out


# ---------------------------------------------------------------- patch
def do_patch():
    log = {"templates": [], "campaigns": [], "skipped": [], "untouched_no_hours": []}
    # ---- phase 1: read + back up everything first
    tmpl = {}
    for t in all_templates():
        st, full = req("GET", f"/smtp/templates/{t['id']}")
        if st != 200:
            print(f"T{t['id']} GET FAILED {st}"); continue
        h = full.get("htmlContent", "") or ""
        h2, n = patch_html(h)
        if t["id"] in MASTER_TEMPLATES or n:
            save(f"template_{t['id']}.orig.html", h)
            tmpl[t["id"]] = (t, h, h2, n)
    camps = {}
    for c in unsent_campaigns():
        cid = c["id"]
        st, full = req("GET", f"/emailCampaigns/{cid}")
        if st != 200:
            print(f"C{cid}: GET FAILED {st} {str(full)[:150]} — NOT patched"); log["skipped"].append({"id": cid, "why": f"GET {st}"}); continue
        h = full.get("htmlContent", "") or ""
        save(f"campaign_{cid}.orig.html", h)
        save(f"campaign_{cid}.meta.json", {k: full.get(k) for k in ("id", "name", "status", "scheduledAt", "subject", "previewText", "recipients")})
        camps[cid] = (full, h)
    print(f"BACKUP DONE: {len(tmpl)} templates, {len(camps)} not-sent campaigns saved to {BK}")

    # ---- phase 2: templates
    print("\n===== TEMPLATES =====")
    for tid, (t, h, h2, n) in sorted(tmpl.items()):
        if h2 == h:
            print(f"T{tid} '{t.get('name')}' no hours strings to change; residuals={residuals(h)[:3]}"); continue
        if not t.get("isActive") and tid not in MASTER_TEMPLATES:
            print(f"T{tid} '{t.get('name')}' INACTIVE non-master — has hours {n} — NOT patched"); continue
        st, r = req("PUT", f"/smtp/templates/{tid}", {"htmlContent": h2})
        st2, chk = req("GET", f"/smtp/templates/{tid}")
        h3 = chk.get("htmlContent", "") if st2 == 200 else ""
        res = residuals(h3)
        ok = st in (200, 204) and h3 == h2 and not res
        save(f"template_{tid}.new.html", h3, overwrite=True)
        print(f"T{tid} '{t.get('name')}' PUT {st} {n} -> verify {'OK' if ok else 'FAIL ' + str(r)[:150]} residuals={res[:4]}")
        for x in contexts(h3): print("    ", x[:200])
        log["templates"].append({"id": tid, "put": st, "changes": n, "verified": ok, "residuals": res})

    # ---- phase 2: campaigns
    print("\n===== NOT-SENT CAMPAIGNS =====")
    for cid, (full, h) in sorted(camps.items()):
        status, name = full.get("status"), full.get("name") or ""
        if cid in NEVER_TOUCH or status in ("sent", "in_process", "archive") or name.upper().startswith("CANCELLED"):
            print(f"C{cid} [{status}] '{name}' skipped by rule"); log["skipped"].append({"id": cid, "why": "rule"}); continue
        h2, n = patch_html(h)
        body = {}
        if h2 != h: body["htmlContent"] = h2
        pv = full.get("previewText") or ""
        if cid == ANNOUNCE_ID and pv != ANNOUNCE_PREVIEW:
            body["previewText"] = ANNOUNCE_PREVIEW
        elif pv:
            pv2, pn = patch_html(pv)
            if pn: body["previewText"] = pv2
        if not body:
            res = residuals(h)
            print(f"C{cid} [{status}] '{name}' no change" + (f" — RESIDUALS {res[:3]}" if res else ""))
            log["untouched_no_hours"].append({"id": cid, "name": name, "residuals": res}); continue
        save(f"campaign_{cid}.prepatch.html", h, overwrite=True)
        st, r = req("PUT", f"/emailCampaigns/{cid}", body)
        st2, chk = req("GET", f"/emailCampaigns/{cid}")
        if status == "queued" and chk.get("status") != "queued" and full.get("scheduledAt"):
            rs, rr = req("PUT", f"/emailCampaigns/{cid}", {"scheduledAt": full["scheduledAt"]})
            print(f"  C{cid} status changed to {chk.get('status')} by the edit — re-scheduled to {full['scheduledAt']}: HTTP {rs} {str(rr)[:150]}")
            st2, chk = req("GET", f"/emailCampaigns/{cid}")
        h3 = chk.get("htmlContent", "") or ""
        res = residuals(h3)
        sched_ok = (status != "queued") or (chk.get("status") == "queued" and chk.get("scheduledAt") == full.get("scheduledAt"))
        ok = st in (200, 204) and not res and sched_ok and ("htmlContent" not in body or h3 == h2)
        save(f"campaign_{cid}.new.html", h3, overwrite=True)
        print(f"C{cid} [{status}->{chk.get('status')}] '{name}' sched={chk.get('scheduledAt')} PUT {st} {n}"
              f"{' +previewText' if 'previewText' in body else ''} -> verify {'OK' if ok else 'FAIL ' + str(r)[:200]} residuals={res[:4]}")
        for x in contexts(h3): print("    ", x[:200])
        log["campaigns"].append({"id": cid, "name": name, "status_before": status, "status_after": chk.get("status"),
                                 "sched_before": full.get("scheduledAt"), "sched_after": chk.get("scheduledAt"), "put": st,
                                 "changes": n, "preview": body.get("previewText"), "verified": ok, "residuals": res})
        if cid == ANNOUNCE_ID and not ok:
            suspend_announce(f"patch verify failed (PUT {st}, residuals {res[:3]})")
    save("patch_log.json", log, overwrite=True)
    print("PATCH DONE")


def suspend_announce(why):
    print(f"!!! SAFETY: suspending #{ANNOUNCE_ID} — {why}")
    st, r = req("PUT", f"/emailCampaigns/{ANNOUNCE_ID}/status", {"status": "suspended"})
    st2, c = req("GET", f"/emailCampaigns/{ANNOUNCE_ID}?excludeHtmlContent=true")
    print(f"    suspend PUT {st} {str(r)[:150]} -> status now {c.get('status') if isinstance(c, dict) else c}")


def preflight(cid):
    pf = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(cid)], capture_output=True, text=True)
    print(f"preflight C{cid}: rc={pf.returncode}\n{pf.stdout}{pf.stderr[-800:]}")
    return pf.returncode


def do_finalize():
    wait_for_window()
    fails = []
    # #78
    st, c = req("GET", f"/emailCampaigns/{ANNOUNCE_ID}")
    h = c.get("htmlContent", "") if st == 200 else ""
    res = residuals(h)
    print(f"C{ANNOUNCE_ID} status={c.get('status')} sched={c.get('scheduledAt')} preview={c.get('previewText')!r}")
    print(f"  residual old-hours strings: {res if res else 'NONE'}")
    for x in contexts(h): print("    new:", x[:200])
    if st != 200 or res: fails.append("residuals")
    if "Sat 10am" not in h and "Saturday, 10am to 5pm" not in h: fails.append("new hours missing")
    if re.search(r"\b(firearms?|guns?|pistols?|rifles?|ammo)\b", strip_comments(h), re.I): fails.append("firearms")
    if "Dixie" in h: fails.append("Dixie Pawn")
    rc = preflight(ANNOUNCE_ID)
    if rc != 0: fails.append("preflight")
    st, c = req("GET", f"/emailCampaigns/{ANNOUNCE_ID}?excludeHtmlContent=true")
    if not str(c.get("scheduledAt", "")).startswith("2026-10-02T10:00:00") or c.get("status") != "queued":
        print(f"  #78 not queued at 10/2 10:00 (status={c.get('status')} sched={c.get('scheduledAt')}) — re-scheduling")
        if not fails:
            rs, rr = req("PUT", f"/emailCampaigns/{ANNOUNCE_ID}", {"scheduledAt": ANNOUNCE_SCHED})
            print(f"  schedule PUT {rs} {str(rr)[:150]}")
    if fails:
        suspend_announce("finalize checks failed: " + ", ".join(fails))
    else:
        st, r = req("POST", f"/emailCampaigns/{ANNOUNCE_ID}/sendTest", {"emailTo": TEST_TO})
        print(f"TEST SEND #{ANNOUNCE_ID} to {TEST_TO}: HTTP {st} {str(r)[:300]}")
    # #76
    rc76 = preflight(SHOP_ID)
    st, c76 = req("GET", f"/emailCampaigns/{SHOP_ID}")
    print(f"C{SHOP_ID} status={c76.get('status')} sched={c76.get('scheduledAt')} residuals={residuals(c76.get('htmlContent', '')) or 'NONE'} preflight_rc={rc76}")
    do_verify()


def do_verify():
    for cid in (ANNOUNCE_ID, SHOP_ID):
        st, c = req("GET", f"/emailCampaigns/{cid}")
        print(f"VERIFY C{cid}: '{c.get('name')}' status={c.get('status')} scheduledAt={c.get('scheduledAt')} "
              f"lists={(c.get('recipients') or {}).get('lists')} residuals={residuals(c.get('htmlContent', '')) or 'NONE'}")
        save(f"campaign_{cid}.final.html", c.get("htmlContent", ""), overwrite=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--patch" in a: do_patch()
    if "--finalize" in a: do_finalize()
    if "--verify" in a: do_verify()
    if not any(x in a for x in ("--patch", "--finalize", "--verify")):
        sys.exit(__doc__)
