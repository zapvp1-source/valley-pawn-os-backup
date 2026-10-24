#!/usr/bin/env python3
"""chekkit_page_text.py URL [MATCH] — read-only: open a dashboard.chekkit.io page on the automation profile
(headless) and save its full text to fleet/state/review_reply/page_<slug>.txt. If MATCH is given, also click
every element whose text contains MATCH (e.g. an API docs section header) and append the text after each click."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vp_browser  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
url = sys.argv[1]
if not url.startswith("https://dashboard.chekkit.io/"):
    sys.exit("only dashboard.chekkit.io pages")
OUT = os.path.join(os.path.dirname(HERE), "fleet", "state", "review_reply"); os.makedirs(OUT, exist_ok=True)
slug = re.sub(r"[^a-z0-9]+", "_", url.split(".io/")[1].lower())[:40]
with sync_playwright() as p:
    ctx = vp_browser.launch(p, headless=True)
    try:
        pg = vp_browser.first_page(ctx)
        pg.goto(url, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(8000)
        txt = pg.locator("body").inner_text(timeout=20000)
        if len(sys.argv) > 2:
            loc = pg.get_by_text(sys.argv[2])
            for i in range(min(loc.count(), 40)):
                try:
                    loc.nth(i).click(timeout=4000); pg.wait_for_timeout(1500)
                    txt += "\n\n===== after click %d =====\n" % i + pg.locator("body").inner_text(timeout=20000)
                except Exception as e:  # noqa: BLE001
                    txt += "\n[click %d failed %s]" % (i, str(e)[:80])
        open(os.path.join(OUT, "page_%s.txt" % slug), "w").write(txt)
        print("ok", pg.url, len(txt))
    finally:
        vp_browser.close(ctx)
