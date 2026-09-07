#!/usr/bin/env python3
"""stage_quarter.py — build one quarter of Valley Pawn weekly Brevo drafts from a calendar JSON.

Owned by the `brevo-stage-next-quarter` scheduled task (Email Dept plan 2026-09-05, file 19, Phase 1).
Generalizes _audit/build_calendar.py (the one-off that staged Sep 10 – Dec 31 2026) so the
weekly calendar can never run out again.

    python3 stage_quarter.py --calendar quarter_2027Q1.json            # dry run (default)
    python3 stage_quarter.py --calendar quarter_2027Q1.json --apply    # create the drafts
    python3 stage_quarter.py --thursdays 2027Q1                        # just list the Thursdays

CALENDAR JSON — a list of objects, one per Thursday, keys:
    date        "January 7, 2027"            (Month D, YYYY — the picker matches this literal string)
    theme       "Culpeper Spotlight"         (campaign name = "<theme> — <date>")
    subject     "..."                        (follow SUBJECT_LINE_EXPERIMENT.md rules)
    slug        "weekly_culpeper_2027-01-07" (utm_campaign)
    eyebrow     "STORE SPOTLIGHT — CULPEPER"
    headline    "..."
    subline     "..."                        (also becomes the hidden preheader)
    body        ["para 1", "para 2"]         (keep under ~120 words total)
    notpawn     "optional local-flavor line or empty string"
    cta         "Get directions" | "Start a layaway" | "Get a free appraisal" | ...
    waves       [17, 18]                     (optional; if absent the script continues the rotation)

MECHANICS
 - Base HTML = newest DRAFT campaign whose body still carries the dashed
   `DEAL OF THE WEEK — POPULATED MONDAY` placeholder (or --base <id>). Only the comment-delimited
   variable regions are touched: HERO BAND, BODY CONTENT SLOT prose (placeholder kept), PRIMARY CTA
   label, preheader, <title>, utm_campaign. Every LOCKED region is untouched.
 - Recipients = [7 engaged, 10 seeds] + two wave lists (14–18), rotating on from the last staged draft.
 - Collision-safe: a Thursday whose date string already appears in a draft name is skipped.
 - Every created draft is GET-verified: name, lists, placeholder present, zero [[MARKER]], /c/ + /t/
   links present, primary_cta present. Failures are printed as FAIL and counted in the exit code.
 - Run brevo_preflight.py <id> on each created id afterwards (the task does this).
"""
import argparse, datetime as dt, json, os, re, sys, time, urllib.request, urllib.error

BASE = "https://api.brevo.com/v3"
KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
ENGAGED, SEEDS = 7, 10
WAVES = [14, 15, 16, 17, 18]
PLACEHOLDER = "DEAL OF THE WEEK — POPULATED MONDAY"
CITIES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]


def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                   headers={"api-key": KEY, "Content-Type": "application/json",
                                            "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + 4 * a)
                continue
            return e.code, e.read().decode()
    return 429, "rate limited"


def thursdays(quarter):
    y, q = int(quarter[:4]), int(quarter[-1])
    start = dt.date(y, 3 * (q - 1) + 1, 1)
    end = (dt.date(y + 1, 1, 1) if q == 4 else dt.date(y, 3 * q + 1, 1)) - dt.timedelta(days=1)
    d = start + dt.timedelta(days=(3 - start.weekday()) % 7)  # Thursday = 3
    out = []
    while d <= end:
        out.append(d)
        d += dt.timedelta(days=7)
    return out


def fmt(d):  # "January 7, 2027" — no zero padding (matches picker + existing names)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def para(t):
    return ('<p style="margin:0 0 14px 0; font-size:16px; line-height:1.6; color:#1a1a1a;">'
            + t + "</p>")


def region(h, start_marker, end_marker):
    s = h.find(start_marker)
    e = h.find(end_marker, s + 1)
    if s < 0 or e < 0:
        raise SystemExit(f"template region not found: {start_marker!r} .. {end_marker!r}")
    return s, e


def build(base, it):
    h = base
    # utm_campaign
    slugs = set(re.findall(r"utm_campaign=([^&\"']+)", h))
    for s in slugs:
        h = h.replace(f"utm_campaign={s}", f"utm_campaign={it['slug']}")
    # HERO BAND: first <p> = eyebrow, <h1> = headline, next <p> = subline
    s, e = region(h, "HERO BAND (variable copy", "YOUR STORE — PERSONALIZED HEADER")
    hero = h[s:e]
    hero = re.sub(r"(<p[^>]*>)(.*?)(</p>)", lambda m: m.group(1) + it["eyebrow"] + m.group(3), hero, count=1, flags=re.S)
    hero = re.sub(r"(<h1[^>]*>)(.*?)(</h1>)", lambda m: m.group(1) + it["headline"] + m.group(3), hero, count=1, flags=re.S)
    # second <p> (after h1)
    h1_end = hero.find("</h1>")
    tail = re.sub(r"(<p[^>]*>)(.*?)(</p>)", lambda m: m.group(1) + it["subline"] + m.group(3), hero[h1_end:], count=1, flags=re.S)
    hero = hero[:h1_end] + tail
    h = h[:s] + hero + h[e:]
    # PREHEADER hidden div
    s, e = region(h, "Preheader (hidden", "<table")
    pre = re.sub(r"(<div[^>]*>)(.*?)(</div>)", lambda m: m.group(1) + it["subline"] + m.group(3), h[s:e], count=1, flags=re.S)
    h = h[:s] + pre + h[e:]
    # TITLE
    h = re.sub(r"<title>.*?</title>", "<title>" + it["subject"].replace("&", "&amp;") + "</title>", h, count=1, flags=re.S)
    # BODY CONTENT SLOT — keep placeholder div, swap prose
    s, e = region(h, "BODY CONTENT SLOT", "<!-- ============ LOCKED: TRUST STRIP")
    body = h[s:e]
    if PLACEHOLDER not in body:
        raise SystemExit("base template lost the DEAL placeholder — refusing to build")
    ph_end = body.find("</div>", body.find(PLACEHOLDER)) + len("</div>")
    new_body = body[:ph_end] + "\n" + "\n".join(para(b) for b in it["body"])
    if it.get("notpawn"):
        new_body += ('\n<p style="margin:18px 0 0 0;font-size:13px;line-height:1.6;color:#8a6a3a;">'
                     "<strong>NOTPAWN</strong> &middot; " + it["notpawn"] + "</p>")
    new_body += "\n          </td>\n        </tr>\n\n        "
    h = h[:s] + new_body + h[e:]
    # PRIMARY CTA label
    s, e = region(h, "PRIMARY CTA (variable", "LOCKED: SECTION DIVIDER")
    cta = h[s:e]
    label = it["cta"]
    def relabel(m):
        city = next((c for c in CITIES if c in m.group(0)), "")
        txt = f"{label} to {city} &rarr;" if (label == "Get directions" and city) else f"{label} &rarr;"
        return m.group(1) + txt + m.group(3)
    cta = re.sub(r"(letter-spacing:0\.2px;\">)(.*?)(</a>)", relabel, cta, flags=re.S)
    h = h[:s] + cta + h[e:]
    return h


def checks(h):
    errs = []
    if PLACEHOLDER not in h: errs.append("placeholder missing")
    left = re.findall(r"\[\[[A-Z_]+\]\]", h)
    if left: errs.append(f"unfilled markers {sorted(set(left))}")
    if h.count("thevalleypawn.com/c/") < 5 or h.count("thevalleypawn.com/t/") < 5: errs.append("call/text links < 5")
    if "utm_content=primary_cta" not in h: errs.append("primary_cta utm missing")
    if "Full Circle" in h: errs.append("legal name leak")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calendar")
    ap.add_argument("--thursdays", help="e.g. 2027Q1 — print the Thursdays and exit")
    ap.add_argument("--base", type=int)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    if a.thursdays:
        for d in thursdays(a.thursdays): print(fmt(d))
        return 0
    if not a.calendar:
        ap.error("--calendar required")
    cal = json.load(open(a.calendar))

    st, drafts = req("GET", "/emailCampaigns?status=draft&limit=100")
    assert st == 200, (st, drafts)
    drafts = drafts.get("campaigns", [])
    names = {c["name"] for c in drafts}

    # base template
    base_id = a.base
    if not base_id:
        cands = [c for c in drafts if PLACEHOLDER in json.dumps(c.get("htmlContent", "")) or True]
        # list endpoint omits htmlContent; probe newest-first
        for c in sorted(drafts, key=lambda c: c["id"], reverse=True):
            if "[PARKED" in c["name"]: continue
            st, full = req("GET", f"/emailCampaigns/{c['id']}")
            if st == 200 and PLACEHOLDER in full.get("htmlContent", ""):
                base_id, base_html = c["id"], full["htmlContent"]; break
        else:
            raise SystemExit("no draft with the DEAL placeholder found — pass --base")
    else:
        st, full = req("GET", f"/emailCampaigns/{base_id}"); assert st == 200, (st, full)
        base_html = full["htmlContent"]
    print(f"base template: campaign {base_id}")

    # wave rotation: continue from the newest draft's pair
    last_waves = []
    for c in sorted(drafts, key=lambda c: c["id"], reverse=True):
        w = [l for l in (c.get("recipients", {}).get("lists") or []) if l in WAVES]
        if w: last_waves = w; break
    idx = (WAVES.index(last_waves[-1]) + 1) % 5 if last_waves else 0

    created, skipped, fails = [], [], 0
    for it in cal:
        name = f"{it['theme']} — {it['date']}"
        if any(it["date"] in n for n in names):
            skipped.append(name); continue
        waves = it.get("waves") or [WAVES[idx % 5], WAVES[(idx + 1) % 5]]
        idx += 2
        html = build(base_html, it)
        errs = checks(html)
        if errs:
            print("FAIL build", name, errs); fails += 1; continue
        payload = {"name": name, "subject": it["subject"], "previewText": it["subline"],
                   "sender": SENDER, "replyTo": REPLY_TO, "htmlContent": html,
                   "recipients": {"listIds": [ENGAGED, SEEDS] + waves},
                   "inlineImageActivation": False, "mirrorActive": True}
        if not a.apply:
            created.append(f"[dry] {name} | {it['subject']} | lists {payload['recipients']['listIds']}"); continue
        st, res = req("POST", "/emailCampaigns", payload)
        if st >= 300:
            print("FAIL create", name, st, res); fails += 1; continue
        cid = res["id"]; time.sleep(0.7)
        st, back = req("GET", f"/emailCampaigns/{cid}")
        v = checks(back.get("htmlContent", ""))
        if back.get("name") != name: v.append("name mismatch")
        if back.get("recipients", {}).get("lists") != payload["recipients"]["listIds"]: v.append("lists mismatch")
        if v:
            print("FAIL verify", cid, name, v); fails += 1
        else:
            created.append(f"OK {cid} {name} | lists {payload['recipients']['listIds']}")
        time.sleep(0.7)

    print("APPLIED" if a.apply else "DRY RUN — pass --apply to create")
    print(f"created ({len(created)}):"); [print("  ", c) for c in created]
    print(f"skipped ({len(skipped)}):"); [print("  ", s) for s in skipped]
    print(f"failures: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
