#!/bin/bash
# ebay_ratings_pull.sh — native data half of `monthly-ebay-ratings-sweep` (1st of month 09:45, 2026-10-02).
# Runs the SKILL's own Step 1 on the host (the script needs ~/.vp_secrets, which a Cowork session can't
# reach — that is why the 10/1 run failed). Writes eBay/ebay-ratings-sweep-<YYYY-MM>.md for the Cowork task.
AGENT="ebay-ratings-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
E="$HOME/Documents/Claude/Projects/eBay"; OUT="$E/ebay-ratings-sweep-$(date +%Y-%m).md"
( cd "$HOME" && "$PY" "$E/ebay_ratings_headless.py" ) > "$OUT.tmp" 2>&1
if grep -q '^| 1 |' "$OUT.tmp"; then mv "$OUT.tmp" "$OUT"; vlog "wrote $OUT"; grep -c 'PULL FAILED' "$OUT"
else ledger "$AGENT" "This month's eBay ratings data pull did not complete." "no"; tail -5 "$OUT.tmp"; exit 1; fi
