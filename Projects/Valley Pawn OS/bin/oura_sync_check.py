#!/usr/bin/env python3
"""oura_sync_check.py <importer-output.txt> <oura_latest.json> — classify a failed Oura import (2026-10-22).

Prints ONE line, never any health value:
  RING_NOT_SYNCED <YYYY-MM-DD>   the importer finished, the Oura API answered (authenticated endpoints returned
                                 rows, no 401/403), the only failure is the staleness sanity check -> the ring has
                                 not synced to the Oura cloud since <date> (newest day of readiness/heartrate data)
  FAULT <reason>                 anything else (auth error, crash, importer did not finish, summary unreadable)
"""
import json
import re
import sys

out_path, latest_path = sys.argv[1], sys.argv[2]
try:
    out = open(out_path, errors="replace").read()
except OSError:
    print("FAULT no importer output")
    sys.exit(0)
if re.search(r"\b(401|403)\b|Unauthorized|invalid[_ ]token|access[_ ]token|Forbidden", out, re.I):
    print("FAULT Oura API refused the token")
    sys.exit(0)
if "=== Done." not in out:
    print("FAULT importer did not finish")
    sys.exit(0)
if not re.search(r"(personal_info|ring_configuration)\s+[1-9]\d* rows", out):
    print("FAULT authenticated endpoints returned nothing")
    sys.exit(0)
stale = re.search(r"AssertionError: \w+ latest (\d{4}-\d{2}-\d{2}) is \d+ days old", out)
tbs = out.count("Traceback (most recent call last)")
if not stale or tbs != 1:
    print("FAULT failure is not the staleness check")
    sys.exit(0)
try:
    d = json.load(open(latest_path))
except Exception:
    print("FAULT summary unreadable")
    sys.exit(0)
days = [str(d.get(k) or "") for k in ("readiness_latest_day", "heartrate_latest_day")]
days = [x for x in days if re.match(r"\d{4}-\d{2}-\d{2}$", x)]
print("RING_NOT_SYNCED %s" % (max(days) if days else stale.group(1)))
