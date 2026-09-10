#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
L=manifests/comedy_record_20260909.log
: > "$L"
for A in Brand Culpeper BrandIG BrandTikTok; do
  /usr/bin/python3 creative_drift.py record --format-id vid_case_walk --account "$A" --engagement 0 --reach 0 >> "$L" 2>&1
done
for A in Brand BrandIG BrandTikTok; do
  /usr/bin/python3 creative_drift.py record --format-id vid_where_it_went --account "$A" --engagement 0 --reach 0 >> "$L" 2>&1
done
echo "exit=$?" >> "$L"
