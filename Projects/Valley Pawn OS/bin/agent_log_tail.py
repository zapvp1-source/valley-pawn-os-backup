#!/usr/bin/env python3
"""agent_log_tail.py <agent> [n] — last n lines of ~/Library/Logs/valleypawn/<agent>.log and .err.log.
Read-only. Exists because the sandbox cannot see ~/Library and tail_log.py is hardwired to usearch."""
import os, sys
H = os.path.expanduser("~/Library/Logs/valleypawn")
a = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
for suf in (".log", ".err.log"):
    f = os.path.join(H, a + suf)
    print("== %s ==" % f.replace(os.path.expanduser("~"), "~"))
    if not os.path.isfile(f):
        print("  (absent)"); continue
    for line in open(f, errors="replace").read().splitlines()[-n:]:
        print(" ", line)
