#!/bin/bash
echo "=== nics-weekly-mtd log ==="
tail -n 60 "/Users/joshuadavis/Library/Logs/valleypawn/nics-weekly-mtd.log" 2>&1
echo "=== blog-announce log ==="
tail -n 40 "/Users/joshuadavis/Library/Logs/valleypawn/blog-announce.log" 2>&1
echo "=== ceo-week-pull log ==="
tail -n 40 "/Users/joshuadavis/Library/Logs/valleypawn/ceo-week-pull.log" 2>&1
echo "=== fb-inbox-replies log (if exists) ==="
tail -n 40 "/Users/joshuadavis/Library/Logs/valleypawn/fb-inbox-replies.log" 2>&1
ls "/Users/joshuadavis/Library/Logs/valleypawn/" | grep -i "fb\|facebook\|inbox"
