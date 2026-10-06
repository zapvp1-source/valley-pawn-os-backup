#!/usr/bin/env python3
"""website_deals.py [--render] — native vp-website-deals-weekly (Mon 13:05, 2026-10-05).

Mirrors this week's Deal of the Week (the Thursday Brevo campaign's deal blocks, whose photos are already public
on thevalleypawn.com) onto https://thevalleypawn.com/retail/ inside <!-- VP-DEALS:START --> ... <!-- VP-DEALS:END -->.
Same rules as the SKILL: rolling store (dedupe store|item|price, prune > 21 days, newest 10), weapons never shown,
card design + scarcity line + Call/Text/Directions, publish via WP REST with the site's app password
(Website/shop-build/.wp_app_credentials), verify /retail/ 200 + exactly one marker pair, then one line to #website.
Never touches content outside the markers. Backs up the page raw before every write."""
import base64
import datetime as dt
import html as H
import json
import os
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
STORE = os.path.expanduser("~/Documents/Claude/Scheduled/vp-website-deals-weekly/deal_store.json")
BACKUP = os.path.join(OS_DIR, "fleet", "website_backups")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CREDS = os.path.expanduser("~/Documents/Claude/Projects/Website/shop-build/.wp_app_credentials")
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
SITE = "https://thevalleypawn.com"
CH = "C0ASE9C0GQ0"
PHONES = {"Culpeper": ("+15404455510", "(540) 445-5510"), "Waynesboro": ("+15402216346", "(540) 221-6346"),
          "Harrisonburg": ("+15405744500", "(540) 574-4500"), "Lexington": ("+15404618349", "(540) 461-8349"),
          "Roanoke": ("+15405620776", "(540) 562-0776")}
WEAPON = re.compile(r"\b(gun|firearm|rifle|pistol|shotgun|revolver|ammo|ammunition|handgun|glock|ar-15|scope mount)\b", re.I)
START, END = "<!-- VP-DEALS:START -->", "<!-- VP-DEALS:END -->"


def ledger(sentence):
    with open(LEDGER, "a") as fh:
        fh.write("| %s (native) | vp-website-deals-weekly | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), sentence))


def wp(path, payload=None, method="GET"):
    kv = dict(l.strip().split("=", 1) for l in open(CREDS) if "=" in l)
    auth = base64.b64encode(("%s:%s" % (kv["WP_USER"].strip().strip('"'), kv["WP_APP_PASSWORD"].strip().strip('"'))).encode()).decode()
    req = urllib.request.Request(SITE + "/wp-json/wp/v2" + path, data=json.dumps(payload).encode() if payload is not None else None, method=method,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def brevo(path):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.brevo.com/v3" + path, headers={"api-key": K}), timeout=60))


def this_weeks_deals(today):
    thu = today + dt.timedelta(days=(3 - today.weekday()) % 7)
    label = "%s %d, %d" % (thu.strftime("%B"), thu.day, thu.year)
    for st in ("queued", "draft", "sent"):
        for c in brevo("/emailCampaigns?status=%s&limit=50&sort=desc" % st).get("campaigns", []):
            if label in (c.get("name") or ""):
                h = brevo("/emailCampaigns/%d" % c["id"]).get("htmlContent") or ""
                out = []
                for m in re.finditer(r'<div style="margin: 0 0 32px 0;">(.*?)</div>', h, re.S):
                    b = m.group(1)
                    g = lambda pat: (re.search(pat, b, re.S) or [None, ""])[1].strip()
                    store = H.unescape(g(r'<p[^>]*letter-spacing: 2px[^>]*>([A-Z ]+)</p>')).title()
                    d = {"store": store, "item": H.unescape(g(r"<h2[^>]*>(.*?)</h2>")), "pitch": H.unescape(g(r'<p style="margin: 0 0 16px 0;[^"]*">(.*?)</p>')),
                         "price": g(r'font-size: 32px[^>]*>\$([\d.,]+)</p>'), "image_url": g(r'<img src="([^"]+)"'), "captured_date": today.isoformat()}
                    if store in PHONES and d["item"] and d["price"] and d["image_url"].startswith(SITE) and not WEAPON.search(d["item"] + " " + d["pitch"]):
                        out.append(d)
                return label, out
    return label, []


def card(d):
    e = lambda s: H.escape(s, quote=True)
    tel, disp = PHONES[d["store"]]
    maps = "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+%s+VA&utm_source=website&utm_medium=retail&utm_campaign=deal_of_week&utm_content=map_%s" % (d["store"], d["store"].lower())
    return ('<div style="flex:1 1 280px;max-width:340px;border:1px solid #e5e5e5;border-radius:10px;overflow:hidden;">'
            '<img src="%s" alt="%s" style="width:100%%;height:220px;object-fit:cover;display:block;">'
            '<div style="padding:16px;">'
            '<p style="margin:0 0 6px;font-size:11px;letter-spacing:2px;color:#c97b3a;font-weight:bold;">%s</p>'
            '<h3 style="margin:0 0 8px;font-size:18px;line-height:1.3;color:#1a1a1a;">%s</h3>'
            '<p style="margin:0 0 12px;font-size:14px;color:#555;line-height:1.5;">%s</p>'
            '<p style="margin:0 0 4px;font-size:26px;font-weight:bold;color:#1a1a1a;">$%s</p>'
            '<p style="margin:0 0 14px;font-size:12px;color:#888;">While it lasts — usually one of a kind. Call to confirm it’s still here.</p>'
            '<a href="tel:%s" style="display:inline-block;margin:0 6px 8px 0;padding:10px 16px;background:#1a1a1a;color:#fff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:bold;">📞 Call %s</a>'
            '<a href="sms:%s" style="display:inline-block;margin:0 6px 8px 0;padding:10px 16px;background:#c97b3a;color:#fff;text-decoration:none;border-radius:6px;font-size:14px;font-weight:bold;">💬 Text %s</a>'
            '<a href="%s" style="display:inline-block;font-size:13px;color:#c97b3a;">📍 Get directions →</a>'
            '</div></div>') % (d["image_url"], e(d["item"]), d["store"].upper(), e(d["item"]), e(d["pitch"]), d["price"], tel, disp, tel, disp, maps)


def block(deals):
    return (START + '\n<!-- wp:html -->\n<div style="margin:0 0 40px;">'
            '<h2>This Week’s Deals — Fresh Finds Across the Valley</h2>'
            '<p>Hand-picked markdowns from our five stores. New deals drop every week — while they last.</p>'
            '<div style="display:flex;flex-wrap:wrap;gap:20px;">' + "".join(card(d) for d in deals) + '</div>'
            '<p style="margin-top:20px;font-size:14px;color:#555;">Prefer email? Our subscribers get these deals first every Thursday. '
            'Culpeper &amp; Roanoke: Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM. Harrisonburg, Waynesboro &amp; Lexington: Mon, Tue, Thu, Fri &amp; Sat 10 AM–6 PM '
            '(closed Wed &amp; Sun). What’s Right Is Right.</p></div>\n<!-- /wp:html -->\n' + END)


def main():
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    label, new = this_weeks_deals(today)
    store = json.load(open(STORE)) if os.path.exists(STORE) else []
    idx = {("%s|%s|%s" % (d["store"], d["item"], d["price"])).lower(): d for d in store}
    for d in new:
        idx[("%s|%s|%s" % (d["store"], d["item"], d["price"])).lower()] = d
    cutoff = (today - dt.timedelta(days=21)).isoformat()
    live = sorted([d for d in idx.values() if d.get("captured_date", "") >= cutoff and (d.get("image_url") or "").startswith("http")],
                  key=lambda d: d["captured_date"], reverse=True)[:10]
    print("Thursday %s: %d new deal(s); %d live after merge/prune" % (label, len(new), len(live)))
    for d in live:
        print("  %s  %s — %s — $%s" % (d["captured_date"], d["store"], d["item"], d["price"]))
    if not live:
        print("nothing to show — page left unchanged")
        return 0
    page = wp("/pages?slug=retail&context=edit&_fields=id,content,status")[0]
    raw = page["content"]["raw"]
    blk = block(live)
    if START in raw and END in raw:
        new_raw = raw[:raw.index(START)] + blk + raw[raw.index(END) + len(END):]
    else:
        new_raw = blk + "\n\n" + raw
    outside_before = raw.replace(raw[raw.index(START):raw.index(END) + len(END)], "") if START in raw else raw
    outside_after = new_raw.replace(blk, "")
    if outside_before.strip() != outside_after.strip():
        ledger("Retail page deals not refreshed — the edit would have changed content outside the deals block.")
        return 1
    if render:
        print("RENDER: page %d, block %d chars, markers now %d" % (page["id"], len(blk), new_raw.count(START)))
        return 0
    os.makedirs(BACKUP, exist_ok=True)
    open(os.path.join(BACKUP, "retail_%s.html" % dt.datetime.now().strftime("%Y%m%d-%H%M%S")), "w").write(raw)
    wp("/pages/%d" % page["id"], {"content": new_raw, "status": "publish"}, "POST")
    json.dump(live, open(STORE, "w"), indent=1)
    chk = wp("/pages/%d?context=edit&_fields=content" % page["id"])["content"]["raw"]
    try:
        code = urllib.request.urlopen(urllib.request.Request(SITE + "/retail/?v=%d" % dt.datetime.now().timestamp(), headers={"User-Agent": "Mozilla/5.0"}), timeout=30).status
    except Exception as e:
        code = getattr(e, "code", 0)
    if code != 200 or chk.count(START) != 1:
        ledger("Retail page deals were written but the live check failed (http %s, %d blocks)." % (code, chk.count(START)))
        return 1
    os.environ["VP_TASK"] = "vp-website-deals-weekly"
    vp_slack.post(CH, "Retail page deals refreshed: %d live now (%s). https://thevalleypawn.com/retail/" % (
        len(live), ", ".join("%s (%s)" % (d["item"], d["store"]) for d in live)))
    print("published + verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
