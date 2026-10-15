#!/usr/bin/env python3
"""trend_page_probe.py — READ-ONLY: where does the "vp-website-trend" page live and when was it last written?
(2026-10-14, Google re-grant prep). Lists name matches under the Claude app's data folder and the Desktop
backup folder, prints mtimes and whether each HTML holds a `const DATA =` block. Never writes anything."""
import os, re, sys, datetime
H = os.path.expanduser("~")
ROOTS = [os.path.join(H, "Library/Application Support/Claude"), os.path.join(H, "Desktop")]
PAT = re.compile(r"(website[-_ ]?trend|vp-website-trend)", re.I)
def ts(p):
    return datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M")
hits = []
for root in ROOTS:
    for dp, dns, fns in os.walk(root):
        if dp.count(os.sep) - root.count(os.sep) > 9:
            dns[:] = []
            continue
        dns[:] = [d for d in dns if d not in ("node_modules", "Cache", "Code Cache", "GPUCache", "IndexedDB", "Service Worker", "vm_bundles")]
        for n in dns + fns:
            if PAT.search(n):
                hits.append(os.path.join(dp, n))
for p in hits[:80]:
    try:
        info = ts(p)
        if os.path.isfile(p):
            sz = os.path.getsize(p)
            data = ""
            if p.endswith((".html", ".htm")):
                t = open(p, encoding="utf-8", errors="replace").read()
                m = re.search(r"refreshed-time\">([^<]*)<", t)
                data = " DATA=%s refreshed=%s" % ("const DATA" in t or "DATA =" in t, m.group(1) if m else "?")
            print("FILE %s  %s  %d B%s" % (p, info, sz, data))
        else:
            print("DIR  %s  %s  %s" % (p, info, sorted(os.listdir(p))[:15]))
    except Exception as e:
        print("ERR  %s %s" % (p, e))
print("hits:", len(hits))
