#!/usr/bin/env python3
"""google_regrant.py — ONE Google consent that gives the Mac's fleet token every read scope it needs.

Built 2026-10-14 (Google re-grant prep). Stdlib only (no google-auth / oauthlib needed).

    google_regrant.py --dry-run     # checks everything, prints the consent URL, opens NOTHING, writes NOTHING
    google_regrant.py --grant       # opens the consent page in the default browser, waits for Allow,
                                    #   backs up the old token, verifies, then saves the new one
    google_regrant.py --verify      # live check of the CURRENT token: real scopes + one call per API

Scopes requested (union; all read-only except spreadsheets, which Sheets jobs already have):
    spreadsheets, analytics.readonly, webmasters.readonly, gmail.readonly, drive.readonly, calendar.readonly

Safety rules:
  * The old token is copied to google-oauth-token.json.bak-pre-regrant-<stamp> BEFORE anything else.
  * The new token is written only if Google returns a refresh token AND it still carries
    `spreadsheets` AND a live Sheets read of the email-analytics sheet succeeds with it.
    Otherwise the old token file is left exactly as it was (Sheets users never break).
  * Real scopes are read from Google's refresh response, never from the file's "scopes" field
    (Scheduled/_shared/sheets_helper.py rewrites that field to its own scope list on every refresh).
  * No secret is ever printed; the consent URL contains only the public client id.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import http.server
import json
import os
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CFG = Path.home() / ".config" / "valley-pawn"
CLIENT_FILE = CFG / "google-oauth-client.json"
TOKEN_FILE = CFG / "google-oauth-token.json"
LOG = Path.home() / "Library" / "Logs" / "valleypawn" / "google-regrant.log"
ACCOUNT = "jdavis@fcfpawn.com"
G = "https://www.googleapis.com/auth/"
SCOPES = [G + "spreadsheets", G + "analytics.readonly", G + "webmasters.readonly",
          G + "gmail.readonly", G + "drive.readonly", G + "calendar.readonly"]
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
# A sheet the Sheets jobs already read (email-analytics-weekly) — used as the "Sheets still works" proof.
PROOF_SHEET = "1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o"
PROBES = {  # scope -> (label, GET url, API name for the enable link)
    G + "spreadsheets": ("Sheets", f"https://sheets.googleapis.com/v4/spreadsheets/{PROOF_SHEET}?fields=properties.title", "sheets.googleapis.com"),
    G + "analytics.readonly": ("GA4", "https://analyticsdata.googleapis.com/v1beta/properties/353209303/metadata", "analyticsdata.googleapis.com"),
    G + "webmasters.readonly": ("Search Console", "https://www.googleapis.com/webmasters/v3/sites", "searchconsole.googleapis.com"),
    G + "gmail.readonly": ("Gmail", "https://gmail.googleapis.com/gmail/v1/users/me/profile", "gmail.googleapis.com"),
    G + "drive.readonly": ("Drive", "https://www.googleapis.com/drive/v3/about?fields=user(emailAddress)", "drive.googleapis.com"),
    G + "calendar.readonly": ("Calendar", "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=1", "calendar-json.googleapis.com"),
}


def log(msg: str) -> None:
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(msg)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def client() -> dict:
    d = json.loads(CLIENT_FILE.read_text())
    kind = "installed" if "installed" in d else ("web" if "web" in d else "?")
    c = d.get(kind, {})
    c["_kind"] = kind
    return c


def post_form(url: str, fields: dict) -> dict:
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(), method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            j = json.loads(body)
        except ValueError:
            j = {"error": f"http {e.code}", "error_description": body[:200]}
        j["_http"] = e.code
        return j


def refresh(c: dict, refresh_token: str) -> dict:
    return post_form(TOKEN_URL, {"client_id": c["client_id"], "client_secret": c.get("client_secret", ""),
                                 "refresh_token": refresh_token, "grant_type": "refresh_token"})


def probe(access_token: str, scope: str) -> str:
    label, url, api = PROBES[scope]
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
            return "OK"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        reason = ""
        try:
            err = json.loads(body).get("error", {})
            reason = err.get("status", "") or ""
            for det in err.get("details", []) or []:
                reason = det.get("reason") or reason
            msg = (err.get("message") or "")[:120]
        except ValueError:
            msg = body[:120]
        if "SERVICE_DISABLED" in body or "has not been used" in body or "is disabled" in body:
            return f"API NOT ENABLED in the GCP project — enable https://console.cloud.google.com/apis/library/{api}"
        if e.code == 403 and ("insufficient" in body.lower() or "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in body):
            return "no scope (needs the re-grant)"
        return f"HTTP {e.code} {reason} {msg}".strip()
    except Exception as e:  # network etc.
        return f"{type(e).__name__}: {e}"


def live_status(c: dict, refresh_token: str) -> tuple[list[str], dict]:
    j = refresh(c, refresh_token)
    if "access_token" not in j:
        return [], {"_refresh": f"refresh failed: {j.get('error')} {j.get('error_description','')[:120]}"}
    have = (j.get("scope") or "").split()
    res = {}
    for s in SCOPES:
        r = probe(j["access_token"], s)
        if s not in have and r.startswith(("OK", "HTTP 403", "no scope")):
            r = "no scope (needs the re-grant)"
        res[s] = r
    return have, res


def print_status(have: list[str], res: dict) -> None:
    if "_refresh" in res:
        log("  " + res["_refresh"])
        return
    for s in SCOPES:
        log(f"  {PROBES[s][0]:<15} {'granted' if s in have else 'MISSING':<8} -> {res[s]}")
    extra = [s for s in have if s not in SCOPES]
    if extra:
        log("  other scopes on token: " + ", ".join(extra))


def pkce() -> tuple[str, str]:
    v = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    ch = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    return v, ch


def consent_url(c: dict, redirect: str, state: str, challenge: str) -> str:
    q = {"client_id": c["client_id"], "redirect_uri": redirect, "response_type": "code",
         "scope": " ".join(SCOPES), "access_type": "offline", "prompt": "consent",
         "include_granted_scopes": "true", "login_hint": ACCOUNT, "state": state,
         "code_challenge": challenge, "code_challenge_method": "S256"}
    return AUTH_URL + "?" + urllib.parse.urlencode(q)


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def preflight() -> tuple[dict, dict | None]:
    ok = True
    if not CLIENT_FILE.exists():
        log(f"FAIL: OAuth client file missing: {CLIENT_FILE}")
        sys.exit(1)
    c = client()
    log(f"OAuth client: {CLIENT_FILE} (type={c['_kind']}, project={c.get('project_id','?')}, "
        f"client_id ...{c.get('client_id','')[-28:]})")
    if c["_kind"] != "installed":
        log("WARN: client is not a Desktop ('installed') client — loopback redirect may be refused.")
    tok = None
    if TOKEN_FILE.exists():
        tok = json.loads(TOKEN_FILE.read_text())
        log(f"Current token: {TOKEN_FILE} (refresh token present: {bool(tok.get('refresh_token'))}; "
            f"file 'scopes' field says {len(tok.get('scopes') or [])} scope(s) — not trusted)")
    else:
        log("Current token: none")
    return c, tok


def do_verify() -> int:
    c, tok = preflight()
    if not tok or not tok.get("refresh_token"):
        log("No refresh token to verify.")
        return 1
    have, res = live_status(c, tok["refresh_token"])
    log("Live status of the CURRENT token:")
    print_status(have, res)
    return 0 if all(res.get(s) == "OK" for s in SCOPES) else 3


def do_dry_run() -> int:
    c, tok = preflight()
    if tok and tok.get("refresh_token"):
        have, res = live_status(c, tok["refresh_token"])
        log("Live status of the CURRENT token (before re-grant):")
        print_status(have, res)
    port = free_port()
    redirect = f"http://127.0.0.1:{port}/"
    srv = http.server.HTTPServer(("127.0.0.1", port), http.server.BaseHTTPRequestHandler)
    srv.server_close()
    log(f"Loopback listener test: 127.0.0.1:{port} bind OK")
    v, ch = pkce()
    url = consent_url(c, redirect, secrets.token_urlsafe(16), ch)
    log("Consent URL that --grant would open (port changes each run):")
    log(url)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="GET"), timeout=20) as r:
            body = r.read().decode(errors="replace")
            bad = "Error 400" in body or "invalid_request" in body or "invalid_client" in body
            log(f"Consent page fetch: HTTP {r.status}{' — Google returned an ERROR page' if bad else ' (sign-in/consent page served)'}")
    except urllib.error.HTTPError as e:
        log(f"Consent page fetch: HTTP {e.code} — {e.read().decode(errors='replace')[:200]}")
    except Exception as e:
        log(f"Consent page fetch: {type(e).__name__}: {e}")
    log("DRY RUN — nothing opened, nothing written.")
    return 0


class _H(http.server.BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" not in q and "error" not in q:
            self.send_response(404)
            self.end_headers()
            return
        _H.result = {k: v[0] for k, v in q.items()}
        ok = "code" in q
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = ("Valley Pawn: Google access approved. You can close this tab."
               if ok else "Valley Pawn: Google access was NOT approved. Nothing changed. You can close this tab.")
        self.wfile.write(f"<html><body style='font:20px -apple-system;padding:40px'>{msg}</body></html>".encode())

    def log_message(self, *a):
        pass


def do_grant(timeout_s: int = 900) -> int:
    c, tok = preflight()
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = None
    if TOKEN_FILE.exists():
        backup = TOKEN_FILE.with_name(f"google-oauth-token.json.bak-pre-regrant-{stamp}")
        shutil.copy2(TOKEN_FILE, backup)
        os.chmod(backup, stat.S_IRUSR | stat.S_IWUSR)
        log(f"Backed up current token -> {backup}")
    port = free_port()
    redirect = f"http://127.0.0.1:{port}/"
    srv = http.server.HTTPServer(("127.0.0.1", port), _H)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    state = secrets.token_urlsafe(16)
    verifier, challenge = pkce()
    url = consent_url(c, redirect, state, challenge)
    log(f"Opening the Google consent page in the default browser (sign in as {ACCOUNT}, click Allow)...")
    subprocess.run(["/usr/bin/open", url], check=False)
    t0 = time.time()
    while not _H.result and time.time() - t0 < timeout_s:
        time.sleep(1)
    srv.shutdown()
    r = _H.result
    if not r:
        log(f"TIMED OUT after {timeout_s // 60} min with no answer. Old token untouched.")
        return 4
    if r.get("state") != state:
        log("REFUSED: state mismatch. Old token untouched.")
        return 5
    if "error" in r:
        log(f"Google said: {r['error']}. Old token untouched.")
        return 6
    j = post_form(TOKEN_URL, {"client_id": c["client_id"], "client_secret": c.get("client_secret", ""),
                              "code": r["code"], "code_verifier": verifier, "grant_type": "authorization_code",
                              "redirect_uri": redirect})
    if "refresh_token" not in j:
        log(f"No refresh token returned ({j.get('error','')} {j.get('error_description','')[:120]}). Old token untouched.")
        return 7
    have, res = live_status(c, j["refresh_token"])
    log("Live status of the NEW token:")
    print_status(have, res)
    if G + "spreadsheets" not in have or res.get(G + "spreadsheets") != "OK":
        log("REFUSED to save: the new token cannot read Sheets. Old token untouched (Sheets jobs keep working).")
        return 8
    new = {
        "token": j.get("access_token"), "refresh_token": j["refresh_token"], "token_uri": TOKEN_URL,
        "client_id": c["client_id"], "client_secret": c.get("client_secret", ""), "scopes": have,
        "universe_domain": "googleapis.com", "account": "",
        "expiry": (dt.datetime.utcnow() + dt.timedelta(seconds=int(j.get("expires_in", 3000)))).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    if tok:  # keep any extra fields other tools rely on
        for k, v in tok.items():
            new.setdefault(k, v)
    tmp = TOKEN_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(new))
    os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
    os.replace(tmp, TOKEN_FILE)
    log(f"SAVED new token -> {TOKEN_FILE} (backup: {backup})")
    missing = [PROBES[s][0] for s in SCOPES if res.get(s) != "OK"]
    if missing:
        log("Saved, but not everything works yet: " + ", ".join(missing) + " (see lines above).")
        return 3
    log("ALL SIX GOOGLE SERVICES OK.")
    return 0


def main() -> int:
    a = sys.argv[1:] or ["--dry-run"]
    if "--grant" in a:
        return do_grant()
    if "--verify" in a:
        return do_verify()
    return do_dry_run()


if __name__ == "__main__":
    sys.exit(main())
