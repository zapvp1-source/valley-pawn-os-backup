#!/usr/bin/env python3
"""
Valley Pawn — Intake Valuation Engine (item-level)
Values each item we take in (buy or loan) against an INDEPENDENT estimate, to catch overpaying
at intake. Item-level, never category-only.

Value sources, in priority order:
  1) MELT  — precious metal: parse weight (DWT/oz) + purity (karat / sterling) x live spot.
  2) COMP  — item-level match to our own historically SOLD items (same make/model tokens),
             value = median realized Last Sold Price of the matched comps.
  3) CAT   — category median realized sale price (last-resort fallback only).
  4) TIER3 — external market price (eBay Browse for general merch; gun-value sites for firearms).
             Invoked when T1+T2 both returned low/no confidence. Set USE_TIER3=True to enable.
Margin = (Value - Cost) / Value, graded vs 50%. Overpay = Cost > Value.

Spot prices (June 9, 2026) — PRODUCTION wires these to the daily vp-weekly-spot-price-update source.
"""
import csv, glob, re, json, statistics, collections, os, sys

# ── Tier 3 toggle ──
# Set USE_TIER3=True to call external APIs for low-confidence items (adds network time).
# Leave False for pure T1/T2 offline runs.
USE_TIER3 = False
_t3 = None
if USE_TIER3:
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from tier3_valuation import get_tier3_value as _get_t3
        _t3 = _get_t3
    except ImportError:
        print("WARNING: tier3_valuation.py not found — Tier 3 disabled.")
        USE_TIER3 = False

BASE = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/"
OUT  = "/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/"
GOLD_SPOT = 4350.0   # $/troy oz
SILVER_SPOT = 68.0   # $/troy oz
TARGET = 0.50
DWT_PER_OZT = 20.0
KARAT = {'24':1.0,'22':0.9167,'18':0.75,'14':0.585,'10':0.417,'9':0.375}
STOP = set("THE AND FOR WITH MODEL SERIAL NUMBER NO SIZE COLOR BLACK WHITE BLUE RED SILVER GOLD "
           "USED NEW ITEM MISC GENT GENTS LADY LADYS LADIES MENS WOMENS PModelC".split())

def money(x):
    x=(x or '').replace('$','').replace(',','').strip()
    if x in ('','-'): return None
    try: return float(x)
    except: return None

def norm_tokens(desc):
    d=(desc or '').upper()
    d=re.sub(r'[^A-Z0-9 ]',' ',d)
    toks=[t for t in d.split() if len(t)>=2 and t not in STOP]
    return toks

def signature(toks):
    # model-like tokens: contain a digit, or are 4+ char brand-ish words
    return set(t for t in toks if any(c.isdigit() for c in t) or len(t)>=4)

# ---------- Melt ----------
def melt_value(category, desc):
    d=(desc or '').upper(); cat=(category or '').upper()
    is_gold = ('GOLD' in cat) or re.search(r'\b\d{1,2}\s*K\b', d) or ('Y/G' in d or 'W/G' in d or 'R/G' in d)
    is_silver = ('SILVER' in cat) or ('STERLING' in d) or ('925' in d) or ('.999' in d and 'SILVER' in (cat+d))
    # weight
    dwt = None
    m=re.search(r'([\d.]+)\s*DWT', d)
    if m: dwt=float(m.group(1))
    ozt=None
    if dwt is not None: ozt=dwt/DWT_PER_OZT
    else:
        m=re.search(r'([\d.]+)\s*(OZ|OUNCE|OZT)', d)
        if m: ozt=float(m.group(1))
    if ozt is None: return None,None
    if is_gold:
        km=re.search(r'\b(\d{1,2})\s*K\b', d)
        purity = KARAT.get(km.group(1), None) if km else None
        if purity is None and ('BULLION' in cat or '.999' in d or '999' in d): purity=0.999
        if purity is None: purity=0.585  # default if gold but karat unreadable (assume 14k)
        return round(ozt*purity*GOLD_SPOT,2), f"melt:{ozt:.3f}ozt x {purity} Au @${GOLD_SPOT}"
    if is_silver:
        purity = 0.999 if ('BULLION' in cat or '999' in d or '.999' in d) else 0.925
        return round(ozt*purity*SILVER_SPOT,2), f"melt:{ozt:.3f}ozt x {purity} Ag @${SILVER_SPOT}"
    return None,None

# ---------- Build comp index from historical SOLD items ----------
def build_comp_index():
    by_cat=collections.defaultdict(list)        # category -> list of (tokens, sig, sold_price)
    cat_prices=collections.defaultdict(list)    # category -> [sold_price]
    for f in glob.glob(BASE+'2025-05-17_to_2026-05-17_*_inventory-details.csv'):
        with open(f,newline='') as fh:
            for row in csv.DictReader(fh):
                sp=money(row.get('Last Sold Price'))
                if sp is None or sp<=0: continue
                cat=(row.get('Category') or '').strip()
                toks=norm_tokens(row.get('Description'))
                by_cat[cat].append((set(toks), signature(toks), sp))
                cat_prices[cat].append(sp)
    return by_cat, cat_prices

def model_tokens(toks):
    # model-like = contains a digit (e.g. CTB8172BK, 26, R500). Brand words excluded.
    return set(t for t in toks if any(c.isdigit() for c in t))

def comp_value(category, desc, by_cat, cat_prices):
    cat=(category or '').strip()
    toks=set(norm_tokens(desc)); mt=model_tokens(toks)
    pool=by_cat.get(cat,[])
    strong=[]   # shares a model-number token -> high confidence
    weak=[]     # shares only brand/word tokens
    for ctoks,csig,sp in pool:
        cmt=model_tokens(ctoks)
        shared_model = mt & cmt
        jac = len(toks & ctoks)/len(toks | ctoks) if (toks|ctoks) else 0
        if shared_model:
            strong.append((len(shared_model)+jac, sp))
        elif (toks & csig):
            weak.append((jac, sp))
    if strong:
        strong.sort(reverse=True)
        top=[sp for _,sp in strong[:7]]
        return round(statistics.median(top),2), "COMP", len(strong), "high"
    # category median (last resort). weak brand-only matches are NOT trusted for value.
    if cat_prices.get(cat):
        return round(statistics.median(cat_prices[cat]),2), "CAT", len(weak), "low"
    return None, "NONE", 0, "none"

# ---------- Load intake sample (real buys-from-public records) ----------
def load_intake():
    rows=[]
    for f in glob.glob(BASE+'2024-*_buys-from-public.csv'):
        store=re.search(r'_([A-Z]{3})_buys', f).group(1)
        with open(f,newline='') as fh:
            for row in csv.DictReader(fh):
                amt=money(row.get('Loan Amount'))
                if amt is None: continue
                rows.append({'store':store,'ticket':row.get('Ticket Number'),
                             'category':(row.get('Category') or '').strip(),
                             'desc':row.get('Full Description'),'cost':amt})
    return rows

def main():
    by_cat,cat_prices = build_comp_index()
    intake = load_intake()
    PM_RE=re.compile(r'GOLD|SILVER|COIN|BULLION|PLATINUM', re.I)
    valued=[]
    for it in intake:
        cat=it['category'] or ''
        is_pm = bool(PM_RE.search(cat))
        mv,mnote = melt_value(cat, it['desc'])
        if mv is not None and mv>0:
            val,src,n,conf = mv,'MELT',0,'high'
        elif is_pm:
            # precious metal but no parseable weight -> do NOT token-comp (generates garbage). Flag for weight.
            val,src,n,conf = None,'PM-NEEDS-WEIGHT',0,'none'
        else:
            val,src,n,conf = comp_value(cat, it['desc'], by_cat, cat_prices)
        # ── Tier 3: external market lookup for low/no-confidence items ──────────
        t3_src=None; t3_rlo=None; t3_rhi=None
        if USE_TIER3 and _t3 and conf in ('low','none') and not is_pm:
            try:
                t3 = _t3(it['desc'], cat, it['cost'])
                if t3.get('value') and t3['confidence'] in ('high','medium'):
                    val   = t3['value']
                    src   = t3['source']
                    conf  = t3['confidence']
                    n     = 0
                    t3_src= src; t3_rlo=t3['range_low']; t3_rhi=t3['range_high']
            except Exception:
                pass  # Tier 3 failure is non-fatal; keep T1/T2 result

        rec=dict(it)
        rec['value']=val; rec['source']=src; rec['comp_n']=n; rec['conf']=conf
        rec['t3_range_lo']=t3_rlo; rec['t3_range_hi']=t3_rhi
        rec['margin']= ((val-it['cost'])/val) if (val and val>0) else None
        # overpay/target trusted for high-confidence valuations (MELT, strong COMP, or T3 high/medium)
        trusted = conf in ('high','medium')
        rec['overpay']= 1 if (trusted and val is not None and it['cost']>val) else 0
        rec['meets']= 1 if (trusted and rec['margin'] is not None and rec['margin']>=TARGET) else 0
        rec['trusted']=1 if trusted else 0
        valued.append(rec)

    # write item-level CSV
    with open(OUT+'intake_valued_items.csv','w',newline='') as fh:
        w=csv.writer(fh)
        w.writerow(['Store','Ticket','Category','Description','Cost','EstValue','ValueSource',
                    'Confidence','CompN','RangeLow','RangeHigh','ImpliedMargin','MeetsTarget','OverpayFlag'])
        for r in valued:
            w.writerow([r['store'],r['ticket'],r['category'],r['desc'],r['cost'],
                        '' if r['value'] is None else r['value'], r['source'], r['conf'], r['comp_n'],
                        '' if r.get('t3_range_lo') is None else r['t3_range_lo'],
                        '' if r.get('t3_range_hi') is None else r['t3_range_hi'],
                        '' if r['margin'] is None else round(r['margin'],4), r['meets'], r['overpay']])

    # summary — stats on TRUSTED (high-confidence) valuations only
    trusted=[r for r in valued if r['trusted']==1]
    src_mix=collections.Counter(r['source'] for r in valued)
    overpays=[r for r in trusted if r['overpay']==1]
    under=[r for r in trusted if r['margin'] is not None and r['margin']<TARGET]
    def pct(a,b): return f"{(a/b*100):.1f}%" if b else "n/a"
    print("=== INTAKE VALUATION ENGINE v2 — item-level, precision-tightened ===")
    print(f"Spot: Gold ${GOLD_SPOT}/ozt  Silver ${SILVER_SPOT}/ozt   Target {int(TARGET*100)}%\n")
    print(f"Intake items: {len(valued)}")
    print(f"Source mix: {dict(src_mix)}")
    print(f"  (MELT + high-confidence COMP are TRUSTED for grading; CAT/PM-NEEDS-WEIGHT shown but not flagged)")
    print(f"Trusted valuations: {len(trusted)} ({pct(len(trusted),len(valued))})")
    tot_cost=sum(r['cost'] for r in trusted); tot_val=sum(r['value'] for r in trusted)
    print(f"Trusted intake — paid ${tot_cost:,.0f} vs est value ${tot_val:,.0f}  "
          f"=> blended margin {pct(tot_val-tot_cost,tot_val)}")
    print(f"Items below 50% target: {len(under)} ({pct(len(under),len(trusted))})")
    print(f"Outright overpays (cost > est value): {len(overpays)} ({pct(len(overpays),len(trusted))})")
    print("\nTop 12 trusted overpay flags (paid vs est value):")
    for r in sorted(overpays,key=lambda x:x['cost']-x['value'],reverse=True)[:12]:
        print(f"  {r['store']} {r['ticket']:<14} {r['category'][:20]:20} paid ${r['cost']:>6,.0f} vs est ${r['value']:>6,.0f} [{r['source']}] {str(r['desc'])[:32]}")

if __name__=='__main__':
    main()
