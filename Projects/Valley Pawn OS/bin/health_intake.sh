#!/bin/bash
# health_intake.sh — native replacement for the Cowork task `health-records-intake`.
#
# WHY (2026-09-23): the Cowork version needs the Control_your_Mac connector for both of its steps
# (inbox_ingest.py, and a vpfind mail search) and that connector is gone from scheduled sessions.
# Native agent, same two steps, same reporting rule: silent when nothing was filed, ONE plain DM to
# Joshua when something was. Never interprets results — repeats the lab's own flags at most.
# Domain 3 — personal. Nothing here touches Valley Pawn.
AGENT="health-records-intake"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 30
HP="$HOME/Documents/Claude/Projects/Health Optimization"
OUT="/tmp/health_intake_$(date +%Y%m%d).txt"

# Step 1 — file whatever is in the intake inbox
( cd "$HP" && $PY scripts/inbox_ingest.py ) > "$OUT" 2>&1; RC=$?
if [ $RC -ne 0 ]; then
  ledger "$AGENT" "The health records intake step errored (exit $RC): $(tail -1 "$OUT" | cut -c1-160)" "no"; exit 1
fi
FILED=$(grep -oE 'Filed [0-9]+ file' "$OUT" | grep -oE '[0-9]+' | head -1); FILED=${FILED:-0}
VALUES=$(grep -oE '[0-9]+ new lab value' "$OUT" | grep -oE '[0-9]+' | head -1); VALUES=${VALUES:-0}

# Step 2 — any new result emails in the last 2 days? (count only; nothing is opened here)
export PATH=/opt/homebrew/bin:$PATH
NEWMAIL=$(vpfind --mail --since "$(date -v-2d +%Y-%m-%d)" -n 30 'Labcorp OR Quest OR MyChart OR "Function Health" OR Genova OR Vibrant OR "test result"' 2>/dev/null | grep -cE '^[0-9]|^- ' )
NEWMAIL=${NEWMAIL:-0}

vlog "filed=$FILED values=$VALUES result_emails=$NEWMAIL"
if [ $RENDER -eq 1 ]; then echo "=== RENDER ONLY ==="; echo "filed=$FILED values=$VALUES result_emails=$NEWMAIL"; cat "$OUT"; exit 0; fi

# Step 3 — report only if something happened
if [ "$FILED" -eq 0 ] && [ "$NEWMAIL" -eq 0 ]; then vlog "Nothing new."; $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$OUT" >/dev/null 2>&1; exit 0; fi
MSG=":file_folder: *Health records* — filed $FILED file(s) with $VALUES new lab value(s) today."
[ "$NEWMAIL" -gt 0 ] && MSG="$MSG"$'\n'"$NEWMAIL result email(s) arrived in the last two days that are not filed yet."
DETAIL=$(grep -E '^  ' "$OUT" | head -6)
[ -n "$DETAIL" ] && MSG="$MSG"$'\n'"$DETAIL"
slack dm "$MSG" >/dev/null && vlog "DM sent" || ledger "$AGENT" "Health intake filed $FILED file(s) but the DM could not be sent." "no"
