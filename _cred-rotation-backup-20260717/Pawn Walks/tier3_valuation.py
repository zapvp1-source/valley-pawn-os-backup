#!/usr/bin/env python3
"""
Valley Pawn — Tier 3 Valuation Module
External market value lookup for items where Tier 1 (melt) and Tier 2 (internal comp)
couldn't produce a high-confidence estimate.

Routing:
  PRECIOUS METALS → pass-through (Tier 1 handles these; do NOT call this for PM items)
  FIREARMS        → gun-value site search via DuckDuckGo (TrueGunValue / GunBroker)
  GENERAL MERCH   → eBay Browse API (active listings, model-match + outlier trim + sold haircut)

Cache: tier3_cache.json in same directory — 7-day TTL for general merch, 30-day for firearms.

Rules:
  - Brand-only matches NOT trusted → returns confidence='none'
  - Require ≥3 model-matched comps for confidence='high'
  - eBay active prices get a 12% sold haircut (SOLD_HAIRCUT=0.88)
  - Outlier trim: drop bottom 10% + top 10% of price list before median
  - Model keys = digit-bearing tokens ≥3 chars (e.g. "SECURITY-9", "XDM", "2922-20")

Usage:
    from tier3_valuation import get_tier3_value
    r = get_tier3_value(description, category, cost)
    # r = {'value': float|None, 'source': str, 'confidence': str,
    #       'range_low': float|None, 'range_high': float|None}
"""

from __future__ import annotations
import re, json, base64, hashlib, os, time, statistics
import urllib.request, urllib.parse, html

# ── Paths & constants ──────────────────────────────────────────────────────

_HERE        = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE   = os.path.join(_HERE, "tier3_cache.json")
SRC_CREDS    = "/Users/joshuadavis/Documents/valley-pawn/ebay_weekly_rankings.py"

SOLD_HAIRCUT        = 0.88   # active listing → sold-price approximation; remove when Insights API approved
CACHE_TTL_GENERAL   = 7  * 86400   # 7 days
CACHE_TTL_FIREARMS  = 30 * 86400   # 30 days — gun prices move slowly

EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_TOKEN_URL  = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SCOPE      = "https://api.ebay.com/oauth/api_scope"

MIN_COMPS_HIGH = 3   # need at least 3 matched comps for HIGH confidence

# ── Token sets ──────────────────────────────────────────────────────────────

STOP = frozenset(
    "THE AND FOR WITH MODEL SERIAL NUMBER NO SIZE COLOR USED NEW ITEM MISC GENT GENTS "
    "LADY LADYS LADIES MENS WOMENS BLACK WHITE BLUE RED GREEN CHROME MATTE NOT INCLUDED "
    "STAINLESS POLYMER SYNTHETIC WOOD OAK WALNUT HAND TOOL MISC GENERAL".split()
)

# Parts/accessory titles on eBay — skip these listings
PARTS_RE = re.compile(
    r'\b(PART|PARTS|MANUAL|DECAL|STICKER|COVER|CASE|REPLACEMENT|CHARGER|CABLE|'
    r'PROTECTOR|MOUNT|BRACKET|FILTER|BELT|BLADE|REPAIR|ACCESSORY|ACCESSORIES|'
    r'HOLSTER|MAGAZINE|MAG|CLIP|DRUM|SLING|GRIP|STOCK|TRIGGER)\b', re.I
)

# Category / description detection
PM_RE    = re.compile(r'\b(GOLD|SILVER|COIN|BULLION|PLATINUM|JEWELRY|JEWELLERY)\b', re.I)
GUN_CAT  = re.compile(r'\b(PISTOL|REVOLVER|RIFLE|SHOTGUN|FIREARM|HANDGUN|GUN)\b', re.I)
GUN_DESC = re.compile(r'\b(PISTOL|REVOLVER|RIFLE|SHOTGUN|FIREARM|HANDGUN|REVOLVER)\b', re.I)

# Price extraction from text (handles $xxx, $x,xxx, $xxx.xx)
PRICE_RE = re.compile(r'\$\s*([\d,]{1,8}(?:\.\d{2})?)')

# Boilerplate to strip before building a gun query
SERIAL_RE = re.compile(r'\bSERIAL\s+NUMBER\s*\S*', re.I)
BOILER_RE = re.compile(
    r'\b(NOT\s+INCLUDED|BLACK|MATTE|STAINLESS|POLYMER|SYNTHETIC|WALNUT|OAK|'
    r'NICKEL|BLUED|CHROME|PARKERIZED|CERAKOTE)\b', re.I
)


# ── Text tokenization ────────────────────────────────────────────────────────

def _toks(s):
    """Normalize and tokenize a description string."""
    s = re.sub(r'[^A-Z0-9 ]', ' ', (s or '').upper())
    return [t for t in s.split() if len(t) >= 2 and t not in STOP]


def _model_keys(ts):
    """Distinctive model tokens: digit-bearing AND ≥3 chars. E.g. 'SECURITY-9', '2922-20', 'XDM'."""
    return [t for t in ts if any(c.isdigit() for c in t) and len(t) >= 3]


# ── Cache ────────────────────────────────────────────────────────────────────

_cache: dict | None = None


def _load_cache() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(CACHE_FILE) as f:
            _cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _cache = {}
    return _cache


def _save_cache():
    if _cache is not None:
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(_cache, f, indent=2)
        except Exception:
            pass  # non-fatal


def _cache_key(desc: str, category: str) -> str:
    norm = re.sub(r'\s+', ' ', f"{category}::{desc}").upper().strip()
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def _get_cached(key: str, ttl: float) -> dict | None:
    entry = _load_cache().get(key)
    if entry and (time.time() - entry.get('fetched_at', 0)) < ttl:
        return {k: entry[k] for k in ('value', 'source', 'confidence', 'range_low', 'range_high')}
    return None


def _set_cached(key: str, result: dict):
    _load_cache()[key] = dict(result, fetched_at=time.time())
    _save_cache()


# ── eBay OAuth token (app-level, cached across calls) ────────────────────────

_ebay_token: str | None = None
_ebay_token_expiry: float = 0.0


def _get_ebay_token() -> str:
    global _ebay_token, _ebay_token_expiry
    if _ebay_token and time.time() < _ebay_token_expiry - 120:
        return _ebay_token
    txt = open(SRC_CREDS).read()
    app  = re.search(r'APP_ID\s*=\s*"([^"]+)"', txt).group(1)
    cert = re.search(r'CERT_ID\s*=\s*"([^"]+)"', txt).group(1)
    cred = base64.b64encode(f"{app}:{cert}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": EBAY_SCOPE,
    }).encode()
    req = urllib.request.Request(
        EBAY_TOKEN_URL, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Authorization": f"Basic {cred}"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        t = json.load(r)
    _ebay_token = t["access_token"]
    _ebay_token_expiry = time.time() + t.get("expires_in", 7200)
    return _ebay_token


# ── eBay Browse valuation (general merch) ────────────────────────────────────

def _ebay_value(desc: str):
    """
    Query eBay Browse API for active USED listings matching the item description.
    Applies:
      - Model-key title matching (brand-only matches rejected)
      - Parts/accessory listing filter
      - Top/bottom 10% outlier trim
      - 12% sold haircut on active prices

    Returns (value, range_low, range_high, n_comps, note) or (None, None, None, 0, reason).
    """
    qtoks = _toks(desc)
    mk = _model_keys(qtoks)
    if not mk:
        # No model-number token → brand-only match not trusted
        return None, None, None, 0, "no-model-token"

    # Build query: first 6 tokens (brand + model) → keeps query tight
    q = " ".join(qtoks[:6])

    try:
        token = _get_ebay_token()
    except Exception as e:
        return None, None, None, 0, f"token-err:{e}"

    url = EBAY_BROWSE_URL + "?" + urllib.parse.urlencode({
        "q": q, "limit": 50, "filter": "conditions:{USED}"
    })
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}",
                 "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        return None, None, None, 0, f"api-err:{getattr(e,'code',type(e).__name__)}"

    mk_set = set(mk)
    prices = []
    for item in data.get("itemSummaries", []):
        title = item.get("title", "")
        # Drop parts, accessories, holsters, magazines, etc.
        if PARTS_RE.search(title):
            continue
        ttoks = set(_toks(title))
        # MUST share ≥1 model-number token — brand-only matches NOT trusted
        if not (mk_set & ttoks):
            continue
        p = item.get("price", {}).get("value")
        if p:
            try:
                prices.append(float(p))
            except (ValueError, TypeError):
                pass

    if len(prices) < MIN_COMPS_HIGH:
        # Could be 1-2 (thin) or 0 (no match)
        if prices:
            # Return thin result flagged as medium confidence
            haircut_med = round(statistics.median(prices) * SOLD_HAIRCUT, 2)
            return haircut_med, round(min(prices)*SOLD_HAIRCUT,2), round(max(prices)*SOLD_HAIRCUT,2), len(prices), f"browse*{SOLD_HAIRCUT}(thin)"
        return None, None, None, 0, "no-match"

    prices.sort()
    lo = int(len(prices) * 0.10)
    hi = max(int(len(prices) * 0.90), lo + 1)
    core = prices[lo:hi] if hi > lo else prices

    med    = statistics.median(core)
    value  = round(med * SOLD_HAIRCUT, 2)
    rng_lo = round(min(core) * SOLD_HAIRCUT, 2)
    rng_hi = round(max(core) * SOLD_HAIRCUT, 2)
    return value, rng_lo, rng_hi, len(core), f"browse*{SOLD_HAIRCUT}"


# ── Gun value search (firearms — DuckDuckGo targeting gun-value sites) ────────

def _build_gun_query(desc: str) -> str:
    """Extract make + model from a firearm description for search, preserving hyphens."""
    # Remove serial number and condition boilerplate first
    d = SERIAL_RE.sub('', desc or '')
    d = BOILER_RE.sub('', d)
    d = re.sub(r'\s+', ' ', d).strip()
    # Split on commas, slashes, and whitespace — but PRESERVE hyphens (e.g. Security-9, DDM4-V7)
    words = []
    for w in re.split(r'[,./\s]+', d.upper()):
        w = w.strip()
        if len(w) < 2 or w in STOP:
            continue
        # Title-case for better search relevance (Ruger Security-9 not RUGER SECURITY-9)
        words.append(w.title())
        if len(words) >= 5:
            break
    return " ".join(words)


def _parse_prices(text: str, lo: float = 50.0, hi: float = 50000.0) -> list:
    """Extract $-denominated prices from text, filtered to a plausible range."""
    prices = []
    for m in PRICE_RE.finditer(text):
        try:
            p = float(m.group(1).replace(',', ''))
            if lo <= p <= hi:
                prices.append(p)
        except (ValueError, TypeError):
            pass
    return prices


def _ddg_fetch(query: str) -> str:
    """Fetch DuckDuckGo lite HTML for a query. Returns raw HTML or '' on error."""
    url = "https://lite.duckduckgo.com/lite/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(
        url,
        headers={
            # NOTE: DDG lite returns empty results for Chrome UAs; use Webkit UA.
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return html.unescape(r.read().decode("utf-8", errors="ignore"))
    except Exception:
        return ""


def _gun_value_search(desc: str):
    """
    Search for firearm market value via two DuckDuckGo queries.

    Strategy (from empirical testing on Mac):
    - Primary:  "{make model} used value price"  — returns snippet prices from multiple
                sources (GunBroker, TrueGunValue, Rock Island Auction, etc.)
    - Fallback: "{make model} gun value blue book used" — alternative framing if primary thin

    Site-targeted queries (site:truegunvalue.com etc.) return too few snippets and add
    noise; broad queries surface prices organically from all relevant pages.
    _build_gun_query preserves hyphens (Security-9, DDM4-V7) for search relevance.

    Returns (value, range_low, range_high, n_comps, note) or (None, ..., reason).
    """
    base_q = _build_gun_query(desc)
    if not base_q:
        return None, None, None, 0, "no-query"

    # Primary: broad value query
    q1 = f"{base_q} used value price"
    body1 = _ddg_fetch(q1)
    prices = _parse_prices(body1)

    # Fallback if primary yields < 3 data points
    if len(prices) < 3:
        time.sleep(0.3)
        q2 = f"{base_q} gun value blue book used"
        body2 = _ddg_fetch(q2)
        prices.extend(_parse_prices(body2))

    if not prices:
        return None, None, None, 0, "no-prices-found"

    # Deduplicate by rounding to nearest $5 (avoids near-duplicate currency conversions)
    prices = sorted(set(round(p / 5) * 5 for p in prices))

    # Outlier trim (top/bottom 10%) if enough data
    if len(prices) >= 5:
        lo_i = int(len(prices) * 0.10)
        hi_i = max(int(len(prices) * 0.90), lo_i + 1)
        core = prices[lo_i:hi_i] or prices
    else:
        core = prices

    med = statistics.median(core)
    return round(med, 2), round(min(core), 2), round(max(core), 2), len(core), "gun-websearch"


# ── Public interface ─────────────────────────────────────────────────────────

def get_tier3_value(description: str, category: str, cost: float = 0.0) -> dict:
    """
    Main entry point for Tier 3 external market valuation.

    Args:
        description:  Full item description (e.g. "RUGER MODEL SECURITY-9, SERIAL NUMBER ...")
        category:     Bravo category string (e.g. "Pistol", "Electric Guitar", "Power Tool")
        cost:         Amount paid (for context only; not used in valuation logic)

    Returns:
        {
          'value':      float | None,   # Estimated market value (sold-basis where possible)
          'source':     str,            # Routing tag, e.g. 'T3-EBAY:browse*0.88', 'T3-GUN:...'
          'confidence': str,            # 'high' | 'medium' | 'low' | 'none'
          'range_low':  float | None,   # Low end of comp range
          'range_high': float | None,   # High end of comp range
        }

    Routing:
        PRECIOUS METALS → passthrough (returns source='T3-PM-PASSTHROUGH', value=None)
        FIREARMS        → DuckDuckGo gun-value search
        EVERYTHING ELSE → eBay Browse API
    """
    cat  = (category    or '').strip()
    desc = (description or '').strip()

    empty = {'value': None, 'source': 'T3-NONE', 'confidence': 'none',
             'range_low': None, 'range_high': None}

    # Precious metals: Tier 1 (melt) already handles these. Pass through cleanly.
    if PM_RE.search(cat) and not GUN_CAT.search(cat):
        return dict(empty, source='T3-PM-PASSTHROUGH')

    is_firearm = bool(GUN_CAT.search(cat) or GUN_DESC.search(desc))
    ttl = CACHE_TTL_FIREARMS if is_firearm else CACHE_TTL_GENERAL
    key = _cache_key(desc, cat)

    # Cache hit
    cached = _get_cached(key, ttl)
    if cached is not None:
        return cached

    # ── Route ──
    if is_firearm:
        val, rlo, rhi, n, note = _gun_value_search(desc)
        if val is not None:
            conf = 'high' if n >= MIN_COMPS_HIGH else ('medium' if n >= 1 else 'none')
            result = {'value': val, 'source': f'T3-GUN:{note}',
                      'confidence': conf, 'range_low': rlo, 'range_high': rhi}
        else:
            result = dict(empty, source=f'T3-GUN:FAIL({note})')
    else:
        val, rlo, rhi, n, note = _ebay_value(desc)
        if val is not None:
            conf = 'high' if n >= MIN_COMPS_HIGH else 'medium'
            result = {'value': val, 'source': f'T3-EBAY:{note}',
                      'confidence': conf, 'range_low': rlo, 'range_high': rhi}
        else:
            result = dict(empty, source=f'T3-EBAY:FAIL({note})')

    _set_cached(key, result)
    return result


# ── Standalone test ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        ("RUGER MODEL SECURITY-9, SERIAL NUMBER 384-54719, BLACK",  "Pistol", 135),
        ("SPRINGFIELD ARMORY MODEL XDM ELITE, SERIAL NUMBER BA123", "Pistol", 250),
        ("MILWAUKEE MODEL 2922-20 M18 FORCE LOGIC PRESS TOOL",     "Power Tool", 480),
        ("DEWALT MODEL DCF887 20V MAX IMPACT DRIVER",              "Electric Drill", 75),
        ("MEZE AUDIO ELITE HEADPHONES",                             "Headphones", 900),
    ]
    print("Tier 3 valuation smoke test")
    print(f"{'Category':22} {'Paid':>7} {'T3Est':>8} {'Conf':8} {'Source'}")
    print("-" * 80)
    for desc, cat, cost in tests:
        r = get_tier3_value(desc, cat, cost)
        v  = f"${r['value']:,.0f}" if r['value'] else "—"
        print(f"{cat[:22]:22} ${cost:>6,.0f} {v:>8} {r['confidence'][:7]:8} {r['source']}")
        time.sleep(0.5)
