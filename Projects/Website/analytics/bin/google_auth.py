#!/usr/bin/env python3
"""google_auth.py — access tokens for the website data layer, from the cached OAuth refresh token.

Same credential the Sheets helper already uses (~/.config/valley-pawn/google-oauth-token.json).
Pure stdlib refresh (no google-auth import needed at run time) so launchd jobs stay dependency-free
and immune to the Python 3.9 deprecation warnings that pollute stdout.

    from google_auth import access_token, has_scope, GOOGLE_SETUP_HINT
    tok = access_token()          # raises NeedsGrant if the token is missing or lacks a scope
"""
from __future__ import annotations
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".config" / "valley-pawn" / "google-oauth-token.json"
ANALYTICS_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
SEARCH_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
GOOGLE_SETUP_HINT = (
    "Google access not granted yet. One-time fix: enable the Google Analytics Data API and the "
    "Google Search Console API in the valley-pawn-automation GCP project, then run "
    "`python3 Website/analytics/bin/google_grant.py` and approve as jdavis@fcfpawn.com. "
    "See Website/analytics/GOOGLE_API_SETUP.md."
)

_cache: dict = {}


class NeedsGrant(RuntimeError):
    pass


def _token_blob() -> dict:
    if not TOKEN_FILE.exists():
        raise NeedsGrant(f"{TOKEN_FILE} not found. {GOOGLE_SETUP_HINT}")
    return json.loads(TOKEN_FILE.read_text())


def scopes() -> list[str]:
    try:
        return list(_token_blob().get("scopes", []))
    except NeedsGrant:
        return []


def has_scope(scope: str) -> bool:
    return scope in scopes()


def access_token(require: str | None = None) -> str:
    blob = _token_blob()
    if require and require not in blob.get("scopes", []):
        raise NeedsGrant(f"cached token lacks scope {require}. {GOOGLE_SETUP_HINT}")
    if _cache.get("tok") and _cache.get("exp", 0) > time.time() + 60:
        return _cache["tok"]
    data = urllib.parse.urlencode({
        "client_id": blob["client_id"],
        "client_secret": blob["client_secret"],
        "refresh_token": blob["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode())
    _cache["tok"] = j["access_token"]
    _cache["exp"] = time.time() + int(j.get("expires_in", 3000))
    return _cache["tok"]


def api_post(url: str, payload: dict, scope: str) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {access_token(require=scope)}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())
