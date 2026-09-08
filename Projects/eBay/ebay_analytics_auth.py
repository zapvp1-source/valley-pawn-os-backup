#!/usr/bin/env python3
"""Valley Pawn — analytics-scope OAuth helper.

Refresh tokens for all 5 stores were minted 2026-09-06 via the full 3-legged OAuth flow
(sell.analytics.readonly + sell.account.readonly + commerce.identity.readonly), good for
~547 days, stored at ~/.vp_secrets/ebay_analytics_oauth.json. This module exchanges a stored
refresh token for a fresh ~2hr access token on demand — nothing here ever needs a browser again
unless a refresh token itself expires (~March 2028) or is revoked.

This is SEPARATE from the Trading API IAF tokens in ~/ebay_weekly_rankings.py used by the
markdown engine, feedback replies, etc. Those are unaffected by anything in this file.

Usage as a library:
    from ebay_analytics_auth import access_token
    tok = access_token("culpeper")   # fresh REST Bearer token, good ~2hrs
"""
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
import ebay_credentials as _c  # noqa: E402

STORE_FILE = os.path.expanduser("~/.vp_secrets/ebay_analytics_oauth.json")
_cache = {}  # store -> (access_token, expires_at_epoch)


def _refresh(store):
    data = json.load(open(STORE_FILE))
    rec = data[store]
    basic = base64.b64encode(f"{_c.APP_ID}:{_c.CERT_ID}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": rec["refresh_token"],
        "scope": ("https://api.ebay.com/oauth/api_scope "
                  "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly "
                  "https://api.ebay.com/oauth/api_scope/sell.account.readonly "
                  "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly"),
    }).encode()
    req = urllib.request.Request(
        "https://api.ebay.com/identity/v1/oauth2/token",
        data=body,
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read().decode())
    return result["access_token"], time.time() + int(result.get("expires_in", 7200)) - 60


def access_token(store):
    store = store.lower()
    tok, exp = _cache.get(store, (None, 0))
    if tok and time.time() < exp:
        return tok
    tok, exp = _refresh(store)
    _cache[store] = (tok, exp)
    return tok


if __name__ == "__main__":
    for s in ("culpeper", "waynesboro", "harrisonburg", "lexington", "roanoke"):
        t = access_token(s)
        print(s, "OK", t[:16] + "...")
