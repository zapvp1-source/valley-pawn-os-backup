#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/marketing_verify.py"
bash "$BIN/gold_silver_monthly.sh" --render
bash "$BIN/deal_of_week_pick.sh" --render
bash "$BIN/brevo_welcome.sh" --render
bash "$BIN/blog_announce.sh" --render
python3 "$BIN/agent_log_tail.py" monthly-we-buy-gold-silver-email 3
python3 "$BIN/agent_log_tail.py" vp-deal-of-week-monday-pick 3
python3 "$BIN/agent_log_tail.py" brevo-welcome-new-contacts 3
python3 "$BIN/agent_log_tail.py" blog-announce 3
bash "$BIN/host_diag.sh" agents
