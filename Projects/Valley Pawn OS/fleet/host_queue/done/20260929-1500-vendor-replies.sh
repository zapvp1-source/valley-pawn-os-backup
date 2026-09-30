#!/bin/bash
# HOST JOB - read-only: Brownells replies since 9/6 in any mailbox (FFL listing follow-up)
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/mail_latest_body.py" brownells --hours 600
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/mail_latest_body.py" sportsmans --hours 600
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/mail_latest_body.py" lipseys --hours 600
