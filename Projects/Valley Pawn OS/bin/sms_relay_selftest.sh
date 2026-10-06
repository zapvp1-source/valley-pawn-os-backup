#!/bin/bash
# sms_relay_selftest.sh — render-only proof that the relay can parse a real Northwest code from the
# last 7 days (prints the code masked). Nothing is written.
SMS_RELAY_MAX_AGE_MIN=10080 /usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/sms_code_relay.py" --render
