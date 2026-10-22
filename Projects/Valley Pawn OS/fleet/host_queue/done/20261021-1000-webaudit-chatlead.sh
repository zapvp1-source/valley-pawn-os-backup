#!/bin/bash
# website follow-up 2026-10-21: verify ga4_pull leads() now returns "Textchat Message" (read-only GA4 pull, no posts)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/website_audit_pull.py" --days 7 --end 2026-10-20 --out "/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-10-20/data_7d_chatlead.json"
