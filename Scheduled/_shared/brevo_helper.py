"""
Valley Pawn — shared Brevo API helper.

Setup:
  - Brevo Standard plan (verified 2026-05-27)
  - API key at ~/.config/valley-pawn/brevo_api_key (mode 600)
  - IP allowlist for API keys: DEACTIVATED (residential IPv6 rotates faster than allowlists
    can keep up; the key file is the security boundary)

Hard limitations to remember:
  - tel: and sms: clicks are NOT trackable by Brevo. They bypass Brevo's tracking redirect
    (which only handles HTTP/HTTPS). To measure Call/Text clicks, wrap them in HTTP redirects
    on thevalleypawn.com (/c/<store> and /t/<store>). Until those redirects ship, calls_clicks
    and texts_clicks in the analytics sheet stay blank.
  - HTTP/HTTPS links (Maps Directions, primary CTA, homepage, Instagram) ARE fully trackable.

Used by:
  - email-analytics-weekly        (pulls campaign list + per-link click stats)
  - (future)                      add yourself here
"""
from __future__ import annotations
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

API_KEY_FILE = Path.home() / ".config" / "valley-pawn" / "brevo_api_key"
API_BASE = "https://api.brevo.com/v3"
DEFAULT_TIMEOUT = 20  # seconds


class BrevoError(Exception):
    """Raised when Brevo returns a non-2xx response or the API key is missing."""


class BrevoClient:
    def __init__(self, key_path: Optional[Path] = None) -> None:
        key_path = key_path or API_KEY_FILE
        if not key_path.exists():
            raise BrevoError(
                f"Brevo API key not found at {key_path}. "
                "See valley-pawn-context.md → Email-program tech stack → Brevo for setup."
            )
        self._key = key_path.read_text().strip()
        if not self._key.startswith("xkeysib-"):
            raise BrevoError(f"Key in {key_path} doesn't start with 'xkeysib-' — wrong format")

    # ---------------------- low-level HTTP ----------------------

    def _call(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = API_BASE + path
        if params:
            url += "?" + urlencode(params)
        req = urllib.request.Request(
            url,
            headers={
                "accept": "application/json",
                "api-key": self._key,
                "user-agent": "valley-pawn-brevo-helper/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise BrevoError(f"HTTP {e.code} from {path}: {body[:400]}") from None
        except urllib.error.URLError as e:
            raise BrevoError(f"Network error calling {path}: {e}") from e

    # ---------------------- account / health ----------------------

    def account(self) -> Dict[str, Any]:
        """Returns account info — useful for verifying the API key works and the plan tier."""
        return self._call("/account")

    # ---------------------- campaigns ----------------------

    # Brevo caps /emailCampaigns at 100 per page (verified 2026-05-27 via HTTP 400 "out_of_range").
    _CAMPAIGNS_MAX_PER_PAGE = 100

    def list_email_campaigns(
        self,
        status: Optional[str] = None,  # "sent", "draft", "scheduled", "archive", "queued", "suspended"
        offset: int = 0,
        sort: str = "desc",
    ) -> List[Dict[str, Any]]:
        """Paginates through all campaigns matching the filter. Returns combined list."""
        out: List[Dict[str, Any]] = []
        page_size = self._CAMPAIGNS_MAX_PER_PAGE
        while True:
            params: Dict[str, Any] = {"limit": page_size, "offset": offset, "sort": sort}
            if status:
                params["status"] = status
            body = self._call("/emailCampaigns", params)
            chunk = body.get("campaigns", [])
            out.extend(chunk)
            if len(chunk) < page_size:
                break
            offset += page_size
            time.sleep(0.2)
        return out

    def get_email_campaign(self, campaign_id: int, with_stats: bool = True) -> Dict[str, Any]:
        """Returns full campaign detail. with_stats=True asks for linksStats too."""
        params = {"statistics": "linksStats"} if with_stats else None
        return self._call(f"/emailCampaigns/{campaign_id}", params)

    def headline_stats(self, campaign_id: int) -> Dict[str, Any]:
        """Per-campaign headline stats with derived rates — the SAFE way to read stats.

        IMPORTANT: this reads statistics.campaignStats, NOT statistics.globalStats.
        For Valley Pawn's list/segment-targeted sends, globalStats is ALL ZEROS and
        makes a fully-sent campaign look like it has "no data". The real numbers live
        in campaignStats[] (one row per recipient list). Always use this method (or
        read campaignStats directly) — never report from globalStats.

        Sums across all campaignStats rows so multi-list sends aren't undercounted.
        Returns a flat dict: delivered, sent, opens, clicks, clickers, complaints,
        unsubscriptions, soft_bounces, hard_bounces, and *_pct rates off delivered.
        """
        full = self.get_email_campaign(campaign_id, with_stats=True)
        rows = (full.get("statistics") or {}).get("campaignStats") or []
        keys = ("delivered", "sent", "uniqueViews", "uniqueClicks", "clickers",
                "complaints", "unsubscriptions", "softBounces", "hardBounces")
        agg = {k: 0 for k in keys}
        for r in rows:
            for k in keys:
                agg[k] += int(r.get(k) or 0)
        delivered = agg["delivered"]
        def pct(n: int) -> float:
            return round(n / delivered * 100, 3) if delivered else 0.0
        return {
            "campaign_id": campaign_id,
            "name": full.get("name", ""),
            "status": full.get("status", ""),
            "delivered": delivered,
            "sent": agg["sent"],
            "opens": agg["uniqueViews"],
            "clicks": agg["uniqueClicks"],
            "clickers": agg["clickers"],
            "complaints": agg["complaints"],
            "unsubscriptions": agg["unsubscriptions"],
            "soft_bounces": agg["softBounces"],
            "hard_bounces": agg["hardBounces"],
            "open_pct": pct(agg["uniqueViews"]),
            "click_pct": pct(agg["uniqueClicks"]),
            "complaint_pct": pct(agg["complaints"]),
            "unsub_pct": pct(agg["unsubscriptions"]),
        }

    # ---------------------- per-link aggregation (THE money method) ----------------------

    def per_link_clicks(self, campaign_id: int) -> Dict[str, int]:
        """
        Returns {url: click_count} for HTTP links tracked by Brevo.
        REMEMBER: tel:/sms: links are NOT in this dict — they aren't trackable.
        """
        body = self.get_email_campaign(campaign_id, with_stats=True)
        links = body.get("statistics", {}).get("linksStats", {}) or {}
        # Normalize: counts come back as ints (or strings on some endpoints — coerce just in case)
        return {url: int(n) for url, n in links.items()}

    def utm_content_bucketed_clicks(self, campaign_id: int) -> Dict[str, int]:
        """
        Sum per-link clicks bucketed by `utm_content` query param.
        E.g. {"store_culpeper_call": 4, "store_culpeper_text": 2, "primary_cta": 12, ...}
        Links without a utm_content end up under the "_unlabeled" bucket.
        """
        from urllib.parse import urlparse, parse_qs
        out: Dict[str, int] = {}
        for url, n in self.per_link_clicks(campaign_id).items():
            qs = parse_qs(urlparse(url).query)
            bucket = qs.get("utm_content", ["_unlabeled"])[0]
            out[bucket] = out.get(bucket, 0) + n
        return out

    # ---------------------- list / engaged segment ----------------------

    def get_list(self, list_id: int) -> Dict[str, Any]:
        return self._call(f"/contacts/lists/{list_id}")

    def segment_count(self, segment_id: int) -> int:
        """Return the contact count for a saved segment (e.g. engaged_90d)."""
        body = self._call(f"/contacts/segments/{segment_id}")
        # Brevo doesn't always include 'totalSubscribers' on segment GET — fall back to lists/contacts
        return int(body.get("totalSubscribers", body.get("uniqueSubscribers", 0) or 0))


# ---------------------- CLI smoke test ----------------------
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="brevo_helper.py smoke test")
    p.add_argument("--campaign", type=int, help="Campaign ID to dump per-link clicks for")
    args = p.parse_args()

    c = BrevoClient()
    acct = c.account()
    plan = (acct.get("plan") or [{}])[0]
    print(f"Plan: {plan.get('type')}  credits: {plan.get('credits')}")
    print(f"Total campaigns in this account:")
    sent = c.list_email_campaigns(status="sent")
    print(f"  sent: {len(sent)}")
    if args.campaign:
        print(f"\nUTM-content buckets for campaign #{args.campaign}:")
        for bucket, n in sorted(c.utm_content_bucketed_clicks(args.campaign).items(), key=lambda kv: -kv[1]):
            print(f"  {n:>4}  {bucket}")
