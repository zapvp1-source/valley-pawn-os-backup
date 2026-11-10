#!/usr/bin/env python3
"""Delete the bot's own 'moved to' pointer posts in channels that stay (2026-11-09)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
for ch, ts in [("C0C06PWLQCR", "1794249680.042739"), ("C0B1PEW0C30", "1794249683.614309"), ("C0BP4M3B99R", "1794249684.358999")]:
    r = vp_slack.call("chat.delete", {"channel": ch, "ts": ts}); print(ch, r.get("ok"), r.get("error"))
