#!/usr/bin/env python3
"""usearch_scan_probe.py — why does the nightly mail rebuild find 0 messages?

WHY (2026-09-21): unified-search-verify has told Joshua every night for 9 days that the rebuild is
"being denied access to Apple Mail and Messages" and needs a Full Disk Access grant. That is FALSE
— proven today: vp-runner read ~/Library/Mail AND ~/Library/Messages/chat.db (58,042 unread,
64,767 messages). So the rebuild fails for some OTHER reason and has been misreporting it, which
sent a standing NEEDS_HUMAN request at Joshua for a permission he already has.

The shrink guard shipped 9/18 aborts when the scan finds 0 or <50% of the indexed corpus. The guard
is working as designed. The question is why the SCAN comes back empty when the store is readable.
This reproduces exactly what the indexer does — walk for .emlx files — and reports what it sees.
"""
import os, sys, time
HOME = os.path.expanduser("~")
MAIL = os.path.join(HOME, "Library/Mail")
print("# Mail scan probe (what the indexer actually sees)\n")
print("root: %s  exists=%s" % (MAIL, os.path.isdir(MAIL)))
try:
    print("top level:", sorted(os.listdir(MAIL)))
except Exception as e:
    print("cannot list root: %s" % e); raise SystemExit(1)
t0 = time.time(); emlx = 0; dirs = 0; sample = []; err = None
try:
    for root, dn, fn in os.walk(MAIL):
        dirs += 1
        for f in fn:
            if f.endswith(".emlx"):
                emlx += 1
                if len(sample) < 3:
                    sample.append(os.path.join(root, f))
        if time.time() - t0 > 90:
            print("\n(stopped walking after 90s — partial numbers below)")
            break
except Exception as e:
    err = "%s: %s" % (type(e).__name__, e)
print("\ndirectories walked: %d" % dirs)
print(".emlx files found: %d" % emlx)
print("walk error: %s" % (err or "none"))
for s in sample:
    print("  sample:", s.replace(HOME, "~"))
print()
if emlx == 0:
    print("**FINDING: the walk sees ZERO .emlx files even though the store is readable.**")
    print("That is why the shrink guard aborts every night — it is protecting the index from a")
    print("scan that legitimately found nothing. The bug is in WHAT the indexer looks for, not in")
    print("permissions. Apple Mail V10 may no longer store messages as loose .emlx files.")
else:
    print("**FINDING: the walk DOES find .emlx files (%d).** So the scan is not inherently empty;" % emlx)
    print("the rebuild's failure is later in the pipeline, not at discovery.")
