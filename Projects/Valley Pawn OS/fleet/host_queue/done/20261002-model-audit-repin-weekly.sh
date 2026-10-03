#!/bin/bash
# HOST JOB — re-pin scheduled-task-model-audit-weekly after its prompt rewrite (update_scheduled_task drops the frontmatter pin)
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" scheduled-task-model-audit-weekly claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/model_pin_report.py"
