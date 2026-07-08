#!/usr/bin/env python3
"""
Valley Pawn $100/month giveaway — monthly winner draw + announcement.

Runs as scheduled task on the last day of each month at 11:59 PM ET.

Flow:
  1. Pull current month's entries from Linkie (via API) — emails collected this month
  2. Random-pick one winner
  3. Email winner directly (Brevo template)
  4. Generate winner announcement post for vp-content-batch to publish next morning
     across Brand FB / IG / X / TikTok / WordPress (brand routing tier)
  5. Log the result for the public winners page

Dependencies:
  - publer_client (existing)
  - Linkie API (need to confirm endpoint — placeholder for now)
  - Brevo connector (for winner email)

Usage:
    python3 giveaway_monthly_draw.py                  # actually draw + announce
    python3 giveaway_monthly_draw.py --dry-run        # show winner, don't email/announce
    python3 giveaway_monthly_draw.py --month 2026-06  # back-fill specific month
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
WINNERS_LOG = HERE / "giveaway_winners.jsonl"

# Linkie API placeholder — replace with actual endpoint when documented
LINKIE_API_BASE = "https://app.linkie.bio/api"  # TBD


def fetch_entries(month_iso: str) -> list[dict]:
    """
    Pull email collection entries from Linkie for the given month.
    month_iso: 'YYYY-MM' (e.g. '2026-07')

    PLACEHOLDER: Linkie's email-collection API isn't publicly documented yet.
    Manual fallback: export CSV from Linkie dashboard, drop into entries_{month}.csv,
    this script will read from that.
    """
    # Try Linkie API first (when available)
    # ... not implemented yet, Linkie doesn't expose a public API for email collection

    # Manual fallback: CSV export
    csv_path = HERE / f"entries_{month_iso}.csv"
    if csv_path.exists():
        import csv
        with csv_path.open() as f:
            return list(csv.DictReader(f))

    # If neither path works, return empty + warn
    print(f"[warn] No entries found for {month_iso}. Place CSV at {csv_path} "
          f"(export from Linkie dashboard).", file=sys.stderr)
    return []


def pick_winner(entries: list[dict]) -> dict | None:
    """Random pick. Each entry should have at least 'email' and ideally 'name'."""
    if not entries:
        return None
    return random.choice(entries)


def generate_winner_announcement(winner: dict, month_iso: str) -> dict:
    """Build the manifest item for vp_social_publisher.py — brand-tier fan-out."""
    name = winner.get("name") or winner.get("email", "").split("@")[0].title()
    # Privacy-conscious: only first name + last initial
    parts = name.split()
    safe_name = parts[0] if len(parts) == 1 else f"{parts[0]} {parts[-1][0]}."

    caption = (
        f"🎉 Congrats to {safe_name} — our {month_iso} $100 giveaway winner!\n\n"
        f"Want a shot at next month's $100? Drop your email at follow.thevalleypawn.com — "
        f"one entry per person, drawn the last day of every month. No purchase necessary.\n\n"
        f"Family-owned. 5 Virginia locations. We've been giving fair deals since 2014. 💙❤️"
    )

    return {
        "id": f"giveaway-winner-{month_iso}",
        "routing_tier": "brand",  # FB + IG + X + WordPress (per current routing config)
        "store_keys": [],         # default brand fan-out
        "caption": caption,
        "scheduled_at": (datetime.now(timezone.utc).replace(hour=14, minute=0, second=0, microsecond=0)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")),  # next 9am ET / 14:00 UTC
        "status": "approved",
    }


def email_winner(winner: dict, month_iso: str, dry_run: bool = False):
    """Send winner notification via Brevo template (placeholder)."""
    email = winner.get("email")
    if not email:
        print("[warn] Winner has no email — skipping notification", file=sys.stderr)
        return
    if dry_run:
        print(f"[DRY] Would email: {email}")
        return
    # TODO: wire to Brevo MCP connector when set up. For now, print.
    print(f"[TODO] Email winner: {email} (Brevo connector not yet wired)")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--month", default=None,
                        help="Target month YYYY-MM (default: current)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Pick + report, but don't email or publish")
    args = parser.parse_args()

    month_iso = args.month or datetime.now(timezone.utc).strftime("%Y-%m")
    print(f"=== Valley Pawn $100 Giveaway Draw: {month_iso} ===")

    entries = fetch_entries(month_iso)
    print(f"[info] {len(entries)} eligible entries for {month_iso}")
    if not entries:
        print("[exit] No entries — no draw this month.")
        sys.exit(1)

    winner = pick_winner(entries)
    print(f"[result] Winner: {winner.get('email', '?')} "
          f"({winner.get('name', 'no name on file')})")

    if args.dry_run:
        print("[dry-run] Skipping email + announcement.")
        return

    # Email winner
    email_winner(winner, month_iso, dry_run=False)

    # Generate announcement manifest for vp_social_publisher.py
    manifest_item = generate_winner_announcement(winner, month_iso)
    manifest_path = HERE / f"giveaway_announcement_{month_iso}.json"
    manifest = {
        "batch_id": f"giveaway-{month_iso}",
        "items": [manifest_item],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"[ok] Announcement manifest written: {manifest_path}")
    print(f"     Run: python3 vp_social_publisher.py {manifest_path}")

    # Append to winners log (used for public /winners page)
    with WINNERS_LOG.open("a") as f:
        f.write(json.dumps({
            "month": month_iso,
            "winner_email": winner.get("email"),
            "winner_name": winner.get("name"),
            "drawn_at": datetime.now(timezone.utc).isoformat(),
        }) + "\n")


if __name__ == "__main__":
    main()
