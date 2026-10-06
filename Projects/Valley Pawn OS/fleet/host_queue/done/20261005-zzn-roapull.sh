#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/bravo_pull.sh" chekkit-invites-range 2026-09-28..2026-10-04 ROA roa-chekkit-recheck-20261005
bash "$BIN/install_agent.sh" com.valleypawn.chekkit-review-invites
