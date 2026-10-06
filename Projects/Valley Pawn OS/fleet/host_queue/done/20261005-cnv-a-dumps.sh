#!/bin/bash
echo ===== weekly-loan-review-canvas-refresh
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-loan-review-canvas-refresh 40000
echo ===== weekly-layaway-review-canvas-refresh
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-layaway-review-canvas-refresh 40000
echo ===== weekly-employee-perf-canvas-refresh
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-employee-perf-canvas-refresh 40000
echo ===== weekly-aged-inventory-canvas-refresh
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-aged-inventory-canvas-refresh 40000
echo ===== weekly-store-perf-canvas-refresh
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-store-perf-canvas-refresh 40000
echo ===== weekly-markdown-verification-pull
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-markdown-verification-pull 40000
echo ===== weekly-markdown-verification-review
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-markdown-verification-review 40000
echo ===== bonus-pace-monday
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" bonus-pace-monday 40000
echo ===== scopes
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/slack_scope_probe.py"
