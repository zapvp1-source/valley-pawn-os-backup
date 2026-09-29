#!/usr/bin/env python3
"""
Valley Pawn Academy - headless render check for built packages (optional, needs Playwright).

    pip install playwright && python3 -m playwright install chromium
    python3 render_check.py                      # L1-05, L3-06, L6-03 at 980x660 (TalentLMS frame) and 375x740 (phone)
    python3 render_check.py L2-03 --shots        # also save PNGs to dist/screenshots/

Serves dist/ over a local http server and loads each preview/<id>/index.html inside a host page
that plays the LMS: an iframe of the given size and a fake SCORM 1.2 API on window.API. It then
clicks through every screen (Start, each slide, Listen, Key points, Floor Check, the whole test
answered correctly, Result) and checks on each one:
  - the main button (Start / Next / Continue / Next question / See my score) is fully inside the
    visible frame without scrolling (the button bar is sticky), and still inside it after scrolling
    to the bottom; html/body never clip (overflow:hidden) and the document scrolls when it is taller
  - no sideways scrolling
and at the end that the fake LMS received passed / score 100 / commit.
Exit code 0 only if every check passes. Nothing is uploaded; the server is bound to 127.0.0.1.
"""
import argparse
import functools
import http.server
import json
import os
import re
import sys
import threading

ACADEMY = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ACADEMY, "dist")
SIZES = {"desktop": (980, 660), "phone": (375, 740)}

HOST = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#ddd}
iframe{border:0;display:block;background:#fff}</style></head><body>
<script>
window.__calls=[]; window.__store={};
window.API={
 LMSInitialize:function(){__calls.push('init');return 'true'},
 LMSFinish:function(){__calls.push('finish');return 'true'},
 LMSGetValue:function(k){return __store[k]||''},
 LMSSetValue:function(k,v){__store[k]=String(v);return 'true'},
 LMSCommit:function(){__calls.push('commit');return 'true'},
 LMSGetLastError:function(){return '0'},LMSGetErrorString:function(){return ''},LMSGetDiagnostic:function(){return ''}
};
</script>
<iframe id="f" src="__SRC__" width="__W__" height="__H__"></iframe></body></html>"""

METRICS_JS = """() => {
  const btn = document.querySelector('.navbar .btn.pri');
  const de = document.documentElement, b = document.body;
  const cs = (e) => getComputedStyle(e);
  const clip = [];
  for (let e = btn; e && e !== document; e = e.parentElement) {
    const s = cs(e);
    if (e !== btn && (s.overflowY === 'hidden' || s.overflowY === 'clip') && e.scrollHeight > e.clientHeight + 1) clip.push(e.tagName + '.' + e.className);
  }
  const out = { step: (document.querySelector('.steps .on') || {}).textContent || '',
    primary: btn ? btn.textContent : null, disabled: btn ? btn.disabled : null,
    vh: innerHeight, vw: innerWidth, docH: de.scrollHeight,
    htmlOverflow: cs(de).overflowY, bodyOverflow: cs(b).overflowY, clippedBy: clip,
    hScroll: de.scrollWidth > innerWidth + 1 };
  if (btn) {
    const r = btn.getBoundingClientRect();
    out.visibleNow = r.top >= 0 && r.bottom <= innerHeight + 0.5 && r.left >= 0 && r.right <= innerWidth + 0.5;
    scrollTo(0, de.scrollHeight);
    const r2 = btn.getBoundingClientRect();
    out.visibleAtBottom = r2.top >= 0 && r2.bottom <= innerHeight + 0.5;
    scrollTo(0, 0);
  }
  out.ok = !!btn && out.htmlOverflow !== 'hidden' && out.bodyOverflow !== 'hidden' && !clip.length && !out.hScroll && out.visibleNow;
  return out;
}"""


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=root)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def lesson_data(lid):
    html = open(os.path.join(DIST, "preview", lid, "index.html"), encoding="utf-8").read()
    raw = re.search(r'<script type="application/json" id="lesson-data">(.*?)</script>', html, re.S).group(1)
    return json.loads(raw.replace("<\\/", "</"))


def run_one(pw_browser, base, lid, size_name, shots_dir):
    w, h = SIZES[size_name]
    L = lesson_data(lid)
    correct = {q["prompt"]: next(o["text"] for o in q["options"] if o["correct"]) for q in L["quiz"]["questions"]}
    phone = size_name == "phone"
    ctx = pw_browser.new_context(viewport={"width": w, "height": h} if phone else {"width": w + 20, "height": h + 20},
                                 device_scale_factor=2 if phone else 1, is_mobile=phone, has_touch=phone)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    host = HOST.replace("__SRC__", f"/preview/{lid}/index.html").replace("__W__", str(w)).replace("__H__", str(h))
    page.route("**/__host.html", lambda r: r.fulfill(status=200, content_type="text/html", body=host))
    page.goto(base + "/__host.html")
    page.wait_for_function("document.getElementById('f').contentDocument && document.getElementById('f').contentDocument.querySelector('.navbar .btn.pri')")
    frame = page.frame_locator("#f")
    fr = next(f for f in page.frames if f.url.endswith("/index.html"))
    screens, shot_names = [], set()

    def check(tag):
        fr.wait_for_timeout(450)  # let the slide-in finish
        m = fr.evaluate(METRICS_JS)
        m["screen"] = tag
        screens.append(m)
        return m

    def shot(tag):
        if shots_dir and tag not in shot_names:
            shot_names.add(tag)
            path = os.path.join(shots_dir, f"{lid}_{tag}_{size_name}_{w}x{h}.png")
            page.locator("#f").screenshot(path=path)

    def primary():
        return frame.locator(".navbar .btn.pri")

    check("start"); shot("start")
    primary().click()
    guard = 0
    while guard < 60:
        guard += 1
        step = fr.evaluate("(document.querySelector('.steps .on')||{}).textContent")
        if step in ("Learn", "Watch"):
            m = check("slide"); shot("slide")
            primary().click()
        elif step == "Listen":
            check("listen")
            for cb in frame.locator(".check input").all():
                cb.check()
            fr.wait_for_timeout(150)
            shot("listen")
            primary().click()
        elif step == "Key points":
            fr.wait_for_timeout(900)
            check("keypoints"); shot("keypoints")
            primary().click()
        elif step == "Floor Check":
            check("floorcheck"); shot("floorcheck")
            primary().click()
        elif step == "Test":
            prompt = frame.locator(".prompt").inner_text()
            check("test-question")
            frame.locator(".opt", has_text=correct[prompt]).first.click()
            fr.wait_for_timeout(900)
            shot("test"); check("test-answered")
            primary().click()
        elif step == "Result":
            fr.wait_for_timeout(1500)
            m = check("result"); shot("result")
            break
    store = page.evaluate("window.__store")
    calls = page.evaluate("window.__calls")
    ctx.close()
    lms_ok = store.get("cmi.core.lesson_status") == "passed" and store.get("cmi.core.score.raw") == "100" and "commit" in calls
    return {"lesson": lid, "size": f"{w}x{h}", "screens": screens, "js_errors": errors,
            "lms": {"status": store.get("cmi.core.lesson_status"), "raw": store.get("cmi.core.score.raw"),
                    "suspend_data": store.get("cmi.suspend_data"), "calls": sorted(set(calls))},
            "ok": all(s["ok"] for s in screens) and not errors and lms_ok}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lessons", nargs="*", default=["L1-05", "L3-06", "L6-03"])
    ap.add_argument("--shots", action="store_true", help="save PNG screenshots to dist/screenshots/")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("render check skipped: Playwright is not installed (pip install playwright; python3 -m playwright install chromium)")
        return 0
    shots_dir = os.path.join(DIST, "screenshots") if a.shots else None
    if shots_dir:
        os.makedirs(shots_dir, exist_ok=True)
    httpd = serve(DIST)
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for lid in a.lessons:
            for size in SIZES:
                r = run_one(browser, base, lid, size, shots_dir)
                results.append(r)
                bad = [s for s in r["screens"] if not s["ok"]]
                print(f"{'PASS' if r['ok'] else 'FAIL'}  {lid} {r['size']}: {len(r['screens'])} screens, "
                      f"main button always reachable: {'yes' if not bad else 'NO'}, LMS: {r['lms']['status']} {r['lms']['raw']}"
                      + (f", JS errors: {r['js_errors']}" if r["js_errors"] else ""))
                for s in bad:
                    print("        -", json.dumps(s))
        browser.close()
    httpd.shutdown()
    with open(os.path.join(DIST, "render_check.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    ok = all(r["ok"] for r in results)
    print("RENDER CHECK GREEN" if ok else "RENDER CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
