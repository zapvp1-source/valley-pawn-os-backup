#!/usr/bin/env python3
"""
waysat5_brevo.py — Waynesboro is a 6-day store (Joshua 2026-10-14): Mon–Fri 10am–6pm, Sat 10am–5pm, closed Sun.
Brevo TEMPLATES lane only (never campaigns, never sends). Host only; stdlib. Pattern from bin/sat5_brevo.py (untouched).

New canonical footer: "Culpeper, Roanoke & Waynesboro: Mon–Fri 10am–6pm, Sat 10am–5pm. Harrisonburg & Lexington:
                       Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
Waynesboro store block: "Waynesboro · Mon–Fri 10am–6pm, Sat 10am–5pm".

  --inspect   read-only: every template, prints the hours contexts it WOULD change; saves nothing remote.
  --patch     backs up template HTML to brevo_backups_2026-10-14_waysat5/ first, then PUT + re-GET verify.
              Patches active templates and the masters 11/48 (read by pipelines even though flagged inactive).
"""
import functools, json, os, re, sys, time, urllib.error, urllib.request
print = functools.partial(print, flush=True)
HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents", "Claude", "Projects", "Valley Pawn OS")
BK = os.path.join(OS_DIR, "brevo_backups_2026-10-14_waysat5")
API = "https://api.brevo.com/v3"
KEY = open(os.path.join(HOME, ".config", "valley-pawn", "brevo_api_key")).read().strip()
MASTER_TEMPLATES = (11, 48)


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
                reset = e.headers.get("x-sib-ratelimit-reset") or e.headers.get("Retry-After") or ""
                try: wait = min(max(float(reset), 1.0) + 1, 600)
                except ValueError: wait = 5 * (2 ** min(a, 6))
                print(f"  429 on {method} {path[:60]} — waiting {wait:.0f}s"); time.sleep(wait); continue
            return e.code, e.read().decode(errors="replace")
        except Exception as e:
            last = str(e); time.sleep(3)
    return 599, last or "failed"


DASH = r"(–|&ndash;|&#8211;|-)"
AMP = r"(&amp;|&)"
RE_FOOT = re.compile(r"Culpeper\s*" + AMP + r"\s*Roanoke:\s*Mon" + DASH + r"Fri\s*10am" + DASH + r"6pm,\s*Sat\s*10am" + DASH
                     + r"5pm\.\s*Harrisonburg,\s*Waynesboro\s*" + AMP + r"\s*Lexington:")
RE_BLOCK = re.compile(r"(Waynesboro(?:,\s*VA\s*\d{5})?\s*(?:&middot;|·|&#183;)\s*)Mon,\s*Tue,\s*Thu,\s*Fri\s*" + AMP + r"\s*Sat\s*10am" + DASH + r"6pm")
RESIDUAL = [r"Harrisonburg,\s*Waynesboro", r"Waynesboro\s*(?:&middot;|·|&#183;)\s*Mon,\s*Tue", r"Culpeper\s*(?:&amp;|&)\s*Roanoke:"]


def patch_html(h):
    n = {}
    h, n["footer"] = RE_FOOT.subn(lambda m: f"Culpeper, Roanoke {m.group(1)} Waynesboro: Mon{m.group(2)}Fri 10am{m.group(2)}6pm, "
                                             f"Sat 10am{m.group(2)}5pm. Harrisonburg {m.group(1)} Lexington:", h)
    h, n["way_block"] = RE_BLOCK.subn(lambda m: f"{m.group(1)}Mon{m.group(3)}Fri 10am{m.group(3)}6pm, Sat 10am{m.group(3)}5pm", h)
    return h, {k: v for k, v in n.items() if v}


def residuals(h):
    no_c = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    return [re.sub(r"\s+", " ", no_c[max(0, m.start() - 60):m.end() + 60]) for p in RESIDUAL for m in re.finditer(p, no_c)]


def all_templates():
    out, off = [], 0
    while True:
        st, r = req("GET", f"/smtp/templates?limit=100&offset={off}")
        if st != 200: print("templates list error", st, str(r)[:200]); break
        ts = r.get("templates", []); out += ts
        if len(ts) < 100: break
        off += 100
    return out


def run(write):
    os.makedirs(BK, exist_ok=True)
    log = []
    for t in all_templates():
        tid = t["id"]
        st, full = req("GET", f"/smtp/templates/{tid}")
        if st != 200: print(f"T{tid} GET FAILED {st}"); continue
        h = full.get("htmlContent", "") or ""
        h2, n = patch_html(h)
        if not n:
            res = residuals(h)
            if res: print(f"T{tid} '{t.get('name')}' no pattern match but RESIDUAL {res[:2]}")
            continue
        active = t.get("isActive") or tid in MASTER_TEMPLATES
        print(f"T{tid} '{t.get('name')}' active={t.get('isActive')} would change {n}")
        if not write: continue
        if not active: print("   inactive non-master — NOT patched"); continue
        p = os.path.join(BK, f"template_{tid}.orig.html")
        if not os.path.exists(p): open(p, "w").write(h)
        pst, r = req("PUT", f"/smtp/templates/{tid}", {"htmlContent": h2})
        gst, chk = req("GET", f"/smtp/templates/{tid}")
        h3 = chk.get("htmlContent", "") if gst == 200 else ""
        res = residuals(h3)
        ok = pst in (200, 204) and h3 == h2 and not res
        open(os.path.join(BK, f"template_{tid}.new.html"), "w").write(h3)
        print(f"   PUT {pst} -> verify {'OK' if ok else 'FAIL ' + str(r)[:150]} residuals={res[:3]}")
        log.append({"id": tid, "name": t.get("name"), "put": pst, "changes": n, "verified": ok, "residuals": res})
    if write:
        json.dump(log, open(os.path.join(BK, "patch_log.json"), "w"), indent=1)
    print("DONE", "patch" if write else "inspect")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--inspect" in a: run(False)
    elif "--patch" in a: run(True)
    else: sys.exit(__doc__)
