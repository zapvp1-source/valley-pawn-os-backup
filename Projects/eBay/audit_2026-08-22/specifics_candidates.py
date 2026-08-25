import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
Q = json.load(open(os.path.join(D, 'quality_pull2.json')))
F = json.load(open(os.path.join(D, 'fees_specs.json')))

rows = []
for store, items in Q.items():
    for iid, v in items.items():
        try:
            p = float(v.get('price') or 0)
        except Exception:
            p = 0
        if p < 100:
            continue
        n = v.get('specifics', 0)
        if n >= 5:
            continue
        rows.append({'store': store, 'item': iid, 'price': p, 'specifics': n,
                     'title': v.get('title', ''), 'cat': v.get('cat')})

rows.sort(key=lambda r: -r['price'])
print('candidates (active, >=$100, <5 item specifics): %d, total value $%.0f' % (
    len(rows), sum(r['price'] for r in rows)))

lines = ['# eBay item-specifics fill queue (>=$100 listings, <5 specifics)',
         '',
         'Generated 2026-08-23 from the audit data. NOT auto-filled — see reasoning below.',
         '',
         '## Why this is a candidate list, not an auto-applied fix',
         '',
         'Item specifics (Body Material, Storage, Ring Size, etc.) require real per-item facts —',
         'guessing them from the title risks the exact failure the 2026-08-22 incident produced on',
         'the Sony ZV-E10 listing (a fabricated "Body" claim contradicted by the item\'s own MPN).',
         'The existing `ebay-weekly-quality-fix` and `ebay-title-photo-accuracy-audit` weekly tasks',
         'already do this kind of enrichment carefully, cross-checking full-res photos before writing',
         'anything. This list hands them a prioritized queue (highest-value listings first) instead of',
         'letting a bulk script assert facts nobody verified.',
         '',
         '| Store | Item | Price | Specifics now | Title |',
         '|---|---|---:|---:|---|']
for r in rows[:80]:
    lines.append('| %s | %s | $%.2f | %d | %s |' % (
        r['store'], r['item'], r['price'], r['specifics'], r['title'][:70].replace('|', '/')))
if len(rows) > 80:
    lines.append('')
    lines.append('_...and %d more, full list in specifics_candidates.json_' % (len(rows) - 80))

open(os.path.join(D, 'SPECIFICS_FILL_QUEUE.md'), 'w').write('\n'.join(lines))
json.dump(rows, open(os.path.join(D, 'specifics_candidates.json'), 'w'), indent=1)
print('wrote SPECIFICS_FILL_QUEUE.md and specifics_candidates.json')
