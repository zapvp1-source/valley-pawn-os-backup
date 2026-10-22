#!/bin/bash
# setup_autopay.sh — one-time, for Joshua. Stores the bank details for the State Police e-check payments in the
# macOS Keychain (never in a file) and opens the sign-in window for the VSP billing site. Run:
#   bash ~/Documents/Claude/Projects/Compliance/vsp/setup_autopay.sh
if [ "$1" = "--password" ]; then
  echo
  echo "Update the State Police billing site password (user X009686) used by the monthly payment."
  echo "Typing is hidden. Nothing is saved to a file."
  read -r -s -p "Current VSP password: " P1; echo
  read -r -s -p "Same password again: " P2; echo
  [ "$P1" = "$P2" ] || { echo "They don't match — run this again."; exit 1; }
  [ -n "$P1" ] || { echo "Empty — run this again."; exit 1; }
  security add-generic-password -U -s vp-vsp-portal-password -a "$USER" -w "$P1" || exit 1
  unset P1 P2
  echo "Saved to your Keychain. Tell Claude 'done'."
  exit 0
fi
echo
echo "VSP gun-check fee auto-pay — one-time setup"
echo "I'll ask for the bank account the fees should come out of. Typing is hidden; nothing is saved to a file."
echo
read -r -p "Name on the bank account (e.g. Full Circle Finance Inc): " NAME
read -r -s -p "Bank routing number (9 digits): " ROUTING; echo
read -r -s -p "Bank account number: " ACCT; echo
read -r -s -p "Account number again: " ACCT2; echo
if [ "$ACCT" != "$ACCT2" ]; then echo "The two account numbers don't match — run this again."; exit 1; fi
case "$ROUTING" in [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;; *) echo "Routing number should be 9 digits — run this again."; exit 1;; esac
security add-generic-password -U -s vp-vsp-ach-name    -a "$USER" -w "$NAME"    || exit 1
security add-generic-password -U -s vp-vsp-ach-routing -a "$USER" -w "$ROUTING" || exit 1
security add-generic-password -U -s vp-vsp-ach-account -a "$USER" -w "$ACCT"    || exit 1
unset ROUTING ACCT ACCT2
echo
echo "Saved to your Keychain."
echo
echo "Next: a Chrome window will open on the State Police billing site. Sign in (user X009686), let Chrome SAVE the"
echo "password when it offers, make sure you land on the Customer Search page, then quit that window with Cmd-Q."
read -r -p "Press Return to open it... " _
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_front.sh" --only vsp
echo
echo "When you've signed in and quit the window, tell Claude 'done'."
