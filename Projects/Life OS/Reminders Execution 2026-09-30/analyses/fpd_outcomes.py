#!/usr/bin/env python3
"""
fpd_outcomes.py -- First-payment-default -> forfeit vs. pay (READ-ONLY, additive)
Built 2026-09-30 for Joshua's reminders plan item "FPD to expire correlations or to pay".

Reads ONLY existing Bravo pipeline CSVs (never drives Bravo):
  output/<date>_<STORE>_fpd-cohort.csv          weekly "Claude First Payment Default" snapshots
  output/2026-09-29_<STORE>_forfeiture-winback.csv  every EXPIRED loan, ~Nov 2024 - 9/29/2026

Facts established from the data (verified in this script's checks):
  * Age = days since the ORIGINAL pawn date (Age + pawn date = capture date for 90%+ rows).
  * Due Date - pawn date = 30 x (1 + number of paid 30-day extensions).  Due-pawn == 30 means the
    loan never had its due date moved by a payment.
  * Pull Date = Due Date + 16 days (grace) on every row.
  * The fpd-cohort saved report returns loans ON LOAN, NO payment ever (Last Payment blank), aged
    46+ days (at/after the pull date).  Some snapshot files are mislabelled (8/30 CUL/ROA/WAY are a
    9/6 capture), so the capture date is taken from each row (pawn date + Age), not the filename.

LENS A (cohort, the direct answer): every loan that appeared in any fpd-cohort snapshot
  (hard FPD: reached its pull date with zero payments).  Outcome as of 9/29/2026:
    FORFEITED  -> ticket is in the 9/29 expired-loan list
    CURED      -> dropped off a later snapshot without being expired (a payment, redemption,
                  renewal, buy-out or void happened -- the data cannot say which)
    OPEN/UNKNOWN -> still on the store's latest snapshot and not expired by 9/29
LENS B (2-year, reverse view): of all loans that expired, what share never had one paid
  extension (due date = pawn + 30).
"""
import csv, glob, os, collections, datetime as dt, json, sys

OUT = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/'
if not os.path.isdir(OUT):
    OUT = '/sessions/' + os.environ.get('SESS', 'loving-great-ramanujan') + '/mnt/Projects/Bravo Data Extraction/output/'
HERE = os.path.dirname(os.path.abspath(__file__))
STORES = ['CUL', 'HAR', 'LEX', 'ROA', 'WAY']
P = lambda s: dt.datetime.strptime(s.strip(), '%m/%d/%Y').date()
money = lambda s: float(s.replace('$', '').replace(',', '').replace('(', '-').replace(')', '') or 0)


def band(a):
    for lo, hi, lab in [(0, 50, '$0-49'), (50, 100, '$50-99'), (100, 250, '$100-249'),
                        (250, 500, '$250-499'), (500, 1e12, '$500+')]:
        if lo <= a < hi:
            return lab


# Category -> department.  EXPLICIT map over the real Bravo category names found in the snapshots
# (170 names, 2026-09-30).  Replaces the first run's keyword matcher, which mis-filed 'Chainsaw' as
# jewelry ('chain'), 'Smart Watch' as jewelry, 'Car Amplifier' as a musical instrument and coins /
# bullion as jewelry.  Any category not listed falls to 'Other' and is counted in the summary.
FIREARMS = {'Pistol', 'Rifle', 'Shotgun', 'Revolver'}
SPORT = {'Firearm Scope', 'Binocular/Scope', 'Ammunition', 'Air Gun/Pellet Gun/BB Gun', 'Crossbow',
         'Bow', 'Hunting Gear', 'Hunting Knife', 'Combat Knife', 'Display Knife', 'Pocket Knife',
         'Vest/Armor', 'Fishing Tackle', 'Camping', 'Paintball', 'Mace/Pepper Spray', 'Metal Detector',
         'Backpack'}
COINS = {'Silver Coin', 'Silver Bullion'}
MUSIC = {'Acoustic Guitar', 'Bass Guitar', 'Bass Guitar Amp', 'Electric Guitar', 'Electric Guitar Amp',
         'Electric-Acoustic Guitar', 'Amplifier/Tube Amp', 'Drum', 'Microphone', 'Effect Equipment',
         'DJ Equipment', 'Computer Recording'}
TOOLS = {'Air Compressor', 'Battery', 'Battery Charger', 'Chainsaw', 'Circular Saw', 'Combination Tool Set',
         'Cordless Drill', 'Diagnostic Tool/Equipment', 'Disc Grinder', 'Electrician Tool', 'Fans/Blowers',
         'Generator', 'Hammer', 'Hand Tool', 'Hedge Trimmer', 'Impact Wrench/Driver', 'Ladder', 'Laser Level',
         'Lawn Edger', 'Lawn Trimmer', 'Leaf Blower', 'Level/Plumb Tool', 'MIG Welder', 'Misc Battery/Charger',
         'Misc Drill/Driver', 'Misc Lawn Tool', 'Misc Safety Gear', 'Misc Tool', 'Miter Saw', 'Mixed Tool Box/Set',
         'Multi-Tool', 'Nailer/Stapler', 'Polisher', 'Pressure Washer', 'Reciprocating Saw', 'Rotary Hammer',
         'Sockets/Ratchet', 'Table Saw', 'Tile Saw', 'Tiller', 'Tool Bag/Belt/Pouch', 'Tool Rollaway Box',
         'Tool Storage Box', 'Welding Helmet', 'Wire Feed Welder', 'Work Light', 'Heater', 'Vacuum Cleaner'}
ELEC = {'Camera Accessory', 'Car Amplifier', 'Computer Accessories', 'Computer Component', 'Digital Camera',
        'Flat Panel Television', 'Game Console', 'Headphones', 'Laptop/Netbook', 'Lens/Filter',
        'Microsoft XBOX One Game', 'Monitor/Speakers', 'Nintendo 64 Game', 'Nintendo DS', 'Nintendo GBA Game',
        'PC Desktop', 'PlayStation 4', 'PlayStation 5', 'PlayStation Portable', 'Projector', 'Radio',
        'Smart Watch', 'Sony PSP Game', 'Speakers', 'Super Nintendo', 'Surround Sound Speakers & System',
        'Tablet', 'VR - Video Glasses', 'Video Game Controller', 'XBox 360', 'XBox ONE', 'XBox ONE X',
        'Xbox Series S Console', 'Xbox Series X Console'}
JEWEL_WORDS = ('Ring', 'Wedding', 'Bracelet', 'Chain', 'Earring', 'Necklace', 'Pendant', 'Charm', 'Gold',
               'Silver', 'Platinum', 'Wristwatch', 'Pocket Watch', 'Bangle', 'Diamond')


def dept(cat):
    c = (cat or '').strip()
    if not c:
        return 'Not recorded'
    for name, group in [('Firearms', FIREARMS), ('Hunting, knives & outdoor', SPORT), ('Coins & bullion', COINS),
                        ('Musical instruments', MUSIC), ('Tools & lawn', TOOLS), ('Electronics & games', ELEC)]:
        if c in group:
            return name
    if c != 'Chainsaw' and any(w in c for w in JEWEL_WORDS):
        return 'Jewelry & watches'
    return 'Other'


def load_expired():
    exp = {}
    allrows = collections.defaultdict(list)
    for s in STORES:
        f = OUT + f'2026-09-29_{s}_forfeiture-winback.csv'
        for x in csv.DictReader(open(f, encoding='utf-8-sig')):
            allrows[(s, x['Ticket Number'])].append(x)
    for (s, t), rows in allrows.items():
        x = rows[0]
        pawn = dt.date(2026, 9, 29) - dt.timedelta(int(x['Age']))
        exp[t] = dict(store=s, ticket=t, exp=P(x['Disposition Date']), due=P(x['Due Date']), pawn=pawn,
                      amt=sum(money(r['Loan Amount']) for r in rows))
    return exp


L75 = set()
for _f in glob.glob(OUT + '2026-09-30_*_loans75-detail.csv'):
    L75 |= {x['Ticket Number'] for x in csv.DictReader(open(_f, encoding='utf-8-sig'))}


def lens_a(exp):
    tickets = {}
    captures = collections.defaultdict(set)   # store -> set(capture dates)
    seen = collections.defaultdict(lambda: collections.defaultdict(set))  # store->capture->tickets
    for f in sorted(glob.glob(OUT + '2026-0[5-9]-*_fpd-cohort.csv')):
        s = os.path.basename(f)[11:14]
        rows = list(csv.DictReader(open(f, encoding='utf-8-sig')))
        if not rows or 'Ticket Number' not in rows[0]:
            continue
        # capture date of the FILE = most common (pawn date + Age) across its rows; a few rows
        # carry a non-pawn Disposition Date and would otherwise yield impossible future dates.
        cap = collections.Counter(P(x['Disposition Date']) + dt.timedelta(int(x['Age']))
                                  for x in rows).most_common(1)[0][0]
        for x in rows:
            pawn = cap - dt.timedelta(int(x['Age']))
            captures[s].add(cap)
            seen[s][cap].add(x['Ticket Number'])
            t = tickets.setdefault(x['Ticket Number'], dict(store=s, pawn=pawn, due=P(x['Due Date']),
                                                           items={}, first=cap, last=cap))
            t['first'] = min(t['first'], cap); t['last'] = max(t['last'], cap)
            key = (x.get('Full Description', ''), x['Loan Amount'], x.get('Category', ''))
            t['items'][key] = (money(x['Loan Amount']), x.get('Category', ''))
    res = []
    for tk, t in tickets.items():
        amt = sum(v[0] for v in t['items'].values())
        topcat = max(t['items'].values(), key=lambda v: v[0])[1]
        last_store_cap = max(captures[t['store']])
        if tk in exp and exp[tk]['exp'] >= t['pawn']:
            out = 'Forfeited'
            days = (exp[tk]['exp'] - t['pawn']).days
        elif t['last'] < last_store_cap:
            out = 'Cured (paid/redeemed/renewed)'
            days = None
        else:
            out = 'Still open / unknown'
            days = None
        # 9/30 cross-check: Bravo's '75 Days Past Due' list pulled 9/30 (loans75-detail, all 5
        # stores).  A still-open ticket on it is CONFIRMED still on loan and unpaid on 9/30.  Used
        # only positively -- absence from it proves nothing (it only lists loans >75 days past due).
        confirmed = (out == 'Still open / unknown' and tk in L75)
        res.append(dict(ticket=tk, store=t['store'], pawn=str(t['pawn']), amount=round(amt, 2),
                        band=band(amt), category=topcat, dept=dept(topcat), outcome=out,
                        days_to_expire=days, first_seen=str(t['first']), last_seen=str(t['last']),
                        on_930_past_due_list=confirmed))
    return res, {s: sorted(str(c) for c in captures[s]) for s in captures}


def lens_b(exp):
    rows = []
    for t in exp.values():
        k = (t['due'] - t['pawn']).days
        rows.append(dict(t, ext=(k // 30 - 1) if k % 30 == 0 else None, span=k))
    return rows


def tab(rows, key, outcomes):
    g = collections.defaultdict(collections.Counter)
    d = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in rows:
        g[r[key]][r['outcome']] += 1
        d[r[key]][r['outcome']] += r['amount']
    return g, d


if __name__ == '__main__':
    exp = load_expired()
    A, caps = lens_a(exp)
    B = lens_b(exp)
    with open(os.path.join(HERE, 'fpd_cohort_outcomes.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(A[0].keys())); w.writeheader(); w.writerows(A)
    # checks
    bad_span = sum(1 for r in B if r['ext'] is None)
    summary = dict(captures=caps, n_fpd_tickets=len(A), expired_tickets=len(B), expired_bad_span=bad_span)
    outs = ['Forfeited', 'Cured (paid/redeemed/renewed)', 'Still open / unknown']
    for key in ['store', 'band', 'dept']:
        g, d = tab(A, key, outs)
        summary['A_by_' + key] = {k: {o: [g[k][o], round(d[k][o], 2)] for o in outs} for k in sorted(g)}
    tot = collections.Counter(r['outcome'] for r in A)
    totd = collections.defaultdict(float)
    for r in A: totd[r['outcome']] += r['amount']
    summary['A_total'] = {o: [tot[o], round(totd[o], 2)] for o in outs}
    dte = sorted(r['days_to_expire'] for r in A if r['days_to_expire'] is not None)
    summary['A_open_confirmed_on_930_list'] = [sum(1 for r in A if r['on_930_past_due_list']),
                                                round(sum(r['amount'] for r in A if r['on_930_past_due_list']), 2)]
    summary['A_open_by_store_confirmed'] = {s_: sum(1 for r in A if r['on_930_past_due_list'] and r['store'] == s_) for s_ in STORES}
    summary['A_days_to_expire_median'] = dte[len(dte) // 2] if dte else None
    # lens B
    lb = collections.defaultdict(lambda: collections.Counter())
    lbd = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in B:
        # The expired-loan list only contains loans pawned on/after ~9/30/2024, so expirations
        # before mid-2025 are biased toward never-extended loans.  Use 7/1/2025+ expirations only.
        if r['ext'] is None or r['exp'] < dt.date(2025, 7, 1): continue
        z = 'never extended' if r['ext'] == 0 else 'extended 1+'
        for k in [('store', r['store']), ('band', band(r['amt'])), ('all', 'all'),
                  ('year', str(r['exp'].year) + ('H1' if r['exp'].month <= 6 else 'H2'))]:
            lb[k][z] += 1; lbd[k][z] += r['amt']
    summary['B'] = {f'{k[0]}:{k[1]}': {z: [lb[k][z], round(lbd[k][z], 2)] for z in ['never extended', 'extended 1+']} for k in sorted(lb)}
    # days from pawn to expiry for never-extended forfeits
    lag = sorted((r['exp'] - r['pawn']).days for r in B if r['ext'] == 0 and r['exp'] >= dt.date(2025, 7, 1))
    summary['B_never_ext_days_pawn_to_expiry_p50_p90'] = [lag[len(lag) // 2], lag[int(len(lag) * .9)]]
    json.dump(summary, open(os.path.join(HERE, 'fpd_outcomes_summary.json'), 'w'), indent=1, default=str)
    print(json.dumps(summary, indent=1, default=str))
