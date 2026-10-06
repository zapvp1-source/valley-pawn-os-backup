#!/usr/bin/env python3
"""suite_fix_draft.py <draft_id> — remove the non-existent Harrisonburg 'Suite/Ste 22' from a Brevo DRAFT (refuses non-drafts)."""
import json, os, re, sys, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
def b(p, payload=None, m="GET"):
    r = urllib.request.Request("https://api.brevo.com/v3" + p, data=json.dumps(payload).encode() if payload else None, method=m,
                               headers={"api-key": K, "content-type": "application/json", "accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as x:
        d = x.read(); return json.loads(d) if d else {}
cid = int(sys.argv[1]); c = b("/emailCampaigns/%d" % cid)
if c["status"] != "draft": sys.exit("not a draft")
h = c["htmlContent"]
for m in re.finditer(r".{0,60}(Suite|Ste\.?)\s*22.{0,20}", h): print("before:", m.group(0))
h2 = re.sub(r",?\s*(Suite|Ste\.?)\s*22\b", "", h)
b("/emailCampaigns/%d" % cid, {"htmlContent": h2}, "PUT")
left = len(re.findall(r"(Suite|Ste\.?)\s*22", b("/emailCampaigns/%d" % cid)["htmlContent"]))
print("remaining:", left)
