#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
MODE="$1"
if [ "$MODE" = "dry" ]; then
  /usr/bin/python3 vp_deal_reel_publish.py --plan manifests/comedy_reels_2026-09-09.json --dry-run \
    > manifests/comedy_publish_20260909_dry.log 2>&1
  echo "exit=$?" >> manifests/comedy_publish_20260909_dry.log
  touch manifests/comedy_publish_20260909_dry.done
else
  /usr/bin/python3 vp_deal_reel_publish.py --plan manifests/comedy_reels_2026-09-09.json \
    > manifests/comedy_publish_20260909.log 2>&1
  echo "exit=$?" >> manifests/comedy_publish_20260909.log
  touch manifests/comedy_publish_20260909.done
fi
