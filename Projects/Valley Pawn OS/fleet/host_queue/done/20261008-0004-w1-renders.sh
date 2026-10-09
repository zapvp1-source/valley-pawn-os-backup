#!/bin/bash
echo ===== AUDIT 2026-10-06
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_audit_send.py" --render 2026-10-06
echo ===== SHOP
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/shop_render.py"
echo ===== DOW PROMPT 2026-10-05
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/deal_of_week_monday.py" prompt --render --day 2026-10-05
echo ===== DOW REMINDER 2026-10-05 at 11:00
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/deal_of_week_monday.py" reminder --render --day 2026-10-05 --at 11:00
echo ===== DOW REMINDER 2026-10-05 at 11:10
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/deal_of_week_monday.py" reminder --render --day 2026-10-05 --at 11:10
echo ===== MORNING 2026-10-07
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --render --day 2026-10-07
echo ===== MORNING 2026-09-25 dedupe
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --render --day 2026-09-25
