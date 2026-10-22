#!/bin/bash
# read-only: all 2025-2026 Purchases + Deposits (line-level account + class) to build store/corporate bank rules (Joshua 10/21: no splits)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Purchase WHERE TxnDate >= '2025-01-01'" purchases_2025_2026
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Deposit WHERE TxnDate >= '2025-01-01'" deposits_2025_2026
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Class" classes
