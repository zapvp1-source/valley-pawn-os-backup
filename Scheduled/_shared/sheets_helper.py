"""
Valley Pawn — shared Google Sheets helper.

Authentication model: USER OAUTH (not service account).
GCP org policy iam.disableServiceAccountKeyCreation blocks SA key downloads for the
fcfpawn.com Workspace org by default. The cleaner answer — also Google's stated
recommendation — is to authorize once as Joshua and cache the refresh token.

One-time setup (already done):
  1. OAuth Client ID (Desktop) created in GCP project valley-pawn-automation
  2. Client config at ~/.config/valley-pawn/google-oauth-client.json
  3. Run google_oauth_setup.py once → cached refresh token at
     ~/.config/valley-pawn/google-oauth-token.json

Because we authenticate AS Joshua, the client inherits Joshua's Drive permissions —
no need to share each sheet with a separate service-account email. Any sheet Joshua
can edit, this helper can edit.

Public API:
  client = SheetsClient()                          # loads cached OAuth token; refreshes if expired
  rows   = client.read(sheet_id, "Sheet1!A1:Z")    # returns list-of-lists (strings)
  client.append(sheet_id, "Sheet1!A:Z", new_rows)  # append rows past the last filled row
  client.update(sheet_id, "Sheet1!A5:Z5", row)     # overwrite a specific range
  client.read_as_dicts(sheet_id, "Sheet1")         # convenience: header row → list-of-dicts
  client.upsert_by_key(sheet_id, tab, key_col, rows_as_dicts)  # update-if-exists, append-if-not

All write methods are idempotent only insofar as the caller deduplicates first.

Used by:
  - email-analytics-weekly        (writes Email Campaign Performance sheet)
  - (future)                      add yourself here
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_FILE = Path.home() / ".config" / "valley-pawn" / "google-oauth-token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsHelperError(Exception):
    """Raised when the helper hits a configuration or API problem the caller should handle."""


class SheetsClient:
    def __init__(self, token_path: Optional[Path] = None) -> None:
        token_path = token_path or TOKEN_FILE
        if not token_path.exists():
            raise SheetsHelperError(
                f"OAuth token not found at {token_path}. "
                "Run ~/Documents/Claude/Scheduled/_shared/google_oauth_setup.py once to authorize."
            )
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        # Refresh if expired (refresh tokens are long-lived; access tokens last ~1hr)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Persist the refreshed access token
                token_path.write_text(creds.to_json())
            else:
                raise SheetsHelperError(
                    "OAuth token is invalid and can't be refreshed. "
                    "Re-run google_oauth_setup.py to re-authorize."
                )
        self._creds = creds
        # cache_discovery=False suppresses a noisy warning on systems without oauth2client
        self._svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    # ---------------------- reads ----------------------

    def read(self, sheet_id: str, range_a1: str) -> List[List[str]]:
        """Return raw row data. Missing cells come back as empty strings."""
        try:
            resp = self._svc.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=range_a1, valueRenderOption="UNFORMATTED_VALUE"
            ).execute()
        except HttpError as e:
            raise SheetsHelperError(f"read failed for {sheet_id} {range_a1}: {e}") from e
        rows = resp.get("values", [])
        # Normalize: ensure every row is the length of the longest row (pad with "")
        width = max((len(r) for r in rows), default=0)
        return [list(r) + [""] * (width - len(r)) for r in rows]

    def read_as_dicts(self, sheet_id: str, tab_name: str) -> List[dict]:
        """Read an entire tab; first row is treated as the header. Returns list-of-dicts."""
        rows = self.read(sheet_id, f"{tab_name}!A:ZZ")
        if not rows:
            return []
        header, *body = rows
        return [{header[i]: (row[i] if i < len(row) else "") for i in range(len(header))} for row in body]

    # ---------------------- writes ----------------------

    def append(self, sheet_id: str, range_a1: str, rows: List[List]) -> dict:
        """Append rows past the last filled row in the given range. Returns the API response."""
        if not rows:
            return {"updatedRows": 0}
        try:
            return self._svc.spreadsheets().values().append(
                spreadsheetId=sheet_id, range=range_a1,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": rows},
            ).execute()
        except HttpError as e:
            raise SheetsHelperError(f"append failed for {sheet_id} {range_a1}: {e}") from e

    def update(self, sheet_id: str, range_a1: str, rows: List[List]) -> dict:
        """Overwrite the given range with the provided rows."""
        try:
            return self._svc.spreadsheets().values().update(
                spreadsheetId=sheet_id, range=range_a1,
                valueInputOption="USER_ENTERED",
                body={"values": rows},
            ).execute()
        except HttpError as e:
            raise SheetsHelperError(f"update failed for {sheet_id} {range_a1}: {e}") from e

    def batch_update(self, sheet_id: str, updates: List[dict]) -> dict:
        """
        Apply many range updates atomically.
        updates: [{"range": "Sheet1!A2:E2", "values": [["a","b","c","d","e"]]}, ...]
        """
        if not updates:
            return {"totalUpdatedRows": 0}
        try:
            return self._svc.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id,
                body={"valueInputOption": "USER_ENTERED", "data": updates},
            ).execute()
        except HttpError as e:
            raise SheetsHelperError(f"batch_update failed for {sheet_id}: {e}") from e

    # ---------------------- convenience ----------------------

    def upsert_by_key(
        self,
        sheet_id: str,
        tab_name: str,
        key_column: str,
        rows_as_dicts: List[dict],
    ) -> dict:
        """
        Read the tab, find each incoming dict's row by key_column, update if present,
        append if not. Header row determines column order.

        Returns: {"updated": N, "appended": M}
        """
        existing = self.read(sheet_id, f"{tab_name}!A:ZZ")
        if not existing:
            raise SheetsHelperError(f"Tab {tab_name!r} appears empty (no header row).")
        header = existing[0]
        if key_column not in header:
            raise SheetsHelperError(f"key_column {key_column!r} not in header {header}")
        key_idx = header.index(key_column)

        # Map existing keys to row numbers (1-indexed in the sheet, header is row 1).
        # Coerce both sides to str: unformatted-read returns ints for numeric columns,
        # while caller dicts often have ints too — but the lookup below uses str(d[key]).
        existing_keys = {
            str(row[key_idx]): i + 2
            for i, row in enumerate(existing[1:])
            if len(row) > key_idx and row[key_idx] not in ("", None)
        }

        updates: List[dict] = []
        new_rows: List[List] = []
        appended = 0

        for d in rows_as_dicts:
            key = str(d.get(key_column, ""))
            if not key:
                continue
            row_values = [d.get(col, "") for col in header]
            if key in existing_keys:
                row_num = existing_keys[key]
                updates.append({
                    "range": f"{tab_name}!A{row_num}:{_col_letter(len(header))}{row_num}",
                    "values": [row_values],
                })
            else:
                new_rows.append(row_values)
                appended += 1

        if updates:
            self.batch_update(sheet_id, updates)
        if new_rows:
            self.append(sheet_id, f"{tab_name}!A:A", new_rows)

        return {"updated": len(updates), "appended": appended}


def _col_letter(n: int) -> str:
    """1 -> A, 26 -> Z, 27 -> AA, 52 -> AZ, 53 -> BA, etc."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


# ---------------------- CLI smoke test ----------------------
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="sheets_helper.py smoke test")
    p.add_argument("sheet_id", help="Google Sheet ID to probe")
    p.add_argument("--tab", default="Sheet1", help="Tab name to read")
    args = p.parse_args()

    c = SheetsClient()
    print(f"Authenticated as Joshua via cached OAuth token at {TOKEN_FILE}")
    rows = c.read(args.sheet_id, f"{args.tab}!A1:Z5")
    print(f"First 5 rows of {args.tab}:")
    for r in rows:
        print(" ", r)
