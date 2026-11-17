#!/bin/bash
# render-only (publishes nothing): new compact sold/discount + flags-only pawn walk
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" discount 2026-11-14 --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" sold 2026-11-14 --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" pawn 2026-11-14 --render
