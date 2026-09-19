#!/usr/bin/env python3
"""inspect_path.py — read-only look at a host path an interactive session cannot reach.

WHY: a Cowork session cannot read ~/Documents/Claude/Scheduled or ~/Library/*, which is exactly
where the answers live when a scheduled task misbehaves. Every past session worked around that by
inventing a new one-off script per question, which is how bin/ grows junk and how the allow-list
gets widened. One general read-only inspector is safer than ten specific ones.

READ-ONLY BY CONSTRUCTION: lists directories, prints the head of text files, stats anything else.
It never writes, moves, or deletes. Output is capped so a huge file cannot flood a job log.

    inspect_path.py <path> [<path> ...] [--lines N]
"""
import os
import sys

LIMIT = int(sys.argv[sys.argv.index("--lines") + 1]) if "--lines" in sys.argv else 40
MAX_ENTRIES = 200
TEXT = (".md", ".txt", ".json", ".sh", ".py", ".plist", ".csv", ".log", ".yaml", ".yml", ".jsonl")


def show(p):
    p = os.path.expanduser(p)
    print("\n=== %s ===" % p)
    if not os.path.exists(p):
        print("DOES NOT EXIST")
        return
    if os.path.isdir(p):
        try:
            names = sorted(os.listdir(p))
        except OSError as e:
            print("cannot list: %s" % e)
            return
        print("directory, %d entries" % len(names))
        for n in names[:MAX_ENTRIES]:
            f = os.path.join(p, n)
            try:
                st = os.stat(f)
                print("  %-52s %9d  %s" % (n + ("/" if os.path.isdir(f) else ""), st.st_size,
                                           __import__("datetime").datetime.fromtimestamp(st.st_mtime)
                                           .strftime("%m/%d %H:%M")))
            except OSError:
                print("  %s (stat failed)" % n)
        if len(names) > MAX_ENTRIES:
            print("  ... %d more" % (len(names) - MAX_ENTRIES))
        return
    st = os.stat(p)
    print("file, %d bytes, modified %s" % (st.st_size,
          __import__("datetime").datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")))
    if not p.lower().endswith(TEXT):
        print("(not a text extension — not printing contents)")
        return
    try:
        with open(p, errors="replace") as f:
            for i, line in enumerate(f):
                if i >= LIMIT:
                    print("... (truncated at %d lines)" % LIMIT)
                    break
                print("  " + line.rstrip()[:200])
    except OSError as e:
        print("cannot read: %s" % e)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--lines" in sys.argv:
        v = sys.argv[sys.argv.index("--lines") + 1]
        args = [a for a in args if a != v]
    if not args:
        print(__doc__)
        return 2
    for a in args:
        show(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
