#!/bin/bash
echo "=== SKILL daily-dress-code-check ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" daily-dress-code-check 40000
echo "=== playwright / profile probe ==="
python3 -c "import playwright, sys; print('playwright', playwright.__version__)" 2>&1
ls -la "$HOME/Library/Application Support/valleypawn/" 2>&1
ls "$HOME/Library/Application Support/valleypawn/pw-cloudcover/Default/" 2>&1 | head -30
pgrep -fl "pw-cloudcover" 2>&1 | head
echo "=== vp_ai key present? ==="
security find-generic-password -s vp-agent-anthropic-key -w >/dev/null 2>&1 && echo "key: yes" || echo "key: NO"
