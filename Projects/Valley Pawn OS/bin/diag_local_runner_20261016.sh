#!/bin/bash
# 2026-10-16 diag: run the local runner once in the foreground and show its log + CLI sign-in state.
"$HOME/.local/bin/claude" auth status 2>&1 | head -5
ls -la "$HOME/.preston_local_runner.lock" 2>&1 | head -2
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/preston_local_runner.py"; echo "rc=$?"
tail -5 "$HOME/Library/Logs/valleypawn/preston-local-runner.log" 2>&1
tail -3 "$HOME/Library/Logs/valleypawn/preston-watch.log" 2>&1
