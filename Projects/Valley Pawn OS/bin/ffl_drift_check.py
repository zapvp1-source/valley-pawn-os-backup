#!/usr/bin/env python3
"""ffl_drift_check.py — weekly READ-ONLY check of Valley Pawn's public FFL listings vs ffl_vendors.json.
Added 2026-10-21 (FFL audit, panel decision D2). Additive: reads public pages only, never logs in,
never submits anything, never posts to Slack. Writes:
  Compliance/state/ffl_drift_latest.json   (machine)
  Compliance/FFL_DRIFT.md                  (human; newest run on top, keeps last 12 runs)
Uses vp_browser (headed off-screen real Chrome) because MasterFFL sits behind Cloudflare.
Usage: ffl_drift_check.py [--dry]   (--dry = fetch + print, write nothing)
Expected values come from ffl_vendors.json, so a roster change (hours/phone) changes the expectation.
"""
import json, os, re, sys, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.expanduser("~/Documents/Claude/Projects")
ROSTER = os.path.join(ROOT, "Compliance", "ffl_vendors.json")
OUT_JSON = os.path.join(ROOT, "Compliance", "state", "ffl_drift_latest.json")
OUT_MD = os.path.join(ROOT, "Compliance", "FFL_DRIFT.md")
DRY = "--dry" in sys.argv

MASTERFFL = {"CUL": "valley-pawn-culpeper-va-356750685", "WAY": "valley-pawn-waynesboro-va-448919954",
             "HAR": "valley-pawn-harrisonburg-va-381954686", "LEX": "valley-pawn-lexington-va-647665659",
             "ROA": "valley-pawn-roanoke-va-163767505"}
GUNNOOK = {"WAY": "valley-pawn-waynesboro-va", "HAR": "valley-pawn-harrisonburg-va", "LEX": "valley-pawn-lexington-va"}
GUNMADE = {"CUL": "culpeper/valley-pawn-10065", "WAY": "waynesboro/valley-pawn-10211", "HAR": "harrisonburg/valley-pawn-10100",
           "LEX": "lexington/valley-pawn-11181", "ROA": "roanoke/valley-pawn-10832", "SAL": "salem/valley-pawn-10967"}
# roster hours string -> the exact "Hours:" sentence we publish in MasterFFL About text
MASTERFFL_HOURS = {
    "Mon-Fri 10-6, Sat 10-5": "Hours: Monday through Friday 10am-6pm, Saturday 10am-5pm. Closed Sunday.",
    "Mon Tue Thu Fri Sat 10-6": "Hours: Monday, Tuesday, Thursday, Friday and Saturday 10am-6pm. Closed Wednesday and Sunday.",
}
FEE = "$25"


def digits(s):
    return re.sub(r"\D", "", s or "")


def fetch_all(urls):
    from playwright.sync_api import sync_playwright
    import vp_browser
    texts = {}
    with sync_playwright() as p:
        ctx = None
        for attempt in range(3):
            try:
                ctx = vp_browser.launch(p)
                break
            except RuntimeError as e:
                print("launch busy:", e); time.sleep(300)
        if ctx is None:
            raise SystemExit("automation Chrome busy 15 min; giving up this run")
        try:
            page = vp_browser.first_page(ctx)
            for key, url in urls.items():
                txt = ""
                for _ in range(2):
                    try:
                        page.goto(url + ("&" if "?" in url else "?") + "v=%d" % time.time(), timeout=45000)
                        for _w in range(12):
                            txt = page.inner_text("body")
                            if "security verification" not in txt.lower() and "just a moment" not in txt.lower():
                                break
                            page.wait_for_timeout(2500)
                        page.wait_for_timeout(3000)
                        html = page.content()
                        try:  # server HTML incl. embedded JSON (MasterFFL keeps the full About text there)
                            html += page.evaluate("fetch(location.href,{cache:'no-store'}).then(r=>r.text())")
                        except Exception:
                            pass
                        html = html.replace("\\u0026", "&").replace("\\n", " ")
                        html = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", html)
                        txt = page.title() + "\n" + txt + "\n" + re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
                        break
                    except Exception as e:
                        txt = "FETCH-ERROR %s" % e
                texts[key] = txt
        finally:
            vp_browser.close(ctx)
    return texts


def main():
    roster = json.load(open(ROSTER))
    st = roster["stores"]
    urls = {}
    for s, slug in MASTERFFL.items():
        urls["masterffl:" + s] = "https://masterffl.com/ffl-dealers/%s/" % slug
    for s, slug in GUNNOOK.items():
        urls["gunnook:" + s] = "https://gunnook.com/ffl/dealer/%s" % slug
    for s, slug in GUNMADE.items():
        urls["gunmade:" + s] = "https://www.gunmade.com/stores/virginia/%s/" % slug
    urls["ffleasy:HAR"] = "https://www.ffleasy.com/virginia/harrisonburg/9854"
    texts = fetch_all(urls)
    drift, ok, unverified = [], [], []

    def flag(k, msg):
        drift.append({"listing": k, "issue": msg, "url": urls[k]})

    for k, t in texts.items():
        site, s = k.split(":")
        if t.startswith("FETCH-ERROR") or "security verification" in t.lower() or len(t) < 300:
            unverified.append({"listing": k, "why": t[:120]}); continue
        low = t.lower()
        if "dixie" in low:
            flag(k, "legacy name 'Dixie' on page")
        if s == "SAL":
            if "active ffl" in low or "verified" in low and "closed" not in low:
                flag(k, "closed Salem store shown as active")
            continue
        r = st[s]
        if site == "masterffl":
            want = MASTERFFL_HOURS.get(r["hours"])
            if not want:
                flag(k, "roster hours '%s' not mapped in ffl_drift_check.MASTERFFL_HOURS" % r["hours"])
            elif want not in t:
                m = re.search(r"Hours:[^\n]{0,100}", t)
                flag(k, "hours: page '%s' vs roster '%s'" % (m.group(0) if m else "none", want))
            if digits(r["phone"])[-10:] not in digits(t):
                flag(k, "roster phone %s not on page" % r["phone"])
            if r["ffl"].split("-")[-1] not in t:
                flag(k, "license %s not on page" % r["ffl"])
            if FEE not in t:
                flag(k, "transfer fee $25 not shown")
        elif site == "gunnook":
            fees = set(re.findall(r"\$\d+", t))
            if fees and FEE not in fees:
                flag(k, "fee shown %s (should be $25)" % ",".join(sorted(fees)))
            if re.search(r"9:00\s*AM", t, re.I):
                flag(k, "hours show 9:00 AM opening (real opening 10 AM)")
        elif site == "gunmade":
            if digits(r["phone"])[-10:] not in digits(t):
                flag(k, "roster phone %s not on page" % r["phone"])
        elif site == "ffleasy":
            pass  # dixie check above is the point
        if not any(d["listing"] == k for d in drift):
            ok.append(k)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    res = {"run": now, "drift": drift, "ok": ok, "unverified": unverified,
           "roster_updated": roster.get("_updated")}
    print(json.dumps(res, indent=1))
    if DRY:
        return
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(res, open(OUT_JSON, "w"), indent=1)
    block = ["## %s — %d drift, %d ok, %d unverified" % (now, len(drift), len(ok), len(unverified))]
    block += ["- **%s**: %s (%s)" % (d["listing"], d["issue"], d["url"]) for d in drift]
    if unverified:
        block.append("- unverified: " + ", ".join(u["listing"] for u in unverified))
    prev = open(OUT_MD).read() if os.path.exists(OUT_MD) else ""
    runs = re.split(r"(?m)^(?=## \d{4}-)", prev.split("\n", 3)[-1]) if prev else []
    runs = [x for x in runs if x.startswith("## ")][:11]
    hdr = ("# FFL listing drift — weekly read-only check (bin/ffl_drift_check.py)\n\n"
           "Compares public FFL listings to `ffl_vendors.json`. Fix drift through the owning site "
           "(see FFL_DEPT_OS.md); most need a store sign-in.\n")
    open(OUT_MD, "w").write(hdr + "\n" + "\n".join(block) + "\n\n" + "".join(runs))


if __name__ == "__main__":
    main()
