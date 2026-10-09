#!/usr/bin/env python3
"""w1_probe.py — READ-ONLY probe for the Mac-first wave-1 builds (2026-10-08). Prints shapes/counts only,
never customer names or phone numbers. (1) candidate Chekkit review endpoints (GET), (2) leaderboard keys,
(3) Apple Mail Envelope Index: counts of Chekkit notification emails (review / unanswered) per day."""
import datetime as dt, glob, json, os, sqlite3, sys, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chekkit_api as ck

def shape(v, d=0):
    if isinstance(v, dict):
        return "{" + ", ".join("%s:%s" % (k, shape(x, d + 1) if d < 2 else type(x).__name__) for k, x in list(v.items())[:25]) + "}"
    if isinstance(v, list):
        return "[%d x %s]" % (len(v), shape(v[0], d + 1) if v else "-")
    return type(v).__name__

for path in ["/v1/reviews", "/v1/reviews?limit=5", "/v1/location", "/v1/locations", "/v1/review-invitations", "/v1/feedback"]:
    try:
        b = ck.get("CUL", path, retries=0)
        print("GET", path, "OK", shape(b)[:900])
    except urllib.error.HTTPError as e:
        print("GET", path, "HTTP", e.code)
    except Exception as e:
        print("GET", path, "ERR", type(e).__name__)
t = dt.date.today()
b = ck.get("CUL", "/v1/leaderboard?from=%s&to=%s" % (t - dt.timedelta(days=2), t))
print("leaderboard", shape(b)[:900])
b = ck.get("CUL", "/v1/conversations")
print("conversations", shape(b)[:900])
c0 = (b.get("conversations") or [{}])[0]
ms = ck.messages("CUL", c0.get("id"))
print("messages", shape({"m": ms})[:600])
from collections import Counter
print("message sender/keys", Counter(m.get("sender") for m in ms), sorted({k for m in ms for k in m}))

envs = glob.glob(os.path.expanduser("~/Library/Mail/V*/MailData/Envelope Index"))
print("envelope index:", len(envs))
if envs:
    c = sqlite3.connect("file:%s?mode=ro" % envs[0].replace(" ", "%20"), uri=True)
    cut = int((dt.datetime.now() - dt.timedelta(days=16)).timestamp())
    rows = list(c.execute("select s.subject, m.date_received, coalesce(m.global_message_id, m.message_id, m.ROWID) from messages m "
                          "left join subjects s on s.ROWID=m.subject left join addresses a on a.ROWID=m.sender "
                          "where lower(a.address) like '%chekkit%' and m.date_received >= ?", (cut,)))
    seen = set(); cnt = Counter()
    for s, ts, g in rows:
        if g in seen: continue
        seen.add(g)
        kind = "review" if "new review" in (s or "").lower() else ("unanswered" if "unanswered" in (s or "").lower() else "other")
        cnt[(dt.datetime.fromtimestamp(ts).strftime("%m-%d"), kind)] += 1
    for k in sorted(cnt): print("mail", k, cnt[k])
