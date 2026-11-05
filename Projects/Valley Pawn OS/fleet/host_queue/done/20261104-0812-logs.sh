#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" texting-scorecard.log 25
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" daily-dress-code-check.log 25
ls -la /Users/joshuadavis/Library/Logs/valleypawn | grep -i "texting\|dress"
