#!/usr/bin/env python3
"""
Valley Pawn — Sold-Side Market Benchmark
========================================

THE PROBLEM THIS SOLVES
-----------------------
The daily Sold Review grades realized margin: (Last Sold Price - Cost) / Last Sold Price.
That answers "did we make money," NOT "did we sell it too cheap." An item bought for $10,
genuinely worth $200, sold for $60 shows an 83% margin and never flags. It looks like a
win. That is the actual blind spot Joshua cares about.

This module supplies the missing benchmark: what SHOULD this item have sold for?

TWO SOURCES, BLENDED — AND WHY IT LEANS LOW
-------------------------------------------
  INTERNAL  what Valley Pawn actually gets for this item (our own realized sales,
            pooled across stores). High trust, zero coverage for items we've never sold.
  EXTERNAL  wider market via eBay (tier3_valuation). Covers items we've never sold, but
            it is active-listing-derived (x0.88 approximation), noisy, and only resolves
            ~35% of lookups.

When both exist we do NOT simply average. The blend is deliberately CONSERVATIVE —
it leans to the lower benchmark, and on material disagreement it takes the lower outright.

Reason: on the SOLD side the error cost is asymmetric and inverted from the intake side.
An inflated benchmark manufactures false "you sold too cheap" alarms. A report that cries
wolf gets ignored, and then it protects nothing. Under-flagging costs us one missed item;
over-flagging costs us the entire report's credibility. So when it flags, it should be real.

CONFIDENCE IS A FIRST-CLASS OUTPUT
----------------------------------
Every benchmark carries a confidence. The caller must refuse to flag on low confidence.
"No opinion" is a valid, honest answer and is returned often — that is correct behaviour,
not a gap to paper over with a guess.

USAGE
-----
    from market_benchmark import BenchmarkEngine
    eng = BenchmarkEngine(use_external=True)
    b = eng.benchmark(description, category, sale_price)
    # b = {value, confidence, source, internal_n, internal, external, note, flag_below}
"""

from __future__ import annotations
import os, re, csv, glob, json, statistics, sys, datetime

_HERE        = os.path.dirname(os.path.abspath(__file__))
BRAVO_OUTPUT = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/"
PAWN_WALKS   = "/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks"

# ── Tunables ──────────────────────────────────────────────────────────────────
# Flag when the realized sale is below this fraction of the benchmark. 0.70 = "sold for
# less than 70% of what this normally brings." Calibrate with backtest_benchmark() before
# trusting — the right value is whatever produces an ACTIONABLE flag rate (~2-5% of items),
# not whatever feels principled.
FLOOR_RATIO = 0.70

# Two benchmarks within this band are considered corroborating; beyond it they disagree
# and we stop trusting the higher one.
AGREE_BAND = 0.25

MIN_INTERNAL_N_HIGH = 3      # >=3 of our own past sales -> high confidence
MIN_INTERNAL_N_USE  = 2      # <2 past sales is a single data point, treat as weak

# Never flag a gap smaller than this in absolute dollars, regardless of percentage.
# Backtest 2026-08-14 surfaced 'SPRINGFIELD XD9 $11.40 vs $16.62 benchmark' — a
# technically-valid 69%-of-benchmark flag that is $5 of exposure. Nobody acts on $5, and
# a report full of $5 findings trains you to ignore it. Percentage alone is not enough.
MIN_GAP_DOLLARS = 25.0

# Category-only comps are a coarse net (see _build_index) and must clear a wider bar.
#
# IMPORTANT — category uses the 25th PERCENTILE, not the median. Categories have huge
# internal price dispersion (186 guitars spanning budget to premium), so the median is a
# poor benchmark for any single item. Backtest 2026-08-14 proved it: an INDIO budget
# guitar sold at $76 flagged against a $170 all-guitar median — a false positive created
# purely by comparing a cheap brand to a mixed population. Using the bottom quartile as
# 'the floor of normal' means we only flag items that undercut even the cheap end of the
# category, which is what 'sold way too cheap' actually means.
CATEGORY_PCTL        = 25     # percentile used as the category floor-of-normal
CATEGORY_FLOOR_RATIO = 0.75   # flag only below 75% of that floor
MIN_CATEGORY_N       = 12     # and only on a decent sample

# Precious metals are valued by melt (Tier 1) and are not resale-comparable items —
# never benchmark or flag them here.
PM_RE = re.compile(r'\b(GOLD|SILVER|STERLING|925|14K|10K|18K|22K|24K|PLATINUM|BULLION|'
                   r'SCRAP|MELT|COIN|DWT|OZT)\b', re.I)

# FIREARMS — never send these to eBay/Terapeak. eBay PROHIBITS firearm sales (see the
# `ebay-context` skill's "NEVER list" section), so a search for 'GLOCK 19' returns holsters,
# magazines and sights — not pistols. Using that as a market comp would be the parts-
# contamination bug in its worst form: a $500 pistol benchmarked against $30 of accessories,
# which would then flag every legitimate firearm sale as 'sold too cheap'.
# Caught 2026-08-14 when the candidate list surfaced GLOCK 19 / PHOENIX HP22A / HOLOSUN.
# Internal comps still work fine for guns (we sell plenty), and `tier3_valuation.py` routes
# firearms to gun-value sites for the intake side. This exclusion is Terapeak-only.
FIREARM_RE = re.compile(
    r'\b(PISTOL|REVOLVER|RIFLE|SHOTGUN|FIREARM|HANDGUN|CARBINE|AR-?15|AK-?47|'
    r'GLOCK|RUGER|SMITH\s*&?\s*WESSON|S&W|SIG|SAUER|BERETTA|TAURUS|SPRINGFIELD\s+ARMORY|'
    r'REMINGTON|WINCHESTER|MOSSBERG|HENRY|MARLIN|BROWNING|COLT|KIMBER|WALTHER|'
    r'HI-?POINT|PHOENIX\s+HP|CZ\s|FN\s|HK\s|HECKLER|SCOPE|OPTIC|RED\s*DOT|HOLOSUN|'
    r'VORTEX|LEUPOLD|BUSHNELL|AMMO|AMMUNITION|MAGAZINE)\b', re.I)

STOP = frozenset(
    "THE AND FOR WITH MODEL SERIAL NUMBER NO SIZE COLOR USED NEW ITEM MISC GENT GENTS "
    "LADY LADYS LADIES MENS WOMENS BLACK WHITE BLUE RED GREEN CHROME MATTE NOT INCLUDED "
    "STAINLESS POLYMER SYNTHETIC WOOD OAK WALNUT HAND TOOL GENERAL SET PIECE PC".split()
)


def money(x) -> float | None:
    """Parse '$1,234.56' -> 1234.56. Returns None for blanks/junk rather than raising."""
    s = str(x or "").replace("$", "").replace(",", "").strip()
    if s in ("", "-", "N/A"):
        return None
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None


def model_keys(desc: str) -> list[str]:
    """
    Digit-bearing tokens of >=3 chars — the same matching rule tier3_valuation uses, kept
    identical on purpose so internal and external comps agree on what 'the same item' means.

    'STIHL CHAINSAW MS170 CHAINSAW' -> ['MS170']
    Brand-only descriptions yield [] and are intentionally NOT matchable: matching on
    'DEWALT' alone would compare a $30 drill bit set to a $400 combo kit.
    """
    out = []
    for tok in re.split(r'[^A-Za-z0-9\-/.]+', (desc or "").upper()):
        tok = tok.strip("-/.")
        if len(tok) < 3 or tok in STOP:
            continue
        if not any(c.isdigit() for c in tok):
            continue
        if tok.isdigit() and len(tok) <= 2:
            continue
        out.append(tok)
    return out


def brand_of(desc: str) -> str | None:
    """
    First meaningful word of a Bravo description is reliably the brand — Bravo's own
    convention ('STIHL CHAINSAW MS170', 'COACH KLARE CROSSBODY', 'NINTENDO SWITCH').
    Returns None when the leading token is a generic noun rather than a maker.
    """
    for tok in re.split(r'[^A-Za-z0-9\-&.]+', (desc or "").upper()):
        tok = tok.strip("-&.")
        if len(tok) < 3 or tok in STOP or tok.isdigit():
            continue
        return tok
    return None


class BenchmarkEngine:
    def __init__(self, use_external: bool = True, exclude_date: str | None = None,
                 verbose: bool = False, use_live_api: bool = True):
        """
        exclude_date — a YYYY-MM-DD whose sales are held OUT of the comp index. Essential
        when benchmarking a day's sales: including the very rows being graded would let an
        item vouch for its own price and quietly suppress the flag we're looking for.
        """
        self.use_external = use_external
        # Live SoldComps calls cost quota, so backtests/candidate scans turn this OFF and
        # read cache only. The daily compile leaves it ON.
        self.use_live_api = use_live_api
        self.verbose = verbose
        self.index: dict[str, list[float]] = {}        # model key      -> prices
        self.brand_cat: dict[tuple, list[float]] = {}  # (brand, cat)   -> prices
        self.cat: dict[str, list[float]] = {}          # category       -> prices
        self._ext = None
        self._build_index(exclude_date)
        if use_external:
            self._load_external()

    # ── Internal comp index ───────────────────────────────────────────────────
    def _iter_history_files(self):
        # 12-month baseline export (currently HAR/LEX/ROA only — CUL/WAY were never
        # exported; known gap. Pooling across stores is intentional: 'what does Valley
        # Pawn get for this item' is not store-specific.)
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_inventory-details.csv"))
        # Every daily sold pull accumulates into the comp base, so coverage and freshness
        # both improve automatically over time without any new export being built.
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_sold-discount-detail.csv"))
        yield from glob.glob(os.path.join(BRAVO_OUTPUT, "*_jewelry-margin-sold.csv"))

    def _build_index(self, exclude_date: str | None):
        exc = set()
        if exclude_date:
            y, m, d = exclude_date.split("-")
            exc = {f"{int(m)}/{int(d)}/{y}", exclude_date}

        rows = seen = 0
        for path in self._iter_history_files():
            try:
                with open(path, newline="", encoding="utf-8-sig") as f:
                    for r in csv.DictReader(f):
                        seen += 1
                        if (r.get("Status") or "").strip().upper() != "SOLD":
                            continue
                        if (r.get("Date") or "").strip() in exc:
                            continue
                        price = money(r.get("Last Sold Price"))
                        if not price:
                            continue
                        desc = r.get("Description") or ""
                        if PM_RE.search(desc):
                            continue
                        cat = (r.get("Category") or "").strip().upper()
                        for k in model_keys(desc):
                            self.index.setdefault(k, []).append(price)
                        # Brand + category, and category alone. Bravo's Category values are
                        # unusually specific ('Chainsaw', 'Handbag', 'Digital Camera'), which
                        # makes them a usable fallback for the ~70% of descriptions carrying
                        # no model number at all ('NINTENDO SWITCH', 'COACH KLARE CROSSBODY').
                        b = brand_of(desc)
                        if cat:
                            if b:
                                self.brand_cat.setdefault((b, cat), []).append(price)
                            self.cat.setdefault(cat, []).append(price)
                        rows += 1
            except Exception as e:
                if self.verbose:
                    print(f"  skip {os.path.basename(path)}: {e}", file=sys.stderr)

        if self.verbose:
            print(f"  comp index: {len(self.index):,} model keys from {rows:,} sold rows "
                  f"({seen:,} scanned)")

    def _load_external(self):
        try:
            sys.path.insert(0, PAWN_WALKS)
            from tier3_valuation import get_tier3_value
            self._ext = get_tier3_value
        except Exception as e:
            if self.verbose:
                print(f"  external (eBay) unavailable: {e}", file=sys.stderr)
            self._ext = None

    # ── Benchmarks ────────────────────────────────────────────────────────────
    def internal(self, desc: str, category: str = "") -> tuple[float | None, int, str]:
        """
        Median of our own realized prices, using the most specific match available.
        Returns (value, n, tier) where tier is 'model' | 'brand-cat' | 'category' | ''.

        Tiers are tried strictly best-first — a model-number match is always preferred to a
        brand match, which is always preferred to a bare category median. The tier is
        returned rather than hidden because the caller uses it to decide how much room to
        require before flagging: a category median is a blunt instrument and is held to a
        much wider bar (CATEGORY_FLOOR_RATIO).
        """
        best, best_n = None, 0
        for k in model_keys(desc):
            prices = self.index.get(k)
            if not prices or len(prices) < MIN_INTERNAL_N_USE:
                continue
            if len(prices) > best_n:
                best, best_n = statistics.median(prices), len(prices)
        if best is not None:
            return best, best_n, "model"

        cat = (category or "").strip().upper()
        b   = brand_of(desc)
        if cat and b:
            prices = self.brand_cat.get((b, cat))
            if prices and len(prices) >= MIN_INTERNAL_N_USE:
                return statistics.median(prices), len(prices), "brand-cat"

        if cat:
            prices = self.cat.get(cat)
            if prices and len(prices) >= MIN_CATEGORY_N:
                # Bottom-quartile floor, not the median — see CATEGORY_PCTL rationale.
                s = sorted(prices)
                idx = max(0, min(len(s) - 1, int(len(s) * CATEGORY_PCTL / 100.0)))
                return s[idx], len(prices), "category"

        return None, 0, ""

    def external(self, desc: str, category: str, cost: float | None):
        """
        Real eBay SOLD comps, from the Terapeak cache. Cache-only by design: the compile
        script must never require a browser to produce a report. Claude fills the cache in
        the task's browser step (see terapeak.py); this just reads it.

        Falls back to the old Browse-API path (ACTIVE listings x0.88) ONLY if no Terapeak
        comp exists — and that is genuinely inferior data, so it is not preferred.
        """
        # 1) True sold comps (preferred). Never for firearms — see FIREARM_RE.
        #    Order: shared cache first (filled by either source), then a live SoldComps
        #    API call. Terapeak's browser path writes into the SAME cache, so it remains a
        #    working fallback with no code change here — if the API key is absent or its
        #    quota is exhausted, whatever the browser step cached still resolves.
        try:
            from terapeak import get as tp_get
            if FIREARM_RE.search(desc or "") or FIREARM_RE.search(category or ""):
                raise StopIteration
            kws = self.terapeak_keywords(desc)
            for kw in kws:
                r = tp_get(kw)
                if r and r.get("value"):
                    return float(r["value"])
            # Nothing cached — try the API live (cheap, cached on success AND on miss).
            if self.use_live_api and kws:
                try:
                    from soldcomps import fetch_comp
                    r = fetch_comp(kws[0])
                    if r and r.get("value"):
                        return float(r["value"])
                except Exception:
                    pass
        except Exception:
            pass

        # 2) Legacy active-listing approximation
        if not self._ext:
            return None
        try:
            r = self._ext(desc, category, cost or 0.0)
            if r and r.get("value") and r.get("confidence") in ("high", "medium"):
                return float(r["value"])
        except Exception:
            pass
        return None

    @staticmethod
    def terapeak_keywords(desc: str) -> list[str]:
        """
        Search phrases to try against the Terapeak cache, most specific first.
        Brand + model is what actually resolves on eBay ('STIHL BG 50'); the raw Bravo
        description carries filler ('LEAF BLOWER BG 50') that hurts match rate.
        """
        d = (desc or "").upper().strip()
        out = []
        b = brand_of(d)
        mk = model_keys(d)
        if b and mk:
            out.append(f"{b} {mk[0]}")
        if b and re.search(r'\b([A-Z]{1,3})\s+(\d{2,4})\b', d):
            m = re.search(r'\b([A-Z]{1,3})\s+(\d{2,4})\b', d)
            out.append(f"{b} {m.group(1)} {m.group(2)}")
        if d:
            out.append(re.sub(r'\s+', ' ', d)[:60])
        seen, uniq = set(), []
        for k in out:
            if k not in seen:
                seen.add(k); uniq.append(k)
        return uniq

    def benchmark(self, desc: str, category: str, sale_price: float | None,
                  cost: float | None = None) -> dict:
        """
        Blended 'what should this have sold for'.
        Returns value=None / confidence='none' whenever we genuinely don't know — the
        caller MUST NOT flag on that.
        """
        out = {"value": None, "confidence": "none", "source": "", "internal": None,
               "internal_n": 0, "external": None, "note": "", "flag_below": None,
               "tier": ""}

        if PM_RE.search(desc or ""):
            out["note"] = "precious metal — priced by melt, not resale comps"
            return out

        iv, n, tier = self.internal(desc, category)
        # ALWAYS consult external — the Terapeak path inside external() is a free local
        # cache read. `use_external` gates only the legacy Browse API (live network calls);
        # gating the whole method would have silently discarded real sold comps we already
        # have on disk, which is the opposite of the point.
        ev = self.external(desc, category, cost)
        out["internal"], out["internal_n"], out["external"], out["tier"] = iv, n, ev, tier

        # A bare category median is too blunt to average against an external comp — using
        # it that way would dress up a coarse guess as a precise number. When we only have
        # a category median, it stands alone at low confidence and a much wider bar.
        if tier == "category" and iv:
            out["value"] = round(iv, 2)
            out["confidence"] = "low"
            out["source"] = f"category p{CATEGORY_PCTL} n={n}"
            out["flag_below"] = round(iv * CATEGORY_FLOOR_RATIO, 2)
            return out

        if iv and ev:
            spread = abs(iv - ev) / max(iv, ev)
            if spread <= AGREE_BAND:
                # Corroborating. Weight internal higher — it is what we actually realize
                # in our own market, and it is a true sold price rather than an
                # active-listing approximation.
                out["value"] = round(0.65 * iv + 0.35 * ev, 2)
                out["confidence"] = "high" if n >= MIN_INTERNAL_N_HIGH else "medium"
                out["source"] = f"blend(int n={n} + ebay)"
            else:
                # They disagree materially. Take the LOWER — see module docstring.
                out["value"] = round(min(iv, ev), 2)
                out["confidence"] = "medium"
                out["source"] = f"lower-of(int ${iv:,.0f}, ebay ${ev:,.0f})"
                out["note"] = f"sources disagree {spread*100:.0f}% — used the lower"
        elif iv:
            out["value"] = round(iv, 2)
            if tier == "model":
                out["confidence"] = "high" if n >= MIN_INTERNAL_N_HIGH else "low"
            else:  # brand-cat — same brand, same category, no model number
                out["confidence"] = "medium" if n >= MIN_INTERNAL_N_HIGH else "low"
            out["source"] = f"internal {tier} n={n}"
        elif ev:
            out["value"] = round(ev, 2)
            out["confidence"] = "low"   # eBay alone, active-derived — directional only
            out["source"] = "ebay only"
        else:
            out["note"] = "no internal history and no external comp — no opinion"
            return out

        out["flag_below"] = round(out["value"] * FLOOR_RATIO, 2)
        return out

    def evaluate(self, desc: str, category: str, sale_price: float | None,
                 cost: float | None = None) -> dict:
        """benchmark() + the actual flag decision. Only medium/high confidence can flag."""
        b = self.benchmark(desc, category, sale_price, cost)
        b["sold_too_cheap"] = False
        b["pct_of_benchmark"] = None
        b["gap_dollars"] = None
        if b["value"] and sale_price:
            b["pct_of_benchmark"] = round(sale_price / b["value"] * 100, 1)
            b["gap_dollars"] = round(b["value"] - sale_price, 2)

            below   = sale_price < (b["flag_below"] or 0)
            # Dollar floor: a percentage gap on a cheap item is not worth anyone's time.
            material = b["gap_dollars"] >= MIN_GAP_DOLLARS
            # Category-only benchmarks are 'low' confidence by construction but are still
            # allowed to flag — they just had to clear the far wider CATEGORY_FLOOR_RATIO
            # to get here, which is its own, stricter form of evidence.
            trusted = b["confidence"] in ("high", "medium") or b["tier"] == "category"

            b["sold_too_cheap"] = bool(below and material and trusted)
        return b


# ── Backtest ──────────────────────────────────────────────────────────────────
def backtest(dates: list[str], use_external: bool = False) -> None:
    """
    Run the benchmark over real past sold days and report the flag rate.

    This exists because a flag rate is the ONLY way to know whether this is publishable.
    A rule that flags 40% of items is noise and will get the report ignored; the target is
    a small, believable number of genuinely suspicious sales.
    """
    print(f"=== Benchmark backtest — {len(dates)} day(s), external={'ON' if use_external else 'OFF'} ===\n")
    tot = flagged = valued = 0
    examples = []

    for date in dates:
        eng = BenchmarkEngine(use_external=use_external, exclude_date=date, verbose=False, use_live_api=False)
        day_rows = 0
        for path in glob.glob(os.path.join(BRAVO_OUTPUT, f"{date}_to_{date}_*_sold-discount-detail.csv")):
            store = os.path.basename(path).split("_")[3]
            with open(path, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    if (r.get("Status") or "").strip().upper() != "SOLD":
                        continue
                    sale = money(r.get("Last Sold Price"))
                    if not sale:
                        continue
                    tot += 1; day_rows += 1
                    res = eng.evaluate(r.get("Description", ""), r.get("Category", ""),
                                       sale, money(r.get("Cost")))
                    if res["value"]:
                        valued += 1
                    if res["sold_too_cheap"]:
                        flagged += 1
                        examples.append((date, store, r.get("Description", "")[:40], sale,
                                         res["value"], res["pct_of_benchmark"],
                                         res["confidence"], res["source"],
                                         res["gap_dollars"]))
        print(f"  {date}: {day_rows} sold items")

    print(f"\n  TOTAL sold items      : {tot}")
    print(f"  benchmarked (any conf): {valued}  ({valued/tot*100:.0f}% coverage)" if tot else "")
    print(f"  FLAGGED sold-too-cheap: {flagged}  ({flagged/tot*100:.1f}% of items)" if tot else "")

    if examples:
        print(f"\n  --- flagged items (worst first by $ left on the table) ---")
        for d, s, desc, sale, bench, pct, conf, src, gap in sorted(examples, key=lambda x: -x[8]):
            print(f"   {d} {s:<4} sold ${sale:>8,.2f}  typical ${bench:>9,.2f}  "
                  f"gap ${gap:>8,.2f} ({pct:>5.1f}%) [{conf:<6}] {desc}  <{src}>")


def candidates(date: str, limit: int = 8) -> None:
    """
    Print the Terapeak keywords worth fetching for a given sold date, best-value first,
    one per line as:  <keyword>\t<url>

    Prioritised by what a lookup is actually WORTH: the sale price of the item, so a $400
    sale gets researched before a $9 one. Skips precious metals (melt-priced), anything
    already fresh in the cache, and anything with no usable search phrase. Capped because
    each entry costs a browser round-trip — the point is a handful of high-value lookups
    per run, not exhaustive coverage.
    """
    try:
        from terapeak import get as tp_get, research_url
    except Exception as e:
        print(f"# terapeak module unavailable: {e}", file=sys.stderr)
        return

    eng = BenchmarkEngine(use_external=False, exclude_date=date, use_live_api=False)
    seen, out = set(), []
    for path in glob.glob(os.path.join(BRAVO_OUTPUT, f"{date}_to_{date}_*_sold-discount-detail.csv")):
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if (r.get("Status") or "").strip().upper() != "SOLD":
                    continue
                desc = r.get("Description", "")
                sale = money(r.get("Last Sold Price"))
                # Skip melt-priced metals and firearms (eBay prohibits gun sales — see
                # FIREARM_RE). Both would burn a browser round-trip for a worthless comp.
                if not sale or PM_RE.search(desc) or FIREARM_RE.search(desc) \
                   or FIREARM_RE.search(r.get("Category", "")):
                    continue
                kws = eng.terapeak_keywords(desc)
                if not kws:
                    continue
                kw = kws[0]
                if kw in seen or tp_get(kw):      # already queued or already cached fresh
                    continue
                seen.add(kw)
                out.append((sale, kw))

    for sale, kw in sorted(out, reverse=True)[:limit]:
        print(f"{kw}\t{research_url(kw)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ext  = "--external" in sys.argv

    if "--candidates" in sys.argv:
        candidates(args[0] if args else datetime.date.today().isoformat())
        sys.exit(0)
    if args:
        backtest(args, use_external=ext)
    else:
        found = sorted({os.path.basename(p).split("_")[0]
                        for p in glob.glob(os.path.join(BRAVO_OUTPUT, "*_sold-discount-detail.csv"))})
        print(f"Available sold dates: {', '.join(found) or '(none)'}")
        if found:
            backtest(found, use_external=ext)
