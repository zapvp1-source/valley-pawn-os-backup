#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
/usr/bin/python3 vp_comedy_reel.py --spec bits_2026-08-26.json --outdir reels/ > reels/comedy_run_2026-08-26.log 2>&1
echo "exit=$?" >> reels/comedy_run_2026-08-26.log
