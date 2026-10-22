#!/bin/bash
# Nov 1 monthly rehearsal — part C: wrapper --render runs for the Slack-history / model agents.
echo "=== RENDER hr-policy-sync ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/hr_policy_sync_monthly.sh" --render --since 2026-09-01 --until 2026-10-01
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-hr-policy-monthly-sync.log 30
echo "=== RENDER entity-compliance ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/entity_compliance_monthly.sh" --render --asof 2026-10-01
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" entity-compliance-check.log 30
echo "=== RENDER comms-drift ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_drift_monthly.sh" --render --asof 2026-10-03
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-comms-drift-monthly-check.log 25
echo "=== RENDER ceo-monthly-scorecard ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ceo_monthly_scorecard.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" ceo-monthly-scorecard.log 30
echo "=== RENDER bonus-month-close ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_month_close.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" bonus-month-close.log 30
echo "=== RENDER eom-recap ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_eom_recap.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-eom-recap.log 40
echo "=== C DONE ==="
