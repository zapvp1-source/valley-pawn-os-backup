#!/usr/bin/env python3
"""send_ffl_set.py — email the signed FFL license PDFs as ATTACHMENTS via Apple Mail, from jdavis@.
Added 2026-09-29 (additive) because some vendors (e.g. KYGUNCO) can't open the website links.
Narrow on purpose: attaches only files from Compliance/ffl-files/<store>-ffl-web.pdf.

Usage: send_ffl_set.py <to_addr> <message_json>
  message_json: {"subject": "...", "body": "...", "stores": ["culpeper","waynesboro",...], "reply_note": "..."}
Reuses ffl_guardian.send_reply (same Apple Mail path the guardian already uses).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ffl_guardian as g

to_addr, msg_path = sys.argv[1], sys.argv[2]
m = json.load(open(msg_path))
atts = []
for s in m["stores"]:
    p = os.path.join(g.FFL_FILES, "%s-ffl-web.pdf" % s)
    if not os.path.isfile(p):
        print("MISSING", p); sys.exit(2)
    atts.append(p)
ok = g.send_reply(to_addr, m["subject"], m["body"], atts)
print("SENT" if ok else "FAILED", to_addr, len(atts), "attachments")
sys.exit(0 if ok else 1)
