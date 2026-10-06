#!/usr/bin/env python3
"""gold_silver_monthly.py [--render] [--month YYYY-MM] [--at ISO8601] — native "We Buy Gold & Silver" email.

Native replacement (2026-10-05) for the Cowork task `monthly-we-buy-gold-silver-email`, which died with the
Mac connector on 9/17 and never sent October. Steps are the SKILL's, byte for byte where it gave code:
  1 duplicate VP Master Template 11, fill its 10 markers (never hand-built HTML)
  2 create the campaign as a DRAFT to lists [3, 10] (customers + Internal Seeds — mandatory), sender id 1
  3 PREFLIGHT: the SKILL's gate (5 Call + 5 Text buttons, >=10 utm_content, no legal-name leak, seeds on)
    AND Email Refinement/brevo_preflight.py v3 (auto-fix + hard-fail rules). Both must pass or nothing sends.
  4 send now (or schedule with --at)
  5 post the launch card to #email-campaigns (C0APR5WUL2Z) as the ops bot
Duplicate guard: a SENT or QUEUED campaign already named for this month = do nothing.
--render: build + print what would happen; creates nothing.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "monthly-we-buy-gold-silver-email"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
PREFLIGHT = os.path.expanduser("~/Documents/Claude/Projects/Email Refinement/brevo_preflight.py")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
DRY = os.path.join(OS_DIR, "fleet", "DRY_RUN.json")
CH = "C0APR5WUL2Z"
API = "https://api.brevo.com/v3"
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
STORES = ["culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"]
SUBJECT = "\U0001F4B0 Turn Your Gold & Silver Into Cash — Fair, Same-Day Offers"
BODY = """<h2 style="margin:0 0 14px 0;color:#2D1A5E;font-size:22px;line-height:1.3;font-weight:800;">Your gold and silver are worth more than a drawer</h2>
<p style="margin:0 0 16px 0;color:#333333;font-size:16px;line-height:1.6;">That broken chain, the mismatched earrings, the coins you inherited &mdash; they hold real value, and precious-metal prices are strong right now. Bring them into any Valley Pawn and we&rsquo;ll weigh, test, and appraise everything right in front of you, then make a fair, transparent offer on the spot.</p>
<h3 style="margin:0 0 10px 0;color:#2D1A5E;font-size:17px;line-height:1.3;font-weight:800;">What we buy</h3>
<ul style="margin:0 0 18px 0;padding-left:20px;color:#333333;font-size:16px;line-height:1.6;">
<li>Gold jewelry &mdash; any karat, broken or whole</li><li>Silver jewelry, flatware, and sterling</li>
<li>Gold &amp; silver coins, bars, and bullion</li><li>Scrap gold, dental gold, and odds and ends</li></ul>
<p style="margin:0 0 16px 0;color:#333333;font-size:16px;line-height:1.6;">No credit check, no pressure, no obligation. If our number doesn&rsquo;t work for you, you keep your items and walk right back out. Everything we do is backed by the promise we&rsquo;ve stood on since 2014: <strong style="color:#2D1A5E;">What&rsquo;s Right Is Right.</strong></p>
<p style="margin:0 0 4px 0;color:#333333;font-size:16px;line-height:1.6;">Not sure what you&rsquo;ve got? Call or text your nearest store below &mdash; we&rsquo;re happy to talk it through before you come in.</p>"""


def api(path, payload=None, method=None):
    req = urllib.request.Request(API + path, data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"api-key": K, "accept": "application/json", "content-type": "application/json"},
                                 method=method or ("POST" if payload is not None else "GET"))
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        return json.loads(body) if body else {}


def ledger(sentence):
    with open(LEDGER, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def main():
    render = "--render" in sys.argv
    today = dt.datetime.now(ET).date()
    ym = arg("--month") or today.strftime("%Y-%m")
    first = dt.date.fromisoformat(ym + "-01")
    monthname = first.strftime("%B %Y")
    name = "Valley Pawn — We Buy Gold & Silver (%s) [Master 11]" % monthname

    # duplicate guard: already sent / queued this month
    for st in ("sent", "queued", "inProcess"):
        for c in api("/emailCampaigns?status=%s&limit=50&sort=desc" % st).get("campaigns", []):
            if c.get("name") == name:
                print("already %s: #%s %s" % (st, c["id"], name))
                return 0

    tpl = api("/smtp/templates/11")
    html = tpl["htmlContent"]
    repl = {"[[SUBJECT_FALLBACK]]": SUBJECT, "[[CAMPAIGN_SLUG]]": "monthly_gold_silver_%s" % ym,
            "[[HERO_EYEBROW]]": "WE BUY GOLD &amp; SILVER", "[[HERO_HEADLINE]]": "Turn your gold &amp; silver into cash",
            "[[HERO_SUBLINE]]": "Prices are strong right now &mdash; bring in what you&rsquo;re not wearing and walk out with a fair, same-day offer.",
            "[[BODY_HTML]]": BODY, "[[PRIMARY_CTA_LABEL]]": "Get a free appraisal", "[[PRIMARY_CTA_URL]]": "https://thevalleypawn.com",
            "[[PRIMARY_CTA_SUB]]": "Walk in any time &mdash; no appointment, no obligation."}
    for k, v in repl.items():
        html = html.replace(k, v)
    # [[PRIMARY_CTA_SEP]] (added to Master 11 after the SKILL was written): "?" or "&" depending on whether
    # the URL in front of it already has a query string — the same rule brevo_preflight.py auto-fixes with.
    html = re.sub(r'href="([^"\[]*)\[\[PRIMARY_CTA_SEP\]\]',
                  lambda m: 'href="%s%s' % (m.group(1), "&" if "?" in m.group(1) else "?"), html)
    left = re.findall(r"\[\[[A-Z_]+\]\]", re.sub(r"<!--.*?-->", "", html, flags=re.S))  # comments are instructions, not content
    if left:
        ledger("Gold & Silver email for %s not built — Master Template 11 has markers this build does not fill (%s)." % (monthname, ", ".join(left)))
        return 1
    if render:
        ca = sum(("/c/%s" % s) in html for s in STORES); tx = sum(("/t/%s" % s) in html for s in STORES)
        print("RENDER: %s | %d bytes | c%d/t%d/utm%d | subject %s" % (name, len(html), ca, tx, html.count("utm_content"), SUBJECT))
        return 0

    # reuse an existing DRAFT of the same name (an earlier failed run) rather than piling up drafts
    cid = None
    for c in api("/emailCampaigns?status=draft&limit=50&sort=desc").get("campaigns", []):
        if c.get("name") == name:
            cid = c["id"]
            api("/emailCampaigns/%d" % cid, {"subject": SUBJECT, "htmlContent": html, "recipients": {"listIds": [3, 10]}}, "PUT")
    if cid is None:
        cid = api("/emailCampaigns", {"name": name, "subject": SUBJECT, "sender": {"id": 1}, "htmlContent": html,
                                       "recipients": {"listIds": [3, 10]}, "inlineImageActivation": False})["id"]

    # PREFLIGHT 1 — the SKILL's gate
    c = api("/emailCampaigns/%d" % cid)
    h = c.get("htmlContent") or ""
    ca = sum(("/c/%s" % s) in h for s in STORES); tx = sum(("/t/%s" % s) in h for s in STORES); u = h.count("utm_content")
    lists = [l["id"] if isinstance(l, dict) else l for l in (c.get("recipients", {}).get("lists") or [])]
    ok1 = ca == 5 and tx == 5 and u >= 10 and "Full Circle" not in h and 10 in lists
    # PREFLIGHT 2 — brevo_preflight.py v3
    p = subprocess.run(["/usr/bin/python3", PREFLIGHT, str(cid)], capture_output=True, text=True, timeout=300)
    ok2 = p.returncode == 0
    print("PREFLIGHT gate=%s (c%d/t%d/utm%d/seeds%s) v3=%s" % ("PASS" if ok1 else "FAIL", ca, tx, u, "Y" if 10 in lists else "N", "PASS" if ok2 else "FAIL"))
    if not (ok1 and ok2):
        tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
        print("\n".join(tail))
        ledger("Gold & Silver email for %s did not send — the pre-send check failed; draft #%d left for a rebuild." % (monthname, cid))
        vp_slack.post(CH, ":rotating_light: Monthly Gold & Silver did NOT send — preflight failed (c%d/t%d/utm%d). Draft #%d left for a rebuild from Master Template 11." % (ca, tx, u, cid))
        return 1

    if os.path.exists(DRY) and json.load(open(DRY)).get("active"):
        print("publish guard armed — draft #%d ready, not sent" % cid)
        return 0

    at = arg("--at")
    if at:
        api("/emailCampaigns/%d" % cid, {"scheduledAt": at}, "PUT")
        when = "Scheduled " + dt.datetime.fromisoformat(at).astimezone(ET).strftime("%a %b %-d, %-I:%M %p ET")
    else:
        api("/emailCampaigns/%d/sendNow" % cid, {}, "POST")
        when = "Sent " + dt.datetime.now(ET).strftime("%a %b %-d, %-I:%M %p ET")
    try:
        lst3 = api("/contacts/lists/3"); lst10 = api("/contacts/lists/10")
        count = "{:,}".format(int(lst3.get("uniqueSubscribers") or lst3.get("totalSubscribers") or 0) + int(lst10.get("uniqueSubscribers") or lst10.get("totalSubscribers") or 0))
    except Exception:
        count = "Valley Pawn Customers list"
    os.environ["VP_TASK"] = AGENT
    vp_slack.post(CH, ":moneybag: *Monthly Gold & Silver Campaign Launched*\n*Subject:* %s\n*Recipients:* %s (Valley Pawn Customers + Internal Seeds)\n"
                      "*Built from:* VP Master Template 11 — full Call/Text + UTM instrumentation, preflight PASSED\n*%s*" % (SUBJECT, count, when))
    print("campaign #%d — %s" % (cid, when))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        ledger("Gold & Silver email did not complete — Brevo refused a request (%s)." % e.code)
        print("HTTP", e.code, e.read().decode()[:400])
        sys.exit(1)
