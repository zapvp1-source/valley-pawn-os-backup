#!/bin/bash
# render-only (publishes nothing): re-render with the rebuilt item-age index
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" discount 2026-11-14 --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/daily_report.sh" sold 2026-11-14 --render
