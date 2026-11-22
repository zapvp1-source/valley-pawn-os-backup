#!/usr/bin/env python3
"""seasonal_campaigns.py [--render] [--offline] [--today YYYY-MM-DD]
Native daily check for the seasonal campaign calendar (Joshua 2026-11-21: "execute flawlessly throughout the year").
Source of truth: Projects/Seasonal Campaigns/campaigns.json. Spec: Seasonal Campaigns/STATUS.md, CHECK_RUNBOOK.md.

READ-ONLY toward customers. It never creates, edits, schedules, suspends or sends a Brevo campaign and never
posts to Slack. The one change it may make: publish a sale page whose WordPress publish date has passed
(WordPress "missed schedule"), content untouched.

Per campaign in its window (21 days before the email/banner, to 8 days after the last sale day):
  email    Brevo status/date/time/audience/copy          page     WordPress page live + copy
  banner   homepage scheduler block still present         briefs   social brief still in the calendar file
  social   sale-week plan mentions the sale (soft check)  results  one file 8 days after the sale
Writes: Seasonal Campaigns/RUN_LOG.md, results/<id>.md, and one deduped row in Life OS/HUMAN_QUEUE.md per failure.
--render prints what it would write and changes nothing. Exit 0 always (failures are rows, not crashes)."""
import base64, datetime as dt, glob, json, os, re, sys, urllib.request, urllib.error
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
PROJ = os.path.expanduser("~/Documents/Claude/Projects")
SC = os.path.join(PROJ, "Seasonal Campaigns")
SOCIAL = os.path.join(PROJ, "Refine Social Media")
HQ = os.path.join(PROJ, "Life OS", "HUMAN_QUEUE.md")
WP_CREDS = os.path.join(PROJ, "Website", "shop-build", ".wp_app_credentials")
RENDER = "--render" in sys.argv
OFFLINE = "--offline" in sys.argv
MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def today():
    if "--today" in sys.argv:
        return dt.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    return dt.datetime.now(ET).date()


def d(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def label(day):
    return "%s %d" % (MON[day.month], day.day)


def http(url, headers=None, payload=None, method=None):
    h = {"User-Agent": "Mozilla/5.0 (vp-seasonal-check)", "accept": "application/json"}
    h.update(headers or {})
    data = json.dumps(payload).encode() if payload is not None else None
    if data:
        h["content-type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=h, method=method or ("POST" if data else "GET"))
    with urllib.request.urlopen(r, timeout=60) as x:
        body = x.read()
    return json.loads(body) if body else {}


def brevo(path):
    k = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
    return http("https://api.brevo.com/v3" + path, {"api-key": k})


def wp_auth():
    kv = {}
    for line in open(WP_CREDS):
        if "=" in line:
            a, b = line.split("=", 1)
            kv[a.strip()] = b.strip().strip('"')
    tok = base64.b64encode(("%s:%s" % (kv["WP_USER"], kv["WP_APP_PASSWORD"])).encode()).decode()
    return {"Authorization": "Basic " + tok}


def wp(path, payload=None, method=None):
    return http("https://thevalleypawn.com/wp-json/wp/v2" + path, wp_auth(), payload, method)


def check_email(c, t, out):
    e = c.get("email") or {}
    cid, send = e.get("brevo_campaign"), d(e.get("send"))
    if not cid or not send:
        return None
    weekly = (cid == 70)
    if weekly and t <= send:
        out.append(("email", "SKIP", "weekly-chain draft #70, checked after its date"))
        return None
    try:
        b = brevo("/emailCampaigns/%d" % cid)
    except Exception as x:  # noqa: BLE001
        out.append(("email", "FAIL", "could not read Brevo campaign #%s (%s)" % (cid, str(x)[:80])))
        return None
    st = b.get("status")
    lists = [(l.get("id") if isinstance(l, dict) else l) for l in ((b.get("recipients") or {}).get("lists") or [])]
    html = b.get("htmlContent") or ""
    probs = []
    if t <= send and st != "sent":
        if st != "queued":
            probs.append("is '%s', not scheduled" % st)
        sa = b.get("scheduledAt")
        if sa:
            when = dt.datetime.fromisoformat(sa.replace("Z", "+00:00")).astimezone(ET)
            if when.date() != send or when.hour != 10:
                probs.append("is set for %s, plan says %s 10:00 AM" % (when.strftime("%b %d %I:%M %p"), send.strftime("%b %d")))
        elif st == "queued":
            probs.append("has no send time")
    elif t > send and st not in ("sent", "in_process"):
        probs.append("did not send on %s (status '%s')" % (send.strftime("%b %d"), st))
    if not weekly:
        if 3 not in lists:
            probs.append("is not addressed to the full customer list")
        if c.get("kind") == "sale":
            if "Some exclusions apply" not in html:
                probs.append("is missing 'Some exclusions apply'")
            for sd in c.get("sale_days") or []:
                if d(sd) and label(d(sd)) not in html:
                    probs.append("does not mention %s" % label(d(sd)))
    if probs:
        out.append(("email", "FAIL", "Email #%s %s" % (cid, "; ".join(probs))))
    else:
        out.append(("email", "PASS", "#%s %s" % (cid, "sent" if st == "sent" else "scheduled %s 10:00 AM" % send.strftime("%b %d"))))
    return b


def check_page(c, t, out):
    w = c.get("website") or {}
    pid, bf = w.get("page_id"), d(w.get("banner_from"))
    if not pid or not bf or t < bf:
        return
    try:
        p = wp("/pages/%d?context=edit&_fields=status,link,content" % pid)
    except Exception as x:  # noqa: BLE001
        out.append(("page", "FAIL", "could not read website page %s (%s)" % (w.get("landing"), str(x)[:80])))
        return
    st = p.get("status")
    raw = ((p.get("content") or {}).get("raw")) or ""
    if st == "future":
        if RENDER:
            out.append(("page", "FAIL", "%s is still waiting to publish (would publish it)" % w.get("landing")))
            return
        try:
            wp("/pages/%d" % pid, {"status": "publish"}, "POST")
            st = "publish"
            out.append(("page", "FIXED", "%s had not published on its date; published it" % w.get("landing")))
        except Exception as x:  # noqa: BLE001
            out.append(("page", "FAIL", "%s did not publish and could not be published (%s)" % (w.get("landing"), str(x)[:80])))
            return
    if st != "publish":
        out.append(("page", "FAIL", "Website page %s is '%s', not live" % (w.get("landing"), st)))
        return
    probs = []
    if c.get("kind") == "sale":
        if "Some exclusions apply" not in raw:
            probs.append("is missing 'Some exclusions apply'")
        for sd in c.get("sale_days") or []:
            if d(sd) and label(d(sd)) not in raw:
                probs.append("does not mention %s" % label(d(sd)))
    if probs:
        out.append(("page", "FAIL", "Website page %s %s" % (w.get("landing"), "; ".join(probs))))
    elif not any(o[0] == "page" for o in out):
        out.append(("page", "PASS", "%s live" % w.get("landing")))


def check_banner(c, t, out, cache):
    w = c.get("website") or {}
    bf, bt = d(w.get("banner_from")), d(w.get("banner_to"))
    if not bf or not bt or t > bt:
        return
    if "home" not in cache:
        try:
            cache["home"] = ((wp("/pages/7?context=edit&_fields=content").get("content") or {}).get("raw")) or ""
        except Exception as x:  # noqa: BLE001
            cache["home"] = "ERR " + str(x)[:80]
    h = cache["home"]
    if h.startswith("ERR "):
        out.append(("banner", "FAIL", "could not read the homepage (%s)" % h[4:]))
    elif "VP-CAMPAIGN-BANNER-START" not in h or 'id="vp-camp"' not in h:
        out.append(("banner", "FAIL", "The homepage campaign banner block is gone"))
    elif '["%s","%s"' % (bf.isoformat(), bt.isoformat()) not in h:
        out.append(("banner", "FAIL", "The homepage banner has no entry for %s to %s" % (bf.isoformat(), bt.isoformat())))
    else:
        out.append(("banner", "PASS", "homepage banner set for %s to %s" % (label(bf), label(bt))))


def check_briefs(c, t, out):
    f = os.path.join(SOCIAL, "CALENDAR_AUG_DEC_2026.md")
    try:
        s = open(f).read()
    except OSError:
        out.append(("briefs", "FAIL", "The social calendar file is missing"))
        return
    m = re.search(r"CAMPAIGN-BRIEFS:BEGIN.*?CAMPAIGN-BRIEFS:END", s, re.S)
    if not m or ("**%s**" % c["name"]) not in m.group(0):
        out.append(("briefs", "FAIL", "The social brief for %s is missing from the calendar the weekly build reads" % c["name"]))
    else:
        out.append(("briefs", "PASS", "social brief present"))


def check_social(c, t, out):
    days = [d(x) for x in (c.get("sale_days") or []) if d(x)]
    if c.get("kind") != "sale" or not days:
        return
    monday = days[0] - dt.timedelta(days=days[0].weekday())
    if t < monday + dt.timedelta(days=1) or t > days[-1]:
        return  # the week's plan is built Monday afternoon; look from Tuesday through the sale
    f = os.path.join(SOCIAL, "state", "plans", "plan_%s.json" % monday.isoformat())
    if not os.path.exists(f):
        out.append(("social", "FAIL", "No social plan was built for the week of %s" % label(monday)))
        return
    s = open(f, errors="replace").read()
    slug = ((c.get("website") or {}).get("landing") or "").strip("/")
    hits = len(re.findall(r"15% off|15 percent off", s, re.I)) + (s.count(slug) if slug else 0)
    if hits == 0:
        out.append(("social", "FAIL", "This week's social and Google profile posts do not mention the %s (15%% off %s and %s)" % (c["name"], label(days[0]), label(days[-1]))))
    else:
        out.append(("social", "PASS", "%d mentions in the week's plan" % hits))


def write_results(c, t, b, out):
    days = [d(x) for x in (c.get("sale_days") or []) if d(x)]
    end = days[-1] if days else d((c.get("website") or {}).get("banner_to"))
    if not end or t < end + dt.timedelta(days=8) or not b:
        return
    path = os.path.join(SC, "results", c["id"] + ".md")
    if os.path.exists(path):
        return
    g = ((b.get("statistics") or {}).get("globalStats")) or {}
    lines = ["# %s — results" % c["name"], "", "Written %s by seasonal_campaigns.py." % t.isoformat(), "",
             "- Email #%s: delivered %s, unique opens %s, unique clicks %s, unsubscribes %s" % (
                 b.get("id"), g.get("delivered"), g.get("uniqueViews"), g.get("uniqueClicks"), g.get("unsubscriptions")),
             "- Checks in the final run: " + ", ".join("%s %s" % (o[0], o[1]) for o in out),
             "- Store sales comparison: not included yet (needs the Bravo sales pull wired in)."]
    if RENDER:
        print("WOULD WRITE", path)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write("\n".join(lines) + "\n")
    out.append(("results", "DONE", "results file written"))


def queue_row(t, cid, item, text):
    key = "[SEASONAL:%s:%s]" % (cid, item)
    try:
        s = open(HQ).read()
    except OSError:
        return
    if key in s:
        return
    row = "| %s | %s **%s (~2 min).** Details: Projects/Seasonal Campaigns/RUN_LOG.md. | Seasonal campaigns | %s | OPEN |" % (
        t.isoformat(), key, text, t.isoformat())
    L = s.split("\n")
    i = next((k for k, x in enumerate(L) if x.startswith("|---")), None)
    if i is None:
        return
    L.insert(i + 1, row)
    if RENDER:
        print("WOULD QUEUE", row)
    else:
        open(HQ, "w").write("\n".join(L))


def main():
    t = today()
    data = json.load(open(os.path.join(SC, "campaigns.json")))
    log = ["", "## %s %s(native check)" % (t.isoformat(), "RENDER " if RENDER else "")]
    cache, n = {}, 0
    for c in data.get("campaigns", []):
        e, w = c.get("email") or {}, c.get("website") or {}
        days = [d(x) for x in (c.get("sale_days") or []) if d(x)]
        start = min([x for x in (d(e.get("send")), d(w.get("banner_from"))) if x] or [None]) if (d(e.get("send")) or d(w.get("banner_from"))) else None
        end = days[-1] if days else d(w.get("banner_to"))
        if not start or not end or not (start - dt.timedelta(days=21) <= t <= end + dt.timedelta(days=8)):
            continue
        n += 1
        out, b = [], None
        if not OFFLINE:
            b = check_email(c, t, out)
            check_page(c, t, out)
            check_banner(c, t, out, cache)
        check_briefs(c, t, out)
        check_social(c, t, out)
        if not OFFLINE:
            write_results(c, t, b, out)
        for item, res, text in out:
            log.append("- %s %s: %s — %s" % (c["id"], item.upper(), res, text))
            if res == "FAIL":
                queue_row(t, c["id"], item, "%s: %s" % (c["name"], text))
    if n == 0:
        log.append("- nothing in window")
    body = "\n".join(log) + "\n"
    if RENDER:
        print(body)
    else:
        with open(os.path.join(SC, "RUN_LOG.md"), "a") as f:
            f.write(body)
        print(body)


if __name__ == "__main__":
    try:
        main()
    except Exception as x:  # noqa: BLE001
        print("seasonal_campaigns: unexpected error:", repr(x))
    sys.exit(0)
