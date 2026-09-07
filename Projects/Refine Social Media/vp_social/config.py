"""Paths, account map, store facts and routing tiers. No I/O to Publer here."""
from __future__ import annotations
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")

# --- paths -------------------------------------------------------------
PKG_DIR = Path(__file__).resolve().parent
RSM = PKG_DIR.parent                                   # Refine Social Media/
PROJECTS = RSM.parent
STUDIOS = PROJECTS / "Valley Pawn Studios"
STATE_DIR = RSM / "state"
# SQLite needs real file locking; the Cowork sandbox mount doesn't provide it (disk I/O error).
# Production runs on the Mac (osascript / launchd). For sandbox tests set VP_SOCIAL_LEDGER=/tmp/x.sqlite.
LEDGER_PATH = Path(os.environ.get("VP_SOCIAL_LEDGER") or (STATE_DIR / "social_ledger.sqlite"))
PLANS_DIR = STATE_DIR / "plans"
LOG_DIR = STATE_DIR / "logs"
REELS_DIR = RSM / "reels"
DEAL_UPLOADS = RSM / "deal_of_week_uploads"
HERO_LIBRARY = STUDIOS / "asset-library" / "heroes"
CASUAL_INBOX = STUDIOS / "casual-video-inbox"
COMMUNITY_KB = RSM / "CITY_COMMUNITY_KB.md"
ACCOUNTS_PATH = RSM / "publer_accounts.json"
CONFIG_PATH = RSM / "publer_config.json"

for _d in (STATE_DIR, PLANS_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- Slack -------------------------------------------------------------
SLACK = {
    "studio_queue": "C0BHTEUPADB",      # #vp-studio-queue (log cards)
    "social_media": "C0BMRC2LN3D",      # #social-media (team-visible)
    "deal_of_week": "C0AVCANK7E3",      # #deal-of-the-week (manager intake)
    "joshua_dm": "D03BHQH5VGT",
}

# --- accounts ----------------------------------------------------------
STORES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
STORE_FB = {s: s for s in STORES}                      # store key == FB page key
STORE_GBP = {s: f"GBP_{s}" for s in STORES}
BRAND_KEYS = ["Brand", "BrandIG", "BrandTwitter"]      # X stays until Joshua decides
VIDEO_BRAND_KEYS = ["Brand", "BrandIG", "BrandTikTok"]
EXCLUDED_FROM_QUOTA = {"BrandTikTok", "BrandBlog"}

STORE_FACTS = {
    # Source of truth: valley-pawn-context skill (canonical NAP). Never invent these.
    "Culpeper":     {"address": "571 James Madison Highway, Culpeper, VA 22701",
                     "hours": "Mon-Sat 10am-6pm, closed Sun", "phone": "(540) 445-5510"},
    "Waynesboro":   {"address": "1321 West Broad Street, Waynesboro, VA 22980",
                     "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun", "phone": "(540) 221-6346"},
    "Harrisonburg": {"address": "1790 East Market Street, Suite 22, Harrisonburg, VA 22801",
                     "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun", "phone": "(540) 574-4500"},
    "Lexington":    {"address": "125 Walker Street, Lexington, VA 24450",
                     "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun", "phone": "(540) 461-8349"},
    "Roanoke":      {"address": "2362 Peters Creek Road, Suite C, Roanoke, VA 24017",
                     "hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun", "phone": "(540) 562-0776"},
}
FIVE_STORE_FOOTER = ("📍 125 Walker St, Lexington · 1321 W Broad St, Waynesboro · "
                     "1790 E Market St Ste 22, Harrisonburg · 571 James Madison Hwy, Culpeper · "
                     "2362 Peters Creek Rd Ste C, Roanoke")

# --- content rules (from vp-brand-studio / PILLAR_OVERLAY / valley-pawn-context) ------
RULES = {
    "humor_max_per_week": 1,
    "community_share": (0.15, 0.20),
    "item_cooldown_days": 14,          # same item on same page: 1 photo + 1 video per 14 days
    "identical_caption_window_days": 7,
    "min_words_store": 25,
    "min_words_brand": 40,
    "x_max_chars": 270,
    "gbp_max_chars": 1500,
}


def load_accounts() -> dict:
    return json.loads(ACCOUNTS_PATH.read_text()).get("accounts", {})


def account_index() -> dict[str, dict]:
    """publer account_id -> {key, provider, name}"""
    idx = {}
    for key, meta in load_accounts().items():
        if meta.get("publer_id"):
            idx[meta["publer_id"]] = {"key": key, "provider": meta.get("provider", "?"),
                                      "name": meta.get("name", key)}
    return idx


def store_of(key: str) -> str | None:
    if key in STORES:
        return key
    if key.startswith("GBP_") and key[4:] in STORES:
        return key[4:]
    return None


def dry_run_enabled() -> bool:
    """Global kill switch: `state/DRY_RUN` file present or VP_SOCIAL_DRY_RUN=1."""
    return (STATE_DIR / "DRY_RUN").exists() or os.environ.get("VP_SOCIAL_DRY_RUN") == "1"
