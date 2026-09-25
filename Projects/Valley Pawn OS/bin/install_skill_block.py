#!/usr/bin/env python3
"""install_skill_block.py <task> <block-file> [--apply]
Append the text in <block-file> to ~/Documents/Claude/Scheduled/<task>/SKILL.md, once. The block's
first line must be a '# ...' heading; that heading is the idempotency marker. Backed up, additive.
Generic successor to the one-off install_*_step.py scripts (2026-09-24)."""
import datetime as dt, os, sys
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
a = [x for x in sys.argv[1:] if not x.startswith("--")]
if len(a) != 2: print(__doc__); sys.exit(2)
task, bf = a
block = open(bf, encoding="utf-8").read().strip("\n")
mark = block.splitlines()[0].strip()
if not mark.startswith("# "): print("block must start with a '# heading' line"); sys.exit(2)
p = os.path.join(SCHED, task, "SKILL.md")
if not os.path.isfile(p): print("MISSING SKILL.md for", task); sys.exit(1)
body = open(p, encoding="utf-8").read()
if mark in body: print("already  %s has %r" % (task, mark)); sys.exit(0)
if "--apply" not in sys.argv: print("WOULD ADD %r to %s" % (mark, task)); sys.exit(0)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
open(p + ".bak-block-" + stamp, "w", encoding="utf-8").write(body)
open(p, "a", encoding="utf-8").write("\n\n---\n\n" + block + "\n")
print("ADDED    %r to %s" % (mark, task))
