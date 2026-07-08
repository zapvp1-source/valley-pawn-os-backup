"""
One-shot OAuth setup for Valley Pawn — run this ONCE to authorize Sheets API access.

What it does:
  1. Loads the OAuth client config from ~/.config/valley-pawn/google-oauth-client.json
  2. Spins up a tiny local HTTP server (random port) and opens your browser
  3. You sign in as jdavis@fcfpawn.com and approve the Sheets scope
  4. The refresh token is saved to ~/.config/valley-pawn/google-oauth-token.json (mode 600)

After this runs successfully, every scheduled task that imports sheets_helper.py will
authenticate automatically using the cached refresh token. No further interaction needed
unless you revoke the grant.

Re-run this script only if:
  - The refresh token is revoked (Google Account → Security → Third-party access)
  - You delete the token file
  - The grant is older than 6 months and considered inactive

Usage:
  python3 google_oauth_setup.py
"""
from __future__ import annotations
import json
import os
import stat
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_FILE = Path.home() / ".config" / "valley-pawn" / "google-oauth-client.json"
TOKEN_FILE = Path.home() / ".config" / "valley-pawn" / "google-oauth-token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main() -> int:
    if not CLIENT_FILE.exists():
        print(f"ERROR: {CLIENT_FILE} not found.", file=sys.stderr)
        print("Run the GCP Console OAuth Client setup first; this file should be there.", file=sys.stderr)
        return 1

    print(f"Loading OAuth client from {CLIENT_FILE}")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)

    # run_local_server() picks a free port, opens browser, waits for OAuth redirect
    print("Opening browser for Google sign-in...")
    print("  (sign in as jdavis@fcfpawn.com and click Allow)")
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        open_browser=True,
        success_message="OAuth complete — you can close this tab.",
    )

    # Persist the credential, including refresh_token, to the token file
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)  # mode 600

    print(f"\n✅ Token saved to {TOKEN_FILE}")
    print(f"   refresh_token present: {bool(creds.refresh_token)}")
    print(f"   scopes: {creds.scopes}")
    print(f"   account: {flow.credentials.id_token if hasattr(flow.credentials, 'id_token') else '(see token file)'}")
    print()
    print("You're done. Future scheduled tasks will use this token automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
