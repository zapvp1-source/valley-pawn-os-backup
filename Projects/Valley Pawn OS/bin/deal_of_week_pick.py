#!/usr/bin/env python3
"""deal_of_week_pick.py [--render] [--thursday YYYY-MM-DD] — native Deal of the Week compiler (2026-10-05).

Native replacement for the Cowork task `vp-deal-of-week-monday-pick`. The Thursday email to ~11K customers
had not gone out since 9/10: the Cowork pick hosted photos through Chrome + a localhost server + WordPress,
all of which need the Mac connector scheduled sessions lost on 9/17. Same steps as the SKILL, new rails:
  1 target = this week's Thursday 10:00 ET; find the Brevo DRAFT whose name contains "Month D, YYYY"
  2 read TODAY's "Deal of the Week submissions open now" prompt in #deal-of-the-week (C0AVCANK7E3) and every
    manager reply after it (thread replies AND channel messages) — via the ops bot
  3 extract item / price / store / manager / pitch FROM THE SUBMISSION TEXT ONLY (Claude, then verified:
    the price must literally appear in what the manager wrote, the store must be one of the five)
  4 qualifying = photo + price; one per store (latest); fixed order CUL, WAY, HAR, LEX, ROA
  5 photo: Slack file (bot files:read) -> sips 1200px JPEG -> Publer media library (public CDN URL)
  6 replace the dashed "DEAL OF THE WEEK — POPULATED MONDAY" block with the header + the SKILL's deal blocks
  7 PUT + schedule Thursday 10:00 ET, run brevo_preflight.py v3, re-GET: must be queued, placeholder gone
  8 post the confirmation in #deal-of-the-week and DM Joshua the summary
Never leaves the campaign unscheduled when a draft exists (HARDENING RULE 2): zero qualifying deals =
theme-only send. Already queued for that Thursday = do nothing.
"""
import datetime as dt
import html as H
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_ai  # noqa: E402
import vp_publer  # noqa: E402
import vp_slack  # noqa: E402

AGENT = "vp-deal-of-week-monday-pick"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
PREFLIGHT = os.path.expanduser("~/Documents/Claude/Projects/Email Refinement/brevo_preflight.py")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
DRY = os.path.join(OS_DIR, "fleet", "DRY_RUN.json")
CH = "C0AVCANK7E3"
JOSHUA = "U03BB52MDSA"
API = "https://api.brevo.com/v3"
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
ORDER = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
PLACEHOLDER = "DEAL OF THE WEEK — POPULATED MONDAY"


def brevo(path, payload=None, method=None):
    req = urllib.request.Request(API + path, data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"api-key": K, "accept": "application/json", "content-type": "application/json"},
                                 method=method or ("POST" if payload is not None else "GET"))
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
        return json.loads(b) if b else {}


def ledger(sentence):
    with open(LEDGER, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def bot_get(method, **params):
    return vp_slack.call(method, params={k: str(v) for k, v in params.items()})


def submissions(prompt_day):
    """Return (prompt_ts, [messages]) for the prompt posted on prompt_day, or (None, [])."""
    hist = bot_get("conversations.history", channel=CH, limit=100).get("messages", [])
    prompt = None
    for m in hist:
        ts = dt.datetime.fromtimestamp(float(m["ts"]), ET)
        if "Deal of the Week submissions open now" in (m.get("text") or "") and ts.date() == prompt_day:
            prompt = m
            break
    if not prompt:
        return None, []
    p_ts = float(prompt["ts"])
    msgs = {m["ts"]: m for m in hist if float(m["ts"]) > p_ts}
    if prompt.get("reply_count"):
        for m in bot_get("conversations.replies", channel=CH, ts=prompt["ts"], limit=200).get("messages", [])[1:]:
            msgs[m["ts"]] = m
    out = [m for m in msgs.values() if not m.get("bot_id") and m.get("subtype") not in ("bot_message", "channel_join")]
    return prompt["ts"], sorted(out, key=lambda m: float(m["ts"]))


EXTRACT_SYS = ("You extract Deal of the Week submissions written by Valley Pawn store managers. Use ONLY facts written "
               "in each submission — never invent, embellish or add specs. Stores are exactly: Culpeper, Waynesboro, "
               "Harrisonburg, Lexington, Roanoke.")
EXTRACT = """For each numbered submission below return one JSON object. Output ONLY a JSON array.
Fields: "n" (the number), "store" (one of the five, or null), "manager" (first name as written, or null),
"item" (item name + brand, as written, title-cased lightly, no price), "price" (the store's selling price exactly as
written, digits and decimal only, e.g. "299.99"; if several prices appear use the one called our/your/sale price; null
if none), "pitch" (ONE sentence in the manager's own words, light grammar cleanup only, no new claims, max 160 chars).

%s"""


def extract(msgs):
    text = "\n\n".join("#%d (Slack user %s):\n%s" % (i, m.get("user"), m.get("text") or "") for i, m in enumerate(msgs))
    rows = vp_ai.ask_json(EXTRACT % text, EXTRACT_SYS, max_tokens=3000)
    out = []
    for r in rows:
        try:
            m = msgs[int(r["n"])]
        except (KeyError, ValueError, IndexError, TypeError):
            continue
        raw = (m.get("text") or "")
        price = (r.get("price") or "").replace(",", "").lstrip("$")
        ok_price = bool(price) and re.sub(r"[^\d.]", "", price) in re.sub(r"[,$]", "", raw)
        out.append({"store": r.get("store") if r.get("store") in ORDER else None, "manager": r.get("manager") or "",
                    "item": (r.get("item") or "").strip(), "price": price if ok_price else None,
                    "pitch": (r.get("pitch") or "").strip(), "msg": m})
    return out


def photo_url(m):
    imgs = [f for f in (m.get("files") or []) if (f.get("mimetype") or "").startswith("image/")]
    if not imgs:
        return None
    f = imgs[0]
    tok = vp_slack.token()
    d = tempfile.mkdtemp(prefix="dow-")
    src = os.path.join(d, "src" + os.path.splitext(f.get("name") or ".jpg")[1])
    req = urllib.request.Request(f["url_private_download"], headers={"Authorization": "Bearer " + tok})
    open(src, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    dst = os.path.join(d, "deal.jpg")
    subprocess.run(["sips", "-Z", "1200", "-s", "format", "jpeg", src, "--out", dst], capture_output=True, timeout=60)
    if not os.path.exists(dst) or os.path.getsize(dst) < 2000:
        return None
    # Publer's CDN is NOT publicly readable (403 for anyone without a Publer session, found 10/5 verify), so it
    # can never be an email image host. Host on the website's own media library via a WordPress application
    # password (Website/shop-build/.wp_app_credentials, else Keychain vp-wp-app-password). Every URL is proven 200 before use.
    url = wp_upload(dst)
    return url if url and public_ok(url) else None


def public_ok(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status == 200
    except Exception:
        return False


def wp_creds():
    # 1st: the website's existing app password (WP admin name "vp-shop-nightly"), used by the shop sync since 8/13
    f = os.path.expanduser("~/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials")
    if os.path.exists(f):
        kv = dict(l.strip().split("=", 1) for l in open(f) if "=" in l)
        if kv.get("WP_USER") and kv.get("WP_APP_PASSWORD"):
            return kv["WP_USER"].strip().strip('"'), kv["WP_APP_PASSWORD"].strip().strip('"')
    r = subprocess.run(["security", "find-generic-password", "-s", "vp-wp-app-password", "-g"], capture_output=True, text=True)
    acct = re.search(r'"acct"<blob>="([^"]+)"', r.stdout or "")
    pw = subprocess.run(["security", "find-generic-password", "-s", "vp-wp-app-password", "-w"], capture_output=True, text=True).stdout.strip()
    return (acct.group(1), pw) if acct and pw else (None, None)


def wp_upload(path):
    user, pw = wp_creds()
    if not user:
        return None
    import base64
    name = "dow_%s_%s" % (dt.date.today().strftime("%Y%m%d"), os.path.basename(os.path.dirname(path))[-6:] + ".jpg")
    req = urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2/media", data=open(path, "rb").read(), method="POST", headers={
        "Authorization": "Basic " + base64.b64encode(("%s:%s" % (user, pw)).encode()).decode(),
        "Content-Type": "image/jpeg", "Content-Disposition": 'attachment; filename="%s"' % name, "User-Agent": "ValleyPawnOps/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r).get("source_url")


def block(d, slug, first):
    store, sl = d["store"], d["store"].lower()
    e = lambda s: H.escape(s, quote=True)
    b = "" if first else '<hr style="border: none; border-top: 1px solid #e5e5e5; margin: 0 0 32px 0;" />\n'
    b += """<div style="margin: 0 0 32px 0;">
  <p style="margin: 0 0 8px 0; font-size: 12px; letter-spacing: 2px; color: #c97b3a; font-weight: bold;">%s</p>
  <h2 style="margin: 0 0 12px 0; font-size: 24px; line-height: 1.3; color: #1a1a1a;">%s</h2>
  <p style="margin: 0 0 16px 0; font-size: 16px; line-height: 1.5; color: #444;">%s</p>
  <p style="margin: 0 0 20px 0; font-size: 32px; line-height: 1; color: #1a1a1a; font-weight: bold;">$%s</p>
  <img src="%s" alt="%s" style="width: 100%%; max-width: 540px; height: auto; display: block; margin: 0 0 16px 0;" />
  <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+%s+VA&utm_source=brevo&utm_medium=email&utm_campaign=%s&utm_content=deal_of_week_%s" style="display: inline-block; padding: 14px 28px; background: #c97b3a; color: #fff; text-decoration: none; font-weight: bold; font-size: 16px; border-radius: 4px;">See it at our %s store</a>
  <p style="margin: 12px 0 0 0; font-size: 13px; color: #777;">Submitted by %s. While supplies last — usually one of a kind.</p>
</div>
""" % (store.upper(), e(d["item"]), e(d["pitch"]), d["price"], d["img"], e(d["item"]), store, slug, sl, store, e(d["manager"] or "the " + store + " team"))
    return b


def replace_placeholder(html, new):
    i = html.find(PLACEHOLDER)
    if i < 0:
        return None
    start = html.rfind("<div", 0, i)
    depth, j = 0, start
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            j = start + m.end()
            break
    return html[:start] + new + html[j:]


def main():
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    thu = dt.date.fromisoformat(arg("--thursday")) if arg("--thursday") else now.date() + dt.timedelta(days=(3 - now.weekday()) % 7)
    monday = thu - dt.timedelta(days=3)
    label = "%s %d, %d" % (thu.strftime("%B"), thu.day, thu.year)
    when = dt.datetime.combine(thu, dt.time(10, 0), ET)

    for st in ("queued", "sent", "inProcess"):
        for c in brevo("/emailCampaigns?status=%s&limit=50&sort=desc" % st).get("campaigns", []):
            if label in (c.get("name") or ""):
                print("already %s for %s: #%s %s" % (st, label, c["id"], c["name"]))
                return 0
    drafts = [c for c in brevo("/emailCampaigns?status=draft&limit=100").get("campaigns", []) if label in (c.get("name") or "")]
    if not drafts:
        ledger("Thursday %s email: no staged draft carries that date, so the deal email could not be built." % label)
        print("no draft for", label)
        return 1
    camp = brevo("/emailCampaigns/%d" % drafts[0]["id"])
    html = camp.get("htmlContent") or ""
    slug = (re.search(r"utm_campaign=([A-Za-z0-9_\-]+)", html) or [None, "weekly_%s" % thu.isoformat()])[1]

    p_ts, msgs = submissions(monday)
    print("draft #%d %s | prompt %s | %d messages" % (camp["id"], camp["name"], "found" if p_ts else "NOT FOUND (theme-only)", len(msgs)))
    deals, skipped = {}, []
    if msgs:
        for d in extract(msgs):
            m = d["msg"]
            has_img = any((f.get("mimetype") or "").startswith("image/") for f in (m.get("files") or []))
            if not d["store"]:
                continue
            if not (has_img and d["price"]):
                skipped.append(d["store"])
                continue
            deals[d["store"]] = d          # later message for the same store wins (msgs are time-ordered)
    skipped = sorted(set(skipped) - set(deals), key=ORDER.index)
    final = []
    for s in ORDER:
        if s not in deals:
            continue
        d = deals[s]
        if render:
            d["img"] = "(would upload %s)" % ((d["msg"].get("files") or [{}])[0].get("name"))
        else:
            try:
                d["img"] = photo_url(d["msg"])
            except Exception as e:
                print("photo failed for", s, e)
                d["img"] = None
            if not d["img"]:
                skipped.append(s)
                continue
        final.append(d)
    n = len(final)
    if n:
        hdr = "THIS WEEK'S DEALS — ONE FROM EACH STORE" if n == 5 else "THIS WEEK'S DEALS — %d STORES FEATURED THIS WEEK" % n
        new = '<p style="margin: 0 0 24px 0; font-size: 12px; letter-spacing: 2px; color: #c97b3a; font-weight: bold;">%s</p>\n' % hdr
        new += "".join(block(d, slug, i == 0) for i, d in enumerate(final))
    else:
        new = ""
    out = replace_placeholder(html, new)
    if out is None:
        ledger("Thursday %s email: the draft has no deal placeholder to fill; left as is." % label)
        return 1
    for d in final:
        print("  %s — %s — $%s — %s — %s" % (d["store"], d["item"], d["price"], d["manager"], d["pitch"]))
    print("  skipped:", ", ".join(skipped) or "none")
    if render:
        return 0
    if os.path.exists(DRY) and json.load(open(DRY)).get("active"):
        print("publish guard active — not scheduling")
        return 0

    brevo("/emailCampaigns/%d" % camp["id"], {"htmlContent": out}, "PUT")
    p = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(camp["id"])], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        print((p.stdout + p.stderr)[-1500:])
        ledger("Thursday %s email was filled with %d deals but the pre-send check failed; left as a draft for a fix." % (label, n))
        vp_slack.post(JOSHUA, "Thursday's deal email (%s) is built with %d store deals but didn't pass the pre-send check, so it is NOT scheduled yet. I'm on it." % (label, n))
        return 1
    brevo("/emailCampaigns/%d" % camp["id"], {"scheduledAt": when.isoformat()}, "PUT")
    c2 = brevo("/emailCampaigns/%d" % camp["id"])
    if c2.get("status") == "draft" or PLACEHOLDER in (c2.get("htmlContent") or ""):
        ledger("Thursday %s email did not end up scheduled after filling (status %s)." % (label, c2.get("status")))
        vp_slack.post(JOSHUA, "Thursday's deal email (%s) did not schedule. I'm on it." % label)
        return 1
    os.environ["VP_TASK"] = AGENT
    lst = ", ".join("%s (%s)" % (d["item"], d["store"]) for d in final)
    msg = ("This week's email features %d deal%s — %s. Thursday's send is scheduled." % (n, "" if n == 1 else "s", lst)) if n else \
          "No qualifying submissions this week — Thursday's send will run with the theme content only."
    if skipped:
        msg += " Skipped (incomplete): %s." % ", ".join(skipped)
    vp_slack.post(CH, msg)
    vp_slack.post(JOSHUA, "Thursday email is scheduled for %s 10 AM with %d store deal%s:\n%s\nCampaign: %s\nSubject: %s\nPreview: https://my.brevo.com/camp/edit/%d/email-template\nSkipped: %s" % (
        label, n, "" if n == 1 else "s", "\n".join("• %s — $%s — %s" % (d["item"], d["price"], d["store"]) for d in final) or "• (theme only)",
        c2.get("name"), c2.get("subject"), camp["id"], ", ".join(skipped) or "none"))
    print("scheduled #%d for %s" % (camp["id"], when.isoformat()))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        ledger("Thursday deal email did not complete — a service refused a request (%s)." % e.code)
        print("HTTP", e.code, getattr(e, "url", ""), e.read().decode()[:400])
        sys.exit(1)
