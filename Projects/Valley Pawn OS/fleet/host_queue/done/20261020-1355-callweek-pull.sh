#!/bin/bash
# comms review restart 2026-10-20: pull the 10/12-10/18 week for the native call-week smoke (read-only Zoom S2S; transcripts mostly already on disk from the 9/28-10/18 harvest), detached
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/call_week_review.py" --since 2026-10-12 --until 2026-10-18 --detach
