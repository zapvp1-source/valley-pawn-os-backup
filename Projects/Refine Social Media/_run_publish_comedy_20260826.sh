#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
/usr/bin/python3 publish_comedy_reels_2026-08-26.py > reels/publish_comedy_2026-08-26.log 2>&1
echo "exit=$?" >> reels/publish_comedy_2026-08-26.log
