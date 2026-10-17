#!/bin/bash
# 2026-10-16: open the one-time sign-in window in Terminal for Joshua.
pkill -f "claude auth login" 2>/dev/null
open -a Terminal "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/Sign In Claude For Preston.command"
echo opened
