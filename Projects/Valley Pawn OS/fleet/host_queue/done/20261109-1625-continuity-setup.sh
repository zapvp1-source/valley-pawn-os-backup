#!/bin/bash
OS="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS"
echo "== vp_ai auto (Claude path) =="
python3 "$OS/bin/vp_ai.py" --selftest
echo "== vp_ai local engine =="
python3 "$OS/bin/vp_ai.py" --selftest --local
echo "== continuity selftest =="
python3 "$OS/bin/continuity_selftest.py" --quiet-ledger
echo "== github last commit =="
python3 "$OS/bin/backup_repo_tool.py" last-commit
echo "== install weekly agent =="
bash "$OS/bin/install_agent.sh" com.valleypawn.continuity-selftest
echo done
