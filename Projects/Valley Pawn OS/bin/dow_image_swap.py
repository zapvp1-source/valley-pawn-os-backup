#!/usr/bin/env python3
"""dow_image_swap.py <campaign_id> — one-off repair 2026-10-05: Publer CDN image URLs are not public (403), so
swap each deal photo in a queued Deal of the Week campaign for its WordPress media-library copy, keep the
schedule, re-run brevo_preflight v3, verify every image answers 200."""
import json, os, re, subprocess, sys, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
MAP = {"jbl": "https://thevalleypawn.com/wp-content/uploads/2026/10/email_20261005_CUL_jblpartybox120.jpg",
       "dewalt": "https://thevalleypawn.com/wp-content/uploads/2026/10/email_20261005_WAY_dewaltcompressord55168.jpg",
       "violin": "https://thevalleypawn.com/wp-content/uploads/2026/10/email_20261005_HAR_fullsizedviolin.jpg",
       "reddy": "https://thevalleypawn.com/wp-content/uploads/2026/10/email_20261005_ROA_reddyheaterpro115forceda.jpg"}
def b(path, payload=None, method="GET"):
    r = urllib.request.Request("https://api.brevo.com/v3" + path, data=json.dumps(payload).encode() if payload else None, method=method,
                               headers={"api-key": K, "content-type": "application/json", "accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as x:
        d = x.read(); return json.loads(d) if d else {}
cid = int(sys.argv[1]); c = b("/emailCampaigns/%d" % cid); h = c["htmlContent"]; at = c.get("scheduledAt")
n = 0
def rep(m):
    global n
    tag = m.group(0); alt = (re.search(r'alt="([^"]*)"', tag) or [None, ""])[1].lower()
    for k, u in MAP.items():
        if k in alt:
            n += 1; return re.sub(r'src="https://cdn\.publer\.com[^"]+"', 'src="%s"' % u, tag)
    return tag
h2 = re.sub(r'<img[^>]+src="https://cdn\.publer\.com[^"]+"[^>]*>', rep, h)
print("swapped", n, "status before", c["status"], at)
if n:
    b("/emailCampaigns/%d" % cid, {"htmlContent": h2}, "PUT")
    c2 = b("/emailCampaigns/%d" % cid)
    if c2["status"] != "queued" and at:
        b("/emailCampaigns/%d" % cid, {"scheduledAt": at}, "PUT")
p = subprocess.run(["/usr/bin/python3", os.path.expanduser("~/Documents/Claude/Projects/Email Refinement/brevo_preflight.py"), str(cid)], capture_output=True, text=True)
print("preflight rc", p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:])
c3 = b("/emailCampaigns/%d" % cid)
imgs = re.findall(r'<img[^>]+src="([^"]+)"', c3["htmlContent"])
for u in imgs:
    try: s = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status
    except Exception as e: s = getattr(e, "code", e)
    print(s, u)
print("final", c3["status"], c3.get("scheduledAt"))
