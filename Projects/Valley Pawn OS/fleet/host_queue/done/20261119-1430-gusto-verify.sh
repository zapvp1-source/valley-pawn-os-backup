#!/bin/bash
# read-only verify Gusto 11/13 sync landed (Joshua 11/19)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM JournalEntry WHERE TxnDate >= '2026-11-10'" je_gusto_check
