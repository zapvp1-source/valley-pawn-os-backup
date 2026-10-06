#!/bin/bash
# launchd wrapper — com.valleypawn.brevo-attr-sync, Tue 17:30 (native, 2026-10-05). Logic: Email Refinement/_audit/enrich_contacts.py (proven 8/24).
AGENT="bravo-brevo-attribute-sync"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 180
cd "$HOME/Documents/Claude/Projects/Email Refinement/_audit" && "$PY" -u enrich_contacts.py --apply >> "$VLOG/$AGENT.log" 2>&1
"$PY" -u verify_enrichment.py >> "$VLOG/$AGENT.log" 2>&1
