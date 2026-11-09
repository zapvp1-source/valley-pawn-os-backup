#!/bin/bash
# launchd wrapper — com.valleypawn.books-nightly (04:15 + 14:00). Joshua 2026-11-08: "accurate numbers through the day before, at any time."
# Runs after bravo-daily-gl: eBay fees per store per day (last 3 days, self-correcting), then the catch-all re-class sweep (misc_sweep.py: known vendors out of Misc Expense, unknowns listed), then the live books snapshot
# (P&L YTD / by store / by month + Balance Sheet through yesterday, with the machine-built AS-OF statement).
AGENT="books-nightly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
QB="$HOME/Documents/Claude/Projects/Quickbooks Set UP"; LOG="$OS_DIR/fleet/state/books_nightly/run.log"
echo "$(date '+%F %T') books-nightly start" >> "$LOG"
"$PY" "$QB/ebay_daily.py" --apply >> "$LOG" 2>&1 || echo "$(date '+%F %T') ebay_daily FAILED exit $?" >> "$LOG"
"$PY" "$QB/misc_sweep.py" --apply --days 10 >> "$LOG" 2>&1 || echo "$(date '+%F %T') misc_sweep FAILED exit $?" >> "$LOG"
"$PY" "$QB/books_snapshot.py" >> "$LOG" 2>&1 || echo "$(date '+%F %T') books_snapshot FAILED exit $?" >> "$LOG"
cp "$QB/snapshots/BOOKS_LATEST.md" "$OS_DIR/fleet/state/books_nightly/STATUS.md" 2>/dev/null
echo "$(date '+%F %T') books-nightly done" >> "$LOG"
