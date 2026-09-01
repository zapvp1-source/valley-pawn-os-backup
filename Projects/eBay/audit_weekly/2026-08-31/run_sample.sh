#!/bin/bash
cd "$(dirname "$0")"
python3 -m py_compile sample_getitem.py
nohup python3 sample_getitem.py > sample.log 2>&1 &
echo "STARTED_PID_$!"
