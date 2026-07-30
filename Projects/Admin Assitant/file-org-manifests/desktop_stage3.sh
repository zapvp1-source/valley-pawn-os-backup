#!/bin/bash
set -x
D='/Users/joshuadavis/Desktop'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
IC='/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs'
FCF="$GD/01 Business/Full Circle Finance (Valley Pawn)"
RE="$GD/02 Real Estate"
P="$IC/03 Personal"
CY="$RE/844 Cypress Crossing Trail - FL (Home)"
TRASH="$GD/99 Archive/_To Trash"

mkdir -p "$GD/00 Inbox" "$IC/00 Inbox" "$TRASH" \
  "$FCF/02 Financial Records/Banking & Accounts/Wells Fargo (Desktop Import)" \
  "$FCF/02 Financial Records/Banking & Accounts/Best Egg (Desktop Import)" \
  "$FCF/02 Financial Records/Banking & Accounts/Dupont LOC (Desktop Import)" \
  "$FCF/02 Financial Records/Bookkeeping/Income Reconciliation (Desktop Import)" \
  "$FCF/02 Financial Records/Bookkeeping/QB Expenses Reconciliation (Desktop Import)" \
  "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)" \
  "$FCF/09 Compliance & Legal/Case Files/Goldchaincase" \
  "$FCF/07 Insurance/General Business Insurance (Desktop Import)" \
  "$RE/_Vendor Disputes & Legal (Unconfirmed Property)" \
  "$P/02 Taxes/Tax Transcripts (Desktop Import)" \
  "$CY/07 Improvements & Maintenance/Real Estate Improvements (Desktop Import)"

# ---- trivial cleanup ----
rm -f "$D/2/.DS_Store"; rmdir "$D/2" 2>/dev/null
rm -f "$D/Full Circle Finance/.DS_Store"; rmdir "$D/Full Circle Finance" 2>/dev/null

# ---- Real Estate Improvments -> Cypress ----
mv -n "$D/Real Estate Improvments"/* "$CY/07 Improvements & Maintenance/Real Estate Improvements (Desktop Import)/"
rmdir "$D/Real Estate Improvments" 2>/dev/null

# ---- Documents / Spreadsheets -> Inbox (bulk, needs secondary sort) ----
mkdir -p "$GD/00 Inbox/Desktop Documents Import (Needs Sorting)" "$GD/00 Inbox/Desktop Spreadsheets Import (Needs Sorting)"
mv -n "$D/Documents"/* "$GD/00 Inbox/Desktop Documents Import (Needs Sorting)/"
rmdir "$D/Documents" 2>/dev/null
mv -n "$D/Spreadsheets"/* "$GD/00 Inbox/Desktop Spreadsheets Import (Needs Sorting)/"
rmdir "$D/Spreadsheets" 2>/dev/null

# ---- Info folder -> Personal Inbox (mixed, needs secondary sort) ----
mkdir -p "$P/00 Inbox/Desktop Info Import (Needs Sorting)"
mv -n "$D/Info "/* "$P/00 Inbox/Desktop Info Import (Needs Sorting)/" 2>/dev/null
mv -n "$D/Info"/* "$P/00 Inbox/Desktop Info Import (Needs Sorting)/" 2>/dev/null
rmdir "$D/Info " "$D/Info" 2>/dev/null

# ---- Other: split real IT assets from junk ----
mkdir -p "$FCF/06 Operations/IT & Admin/Desktop Import"
for f in "Bravo.appref-ms" "Bravo.exe" "ebay_account_health.py" "ebay_daily_listings.py" "com.valleypawn.ebay-daily-listings.plist" "DSM_DS225+_90075.pat"; do
  mv -n "$D/Other/$f" "$FCF/06 Operations/IT & Admin/Desktop Import/" 2>/dev/null
done
mkdir -p "$TRASH/Other (Desktop junk & dupes)"
mv -n "$D/Other"/* "$TRASH/Other (Desktop junk & dupes)/" 2>/dev/null
rmdir "$D/Other" 2>/dev/null

# ---- Inter-4: keep fonts, pull stray PDF, trash the rest ----
mv -n "$D/Inter-4/Scheduled_Tasks_Model_Recommendations.pdf" "$FCF/06 Operations/IT & Admin/Desktop Import/Scheduled_Tasks_Model_Recommendations.pdf"
mkdir -p "$TRASH/Inter-4 (font package)"
mv -n "$D/Inter-4"/* "$TRASH/Inter-4 (font package)/" 2>/dev/null
rmdir "$D/Inter-4" 2>/dev/null

# ---- First Coast Tile web-scrape junk ----
mkdir -p "$TRASH/First Coast Tile (web scrape junk)"
mv -n "$D/First Coast Tile_files"/* "$TRASH/First Coast Tile (web scrape junk)/" 2>/dev/null
rmdir "$D/First Coast Tile_files" 2>/dev/null

# ---- Response: sensitive dispute folder, relocate INTACT, do not analyze ----
mv -n "$D/Response" "$RE/_Vendor Disputes & Legal (Unconfirmed Property)/Response (NEEDS YOUR CONFIRMATION - which property)"

# ---- Wells Fargo bank statements ----
mv -n "$D/Wells Fargo "/* "$FCF/02 Financial Records/Banking & Accounts/Wells Fargo (Desktop Import)/" 2>/dev/null
mv -n "$D/Wells Fargo"/* "$FCF/02 Financial Records/Banking & Accounts/Wells Fargo (Desktop Import)/" 2>/dev/null
rmdir "$D/Wells Fargo " "$D/Wells Fargo" 2>/dev/null

# ---- Tax and Entity Set Up: "2" is the more complete version, keep it, dedupe original ----
mv -n "$D/Tax and Entity Set Up 2"/* "$FCF/09 Compliance & Legal/Entity Set Up Documents/"
rmdir "$D/Tax and Entity Set Up 2" 2>/dev/null
mkdir -p "$TRASH/Tax and Entity Set Up (original - fully duplicated in Entity Set Up Documents)"
mv -n "$D/Tax and Entity Set Up"/* "$TRASH/Tax and Entity Set Up (original - fully duplicated in Entity Set Up Documents)/" 2>/dev/null
rmdir "$D/Tax and Entity Set Up" 2>/dev/null

# ---- Claude Income Rec ----
mv -n "$D/Claude Income Rec"/* "$FCF/02 Financial Records/Bookkeeping/Income Reconciliation (Desktop Import)/"
rmdir "$D/Claude Income Rec" 2>/dev/null

# ---- 2025 Business Financials old books ----
rm -f "$D/2025 Business Fiancials old books/.DS_Store"
mv -n "$D/2025 Business Fiancials old books"/* "$FCF/02 Financial Records/2025 Financials (Desktop Import)/"
rmdir "$D/2025 Business Fiancials old books" 2>/dev/null

# ---- General Business Insurance ----
mv -n "$D/General Business Insurance "/* "$FCF/07 Insurance/General Business Insurance (Desktop Import)/" 2>/dev/null
mv -n "$D/General Business Insurance"/* "$FCF/07 Insurance/General Business Insurance (Desktop Import)/" 2>/dev/null
rmdir "$D/General Business Insurance " "$D/General Business Insurance" 2>/dev/null

# ---- Goldchaincase (pawn dispute case) ----
mv -n "$D/Goldchaincase"/* "$FCF/09 Compliance & Legal/Case Files/Goldchaincase/"
rmdir "$D/Goldchaincase" 2>/dev/null

# ---- QB Expesnes Rec ----
rm -f "$D/QB Expesnes Rec/.DS_Store"
mv -n "$D/QB Expesnes Rec"/* "$FCF/02 Financial Records/Bookkeeping/QB Expenses Reconciliation (Desktop Import)/"
rmdir "$D/QB Expesnes Rec" 2>/dev/null

# ---- Best Egg Statements ----
rm -f "$D/Best Egg Statements/.DS_Store"
mv -n "$D/Best Egg Statements"/* "$FCF/02 Financial Records/Banking & Accounts/Best Egg (Desktop Import)/"
rmdir "$D/Best Egg Statements" 2>/dev/null

# ---- Dupont LOC statements ----
rm -f "$D/Dupont LOC statements/.DS_Store"
mv -n "$D/Dupont LOC statements"/* "$FCF/02 Financial Records/Banking & Accounts/Dupont LOC (Desktop Import)/"
rmdir "$D/Dupont LOC statements" 2>/dev/null

# ---- 843 claims + COVID submissions ----
mkdir -p "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)/843 Submissions COVID" \
  "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)/IRS Form 843 - Kwong Protective Claims"
mv -n "$D/843 Submissions COVID"/* "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)/843 Submissions COVID/"
rmdir "$D/843 Submissions COVID" 2>/dev/null
mv -n "$D/IRS Form 843 - Kwong Protective Claims"/* "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)/IRS Form 843 - Kwong Protective Claims/"
rmdir "$D/IRS Form 843 - Kwong Protective Claims" 2>/dev/null

# ---- IRS Transcripts (empty) ----
rmdir "$D/IRS Transcripts" 2>/dev/null

# ---- Tax Transcripts (personal, contains dishonored-payment + balance-owed flags) ----
mv -n "$D/Tax Transcripts"/* "$P/02 Taxes/Tax Transcripts (Desktop Import)/"
rmdir "$D/Tax Transcripts" 2>/dev/null

# ---- loose root files ----
mv -n "$D/jewelry-scrap-12v18-final.pdf" "$FCF/06 Operations/jewelry-scrap-12v18-final.pdf"
mkdir -p "$TRASH/Desktop root dupes"
mv -n "$D/EndOfMonthSpreadsheetReport.xlsx" "$TRASH/Desktop root dupes/"
mv -n "$D/Service Finance Home Depot Windows.pdf" "$TRASH/Desktop root dupes/"
mv -n "$D/Thumbs.db" "$D/desktop.ini" "$TRASH/Desktop root dupes/" 2>/dev/null
mkdir -p "$TRASH/pycache"
mv -n "$D/__pycache__"/* "$TRASH/pycache/" 2>/dev/null
rmdir "$D/__pycache__" 2>/dev/null
mkdir -p "$TRASH/Office lock files"
mv -n "$D"/~\$* "$TRASH/Office lock files/" 2>/dev/null

# ---- CRITICAL: Wells Fargo Notice of Garnishment - file it but keep name URGENT for visibility ----
mv -n "$D/Wells Fargo Notice of Garnishment.pdf" "$FCF/09 Compliance & Legal/Case Files/URGENT - Wells Fargo Notice of Garnishment.pdf"

echo STAGE3_DONE
exit 0
