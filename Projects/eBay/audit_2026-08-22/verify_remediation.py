import json, os, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'
D = os.path.dirname(os.path.abspath(__file__))


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


st = json.load(open(os.path.join(HOME, 'vp_ebay_fix_state.json')))
Q = json.load(open(os.path.join(D, 'quality_pull2.json')))

# Build the ORIGINAL target sets fresh from the audit's own quality_pull2.json (verified data),
# same rules the fix script used, so we can diff "should have been touched" vs "state says touched"
# vs "live now confirms fixed".
targets = {'A': [], 'B': [], 'C': []}
for store, items in Q.items():
    for iid, r in items.items():
        acc = r.get('returns'); within = r.get('returns_within')
        if store == 'Roanoke' and acc == 'ReturnsAccepted' and within == 'Days_14':
            targets['A'].append((store, iid))
        elif acc != 'ReturnsAccepted':
            targets['B'].append((store, iid))
        if store == 'Culpeper' and str(r.get('best_offer')).lower() != 'true':
            try:
                p = float(r.get('price') or 0)
            except Exception:
                p = 0
            if p > 0:
                targets['C'].append((store, iid))

for fix in ('A', 'B', 'C'):
    in_state = set(k.split('|')[2] for k in st if k.startswith(fix + '|'))
    tgt_ids = set(i for _, i in targets[fix])
    missing = tgt_ids - in_state
    print('%s  target=%d  in_state=%d  missing_from_state=%d' % (fix, len(tgt_ids), len(in_state), len(missing)))
    if missing:
        print('   missing ids:', list(missing)[:20])

# Now spot-check LIVE state on a random sample of 8 per fix to confirm the API calls actually stuck
import random
random.seed(11)
print('\n=== LIVE VERIFICATION SAMPLE ===')
out = []
for fix in ('A', 'B', 'C'):
    keys = [k for k in st if k.startswith(fix + '|')]
    sample = random.sample(keys, min(8, len(keys)))
    for k in sample:
        _, store, iid = k.split('|')
        r = call(TOK[store], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
        it = r.find('.//{%s}Item' % NS)
        if it is None:
            out.append((fix, store, iid, 'NO ITEM'))
            continue
        rp = it.find('{%s}ReturnPolicy' % NS)
        bo = it.find('{%s}BestOfferDetails' % NS)
        status = T(it.find('{%s}SellingStatus' % NS), 'ListingStatus')
        if fix in ('A', 'B'):
            ok = (T(rp, 'ReturnsAcceptedOption') == 'ReturnsAccepted' and T(rp, 'ReturnsWithinOption') == 'Days_30'
                  and T(rp, 'ShippingCostPaidByOption') == 'Buyer')
            detail = 'accepted=%s within=%s' % (T(rp, 'ReturnsAcceptedOption'), T(rp, 'ReturnsWithinOption'))
        else:
            ok = T(bo, 'BestOfferEnabled') == 'true' if bo is not None else False
            aap = T(bo, 'BestOfferAutoAcceptPrice') if bo is not None else None
            detail = 'enabled=%s autoaccept=%s' % (T(bo, 'BestOfferEnabled') if bo is not None else None, aap)
        out.append((fix, store, iid, status, ok, detail))
        time.sleep(0.2)

for row in out:
    print(' ', row)

confirmed = sum(1 for r in out if len(r) >= 5 and r[4])
print('\nconfirmed live-correct: %d / %d sampled' % (confirmed, len(out)))
