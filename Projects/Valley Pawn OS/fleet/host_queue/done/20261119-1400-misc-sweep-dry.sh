#!/bin/bash
# dry run of extended misc_sweep (ATM, Culpeper util, Burrell, LOC pair, Gusto debit) — Joshua 11/19 books health
cd "/Users/joshuadavis/Documents/Claude/Projects/Quickbooks Set UP" && python3 misc_sweep.py --days 15 2>&1 | grep -v Warning | grep -v warnings.warn
