#!/usr/bin/env python3
"""
Publer API client for Valley Pawn.

Single source of truth for all Publer API interactions. Used by:
  - vp-content-batch (publishing path)
  - vp-social-publisher scheduled task
  - friday_close_engagement.py (Publer analytics variant)

Auth: Publer uses a custom header style: `Authorization: Bearer-API {key}`.
NOT standard OAuth Bearer.

Config files:
  - publer_config.json — { api_key, api_base, workspace_id }
  - publer_accounts.json — Valley Pawn store-key → Publer account_id mapping

Usage:
    from publer_client import PublerClient
    p = PublerClient()
    p.list_accounts()                          # all connected social accounts
    p.account_id("Brand")                      # publer id by store key
    p.schedule_post(
        text="Gold prices are up...",
        account_ids=[p.account_id("Brand"), p.account_id("BrandIG")],
        scheduled_at="2026-06-22T09:00:00",   # ISO; local time interpreted by Publer
        image_urls=["https://..."],
    )
    p.analytics(account_id="...", since="2026-06-15", until="2026-06-22")
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any, Iterable

import requests

# ----------------------- paths -----------------------

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "publer_config.json"
ACCOUNTS_PATH = ROOT / "publer_accounts.json"


# ----------------------- exceptions -----------------------

class PublerError(Exception):
    """Raised for non-2xx API responses."""


# ----------------------- client -----------------------

class PublerClient:
    """Thin wrapper around the Publer v1 API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        workspace_id: str | None = None,
        accounts: dict | None = None,
        timeout: float = 20.0,
    ):
        if CONFIG_PATH.exists():
            cfg = json.loads(CONFIG_PATH.read_text())
        else:
            cfg = {}

        self.api_key = api_key or cfg.get("api_key") or os.environ.get("PUBLER_API_KEY")
        if not self.api_key:
            raise PublerError(f"No Publer API key found in {CONFIG_PATH} or env PUBLER_API_KEY")
        self.api_base = (api_base or cfg.get("api_base", "https://app.publer.com/api/v1")).rstrip("/")
        self.workspace_id = workspace_id or cfg.get("workspace_id")

        if accounts is not None:
            self.accounts = accounts
        elif ACCOUNTS_PATH.exists():
            self.accounts = json.loads(ACCOUNTS_PATH.read_text()).get("accounts", {})
        else:
            self.accounts = {}

        self.timeout = timeout

    # --- internal HTTP ---

    def _headers(self) -> dict:
        h = {
            "Authorization": f"Bearer-API {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.workspace_id:
            h["Publer-Workspace-Id"] = self.workspace_id
        return h

    def _request(self, method: str, path: str, **kw) -> Any:
        url = f"{self.api_base}{path}"
        kw.setdefault("timeout", self.timeout)
        kw.setdefault("headers", self._headers())
        r = requests.request(method, url, **kw)
        if not r.ok:
            raise PublerError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        if r.text.strip() == "":
            return None
        return r.json()

    def get(self, path: str, **kw): return self._request("GET", path, **kw)
    def post(self, path: str, **kw): return self._request("POST", path, **kw)
    def put(self, path: str, **kw): return self._request("PUT", path, **kw)
    def delete(self, path: str, **kw): return self._request("DELETE", path, **kw)

    # --- accounts ---

    def list_accounts(self) -> list[dict]:
        """All social accounts connected to the workspace."""
        return self.get("/accounts")

    def account_id(self, store_key: str) -> str:
        """
        Map a Valley Pawn store key to the Publer account id.

        Store keys: Brand, Lexington, Roanoke, Harrisonburg, Culpeper, Waynesboro, BrandIG.
        """
        if store_key not in self.accounts:
            raise PublerError(f"Unknown store key '{store_key}'. Known: {sorted(self.accounts)}")
        return self.accounts[store_key]["publer_id"]

    def account_ids_for(self, store_keys: Iterable[str]) -> list[str]:
        return [self.account_id(k) for k in store_keys]

    # --- posts (the actual publishing path) ---

    # Map publer_accounts.json provider → Publer API "networks" key.
    _PROVIDER_TO_NETWORK = {
        "facebook": "facebook",
        "instagram": "instagram",
        "twitter": "twitter",  # X uses "twitter" in Publer API
        "tiktok": "tiktok",
        "linkedin": "linkedin",
        "youtube": "youtube",
        "pinterest": "pinterest",
        "google_business": "google",
        "wordpress_oauth": "wordpress",
        "wordpress": "wordpress",
    }

    def _account_meta(self, store_key: str) -> dict:
        """Return {publer_id, provider, network_key} for a store key."""
        if store_key not in self.accounts:
            raise PublerError(f"Unknown store key '{store_key}'. Known: {sorted(self.accounts)}")
        cfg = self.accounts[store_key]
        provider = cfg.get("provider", "facebook")
        network = self._PROVIDER_TO_NETWORK.get(provider, provider)
        return {"publer_id": cfg["publer_id"], "provider": provider, "network": network}

    def schedule_post(
        self,
        text: str,
        store_keys: list[str] | None = None,
        account_ids: list[str] | None = None,
        scheduled_at: str | None = None,
        image_urls: list[str] | None = None,
        video_url: str | None = None,
        link: str | None = None,
        immediate: bool = False,
    ) -> dict:
        """
        Schedule a single post to one or more accounts using Publer's bulk/networks API.

        Pass EITHER store_keys (preferred — auto-resolves provider) OR account_ids
        (backwards-compat — assumes facebook for unknown provider). store_keys wins
        if both supplied.

        scheduled_at: ISO 8601 with timezone (e.g. "2026-06-22T09:00:00Z" or
                      "2026-06-22T09:00:00-04:00"). Must be >=1 min in the future.
                      Ignored if immediate=True.
        immediate=True routes to /posts/schedule/publish (no scheduled_at allowed).

        Returns: {"job_id": "..."} — poll job_status() for completion.
        """
        # Resolve store_keys to account metas (provider + publer_id)
        if store_keys:
            account_metas = [self._account_meta(k) for k in store_keys]
        elif account_ids:
            # Reverse lookup — find the store key whose publer_id matches.
            id_to_key = {v["publer_id"]: k for k, v in self.accounts.items()}
            account_metas = []
            for aid in account_ids:
                key = id_to_key.get(aid)
                if key:
                    account_metas.append(self._account_meta(key))
                else:
                    # Unknown id — default to facebook network.
                    account_metas.append({"publer_id": aid, "provider": "facebook", "network": "facebook"})
        else:
            raise PublerError("schedule_post requires either store_keys or account_ids")

        # Group accounts by network so we build per-network content.
        networks: dict[str, dict] = {}
        for meta in account_metas:
            net = meta["network"]
            if net not in networks:
                # Pick content type based on media presence
                if video_url:
                    content_type = "video"
                elif image_urls:
                    content_type = "photo"
                elif link:
                    content_type = "link"
                else:
                    content_type = "status"
                networks[net] = {"type": content_type, "text": text}
                if image_urls:
                    networks[net]["media"] = [{"type": "image", "url": u} for u in image_urls]
                if video_url:
                    networks[net]["media"] = [{"type": "video", "url": video_url}]
                if link:
                    networks[net]["link"] = link

        # Build accounts array (each entry: id + optional scheduled_at)
        accounts_payload = []
        for meta in account_metas:
            entry = {"id": meta["publer_id"]}
            if scheduled_at and not immediate:
                entry["scheduled_at"] = scheduled_at
            accounts_payload.append(entry)

        body = {
            "bulk": {
                "state": "scheduled",
                "posts": [
                    {
                        "networks": networks,
                        "accounts": accounts_payload,
                    }
                ],
            }
        }

        endpoint = "/posts/schedule/publish" if immediate else "/posts/schedule"
        return self.post(endpoint, json=body)

    def job_status(self, job_id: str) -> dict:
        """Poll a Publer job status — returns {status, ...}. status in {working, completed, failed}."""
        return self.get(f"/job_status/{job_id}")

    def wait_for_job(self, job_id: str, max_seconds: int = 60, poll_interval: float = 2.0) -> dict:
        """Block until job completes or fails. Returns final status payload."""
        deadline = time.time() + max_seconds
        while time.time() < deadline:
            status = self.job_status(job_id)
            state = status.get("status") if isinstance(status, dict) else None
            if state in ("completed", "failed"):
                return status
            time.sleep(poll_interval)
        return {"status": "timeout", "job_id": job_id}

    def list_posts(self, state: str | None = None, limit: int = 100) -> list[dict]:
        """state: 'scheduled' | 'published' | 'draft' | 'failed' | None for all."""
        params = {"limit": str(limit)}
        if state:
            params["state"] = state
        data = self.get("/posts", params=params)
        if isinstance(data, dict):
            return data.get("posts", [])
        return data or []

    def delete_post(self, post_id: str) -> None:
        self.delete(f"/posts/{post_id}")

    # --- analytics (replaces direct Meta Graph API reads) ---
    # Endpoint per Publer docs: /analytics/{account_id}/post_insights
    # Returns a list of posts with per-post metrics (reach, impressions, likes,
    # comments, shares, saves, video_views, link_clicks, etc.)

    def post_insights(
        self,
        account_id: str,
        since: str | None = None,
        until: str | None = None,
        sort: str = "scheduled_at",
        limit: int = 100,
    ) -> list[dict]:
        """
        Per-post performance analytics for a single connected account.

        sort options (per Publer docs): scheduled_at, reach, engagement,
        engagement_rate, click_through_rate, reach_rate, postType, likes,
        video_views, comments, shares, saves, link_clicks, post_clicks.
        """
        params: dict[str, str] = {"sort": sort, "limit": str(limit)}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        data = self.get(f"/analytics/{account_id}/post_insights", params=params)
        if isinstance(data, dict):
            # Publer typically wraps as {posts: [...], total: N}
            return data.get("posts") or data.get("data") or []
        return data or []

    # --- convenience batch publish ---

    def schedule_brand_post(
        self,
        text: str,
        scheduled_at: str,
        image_urls: list[str] | None = None,
        include_ig: bool = True,
    ) -> dict:
        """Schedule a post that goes to Brand FB + @valley_pawn IG (default brand cross-post)."""
        keys = ["Brand"] + (["BrandIG"] if include_ig else [])
        return self.schedule_post(
            text=text,
            account_ids=self.account_ids_for(keys),
            scheduled_at=scheduled_at,
            image_urls=image_urls,
        )

    def schedule_store_post(
        self,
        store_key: str,
        text: str,
        scheduled_at: str,
        image_urls: list[str] | None = None,
    ) -> dict:
        """Schedule a store-local post (single store FB Page only)."""
        return self.schedule_post(
            text=text,
            account_ids=[self.account_id(store_key)],
            scheduled_at=scheduled_at,
            image_urls=image_urls,
        )


# ----------------------- CLI test harness -----------------------

def _cli_test():
    """python publer_client.py — quick connection + accounts sanity check."""
    p = PublerClient()
    print(f"API base: {p.api_base}")
    print(f"Workspace: {p.workspace_id}")
    print(f"Store keys in accounts map: {sorted(p.accounts.keys())}")

    print("\nLive accounts from API:")
    for a in p.list_accounts():
        print(f"  {a.get('provider','?'):10s} | {a.get('type','?'):12s} | {a.get('name','?'):30s} | id={a.get('id','?')}")

    print("\nScheduled posts (limit 5):")
    for post in p.list_posts(state="scheduled", limit=5):
        print(f"  • {post.get('scheduled_at','?')} | {post.get('text','')[:60]}")


if __name__ == "__main__":
    _cli_test()
