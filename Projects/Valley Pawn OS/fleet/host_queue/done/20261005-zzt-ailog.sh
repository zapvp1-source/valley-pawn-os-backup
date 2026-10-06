#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/tail_any.sh" chekkit_ai_responder/run.log 15
bash "$BIN/tail_any.sh" chekkit_ai_responder/heartbeat.json 5
bash "$BIN/tail_any.sh" chekkit-ai-responder.err.log 10
