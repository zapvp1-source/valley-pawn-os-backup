#!/bin/bash
# comms review 2026-10-20: verify the scorecard unanswered-count fix (re-render 10/19) and the review-alert wording (render only, nothing sent)
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "== scorecard 10/19 re-render"
python3 "$BIN/texting_scorecard.py" --date 2026-10-19
echo "== scorecard today"
python3 "$BIN/texting_scorecard.py"
echo "== review alert render (last 120h, all)"
python3 "$BIN/chekkit_review_alert.py" --render --all --hours 120
echo "== ai responder self-test"
python3 "$BIN/chekkit_ai_responder.py" --selftest
