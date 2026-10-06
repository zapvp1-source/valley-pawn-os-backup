#!/bin/bash
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_token_refresh.sh" --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" qbo-api-token-refresh.log 4
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.online-store-audit
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.qbo-token-refresh
