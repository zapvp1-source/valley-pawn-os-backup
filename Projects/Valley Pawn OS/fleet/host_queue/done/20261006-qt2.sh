#!/bin/bash
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-weekly-spot-price-update.log 40
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-weekly-spot-price-update.err.log 10
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" chekkit_ai_responder/run.log 3
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" missed_call_text/run.log 3
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/retire_agent.sh" com.valleypawn.chekkitperms-oneshot --archive-logs
