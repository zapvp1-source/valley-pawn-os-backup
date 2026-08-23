#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
(
  /usr/bin/python3 -u _diag_video_payload.py > /tmp/diag_video.log 2>&1
  echo "exit=$?" >> /tmp/diag_video.log
  echo "DONE" >> /tmp/diag_video.log
) < /dev/null > /dev/null 2>&1 &
disown
exit 0
