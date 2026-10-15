#!/bin/bash
# Waynesboro Sat 5 PM close (Joshua 2026-10-14) — render-only verification; nothing posted, texted or sent.
B="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
echo ===== chekkit morning render Sat 10/10 and Wed 10/14
python3 "$B/chekkit_unanswered.py" morning --day 2026-10-10 --render
python3 "$B/chekkit_unanswered.py" morning --day 2026-10-14 --render
echo ===== ai responder WAY Sat 10/17 16:30 / 17:30, Fri 10/16 17:30
python3 "$B/chekkit_ai_responder.py" --text "are you open today" --store WAY --at 2026-10-17T16:30:00-04:00
python3 "$B/chekkit_ai_responder.py" --text "are you open today" --store WAY --at 2026-10-17T17:30:00-04:00
python3 "$B/chekkit_ai_responder.py" --text "are you open today" --store WAY --at 2026-10-16T17:30:00-04:00
