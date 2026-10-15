#!/bin/bash
# analytics_api_pull.sh [check|daily|week] — headless GA4 + Search Console pull (LOGINS project 2026-10-14).
# Replaces Chrome scraping of the GA4 / Search Console web UI. Writes JSON under Website/analytics/data and
# mirrors the latest files to Google Drive (Valley Pawn Data/analytics) so cloud tasks read them with the
# Drive connector — no browser, no Google sign-in.
MODE="${1:-daily}"
A="$HOME/Documents/Claude/Projects/Website/analytics"
OUT="$HOME/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/Valley Pawn Data/analytics"
mkdir -p "$OUT"
case "$MODE" in
  check) /usr/bin/python3 "$A/bin/ga4_pull.py" --check; echo "ga4 rc=$?"; /usr/bin/python3 "$A/bin/gsc_pull.py" --check; echo "gsc rc=$?";;
  daily) /usr/bin/python3 "$A/bin/ga4_pull.py" --windows; echo "ga4 windows rc=$?"
         if [ "$(date +%u)" = 1 ]; then /usr/bin/python3 "$A/bin/ga4_pull.py" --week; echo "ga4 week rc=$?"; /usr/bin/python3 "$A/bin/gsc_pull.py" --week; echo "gsc week rc=$?"; fi;;
  week)  /usr/bin/python3 "$A/bin/ga4_pull.py" --week; echo "ga4 week rc=$?"; /usr/bin/python3 "$A/bin/gsc_pull.py" --week; echo "gsc week rc=$?";;
esac
# Drive copies are prefixed by source so GA4 and Search Console files never overwrite each other.
[ -f "$A/data/ga4/week_latest.json" ] && cp -f "$A/data/ga4/week_latest.json" "$OUT/ga4_week_latest.json"
W=$(ls -t "$A"/data/ga4/windows_*.json 2>/dev/null | head -1); [ -n "$W" ] && cp -f "$W" "$OUT/ga4_windows_latest.json"
G=$(ls -t "$A"/data/gsc/week_*.json 2>/dev/null | grep -v latest | head -1); [ -n "$G" ] && cp -f "$G" "$OUT/gsc_week_latest.json"
rm -f "$OUT/week_latest.json" "$OUT/windows_latest.json" "$OUT/gsc_latest.json"
ls -la "$OUT"
