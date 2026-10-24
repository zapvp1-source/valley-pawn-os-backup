#!/usr/bin/env python3
"""review_reply_diag.py — one-shot look at the Chekkit reviews page on the automation profile (read-only).
Saves fleet/state/review_reply/diag.png + diag.txt (url, comboboxes, buttons, first 1500 chars of body)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vp_browser  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
OUT = os.path.join(os.path.dirname(HERE), "fleet", "state", "review_reply"); os.makedirs(OUT, exist_ok=True)
JS = """() => {
 const r = {combos: [], buttons: [], selects: []};
 for (const e of document.querySelectorAll('[role=combobox],button[aria-haspopup],[aria-haspopup=listbox]')) r.combos.push([e.tagName, e.getAttribute('aria-label'), (e.innerText||'').trim().slice(0,60)]);
 for (const e of document.querySelectorAll('button')) { const t=(e.innerText||e.getAttribute('aria-label')||'').trim(); if (t) r.buttons.push(t.slice(0,50)); }
 for (const e of document.querySelectorAll('select')) r.selects.push([...e.options].map(o=>o.text).slice(0,10));
 return r; }"""
with sync_playwright() as p:
    ctx = vp_browser.launch(p, headless=True)
    try:
        pg = vp_browser.first_page(ctx)
        pg.goto("https://dashboard.chekkit.io/reviews", wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(7000)
        if "--switcher" in sys.argv:
            pg.locator("button", has_text="Valley Pawn - ").first.click(timeout=15000); pg.wait_for_timeout(2500)
            menu = pg.evaluate("""() => [...document.querySelectorAll('[role=option],[role=menuitem],[role=listbox] *,[cmdk-item],li,a')].map(e=>[e.tagName,e.getAttribute('role'),(e.innerText||'').trim().slice(0,70)]).filter(x=>/Valley Pawn/.test(x[2]))""")
            print("MENU", menu)
            print("INPUTS", pg.evaluate("() => [...document.querySelectorAll('input')].map(e=>[e.type,e.placeholder])"))
        pg.screenshot(path=os.path.join(OUT, "diag.png"), full_page=False)
        info = pg.evaluate(JS)
        body = pg.locator("body").inner_text(timeout=15000)
        with open(os.path.join(OUT, "diag.txt"), "w") as f:
            f.write("URL %s\n" % pg.url)
            f.write("COMBOS %s\nSELECTS %s\nBUTTONS %s\n" % (info["combos"], info["selects"], info["buttons"][:60]))
            f.write("BODY\n" + body[:1500])
        print("ok", pg.url)
    finally:
        vp_browser.close(ctx)
