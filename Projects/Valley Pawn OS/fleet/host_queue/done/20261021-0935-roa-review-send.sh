#!/bin/bash
# website audit follow-up 2026-10-21 (Joshua approved "go fix 1-4"): Roanoke review-invite catch-up SEND, 576 previewed phones; Chekkit dedupes 1/yr; no Slack posts
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/chekkit_review_backfill.py" --store ROA --from 2026-04-01 --to 2026-09-28 --no-pull --send
