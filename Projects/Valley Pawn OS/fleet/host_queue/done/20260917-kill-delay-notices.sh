#!/bin/bash
# HOST JOB — Phase 0.5 rollback. Disable the delay-notice line (already off in code; this reloads
# the agent) and retract the two notices the bot posted in #pawn-walks. Allow-listed scripts only.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
/usr/bin/python3 "$BIN/comms_engine.py" retract --channel C0B8WR95N31 --ts 1789659030.055009
/usr/bin/python3 "$BIN/comms_engine.py" retract --channel C0B8WR95N31 --ts 1789617465.146259
bash "$BIN/install_agent.sh" com.valleypawn.field-scorecard --restart-only
/usr/bin/python3 "$BIN/field_scorecard.py"
