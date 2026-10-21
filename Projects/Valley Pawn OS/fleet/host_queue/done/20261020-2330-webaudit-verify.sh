#!/bin/bash
# website audit 2026-10-20: verify the ga4_pull form_submit filter on the host (read-only GA4 pull)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/website_audit_pull.py" --days 90 --end 2026-10-19 --out "/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-10-20/data_90d_postfix.json"
