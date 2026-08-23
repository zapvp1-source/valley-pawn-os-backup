#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
(
  /usr/bin/python3 publish_comedy_reels_2026-08-22.py > /tmp/comedy_publish.log 2>&1
  echo "exit=$?" >> /tmp/comedy_publish.log
  echo "DONE" >> /tmp/comedy_publish.log
) < /dev/null > /dev/null 2>&1 &
disown
exit 0
