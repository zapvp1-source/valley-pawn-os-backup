#!/usr/bin/env python3
"""gold_scorecard.py — the weekly measurement + evaluation step of GOLD_PLAN_OPERATING_LOOP.md.

One finished funnel per store for the last full week (Mon..Sun), compared with the locked baseline:
  found      sessions landing on /sell-gold*/, /sell-silver*/, /sell-coins*/ (GA4 Data API, by landing page)
  acted      sms_click + phone_click + Textchat Message fired ON those pages (GA4)
  searched   Search Console clicks/impressions for gold/silver/coin/jewelry/scrap queries
  conversed  Chekkit conversations in the week where the CUSTOMER wrote about gold/silver/jewelry/coins
  bought     Bravo intake-detail BUY rows in precious-metal / jewelry categories: count and $ per store-day
Writes ceo-briefing/gold/week_<end>.json, appends gold_history.csv, renders report_<end>.md, evaluates the
decision rules (section 5 of the loop doc) and writes the next action to gold_actions.json. Posts nothing.
A source that fails is recorded as "unmeasured" with the reason in the JSON and the log — never a guess.

  gold_scorecard.py [--end YYYY-MM-DD] [--print]
"""
import csv, datetime as dt, glob, json, os, re, sys, time, traceback

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents", "Claude", "Projects")
if not os.path.isdir(PROJ):  # Cowork VM mount
    PROJ = os.path.join(HOME, "mnt", "Projects")
GS = os.path.join(PROJ, "Gold and Silver Markeitng")
OUT = os.environ.get("GOLD_OUT") or os.path.join(GS, "ceo-briefing", "gold")
BRAVO_OUT = os.path.join(PROJ, "Bravo Data Extraction", "output")
sys.path.insert(0, os.path.join(PROJ, "Website", "analytics", "bin"))
sys.path.insert(0, os.path.join(PROJ, "Valley Pawn OS", "bin"))

STORES = ["CUL", "WAY", "HAR", "LEX", "ROA"]
CITY = {"CUL": "Culpeper", "WAY": "Waynesboro", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke"}
SLUG = {"CUL": "culpeper", "WAY": "waynesboro", "HAR": "harrisonburg", "LEX": "lexington", "ROA": "roanoke"}
PM_CAT = re.compile(r"gold|silver|scrap|jewel|ring|chain|coin|bullion|bracelet|necklace|earring|pendant|platinum|watch", re.I)
GOLD_WORDS = re.compile(r"\bgold\b|\bsilver\b|\bjewel|\bring\b|\bchain\b|\bcoin|\bbullion\b|\bscrap\b|\bkarat\b|\b1[04]k\b|\b18k\b|\b22k\b|\b24k\b|\bsterling\b|\bnecklace\b|\bbracelet\b", re.I)
GOLD_PAGE = re.compile(r"/sell-(gold|silver|coins|jewelry)", re.I)
BASELINE = {"start": "2026-09-01", "end": "2026-10-06"}
RULES = {"found_min_sessions": 50, "acted_min_rate": 0.08, "conversed_min_rate": 0.30}


def log(msg):
    sys.stderr.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")


def week_bounds(end=None):
    today = dt.date.today()
    if end:
        e = dt.date.fromisoformat(end)
    else:
        e = today - dt.timedelta(days=today.weekday() + 1)  # last Sunday
    s = e - dt.timedelta(days=6)
    return s, e


# ---------------- Bravo: bought ----------------
def bravo_days():
    """{(date, store): rows} for every single-day intake-detail file with a real header."""
    out = {}
    for f in glob.glob(os.path.join(BRAVO_OUT, "*_intake-detail.csv")):
        m = re.match(r"(\d{4}-\d\d-\d\d)_to_(\d{4}-\d\d-\d\d)_([A-Z]+)_", os.path.basename(f))
        if not m or m.group(1) != m.group(2):
            continue
        try:
            with open(f, encoding="utf-8-sig", errors="replace", newline="") as fh:
                rows = list(csv.DictReader(fh))
        except Exception:
            continue
        if rows and "Ticket Kind" in rows[0]:
            out[(m.group(1), m.group(3))] = rows
        elif not rows:
            out[(m.group(1), m.group(3))] = []  # a real pull with zero rows still counts as covered
    return out


def pm_buys(rows):
    n, usd = 0, 0.0
    for r in rows:
        if r.get("Ticket Kind") != "BUY" or not PM_CAT.search(r.get("Category") or ""):
            continue
        n += 1
        usd += float(re.sub(r"[^0-9.\-]", "", r.get("Loan Amount") or "0") or 0)
    return n, usd


def bought(days, s, e):
    per = {}
    for st in STORES:
        cov, n, usd = 0, 0, 0.0
        d = s
        while d <= e:
            rows = days.get((d.isoformat(), st))
            if rows is not None:
                cov += 1
                a, b = pm_buys(rows)
                n += a; usd += b
            d += dt.timedelta(days=1)
        per[st] = {"store_days": cov, "expected_days": (e - s).days + 1, "buys": n, "usd": round(usd, 2),
                   "buys_per_day": round(n / cov, 2) if cov else None, "usd_per_day": round(usd / cov, 2) if cov else None}
    return per


def baseline(days):
    s, e = dt.date.fromisoformat(BASELINE["start"]), dt.date.fromisoformat(BASELINE["end"])
    return bought(days, s, e)


# ---------------- GA4: found / acted ----------------
def ga4_block(s, e):
    from google_auth import ANALYTICS_SCOPE, api_post
    base = "https://analyticsdata.googleapis.com/v1beta/properties/353209303:runReport"
    rng = [{"startDate": s.isoformat(), "endDate": e.isoformat()}]
    pagef = {"filter": {"fieldName": "pagePath", "stringFilter": {"matchType": "CONTAINS", "value": "/sell-"}}}
    found = {st: {"sessions": 0, "views": 0, "by_channel": {}} for st in STORES}
    found["hub"] = {"sessions": 0, "views": 0, "by_channel": {}}
    r = api_post(base, {"dateRanges": rng, "dimensions": [{"name": "landingPagePlusQueryString"}, {"name": "sessionDefaultChannelGroup"}],
                        "metrics": [{"name": "sessions"}], "limit": 500,
                        "dimensionFilter": {"filter": {"fieldName": "landingPagePlusQueryString", "stringFilter": {"matchType": "CONTAINS", "value": "/sell-"}}}}, ANALYTICS_SCOPE)
    for row in r.get("rows", []):
        lp, ch = row["dimensionValues"][0]["value"], row["dimensionValues"][1]["value"]
        if not GOLD_PAGE.search(lp):
            continue
        n = int(float(row["metricValues"][0]["value"]))
        key = next((st for st in STORES if SLUG[st] in lp), "hub")
        found[key]["sessions"] += n
        found[key]["by_channel"][ch] = found[key]["by_channel"].get(ch, 0) + n
    r = api_post(base, {"dateRanges": rng, "dimensions": [{"name": "pagePath"}], "metrics": [{"name": "screenPageViews"}],
                        "limit": 500, "dimensionFilter": pagef}, ANALYTICS_SCOPE)
    for row in r.get("rows", []):
        p = row["dimensionValues"][0]["value"]
        if GOLD_PAGE.search(p):
            key = next((st for st in STORES if SLUG[st] in p), "hub")
            found[key]["views"] += int(float(row["metricValues"][0]["value"]))
    acted = {k: {"sms_click": 0, "phone_click": 0, "Textchat Message": 0, "calc_quoted": 0, "calc_text_offer": 0} for k in found}
    r = api_post(base, {"dateRanges": rng, "dimensions": [{"name": "pagePath"}, {"name": "eventName"}], "metrics": [{"name": "eventCount"}],
                        "limit": 2000, "dimensionFilter": pagef}, ANALYTICS_SCOPE)
    for row in r.get("rows", []):
        p, ev = row["dimensionValues"][0]["value"], row["dimensionValues"][1]["value"]
        if not GOLD_PAGE.search(p) or ev not in acted["hub"]:
            continue
        key = next((st for st in STORES if SLUG[st] in p), "hub")
        acted[key][ev] += int(float(row["metricValues"][0]["value"]))
    # site-wide leads for context (same definition as the Monday #website post)
    r = api_post(base, {"dateRanges": rng, "dimensions": [{"name": "eventName"}], "metrics": [{"name": "eventCount"}], "limit": 200}, ANALYTICS_SCOPE)
    site = {row["dimensionValues"][0]["value"]: int(float(row["metricValues"][0]["value"])) for row in r.get("rows", [])
            if row["dimensionValues"][0]["value"] in ("sms_click", "phone_click", "Textchat Message", "directions_click")}
    return {"found": found, "acted": acted, "site_leads": site}


# ---------------- Search Console: searched ----------------
def gsc_block(s, e):
    from google_auth import SEARCH_SCOPE, api_post
    url = "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fthevalleypawn.com%2F/searchAnalytics/query"
    j = api_post(url, {"startDate": s.isoformat(), "endDate": e.isoformat(), "dimensions": ["query"], "rowLimit": 1000, "type": "web"}, SEARCH_SCOPE)
    clicks = imps = 0; top = []; pos = []
    for row in j.get("rows", []):
        q = row["keys"][0]
        if GOLD_WORDS.search(q):
            clicks += row["clicks"]; imps += row["impressions"]; pos.append((row["position"], row["impressions"]))
            top.append({"q": q, "clicks": row["clicks"], "impressions": row["impressions"], "position": round(row["position"], 1)})
    top.sort(key=lambda x: (-x["clicks"], -x["impressions"]))
    avgpos = round(sum(p * w for p, w in pos) / sum(w for _, w in pos), 1) if pos else None
    j2 = api_post(url, {"startDate": s.isoformat(), "endDate": e.isoformat(), "dimensions": ["page"], "rowLimit": 500, "type": "web",
                        "dimensionFilterGroups": [{"filters": [{"dimension": "page", "operator": "contains", "expression": "/sell-"}]}]}, SEARCH_SCOPE)
    pages = [{"page": r["keys"][0].replace("https://thevalleypawn.com", ""), "clicks": r["clicks"], "impressions": r["impressions"], "position": round(r["position"], 1)}
             for r in j2.get("rows", []) if GOLD_PAGE.search(r["keys"][0])]
    return {"clicks": clicks, "impressions": imps, "avg_position": avgpos, "top_queries": top[:15], "pages": pages}


# ---------------- Chekkit: conversed ----------------
def chekkit_block(s, e):
    import chekkit_api as ck
    since = dt.datetime.combine(s, dt.time.min).replace(tzinfo=dt.timezone.utc)
    until = dt.datetime.combine(e + dt.timedelta(days=1), dt.time.min).replace(tzinfo=dt.timezone.utc)
    out = {}
    for st in STORES:
        convs = ck.conversations_since(st, since)
        n_conv = n_gold = 0; checked = 0
        for p, c in convs.items():
            last = ck.ts(c.get("lastMessageAt"))
            if last and last >= until:
                continue
            n_conv += 1
            if checked >= 200:
                continue
            checked += 1
            hit = False
            lm = (c.get("lastMessage") or {})
            if isinstance(lm, dict) and GOLD_WORDS.search(lm.get("text") or "") and lm.get("sender") == "customer":
                hit = True
            else:
                try:
                    for m in ck.messages(st, c.get("id") or c.get("_id")):
                        t = ck.ts(m.get("createdAt") or m.get("sentAt"))
                        if m.get("sender") == "customer" and (t is None or since <= t < until) and GOLD_WORDS.search(m.get("text") or ""):
                            hit = True; break
                    time.sleep(0.4)
                except Exception as ex:
                    log(f"chekkit {st} conv {c.get('id')}: {ex}")
            n_gold += 1 if hit else 0
        out[st] = {"conversations": n_conv, "gold_conversations": n_gold, "checked": checked}
    return out


# ---------------- evaluate ----------------
def evaluate(wk):
    f = wk["funnel"]
    msgs, action = [], None
    if "found" in wk["unmeasured"]:
        msgs.append("Found: unmeasured this week (GA4) — fix the pull before judging traffic.")
    else:
        sess = sum(v["sessions"] for v in f["found"].values())
        clicks = sum(sum(v.values()) - v.get("calc_quoted", 0) for v in f["acted"].values())
        rate = clicks / sess if sess else 0
        if sess < RULES["found_min_sessions"]:
            action = ("traffic", f"{sess} sessions landed on the sell-gold pages (rule: ≥{RULES['found_min_sessions']}). Next fix comes from the Traffic backlog.")
        elif rate < RULES["acted_min_rate"]:
            action = ("page", f"{sess} sessions but only {clicks} contact clicks ({rate:.0%}; rule ≥{RULES['acted_min_rate']:.0%}). Next fix comes from the Page backlog.")
        else:
            ck = f.get("conversed")
            if ck and "conversed" not in wk["unmeasured"]:
                conv = sum(v["gold_conversations"] for v in ck.values())
                if clicks and conv / clicks < RULES["conversed_min_rate"]:
                    action = ("response", f"{clicks} clicks became {conv} gold conversations ({conv/clicks:.0%}; rule ≥{RULES['conversed_min_rate']:.0%}). Store response fix.")
            if action is None:
                action = ("offer", "Traffic, clicks and conversations clear the rules; buys decide. Compare payout % by karat against the top two competitors per city.")
    # store lag rule
    lag = []
    for st in STORES:
        b, base = f["bought"][st], wk["baseline"][st]
        if b["store_days"] >= 4 and base["usd_per_day"] and b["usd_per_day"] is not None and b["usd_per_day"] < 0.8 * base["usd_per_day"]:
            lag.append(st)
    return action, lag, msgs


def render(wk):
    s, e = wk["period"]["start"], wk["period"]["end"]
    f, base = wk["funnel"], wk["baseline"]
    L = [f"# We Buy Gold — weekly scorecard {s} → {e}", ""]
    tb = sum(v["buys"] for v in f["bought"].values()); tu = sum(v["usd"] for v in f["bought"].values())
    sd = sum(v["store_days"] for v in f["bought"].values()); ed = sum(v["expected_days"] for v in f["bought"].values())
    bb = sum(v["buys"] for v in base.values()); bu = sum(v["usd"] for v in base.values()); bsd = sum(v["store_days"] for v in base.values())
    L.append(f"**Bought (the number that counts):** {tb} precious-metal/jewelry buys, ${tu:,.0f}, over {sd}/{ed} store-days captured "
             f"→ {tb/sd if sd else 0:.2f} buys and ${tu/sd if sd else 0:,.0f} per store-day. Baseline (Sep 1–Oct 6): {bb/bsd if bsd else 0:.2f} buys and ${bu/bsd if bsd else 0:,.0f} per store-day.")
    if sd < ed:
        L.append(f"Coverage: {ed-sd} store-days missing from Bravo this week — the nightly backfill re-pulls them; rates above use captured days only.")
    L.append("")
    L.append("| Store | Found (sessions) | Acted (text/call/chat) | Gold convos | Buys | $ | Store-days | $/day | Baseline $/day |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for st in STORES:
        fo = f.get("found", {}).get(st, {}); ac = f.get("acted", {}).get(st, {}); ck = (f.get("conversed") or {}).get(st, {}); b = f["bought"][st]
        acted = (ac.get("sms_click", 0) + ac.get("phone_click", 0) + ac.get("Textchat Message", 0)) if ac else "—"
        L.append(f"| {CITY[st]} | {fo.get('sessions','—')} | {acted} | {ck.get('gold_conversations','—')} | {b['buys']} | ${b['usd']:,.0f} | {b['store_days']}/{b['expected_days']} | "
                 f"{'$%s' % format(b['usd_per_day'], ',.0f') if b['usd_per_day'] is not None else '—'} | ${base[st]['usd_per_day'] or 0:,.0f} |")
    hub = f.get("found", {}).get("hub")
    if hub:
        L.append(f"| Hub /sell-gold/ | {hub['sessions']} | {sum(v for k, v in f['acted']['hub'].items() if k != 'calc_quoted')} | | | | | | |")
    L.append("")
    g = f.get("searched")
    if g:
        L.append(f"**Searched:** {g['clicks']} Google clicks from {g['impressions']} impressions on gold/silver/coin/jewelry searches (avg position {g['avg_position']}). "
                 + ("Top: " + "; ".join(f"“{q['q']}” {q['clicks']}/{q['impressions']} @{q['position']}" for q in g["top_queries"][:5]) if g["top_queries"] else "No gold queries recorded."))
    sl = f.get("site_leads")
    if sl:
        L.append(f"**Whole site for context:** {sl.get('phone_click',0)} calls, {sl.get('sms_click',0)} texts, {sl.get('Textchat Message',0)} chats, {sl.get('directions_click',0)} directions.")
    if wk["unmeasured"]:
        L.append("**Unmeasured this week:** " + "; ".join(f"{k} ({v})" for k, v in wk["unmeasured"].items()))
    L.append("")
    a = wk["evaluation"]
    if a["action"]:
        L.append(f"**Rule that fired:** {a['action'][0].upper()} — {a['action'][1]}")
    if a["lagging_stores"]:
        L.append(f"**Stores below 80% of their own baseline:** {', '.join(CITY[s] for s in a['lagging_stores'])}.")
    if wk.get("annotations"):
        L.append("**Changes live this week:** " + "; ".join(wk["annotations"]))
    return "\n".join(L) + "\n"


def main():
    end = None; do_print = False
    args = sys.argv[1:]
    if "--end" in args:
        end = args[args.index("--end") + 1]
    do_print = "--print" in args
    s, e = week_bounds(end)
    os.makedirs(OUT, exist_ok=True)
    wk = {"period": {"start": s.isoformat(), "end": e.isoformat()}, "generated": dt.datetime.now().isoformat(timespec="seconds"),
          "funnel": {}, "unmeasured": {}, "rules": RULES}
    days = bravo_days()
    wk["funnel"]["bought"] = bought(days, s, e)
    wk["baseline"] = baseline(days)
    for name, fn in (("ga4", ga4_block), ("searched", gsc_block), ("conversed", chekkit_block)):
        try:
            blk = fn(s, e)
            if name == "ga4":
                wk["funnel"].update(blk)
            else:
                wk["funnel"][name] = blk
        except Exception as ex:
            key = "found" if name == "ga4" else name
            wk["unmeasured"][key] = str(ex).splitlines()[0][:160]
            log(f"{name}: {ex}\n{traceback.format_exc()}")
    ann_file = os.path.join(OUT, "annotations.json")
    if os.path.exists(ann_file):
        try:
            anns = json.load(open(ann_file))
            wk["annotations"] = [a["note"] for a in anns if s.isoformat() <= a["date"] <= e.isoformat()]
        except Exception:
            pass
    action, lag, msgs = evaluate(wk)
    wk["evaluation"] = {"action": action, "lagging_stores": lag, "notes": msgs}
    json.dump(wk, open(os.path.join(OUT, f"week_{e.isoformat()}.json"), "w"), indent=1)
    json.dump(wk, open(os.path.join(OUT, "week_latest.json"), "w"), indent=1)
    rep = render(wk)
    open(os.path.join(OUT, f"report_{e.isoformat()}.md"), "w").write(rep)
    open(os.path.join(OUT, "report_latest.md"), "w").write(rep)
    # history
    hist = os.path.join(OUT, "gold_history.csv")
    new = not os.path.exists(hist)
    rows = []
    for st in STORES:
        b = wk["funnel"]["bought"][st]; fo = wk["funnel"].get("found", {}).get(st, {}); ac = wk["funnel"].get("acted", {}).get(st, {})
        ck = (wk["funnel"].get("conversed") or {}).get(st, {})
        rows.append([e.isoformat(), st, fo.get("sessions", ""), (ac.get("sms_click", 0) + ac.get("phone_click", 0) + ac.get("Textchat Message", 0)) if ac else "",
                     ck.get("gold_conversations", ""), b["buys"], b["usd"], b["store_days"], b["expected_days"], action[0] if action else ""])
    existing = []
    if not new:
        existing = [r for r in csv.reader(open(hist)) if r and r[0] != e.isoformat()]
    with open(hist, "w", newline="") as fh:
        w = csv.writer(fh)
        if new or not existing or existing[0][0] != "week_end":
            w.writerow(["week_end", "store", "found_sessions", "acted_clicks", "gold_conversations", "pm_buys", "pm_usd", "store_days", "expected_days", "rule_fired"])
            existing = [r for r in existing if r[0] != "week_end"]
        w.writerows(existing); w.writerows(rows)
    # actions
    af = os.path.join(OUT, "gold_actions.json")
    acts = json.load(open(af)) if os.path.exists(af) else []
    if action:
        acts.append({"week_end": e.isoformat(), "rule": action[0], "why": action[1], "lagging_stores": lag, "status": "open", "logged": wk["generated"]})
        json.dump(acts, open(af, "w"), indent=1)
    if do_print:
        print(rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
