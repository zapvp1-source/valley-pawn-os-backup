#!/usr/bin/env python3
"""reg_shape.py — what shape is the scheduled-tasks registry actually in?

chromeperms_audit.py reported "enabled tasks scanned: 0", which is a tool failure, not a clean
fleet. Dump the real structure before writing another parser against an assumption.
"""
import json, os
REG = os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions/"
                         "823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"
                         "scheduled-tasks.json")
print("path exists:", os.path.isfile(REG), "size:", os.path.getsize(REG) if os.path.isfile(REG) else "-")
d = json.load(open(REG))
print("top type:", type(d).__name__)
if isinstance(d, dict):
    print("top keys:", list(d)[:12])
    for k, v in list(d.items())[:6]:
        print("  %-22s %s len=%s" % (k, type(v).__name__, len(v) if hasattr(v, "__len__") else "-"))
    # find the container that holds task-like records
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            print("\nlist '%s' first record keys:" % k, list(v[0])[:18]); break
        if isinstance(v, dict) and v:
            fk = list(v)[0]
            if isinstance(v[fk], dict):
                print("\ndict '%s' first record id=%r keys:" % (k, fk), list(v[fk])[:18]); break
elif isinstance(d, list):
    print("list len:", len(d))
    if d: print("first record keys:", list(d[0])[:18])
