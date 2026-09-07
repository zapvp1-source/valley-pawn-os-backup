"""
vp_social — the deterministic social-media engine for Valley Pawn (built 2026-09-05).

One engine, one publisher, one ledger:
  config.py   paths, account map, store facts, routing tiers
  reader.py   THE ONLY reader of Publer (always from/to, always paginated)
  ledger.py   SQLite ledger of every planned / scheduled / published post
  publish.py  THE ONLY writer to Publer (QA gates, idempotent by ledger key)
  plan.py     weekly planner — slots, de-duplication, caption contracts
  report.py   deterministic formatters (Rule 18: withhold on any gap)
  cli.py      `python3 -m vp_social <command>`

Design notes: see Refine Social Media/SOCIAL_SYSTEM_SPEC.md
"""
__version__ = "0.1.0"
