#!/bin/bash
# HOST JOB — 2026-10-02 model audit: pin the 14 enabled-but-UNPINNED tasks (they were running on the app default)
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" chekkit-smart-replies-weekly-check claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" entity-compliance-check claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" fortis-email-monitor claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" gun-safety-cert-followup-20261015 claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" jewelry-sourcing-refresh-oneshot-20261004 claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" mobilepawn-app-social-monthly claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" mobilepawn-bravo-reply-check claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" roanoke-culpeper-hours-listing-check-oneshot-20261005 claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" scrap-bucket-name-check claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" scrap-monthly-bravo-approval-watch claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" scrap-monthly-bravo-manifest-stage claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" tuesday-supply-prep claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" vp-hiring-pipeline claude-sonnet-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/pin_task_model.py" nrf-riseup-approval-watch claude-haiku-4-5
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/model_pin_report.py"
