#!/bin/bash
D='/Users/joshuadavis/Desktop'
GD='/Users/joshuadavis/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive'
IC='/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs'
FCF="$GD/01 Business/Full Circle Finance (Valley Pawn)"
RE="$GD/02 Real Estate"
P="$IC/03 Personal"

mkdir -p "$FCF/09 Compliance & Legal/Licensing & Permits" \
  "$FCF/09 Compliance & Legal/Entity Set Up Documents" \
  "$FCF/09 Compliance & Legal/IRS Form 843 Claims (Desktop Import)" \
  "$FCF/09 Compliance & Legal/Case Files" \
  "$FCF/10 Strategy & M&A" \
  "$FCF/01 Corporate Governance/Executive (Desktop Import)" \
  "$FCF/02 Financial Records/Banking & Accounts" \
  "$FCF/02 Financial Records/Bookkeeping" \
  "$FCF/02 Financial Records/2025 Financials (Desktop Import)" \
  "$FCF/06 Operations/IT & Admin" \
  "$RE/844 Cypress Crossing Trail - FL (Home)/07 Improvements & Maintenance" \
  "$RE/844 Cypress Crossing Trail - FL (Home)/08 Photos" \
  "$RE/282 Bald Rock Rd - Verona VA (Rental)/07 Improvements & Maintenance" \
  "$RE/_Vendor Disputes & Legal (Unconfirmed Property)" \
  "$P/08 Photos" \
  "$P/06 Family" \
  "$P/07 Memberships & Travel" \
  "$GD/99 Archive/_To Trash"

FCFD="$D/Full Circle Finance"
mv -n "$FCFD/Compliance"/* "$FCF/09 Compliance & Legal/"
mv -n "$FCFD/Culpeper FFL.pdf" "$FCF/09 Compliance & Legal/Licensing & Permits/"
mv -n "$FCFD/Executive"/* "$FCF/01 Corporate Governance/Executive (Desktop Import)/"
mv -n "$FCFD/Finance"/* "$FCF/02 Financial Records/"
mv -n "$FCFD/Human Resources"/* "$FCF/03 Human Resources/"
mv -n "$FCFD/Marketing"/* "$FCF/05 Marketing & Advertising/"
mv -n "$FCFD/Operations"/* "$FCF/06 Operations/"
mv -n "$FCFD/Risk & Insurance"/* "$FCF/07 Insurance/"
mv -n "$FCFD/Strategy & M&A"/* "$FCF/10 Strategy & M&A/"
mv -n "$FCFD/Tax"/* "$FCF/02 Financial Records/"
mv -n "$FCFD/chekkit_csvs" "$FCF/06 Operations/chekkit_csvs (Desktop Import)"
mv -n "$FCFD/Real Estate/Leases" "$RE/Valley Pawn Store Leases/Leases (Desktop Import)"
mv -n "$FCFD/Real Estate/Landlord Letters of Recommendation" "$RE/Valley Pawn Store Leases/"
mv -n "$FCFD/Real Estate/Lynchburg (Location)" "$RE/Valley Pawn Store Leases/"
rmdir "$FCFD/Real Estate" 2>/dev/null
mv -n "$FCFD/_Cleanup Notes.md" "$GD/99 Archive/FCF_Desktop_Cleanup_Notes.md"
rmdir "$FCFD/_DELETE_ME (empty wrappers)" "$FCFD/_FCF Dupes (review)" 2>/dev/null
for f in "$FCFD"/~\$*; do [ -e "$f" ] && mv -n "$f" "$GD/99 Archive/_To Trash/"; done

echo STAGE1_DONE
exit 0
