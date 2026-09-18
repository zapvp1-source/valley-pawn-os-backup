#!/bin/bash
# HOST JOB — Phase 0.4: re-run field_scorecard.py after (a) +19 verified manifest entries,
# (b) monsat cadence, dated-file placeholders, case-insensitive markers, CANVAS/INFRA/DM-SURFACE
# statuses. Then restart the launchd agent so the 30-min loop picks up the new code.
set +e
U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "=== rerun2 start $(date) ==="
/usr/bin/python3 "$OS/bin/field_scorecard.py" 2>&1; echo "rc=$?"
launchctl kickstart -k gui/$U/com.valleypawn.field-scorecard 2>&1 && echo "agent restarted"
sleep 2; launchctl list | grep field-scorecard
echo; echo "--- status counts ---"
for s in OK MISSED UNVERIFIED PENDING DM-SURFACE CANVAS INFRA "NO COVERAGE" SKIPPED; do
  printf "%-12s %s\n" "$s" "$(grep -c "| $s |" "$OS/fleet/FIELD_SCORECARD.md")"
done
echo "=== rerun2 done $(date) ==="
