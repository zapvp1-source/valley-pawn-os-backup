#!/bin/bash
cd "$(dirname "$0")"
nohup python3 sample_getitem.py > sample.log 2>&1 &
echo "STARTED_PID_$!"
