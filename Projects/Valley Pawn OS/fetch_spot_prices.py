#!/usr/bin/env python3
"""
Valley Pawn — Canonical Metals Spot Price Feed
==============================================

WHY THIS EXISTS (2026-08-14)
----------------------------
Gold and silver spot prices were HARDCODED in `Pawn Walks/intake_valuation_engine.py`
as `GOLD_SPOT = 4350.0` / `SILVER_SPOT = 68.0`, dated 2026-06-09. Melt is the single
largest valuation source in the daily intake report (28 of 67 items on 2026-08-13), so
every jewelry and bullion number rode on two literals nobody was updating.

By 2026-08-14 the drift was: gold 4350 vs ~4370 actual (~0.5% — near-right by luck),
silver 68.00 vs ~64.40 actual (~5.6% HIGH). Silver being high is the dangerous
direction — it inflates estimated value, which makes a bad buy look acceptable.

Separately, a `vp-weekly-spot-price-update` scheduled task already fetched live prices
daily — but only wrote them into a WordPress snippet for the customer-facing calculator.
Nothing persisted them where the valuation engine could read. This file closes that gap:
ONE fetch, ONE canonical file, MANY consumers.

DESIGN PRINCIPLE
----------------
A wrong price is worse than a stale price, because a wrong price is silent. Every guard
below exists to refuse bad data rather than propagate it. If this script cannot get a
trustworthy number, it leaves the last known good value in place and says so loudly.

CONSUMERS
---------
  - Pawn Walks/intake_valuation_engine.py  (melt valuation — GOLD_SPOT / SILVER_SPOT)
  - vp-weekly-spot-price-update task       (website calculator HFCM snippet)
  - any future scrap/jewelry pricing work  — read this file, do not re-fetch

USAGE
-----
  python3 fetch_spot_prices.py           # fetch + write (normal daily run)
  python3 fetch_spot_prices.py --check   # read-only: print current state, exit 0/1 on staleness

READING IT FROM PYTHON
----------------------
  from fetch_spot_prices import load_spot
  s = load_spot()
  s["gold"], s["silver"], s["stale"], s["age_hours"]
"""

from __future__ import annotations
import json, os, sys, time, datetime, urllib.request

_HERE      = os.path.dirname(os.path.abspath(__file__))
SPOT_FILE  = os.path.join(_HERE, "spot_prices.json")

# ── Guards ────────────────────────────────────────────────────────────────────
# These are deliberately WIDE. They are not trying to predict the market — they only
# catch data that is structurally wrong: wrong units, wrong currency, a parse failure
# returning 0, or a source returning a per-kilo/per-gram figure instead of per-ozt.
# (Real example encountered while building this: a source quoting silver at "US$88,848
# /troy ounce" — that is a currency/unit artifact, not a price.)
PLAUSIBLE = {
    "gold":   (500.0, 20000.0),   # USD per troy oz
    "silver": (5.0,     500.0),
}

# Silver has genuinely moved >5%/day multiple times in Aug 2026, and its 52-week range
# is $36.97–$121.58 — so a tight day-over-day gate would reject REAL moves. This gate is
# set to catch a source glitch, not a rally. A move beyond this is written but FLAGGED,
# never silently dropped.
MAX_DAILY_MOVE_PCT = 25.0

STALE_AFTER_HOURS = 36.0   # ~1.5 days: a daily feed that missed one run is still usable

# ── Sources ───────────────────────────────────────────────────────────────────
# Primary is keyless and returns clean JSON with its own `updatedAt`. Secondary is used
# ONLY as a cross-check — if the two disagree materially we still write the primary but
# mark the record so consumers know confidence is reduced.
SOURCES = {
    "gold":   {"primary": "https://api.gold-api.com/price/XAU"},
    "silver": {"primary": "https://api.gold-api.com/price/XAG"},
}

CROSS_CHECK_DISAGREE_PCT = 5.0


def _fetch_json(url: str, timeout: int = 20) -> dict | None:
    """GET a JSON endpoint. Returns None on any failure — never raises."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ValleyPawn-SpotFeed/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"    fetch failed {url}: {e}", file=sys.stderr)
        return None


def _extract_price(payload: dict | None) -> float | None:
    """Pull a numeric price out of a source payload, tolerant of key naming."""
    if not isinstance(payload, dict):
        return None
    for key in ("price", "spot", "rate", "value", "ask"):
        v = payload.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    return None


def load_spot() -> dict:
    """
    Read the canonical spot file. ALWAYS returns a usable dict — callers should check
    `stale` and decide whether to trust it, but will never get an exception or a None.

    Returns: {gold, silver, updated_at, age_hours, stale, source, ok, note}
    """
    try:
        with open(SPOT_FILE) as f:
            d = json.load(f)
    except Exception:
        return {"gold": None, "silver": None, "updated_at": None, "age_hours": None,
                "stale": True, "source": "none", "ok": False,
                "note": "spot_prices.json missing or unreadable"}

    age_h = None
    try:
        ts = datetime.datetime.fromisoformat(d["updated_at"])
        if ts.tzinfo is None:
            ts = ts.astimezone()
        age_h = (datetime.datetime.now(ts.tzinfo) - ts).total_seconds() / 3600.0
    except Exception:
        pass

    stale = (age_h is None) or (age_h > STALE_AFTER_HOURS)
    return {
        "gold":       d.get("gold_usd_per_ozt"),
        "silver":     d.get("silver_usd_per_ozt"),
        "updated_at": d.get("updated_at"),
        "age_hours":  round(age_h, 1) if age_h is not None else None,
        "stale":      stale,
        "source":     d.get("source", "unknown"),
        "ok":         bool(d.get("gold_usd_per_ozt") and d.get("silver_usd_per_ozt")),
        "note":       d.get("note", ""),
    }


def _validate(metal: str, new: float | None, prev: float | None) -> tuple[bool, str]:
    """
    Decide whether `new` is trustworthy enough to write.
    Returns (accept, note). Rejection means we keep the previous value.
    """
    if new is None:
        return False, "no price returned by source"

    lo, hi = PLAUSIBLE[metal]
    if not (lo <= new <= hi):
        return False, f"implausible {metal} price ${new:,.2f} (outside ${lo:,.0f}-${hi:,.0f}) — likely a unit/currency error"

    if prev:
        move = abs(new - prev) / prev * 100.0
        if move > MAX_DAILY_MOVE_PCT:
            # Accept but flag — refusing a real 26% move would be worse than noting it.
            return True, f"LARGE MOVE: {metal} {move:+.1f}% vs previous ${prev:,.2f} — verify before trusting downstream valuations"

    return True, ""


def fetch_and_write() -> int:
    """Fetch, validate, and write the canonical file. Returns a process exit code."""
    prev = load_spot()
    now  = datetime.datetime.now().astimezone()
    print(f"=== Valley Pawn spot price feed — {now.isoformat(timespec='seconds')} ===")
    if prev["ok"]:
        print(f"    previous: Au ${prev['gold']:,.2f}  Ag ${prev['silver']:,.2f}  ({prev['age_hours']}h old)")
    else:
        print("    previous: none on file (first run)")

    results, notes, accepted_any = {}, [], False

    for metal in ("gold", "silver"):
        payload = _fetch_json(SOURCES[metal]["primary"])
        price   = _extract_price(payload)
        prev_v  = prev.get(metal)

        accept, note = _validate(metal, price, prev_v)
        if accept:
            results[metal] = round(price, 2)
            accepted_any = True
            delta = ""
            if prev_v:
                delta = f"  ({(price - prev_v) / prev_v * 100:+.2f}%)"
            print(f"    {metal:<7} ${price:,.2f}{delta}")
        else:
            # Keep last known good rather than writing garbage or a zero.
            results[metal] = prev_v
            print(f"    {metal:<7} REJECTED — {note}; keeping ${prev_v if prev_v else 'nothing'}", file=sys.stderr)
        if note:
            notes.append(f"{metal}: {note}")

    if not accepted_any:
        print("ERROR: no metal price could be refreshed — leaving previous file untouched.", file=sys.stderr)
        return 1

    if not (results.get("gold") and results.get("silver")):
        print("ERROR: incomplete price set and no previous value to fall back on.", file=sys.stderr)
        return 1

    record = {
        "updated_at":          now.isoformat(timespec="seconds"),
        "gold_usd_per_ozt":    results["gold"],
        "silver_usd_per_ozt":  results["silver"],
        "source":              "api.gold-api.com (XAU/XAG, keyless JSON)",
        "note":                " | ".join(notes),
        "_comment": ("Canonical metals spot for Valley Pawn. Written by "
                     "Valley Pawn OS/fetch_spot_prices.py. Do NOT hardcode spot prices "
                     "anywhere else — read this file. See the module docstring for why."),
    }

    # Rolling history, newest last, capped. Useful for calibrating premiums later and for
    # answering 'what did we think gold was worth on the day we made that buy?'
    hist = []
    try:
        with open(SPOT_FILE) as f:
            hist = json.load(f).get("history", [])
    except Exception:
        pass
    hist.append({"t": record["updated_at"],
                 "gold": record["gold_usd_per_ozt"],
                 "silver": record["silver_usd_per_ozt"]})
    record["history"] = hist[-400:]

    tmp = SPOT_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(record, f, indent=2)
    os.replace(tmp, SPOT_FILE)   # atomic — a crash mid-write can't corrupt the live file

    print(f"    → {SPOT_FILE}")
    if notes:
        print("    NOTES: " + " | ".join(notes))
    return 0


def main() -> int:
    if "--check" in sys.argv:
        s = load_spot()
        print(json.dumps(s, indent=2))
        if not s["ok"]:
            print("STATUS: NO DATA", file=sys.stderr); return 1
        if s["stale"]:
            print(f"STATUS: STALE ({s['age_hours']}h old)", file=sys.stderr); return 1
        print("STATUS: OK")
        return 0
    return fetch_and_write()


if __name__ == "__main__":
    sys.exit(main())
