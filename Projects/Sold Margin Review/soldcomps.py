#!/usr/bin/env python3
"""
Valley Pawn — SoldComps API client (real eBay SOLD comps, no browser)
=====================================================================

REPLACES the Terapeak browser scrape as the primary market-comp source.
Terapeak stays built and is the automatic fallback — see `terapeak.py`.

WHY: eBay's own API cannot serve sold data (proven against our credentials —
`Pawn Walks/ebay_scope_probe.py`: insights scope -> invalid_scope, item_sales -> 403,
findCompletedItems dead since Feb 2025). Terapeak works but is browser automation against
a UI we don't control, so it breaks silently when eBay changes their page. SoldComps sells
a versioned HTTP contract and takes on that maintenance — which is the actual thing being
purchased here, not better data.

API CONTRACT (verified against https://api.sold-comps.com/openapi.json, 2026-08-14)
  GET https://api.sold-comps.com/v1/scrape
  Auth:  Authorization: Bearer sc_...        (NOT x-api-key — that scheme does not exist)
  Params: keyword (required), sold="true", ebaySite, soldAfter/soldBefore (YYYY-MM-DD),
          itemCondition (any|new|used), count (<=240), page
  200 -> {keyword, page, totalItems, totalResults, hasNextPage, items:[...]}
  Item -> title, soldPrice (STRING!), endedAt (date-only string), condition, buyingFormat,
          shippingPrice, totalPrice, sellerFeedbackScore, url, itemId
  429  -> TWO shapes, branch on `code`:
            "rate_limited"   -> wait retry_after seconds, retry
            "quota_exceeded" -> STOP. Quota won't reset until reset_at. Do not retry.

GOTCHAS BAKED IN BELOW
  - soldPrice is a STRING ("899.99"), not a number. Must be cast.
  - Sold-only fields are OMITTED (not null) when sold=false. We always send sold=true.
  - Error bodies are snake_case (retry_after, reset_at) while everything else is camelCase.
  - The `keyword` param supports eBay minus-syntax, so we exclude junk at the SOURCE as
    well as filtering after — belt and braces, because the parts problem is the single
    biggest source of wrong comps (see terapeak.py docstring, STIHL BG 50: $61.84 vs $195).

SETUP — Joshua does this once:
  Put the API key in:  <project>/.soldcomps_key      (file containing just `sc_...`)
  or export SOLDCOMPS_API_KEY. The key is never printed, logged, or committed.

USAGE
  python3 soldcomps.py --test                 # verify key + live call, prints no secrets
  python3 soldcomps.py --fetch "STIHL BG 50"  # fetch, filter, cache
  from soldcomps import fetch_comp
"""

from __future__ import annotations
import os, sys, json, time, statistics, urllib.parse, urllib.request, urllib.error

_HERE    = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(_HERE, ".soldcomps_key")
API_URL  = "https://api.sold-comps.com/v1/scrape"

# ONE definition of what a "part" is — imported from terapeak so the browser path and the
# API path can never disagree about which comps are real. Do not redefine these here.
from terapeak import (PARTS_RE, LOT_RE, MIN_COMPS, put as cache_put,
                      get as cache_get, get_any as cache_get_any)

# Query-level exclusions. eBay minus-syntax removes the worst offenders before they ever
# count against our 240-item page, which materially improves signal per request.
NEGATIVE_TERMS = ("-parts -part -repair -broken -\"for parts\" -manual -decal "
                  "-carburetor -carb -gasket -screw -bolt -filter -cover -case "
                  "-muffler -throttle -\"spark plug\" -choke -exhaust")

# EXTRA parts terms, applied ON TOP of the shared PARTS_RE — additive superset,
# NOT a replacement (the shared regex is fixture-validated in terapeak.py and is
# not touched). Found live 2026-08-14: a $14 OEM muffler and a $15.99 throttle
# handle survived PARTS_RE and dragged the STIHL BG 50 median to $32.54 vs the
# known-good $195. Same trap, new vocabulary.
import re as _re
EXTRA_PARTS_RE = _re.compile(
    r'\b(MUFFLER|THROTTLE|SPARK\s*PLUG|FUEL\s*LINE|CHOKE|EXHAUST|CRANKCASE|'
    r'CRANK\s*CASE|AIR\s*BOX|INTAKE|HANDLE\s+HALF|SHROUD|PULL\s*CORD)\b', _re.I)

DEFAULT_DAYS = 90

# ── Daily quota guard (BLEND_V2_PLAN, Phase 1) ────────────────────────────────
# Plan math: ~35-40 fresh lookups/day ≈ 1,100/mo vs the 2,000/mo quota. This
# ceiling is the safety valve: no single day may burn more than 60 requests, so
# a runaway loop or a giant sold day cannot torch the month. Shared by EVERY
# caller because it lives inside fetch_comp itself. Callers order their lookups
# by sale value, so when the guard trips it is the $9 items that degrade.
DAILY_CEILING = 60
USAGE_FILE    = os.path.join(_HERE, ".soldcomps_usage.json")


def _usage_today() -> int:
    try:
        with open(USAGE_FILE) as f:
            d = json.load(f)
        return int(d.get(time.strftime("%Y-%m-%d"), 0))
    except Exception:
        return 0


def _bump_usage() -> None:
    today = time.strftime("%Y-%m-%d")
    try:
        try:
            with open(USAGE_FILE) as f:
                d = json.load(f)
        except Exception:
            d = {}
        d = {k: v for k, v in d.items() if k >= time.strftime(
            "%Y-%m-%d", time.localtime(time.time() - 35 * 86400))}
        d[today] = int(d.get(today, 0)) + 1
        tmp = USAGE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(d, f)
        os.replace(tmp, USAGE_FILE)
    except Exception:
        pass  # accounting must never break a fetch


def _api_key() -> str | None:
    k = (os.environ.get("SOLDCOMPS_API_KEY") or "").strip()
    if k:
        return k
    try:
        k = open(KEY_FILE).read().strip()
        return k or None
    except Exception:
        return None


def _request(params: dict, key: str, timeout: int = 45) -> tuple[dict | None, str]:
    """Returns (payload, note). Never raises. Distinguishes quota from rate-limit."""
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "ValleyPawn-SoldReview/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), ""
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            pass
        if e.code == 429:
            code = body.get("code", "")
            if code == "quota_exceeded":
                # HARD STOP. Retrying burns nothing but wastes the run and cannot succeed.
                return None, (f"QUOTA EXHAUSTED for plan '{body.get('plan','?')}' "
                              f"({body.get('used','?')}/{body.get('limit','?')}); "
                              f"resets {body.get('reset_at','?')} — stop until then")
            return None, (f"RATE LIMITED — retry after {body.get('retry_after','?')}s")
        if e.code == 401:
            return None, "AUTH FAILED — API key missing, malformed, or revoked"
        return None, f"HTTP {e.code} — {body.get('error') or 'request failed'}"
    except Exception as e:
        return None, f"request error: {e}"


def fetch_comp(keyword: str, days: int = DEFAULT_DAYS, condition: str = "any",
               use_cache: bool = True) -> dict:
    """
    Fetch + filter + return a defensible sold-comp figure, shaped IDENTICALLY to
    terapeak.parse_page() so it is a drop-in for the same cache and blend logic.

    {value, n, n_raw, low, high, excluded, source, note, keyword}
    `value` is None whenever there isn't enough clean evidence — a valid, honest answer
    the caller must treat as "no external opinion", never as zero.
    """
    out = {"value": None, "n": 0, "n_raw": 0, "low": None, "high": None,
           "excluded": 0, "source": "soldcomps-api", "note": "", "keyword": keyword,
           "condition": condition}

    if use_cache:
        # get_any, not get: a cached MISS is also an answer. Without this,
        # every known-dud keyword was re-fetched (and re-billed) daily.
        # Exception: a cached used-condition miss does NOT satisfy a wider
        # (condition="any") query — the widen-ladder retry must go through.
        hit = cache_get_any(keyword)
        if hit and (hit.get("value") or hit.get("condition", "any") == condition
                    or condition != "any"):
            return hit

    key = _api_key()
    if not key:
        out["note"] = f"no API key (set SOLDCOMPS_API_KEY or create {KEY_FILE})"
        return out

    # Quota guard — degrade, don't die, and NEVER cache the degraded miss
    # (a ceiling-hit is not evidence about the keyword).
    if _usage_today() >= DAILY_CEILING:
        out["note"] = f"daily ceiling reached ({DAILY_CEILING}) — degraded, retry tomorrow"
        out["quota_degraded"] = True
        return out

    since = time.strftime("%Y-%m-%d", time.localtime(time.time() - days * 86400))
    _bump_usage()
    payload, note = _request({
        "keyword": f"{keyword} {NEGATIVE_TERMS}",
        "sold": "true",
        "ebaySite": "ebay.com",
        "itemCondition": condition,
        "soldAfter": since,
        "count": 240,
        "page": 1,
    }, key)

    if payload is None and note.startswith("RATE LIMITED"):
        # transient — wait the hinted interval (capped) and retry once
        m = __import__("re").search(r"(\d+)", note)
        time.sleep(min(int(m.group(1)) if m else 5, 30))
        _bump_usage()
        payload, note = _request({
            "keyword": f"{keyword} {NEGATIVE_TERMS}", "sold": "true",
            "ebaySite": "ebay.com", "itemCondition": condition,
            "soldAfter": since, "count": 240, "page": 1,
        }, key)

    if payload is None:
        out["note"] = note
        if note.startswith("QUOTA EXHAUSTED"):
            # monthly quota gone — signal callers to stop the whole sweep
            out["quota_degraded"] = True
        return out

    items = payload.get("items") or []
    out["n_raw"] = len(items)
    if not items:
        out["note"] = "no sold listings returned for this keyword"
        cache_put(keyword, out)          # cache the miss so we don't retry daily
        return out

    kept = []
    for it in items:
        title = (it.get("title") or "")
        raw   = it.get("soldPrice")      # STRING per the spec
        if raw is None:
            continue
        try:
            price = float(str(raw).replace(",", ""))
        except ValueError:
            continue
        if price <= 0 or PARTS_RE.search(title) or EXTRA_PARTS_RE.search(title):
            continue
        lot = LOT_RE.search(title)
        if lot:                          # normalise multi-packs to per-unit
            try:
                q = int(lot.group(1))
                if 1 < q <= 20:
                    price /= q
            except ValueError:
                pass
        kept.append(price)

    # Cohort-relative price floor — the structural backstop the regex can't be.
    # No parts vocabulary is ever complete; what IS reliable is that a $14 part
    # sits far below the cohort of real units. With a decent sample, drop
    # anything under 20% of the 75th percentile. (A genuine cheap unit sits at
    # 40-60% of p75, nowhere near 20% — verified on the STIHL BG 50 live set.)
    if len(kept) >= 6:
        p75 = sorted(kept)[int(len(kept) * 0.75)]
        kept = [p for p in kept if p >= 0.20 * p75]

    out["excluded"] = len(items) - len(kept)

    if len(kept) < MIN_COMPS:
        out["note"] = (f"only {len(kept)} non-part comp(s) of {len(items)} — "
                       "not enough clean evidence")
        cache_put(keyword, out)
        return out

    s = sorted(kept)
    if len(s) >= 8:                      # trim extremes; mis-titled listings survive filters
        cut = max(1, len(s) // 10)
        s = s[cut:-cut]

    out["value"] = round(statistics.median(s), 2)
    out["n"]     = len(s)
    out["low"], out["high"] = round(min(s), 2), round(max(s), 2)
    out["note"]  = f"{out['excluded']} parts/accessories excluded of {len(items)} raw"
    cache_put(keyword, out)
    return out


def selftest() -> int:
    """Verify the key works end-to-end against a known item. Prints NO secrets."""
    key = _api_key()
    print("=== SoldComps API self-test ===")
    if not key:
        print(f"✗ No API key found.\n  Put it in {KEY_FILE} (just the sc_... string), "
              f"or export SOLDCOMPS_API_KEY.")
        return 1
    print(f"  key loaded: {key[:3]}…{key[-4:]} ({len(key)} chars)")

    # condition="used" mirrors the production path (pawn stock is used; the
    # condition=any pool is dominated by NEW aftermarket parts listings).
    r = fetch_comp("STIHL BG 50", condition="used", use_cache=False)
    if r["value"]:
        print(f"✓ LIVE CALL OK — STIHL BG 50 median ${r['value']:,.2f} "
              f"(n={r['n']} clean, {r['excluded']} parts excluded of {r['n_raw']} raw, "
              f"range ${r['low']:,.2f}-${r['high']:,.2f})")
        print(f"  Terapeak's filtered answer for the same item was $195.00 — "
              f"these should be in the same ballpark.")
        return 0
    print(f"✗ No usable comp: {r['note']}")
    return 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--test":
        sys.exit(selftest())
    if len(a) > 1 and a[0] == "--fetch":
        r = fetch_comp(" ".join(a[1:]))
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["value"] else 1)
    print(__doc__)
