#!/bin/bash
# Texts-only Unified Search refresh — every 30 min (2026-10-14). The nightly full chain (03:30) left
# iMessage/SMS up to ~24h stale; msgindex.py alone is small (~66k rows) and safe to run often.
# Shares the full chain's lock so the two never overlap; msgindex.py's shrink guard still applies.
AGENT=usearch-msgs; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
U="$HOME/Documents/Claude/Projects/Unified Search"
LOCK="$U/.refresh.lockdir"
cd "$U" || exit 1
mkdir "$LOCK" 2>/dev/null || { vlog "full refresh running — skip"; exit 0; }
trap 'rm -rf "$LOCK"' EXIT
/usr/bin/nice -n 10 /usr/bin/python3 msgindex.py >> "$VLOG/usearch-msgs.out.log" 2>&1
rc=$?
STAMP="$VLOG/.usearch-msgs.ok"
if [ $rc -eq 0 ]; then touch "$STAMP"; vlog "msgindex ok"
else
  vlog "msgindex FAILED rc=$rc"
  # one ledger row only if texts have been stale > 6h (no per-run noise)
  if [ ! -f "$STAMP" ] || [ -n "$(find "$STAMP" -mmin +360)" ]; then
    ledger "usearch-msgs" "Texts index has not refreshed in 6h+ (msgindex.py rc=$rc; see usearch-msgs.out.log)" "no"
    touch "$STAMP"
  fi
fi
exit 0
