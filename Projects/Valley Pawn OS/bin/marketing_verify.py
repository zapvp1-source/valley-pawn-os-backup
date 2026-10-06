#!/usr/bin/env python3
"""marketing_verify.py — READ-ONLY independent check of the 10/5 marketing builds (source of record, not run logs).
Brevo: campaigns 79 + 58 status/schedule/instrumentation, every <img> in them answers HTTP 200.
Publer: scheduled posts for the coming 7 days by account. Slack: #deal-of-the-week confirmation present."""
import collections, datetime as dt, json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_publer, vp_slack
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
def bget(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.brevo.com/v3" + p, headers={"api-key": K}), timeout=60))
def head(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status
    except Exception as e:
        return getattr(e, "code", str(e)[:40])
for cid in (79, 58):
    c = bget("/emailCampaigns/%d" % cid)
    h = c.get("htmlContent") or ""
    S = ["culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"]
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', h)
    bad = [(u, head(u)) for u in imgs if head(u) != 200]
    lists = [l["id"] if isinstance(l, dict) else l for l in (c.get("recipients", {}).get("lists") or [])]
    print("#%d %s | status=%s at=%s | lists=%s | call=%d text=%d utm=%d | deal blocks=%d | placeholder=%s | [[markers]]=%d | imgs=%d bad=%s | subject=%s" % (
        cid, c["name"], c["status"], c.get("scheduledAt"), lists, sum(("/c/%s" % s) in h for s in S), sum(("/t/%s" % s) in h for s in S),
        h.count("utm_content"), h.count("deal_of_week_"), "POPULATED MONDAY" in h, len(re.findall(r"\[\[[A-Z_]+\]\]", re.sub(r"<!--.*?-->", "", h, flags=re.S))),
        len(imgs), bad, c.get("subject")))
now = dt.datetime.now(dt.timezone.utc)
r = vp_publer.call("GET", "/posts", params={"state": "scheduled", "from": now.date().isoformat(), "to": (now + dt.timedelta(days=8)).date().isoformat(), "limit": "200"})
posts = r.get("posts", []) if isinstance(r, dict) else r
acc = {a["publer_id"]: k for k, a in vp_publer.accounts().items()}
by = collections.Counter(acc.get(p.get("account_id"), p.get("account_type")) for p in posts)
print("publer scheduled next 8 days: %d" % len(posts), dict(sorted(by.items())))
days = collections.Counter((p.get("scheduled_at") or "")[:10] for p in posts)
print("by day:", dict(sorted(days.items())))
noimg = [p for p in posts if p.get("type") in ("photo", "video") and not p.get("media")]
print("photo/video posts missing media:", len(noimg))
m = vp_slack.call("conversations.history", params={"channel": "C0AVCANK7E3", "limit": "10"}).get("messages", [])
print("deal channel confirmation:", any("This week's email features" in (x.get("text") or "") for x in m))
