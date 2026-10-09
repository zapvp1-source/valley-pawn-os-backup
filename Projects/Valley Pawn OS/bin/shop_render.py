#!/usr/bin/env python3
"""shop_render.py — host-queue entry point for a --render of the native vp-website-shop-nightly runner
(Mac-first wave 1, 2026-10-08). Runs Website/analytics/bin/shop_refresh.py --dry-run (fetch 5 eBay stores ->
gate -> build; NO publish, NO Slack) and prints the exact #website body it would post, then the last real
body from result.json for comparison."""
import json, os, subprocess, sys
W = os.path.expanduser("~/Documents/Claude/Projects/Website/analytics")
r = subprocess.run([sys.executable, os.path.join(W, "bin", "shop_refresh.py"), "--dry-run"], capture_output=True, text=True, timeout=900)
print("=== WOULD POST C0ASE9C0GQ0 (rc=%d)\n%s" % (r.returncode, r.stdout.strip()))
try:
    res = json.load(open(os.path.join(W, "data", "shop", "result.json")))
    print("=== LAST REAL (%s %s posted=%s by %s)\n%s" % (res.get("slot"), res.get("ts"), res.get("posted"), res.get("posted_by"), res.get("slack_body")))
except Exception as e:
    print("no result.json:", e)
