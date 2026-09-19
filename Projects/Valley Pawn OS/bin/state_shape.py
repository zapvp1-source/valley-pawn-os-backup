#!/usr/bin/env python3
"""One-line integrity probe for field_scorecard's state file. Exists because that file silently
held a bare string for an unknown length of time and killed the watchdog on every run."""
import json, os
p = os.path.expanduser("~/Library/Logs/valleypawn/field_scorecard_state.json")
try:
    d = json.load(open(p))
    print("state file type: %s  keys: %s" % (type(d).__name__, list(d)[:8] if isinstance(d, dict) else repr(d)[:80]))
    raise SystemExit(0 if isinstance(d, dict) else 1)
except FileNotFoundError:
    print("state file absent (clean start) — OK"); raise SystemExit(0)
