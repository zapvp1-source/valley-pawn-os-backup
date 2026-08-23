#!/bin/bash
cd "$HOME/Documents/Claude/Projects/Refine Social Media" || exit 1
(
  /usr/bin/python3 _probe_upload_20260822.py > /tmp/probe_upload.log 2>&1
  echo "exit=$?" >> /tmp/probe_upload.log
  echo "DONE" >> /tmp/probe_upload.log
) < /dev/null > /dev/null 2>&1 &
disown
exit 0
