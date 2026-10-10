#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.ceo-week-pull
bash "$BIN/ceo_week_pull.sh" --week 2026-09-28
