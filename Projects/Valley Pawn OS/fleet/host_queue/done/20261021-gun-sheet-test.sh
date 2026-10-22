#!/bin/bash
# 2026-10-21 gun-audit Trends sheet writer fix: render-only tests against the live jdavis sheet. Nothing written. No Slack.
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
ST="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet"
/usr/bin/python3 "$BIN/gun_audit_sheet.py" --test "$ST/state/gun_audit/2026-09_format_input.json"
/usr/bin/python3 "$BIN/gun_audit_sheet.py" --test "$ST/test_output/gun_audit_sheet_test/2026-10_synthetic_format_input.json"
/usr/bin/python3 "$BIN/trends_migrate.py" --sheet-test 2026-09
