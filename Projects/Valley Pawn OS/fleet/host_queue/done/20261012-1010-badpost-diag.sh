#!/bin/bash
B="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/bin/bash "$B/tail_any.sh" monday-compile.log 60
/bin/bash "$B/tail_any.sh" nics-weekly-mtd-ranking.log 40
/usr/bin/python3 "$B/vp_slack.py" raw C0BPH5T1NFL 1791813257.553729
/usr/bin/python3 "$B/vp_slack.py" raw C0BPH5T1NFL 1791209268.392419
