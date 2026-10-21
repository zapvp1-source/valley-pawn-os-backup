#!/bin/bash
# comms review 2026-10-20: install the three new native agents (dormant/gated where noted) + probe the review-reply agent + render it
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.call-week-review
bash "$BIN/install_agent.sh" com.valleypawn.ai-reply-audit
bash "$BIN/install_agent.sh" com.valleypawn.review-reply
python3 "$BIN/review_reply.py" --probe
python3 "$BIN/review_reply.py" --render
