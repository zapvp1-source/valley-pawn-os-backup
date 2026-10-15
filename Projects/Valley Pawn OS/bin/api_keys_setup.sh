#!/bin/bash
# api_keys_setup.sh <guesty|talentlms|all> — one-time, hidden-entry dialogs that save vendor API keys to the
# macOS Keychain and verify each one live before keeping it (LOGINS project, 2026-10-14). Same pattern as
# chekkit_token_setup.sh. Secrets never leave the Mac and never appear in any log or file.
WHAT="${1:-all}"
ask() { osascript -e "text returned of (display dialog \"$1\" default answer \"\" $2 with title \"Valley Pawn — one-time setup\" buttons {\"Skip\",\"Save\"} default button \"Save\" giving up after 1800)" 2>/dev/null | tr -d ' \n\r'; }
say() { osascript -e "display dialog \"$1\" buttons {\"OK\"} with title \"Valley Pawn — one-time setup\" giving up after 600" >/dev/null 2>&1; }
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
if [ "$WHAT" = guesty ] || [ "$WHAT" = all ]; then
  if /usr/bin/python3 "$BIN/guesty_pull.py" --check 2>/dev/null | grep -q '^OK'; then echo "guesty: already working"; else
    ID=$(ask "Guesty (Bald Rock): in Guesty go to Integrations > Developer tools > OAuth applications > New application (name it Valley Pawn Ops). Paste the CLIENT ID here:" "")
    SEC=$(ask "Now paste the CLIENT SECRET for that same Guesty application:" "with hidden answer")
    if [ -n "$ID" ] && [ -n "$SEC" ]; then
      security add-generic-password -s vp-guesty-client-id -a "$(whoami)" -w "$ID" -U
      security add-generic-password -s vp-guesty-client-secret -a "$(whoami)" -w "$SEC" -U
      security delete-generic-password -s vp-guesty-token >/dev/null 2>&1
      R=$(/usr/bin/python3 "$BIN/guesty_pull.py" --check 2>&1 | tail -1)
      case "$R" in OK*) echo "guesty: saved + verified"; /usr/bin/python3 "$BIN/guesty_pull.py" | tail -1;;
        *) echo "guesty: REFUSED (did not verify)"; security delete-generic-password -s vp-guesty-client-secret >/dev/null 2>&1; say "That Guesty ID/secret did not work. Nothing was saved. Create a new application and tell Claude to run setup again.";; esac
    else echo "guesty: skipped"; fi
    unset ID SEC
  fi
fi
if [ "$WHAT" = talentlms ] || [ "$WHAT" = all ]; then
  K=$(ask "TalentLMS (training academy): in TalentLMS go to Account & Settings > Integrations > API, tick Enable API, then paste the API key here:" "with hidden answer")
  if [ -n "$K" ]; then
    C=$(curl -s -o /dev/null -w '%{http_code}' -u "$K:" "https://valleypawn.talentlms.com/api/v1/siteinfo")
    if [ "$C" = 200 ]; then security add-generic-password -s vp-talentlms-api-key -a "$(whoami)" -w "$K" -U; echo "talentlms: saved + verified"
    else echo "talentlms: REFUSED (HTTP $C)"; say "That TalentLMS key did not work (HTTP $C). Nothing was saved."; fi
  else echo "talentlms: skipped"; fi
  unset K
fi
