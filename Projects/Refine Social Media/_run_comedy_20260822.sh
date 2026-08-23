#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
(
  /usr/bin/python3 vp_comedy_reel.py --spec bits_2026-08-22.json --outdir reels/ > /tmp/comedy_render.log 2>&1
  echo "exit=$?" >> /tmp/comedy_render.log
  echo "DONE" >> /tmp/comedy_render.log
) < /dev/null > /dev/null 2>&1 &
disown
exit 0
