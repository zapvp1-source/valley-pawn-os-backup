#!/bin/bash
# HOST JOB 2026-09-17 — install the 10 native agents replacing osascript-dependent Cowork tasks; prove the 3 daily reports on 9/16 data.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.bravo-relaunch
bash "$BIN/install_agent.sh" com.valleypawn.bravo-health-watchdog
bash "$BIN/install_agent.sh" com.valleypawn.business-os-refresh
bash "$BIN/install_agent.sh" com.valleypawn.usearch-refresh
bash "$BIN/install_agent.sh" com.valleypawn.usearch-verify
bash "$BIN/install_agent.sh" com.valleypawn.github-backup
bash "$BIN/install_agent.sh" com.valleypawn.jewelry-pull-watchdog
bash "$BIN/install_agent.sh" com.valleypawn.daily-report-pawn
bash "$BIN/install_agent.sh" com.valleypawn.daily-report-sold
bash "$BIN/install_agent.sh" com.valleypawn.daily-report-discount
bash "$BIN/daily_report.sh" pawn 2026-09-16
bash "$BIN/daily_report.sh" sold 2026-09-16
bash "$BIN/daily_report.sh" discount 2026-09-16
bash "$BIN/host_diag.sh" agents
