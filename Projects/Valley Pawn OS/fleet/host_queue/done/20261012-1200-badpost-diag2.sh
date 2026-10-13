#!/bin/bash
/bin/bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monday-compile.log 60
/bin/bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" nics-weekly-mtd-ranking.log 40
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" raw C0BPH5T1NFL 1791813257.553729
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" raw C0BPH5T1NFL 1791209268.392419
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/store_rankings.py" 2026-10-12 --render --prefix "Corrected:"
