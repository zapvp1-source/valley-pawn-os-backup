#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/google_token_scopes.py"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" "$HOME/.config/valley-pawn"
