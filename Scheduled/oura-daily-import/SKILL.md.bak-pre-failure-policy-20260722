---
name: oura-daily-import
description: Pull the latest Oura Ring data into the local SQLite database each morning.
model: claude-haiku-4-5
---

Run Joshua's daily Oura Ring data import. This pulls the last few days of Oura data into a local SQLite database so it stays current.

Steps (use the Bash / workspace shell tool):

1. Locate the runner script. The oura folder lives inside Joshua's "Health Optimization" connected folder, mounted under /sessions/<id>/mnt/. Find it with:
   find /sessions/*/mnt -maxdepth 3 -name run_daily.sh -path '*oura*' 2>/dev/null | head -1

2. Run it:
   bash "<that path>"

   The script copies oura.db to local disk (SQLite can't run directly on the synced folder), runs `python3 oura_import.py --days 3` against it, checkpoints, and copies the updated oura.db back into the folder. It reads the Oura Personal Access Token from oura_token.txt next to the script. The import is idempotent — re-pulling the last 3 days never creates duplicates.

3. Confirm success: the script prints "daily import complete" at the end. If it printed that, the run succeeded.

4. Report back in ONE short line: the latest day now present in daily_readiness and the total heartrate row count. Get these by copying the db to /tmp and querying it (do NOT open the db directly on the mounted folder — that throws a disk I/O error):
   cp "<oura folder>/oura.db" /tmp/oura_check.db
   python3 -c "import sqlite3;c=sqlite3.connect('/tmp/oura_check.db');print('readiness latest:',c.execute('select max(day) from daily_readiness').fetchone()[0],'| heartrate rows:',c.execute('select count(*) from heartrate').fetchone()[0])"

If the import fails with an auth error (HTTP 401/403), it means the Oura Personal Access Token has expired or membership lapsed — tell Joshua he needs to regenerate the token at cloud.ouraring.com/personal-access-tokens and replace oura_token.txt. Do not retry repeatedly.

Keep the final message to Joshua brief — just confirm it ran and the two numbers, unless something failed.