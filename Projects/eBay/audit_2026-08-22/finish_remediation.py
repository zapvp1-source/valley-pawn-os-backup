import json, os, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'
STATE = os.path.join(HOME, 'vp_ebay_fix_state.json')

MISSING_A = ['298122752867', '307137703602', '298604747511', '298575709087',
             '307104894147', '298262387151', '298604754102', '298505042432']
MISSING_B = ['398235964930']
STORE_A = 'Roanoke'
STORE_B = {'398235964930': None}  # resolve via GetItem lookup below is unnecessary; find store from quality_pull2

D = os.path.dirname(os.path.abspath(__file__))
Q = json.load(open(os.path.join(D, 'quality_pull2.json')))
store_of = {}
for store, items in Q.items():
    for iid in items:
        store_of[iid] = store


def call(tok, name, inner):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            ) % (name, tok, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': ns['APP_ID'],
         'X-EBAY-API-DEV-NAME': ns['DEV_ID'], 'X-EBAY-API-CERT-NAME': ns['CERT_ID'],
         'X-EBAY-API-IAF-TOKEN': tok, 'Content-Type': 'text/xml'}
    with urlopen(Request('https://api.ebay.com/ws/api.dll', data=body.encode(), headers=h), timeout=90) as r:
        return ET.fromstring(r.read().decode())


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text else d


RET30 = ('<ReturnPolicy><ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>'
         '<RefundOption>MoneyBack</RefundOption>'
         '<ReturnsWithinOption>Days_30</ReturnsWithinOption>'
         '<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption></ReturnPolicy>')

st = json.load(open(STATE))
done, skipped, failed = [], [], []

for iid in MISSING_A + MISSING_B:
    fix = 'A' if iid in MISSING_A else 'B'
    store = STORE_A if fix == 'A' else store_of.get(iid)
    if not store:
        failed.append((fix, iid, 'store unknown'))
        continue
    key = '%s|%s|%s' % (fix, store, iid)
    if key in st:
        skipped.append(key)
        continue
    r = call(TOK[store], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
    it = r.find('.//{%s}Item' % NS)
    if it is None:
        failed.append((fix, iid, 'no item / auction ended'))
        continue
    status = T(it.find('{%s}SellingStatus' % NS), 'ListingStatus')
    rp = it.find('{%s}ReturnPolicy' % NS)
    before = {'returns': T(rp, 'ReturnsAcceptedOption'), 'returns_within': T(rp, 'ReturnsWithinOption'),
              'ret_ship_by': T(rp, 'ShippingCostPaidByOption')}
    if status != 'Active':
        failed.append((fix, iid, 'status=%s, skipping (ended, cannot revise)' % status))
        continue
    if before['returns'] == 'ReturnsAccepted' and before['returns_within'] == 'Days_30':
        st[key] = {'before': before, 'label': 'already-correct-on-recheck'}
        done.append((fix, iid, 'already correct'))
        json.dump(st, open(STATE, 'w'), indent=1)
        continue
    r2 = call(TOK[store], 'ReviseFixedPriceItem', '<Item><ItemID>%s</ItemID>%s</Item>' % (iid, RET30))
    ack = T(r2, 'Ack')
    if ack in ('Success', 'Warning'):
        st[key] = {'before': before, 'label': '%s (retry batch)' % ('14d -> 30d returns' if fix == 'A' else 'no returns -> 30d returns')}
        json.dump(st, open(STATE, 'w'), indent=1)
        done.append((fix, iid, ack))
    else:
        errs = [T(e, 'LongMessage') for e in r2.findall('.//{%s}Errors' % NS)]
        failed.append((fix, iid, '; '.join(errs[:1])))
    time.sleep(0.3)

print('DONE:', len(done))
for d in done:
    print('  ', d)
print('SKIPPED (already in state):', skipped)
print('FAILED:', len(failed))
for f in failed:
    print('  ', f)
