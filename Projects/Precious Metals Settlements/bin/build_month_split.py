#!/usr/bin/env python3
"""build_month_split.py — deterministic monthly scrap-gold split (added 2026-10-01).

Usage:
  python3 build_month_split.py --month 2026-09 --gold-net 38952.34 --stones-net 39187.08 \
      --gold-premelt 352.5 --stones-premelt 355.7 --readonly-result <results-scrap/...result.json> [...more result files] \
      --map "CUL:2026-09 GOLD:gold" --map "CUL:2026-09 GOLD WITH STONES:stones" ... (10 maps)

Reads live weights from one or more READ-ONLY (readOnly:true) scrap closeout result JSONs,
allocates each net wire by weight share (cents by largest remainder -> totals exact to the penny),
writes reviews/<month>_allocations_REVIEW.csv and
Bravo Data Extraction/triggers-scrap/pending-approval/scrap-closeout-<month>.json.
Refuses (exit 2) if any of the 10 buckets has no live weight. Never posts anything.
"""
import argparse, json, os, sys
from decimal import Decimal as D, ROUND_FLOOR
ROOT = os.path.expanduser("~/Documents/Claude/Projects")
if not os.path.isdir(ROOT):
    ROOT = "/sessions/" + os.environ.get("USER", "") + "/mnt/Projects"

def split(total, w):
    tw = sum(D(str(v)) for v in w.values()); cents = int(D(str(total)) * 100)
    raw = {k: D(str(v)) / tw * cents for k, v in w.items()}
    fl = {k: int(r.to_integral_value(ROUND_FLOOR)) for k, r in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - fl[k], reverse=True)[: cents - sum(fl.values())]:
        fl[k] += 1
    return float(tw), {k: D(fl[k]) / 100 for k in fl}

ap = argparse.ArgumentParser()
ap.add_argument("--month", required=True); ap.add_argument("--gold-net", required=True); ap.add_argument("--stones-net", required=True)
ap.add_argument("--gold-premelt", type=float); ap.add_argument("--stones-premelt", type=float)
ap.add_argument("--readonly-result", action="append", required=True)
ap.add_argument("--map", action="append", required=True, help="STORE:Bucket Name:gold|stones")
ap.add_argument("--root", default=ROOT)
a = ap.parse_args()

live = {}
for f in a.readonly_result:
    d = json.loads(open(f, encoding="utf-8-sig").read())
    for b in d["buckets"]:
        if b.get("status") == "readonly" and b.get("liveWeightDwt"):
            live[(b["store"], b["bucketName"])] = b["liveWeightDwt"]
maps = [m.split(":", 2) for m in a.map]
missing = [f"{s}:{n}" for s, n, t in maps if (s, n) not in live]
if missing or len(maps) != 10:
    print("REFUSE: need 10 buckets with live weights; missing:", missing, "maps:", len(maps)); sys.exit(2)
gw = {s: float(live[(s, n)]) for s, n, t in maps if t == "gold"}
sw = {s: float(live[(s, n)]) for s, n, t in maps if t == "stones"}
tg, G = split(a.gold_net, gw); ts, S = split(a.stones_net, sw)
assert sum(G.values()) == D(a.gold_net) and sum(S.values()) == D(a.stones_net)
money = lambda x: f'"${x:,.2f}"'
rows = ["PRECIOUS METALS SETTLEMENT ALLOCATION - REVIEW,,,,,,,",
        f"Scrap month:,{a.month},Generated:,build_month_split.py from live Bravo weights,,,,",
        f"Gold net wire:,{money(D(a.gold_net))},Bravo gold dwt:,{tg:.4f},Elemetal pre-melt:,{a.gold_premelt or ''},,",
        f"Stones net wire:,{money(D(a.stones_net))},Bravo stones dwt:,{ts:.4f},Elemetal pre-melt:,{a.stones_premelt or ''},,",
        ",,,,,,,", "Store,Gold Weight (dwt),Gold Share %,Gold $,Stones Weight (dwt),Stones Share %,Stones $,Grand Total $"]
for s in gw:
    rows.append(f"{s},{gw[s]:.4f},{gw[s]/tg*100:.3f}%,{money(G[s])},{sw[s]:.4f},{sw[s]/ts*100:.3f}%,{money(S[s])},{money(G[s]+S[s])}")
rows.append(f"TOTAL,{tg:.4f},100.000%,{money(sum(G.values()))},{ts:.4f},100.000%,{money(sum(S.values()))},{money(sum(G.values())+sum(S.values()))}")
rows += [",,,,,,,", "BUCKET DETAIL,,,,,,,", "Store,Bucket Name,Occurrence,Type,Live Weight (dwt),Bucket $,,"]
buckets = []
for s, n, t in maps:
    amt = G[s] if t == "gold" else S[s]
    rows.append(f"{s},{n},0,{'no-stones' if t=='gold' else 'stones'},{float(live[(s,n)]):.4f},{money(amt)},,")
    buckets.append({"store": s, "bucketName": n, "occurrence": 0, "expectedWeightDwt": live[(s, n)], "amountPaid": (f"{amt:.2f}".rstrip("0").rstrip(".")), "tenderType": "Cashiers Check"})
rows.append("STATUS:,REVIEW - awaiting Joshua's approval,,,,,,")
rev = os.path.join(a.root, "Precious Metals Settlements/reviews", f"{a.month}_allocations_REVIEW.csv")
pend = os.path.join(a.root, "Bravo Data Extraction/triggers-scrap/pending-approval"); os.makedirs(pend, exist_ok=True)
man = os.path.join(pend, f"scrap-closeout-{a.month}.json")
open(rev, "w").write("\n".join(rows) + "\n")
json.dump({"id": f"scrap-closeout-{a.month}", "buckets": buckets}, open(man, "w"), indent=2)
print("\n".join(rows)); print("WROTE", rev); print("WROTE", man)
