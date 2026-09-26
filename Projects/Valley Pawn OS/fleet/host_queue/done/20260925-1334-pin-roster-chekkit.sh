#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" roster-refresh claude-sonnet-5
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" chekkit-unanswered-alert claude-sonnet-5
