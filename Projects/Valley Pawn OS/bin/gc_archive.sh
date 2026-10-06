#!/bin/bash
# gc_archive.sh <YYYY-MM> — copy the gift card xlsx to the Drive reports folder, showing any error.
YM="$1"; SRC="$HOME/Documents/Claude/Projects/Gift Card & Store Credit/out/$YM/gift_credit_$YM.xlsx"
D="$HOME/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/01 Business/Full Circle Finance (Valley Pawn)/08 Reports & Analysis/Gift Card & Store Credit"
ls -la "$SRC"; [ -d "$D" ] && echo "dir ok" || echo "dir test failed"
cp -vX "$SRC" "$D/" && { ls -la "$D/gift_credit_$YM.xlsx"; exit 0; }
echo "cp -X failed; trying a plain byte copy"
cat "$SRC" > "$D/gift_credit_$YM.xlsx" && ls -la "$D/gift_credit_$YM.xlsx"
