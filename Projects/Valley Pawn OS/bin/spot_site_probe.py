#!/usr/bin/env python3
"""read-only: every VP_GOLD_SPOT / VP_SILVER_SPOT assignment on the gold/silver pages, with page + context."""
import re, urllib.request
pages = ["/sell-gold-culpeper/", "/sell-gold-waynesboro/", "/sell-gold-harrisonburg/", "/sell-gold-lexington/", "/sell-gold-roanoke/", "/", "/sell-gold/", "/gold-calculator/", "/silver-calculator/"]
for p in pages:
    try:
        h = urllib.request.urlopen(urllib.request.Request("https://thevalleypawn.com" + p + "?nocache=1", headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        print(p, "ERR", getattr(e, "code", e)); continue
    hits = [(m.start(), h[max(0, m.start()-200):m.end()+60].replace("\n", " ")) for m in re.finditer(r"VP_(GOLD|SILVER)_SPOT\s*=\s*[\d.]+", h)]
    print("==", p, len(hits))
    for pos, ctx in hits: print("   @%d %s" % (pos, ctx[-330:]))
