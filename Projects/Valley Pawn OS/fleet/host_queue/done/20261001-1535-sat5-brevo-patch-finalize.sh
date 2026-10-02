#!/bin/bash
# HOST JOB — Culpeper & Roanoke close 5 PM Saturdays (Joshua 2026-10-01): back up + patch T11/T48 + all not-sent
# campaigns (incl. #76, #78; never sent / #52), then preflight #78 + #76, test #78 to jdavis@, verify schedules.
# #78 is auto-SUSPENDED if any check fails.
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/sat5_brevo.py" --patch --finalize
