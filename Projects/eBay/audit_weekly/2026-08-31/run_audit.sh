#!/bin/bash
cd "$(dirname "$0")"
nohup python3 audit.py > run.log 2>&1 &
echo "STARTED_PID_$!"
