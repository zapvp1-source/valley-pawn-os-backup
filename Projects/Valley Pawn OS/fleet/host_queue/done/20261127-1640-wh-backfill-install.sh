# Bravo Warehouse: rebuild the warehouse on the host (no Bravo contact), then install the Sunday backfill agent.
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/wh_backfill.sh" --rebuild-only
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.wh-backfill
