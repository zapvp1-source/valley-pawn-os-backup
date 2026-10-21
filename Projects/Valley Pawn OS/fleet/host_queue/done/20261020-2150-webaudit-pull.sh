#!/bin/bash
# website audit 2026-10-20: read-only 90-day GA4 + Search Console deep pull (no posts, no site writes)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/website_audit_pull.py" --days 90 --end 2026-10-19
