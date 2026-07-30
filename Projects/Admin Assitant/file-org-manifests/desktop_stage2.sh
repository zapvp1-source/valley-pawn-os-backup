#!/bin/bash
D='/Users/joshuadavis/Desktop'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
IC='/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs'
FCF="$GD/01 Business/Full Circle Finance (Valley Pawn)"
RE="$GD/02 Real Estate"
P="$IC/03 Personal"
CY="$RE/844 Cypress Crossing Trail - FL (Home)"
BR="$RE/282 Bald Rock Rd - Verona VA (Rental)"

# ---- Airbnb MGMT -> Bald Rock ----
mkdir -p "$BR/Airbnb MGMT (Desktop Import)"
mv -n "$D/Airbnb MGMT"/* "$BR/Airbnb MGMT (Desktop Import)/"
rm -f "$D/Airbnb MGMT/.DS_Store"
rmdir "$D/Airbnb MGMT" 2>/dev/null

# ---- Real Estate Improvments -> split by property ----
RI="$D/Real Estate Improvments"
mkdir -p "$CY/07 Improvements & Maintenance" "$BR/07 Improvements & Maintenance"
mv -n "$RI/282 CAP GAIN Improvements" "$BR/07 Improvements & Maintenance/"
for sub in "844 Cap Gain Improvemnts" "844 Remodel" "Casings and Moldings" "Mudroom" "Pool Project" "Home Depot Quote"; do
  mv -n "$RI/$sub" "$CY/07 Improvements & Maintenance/"
done
mv -n "$RI/Building Permits Extension.docx" "$CY/07 Improvements & Maintenance/"
rmdir "$RI/14300 Cap Gains" 2>/dev/null
rm -f "$RI/.DS_Store"
rmdir "$RI" 2>/dev/null

# ---- 844 Cypress cluster ----
mv -n "$D/Anchient City" "$CY/07 Improvements & Maintenance/"
mv -n "$D/Pool Spec" "$CY/07 Improvements & Maintenance/"
mv -n "$D/Bathroom" "$CY/07 Improvements & Maintenance/"
mv -n "$D/Green Nest" "$CY/07 Improvements & Maintenance/"
mv -n "$D/appliances" "$CY/07 Improvements & Maintenance/"
mv -n "$D/untitled folder" "$CY/07 Improvements & Maintenance/Florida Contracts & Disclosures"
mv -n "$D/844 pics"/* "$CY/08 Photos/"
rm -f "$D/844 pics/.DS_Store"
rmdir "$D/844 pics" 2>/dev/null
mv -n "$D/Plans (dragged).pdf" "$CY/07 Improvements & Maintenance/Plans (dragged).pdf"
mv -n "$D/Plans (dragged) 2.pdf" "$CY/07 Improvements & Maintenance/Plans (dragged) 2.pdf"
mv -n "$D/148 Home Insurance" "$RE/148 Hardinberry Street/Insurance (empty - Desktop placeholder)" 2>/dev/null
rmdir "$D/148 Home Insurance" 2>/dev/null

# ---- Health record exports -> Personal Health ----
mkdir -p "$P/03 Health/MyChart Exports"
for f in "1" "2" "3" "2021-2022" "2023" "2024" "2025-2026"; do
  mkdir -p "$P/03 Health/MyChart Exports/$f"
  mv -n "$D/$f"/* "$P/03 Health/MyChart Exports/$f/"
  rmdir "$D/$f" 2>/dev/null
done
mv -n "$D/my chart" "$P/03 Health/my chart (old)"

# ---- Personal misc ----
mv -n "$D/Sav Taxes" "$P/06 Family/Savannah Taxes"
mv -n "$D/2025 Taxes"/* "$P/02 Taxes/2025/"
rmdir "$D/2025 Taxes" 2>/dev/null
mv -n "$D/Sandals"/* "$P/07 Memberships & Travel/"
rmdir "$D/Sandals" 2>/dev/null
mkdir -p "$P/08 Photos/Desktop Photos Import" "$P/08 Photos/Videos" "$P/08 Photos/Tim Court"
mv -n "$D/Photos"/* "$P/08 Photos/Desktop Photos Import/"
rmdir "$D/Photos" 2>/dev/null
mv -n "$D/Videos"/* "$P/08 Photos/Videos/"
rmdir "$D/Videos" 2>/dev/null
mv -n "$D/Tim Court"/* "$P/08 Photos/Tim Court/"
rmdir "$D/Tim Court" 2>/dev/null
rmdir "$D/Mad Taxes" 2>/dev/null
rmdir "$D/email by Store" 2>/dev/null

echo STAGE2_DONE
exit 0
