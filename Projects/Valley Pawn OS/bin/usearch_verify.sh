#!/bin/bash
# Native replacement for unified-search-verify — 2026-09-17 (deterministic branch; a FAILED log is ledgered, not "fixed" blind).
AGENT=usearch-verify; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
U="$HOME/Documents/Claude/Projects/Unified Search"; TODAY=$(date +%Y-%m-%d); ST="UNKNOWN"
L=$(tail -c 1500 "$U/refresh_hardened.log" 2>/dev/null | tr '\r' '\n')
if echo "$L" | grep -q "=== hardened success on attempt" && [ "$(stat -f %Sm -t %Y-%m-%d "$U/stats.txt" 2>/dev/null)" = "$TODAY" ]; then ST=SUCCESS
elif pgrep -f refresh_hardened.sh >/dev/null; then ST=RUNNING
elif echo "$L" | grep -q "=== hardened FAILED after"; then ST=FAILED
else ( bash "$U/refresh_hardened.sh" ) > /tmp/usearch_task_run.log 2>&1 < /dev/null & sleep 15; pgrep -f refresh_hardened.sh >/dev/null && ST=RELAUNCHED || ST=FAILED; fi
PH="N/A"; PL=$(tail -8 "$U/photosindex_documents.log" 2>/dev/null | grep "DOCUMENT PHOTOS INDEX DONE" | tail -1)
[ -n "$PL" ] && { echo "$PL" | grep -q "$TODAY" && PH=SUCCESS || PH=STALE; }
echo "$(date +%Y-%m-%dT%H:%M:%S%z) usearch=$ST photos=$PH (native)" >> "$U/verify_runs.log"; vlog "usearch=$ST photos=$PH"
[ "$ST" = "FAILED" ] && ledger "unified-search-verify" "The overnight search index rebuild finished FAILED after 3 attempts — last lines: $(echo "$L" | tail -3 | tr '\n' ' ' | cut -c1-160)" "no"
exit 0
