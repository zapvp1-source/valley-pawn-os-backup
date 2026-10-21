#!/bin/bash
# comms review 2026-10-20: smoke-test the native weekly phone/text review on Oct 12-18 with the Zoom pull (read-only; transcripts already on disk), 40 calls, render only
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_grade.py" --since 2026-10-12 --until 2026-10-18 --max-calls 40 --render
