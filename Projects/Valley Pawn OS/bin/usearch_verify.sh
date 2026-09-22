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

# ---- STALENESS GATE (added 2026-09-20) -------------------------------------------------
# Why: the index silently rotted for 8 days and this verifier never once ledgered it. Its only
# alarm was the literal "hardened FAILED after 3 attempts" marker, which the wrapper can only
# write if it SURVIVES all 3 attempts. On 9/18 and 9/19 the wrapper was SIGTERM'd mid-attempt-1,
# so the status stayed RELAUNCHED, no row was ever written, and two nights of total failure looked
# identical to a healthy relaunch. A verifier whose alarm depends on the thing it is verifying
# finishing cleanly is not a verifier. This gate asks the only question that actually matters —
# HOW OLD IS THE INDEX — and is independent of how or why any run died.
# Age is measured from stats.txt, the file that is only written when a full chain succeeds.
ST_MTIME=$(stat -f %m "$U/stats.txt" 2>/dev/null || echo 0)
case "$ST_MTIME" in ''|*[!0-9]*) ST_MTIME=0 ;; esac
if [ "$ST_MTIME" -eq 0 ]; then
  AGE_DAYS=999; AGE_TEXT="has never finished a rebuild"; LAST_GOOD="never"
else
  AGE_DAYS=$(( ( $(date +%s) - ST_MTIME ) / 86400 ))
  AGE_TEXT="has not refreshed in $AGE_DAYS days"; LAST_GOOD=$(date -r "$ST_MTIME" '+%b %-d' 2>/dev/null)
fi
STAMP="$U/.stale_ledgered_on"
if [ "$AGE_DAYS" -ge 2 ] && [ "$(cat "$STAMP" 2>/dev/null)" != "$TODAY" ]; then
  echo "$TODAY" > "$STAMP"
  # Plain language only, no jargon (Rule 16). One row per calendar day, never a per-run burst.
  if grep -q "SHRINK GUARD TRIPPED" "$U/.refresh_attempt.log" 2>/dev/null; then
    # 2026-09-21: this used to tell Joshua the rebuild was "being denied access to Apple Mail and
    # Messages" and to grant Full Disk Access to ~/bin/vp-runner. THAT WAS FALSE and it sent him a
    # standing NEEDS_HUMAN request, every night for nine days, for a permission he already had.
    # Proven that day: vp-runner read ~/Library/Mail (58,042 unread) AND ~/Library/Messages/chat.db
    # (64,767 rows), and the indexer's own walk found 349,588 .emlx files. Access was never the
    # problem. The guard trips for some other reason, and this row must NOT invent one — naming a
    # cause we have not proven is what cost those nine days.
    ledger "unified-search-verify" \
      "Joshua's mail/text/file search $AGE_TEXT — nothing newer than $LAST_GOOD is findable. The nightly rebuild stopped itself rather than risk damaging the existing index, which is the safe behaviour, but it means the search is going stale. No data has been lost. Cause not yet established — it is NOT a permissions problem (that was checked and ruled out on 2026-09-21)." \
      "no — do NOT grant Full Disk Access; vp-runner already has it. This needs a look at why the rebuild's safety check is tripping, not a settings change."
  else
    ledger "unified-search-verify" \
      "Joshua's mail/text/file search $AGE_TEXT. The nightly rebuild is starting but never finishing." \
      "yes — see CHANGELOG 2026-09-18/09-20 and the Open Items Register."
  fi
fi
exit 0
