#!/bin/bash
# wave 3 second pass - RE-RENDERS after fixes (names, token budgets, gates). Nothing posted, no pulls.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/gun_audit_monthly.py" --period 2026-09 --render --no-sheet
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ceo_monthly_scorecard.py" 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_drift_monthly.py" --render --asof 2026-10-03
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/entity_compliance_monthly.py" --render --asof 2026-10-01
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_eom_recap.py" 2026-09 --render
