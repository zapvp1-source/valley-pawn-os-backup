#!/usr/bin/env python3
"""read-only-ish test: prove deal_of_week_pick.wp_upload works headless (uploads one small test image, checks 200, deletes it)."""
import base64, json, os, sys, urllib.request, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deal_of_week_pick as d
u, p = d.wp_creds(); print("creds:", bool(u))
src = os.path.expanduser("~/Documents/Claude/Projects/Refine Social Media/deal_of_week_uploads/20261005_WAY_dewaltcompressord55168.jpg")
tmp = "/tmp/dowtest/x"; os.makedirs(tmp, exist_ok=True); dst = os.path.join(tmp, "deal.jpg")
subprocess.run(["sips", "-Z", "300", "-s", "format", "jpeg", src, "--out", dst], capture_output=True)
url = d.wp_upload(dst); print("url:", url, "public:", d.public_ok(url) if url else None)
r = json.load(urllib.request.urlopen(urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2/media?search=dow_&per_page=5&_fields=id,source_url",
    headers={"Authorization": "Basic " + base64.b64encode(("%s:%s" % (u, p)).encode()).decode(), "User-Agent": "ValleyPawnOps/1.0"})))
for m in r:
    if m["source_url"] == url:
        req = urllib.request.Request("https://thevalleypawn.com/wp-json/wp/v2/media/%d?force=true" % m["id"], method="DELETE",
            headers={"Authorization": "Basic " + base64.b64encode(("%s:%s" % (u, p)).encode()).decode(), "User-Agent": "ValleyPawnOps/1.0"})
        print("cleanup", urllib.request.urlopen(req).status)
