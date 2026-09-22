#!/bin/bash
# HOST JOB — weekly-store-kpis (2026-09-21): compile the 5-store EOM xlsx (pulled by the
# 1130-weekly-store-kpis-eom-pull job) into the two Slack ranking messages.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=== weekly-store-kpis compile for 2026-09-20 ==="
bash "$BIN/store_kpis_compile_run.sh" 2026-09-20
echo "compile exit=$?"
