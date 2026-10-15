#!/usr/bin/env python3
"""ncc_probe.py — READ-ONLY environment probe for the 2026-10-14 native cloudcover + eBay audit builds.
Prints versions, whether files exist (mtime/size only — never contents), and the eBay store NAMES
(token lengths only). Never writes, never posts, never prints a secret."""
import datetime as dt
import os
import sys

print("python", sys.version.split()[0], sys.executable)
try:
    import playwright
    from importlib.metadata import version
    print("playwright", version("playwright"))
except Exception as e:
    print("playwright MISSING", type(e).__name__)
for p in ["/Applications/Google Chrome.app", os.path.expanduser("~/Library/Application Support/valleypawn"),
          os.path.expanduser("~/Library/Application Support/valleypawn/pw-cloudcover"),
          os.path.expanduser("~/.vp_secrets/ebay_store_tokens.py"), os.path.expanduser("~/ebay_markdown_state.json"),
          os.path.expanduser("~/ebay_feedback_answered.json"), os.path.expanduser("~/ebay_weekly_rankings.py")]:
    if os.path.exists(p):
        st = os.stat(p)
        print("EXISTS", p, st.st_size, dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"))
    else:
        print("ABSENT", p)
try:
    sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
    from ebay_store_tokens import STORES, APP_ID
    print("ebay stores", [(s.get("name"), len(s.get("token") or "")) for s in STORES], "app_id_len", len(APP_ID or ""))
except Exception as e:
    print("ebay tokens import FAILED", type(e).__name__, str(e)[:120])
