#!/usr/bin/env python3
"""google_grant.py — ONE-TIME re-consent that unlocks the whole website data layer.

Why this and not a service account: `Scheduled/_shared/sheets_helper.py` records that the
fcfpawn.com Workspace org enforces `iam.disableServiceAccountKeyCreation`, so SA key downloads
are blocked. The existing pattern — authorize once AS Joshua, cache the refresh token — already
works for Sheets. This script simply re-runs that consent with two more read-only scopes added,
so nothing that works today breaks and GA4 + Search Console start working headlessly.

WHAT JOSHUA DOES (about 3 minutes, once):
  1. In the GCP project `valley-pawn-automation`, enable these two APIs (Console → APIs & Services
     → Library → search → Enable):
        • "Google Analytics Data API"
        • "Google Search Console API"
  2. Run:   python3 "/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin/google_grant.py"
  3. A browser opens. Sign in as **jdavis@fcfpawn.com** (the GA4 + Search Console account) and Allow.
That's it. The refresh token is cached at ~/.config/valley-pawn/google-oauth-token.json (mode 600)
and every native job authenticates from it forever after, with no browser and no password screen.

Safety: the existing token is backed up first, and the new grant is a SUPERSET of the old scopes,
so `email-analytics-weekly` and anything else using sheets_helper keeps working unchanged. Both new
scopes are READ-ONLY — this grant cannot modify analytics or the site.
"""
from __future__ import annotations
import json
import os
import shutil
import stat
import sys
from pathlib import Path

CFG = Path.home() / ".config" / "valley-pawn"
CLIENT_FILE = CFG / "google-oauth-client.json"
TOKEN_FILE = CFG / "google-oauth-token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",              # existing — keep (sheets_helper)
    "https://www.googleapis.com/auth/analytics.readonly",        # NEW — GA4 Data API
    "https://www.googleapis.com/auth/webmasters.readonly",       # NEW — Search Console API
]


def main() -> int:
    if not CLIENT_FILE.exists():
        print(f"ERROR: {CLIENT_FILE} not found — the OAuth client config should already be there.",
              file=sys.stderr)
        return 1
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: google-auth-oauthlib is not installed for this interpreter.\n"
              "  /usr/bin/python3 -m pip install --user google-auth-oauthlib", file=sys.stderr)
        return 1

    if TOKEN_FILE.exists():
        bak = TOKEN_FILE.with_suffix(".json.bak-pre-analytics-grant")
        shutil.copy2(TOKEN_FILE, bak)
        print(f"Backed up existing token → {bak}")

    print("Scopes being requested:")
    for s in SCOPES:
        print("  •", s)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
    print("\nOpening the browser — sign in as jdavis@fcfpawn.com and click Allow.")
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline",
                                  open_browser=True,
                                  success_message="Valley Pawn analytics access granted — you can close this tab.")
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    got = sorted(json.loads(TOKEN_FILE.read_text()).get("scopes", []))
    print("\nSaved. Scopes now on the cached token:")
    for s in got:
        print("  •", s)
    missing = [s for s in SCOPES if s not in got]
    if missing:
        print("\nWARNING — these scopes were NOT granted:", missing, file=sys.stderr)
        return 1
    print("\nNext: python3 ga4_pull.py --check   and   python3 gsc_pull.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
