#!/usr/bin/env python3
"""
Valley Pawn — Item age (days on shelf) for any Bravo SKU
=========================================================
Built 2026-09-28. Shared by discount review, sold review, pawn walks and any other
report that needs "how long did this item sit before it sold".

WHY THIS EXISTS
  Bravo's sold reports carry the SALE date, never the date the item went into
  inventory. The report that would carry it (all on-shelf items) cannot be pulled:
  the grid is too large for the pipeline to walk (BRAVO_KNOWN_ISSUES). So age is
  derived from something every sold row already has: the SKU number.

HOW
  Bravo assigns SKUs from a per-store counter that only goes up. Every sold row we
  have ever pulled (sold-discount-detail, jewelry-margin-sold, inventory-details,
  sales-detail, aged sales...) tells us "a SKU at least this high existed on this
  date". The running maximum by date is the counter's FRONTIER. An item's intake
  date is the first day the frontier reached its SKU. Age = sale date - that day.

  SKUs are grouped into SERIES by prefix + digit length (+ first two digits for the
  7-digit series), because different stores share prefixes with different number
  ranges (HAR 'VA50xxxxx' vs LEX 'VA10xxxxx'). A transferred item keeps its origin
  store's SKU, so series are global, not per selling store.

ACCURACY (backtest 2026-09-28 against 700+ items whose real intake date Bravo
reports in the markdown-verification pull, intake on/after 2025-07-01):
  VP40 (CUL) 94% within 14 days · VA50 (HAR) 89% · VA10 (LEX) 96% ·
  ROA (ROA) 100% · VAP 5-digit (WAY) 97%. Median error 1-3 days.
  The misses are mostly items whose Bravo date was re-stamped (returned /
  re-received), not estimator error. Series that fail validation return
  confidence 'unknown' and NO age — the reports then treat the item as undated
  rather than guessing.

  Items older than the sold history (first pulls May 2025 for most stores) get an
  age that is a LOWER BOUND (flag lower_bound=True). The band is still right for
  anything past a year, which is all the bands care about.

USAGE
  from item_age import AgeIndex
  idx = AgeIndex.load()                 # rebuilds the cache if older than today
  idx.estimate("VP4032036", "2026-09-27")
  -> {'age_days': 41, 'intake_est': '2026-08-17', 'band': '31-60',
      'confidence': 'high', 'lower_bound': False, 'series': 'VP7-40'}

  python3 item_age.py --rebuild          # rebuild cache + print validation
  python3 item_age.py VP4032036 2026-09-27
"""
from __future__ import annotations
import csv, glob, json, os, re, sys, bisect, datetime as dt, collections

BRAVO_OUTPUT = os.environ.get(
    "VP_BRAVO_OUTPUT", "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/")
_HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(_HERE, "item_age_index.json")

# Age bands shared by every report (days, inclusive upper edge). Keep in sync with
# discount_policy.json — the policy file is the one people edit.
BANDS = [(30, "0-30"), (60, "31-60"), (90, "61-90"), (180, "91-180"), (365, "181-365"),
         (10**6, "365+")]

VALID_MIN_N = 20        # anchors needed to call a series validated
VALID_MIN_HIT = 0.85    # share of anchors within 14 days
MEDIUM_MIN_SOLD = 300   # unvalidated series with this much sold history -> 'medium'

_SKU_RE = re.compile(r"^([A-Z]+)(\d+)$")


def parse_sku(s: str):
    m = _SKU_RE.match((s or "").strip().upper())
    return (m.group(1), int(m.group(2)), len(m.group(2))) if m else None


def series_of(sku: str) -> str | None:
    p = parse_sku(sku)
    if not p:
        return None
    pre, n, _ = p
    digits = str(n)                       # leading zeros are padding, not part of the counter
    return f"{pre}{len(digits)}-{digits[:2]}" if len(digits) >= 6 else f"{pre}{len(digits)}"


def band_of(days: int | None) -> str | None:
    if days is None:
        return None
    for edge, name in BANDS:
        if days <= edge:
            return name
    return BANDS[-1][1]


def _date(s):
    s = (s or "").strip()
    for f in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    return None


class AgeIndex:
    def __init__(self, data: dict):
        self.built = data["built"]
        self.series = data["series"]          # name -> {dates:[], maxes:[], first, conf, val}
        self._d = {k: [dt.date.fromisoformat(x) for x in v["dates"]] for k, v in self.series.items()}

    # ── build ────────────────────────────────────────────────────────────────
    @classmethod
    def build(cls, verbose: bool = False) -> "AgeIndex":
        sold = collections.defaultdict(list)
        anchors = {}
        for path in glob.glob(os.path.join(BRAVO_OUTPUT, "*.csv")):
            m = re.search(r"_(CUL|HAR|LEX|ROA|WAY)_([a-z0-9-]+)\.csv$", path)
            if not m:
                continue
            kind = m.group(2)
            try:
                with open(path, newline="", encoding="utf-8-sig", errors="ignore") as f:
                    rows = list(csv.DictReader(f))
            except Exception:
                continue
            for r in rows:
                sku = r.get("Number") or r.get("Item Number")
                ser = series_of(sku)
                if not ser:
                    continue
                d = _date(r.get("Date") or r.get("Sale Date"))
                if not d:
                    continue
                n = parse_sku(sku)[1]
                status = (r.get("Status") or "SOLD").strip().upper()
                if kind == "markdown-verification" and status == "INVENTORY":
                    anchors[(ser, n)] = d
                elif status == "SOLD" or kind == "sales-detail":
                    sold[ser].append((d, n))
        series = {}
        for ser, v in sold.items():
            v.sort()
            dates, maxes, cur = [], [], -1
            for d, n in v:
                cur = max(cur, n)
                if dates and dates[-1] == d:
                    maxes[-1] = cur
                else:
                    dates.append(d); maxes.append(cur)
            # dense window: from the last gap > 21 days onward the frontier is continuous
            dense = dates[0]
            for a, b in zip(dates, dates[1:]):
                if (b - a).days > 21:
                    dense = b
            series[ser] = {"dates": [d.isoformat() for d in dates], "maxes": maxes,
                           "first": dates[0].isoformat(), "dense": dense.isoformat(),
                           "n_sold": len(v)}
        idx = cls({"built": dt.date.today().isoformat(), "series": series})
        # validation against real intake dates (only anchors inside the sold window)
        by = collections.defaultdict(list)
        for (ser, n), true in anchors.items():
            if ser not in series:
                continue
            dense = dt.date.fromisoformat(series[ser]["dense"])
            if true < dense + dt.timedelta(days=45):
                continue
            est = idx._intake(ser, n)
            if est:
                by[ser].append((est - true).days)
        for ser, s in series.items():
            errs = by.get(ser, [])
            hit = (sum(1 for e in errs if abs(e) <= 14) / len(errs)) if errs else None
            s["val"] = {"n": len(errs), "within14": round(hit, 3) if hit is not None else None}
            if errs and len(errs) >= VALID_MIN_N and hit >= VALID_MIN_HIT:
                s["conf"] = "high"
            elif s["n_sold"] >= MEDIUM_MIN_SOLD and (not errs or hit >= 0.6):
                s["conf"] = "medium"
            else:
                s["conf"] = "unknown"
        with open(CACHE + ".tmp", "w") as f:
            json.dump({"built": idx.built, "series": series}, f)
        os.replace(CACHE + ".tmp", CACHE)
        if verbose:
            for ser, s in sorted(series.items(), key=lambda x: -x[1]["n_sold"]):
                if s["n_sold"] >= 50:
                    print(f"  {ser:10s} sold={s['n_sold']:6d} dense since {s['dense']}  "
                          f"validation n={s['val']['n']:4d} within14={s['val']['within14']}  -> {s['conf']}")
        return cls({"built": idx.built, "series": series})

    @classmethod
    def load(cls, max_age_days: int = 0) -> "AgeIndex":
        try:
            with open(CACHE) as f:
                data = json.load(f)
            if (dt.date.today() - dt.date.fromisoformat(data["built"])).days <= max_age_days:
                return cls(data)
        except Exception:
            pass
        return cls.build()

    # ── query ────────────────────────────────────────────────────────────────
    def _intake(self, ser: str, n: int):
        s = self.series.get(ser)
        if not s:
            return None
        i = bisect.bisect_left(s["maxes"], n)
        return self._d[ser][i] if i < len(s["maxes"]) else None

    def estimate(self, sku: str, sale_date) -> dict:
        out = {"age_days": None, "intake_est": None, "band": None, "confidence": "unknown",
               "lower_bound": False, "series": None}
        ser = series_of(sku)
        if not ser or ser not in self.series:
            return out
        s = self.series[ser]
        out["series"] = ser
        if s.get("conf", "unknown") == "unknown":
            return out
        sd = sale_date if isinstance(sale_date, dt.date) else _date(str(sale_date))
        if not sd:
            return out
        n = parse_sku(sku)[1]
        intake = self._intake(ser, n)
        if intake is None or intake > sd:
            # SKU newer than any sale we have seen by the sale date: created that day.
            intake = sd
        dense = dt.date.fromisoformat(s.get("dense", s["first"]))
        if intake <= dense:
            # older than the continuous sales history: we only know it is AT LEAST this old
            intake = min(intake, dense)
            out["lower_bound"] = True
        age = (sd - intake).days
        out.update(age_days=max(age, 0), intake_est=intake.isoformat(),
                   band=band_of(max(age, 0)), confidence=s["conf"])
        return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        AgeIndex.build(verbose=True)
    elif len(sys.argv) == 3:
        print(json.dumps(AgeIndex.load().estimate(sys.argv[1], sys.argv[2]), indent=2))
    else:
        print(__doc__)
