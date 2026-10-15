#!/bin/bash
set +e
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.analytics-api-pull
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.guesty-pull
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/guesty_pull.py" --check
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/analytics_api_pull.sh" week
