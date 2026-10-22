#!/usr/bin/env python3
"""giveaway_pause.py [--apply] — pause the $100/month giveaway on thevalleypawn.com (Joshua 2026-10-21: "pause").
Follow pages 748-753: removes the "WIN $100 EVERY MONTH" block and the Brevo giveaway-entry form iframe
(page stays live; follow links unchanged). Rules page 832: adds a dated "paused" notice at the top (URL kept so
printed QR signs never 404). Backs up raw content to Website/giveaway_pause_backup_<date>/ first.
Without --apply: prints what would change."""
import base64, datetime as dt, json, os, re, sys, urllib.request
P = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects"))
kv = dict(l.strip().split("=", 1) for l in open(P + "/Website/shop-build/.wp_app_credentials") if "=" in l)
A = "Basic " + base64.b64encode(("%s:%s" % (kv["WP_USER"].strip().strip('"'), kv["WP_APP_PASSWORD"].strip().strip('"'))).encode()).decode()
def wp(method, path, payload=None):
    r = urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2" + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": A, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    with urllib.request.urlopen(r, timeout=60) as x:
        return json.load(x)
apply = "--apply" in sys.argv
bk = P + "/Website/giveaway_pause_backup_%s" % dt.date.today().isoformat(); os.makedirs(bk, exist_ok=True)
NOTICE = ('<div style="background:#FFF4D6;border:1px solid #B08A3E;border-radius:8px;padding:14px 16px;margin:0 0 20px;">'
          '<strong>This promotion is paused.</strong> As of October 21, 2026, the Valley Pawn &#8220;$100 Every Month&#8221; '
          'giveaway is not accepting new entries. The rules below are kept for reference.</div>\n')
for pid in (748, 749, 750, 751, 752, 753, 832):
    d = wp("GET", "/pages/%d?context=edit&_fields=id,slug,content" % pid)
    raw = d["content"]["raw"]
    json.dump(d, open("%s/page_%d.json" % (bk, pid), "w"))
    if pid == 832:
        new = raw if "This promotion is paused" in raw else NOTICE + raw
    else:
        new = re.sub(r'\s*<div class="vp-giveaway">.*?</div>\s*</div>', "\n", raw, flags=re.S)
        new = re.sub(r'\s*<iframe[^>]*sibforms\.com[^>]*>\s*</iframe>', "\n", new, flags=re.S)
    changed = new != raw
    print(pid, d["slug"], "CHANGE" if changed else "no change", len(raw), "->", len(new),
          "| giveaway mentions left:", new.lower().count("giveaway") - (new.count("This promotion is paused") * 1 if pid == 832 else 0))
    if apply and changed:
        out = wp("POST", "/pages/%d" % pid, {"content": new})
        print("   saved", out.get("id"), out.get("modified"))
