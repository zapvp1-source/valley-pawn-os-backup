#!/usr/bin/env python3
"""
Valley Pawn eBay remediation — REVERSIBLE, additive, from the 2026-08-22 audit.

FIX A  Roanoke 14-day returns -> 30-day returns (matches the company 30-day warranty).
FIX B  Listings accepting NO returns -> 30-day returns, buyer-paid, money back.
FIX C  Culpeper listings with Best Offer OFF -> ON, auto-accept 90% of list,
       auto-decline below 75% of list (thresholds per ebay-context skill).

NOT DONE HERE (deliberate): handling time 2/3d -> 1d. That change only pays off if the
stores can actually ship in 1 business day; Lexington is already Below Standard on late
shipments (4.23%). Applying it blind would risk pushing more stores under. Needs per-store
late-ship data first.

State written to ~/vp_ebay_fix_state.json so every change can be reverted.
Usage: vp_ebay_fix.py [--apply] [--revert] [--only A|B|C]
"""
import json, os, sys, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
STORES = {s['name']: s for s in ns['STORES']}
APP_ID = ns['APP_ID']; DEV_ID = ns['DEV_ID']; CERT_ID = ns['CERT_ID']
NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
BASE = os.path.expanduser('~/Documents/Claude/Projects/eBay/audit_2026-08-22/')
STATE = os.path.expanduser('~/vp_ebay_fix_state.json')
Q = json.load(open(BASE + 'quality_pull.json'))

APPLY = '--apply' in sys.argv
REVERT = '--revert' in sys.argv
ONLY = None
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1].upper()

def call(token, name, inner, tries=3):
    body = ('<?xml version="1.0" encoding="utf-8"?>'
            '<%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>'
            '%s</%sRequest>') % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': APP_ID,
         'X-EBAY-API-DEV-NAME': DEV_ID, 'X-EBAY-API-CERT-NAME': CERT_ID,
         'X-EBAY-API-IAF-TOKEN': token, 'Content-Type': 'text/xml'}
    for i in range(tries):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=90) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2)

def revise(store, item_xml):
    r = call(STORES[store]['token'], 'ReviseFixedPriceItem', '<Item>%s</Item>' % item_xml)
    ack = r.findtext('{%s}Ack' % NS, '')
    msg = r.findtext('.//{%s}LongMessage' % NS) or r.findtext('.//{%s}ShortMessage' % NS) or ack
    return ack in ('Success', 'Warning'), (msg or '')[:180]

RET30 = ('<ReturnPolicy><ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>'
         '<RefundOption>MoneyBack</RefundOption>'
         '<ReturnsWithinOption>Days_30</ReturnsWithinOption>'
         '<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption></ReturnPolicy>')

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

# ---------------- build work list ----------------
jobs = []   # (fix, store, itemid, xml, before_dict, label)
for store, items in Q.items():
    for iid, r in items.items():
        within = r.get('returns_within'); acc = r.get('returns')
        before = {'returns': acc, 'returns_within': within,
                  'ret_ship_by': r.get('ret_ship_by'), 'best_offer': r.get('best_offer'),
                  'price': r.get('price')}
        if store == 'Roanoke' and acc == 'ReturnsAccepted' and within == 'Days_14':
            jobs.append(('A', store, iid, '<ItemID>%s</ItemID>%s' % (iid, RET30), before,
                         '14d -> 30d returns'))
        elif acc != 'ReturnsAccepted':
            jobs.append(('B', store, iid, '<ItemID>%s</ItemID>%s' % (iid, RET30), before,
                         'no returns -> 30d returns'))
        if store == 'Culpeper' and r.get('best_offer') != 'true':
            try:
                p = float(r.get('price') or 0)
            except Exception:
                p = 0
            if p <= 0:
                continue
            acc_p = round(p * 0.90, 2); dec_p = round(p * 0.75, 2)
            xml = ('<ItemID>%s</ItemID>'
                   '<BestOfferDetails><BestOfferEnabled>true</BestOfferEnabled></BestOfferDetails>'
                   '<ListingDetails>'
                   '<BestOfferAutoAcceptPrice currencyID="USD">%.2f</BestOfferAutoAcceptPrice>'
                   '<MinimumBestOfferPrice currencyID="USD">%.2f</MinimumBestOfferPrice>'
                   '</ListingDetails>') % (iid, acc_p, dec_p)
            jobs.append(('C', store, iid, xml, before,
                         'BestOffer ON (accept>=$%.2f, decline<$%.2f)' % (acc_p, dec_p)))

if ONLY:
    jobs = [j for j in jobs if j[0] == ONLY]

# ---------------- revert ----------------
if REVERT:
    for key, rec in list(state.items()):
        fix, store, iid = key.split('|')
        b = rec['before']
        if fix in ('A', 'B'):
            if b['returns'] == 'ReturnsAccepted':
                xml = ('<ItemID>%s</ItemID><ReturnPolicy>'
                       '<ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>'
                       '<RefundOption>MoneyBack</RefundOption>'
                       '<ReturnsWithinOption>%s</ReturnsWithinOption>'
                       '<ShippingCostPaidByOption>%s</ShippingCostPaidByOption></ReturnPolicy>'
                       ) % (iid, b['returns_within'], b['ret_ship_by'])
            else:
                xml = ('<ItemID>%s</ItemID><ReturnPolicy>'
                       '<ReturnsAcceptedOption>ReturnsNotAccepted</ReturnsAcceptedOption>'
                       '</ReturnPolicy>') % iid
        else:
            xml = ('<ItemID>%s</ItemID><BestOfferDetails>'
                   '<BestOfferEnabled>false</BestOfferEnabled></BestOfferDetails>') % iid
        if APPLY:
            ok, m = revise(store, xml)
            print(('OK   ' if ok else 'FAIL ') + key, m)
            if ok: state.pop(key, None)
        else:
            print('DRY-REVERT', key)
    if APPLY: json.dump(state, open(STATE, 'w'), indent=1)
    sys.exit()

# ---------------- apply ----------------
from collections import Counter
print('WORK LIST:', dict(Counter(j[0] for j in jobs)), '| total', len(jobs))
if not APPLY:
    for fix, store, iid, xml, before, label in jobs[:15]:
        print('  DRY %s %-13s %s  %s' % (fix, store, iid, label))
    print('  ... (%d total; run with --apply)' % len(jobs))
    sys.exit()

res = Counter(); fails = []
for n, (fix, store, iid, xml, before, label) in enumerate(jobs, 1):
    key = '%s|%s|%s' % (fix, store, iid)
    if key in state:
        res['skip'] += 1; continue
    try:
        ok, m = revise(store, xml)
    except Exception as e:
        ok, m = False, str(e)[:180]
    if ok:
        state[key] = {'before': before, 'label': label}
        res[fix] += 1
    else:
        res['FAIL'] += 1; fails.append((key, label, m))
    if n % 25 == 0:
        print('  ...%d/%d  %s' % (n, len(jobs), dict(res)), flush=True)
        json.dump(state, open(STATE, 'w'), indent=1)

json.dump(state, open(STATE, 'w'), indent=1)
print('\nRESULT:', dict(res))
if fails:
    print('\nFAILURES (%d), first 20:' % len(fails))
    for k, l, m in fails[:20]:
        print('  ', k, '|', l, '|', m)
print('\nState: %s  (revert with --revert --apply)' % STATE)
