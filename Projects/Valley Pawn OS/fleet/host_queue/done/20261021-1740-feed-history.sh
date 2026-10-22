#!/bin/bash
# read-only: 2025-2026 GL of every bank-feed account (memo = bank description, split = category) to derive auto-add bank rules
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF Checking 2797" 2025-01-01 2026-10-21 feedhist_WFChecking2797
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF Checking 3563" 2025-01-01 2026-10-21 feedhist_WFChecking3563
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF Checking 6507" 2025-01-01 2026-10-21 feedhist_WFChecking6507
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "WF LOC 4116" 2025-01-01 2026-10-21 feedhist_WFLOC4116
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Amex Card 3001" 2025-01-01 2026-10-21 feedhist_AmexCard3001
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Lowes for PROS" 2025-01-01 2026-10-21 feedhist_LowesforPROS
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Sales Tax Reserve Account (3861)" 2025-01-01 2026-10-21 feedhist_SalesTaxReserveAccount3861
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Delta Amex" 2025-01-01 2026-10-21 feedhist_DeltaAmex
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "BUSINESS CHECKING (-S90)" 2025-01-01 2026-10-21 feedhist_BUSINESSCHECKINGS90
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "BUSINESS MAIN SHARE SAVINGS (8-S0)" 2025-01-01 2026-10-21 feedhist_BUSINESSMAINSHARESAVINGS8S0
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/qbo_read.py" gl "Dupont Line of Credit" 2025-01-01 2026-10-21 feedhist_DupontLineofCredit
