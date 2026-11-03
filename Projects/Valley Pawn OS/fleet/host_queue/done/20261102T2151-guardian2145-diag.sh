python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" scorecard
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" supply-order.log 20
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" supply-deliveries.out.log 20
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" asset-recovery.log 30
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" bravo-health-watchdog.log 20
