#!/usr/bin/env python3
"""wp_client.py — shared WordPress REST client for thevalleypawn.com (Valley Pawn).

Replaces every Chrome-nonce / wp.apiFetch path with the Application Password that already
exists (Website/shop-build/.wp_app_credentials — WP_USER / WP_APP_PASSWORD / WP_SITE).
Stdlib only (urllib). Safe to import from any native job or Cowork task.

    from wp_client import WP
    wp = WP()
    raw = wp.get_page_raw(833)                 # content.raw via context=edit (ground truth)
    wp.update_page(833, new_content)          # POST, returns parsed JSON
    html = wp.fetch_live("/shop/")            # public page, cache-busted
    wp.wait_live("/shop/", lambda h: h.count('class="vp-card"') == 444)   # CDN lag aware

Known site facts baked in (see Website/shop-build/METHOD_NOTES.md):
  * /wp-json/wp/v2/pages/<id> POST needs Basic auth (App Password) — no nonce.
  * The a8c CDN edge can serve a stale page for 20–60 s after publish while reporting
    cache MISS. Ground truth is context=edit; live checks must retry, never fail fast.
  * WooCommerce shop-page setting MUST stay pointed at page 1110 (do not touch).
"""
from __future__ import annotations
import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Resolved relative to this file so the same code runs on the Mac (launchd / osascript) and in a
# Cowork sandbox where the Website folder is mounted under a different absolute path.
CRED_FILE = Path(__file__).resolve().parent.parent.parent / "shop-build" / ".wp_app_credentials"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


def load_credentials(path: Path = CRED_FILE) -> dict:
    creds = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip().strip('"').strip("'")
    missing = [k for k in ("WP_USER", "WP_APP_PASSWORD", "WP_SITE") if not creds.get(k)]
    if missing:
        raise RuntimeError(f"wp_client: credentials file missing {missing}")
    creds["WP_SITE"] = creds["WP_SITE"].rstrip("/")
    return creds


class WP:
    def __init__(self, cred_path: Path = CRED_FILE, timeout: int = 120):
        c = load_credentials(cred_path)
        self.site = c["WP_SITE"]
        self.timeout = timeout
        tok = base64.b64encode(f"{c['WP_USER']}:{c['WP_APP_PASSWORD']}".encode()).decode()
        self._auth = "Basic " + tok

    # ---- REST -----------------------------------------------------------
    def _req(self, path: str, method: str = "GET", data: bytes | None = None,
             headers: dict | None = None, auth: bool = True):
        url = path if path.startswith("http") else f"{self.site}/wp-json{path}"
        h = {"User-Agent": UA, "Accept": "application/json"}
        if auth:
            h["Authorization"] = self._auth
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "ignore")

    def get_json(self, path: str) -> tuple[int, dict | list | None]:
        st, body = self._req(path)
        try:
            return st, json.loads(body)
        except Exception:
            return st, None

    def get_page(self, page_id: int, fields: str = "id,modified_gmt,status,link,content") -> dict:
        st, j = self.get_json(f"/wp/v2/pages/{page_id}?context=edit&_fields={fields}")
        if st != 200 or not isinstance(j, dict):
            raise RuntimeError(f"wp_client: GET page {page_id} -> HTTP {st}")
        return j

    def get_page_raw(self, page_id: int) -> str:
        return self.get_page(page_id).get("content", {}).get("raw", "")

    def update_page(self, page_id: int, content: str, status: str = "publish") -> dict:
        payload = json.dumps({"content": content, "status": status}).encode("utf-8")
        st, body = self._req(f"/wp/v2/pages/{page_id}", method="POST", data=payload,
                             headers={"Content-Type": "application/json"})
        try:
            j = json.loads(body)
        except Exception:
            j = {"_raw": body[:500]}
        if st != 200 or j.get("id") != page_id:
            raise RuntimeError(f"wp_client: POST page {page_id} -> HTTP {st}: {str(j)[:300]}")
        return j

    def upload_media(self, data: bytes, filename: str, mime: str) -> dict:
        st, body = self._req("/wp/v2/media", method="POST", data=data, headers={
            "Content-Type": mime,
            "Content-Disposition": f'attachment; filename="{filename}"',
        })
        j = json.loads(body)
        if st != 201:
            raise RuntimeError(f"wp_client: media upload -> HTTP {st}: {str(j)[:300]}")
        return j

    # ---- Public (live) page ---------------------------------------------
    def fetch_live(self, path: str) -> str:
        sep = "&" if "?" in path else "?"
        url = f"{self.site}{path}{sep}v={int(time.time() * 1000)}"
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache",
                                                   "Pragma": "no-cache"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "ignore")

    def wait_live(self, path: str, predicate, tries: int = 9, delay: int = 20) -> tuple[bool, str]:
        """Re-fetch the public page until predicate(html) is True. Returns (ok, last_html)."""
        html = ""
        for i in range(tries):
            try:
                html = self.fetch_live(path)
                if predicate(html):
                    return True, html
            except Exception:
                pass
            if i < tries - 1:
                time.sleep(delay)
        return False, html
