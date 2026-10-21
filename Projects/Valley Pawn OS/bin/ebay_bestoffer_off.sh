#!/bin/bash
# ebay_bestoffer_off.sh — host-queue wrapper for Projects/eBay/engine/ebay_bestoffer_off.py (2026-10-20 eBay audit).
# Switches Best Offer OFF only: video games (Rule 2) and the Culpeper listings our own August remediation
# turned on (Joshua yes, 2026-09-17). Dry run unless --apply is passed. Never writes BestOfferEnabled=true.
E="$HOME/Documents/Claude/Projects/eBay/engine"
exec /usr/bin/python3 "$E/ebay_bestoffer_off.py" "$@"
