#!/usr/bin/env python3
"""
Valley Pawn — firearm values that are actually firearm values
=============================================================
Built 2026-09-28 after the 9/28 huddle (Preston: sold-review gun values look wrong).

THE BUG THIS FIXES (verified in the 2026-09-26 sold review):
  SIG SAUER P320 9MM sold $460 -> "fair ~$22"
  GLENFIELD 30A 30-30  sold $600 -> "fair ~$35"
  SAVAGE AXIS 6.5 CREED sold $300 -> "fair ~$30"
  TISAS 1911 DUTY B9R  sold $404 -> "fair ~$60"
The shared comp index matches on any digit-bearing token. For guns those tokens are
mostly CALIBERS ("9MM", "30-30", "6.5") and generic model numbers ("P320", "1911")
that also appear on magazines, holsters, ammo and scope sales in the same history.
A $460 pistol was being compared with $22 magazines.

THE FIX
  1. A gun is identified by its Bravo CATEGORY (Pistol, Rifle, Shotgun, Revolver,
     Black Powder Gun, Pistol Grip Shotgun, Frame; Receiver only when the text says
     firearm). Description words alone are not enough — "SIG MAGAZINE" is not a gun.
  2. Gun comps come ONLY from past sales in gun categories.
  3. Caliber tokens are never used as a match key.
  4. Tiers: brand + model within the same gun category (n>=3) -> brand + category
     (n>=5, wide band, low confidence) -> no opinion. No opinion beats a wrong one.
  5. External: GunBroker's official API (completed auctions that actually sold).
     This is the same data True Gun Value republishes; True Gun Value's own terms
     forbid business/automated use, GunBroker's API is licensed for it. Needs a
     free developer key + the company GunBroker login saved in
     .gunbroker_credentials.json (see GUNBROKER_SETUP.md). Until then the module
     runs internal-only and says so.

USAGE
  from gun_value import is_firearm, GunValue
  gv = GunValue.load(exclude_date="2026-09-26")
  gv.estimate("SIG SAUER P320 9MM", "Pistol")
  python3 gun_value.py "SIG SAUER P320 9MM" Pistol
"""
from __future__ import annotations
import csv, glob, json, os, re, sys, statistics, datetime as dt, urllib.request, urllib.parse

BRAVO_OUTPUT = os.environ.get(
    "VP_BRAVO_OUTPUT", "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/")
_HERE = os.path.dirname(os.path.abspath(__file__))
GB_CRED = os.path.join(_HERE, ".gunbroker_credentials.json")
GB_CACHE = os.path.join(_HERE, "gunbroker_cache.json")
GB_TTL_DAYS = 14
GB_DAILY_CAP = 150

GUN_CATS = {"PISTOL", "RIFLE", "SHOTGUN", "REVOLVER", "BLACK POWDER GUN",
            "PISTOL GRIP SHOTGUN", "FRAME", "DERRINGER", "HANDGUN", "FIREARM"}
_RECEIVER_GUN = re.compile(r"\b(AR-?15|AR-?10|LOWER|UPPER|80%|FIREARM|ARMS|ARMORY|PRECISION)\b", re.I)

# Words that are never a model key for a gun.
CALIBER_RE = re.compile(
    r"^(\.?\d{2,3}(LR|WMR|HMR|ACP|AUTO|SPL|SPECIAL|MAG|MAGNUM|WIN|REM|S&W|SW|CAL|GAP|SUPER|WSM|CREED|CM|PRC|BLK|GA|G)?"
    r"|\d{1,2}(\.\d{1,2})?(MM|X\d{2,3}(MM)?|CM)"
    r"|\d{1,2}\.\d{1,2}"
    r"|\d{2,3}-\d{2,3}"
    r"|\d{1,2}GA|\d{1,2}-?GAUGE|410|\.410)$", re.I)
_BARE_CALIBERS = {"22", "25", "32", "38", "40", "44", "45", "223", "243", "270", "300", "308",
                  "357", "380", "410", "30-06", "30-30", "45-70", "6.5", "5.56", "7.62", "9MM",
                  "10MM", "12GA", "20GA", "16GA", "28GA", "17HMR", "22LR", "22WMR"}
STOP = set("THE AND FOR WITH MODEL SERIAL NUMBER NO NEW USED BLACK STAINLESS PISTOL RIFLE "
           "SHOTGUN REVOLVER FIREARMS FIREARM ARMS INC CO GUN SEMI AUTO BOLT PUMP LEVER".split())


def is_firearm(category: str, desc: str = "") -> bool:
    c = (category or "").strip().upper()
    if c in GUN_CATS:
        return True
    if c == "RECEIVER" and _RECEIVER_GUN.search(desc or ""):
        return True
    return False


def _money(x):
    s = str(x or "").replace("$", "").replace(",", "").strip()
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None


def brand_of(desc: str) -> str | None:
    toks = [t for t in re.split(r"[^A-Z0-9&.\-]+", (desc or "").upper()) if t]
    for i, t in enumerate(toks):
        t = t.strip(".-")
        if len(t) < 2 or t in STOP or t.isdigit():
            continue
        # two-word makers
        if t in {"SMITH", "S&W"}:
            return "S&W"
        if t == "SIG" or (t == "SAUER" and i and toks[i - 1] == "SIG"):
            return "SIG"
        if t in {"HI", "HI-POINT"}:
            return "HI-POINT"
        if t in {"HENRY", "RUGER", "GLOCK", "TAURUS", "MOSSBERG", "REMINGTON", "SAVAGE"}:
            return t
        return t
    return None


_SERIAL_RE = re.compile(r"\bSERIAL\b.*$|\bS/N\b.*$", re.I)


def model_keys(desc: str) -> list[str]:
    # Intake descriptions carry "..., SERIAL NUMBER ABC123" — a serial is never a model.
    d = _SERIAL_RE.sub("", (desc or "").upper())
    glock = "GLOCK" in d          # Glock models ARE bare numbers (19, 43, 45, 48)
    out = []
    for tok in re.split(r"[^A-Za-z0-9\-/.&]+", d):
        tok = tok.strip("-/.")
        if glock and re.fullmatch(r"G?\d{2}X?", tok):
            out.append(tok.lstrip("G"))
            continue
        if len(tok) < 2 or tok in STOP or tok in _BARE_CALIBERS or CALIBER_RE.match(tok):
            continue
        if not any(ch.isdigit() for ch in tok):
            continue
        out.append(tok)
    return out


def _wstats(pairs):
    pairs = sorted(pairs)
    tot = sum(w for _, w in pairs)

    def pct(q):
        acc = 0.0
        for p, w in pairs:
            acc += w
            if acc >= q * tot:
                return p
        return pairs[-1][0]
    med, p25, p75 = pct(.5), pct(.25), pct(.75)
    return {"median": round(med, 2), "p25": round(p25, 2), "p75": round(p75, 2),
            "n": len(pairs), "cv": round(max(((p75 - p25) / (2 * med)) if med else 1, 0.02), 3)}


class GunValue:
    HALF_LIFE = 365.0

    def __init__(self, exclude_date: str | None = None, ref_date: str | None = None):
        self.ref = dt.date.fromisoformat(ref_date) if ref_date else dt.date.today()
        self.exclude = exclude_date
        self.by_model = {}      # (brand, cat, key) -> [(price, age)]
        self.by_brandcat = {}   # (brand, cat)      -> [(price, age)]
        self._build()

    @classmethod
    def load(cls, **kw):
        return cls(**kw)

    def _build(self):
        exc = set()
        if self.exclude:
            y, m, d = self.exclude.split("-")
            exc = {f"{int(m)}/{int(d)}/{y}", self.exclude}
        seen = set()
        files = (glob.glob(os.path.join(BRAVO_OUTPUT, "*_inventory-details.csv")) +
                 glob.glob(os.path.join(BRAVO_OUTPUT, "*_sold-discount-detail.csv")) +
                 glob.glob(os.path.join(BRAVO_OUTPUT, "*_jewelry-margin-sold.csv")))
        for path in files:
            try:
                rows = list(csv.DictReader(open(path, newline="", encoding="utf-8-sig", errors="ignore")))
            except Exception:
                continue
            for r in rows:
                if (r.get("Status") or "").strip().upper() != "SOLD":
                    continue
                cat, desc = (r.get("Category") or "").strip().upper(), r.get("Description") or ""
                if not is_firearm(cat, desc):
                    continue
                ds = (r.get("Date") or "").strip()
                if ds in exc:
                    continue
                price = _money(r.get("Last Sold Price"))
                if not price or price < 40:      # $0 = FFL transfer; <$40 is not a gun sale
                    continue
                key = (r.get("Number"), ds)       # the same sale appears in several pulls
                if key in seen:
                    continue
                seen.add(key)
                try:
                    sd = dt.datetime.strptime(ds, "%m/%d/%Y").date()
                    age = max((self.ref - sd).days, 0)
                except ValueError:
                    age = 400
                b = brand_of(desc)
                if not b:
                    continue
                self.by_brandcat.setdefault((b, cat), []).append((price, age))
                for k in model_keys(desc):
                    self.by_model.setdefault((b, cat, k), []).append((price, age))

    def internal(self, desc: str, category: str) -> dict | None:
        cat, b = (category or "").strip().upper(), brand_of(desc)
        if not b:
            return None
        best = None
        for k in model_keys(desc):
            raw = self.by_model.get((b, cat, k))
            if raw and len(raw) >= 3:
                st = _wstats([(p, 0.5 ** (a / self.HALF_LIFE)) for p, a in raw])
                st.update(tier="model", key=f"{b} {k}")
                if best is None or st["n"] > best["n"]:
                    best = st
        if best:
            return best
        raw = self.by_brandcat.get((b, cat))
        if raw and len(raw) >= 5:
            st = _wstats([(p, 0.5 ** (a / self.HALF_LIFE)) for p, a in raw])
            st.update(tier="brand-cat", key=f"{b} {cat.title()}")
            return st
        return None

    def estimate(self, desc: str, category: str, allow_live: bool = True) -> dict:
        out = {"fair": None, "band": None, "basis": "", "internal": None, "external": None}
        if not is_firearm(category, desc):
            out["basis"] = "not a firearm category"
            return out
        iv = self.internal(desc, category)
        ev = gunbroker_comp(desc, category) if allow_live else None
        out["internal"], out["external"] = iv, ev
        if iv and ev:
            wi, we = iv["n"] / (1 + iv["cv"]), ev["n"] / (1 + ev["cv"])
            # GunBroker prices are what private buyers pay online incl. no store overhead;
            # use them as-is (no fee haircut: buyer pays shipping/transfer on top).
            out["fair"] = round((wi * iv["median"] + we * ev["median"]) / (wi + we), 2)
            out["basis"] = f"guns: our {iv['key']} n={iv['n']} + GunBroker n={ev['n']}"
            out["band"] = round(max((iv["p75"] - iv["p25"]) / 2, abs(iv["median"] - ev["median"]) / 2), 2)
        elif ev:
            out.update(fair=ev["median"], band=round((ev["p75"] - ev["p25"]) / 2, 2),
                       basis=f"guns: GunBroker sold n={ev['n']}")
        elif iv:
            out.update(fair=iv["median"], band=round((iv["p75"] - iv["p25"]) / 2, 2),
                       basis=f"guns: our sales {iv['key']} ({iv['tier']}) n={iv['n']}")
        else:
            out["basis"] = "guns: no reliable comp"
        return out


# ── GunBroker (official API) ──────────────────────────────────────────────────
_gb_token = None


def _gb_creds():
    try:
        with open(GB_CRED) as f:
            c = json.load(f)
        return c if c.get("dev_key") and c.get("username") and c.get("password") else None
    except Exception:
        return None


def _gb_req(method, path, creds, token=None, params=None, body=None):
    url = "https://api.gunbroker.com/v1/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    h = {"Content-Type": "application/json", "X-DevKey": creds["dev_key"]}
    if token:
        h["X-AccessToken"] = token
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=25) as r:
        return json.loads(r.read().decode())


def _gb_cache():
    try:
        return json.load(open(GB_CACHE))
    except Exception:
        return {"entries": {}, "calls": {}}


def gunbroker_comp(desc: str, category: str) -> dict | None:
    """Median of completed GunBroker listings that actually SOLD (used), last 30 days."""
    global _gb_token
    b, keys = brand_of(desc), model_keys(desc)
    if not b or not keys:
        return None
    q = f"{b} {keys[0]}"
    cache = _gb_cache()
    e = cache["entries"].get(q)
    today = dt.date.today().isoformat()
    if e and (dt.date.today() - dt.date.fromisoformat(e["at"])).days <= GB_TTL_DAYS:
        return e["comp"]
    creds = _gb_creds()
    if not creds or cache["calls"].get(today, 0) >= GB_DAILY_CAP:
        return None
    try:
        if not _gb_token:
            _gb_token = _gb_req("POST", "Users/AccessToken", creds,
                                body={"Username": creds["username"], "Password": creds["password"]})
            _gb_token = {k.lower(): v for k, v in _gb_token.items()}["accesstoken"]
        res = _gb_req("GET", "Items/Completed", creds, _gb_token,
                      {"Keywords": q, "Condition": 4, "Timeframe": 12, "PageSize": 100, "Country": "US"})
        cache["calls"][today] = cache["calls"].get(today, 0) + 1
        prices = []
        res = {k.lower(): v for k, v in res.items()}
        for it in res.get("results", []) or []:
            it = {k.lower(): v for k, v in it.items()}      # API casing varies by version
            sold = (it.get("highbidderid") or 0) > 0 and (not it.get("hasreserve") or it.get("hasreservebeenmet"))
            title = (it.get("title") or "").upper()
            if sold and it.get("price", 0) >= 75 and not re.search(r"\b(MAG(AZINE)?S?|HOLSTER|GRIPS?|SLIDE|BARREL|PARTS?|KIT|CASE|SIGHTS?|SCOPE|AMMO)\b", title):
                prices.append(float(it["price"]))
        comp = None
        if len(prices) >= 3:
            st = _wstats([(p, 1.0) for p in prices])
            st["source"] = "gunbroker"
            comp = st
        cache["entries"][q] = {"at": today, "comp": comp}
        json.dump(cache, open(GB_CACHE, "w"))
        return comp
    except Exception:
        return None


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        gv = GunValue.load()
        print(json.dumps(gv.estimate(sys.argv[1], sys.argv[2]), indent=2))
        print("GunBroker connected:", bool(_gb_creds()))
    else:
        print(__doc__)
