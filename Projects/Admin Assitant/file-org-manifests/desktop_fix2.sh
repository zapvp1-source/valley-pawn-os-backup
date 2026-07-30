#!/bin/bash
D='/Users/joshuadavis/Desktop/Full Circle Finance'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
FCF="$GD/01 Business/Full Circle Finance (Valley Pawn)"

mv -n "$D/Compliance/Licensing & Permits"/* "$FCF/09 Compliance & Legal/Licensing & Permits/"
rm -f "$D/Compliance/Licensing & Permits/.DS_Store"
rmdir "$D/Compliance/Licensing & Permits"
rm -f "$D/Compliance/.DS_Store" "$D/Finance/Bookkeeping/.DS_Store" "$D/Marketing/.DS_Store" "$D/Operations/.DS_Store" "$D/Tax/.DS_Store"
rmdir "$D/Compliance" "$D/Finance/Bookkeeping" "$D/Finance" "$D/Marketing" "$D/Operations" "$D/Tax"
echo FIX2_DONE
find "$D" -mindepth 1 2>&1
exit 0
