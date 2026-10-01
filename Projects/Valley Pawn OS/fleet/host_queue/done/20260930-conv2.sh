#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/desktop_cleanup.sh" --render
bash "$BIN/docphotos_index.sh" --render
bash "$BIN/install_agent.sh" com.valleypawn.desktop-cleanup
bash "$BIN/install_agent.sh" com.valleypawn.docphotos-index
