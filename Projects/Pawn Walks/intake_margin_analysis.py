#!/usr/bin/env python3
"""
Valley Pawn — Intake Margin Analysis
Grades what we take in (buys from public + forfeited-loan collateral) against the
~50% gross-margin target. Reuse-first: reads the existing Bravo `inventory-details`
pipeline CSVs (columns: Number, Status, Category, Description, Cost, Price,
Last Sold Price, Date). No new Bravo report required.

Margin definitions (gross margin on revenue):
  realized_margin = (Last Sold Price - Cost) / Last Sold Price   # actual outcome (SOLD items)
  markup_margin   = (Price - Cost) / Price                        # intended pricing discipline
Target: >= 50%  (i.e. we paid/loaned <= 50% of resale value)
"""
import csv, glob, json, collections, statistics, sys, os, re

BASE = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/"
OUT  = "/Users/joshuadavis/Documents/Claude/Projects/Pawn Walks/"
TARGET = 0.50
STORE_RE = re.compile(r'_([A-Z]{3})_inventory-details\.csv$')

def money(x):
    x = (x or '').replace('$','').replace(',','').strip()
    if x in ('', '-'): return None
    try: return float(x)
    except: return None

def margin(rev, cost):
    if rev is None or cost is None or rev <= 0: return None
    return (rev - cost) / rev

def load(pattern):
    rows = []
    for f in sorted(glob.glob(BASE + pattern)):
        m = STORE_RE.search(f)
        store = m.group(1) if m else '???'
        with open(f, newline='') as fh:
            for row in csv.DictReader(fh):
                row['_store'] = store
                rows.append(row)
    return rows

def summarize(items):
    """items: list of dicts with cost, rev (realized), price (asking), category, store."""
    n = len(items)
    deployed = sum(i['cost'] for i in items if i['cost'] is not None)
    revenue  = sum(i['rev']  for i in items if i['rev']  is not None)
    realized = [i['rm'] for i in items if i['rm'] is not None]
    intended = [i['mm'] for i in items if i['mm'] is not None]
    # dollar-weighted blended realized margin
    blended = margin(revenue, deployed)
    pass_items = sum(1 for i in items if i['rm'] is not None and i['rm'] >= TARGET)
    eligible   = sum(1 for i in items if i['rm'] is not None)
    pass_dollars = sum(i['rev'] for i in items if i['rm'] is not None and i['rm'] >= TARGET)
    return {
        'items': n,
        'deployed': round(deployed, 2),
        'revenue': round(revenue, 2),
        'gross_profit': round(revenue - deployed, 2),
        'blended_realized_margin': round(blended, 4) if blended is not None else None,
        'median_item_realized_margin': round(statistics.median(realized), 4) if realized else None,
        'median_item_markup_margin': round(statistics.median(intended), 4) if intended else None,
        'pct_items_meeting_target': round(pass_items / eligible, 4) if eligible else None,
        'pct_dollars_meeting_target': round(pass_dollars / revenue, 4) if revenue else None,
    }

def main():
    raw = load('2025-05-17_to_2026-05-17_*_inventory-details.csv')
    items = []
    for r in raw:
        cost = money(r.get('Cost'))
        price = money(r.get('Price'))
        rev = money(r.get('Last Sold Price'))
        items.append({
            'store': r['_store'],
            'category': (r.get('Category') or 'Unknown').strip(),
            'cost': cost, 'price': price, 'rev': rev,
            'rm': margin(rev, cost),
            'mm': margin(price, cost),
        })

    company = summarize(items)

    by_store = {}
    for s in sorted(set(i['store'] for i in items)):
        by_store[s] = summarize([i for i in items if i['store'] == s])

    # category roll-up (company-wide), ranked by capital deployed
    cats = collections.defaultdict(list)
    for i in items:
        cats[i['category']].append(i)
    cat_rows = []
    for c, lst in cats.items():
        s = summarize(lst)
        s['category'] = c
        cat_rows.append(s)
    cat_rows.sort(key=lambda x: x['deployed'], reverse=True)

    # worst performers among material categories (>= $1000 deployed), lowest blended margin
    material = [c for c in cat_rows if c['deployed'] >= 1000]
    worst = sorted(material, key=lambda x: (x['blended_realized_margin'] is None, x['blended_realized_margin']))[:12]

    result = {
        'window': '2025-05-17 to 2026-05-17 (trailing 12 months, SOLD items)',
        'stores_in_data': sorted(set(i['store'] for i in items)),
        'target_margin': TARGET,
        'company': company,
        'by_store': by_store,
        'categories_by_capital': cat_rows[:30],
        'worst_material_categories': worst,
        'notes': [
            'Source: existing Bravo inventory-details pipeline CSVs (SOLD items only in this pull).',
            'realized_margin = (Last Sold Price - Cost) / Last Sold Price.',
            'Cost = our dollars in at intake (buy price OR forfeited-loan principal basis).',
            'Stores in this baseline: HAR, LEX, ROA. CUL & WAY have a known inventory-details pipeline gap (per Optimize Loan Portfolio STATUS) — they join once the daily pull covers them.',
        ],
    }

    with open(OUT + 'intake_margin_summary.json', 'w') as fh:
        json.dump(result, fh, indent=2)

    # per-item flat CSV for the workbook Data sheet
    with open(OUT + 'intake_items.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Store','Category','Cost','AskingPrice','SoldPrice','RealizedMargin','MarkupMargin','MeetsTarget'])
        for i in items:
            w.writerow([
                i['store'], i['category'],
                '' if i['cost'] is None else round(i['cost'],2),
                '' if i['price'] is None else round(i['price'],2),
                '' if i['rev'] is None else round(i['rev'],2),
                '' if i['rm'] is None else round(i['rm'],4),
                '' if i['mm'] is None else round(i['mm'],4),
                1 if (i['rm'] is not None and i['rm'] >= TARGET) else 0,
            ])

    # console report
    def pct(x): return f"{x*100:.1f}%" if x is not None else "n/a"
    print("=== VALLEY PAWN — INTAKE MARGIN (realized, trailing 12 mo, SOLD) ===")
    print(f"Stores: {', '.join(result['stores_in_data'])}  |  Target: {int(TARGET*100)}% gross margin\n")
    c = company
    print(f"COMPANY: {c['items']:,} items | ${c['deployed']:,.0f} deployed -> ${c['revenue']:,.0f} revenue "
          f"| gross profit ${c['gross_profit']:,.0f}")
    print(f"  Blended realized margin: {pct(c['blended_realized_margin'])}  "
          f"(median item {pct(c['median_item_realized_margin'])})")
    print(f"  Items meeting 50% target: {pct(c['pct_items_meeting_target'])}  |  "
          f"Revenue meeting target: {pct(c['pct_dollars_meeting_target'])}\n")
    print("BY STORE (blended realized margin | % items >=50% | $ deployed):")
    for s, v in by_store.items():
        print(f"  {s}: {pct(v['blended_realized_margin'])} | {pct(v['pct_items_meeting_target'])} | ${v['deployed']:,.0f}")
    print("\nWORST MATERIAL CATEGORIES (>= $1k deployed, lowest blended margin):")
    for w in worst:
        print(f"  {w['category'][:34]:34} {pct(w['blended_realized_margin']):>7} "
              f"| {w['items']:>4} items | ${w['deployed']:>9,.0f} in | {pct(w['pct_items_meeting_target'])} hit")
    print("\nTOP CATEGORIES BY CAPITAL DEPLOYED:")
    for w in cat_rows[:12]:
        print(f"  {w['category'][:34]:34} {pct(w['blended_realized_margin']):>7} "
              f"| {w['items']:>4} items | ${w['deployed']:>9,.0f} in")

if __name__ == '__main__':
    main()
