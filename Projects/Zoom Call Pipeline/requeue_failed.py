#!/usr/bin/env python3
"""
requeue_failed.py — delete transcripts that are nothing but the recorded-line announcement, so
harvest_transcripts.py will re-pull and re-transcribe them with the -mc 0 fix.

WHY THESE EXIST
    whisper carries decoded text forward as context. Every call opens with the same announcement,
    the model locks onto it, repeats it 2-8 times, and drops the actual conversation. The audio was
    always fine — loud, two people talking, full length. Adding `-mc 0` to the whisper call fixes
    it (verified on the same file: 4 copies of the announcement before, full conversation after).

    Nothing is lost by deleting these — they contain no information. The audio still lives in Zoom.

USAGE
    python3 requeue_failed.py            # report only
    python3 requeue_failed.py --delete   # actually remove them, then re-run harvest_transcripts.py
"""
import os, re, sys, json, glob, argparse

BASE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline")
TX = os.path.join(BASE, "out", "transcripts")
AN = re.compile(r"this call may be recorded for quality assurance and training purposes\.?", re.I)


def is_failed(text):
    body = re.sub(r"[\[\(].*?[\]\)]", "", AN.sub("", text or "")).strip()
    return len(body) < 25


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delete", action="store_true")
    a = ap.parse_args()

    failed, total = [], 0
    for p in glob.glob(os.path.join(TX, "*", "*.json")):
        total += 1
        r = json.load(open(p, encoding="utf-8"))
        if is_failed(r.get("transcript")):
            failed.append((p, r))

    print("transcripts on disk: %d" % total)
    print("announcement-only (whisper looped, conversation lost): %d (%.0f%%)"
          % (len(failed), 100.0 * len(failed) / max(total, 1)))

    by_day = {}
    for _, r in failed:
        by_day[r["date"]] = by_day.get(r["date"], 0) + 1
    for d in sorted(by_day):
        print("   %s  %d" % (d, by_day[d]))

    secs = sum(r.get("duration_s", 0) for _, r in failed)
    print("\naudio to re-transcribe: %.0f minutes across %d calls" % (secs / 60.0, len(failed)))

    if not a.delete:
        print("\n(report only — pass --delete to requeue them)")
        return 0

    for p, _ in failed:
        os.remove(p)
    print("\ndeleted %d. Now run: python3 harvest_transcripts.py --since 2026-08-21" % len(failed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
