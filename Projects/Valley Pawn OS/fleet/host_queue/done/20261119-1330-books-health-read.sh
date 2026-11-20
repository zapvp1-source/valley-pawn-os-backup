#!/bin/bash
# read-only: recent Gusto / LOC-advance / transfer postings to see how the sweep should treat them (Joshua 11/19 "is our bookkeeping healthy")
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Purchase WHERE TxnDate >= '2026-10-01'" purch_oct_nov
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Deposit WHERE TxnDate >= '2026-10-01'" dep_oct_nov
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM Transfer WHERE TxnDate >= '2026-10-01'" xfer_oct_nov
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" query "SELECT * FROM JournalEntry WHERE TxnDate >= '2026-10-01'" je_oct_nov
