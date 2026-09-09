#!/usr/bin/env python3
"""Shape of the silent-recording problem: by direction, store, duration, announcement repeats."""
import json, glob, re, os, statistics as st

TX = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline/out/transcripts")
AN = re.compile(r"this call may be recorded for quality assurance and training purposes\.?", re.I)

rows = []
for p in glob.glob(TX + "/*/*.json"):
    d = os.path.basename(os.path.dirname(p))
    if not ("2026-08-31" <= d <= "2026-09-06"):
        continue
    r = json.load(open(p, encoding="utf-8"))
    t = r.get("transcript") or ""
    body = re.sub(r"[\[\(].*?[\]\)]", "", AN.sub("", t)).strip()
    r["_silent"] = len(body) < 25
    r["_reps"] = len(AN.findall(t))
    rows.append(r)

sil = [r for r in rows if r["_silent"]]
spk = [r for r in rows if not r["_silent"]]
print("TOTAL %d   silent %d (%.0f%%)" % (len(rows), len(sil), 100.0 * len(sil) / len(rows)))

print("\nby direction:")
for dirn in ("inbound", "outbound"):
    a = [r for r in rows if r["direction"] == dirn]
    s = [r for r in a if r["_silent"]]
    print("  %-9s %3d of %3d silent (%.0f%%)" % (dirn, len(s), len(a), 100.0 * len(s) / max(len(a), 1)))

print("\nby store:")
for s_ in ("HAR", "WAY", "LEX"):
    a = [r for r in rows if r.get("store") == s_]
    s = [r for r in a if r["_silent"]]
    print("  %-4s %3d of %3d (%.0f%%)" % (s_, len(s), len(a), 100.0 * len(s) / max(len(a), 1)))

print("\nannouncement repeats (how many times the greeting plays in one recording):")
print("  silent recordings   : median %.0f, max %d" % (
    st.median([r["_reps"] for r in sil]), max(r["_reps"] for r in sil)))
print("  recordings w/ speech: median %.0f, max %d" % (
    st.median([r["_reps"] for r in spk]), max(r["_reps"] for r in spk)))

print("\nduration of silent recordings:")
ds = [r["duration_s"] for r in sil]
print("  median %ds   under 30s: %d   30-120s: %d   over 120s: %d" % (
    st.median(ds), sum(1 for d in ds if d < 30),
    sum(1 for d in ds if 30 <= d <= 120), sum(1 for d in ds if d > 120)))

print("\nhour of day (inbound silent vs inbound with speech):")
print("  (recording metadata has no local time here — using date only)")

# Does a silent recording tend to be followed by a real call from a queue perspective?
print("\nsilent recordings by day:")
for d in sorted({r["date"] for r in rows}):
    a = [r for r in rows if r["date"] == d]
    s = [r for r in a if r["_silent"]]
    print("  %s  %2d of %2d (%.0f%%)" % (d, len(s), len(a), 100.0 * len(s) / max(len(a), 1)))
