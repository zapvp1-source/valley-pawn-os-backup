#!/bin/bash
B="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction"
echo "=== latest range-run log ==="
f=$(ls -t "$B"/logs/intake-detail-range* 2>/dev/null | head -1)
echo "$(basename "$f")"
egrep 'Running intake-detail|select saved report|override Start|override End|click Ok|walk grid|no DataItems|rows_written|count_from_title|SUCCESS|Run complete' "$f" 2>/dev/null | tail -16
echo "=== WAY 7-day intake-detail CSV ==="
c="$B/output/2026-06-04_to_2026-06-10_WAY_intake-detail.csv"
if [ -e "$c" ]; then
  echo "$(wc -l < "$c") lines"
  echo "HEADER: $(head -1 "$c")"
  echo "ROW2:   $(sed -n '2p' "$c")"
  echo "ROW3:   $(sed -n '3p' "$c")"
else
  echo "not written yet"
fi
echo "=== result.json for range ==="
cat "$B"/results/intake-detail-range*.result.json 2>/dev/null | head -30 || echo "no result yet"
