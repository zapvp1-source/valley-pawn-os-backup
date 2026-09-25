#!/bin/bash
# RENDER ONLY — missed-call-text against live Zoom call history. Sends nothing, writes no state.
# Purpose: prove the API scope + credentials work and see every real call_result value Zoom returns.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/missed_call_text.sh" --render --hours 10
