#!/usr/bin/env python3
"""build_month.py — build one month's "Shop Us Online" (eBay) campaign pack.

Owner: the monthly eBay customer campaign (see PLAYBOOK.md in this folder).

    python3 build_month.py                      # next calendar month, dry run (files only)
    python3 build_month.py --month 2026-10      # a specific month
    python3 build_month.py --month 2026-10 --apply
          # ALSO creates the Brevo email as a DRAFT
    python3 build_month.py --month 2026-10 --schedule
          # creates/reuses the draft, runs the house preflight (Email Refinement/brevo_preflight.py),
          # then schedules it for the 1st Tuesday 10:00 ET. Joshua authorized full automation 2026-09-29.

WHAT IT PRODUCES  ->  packs/<YYYY-MM>/
    email.html      full customer email, built from the production master (campaign 28 shell)
    push.txt        push title + body + link  (paste into Bravo / MobilePawn marketing)
    sms.txt         one text, <=160 chars incl. link + STOP line (paste into Bravo marketing)
    featured.json   the 6 live eBay items featured this month
    PACK.md         send dates, audiences, links, compliance checklist, KPIs
    brevo_draft.json  (only with --apply) the created draft id + GET-verification

HARD RULES (do not loosen):
  - Schedules only with --schedule, and only after every automated check AND the house preflight pass.
  - Never features weapons / knives / replicas / firearm accessories (valley-pawn-context).
  - Never names a draft with a "Month D, YYYY" date string — the Deal-of-the-Week picker
    matches that pattern to find WEEKLY drafts (see Email Refinement/_audit/build_calendar.py).
  - Email must keep logo, call+text per store with number visible, 5-store directory, DBA-only
    footer — all of which live in the LOCKED regions of the base and are left untouched.
"""
import argparse, calendar, datetime as dt, html, json, os, re, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.dirname(HERE)
ITEMS = os.path.join(PROJECTS, "Website", "shop-build", "items.json")
LOCAL_CAMPS = os.path.join(PROJECTS, "Email Refinement", "_audit", "allcamps.json")
KEY_PATH = os.path.expanduser("~/.config/valley-pawn/brevo_api_key")
BASE = "https://api.brevo.com/v3"
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
BASE_CAMPAIGN_ID = 28           # production master shell (W13) — same base build_calendar.py uses
BASE_UTM = "weekly_lexington_2026-08-27"
SEEDS_LIST = 10
SHOP = "https://thevalleypawn.com/shop/"
APP_URL = "https://thevalleypawn.com/app/"   # MobilePawn (Bravo) download page — redirects to App Store / Google Play
try:
    _CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
except Exception:
    _CFG = {}
APP_BLOCK = bool(_CFG.get("app_block_enabled", False))
APP_SMS = bool(_CFG.get("app_sms_own", False))   # our monthly text carries the MobilePawn ask (fallback if Bravo won't run theirs monthly)

STORES = {
    "Culpeper":     {"ebay": "https://www.ebay.com/str/vpculpeper",             "tel": "+15404455510", "ph": "(540) 445-5510"},
    "Waynesboro":   {"ebay": "https://www.ebay.com/str/valleypawnwaynesboro",   "tel": "+15402216346", "ph": "(540) 221-6346"},
    "Harrisonburg": {"ebay": "https://www.ebay.com/str/valleypawnharrisonburg", "tel": "+15405744500", "ph": "(540) 574-4500"},
    "Lexington":    {"ebay": "https://www.ebay.com/str/valleypawnlexington",    "tel": "+15404618349", "ph": "(540) 461-8349"},
    "Roanoke":      {"ebay": "https://www.ebay.com/str/valleypawnroanoke",      "tel": "+15405620776", "ph": "(540) 562-0776"},
}

EXCLUDE = re.compile(
    r"\b(knife|knives|sword|swords|blade|blades|replica|gun|guns|pistol|rifle|shotgun|firearm|"
    r"ammo|ammunition|holster|scope|magazine|airsoft|bb|pellet|taser|stun|pepper|crossbow|"
    r"bayonet|machete|dagger|katana|tactical|knuckle|knuckles|nunchuck|throwing|hatchet|axe)\b", re.I)

# 2026-10-01: Roanoke now open Wednesdays (Joshua) — canonical hours line updated.
# 2026-10-01 (later): any store open 6 days a week closes 5 PM Saturdays (Joshua) — Culpeper & Roanoke Sat 10am-5pm.
HOURS = ("Culpeper &amp; Roanoke: Mon&ndash;Fri 10am&ndash;6pm, Sat 10am&ndash;5pm. Harrisonburg, Waynesboro &amp; Lexington: "
         "Mon, Tue, Thu, Fri &amp; Sat 10am&ndash;6pm (closed Wed &amp; Sun).")
SIX_DAY_BLOCK = "Mon\u2013Fri 10am\u20136pm, Sat 10am\u20135pm"
# The base shell (sent campaign 28) still carries the pre-10/1 hours in its LOCKED footer + YOUR STORE block;
# build_email() swaps these exact strings so every new build ships the current hours.
OLD_HOURS_FIXES = [
    ("Culpeper: Mon&ndash;Sat 10am&ndash;6pm. All other stores: Mon, Tue, Thu, Fri &amp; Sat 10am&ndash;6pm (closed Wed &amp; Sun).", HOURS),
    ("Culpeper &amp; Roanoke: Mon&ndash;Sat 10am&ndash;6pm. Harrisonburg, Waynesboro &amp; Lexington: "
     "Mon, Tue, Thu, Fri &amp; Sat 10am&ndash;6pm (closed Wed &amp; Sun).", HOURS),
    ("Roanoke &middot; Mon, Tue, Thu, Fri & Sat 10am\u20136pm", "Roanoke &middot; " + SIX_DAY_BLOCK),
    ("Roanoke &middot; Mon\u2013Sat 10am\u20136pm", "Roanoke &middot; " + SIX_DAY_BLOCK),
    ("Culpeper &middot; Mon\u2013Sat 10am\u20136pm", "Culpeper &middot; " + SIX_DAY_BLOCK),
]


# ------------------------------------------------------------------ helpers
def nth_weekday(year, month, weekday, n):
    """weekday: Mon=0 ... Sun=6; n: 1-based."""
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if dt.date(year, month, d).weekday() == weekday]
    return dt.date(year, month, days[n - 1])


def utm(url, source, medium, campaign, content=None):
    sep = "&" if "?" in url else "?"
    u = f"{url}{sep}utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"
    return u + (f"&utm_content={content}" if content else "")


def price_val(p):
    try:
        return float(re.sub(r"[^\d.]", "", p) or 0)
    except ValueError:
        return 0.0


def pick_featured(items, keywords, n=6):
    ok = [i for i in items if not EXCLUDE.search(i["t"]) and i.get("img") and i.get("u")]
    kwre = re.compile(r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b", re.I) if keywords else None
    themed = [i for i in ok if kwre.search(i["t"])] if kwre else []
    pool = themed if len(themed) >= n else themed + [i for i in ok if i not in themed]
    # round-robin across stores so the email shows the whole company, biggest tickets first
    by_store = {}
    for i in sorted(pool, key=lambda x: -price_val(x["p"])):
        if 25 <= price_val(i["p"]) <= 1500:      # skip giveaway-priced and sticker-shock items
            by_store.setdefault(i["s"], []).append(i)
    order = sorted(by_store, key=lambda s: -len(by_store[s]))
    out = []
    while len(out) < n and any(by_store.values()):
        for s in order:
            if by_store[s] and len(out) < n:
                out.append(by_store[s].pop(0))
    return out, len(themed)


def gsm_ok(s):
    return all(ord(c) < 128 for c in s)


# ------------------------------------------------------------------ email
CODE_RE = re.compile(r"\s*\(?(?:VAP|VP|VA|CUL|ROA|WAY|HAR|LEX)\d{5,}\)?", re.I)


def clean_title(t):
    """Display only: decode entities and hide Bravo intake codes (eBay listing is untouched)."""
    return re.sub(r"\s{2,}", " ", CODE_RE.sub("", html.unescape(t))).strip(" -")


def item_cell(it, camp):
    link = html.escape(utm(it["u"], "brevo", "email", camp, f"item_{it['s'].lower()}"))
    title = html.escape(clean_title(it["t"]))
    return (
        '<td class="stack" width="50%" valign="top" style="padding:8px;">'
        f'<a href="{link}" style="text-decoration:none;color:#1a1a1a;">'
        f'<img src="{html.escape(it["img"])}" width="240" alt="{title}" '
        'style="display:block;width:100%;max-width:240px;height:auto;border-radius:8px;border:1px solid #EEE;margin:0 auto 8px auto;">'
        f'<p style="margin:0 0 4px 0;font-size:14px;line-height:1.35;color:#1a1a1a;">{title}</p>'
        f'<p style="margin:0;font-size:15px;font-weight:700;color:#2D1A5E;">{html.escape(it["p"])} '
        f'<span style="font-size:12px;font-weight:600;color:#0099DD;">&middot; {html.escape(it["s"])}</span></p>'
        '</a></td>')


def body_block(cfg, featured, camp):
    paras = "\n".join(
        f'<p style="margin:0 0 14px 0; font-size:16px; line-height:1.6; color:#1a1a1a;">{b}</p>'
        for b in cfg["body"])
    rows = ""
    for k in range(0, len(featured), 2):
        pair = featured[k:k + 2]
        rows += "<tr>" + "".join(item_cell(i, camp) for i in pair) + ("<td></td>" if len(pair) == 1 else "") + "</tr>\n"
    grid = (
        '<p style="margin:18px 0 6px 0;font-size:12px;letter-spacing:2px;color:#c97b3a;font-weight:700;">'
        'ONLINE NOW FROM OUR STORES</p>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        + rows + '</table>')
    links = " &nbsp;&middot;&nbsp; ".join(
        f'<a href="{html.escape(utm(v["ebay"], "brevo", "email", camp, "ebay_" + k.lower()))}" '
        f'style="color:#0099DD;font-weight:700;">{k}</a>' for k, v in STORES.items())
    stores = (
        '<p style="margin:18px 0 6px 0;font-size:14px;line-height:1.6;color:#1a1a1a;">'
        '<strong>Browse one store&rsquo;s online shelf:</strong><br>' + links + '</p>'
        '<p style="margin:10px 0 0 0;font-size:14px;line-height:1.6;color:#555;">'
        'Saw it online but want to see it in person? Call or text that store &mdash; numbers are below.</p>')
    return paras + "\n" + grid + "\n" + stores


def cta_block(camp):
    href = html.escape(utm(SHOP, "brevo", "email", camp, "primary_cta"))
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
        '<td align="center" bgcolor="#F58C8A" style="border-radius:999px;">'
        f'<a href="{href}" style="display:inline-block;padding:16px 32px;font-size:16px;font-weight:700;'
        'color:#2D1A5E;text-decoration:none;border-radius:999px;letter-spacing:0.2px;">'
        'Shop all 5 stores online &rarr;</a></td></tr></table>'
        f'<p style="margin:14px 0 0 0;color:#777777;font-size:13px;line-height:1.5;">{HOURS}</p>')


def app_block(camp):
    """MobilePawn download ask (added 2026-09-29, config.json app_block_enabled)."""
    href = html.escape(utm(APP_URL, "brevo", "email", camp, "app_download"))
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:22px 0 0 0;background:#F4F1FB;border-radius:10px;"><tr><td style="padding:18px 20px;">'
        '<p style="margin:0 0 6px 0;font-size:12px;letter-spacing:2px;color:#c97b3a;font-weight:700;">GET THE FREE APP</p>'
        '<p style="margin:0 0 12px 0;font-size:16px;line-height:1.5;color:#1a1a1a;">'
        'Pay or extend your loan, make layaway payments and check due dates from your phone with '
        '<strong>MobilePawn</strong>. Download it and choose Valley Pawn.</p>'
        f'<a href="{href}" style="display:inline-block;padding:12px 24px;font-size:15px;font-weight:700;'
        'color:#ffffff;background:#2D1A5E;text-decoration:none;border-radius:999px;">Download MobilePawn &rarr;</a>'
        '</td></tr></table>')


def build_email(base, cfg, featured, camp):
    h = base
    # title + preheader + hero (variable regions only)
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(cfg['headline'])}</title>", h, 1, re.S)
    h = re.sub(r"(mso-hide:all;\">)\s*.*?\s*(</div>)", lambda m: m.group(1) + "\n  " + cfg["subline"] + "\n" + m.group(2), h, 1, re.S)
    hero_s = h.find("<!-- ============ HERO BAND")
    hero_e = h.find("<!-- ============", hero_s + 10)
    hero = h[hero_s:hero_e]
    hero = re.sub(r"(font-weight:700;\">).*?(</p>)", lambda m: m.group(1) + cfg["eyebrow"] + m.group(2), hero, 1, re.S)
    hero = re.sub(r"(<h1[^>]*>).*?(</h1>)", lambda m: m.group(1) + "\n              " + cfg["headline"] + "\n            " + m.group(2), hero, 1, re.S)
    hero = re.sub(r"(color:#E6DEF7;[^>]*>).*?(</p>)", lambda m: m.group(1) + "\n              " + cfg["subline"] + "\n            " + m.group(2), hero, 1, re.S)
    h = h[:hero_s] + hero + h[hero_e:]
    # body slot: replace everything inside the slot's <td> (drops the weekly deal placeholder)
    bs = h.find("<!-- ============ BODY CONTENT SLOT")
    be = h.find("<!-- ============ LOCKED: TRUST STRIP")
    slot = h[bs:be]
    td_open = slot.find(">", slot.find("<td")) + 1
    td_close = slot.rfind("</td>")
    slot = slot[:td_open] + "\n" + body_block(cfg, featured, camp) + (app_block(camp) if APP_BLOCK else "") + "\n          " + slot[td_close:]
    h = h[:bs] + slot + h[be:]
    # primary CTA: one button to the shop page + correct hours
    cs = h.find("<!-- ============ PRIMARY CTA")
    ce = h.find("<!-- ============", cs + 10)
    cta = h[cs:ce]
    td_open = cta.find(">", cta.find("<td")) + 1
    td_close = cta.rfind("</td>")
    cta = cta[:td_open] + "\n" + cta_block(camp) + "\n          " + cta[td_close:]
    h = h[:cs] + cta + h[ce:]
    # campaign tag everywhere (locked regions keep their utm_content)
    h = h.replace(BASE_UTM, camp)
    for a, b in OLD_HOURS_FIXES:   # 2026-10-01 Roanoke Wednesdays
        h = h.replace(a, b)
    return h


def check_email(h, camp):
    probs = []
    if "DEAL OF THE WEEK" in h: probs.append("weekly deal placeholder still present")
    if BASE_UTM in h: probs.append("old utm_campaign still present")
    if "vp_logo_name-no-tag.png" not in h: probs.append("logo missing")
    for s, v in STORES.items():
        if f"thevalleypawn.com/c/{s.lower()}" not in h: probs.append(f"call link missing for {s}")
        if f"thevalleypawn.com/t/{s.lower()}" not in h: probs.append(f"text link missing for {s}")
        if v["ph"] not in h: probs.append(f"phone number not visible for {s}")
    if "Full Circle Finance" in h: probs.append("legal entity name in customer email")
    if re.search(r"dixie", h, re.I): probs.append("legacy name present")
    if EXCLUDE.search(re.sub(r"<[^>]+>", " ", h.split("BODY CONTENT SLOT")[1].split("TRUST STRIP")[0])):
        probs.append("weapon-type word in body")
    if "utm_content=primary_cta" not in h: probs.append("primary CTA tag missing")
    if SHOP not in h: probs.append("shop link missing")
    if APP_BLOCK and "utm_content=app_download" not in h: probs.append("MobilePawn app block missing")
    return probs


# ------------------------------------------------------------------ brevo
def brevo(method, path, body=None):
    key = open(KEY_PATH).read().strip()
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"api-key": key, "Content-Type": "application/json",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def load_base():
    if os.path.exists(KEY_PATH):
        st, c = brevo("GET", f"/emailCampaigns/{BASE_CAMPAIGN_ID}")
        if st == 200 and c.get("htmlContent"):
            return c["htmlContent"], "live Brevo campaign 28"
    d = json.load(open(LOCAL_CAMPS))
    cs = d if isinstance(d, list) else d.get("campaigns", d)
    return [c for c in cs if c["id"] == BASE_CAMPAIGN_ID][0]["htmlContent"], "local snapshot of campaign 28"


WEEKLY_NAME = re.compile(r"— [A-Z][a-z]+ \d{1,2}, \d{4}$")   # weekly drafts: "<Theme> — Month D, YYYY"


def recipients_like_last_weekly():
    """Send to exactly the audience the most recent SENT *weekly* email reached (proven
    deliverability while the sending domain warms), plus the internal seeds list.
    Only weekly-named campaigns count — a one-off (e.g. giveaway, list 6) must never set the audience.
    Fails closed: returns None if no sent weekly is found."""
    st, res = brevo("GET", "/emailCampaigns?status=sent&limit=100&sort=desc")
    if st != 200:
        return None
    camps = [c for c in res.get("campaigns", []) if WEEKLY_NAME.search(c.get("name", ""))]
    camps.sort(key=lambda c: c.get("sentDate") or "", reverse=True)
    for c in camps:
        ls = (c.get("recipients") or {}).get("lists") or []
        if ls:
            return sorted(set(ls) | {SEEDS_LIST})
    return None


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--schedule", action="store_true", help="create/reuse the draft, run house preflight, schedule it")
    a = ap.parse_args()
    today = dt.date.today()
    if a.month:
        y, m = map(int, a.month.split("-"))
    else:
        y, m = (today.year + (today.month == 12), today.month % 12 + 1)
    key = f"{y:04d}-{m:02d}"
    cal = json.load(open(os.path.join(HERE, "calendar.json")))["months"]
    if key not in cal:
        sys.exit(f"FAIL: no theme for {key} in calendar.json — add one (see PLAYBOOK.md) and rerun")
    cfg = cal[key]
    camp = f"ebay_monthly_{key}"
    tag = f"eb{key[2:4]}{key[5:7]}"                       # short tag for SMS / push links

    items = json.load(open(ITEMS))["items"]
    featured, n_themed = pick_featured(items, cfg["keywords"])
    if len(featured) < 4:
        sys.exit(f"FAIL: only {len(featured)} eligible live items — shop feed looks empty; rerun after the nightly shop refresh")

    email_date = nth_weekday(y, m, 1, 1)   # 1st Tuesday
    push_date = nth_weekday(y, m, 4, 2)    # 2nd Friday
    sms_date = nth_weekday(y, m, 3, 3)     # 3rd Thursday

    push_link = f"{SHOP}?utm_source=bravo_push&utm_medium=push&utm_campaign={tag}"
    sms_link = f"thevalleypawn.com/shop/?utm_source=sms&utm_campaign={tag}"
    sms = f"{cfg['sms']} {sms_link} Reply STOP to opt out"
    if len(sms) > 160 or not gsm_ok(sms):
        sms = f"Valley Pawn: shop all 5 stores online. {sms_link} Reply STOP to opt out"
    if APP_SMS:
        # One text a month, both asks. Short links keep it inside one 160-char GSM segment.
        app_link = f"thevalleypawn.com/app/?utm_source=sms&utm_campaign={tag}"
        sms = f"Valley Pawn: pay your loan from your phone w/ our free app thevalleypawn.com/app/?utm_source=sms Shop online thevalleypawn.com/shop Reply STOP to opt out"
        if len(sms) > 160:
            sms = f"Valley Pawn: pay your loan from your phone w/ our free app {app_link} Reply STOP to opt out"

    base, base_src = load_base()
    email = build_email(base, cfg, featured, camp)
    problems = check_email(email, camp)
    if len(cfg["push_title"]) > 40: problems.append("push title over 40 chars")
    if len(cfg["push_body"]) > 120: problems.append("push body over 120 chars")
    if len(sms) > 160 or not gsm_ok(sms): problems.append(f"SMS is {len(sms)} chars / non-GSM")

    out = os.path.join(HERE, "packs", key)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "email.html"), "w").write(email)
    json.dump(featured, open(os.path.join(out, "featured.json"), "w"), indent=1)
    open(os.path.join(out, "push.txt"), "w").write(
        f"SEND: {push_date:%A %B %-d, %Y} around 11:00 AM\nAUDIENCE: all MobilePawn app users, all 5 stores\n\n"
        f"TITLE ({len(cfg['push_title'])}/40): {cfg['push_title']}\n"
        f"BODY ({len(cfg['push_body'])}/120): {cfg['push_body']}\nLINK: {push_link}\n")
    open(os.path.join(out, "sms.txt"), "w").write(
        f"SEND: {sms_date:%A %B %-d, %Y} around 11:00 AM (never before 8am or after 9pm)\n"
        f"AUDIENCE: the per-store Chekkit lists (chekkit_<Store>.csv); opt-in/opt-out handled by Chekkit\n\n"
        f"TEXT ({len(sms)}/160):\n{sms}\n")

    store_ct = {}
    for i in items:
        store_ct[i["s"]] = store_ct.get(i["s"], 0) + 1
    pack = f"""# Shop Us Online — {key} — "{cfg['theme']}"

Built {dt.datetime.now():%Y-%m-%d %H:%M} from {len(items)} live online items ({', '.join(f'{k} {v}' for k, v in store_ct.items())}).
Email base: {base_src}. Featured items: {len(featured)} ({n_themed} matched this month's theme).
Automated checks: {'ALL PASSED' if not problems else 'PROBLEMS: ' + '; '.join(problems)}

| # | Channel | Send | Audience | Where it's sent from |
|---|---|---|---|---|
| 1 | Email | {email_date:%a %b %-d} 10:00 AM | Same lists as the latest weekly email + internal seeds | Brevo (draft "Shop Online — {key}") |
| 2 | Push | {push_date:%a %b %-d} ~11:00 AM | All MobilePawn app users | Bravo marketing (push.txt) |
| 3 | Text | {sms_date:%a %b %-d} ~11:00 AM | Per-store Chekkit lists | Chekkit (sms.txt + chekkit_*.csv) |

Email subject: **{cfg['subject']}**
Preview text: {cfg['subline']}

Links (each channel tagged so we can see what worked):
- Email button: {utm(SHOP, 'brevo', 'email', camp, 'primary_cta')}
- Push: {push_link}
- Text: https://{sms_link}

Featured this month:
""" + "\n".join(f"- {i['s']}: {clean_title(i['t'])} — {i['p']}" for i in featured) + f"""

Before each send (30 seconds): open the link on a phone and confirm the shop page loads with items.
Results: read at month end per PLAYBOOK.md §Scorecard.
"""
    open(os.path.join(out, "PACK.md"), "w").write(pack)

    print(f"{key}: pack written to {out}")
    print("checks:", "ALL PASSED" if not problems else problems)

    if a.apply or a.schedule:
        if problems:
            sys.exit("FAIL: not touching Brevo until the checks pass")
        name = f"Shop Online — {key}"
        cid, status = None, None
        for stt in ("queued", "draft", "inProcess", "sent"):
            st, ex = brevo("GET", f"/emailCampaigns?status={stt}&limit=100&sort=desc")
            hit = [c for c in (ex.get("campaigns", []) if st == 200 else []) if c["name"] == name]
            if hit:
                cid, status = hit[0]["id"], stt
                break
        lists = recipients_like_last_weekly()
        if not lists:
            sys.exit("FAIL: could not determine the weekly-email audience — nothing created or scheduled")
        if cid is not None:
            st, cur = brevo("GET", f"/emailCampaigns/{cid}")
            have = sorted((cur.get("recipients") or {}).get("lists") or [])
            if st == 200 and have != lists:     # self-heal a wrong audience before it sends
                st2, r2 = brevo("PUT", f"/emailCampaigns/{cid}", {"recipients": {"listIds": lists}})
                print(f"audience corrected {have} -> {lists}: {st2}")
                if st2 >= 300:
                    sys.exit(f"FAIL: audience correction returned {st2}: {r2}")
        if status in ("inProcess", "sent"):
            print(f"done already: '{name}' is {status} (id {cid})")
            return
        if status == "queued":
            st, got = brevo("GET", f"/emailCampaigns/{cid}")
            sv = {"id": cid, "status": got.get("status"), "scheduledAt": got.get("scheduledAt"),
                  "lists": (got.get("recipients") or {}).get("lists")}
            json.dump(sv, open(os.path.join(out, "brevo_state.json"), "w"), indent=1)
            print("already scheduled:", sv)
            if sorted(sv["lists"] or []) != lists:
                sys.exit("FAIL: audience did not verify")
            return
        if cid is None:
            payload = {"name": name, "subject": cfg["subject"], "previewText": cfg["subline"],
                       "sender": SENDER, "replyTo": REPLY_TO, "htmlContent": email,
                       "recipients": {"listIds": lists}}
            st, res = brevo("POST", "/emailCampaigns", payload)
            if st >= 300:
                sys.exit(f"FAIL: Brevo draft create returned {st}: {res}")
            cid = res["id"]
        st, got = brevo("GET", f"/emailCampaigns/{cid}")
        v = {"id": cid, "name": got.get("name"), "status": got.get("status"),
             "lists": (got.get("recipients") or {}).get("lists"),
             "html_ok": not check_email(got.get("htmlContent", ""), camp)}
        json.dump(v, open(os.path.join(out, "brevo_draft.json"), "w"), indent=1)
        print("brevo draft:", v)
        if v["status"] != "draft" or not v["html_ok"]:
            sys.exit("FAIL: draft did not verify")

        if a.schedule:
            # house preflight (auto-fixes mechanical defects, hard-fails judgment defects)
            pre = os.path.join(PROJECTS, "Email Refinement", "brevo_preflight.py")
            rc = os.system(f'"{sys.executable}" "{pre}" {cid}')
            if rc != 0:
                sys.exit("FAIL: house preflight did not pass — left as draft, not scheduled")
            from zoneinfo import ZoneInfo
            et = ZoneInfo("America/New_York")
            when = dt.datetime.combine(email_date, dt.time(10, 0), tzinfo=et)
            now = dt.datetime.now(et)
            if when < now + dt.timedelta(hours=2):       # late build: next weekday 10am, never same-hour
                when = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(10, 0), tzinfo=et)
                while when.weekday() in (2, 5, 6):        # skip Wed/Sat/Sun
                    when += dt.timedelta(days=1)
            st, res = brevo("PUT", f"/emailCampaigns/{cid}", {"scheduledAt": when.isoformat()})
            if st >= 300:
                sys.exit(f"FAIL: schedule returned {st}: {res}")
            st, got = brevo("GET", f"/emailCampaigns/{cid}")
            sv = {"id": cid, "status": got.get("status"), "scheduledAt": got.get("scheduledAt"),
                  "intended": when.isoformat()}
            json.dump(sv, open(os.path.join(out, "brevo_state.json"), "w"), indent=1)
            print("scheduled:", sv)
            if not got.get("scheduledAt"):
                sys.exit("FAIL: schedule did not verify")

if __name__ == "__main__":
    main()
