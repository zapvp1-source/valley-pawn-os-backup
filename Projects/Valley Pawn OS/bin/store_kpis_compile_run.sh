#!/bin/bash
# store_kpis_compile_run.sh <ENDDATE>
# Allow-listed host wrapper for the weekly-store-kpis compile step. The compile script
# (store_kpis_compile.py) lives in the Bravo Data Extraction project, not under Valley Pawn OS/bin,
# so host_queue_run.sh's validator (which requires the invoked script to live under bin/) can't call
# it directly. This thin wrapper is the sanctioned way to add that capability (per host_queue_run.sh's
# own comment: "add a versioned script to bin/, list it, and call that").
BRAVO="$HOME/Documents/Claude/Projects/Bravo Data Extraction"
ENDDATE="$1"
[ -z "$ENDDATE" ] && { echo "usage: store_kpis_compile_run.sh <ENDDATE>"; exit 2; }
cd "$BRAVO" || exit 1
/usr/bin/python3 store_kpis_compile.py "$ENDDATE"
exit $?
