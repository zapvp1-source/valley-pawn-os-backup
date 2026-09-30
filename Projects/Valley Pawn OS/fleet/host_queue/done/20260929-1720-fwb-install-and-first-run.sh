#!/bin/bash
# HOST JOB — Forfeited-loan win-back: install the weekly native agent (Sun 12:30) and run the first pull now.
# First run skips the long 24-month directory pull (it lands Sunday) so tonight's 8:30 PM jewelry pull is not delayed.
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.forfeiture-winback
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/forfeiture_winback_weekly.sh" --no-dir
