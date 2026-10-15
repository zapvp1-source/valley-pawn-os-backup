#!/bin/bash
# Waynesboro open Wednesdays (Joshua 2026-10-14) — verify gates on the Mac + read cloud-source SKILL.md Wednesday text. Read-only / render-only; nothing posted.
OS="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS"
echo ===== chekkit morning render 10/14 and 10/7
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --day 2026-10-14 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --day 2026-10-07 --render
echo ===== daily audit digest render 10/7 and 10/13 to test_output
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_audit_digest.py" 2026-10-07 --out "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/test_output/waywed_20261014"
echo ===== ebay ship alert render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ship_alert.py" --render
echo ===== chekkit ai responder next-open WAY Tue 7pm and Wed 11am
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_ai_responder.py" --text "are you open tomorrow" --store WAY --at 2026-10-13T19:00:00-04:00
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_ai_responder.py" --text "are you open today" --store WAY --at 2026-10-14T11:00:00-04:00
echo ===== SKILL.md sources
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "/Users/joshuadavis/Documents/Claude/Scheduled/daily-clockin-check/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-onhand-nightly-pull/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/zoom-voicemail-alert/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/missed-call-text-report/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/forfeiture-winback-texts-weekly/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/daily-cloudcover-check/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/chekkit-unanswered-alert/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/chekkit-unanswered-eod-followup/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/daily-store-audit-digest/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/vp-ai-search-health-check/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/vp-ai-visibility-metrics/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/vp-presence-audit-weekly/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/vp-hiring-pipeline/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/tuesday-supply-prep/SKILL.md" "/Users/joshuadavis/Documents/Claude/Scheduled/northwest-registered-agent-daily-check/SKILL.md" --lines 2000
