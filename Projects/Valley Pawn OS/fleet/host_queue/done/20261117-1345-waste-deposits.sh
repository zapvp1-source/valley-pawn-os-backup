#!/bin/bash
# read-only: deposits + purchases 12m for the waste review
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Deposit WHERE TxnDate >= '2025-11-01' MAXRESULTS 1000" waste_deposits_12m
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" report TransactionList 2025-11-01 2026-11-17 waste_txnlist_12m
