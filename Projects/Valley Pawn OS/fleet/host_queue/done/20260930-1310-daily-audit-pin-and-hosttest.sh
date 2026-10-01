# daily-store-audit-digest: pin model to Sonnet (scheduled-task-models tier: templated report post) + host-side test render (writes files only, posts nothing)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" daily-store-audit-digest claude-sonnet-5
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/daily_audit_digest.py" 2026-09-29 --out "/Users/joshuadavis/Documents/Claude/Projects/Life OS/Reminders Execution 2026-09-30/daily-audit/host-test"
