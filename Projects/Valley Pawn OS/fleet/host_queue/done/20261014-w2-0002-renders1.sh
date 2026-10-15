#!/bin/bash
echo ===== VIDEO 2026-10-13 09:10
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/staff_video_prompt.py" --render --day 2026-10-13 --at 09:10
echo ===== VIDEO 2026-10-06 09:10
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/staff_video_prompt.py" --render --day 2026-10-06 --at 09:10
echo ===== VIDEO now
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/staff_video_prompt.py" --render
echo ===== VIDEO 2026-10-20 09:10 replay
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/staff_video_prompt.py" --render --day 2026-10-20 --at 09:10
echo ===== PUBLER 2026-10-09
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/publer_friday.py" --render --day 2026-10-09
echo ===== PUBLER 2026-10-02
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/publer_friday.py" --render --day 2026-10-02
echo ===== THU 2026-10-08
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/thursday_email_watchdog.py" --render --day 2026-10-08
echo ===== THU 2026-10-01
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/thursday_email_watchdog.py" --render --day 2026-10-01
echo ===== THU 2026-10-15
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/thursday_email_watchdog.py" --render --day 2026-10-15
