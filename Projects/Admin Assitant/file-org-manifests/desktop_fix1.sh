#!/bin/bash
D='/Users/joshuadavis/Desktop/Full Circle Finance'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
FCF="$GD/01 Business/Full Circle Finance (Valley Pawn)"

mv -n "$D/Finance/Bookkeeping"/* "$FCF/02 Financial Records/Bookkeeping/"
rmdir "$D/Finance/Bookkeeping"
mv -n "$D/Operations/IT & Admin"/* "$FCF/06 Operations/IT & Admin/"
rmdir "$D/Operations/IT & Admin"
rmdir "$D/Finance" "$D/Operations" "$D/Compliance" "$D/Executive" "$D/Human Resources" "$D/Marketing" "$D/Risk & Insurance" "$D/Strategy & M&A" "$D/Tax"
echo FIX1_DONE
exit 0
