bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" all
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" dress-code-check.log 40
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" conductwatch-report.log 40
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" supply-order.log 15
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py" --task daily-dress-code-check
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
