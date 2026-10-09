#!/bin/bash
# HOST JOB — read-only: last lines of the forfeiture win-back agent log (verify Sunday build + Tuesday email schedule)
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" forfeiture-winback.log 40
