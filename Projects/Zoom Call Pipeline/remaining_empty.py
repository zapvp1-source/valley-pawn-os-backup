#!/usr/bin/env python3
"""Are the still-empty transcripts genuinely empty calls, or is whisper still failing?

If they are overwhelmingly very short, they are hangups / wrong numbers / caller-never-spoke —
genuinely nothing to transcribe. If long ones remain, the fix is incomplete.
"""
import json, glob, re, os, statistics as st

TX = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline/out/transcripts")
AN = re.compile(r"this call may be recorded for quality assurance and training purposes\.?", re.I)

d = []
for p in glob.glob(TX + "/*/*.json"):
    r = json.load(open(p, encoding="utf-8"))
    t = r.get("transcript") or ""
    if len(re.sub(r"[\[\(].*?[\]\)]", "", AN.sub("", t)).strip()) < 25:
        d.append(r.get("duration_s", 0))
d.sort()
print("remaining empty: %d" % len(d))
if d:
    print("median %ds   max %ds" % (st.median(d), max(d)))
    print("under 20s: %d    20-45s: %d    over 45s: %d" % (
        sum(1 for x in d if x < 20), sum(1 for x in d if 20 <= x <= 45),
        sum(1 for x in d if x > 45)))
    print("the long ones still empty:", [x for x in d if x > 45][:15])
