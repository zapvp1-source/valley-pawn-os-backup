#!/usr/bin/env python3
"""suite_restore_draft.py <draft_id> — undo suite_fix_draft.py (Joshua 10/5: Harrisonburg's official address DOES include Suite 22)."""
import json, os, re, sys, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
def b(p, payload=None, m="GET"):
    r = urllib.request.Request("https://api.brevo.com/v3" + p, data=json.dumps(payload).encode() if payload else None, method=m,
                               headers={"api-key": K, "content-type": "application/json", "accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as x:
        d = x.read(); return json.loads(d) if d else {}
cid = int(sys.argv[1]); c = b("/emailCampaigns/%d" % cid)
if c["status"] != "draft": sys.exit("not a draft")
h2 = re.sub(r"1790 East Market Street(?!,? Suite 22)", "1790 East Market Street, Suite 22", c["htmlContent"])
b("/emailCampaigns/%d" % cid, {"htmlContent": h2}, "PUT")
print("now:", re.findall(r".{0,20}1790 East Market Street, Suite 22.{0,15}", b("/emailCampaigns/%d" % cid)["htmlContent"]))
