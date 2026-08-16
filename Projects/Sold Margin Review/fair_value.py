#!/usr/bin/env python3
"""
Valley Pawn — Fair Value v2 (precision-weighted, channel-normalized blend)
==========================================================================

WHAT THIS ANSWERS vs WHAT market_benchmark.py ANSWERS — read this first
-----------------------------------------------------------------------
ONE question was doing two jobs (BLEND_V2_PLAN.md, 2026-08-14):

  FLAG FLOOR  "is this sale bad enough to alert on?"  -> market_benchmark.py.
              Deliberately CONSERVATIVE (lower-of on disagreement, 3.3% flag
              rate, validated). UNCHANGED by this module. Flags still fire
              exclusively off that engine.

  FAIR VALUE  "what SHOULD this item have sold for?"  -> THIS module.
              Wants the most ACCURATE estimate, not the safest one. New.

The daily report shows FAIR VALUE per item; flags keep firing off the
conservative floor. Same data, two purposes, no longer conflated.

THE THREE ACCURACY FIXES (vs the v1 blend)
------------------------------------------
1. No more lower-of. Sources are blended BY PRECISION: weight ∝ n/(1+cv).
   A 45-sale tight internal comp outweighs a 6-sale scattered eBay comp,
   and vice versa. No hardcoded 65/35.
2. Channel normalization — an eBay sold price is a DIFFERENT MARKET:
   seller nets ~87% after fees, free-shipping listings absorb label cost,
   and comps mix new+used unless condition-filtered. We convert eBay gross
   to NET-EQUIVALENT before comparing:  net = gross*(1-fee) - ship_absorb.
   Constants start from eBay's published schedule and are OVERRIDDEN by
   .channel_calibration.json when calibrate_fees.py has measured our own
   stores' real fee ratio (Phase 4).
3. Time decay — a May 2025 sale is not a last-week sale. Internal comps are
   weighted with a half-life of 6 months for electronics/tools, 12 months
   for everything else. Recent sales dominate.

Disagreement >30% AFTER normalization is a FINDING, not a nuisance: we do
not average it away — both numbers are reported and the pair is logged to
pricing_health.jsonl. Persistent per-category disagreement IS the
systematic-underpricing signal (STIHL: we realize $104 vs $195 market).

ELIGIBILITY LADDER (coverage: every item, every day — no 8-item cap)
--------------------------------------------------------------------
  a) Precious metals -> melt (live spot via Pawn Walks engine). Never comped.
  b) Firearms        -> internal comps only. NEVER eBay (prohibited there;
                        a GLOCK query returns $30 holsters, not $500 pistols).
  c) Everything else -> SoldComps API, condition=used (pawn stock is used),
                        model-key query first, brand+category fallback.

Quota: ~35-40 fresh lookups/day vs 2,000/mo plan. Hard safety ceiling lives
in soldcomps.py (60/day, shared by every caller); lookups here are ordered
by SALE VALUE so if the guard trips, the $400 item got its comp and the $9
item degraded. Cache (30d, shared with Terapeak) makes repeat models free.

USAGE
-----
  python3 fair_value.py --lookup-all 2026-08-13   # fill cache for a sold day (API, no browser)
  python3 fair_value.py --estimate "STIHL BG 50 LEAF BLOWER" "Leaf Blower"
  python3 fair_value.py --validate                # weekly backtest, MAPE per estimator
  python3 fair_value.py --health                  # pricing-health aggregate
"""

from __future__ import annotations
import os, re, csv, glob, json, math, statistics, sys, datetime

_HERE        = os.path.dirname(os.path.abspath(__file__))
BRAVO_OUTPUT = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/"
PAWN_WALKS   = "/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks"

HEALTH_FILE  = os.path.join(_HERE, "pricing_health.jsonl")
CAL_FILE     = os.path.join(_HERE, ".channel_calibration.json")
VALID_FILE   = os.path.join(_HERE, "validation_history.jsonl")

# Shared vocabulary — imported, never redefined, so this engine can NEVER
# disagree with the flag engine about what a metal, a gun, or a model key is.
from market_benchmark import (PM_RE, FIREARM_RE, money, model_keys, brand_of,
                              MIN_INTERNAL_N_USE)
from terapeak import get as cache_get, MIN_COMPS

# ── Channel normalization constants (defaults; calibration file overrides) ────
# Fee: eBay final value fee is ~12.9-13.25% + $0.30 for most categories we sell.
# Calibrated by calibrate_fees.py from OUR OWN stores' real transactions.
DEFAULT_FEE_RATE = 0.13

# Shipping the seller absorbs on a typical free-shipping listing, by rough
# category group. These are the plan's "shipping_absorbed(category)".
SHIP_GROUPS = [
    (re.compile(r'\b(MOWER|GENERATOR|WELDER|COMPRESSOR|PRESSURE\s*WASHER|TILLER)\b', re.I), 25.0),
    (re.compile(r'\b(SAW|DRILL|BLOWER|TRIMMER|GRINDER|SANDER|ROUTER|NAILER|TOOL|WRENCH|JACK)\b', re.I), 15.0),
    (re.compile(r'\b(TV|MONITOR|GUITAR|AMP|AMPLIFIER|SPEAKER|SUBWOOFER|KEYBOARD|PIANO)\b', re.I), 20.0),
    (re.compile(r'\b(LAPTOP|CONSOLE|TABLET|CAMERA|DRONE|GPU|COMPUTER|STEREO|RECEIVER)\b', re.I), 12.0),
    (re.compile(r'\b(RING|NECKLACE|CHAIN|BRACELET|EARRING|PENDANT|WATCH|COIN)\b', re.I), 5.0),
    (re.compile(r'\b(GAME|DVD|BLU-?RAY|CD|BOOK|PHONE|AIRPODS|EARBUD)\b', re.I), 6.0),
]
DEFAULT_SHIP_ABSORB = 10.0

# Time decay half-lives (days). Electronics/tools move; most else is flat-ish.
FAST_DECAY_RE = re.compile(
    r'\b(TV|LAPTOP|TABLET|PHONE|CONSOLE|GAME|GAMING|CAMERA|GPU|COMPUTER|MONITOR|'
    r'DRONE|AUDIO|SPEAKER|HEADPHONE|EARBUD|SMART|STEREO|RECEIVER|SAW|DRILL|'
    r'MOWER|BLOWER|TRIMMER|GRINDER|SANDER|WELDER|GENERATOR|PRESSURE|TOOL)\b', re.I)
HALF_LIFE_FAST = 182.0    # ~6 months
HALF_LIFE_SLOW = 365.0    # ~12 months

# Disagreement threshold AFTER channel normalization. Above this we refuse to
# average — both numbers are surfaced and the pair feeds pricing health.
DISPUTE_BAND = 0.30

# Categories where new-in-box is common pawn stock -> query condition=any.
NEW_OK_RE = re.compile(r'\b(SEALED|NIB|NEW IN BOX|UNOPENED)\b', re.I)

# ── Keyword specificity guard (added 2026-08-14, first live sweep) ────────────
# A comp is only as good as its keyword. The first full sweep proved that
# generic descriptions produce confidently WRONG externals:
#   "MISC TOOLS"       -> $17.66 net (comped against random tool listings)
#   "APPLE IPAD PRO"   -> $341 net (every iPad Pro generation pooled)
#   "NINTENDO SWITCH"  -> $39.50 net (games + joycons contaminate 'used Switch')
# Rule: an external lookup requires a MODEL KEY, or a non-generic brand plus at
# least one more meaningful token. Items failing this stay internal-only —
# honest "no external opinion" beats a precise-looking wrong number.
GENERIC_LEADS = frozenset(
    "MISC ASSORTED VARIOUS LOT COMIC BOOK BOOKS TOOLS TOOL JEWELRY GAME GAMES "
    "MOVIE MOVIES DVD CD VHS TOY TOYS BUNDLE ELECTRONICS ACCESSORY".split())
# Product families whose used-market listings are dominated by accessories/
# games rather than the item itself — external comp structurally unreliable.
# Proven live 2026-08-15: a $450 PS5 drew "fair ~$37" because used
# 'PLAYSTATION 5' sold listings are overwhelmingly $20-40 games and
# controllers. Consoles stay INTERNAL-ONLY — we sell plenty, the internal
# index is deep (n=hundreds), and it can't be games-contaminated.
AMBIGUOUS_RE = re.compile(
    r'\b(NINTENDO\s+SWITCH|XBOX|PLAY\s*STATION|PS[2345]\b|WII\b|GAME\s*CUBE|'
    r'GAMING\s+CONSOLE)\b', re.I)


def keyword_ok(desc: str) -> bool:
    d = re.sub(r'\s+', ' ', (desc or '').upper()).strip()
    if not d or AMBIGUOUS_RE.search(d):
        return False
    if model_keys(d):
        return True
    b = brand_of(d)
    if not b or b in GENERIC_LEADS:
        return False
    # brand alone is not a keyword ("DEWALT" comps a $30 bit set vs $400 kit)
    rest = [t for t in d.split() if t != b]
    return len(rest) >= 1


def _load_calibration() -> dict:
    try:
        with open(CAL_FILE) as f:
            d = json.load(f)
        if 0.05 <= float(d.get("fee_rate", 0)) <= 0.25:
            return d
    except Exception:
        pass
    return {}


_CAL = _load_calibration()
FEE_RATE = float(_CAL.get("fee_rate", DEFAULT_FEE_RATE))


def ship_absorb(desc: str, category: str) -> float:
    blob = f"{desc} {category}"
    for rx, amt in SHIP_GROUPS:
        if rx.search(blob):
            return float(_CAL.get("ship_absorb", {}).get(str(amt), amt)) if _CAL else amt
    return DEFAULT_SHIP_ABSORB


def ebay_net(gross: float, desc: str, category: str) -> float:
    """Channel-normalize an eBay sold GROSS price to a net-equivalent our
    counter could be compared against. Never below 50% of gross (sanity)."""
    n = gross * (1.0 - FEE_RATE) - ship_absorb(desc, category)
    return round(max(n, gross * 0.5), 2)


def half_life_for(desc: str, category: str) -> float:
    return HALF_LIFE_FAST if FAST_DECAY_RE.search(f"{desc} {category}") else HALF_LIFE_SLOW


# ── Weighted statistics ───────────────────────────────────────────────────────
def _wpctl(pairs: list[tuple[float, float]], q: float) -> float:
    """Weighted percentile of [(value, weight)] — q in [0,1]."""
    s = sorted(pairs)
    tot = sum(w for _, w in s)
    if tot <= 0:
        return s[len(s) // 2][0]
    acc = 0.0
    for v, w in s:
        acc += w
        if acc >= q * tot:
            return v
    return s[-1][0]


def _decayed_stats(pairs: list[tuple[float, float]]) -> dict:
    """pairs = [(price, weight)] -> {median, p25, p75, n_eff, cv}"""
    med = _wpctl(pairs, 0.50)
    p25, p75 = _wpctl(pairs, 0.25), _wpctl(pairs, 0.75)
    n_eff = sum(w for _, w in pairs)
    cv = ((p75 - p25) / (2.0 * med)) if med else 1.0
    return {"median": round(med, 2), "p25": round(p25, 2), "p75": round(p75, 2),
            "n_eff": round(n_eff, 1), "n_raw": len(pairs), "cv": round(max(cv, 0.02), 3)}


# ── Engine ────────────────────────────────────────────────────────────────────
class FairValueEngine:
    """
    Time-decayed internal comp index. Built separately from market_benchmark's
    (which stays untouched — Rule #4) because this one must carry DATES.
    """

    def __init__(self, exclude_date: str | None = None, ref_date: str | None = None,
                 allow_live_api: bool = True, verbose: bool = False):
        self.exclude = exclude_date
        self.ref = datetime.date.fromisoformat(ref_date) if ref_date else datetime.date.today()
        self.allow_live_api = allow_live_api
        self.verbose = verbose
        # key -> [(price, age_days)]
        self.model: dict[str, list] = {}
        self.brand_cat: dict[tuple, list] = {}
        self._build()

    def _iter_files(self):
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_inventory-details.csv"))
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_sold-discount-detail.csv"))
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_jewelry-margin-sold.csv"))

    @staticmethod
    def _parse_date(s: str):
        s = (s or "").strip()
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    def _build(self):
        exc = set()
        if self.exclude:
            y, m, d = self.exclude.split("-")
            exc = {f"{int(m)}/{int(d)}/{y}", self.exclude}
        rows = 0
        for path in self._iter_files():
            try:
                with open(path, newline="", encoding="utf-8-sig") as f:
                    for r in csv.DictReader(f):
                        if (r.get("Status") or "").strip().upper() != "SOLD":
                            continue
                        ds = (r.get("Date") or "").strip()
                        if ds in exc:
                            continue
                        price = money(r.get("Last Sold Price"))
                        if not price:
                            continue
                        desc = r.get("Description") or ""
                        if PM_RE.search(desc):
                            continue
                        sold = self._parse_date(ds)
                        age = (self.ref - sold).days if sold else 400
                        age = max(age, 0)
                        cat = (r.get("Category") or "").strip().upper()
                        for k in model_keys(desc):
                            self.model.setdefault(k, []).append((price, age))
                        b = brand_of(desc)
                        if b and cat:
                            self.brand_cat.setdefault((b, cat), []).append((price, age))
                        rows += 1
            except Exception as e:
                if self.verbose:
                    print(f"  skip {os.path.basename(path)}: {e}", file=sys.stderr)
        if self.verbose:
            print(f"  fair-value index: {len(self.model):,} model keys, "
                  f"{len(self.brand_cat):,} brand-cats from {rows:,} dated sold rows")

    # ── internal (time-decayed) ───────────────────────────────────────────────
    def internal(self, desc: str, category: str) -> dict | None:
        hl = half_life_for(desc, category)
        best = None
        # Consoles: "PS5" as a model key matches every GAME with PS5 in the
        # title ($20-40), polluting the comp from the inside (live 2026-08-15:
        # a $450 PS5 drew fair ~$37 from our own games history). For AMBIGUOUS
        # items skip the model tier — brand+category separates 'Video Game
        # System' from 'Video Games' and gives the honest console comp.
        mk = [] if AMBIGUOUS_RE.search(desc or "") else model_keys(desc)
        for k in mk:
            raw = self.model.get(k)
            if not raw or len(raw) < MIN_INTERNAL_N_USE:
                continue
            pairs = [(p, 0.5 ** (age / hl)) for p, age in raw]
            st = _decayed_stats(pairs)
            st["tier"] = "model"
            if best is None or st["n_eff"] > best["n_eff"]:
                best = st
        if best:
            return best
        b = brand_of(desc)
        cat = (category or "").strip().upper()
        raw = self.brand_cat.get((b, cat)) if (b and cat) else None
        if raw and len(raw) >= MIN_INTERNAL_N_USE:
            pairs = [(p, 0.5 ** (age / hl)) for p, age in raw]
            st = _decayed_stats(pairs)
            st["tier"] = "brand-cat"
            return st
        return None
        # NOTE: no bare-category tier here on purpose. A category p25 is a flag
        # floor, not a fair value — pretending it estimates a specific item
        # would be false precision. Items with no model/brand match and no
        # external comp honestly return None.

    # ── external (SoldComps/Terapeak shared cache; quota-guarded live) ────────
    def external(self, desc: str, category: str) -> dict | None:
        if FIREARM_RE.search(desc or "") or FIREARM_RE.search(category or ""):
            return None
        if not keyword_ok(desc):
            return None  # generic/ambiguous keyword -> no external opinion
        from market_benchmark import BenchmarkEngine
        kws = BenchmarkEngine.terapeak_keywords(desc)
        entry = None
        for kw in kws:
            entry = cache_get(kw)
            if entry and entry.get("value"):
                break
        if (not entry or not entry.get("value")) and self.allow_live_api and kws:
            try:
                from soldcomps import fetch_comp
                cond = "any" if NEW_OK_RE.search(desc or "") else "used"
                r = fetch_comp(kws[0], condition=cond)
                # Widen-ladder (added 2026-08-14): niche brands (FIELDPIECE,
                # BLCKTEC...) often have too few USED sales in 90 days to clear
                # MIN_COMPS. Before declaring "no opinion" on a real item, widen
                # once: any condition, 180 days. A wider comp with n listed
                # beats no comp — the n and cv keep its weight honest.
                if (not r or not r.get("value")) and not r.get("quota_degraded"):
                    r = fetch_comp(kws[0], condition="any", days=180)
                if r and r.get("value"):
                    entry = r
            except Exception:
                entry = None
        if not entry or not entry.get("value"):
            return None
        gross = float(entry["value"])
        n = int(entry.get("n") or MIN_COMPS)
        lo, hi = entry.get("low"), entry.get("high")
        cv = ((float(hi) - float(lo)) / (2.0 * gross)) if (lo and hi and gross) else 0.35
        return {"gross": round(gross, 2),
                "net": ebay_net(gross, desc, category),
                "n": n, "cv": round(max(min(cv, 1.5), 0.02), 3),
                "source": entry.get("source", "cache")}

    # ── melt ──────────────────────────────────────────────────────────────────
    _melt_fn = "unloaded"

    def melt(self, desc: str, category: str):
        if FairValueEngine._melt_fn == "unloaded":
            try:
                sys.path.insert(0, PAWN_WALKS)
                from intake_valuation_engine import melt_value
                FairValueEngine._melt_fn = melt_value
            except Exception:
                FairValueEngine._melt_fn = None
        if FairValueEngine._melt_fn:
            try:
                v, note = FairValueEngine._melt_fn(category, desc)
                if v:
                    return round(float(v), 2), note
            except Exception:
                pass
        return None, "melt engine unavailable"

    # ── the blend ─────────────────────────────────────────────────────────────
    def estimate(self, desc: str, category: str, sale_price: float | None = None,
                 store: str | None = None, date: str | None = None) -> dict:
        """
        Returns:
          {fair, band, basis, disputed, internal:{...}|None, external:{...}|None,
           weights:{internal, external}, note}
        fair=None is a valid honest answer ("no opinion"), never zero.
        """
        out = {"fair": None, "band": None, "basis": "", "disputed": False,
               "internal": None, "external": None, "weights": None, "note": ""}

        # (a) precious metals -> melt, never comped
        if PM_RE.search(desc or ""):
            v, note = self.melt(desc, category)
            if v:
                out.update(fair=v, band=round(v * 0.08, 2), basis="melt", note=note)
            else:
                out.update(basis="melt", note=f"precious metal — {note}")
            return out

        iv = self.internal(desc, category)
        # (b) firearms -> internal only, never eBay
        ev = None if FIREARM_RE.search(f"{desc} {category}") else self.external(desc, category)
        out["internal"], out["external"] = iv, ev

        if iv and ev:
            spread = abs(iv["median"] - ev["net"]) / max(iv["median"], ev["net"])
            w_i = iv["n_eff"] / (1.0 + iv["cv"])
            w_e = ev["n"] / (1.0 + ev["cv"])
            out["weights"] = {"internal": round(w_i, 2), "external": round(w_e, 2)}
            if spread > DISPUTE_BAND:
                # A finding, not a nuisance. Do NOT average. Point estimate is
                # the higher-precision source; both are surfaced; pair logged.
                out["disputed"] = True
                lead = iv if w_i >= w_e else {"median": ev["net"]}
                out["fair"] = round(lead["median"], 2)
                out["basis"] = (f"DISPUTED int ${iv['median']:,.0f} vs ebay-net "
                                f"${ev['net']:,.0f} ({spread*100:.0f}% apart)")
                d_i = (iv["p75"] - iv["p25"]) / 2.0
                out["band"] = round(max(d_i, abs(iv["median"] - ev["net"]) / 2.0), 2)
                _health_log(date, store, category, desc, sale_price,
                            iv["median"], ev["gross"], ev["net"], disputed=True)
            else:
                blend = (w_i * iv["median"] + w_e * ev["net"]) / (w_i + w_e)
                out["fair"] = round(blend, 2)
                out["basis"] = (f"blend int(n_eff={iv['n_eff']},{iv['tier']}) + "
                                f"ebay-net(n={ev['n']})")
                d_i = (iv["p75"] - iv["p25"]) / 2.0
                d_e = ev["cv"] * ev["net"]
                pooled = math.sqrt((w_i * d_i ** 2 + w_e * d_e ** 2) / (w_i + w_e))
                out["band"] = round(pooled, 2)
                _health_log(date, store, category, desc, sale_price,
                            iv["median"], ev["gross"], ev["net"], disputed=False)
        elif iv:
            out["fair"] = iv["median"]
            out["band"] = round((iv["p75"] - iv["p25"]) / 2.0, 2)
            out["basis"] = f"internal {iv['tier']} n_eff={iv['n_eff']}"
        elif ev:
            out["fair"] = ev["net"]
            out["band"] = round(ev["cv"] * ev["net"], 2)
            out["basis"] = f"ebay-net only n={ev['n']}"
        else:
            out["note"] = "no internal history, no external comp — no opinion"
        return out


# ── Pricing-health aggregate (the money finding) ─────────────────────────────
def _health_log(date, store, category, desc, our_price, internal, ebay_gross,
                ebay_net_v, disputed):
    """Accumulate {category, our_price, ebay_net} pairs. Append-only JSONL."""
    try:
        rec = {"date": date or datetime.date.today().isoformat(), "store": store,
               "category": (category or "").strip().upper() or "UNKNOWN",
               "desc": (desc or "")[:60], "our_price": our_price,
               "internal": internal, "ebay_gross": ebay_gross,
               "ebay_net": ebay_net_v, "disputed": bool(disputed),
               "logged_at": datetime.datetime.now().isoformat(timespec="seconds")}
        with open(HEALTH_FILE, "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass  # health logging must never break an estimate


def health_aggregate(min_n: int = 30, days: int = 90) -> list[dict]:
    """
    Per-category: how do OUR realized prices sit vs eBay net?  Gated on n>=min_n
    so it never publishes confident noise. Dedup by (date,desc) so a re-run of
    the same day doesn't double-count.
    """
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    seen, by_cat = set(), {}
    try:
        with open(HEALTH_FILE) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if (r.get("date") or "") < cutoff:
                    continue
                key = (r.get("date"), r.get("desc"), r.get("store"))
                if key in seen:
                    continue
                seen.add(key)
                if not (r.get("our_price") and r.get("ebay_net")):
                    continue
                by_cat.setdefault(r["category"], []).append(
                    (float(r["our_price"]), float(r["ebay_net"])))
    except FileNotFoundError:
        return []

    out = []
    for cat, pairs in by_cat.items():
        if len(pairs) < min_n:
            continue
        ratios = sorted(o / e for o, e in pairs if e > 0)
        med = ratios[len(ratios) // 2]
        out.append({"category": cat, "n": len(pairs),
                    "median_vs_ebay_net": round((med - 1.0) * 100, 1),
                    "our_median": round(statistics.median(o for o, _ in pairs), 2),
                    "ebay_net_median": round(statistics.median(e for _, e in pairs), 2)})
    return sorted(out, key=lambda r: r["median_vs_ebay_net"])


def health_lines(min_n: int = 30) -> list[str]:
    """Slack-ready lines, only for categories that clear the sample gate."""
    rows = health_aggregate(min_n=min_n)
    lines = []
    for r in rows:
        arrow = "🔻" if r["median_vs_ebay_net"] < -15 else ("▫️" if abs(r["median_vs_ebay_net"]) <= 15 else "🔺")
        lines.append(f"{arrow} {r['category'].title()}: our prices {r['median_vs_ebay_net']:+.0f}% "
                     f"vs eBay net (n={r['n']})")
    return lines


# ── Coverage driver: fill the cache for a sold day (no cap, no browser) ───────
def lookup_all(date: str, ceiling: int | None = None) -> dict:
    """
    Eligibility ladder over EVERY sold item for `date`, ordered by sale value
    (highest first) so quota degradation hits the cheapest items. Uses the
    SoldComps API only; quota guard lives in soldcomps.fetch_comp itself.
    """
    from market_benchmark import BenchmarkEngine
    from soldcomps import fetch_comp
    stats = {"date": date, "items": 0, "eligible": 0, "cached": 0, "fetched": 0,
             "missed": 0, "quota_stopped": False}
    rows = []
    for path in glob.glob(os.path.join(BRAVO_OUTPUT, f"{date}_to_{date}_*_sold-discount-detail.csv")):
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if (r.get("Status") or "").strip().upper() != "SOLD":
                    continue
                sale = money(r.get("Last Sold Price"))
                if sale:
                    rows.append((sale, r.get("Description", ""), r.get("Category", "")))
    stats["items"] = len(rows)
    seen = set()
    done = 0
    for sale, desc, cat in sorted(rows, reverse=True):
        if PM_RE.search(desc) or FIREARM_RE.search(desc) or FIREARM_RE.search(cat):
            continue  # melt / internal-only — never comped externally
        if not keyword_ok(desc):
            continue  # generic keyword would buy a confidently wrong comp
        kws = BenchmarkEngine.terapeak_keywords(desc)
        if not kws:
            continue
        kw = kws[0]
        if kw in seen:
            continue
        seen.add(kw)
        stats["eligible"] += 1
        from terapeak import get_any
        prior = get_any(kw)
        if prior and prior.get("value"):
            stats["cached"] += 1
            continue
        if prior and prior.get("condition") == "any":
            stats["cached"] += 1     # already widened and still a miss — done
            continue
        if ceiling is not None and done >= ceiling:
            continue
        cond = "any" if NEW_OK_RE.search(desc) else "used"
        r = fetch_comp(kw, condition=cond)
        done += 1
        if r.get("quota_degraded"):
            stats["quota_stopped"] = True
            break
        if not r.get("value"):
            # widen once: any condition, 180 days (niche used markets are thin)
            r = fetch_comp(kw, condition="any", days=180)
            done += 1
            if r.get("quota_degraded"):
                stats["quota_stopped"] = True
                break
        if r.get("value"):
            stats["fetched"] += 1
        else:
            # model-key query failed -> brand+category fallback ("COACH KLARE
            # CROSSBODY" -> "COACH crossbody"): one retry, cheap, often lands.
            b = brand_of(desc)
            if b and cat and len(kws) > 1:
                r2 = fetch_comp(f"{b} {cat}".strip(), condition=cond)
                done += 1
                if r2.get("value"):
                    stats["fetched"] += 1
                else:
                    stats["missed"] += 1
                if r2.get("quota_degraded"):
                    stats["quota_stopped"] = True
                    break
            else:
                stats["missed"] += 1
    return stats


# ── Validation loop: accuracy as a measured number, not a claim ───────────────
def validate(days: int = 7) -> dict:
    """
    For every item sold in the last `days` that ALSO has >=2 prior internal
    sales: what would each estimator have predicted vs the realized price?
      internal-only | ebay-net-only | blend-v2 | lower-of (old rule)
    Reports MAPE per estimator. Blend weights get tuned from THIS, publicly.
    """
    dates = sorted({os.path.basename(p).split("_")[0] for p in
                    glob.glob(os.path.join(BRAVO_OUTPUT, "*_sold-discount-detail.csv"))})[-days:]
    errs = {"internal": [], "ebay_net": [], "blend_v2": [], "lower_of": []}
    n_items = 0
    for d in dates:
        eng = FairValueEngine(exclude_date=d, ref_date=d, allow_live_api=False)
        for path in glob.glob(os.path.join(BRAVO_OUTPUT, f"{d}_to_{d}_*_sold-discount-detail.csv")):
            with open(path, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    if (r.get("Status") or "").strip().upper() != "SOLD":
                        continue
                    sale = money(r.get("Last Sold Price"))
                    desc, cat = r.get("Description", ""), r.get("Category", "")
                    if not sale or sale < 10 or PM_RE.search(desc):
                        continue
                    iv = eng.internal(desc, cat)
                    if not iv or iv["n_raw"] < 2:
                        continue  # criterion: >=2 prior internal sales
                    ev = None if FIREARM_RE.search(f"{desc} {cat}") else eng.external(desc, cat)
                    est = eng.estimate(desc, cat, sale, date=d)
                    n_items += 1
                    errs["internal"].append(abs(iv["median"] - sale) / sale)
                    if ev:
                        errs["ebay_net"].append(abs(ev["net"] - sale) / sale)
                        errs["lower_of"].append(abs(min(iv["median"], ev["net"]) - sale) / sale)
                    if est["fair"]:
                        errs["blend_v2"].append(abs(est["fair"] - sale) / sale)
    out = {"window_days": days, "dates": dates, "n_items": n_items,
           "mape": {k: (round(100 * statistics.mean(v), 1) if v else None)
                    for k, v in errs.items()},
           "n_per": {k: len(v) for k, v in errs.items()},
           "ran_at": datetime.datetime.now().isoformat(timespec="seconds")}
    try:
        with open(VALID_FILE, "a") as f:
            f.write(json.dumps(out) + "\n")
    except Exception:
        pass
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--lookup-all":
        d = a[1] if len(a) > 1 else (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        print(json.dumps(lookup_all(d), indent=2))
    elif a and a[0] == "--estimate" and len(a) >= 2:
        eng = FairValueEngine(allow_live_api="--no-api" not in a)
        r = eng.estimate(a[1], a[2] if len(a) > 2 and not a[2].startswith("--") else "")
        print(json.dumps(r, indent=2))
    elif a and a[0] == "--validate":
        r = validate(int(a[1]) if len(a) > 1 else 7)
        print(json.dumps(r, indent=2))
        m = r["mape"]
        if m.get("blend_v2") is not None and m.get("internal") is not None:
            verdict = ("blend-v2 BEATS internal-only" if m["blend_v2"] <= m["internal"]
                       else "blend-v2 LOSES to internal-only — revisit weighting (publicly)")
            print(f"\n{verdict}: blend {m['blend_v2']}% vs internal {m['internal']}% MAPE")
    elif a and a[0] == "--health":
        min_n = int(a[1]) if len(a) > 1 else 30
        rows = health_aggregate(min_n=min_n)
        if rows:
            for ln in health_lines(min_n=min_n):
                print(ln)
        else:
            print(f"(no category has n>={min_n} pairs yet — keeps accumulating daily)")
    else:
        print(__doc__)
