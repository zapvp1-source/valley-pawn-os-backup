"""
Pinterest lane (added 2026-11-21, Joshua approved Pinterest Business for jewelry + watches).

Source: the live eBay listings snapshot that also feeds thevalleypawn.com/shop/
(Website/shop-build/items.json, refreshed nightly). Every pin is a REAL item that is for sale
right now, linked to its own listing, so nothing ever points at a sold item on day one.
Weekly deal photos are almost never jewelry (0 of ~40 deals Sep-Nov 2026), so they are not the source.

pick(monday, n) -> up to n items {title, price, url, img, store, board, board_id, item_key}
  * jewelry / watch nouns only; flatware, sneakers, bags, tools, guitars, anything weapons-adjacent excluded
  * one pin per listing per 90 days (ledger), spread across stores
  * board chosen by keyword (engagement > diamond > rings > watches > earrings/bracelets > chains/necklaces > gold/silver)
"""
from __future__ import annotations
import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from . import config, ledger

ITEMS_PATH = config.RSM.parent / "Website" / "shop-build" / "items.json"
LANE_DIR = config.RSM / "pinterest_lane"
COOLDOWN_DAYS = 90
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")

_JEWELRY = re.compile(r"\b(ring|rings|necklace|necklaces|chain|chains|bracelet|bracelets|bangle|earring|earrings|pendant|"
                      r"diamond|diamonds|solitaire|brooch|cufflinks?|choker|locket|charm|watch|watches|wristwatch|"
                      r"rolex|omega|seiko|citizen|bulova|accutron|tag heuer|tissot|movado|pandora|yurman|ripka|john hardy|"
                      r"10k|14k|18k|24k|\.925|sterling)\b", re.I)
_EXCLUDE = re.compile(r"\b(fork|spoon|knife|knives|butter|carving|dish|cushion|calend[ae]r|tray|bowl|platter|flatware|"
                      r"sneakers?|shoes?|jordan|handbag|purse|bag|tote|crossbody|tool|alignment|guitar|bass|amp|"
                      r"smart ?watch|apple watch|galaxy watch|fitbit|gun|rifle|pistol|firearm|ammo|holster|blade|dagger|"
                      r"medal|medallion|medalion|coin|bar|bullion|calander|franklin mint|reed & barton|gorham|wallace|hollow|python|embossed)\b", re.I)
_BOARDS = [  # first match wins
    ("engagement-rings", re.compile(r"\b(engagement|bridal|wedding set|solitaire)\b", re.I)),
    ("diamond-jewelry", re.compile(r"\b(diamond|diamonds|ctw|carat)\b", re.I)),
    ("rings", re.compile(r"\b(ring|rings|band)\b", re.I)),
    ("luxury-watches", re.compile(r"\b(watch|watches|wristwatch|rolex|omega|seiko|citizen|bulova|accutron|tag heuer|tissot|movado)\b", re.I)),
    ("earrings-and-bracelets", re.compile(r"\b(earring|earrings|bracelet|bracelets|bangle|cuff|wrap)\b", re.I)),
    ("gold-chains-and-necklaces", re.compile(r"\b(chain|chains|necklace|necklaces|pendant|choker|locket)\b", re.I)),
    ("gold-and-silver", re.compile(r".", re.I)),
]


def clean_title(t: str) -> str:
    t = html.unescape(t or "")
    t = re.sub(r"\s*\((?:VP|VA|ROA|WAY|HAR|LEX|CUL)?\d{4,}\)\s*$", "", t)       # internal stock numbers
    t = re.sub(r"\s*\(PLEASE READ.*$", "", t, flags=re.I)
    return re.sub(r"\s{2,}", " ", t).strip(" -–")


def board_for(title: str) -> str:
    for slug, rx in _BOARDS:
        if rx.search(title):
            return slug
    return "gold-and-silver"


def board_ids() -> dict:
    return (config.load_accounts().get("BrandPinterest") or {}).get("boards") or {}


def eligible(item: dict) -> bool:
    t = clean_title(item.get("t", ""))
    return bool(t and item.get("img") and item.get("u") and _JEWELRY.search(t) and not _EXCLUDE.search(t))


def item_key(item: dict) -> str:
    m = re.search(r"/itm/(\d+)", item.get("u", ""))
    return "pin:" + (m.group(1) if m else re.sub(r"\W+", "", item.get("t", "").lower())[:40])


def tagged_url(url: str, store: str) -> str:
    sep = "&" if "?" in url else "?"
    return url + sep + urllib.parse.urlencode({"utm_source": "pinterest", "utm_medium": "social",
                                                "utm_campaign": "pinterest_jewelry", "utm_content": store.lower()})


def pick(monday: dt.date, n: int) -> list[dict]:
    try:
        raw = json.loads(ITEMS_PATH.read_text())
    except Exception:
        return []
    items = raw.get("items", raw) if isinstance(raw, dict) else raw
    ids = board_ids()
    pool = []
    for it in items:
        if not eligible(it):
            continue
        k = item_key(it)
        if ledger.recent_item_posts(k, "BrandPinterest", COOLDOWN_DAYS):
            continue
        t = clean_title(it["t"])
        b = board_for(t)
        pool.append({"title": t, "price": it.get("p"), "url": tagged_url(it["u"], it.get("s", "")), "listing": it["u"],
                     "img": re.sub(r"s-l\d+\.", "s-l1600.", it["img"]), "store": it.get("s", ""),
                     "board": b, "board_id": ids.get(b), "item_key": k})
    pool = [p for p in pool if p["board_id"]]
    # round-robin across stores, rotating the starting store weekly so one store never always leads
    stores = [s for s in config.STORES if any(p["store"] == s for p in pool)]
    if not stores:
        return []
    off = monday.isocalendar()[1] % len(stores)
    stores = stores[off:] + stores[:off]
    by = {s: [p for p in pool if p["store"] == s] for s in stores}
    out = []
    while len(out) < n and any(by.values()):
        for s in stores:
            if by[s] and len(out) < n:
                out.append(by[s].pop(0))
    return out


def fetch_image(url: str, dest: Path) -> str | None:
    """Download the listing photo so Publer can host it (upload_media takes a local path)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 5000:
        return str(dest)
    for u in (url, re.sub(r"s-l1600\.", "s-l500.", url)):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) > 5000:
                try:                      # eBay serves webp; Pinterest/Publer are safest with JPEG
                    import io
                    from PIL import Image
                    Image.open(io.BytesIO(data)).convert("RGB").save(dest, "JPEG", quality=92)
                except Exception:
                    dest.write_bytes(data)
                return str(dest)
        except Exception:
            continue
    return None
