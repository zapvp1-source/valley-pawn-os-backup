#!/bin/bash
D='/Users/joshuadavis/Desktop'
IC='/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
P="$IC/03 Personal"
TRASH="$GD/99 Archive/_To Trash"

mv -n "$D/Sandals/Davis - Sandals and Beaches Credit Night Voucher.pdf" "$P/07 Memberships & Travel/"
rm -f "$D/Sandals/.DS_Store"; rmdir "$D/Sandals" 2>/dev/null

rm -f "$D/Info /.DS_Store"; rmdir "$D/Info " 2>/dev/null
rm -f "$D/Tax and Entity Set Up 2/.DS_Store"; rmdir "$D/Tax and Entity Set Up 2" 2>/dev/null
rm -f "$D/Tim Court/.DS_Store"; rmdir "$D/Tim Court" 2>/dev/null

mkdir -p "$TRASH/RECYCLE.BIN (windows artifact)"
mv -n "$D/\$RECYCLE.BIN"/* "$TRASH/RECYCLE.BIN (windows artifact)/" 2>/dev/null
rmdir "$D/\$RECYCLE.BIN" 2>/dev/null

echo FINAL_CLEANUP_DONE
ls -la "$D"
exit 0
