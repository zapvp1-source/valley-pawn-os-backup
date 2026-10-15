#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Website/analytics/bin/ga4_pull.py" --check
python3 "$HOME/Documents/Claude/Projects/Website/analytics/bin/gsc_pull.py" --check
python3 "$HOME/Documents/Claude/Projects/Website/analytics/bin/ga4_pull.py" --windows
