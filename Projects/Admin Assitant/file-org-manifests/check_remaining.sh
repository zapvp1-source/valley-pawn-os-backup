#!/bin/bash
cd /Users/joshuadavis/Desktop
for d in "Info " "Sandals" "Tax and Entity Set Up 2" "Tim Court" '$RECYCLE.BIN'; do
  echo "=== $d ==="
  find "$d" 2>&1
done
