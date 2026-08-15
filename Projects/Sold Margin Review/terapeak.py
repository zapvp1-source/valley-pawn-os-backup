#!/usr/bin/env python3
"""
Valley Pawn — Terapeak SOLD-comp parser + cache
===============================================

WHY TERAPEAK AND NOT THE API (settled 2026-08-14, by test — do not re-litigate)
------------------------------------------------------------------------------
Probed our own production credentials (`Pawn Walks/ebay_scope_probe.py`):
  - baseline app OAuth ............ WORKS (Browse returned 1,507 results)
  - buy.marketplace.insights scope . invalid_scope, HTTP 400
  - item_sales/search w/ base token  HTTP 403 "Insufficient permissions"
  - findCompletedItems ............ shut down by eBay Feb 2025
So true sold data is NOT reachable by API, and Marketplace Insights is documented as
closed to new users with non-partners being denied — applying is near-certainly futile.

Terapeak Product Research IS reachable: free to any eBay seller with Seller Hub (we are
`valley_pawn_lexington`), up to 3 years of real completed sales — the same data Insights
gates. It is a UI, so Claude drives Chrome, parses the page, and caches the result here;
the compile script then reads the cache. That split matters: python does math, Claude does
the browser. `run_daily_sold_review.py` must NEVER need a browser to produce a report.

This also matches the standard already written in the `ebay-context` skill:
  "benchmark against SOLD comps, not asking prices ... use the median of recent solds"

THE PARTS TRAP — THE WHOLE REASON THIS PARSER EXISTS
----------------------------------------------------
NEVER use Terapeak's headline "Avg sold price". Proven live 2026-08-14 on STIHL BG 50:
headline avg was $61.84, but that pooled gas caps ($14.95), primer bulbs ($13.79),
carburetors ($43), flywheels ($42.95) with actual complete blowers ($125.99, $190.00,
$199.99, $209.95). Real market for the item is ~$126-210 — the headline understated it by
2-3x. Same failure as the `Husqvarna YTH22V46 -> $22` bad match in Pawn Walks/STATUS.md.
We parse the per-listing rows and drop accessories before taking a median.

USAGE
-----
  Claude (browser step): navigate to research_url(kw), get_page_text, then
      from terapeak import parse_page, put
      r = parse_page(text); put(kw, r)
  Compile step (no browser):
      from terapeak import get
      r = get(kw)   # None if absent or stale
"""

from __future__ import annotations
import os, re, json, time, statistics, urllib.parse

_HERE      = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(_HERE, "terapeak_cache.json")

CACHE_TTL_DAYS = 30      # sold comps move slowly; long TTL keeps browser usage minimal
MIN_COMPS      = 3       # fewer than this is an anecdote, not a market

# Accessory/part exclusions. Deliberately broader than the intake-side PARTS_RE because a
# sold-comp median is far more sensitive to cheap parts than a single valuation lookup is:
# one $7 throttle linkage among four real units drags a median hard.
PARTS_RE = re.compile(
    r'\b(PART|PARTS|MANUAL|DECAL|STICKER|COVER|CASE|REPLACEMENT|CHARGER|CABLE|CORD|'
    r'PROTECTOR|MOUNT|BRACKET|FILTER|BELT|BLADE|REPAIR|ACCESSORY|ACCESSORIES|KIT|'
    r'HOLSTER|MAGAZINE|CLIP|DRUM|SLING|GRIP|TRIGGER|CARB|CARBURETOR|GASKET|SPRING|'
    r'PRIMER|BULB|FLYWHEEL|IGNITION|COIL|SWITCH|SHROUD|HOUSING|TANK|CAP|PISTON|'
    r'CRANKSHAFT|CYLINDER|RECOIL|STARTER|PULL START|FAN|TUBE|LINKAGE|SCREW|BOLT|'
    r'ADAPTER|FITS |FOR STIHL|FOR |RACK|HANGER|HOLDER|DRIVER|WRENCH|OEM NEW STIHL)\b',
    re.I)

# Multi-item lots distort a per-unit median ("2 Pack ... Blowers" at $299.99 is ~$150/ea).
LOT_RE = re.compile(r'\b(\d+)\s*(?:X|PACK|PC|PCS|PIECE|LOT|SET|BUNDLE)\b', re.I)

# One Terapeak result row, as it appears in get_page_text output:
#     , preview full size image
#     <TITLE>
#
#     Edit
#
#     $<PRICE>
ROW_RE = re.compile(
    r', preview full size image\s*\n(?P<title>[^\n]+?)\s*\n\s*\nEdit\s*\n\s*\n\$'
    r'(?P<price>[\d,]+(?:\.\d{1,2})?)', re.I)

HEADLINE_RE = re.compile(r'\$([\d,]+(?:\.\d{2})?)\s*\nAvg sold price')


def research_url(keyword: str, days: int = 90) -> str:
    """Terapeak Product Research, SOLD tab, driven entirely by URL (no clicking)."""
    return ("https://www.ebay.com/sh/research?" + urllib.parse.urlencode({
        "marketplace": "EBAY-US", "keywords": keyword, "dayRange": days,
        "categoryId": 0, "offset": 0, "limit": 50, "sorting": "-itemsold",
        "tabName": "SOLD"}))


def parse_page(text: str, keyword: str = "") -> dict:
    """
    Parse Terapeak page text into a defensible sold-comp figure.

    Returns {value, n, n_raw, low, high, headline_avg, excluded, source, note}.
    `value` is None when there isn't enough clean evidence — that is a valid, honest
    answer and callers must treat it as "no external opinion", never as zero.
    """
    rows = [(m.group("title").strip(), float(m.group("price").replace(",", "")))
            for m in ROW_RE.finditer(text or "")]

    headline = None
    hm = HEADLINE_RE.search(text or "")
    if hm:
        headline = float(hm.group(1).replace(",", ""))

    out = {"value": None, "n": 0, "n_raw": len(rows), "low": None, "high": None,
           "headline_avg": headline, "excluded": 0, "source": "terapeak-sold",
           "note": "", "keyword": keyword}

    if not rows:
        out["note"] = "no sold rows parsed (page may not have rendered)"
        return out

    kept = []
    for title, price in rows:
        if PARTS_RE.search(title):
            continue
        lot = LOT_RE.search(title)
        if lot:
            try:                       # normalise a multi-pack to per-unit
                qty = int(lot.group(1))
                if 1 < qty <= 20:
                    price = price / qty
            except ValueError:
                pass
        kept.append(price)

    out["excluded"] = len(rows) - len(kept)

    if len(kept) < MIN_COMPS:
        out["note"] = (f"only {len(kept)} non-part comp(s) of {len(rows)} rows — "
                       "not enough clean evidence")
        return out

    # Trim the extremes before the median: Terapeak returns whole-lot oddities and the
    # occasional mis-titled listing that survives the parts filter.
    s = sorted(kept)
    if len(s) >= 8:
        cut = max(1, len(s) // 10)
        s = s[cut:-cut]

    out["value"] = round(statistics.median(s), 2)
    out["n"]     = len(s)
    out["low"], out["high"] = round(min(s), 2), round(max(s), 2)
    if headline and out["value"]:
        drift = (out["value"] - headline) / headline * 100
        out["note"] = f"filtered median is {drift:+.0f}% vs Terapeak headline ${headline:,.2f}"
    return out


# ── Cache ─────────────────────────────────────────────────────────────────────
def _load() -> dict:
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _key(keyword: str) -> str:
    return re.sub(r'\s+', ' ', (keyword or "").strip().upper())


def get(keyword: str, max_age_days: int = CACHE_TTL_DAYS) -> dict | None:
    """Fresh cached comp, or None. Never raises — the report must survive a bad cache."""
    e = _load().get(_key(keyword))
    if not e:
        return None
    if (time.time() - e.get("fetched_at", 0)) > max_age_days * 86400:
        return None
    return e if e.get("value") else None


def put(keyword: str, parsed: dict) -> None:
    """Store a parse result (including misses — a miss is worth caching so we don't retry daily)."""
    d = _load()
    e = dict(parsed)
    e["fetched_at"] = time.time()
    e["fetched_readable"] = time.strftime("%Y-%m-%d %H:%M")
    d[_key(keyword)] = e
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, CACHE_FILE)


def needs_lookup(keyword: str) -> bool:
    return get(keyword) is None


def get_any(keyword: str, max_age_days: int = CACHE_TTL_DAYS) -> dict | None:
    """
    Like get(), but ALSO returns cached MISSES (entries with value=None).
    Added 2026-08-14: get() filters value-less entries out, which meant a
    cached miss was invisible to callers — so known-dud keywords were being
    re-fetched (and re-billed) every single day. Callers that need to know
    "did we already try this?" must use THIS, not get().
    """
    e = _load().get(_key(keyword))
    if not e:
        return None
    if (time.time() - e.get("fetched_at", 0)) > max_age_days * 86400:
        return None
    return e


def stats() -> dict:
    d = _load()
    hit = sum(1 for v in d.values() if v.get("value"))
    return {"entries": len(d), "with_value": hit, "misses": len(d) - hit,
            "file": CACHE_FILE}


FIXTURE      = os.path.join(_HERE, "test_fixtures", "terapeak_stihl_bg50.txt")
FIXTURE_EXPECT = 195.00        # known-good filtered median for the saved STIHL BG 50 page


def selfcheck() -> dict:
    """
    DAILY CANARY — the permanent fix for silent breakage.

    Terapeak is browser automation against a UI we don't control. eBay WILL change that
    page eventually. The danger is not that it breaks — it's that it breaks QUIETLY: the
    parser finds no rows, every item falls back to internal-only, the market column goes
    blank, and the report keeps publishing looking perfectly healthy. Nobody notices for
    weeks. That is the same silent-failure class as the `slack_skipped` bug (2026-08-14).

    So every run re-parses a SAVED REAL PAGE with a known answer. If the parser no longer
    returns ~$195 on it, the parser broke — independent of network, login, or eBay being up.
    That distinction matters: a fixture failure means OUR CODE is wrong; a fixture pass with
    an empty cache means the BROWSER STEP is failing. Different problems, different fixes.

    Returns {ok, parser_ok, note, entries, with_value, fresh_7d}. Never raises.
    """
    out = {"ok": False, "parser_ok": False, "note": "", "entries": 0,
           "with_value": 0, "fresh_7d": 0}
    # 1) Parser integrity — offline, deterministic, no dependencies.
    try:
        got = parse_page(open(FIXTURE, encoding="utf-8").read(), "SELFCHECK")["value"]
        if got is None:
            out["note"] = "PARSER BROKEN: fixture yielded no comps — eBay page format likely changed"
        elif abs(got - FIXTURE_EXPECT) > 1.0:
            out["note"] = (f"PARSER DRIFT: fixture returned ${got:,.2f}, expected "
                           f"${FIXTURE_EXPECT:,.2f} — filter/median logic changed behaviour")
        else:
            out["parser_ok"] = True
    except FileNotFoundError:
        out["note"] = "PARSER UNCHECKED: regression fixture missing"
    except Exception as e:
        out["note"] = f"PARSER ERROR: {e}"

    # 2) Cache health — is the browser step actually feeding us anything?
    try:
        d = _load()
        out["entries"] = len(d)
        out["with_value"] = sum(1 for v in d.values() if v.get("value"))
        cutoff = time.time() - 7 * 86400
        out["fresh_7d"] = sum(1 for v in d.values() if v.get("fetched_at", 0) > cutoff)
        if out["parser_ok"] and out["entries"] and out["fresh_7d"] == 0:
            out["note"] = ("BROWSER STEP STALLED: parser is fine but nothing new cached in 7 "
                           "days — the Terapeak fetch in STEP 5b is not running or is being "
                           "blocked (login wall?)")
    except Exception as e:
        out["note"] = out["note"] or f"CACHE ERROR: {e}"

    out["ok"] = out["parser_ok"] and not out["note"]
    return out


def ingest(keyword: str, path: str) -> dict:
    """
    Parse a saved Terapeak page dump and store it. This is the bridge between the browser
    step (Claude saves page text to a file) and the cache (python parses + stores), chosen
    so no large page text ever has to survive shell/AppleScript quoting.
    """
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    r = parse_page(txt, keyword)
    put(keyword, r)
    return r


if __name__ == "__main__":
    import sys
    a = sys.argv[1:]
    if a and a[0] == "--stats":
        print(json.dumps(stats(), indent=2))
    elif len(a) > 1 and a[0] == "--url":
        print(research_url(" ".join(a[1:])))
    elif len(a) > 2 and a[0] == "--ingest":
        # usage: terapeak.py --ingest "STIHL BG 50" /path/to/page.txt
        r = ingest(a[1], a[2])
        if r.get("value"):
            print(f"OK  {a[1]!r} -> ${r['value']:,.2f}  (n={r['n']} clean of {r['n_raw']} rows, "
                  f"{r['excluded']} parts excluded)  headline was ${r.get('headline_avg') or 0:,.2f}")
        else:
            print(f"MISS {a[1]!r} -> no usable comp: {r.get('note')}")
    else:
        print(__doc__)
        print(json.dumps(stats(), indent=2))
