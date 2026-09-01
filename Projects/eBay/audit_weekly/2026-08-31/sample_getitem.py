#!/usr/bin/env python3
# GetMyeBaySelling under-returns detail fields (pics/specifics/BestOffer/ReturnPolicy/DispatchTime
# all came back empty/None on the bulk pull - confirmed 2026-08-31, same class of gap the 2026-08-22
# audit hit with item specifics). Sample-verify via GetItem instead, same methodology as 2026-08-22.
import json, os, random, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
STORES = ns['STORES']; APP_ID = ns['APP_ID']; DEV_ID = ns['DEV_ID']; CERT_ID = ns['CERT_ID']
NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(20260831)

def q(name): return '{%s}%s' % (NS, name)
def T(el, tag, d=None):
    if el is None: return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text is not None else d

def call(token, name, inner, tries=3):
    body = ('<?xml version="1.0" encoding="utf-8"?>'
            '<%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>'
            '%s</%sRequest>') % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967',
         'X-EBAY-API-CALL-NAME':name,'X-EBAY-API-APP-NAME':APP_ID,
         'X-EBAY-API-DEV-NAME':DEV_ID,'X-EBAY-API-CERT-NAME':CERT_ID,
         'X-EBAY-API-IAF-TOKEN':token,'Content-Type':'text/xml'}
    last = None
    for i in range(tries):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=60) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception as e:
            last = e; time.sleep(2)
    raise last

def get_item(token, item_id):
    inner = '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel><IncludeItemSpecifics>true</IncludeItemSpecifics>' % item_id
    r = call(token, 'GetItem', inner)
    it = r.find(q('Item'))
    if it is None: return None
    pd = it.find(q('PictureDetails'))
    bo = it.find(q('BestOfferDetails'))
    rp = it.find(q('ReturnPolicy'))
    return {
        'id': item_id,
        'pics': len(pd.findall(q('PictureURL'))) if pd is not None else 0,
        'best_offer': (T(bo,'BestOfferEnabled') or 'false').lower() == 'true',
        'condition': T(it, 'ConditionDisplayName'),
        'dispatch_max': T(it, 'DispatchTimeMax'),
        'returns_accepted': T(rp, 'ReturnsAcceptedOption'),
        'returns_within': T(rp, 'ReturnsWithinOption'),
        'shipping_cost_paid_by': T(rp, 'ShippingCostPaidByOption'),
        'specifics_count': len(it.findall('.//' + q('NameValueList'))),
        'title_len': len(T(it,'Title','') or ''),
    }

raw = json.load(open(os.path.join(OUT, 'raw_pull.json')))
results = {}
for s in STORES:
    name = s['name']
    active = raw.get(name, {}).get('active', [])
    ids = [a['id'] for a in active if a.get('id')]
    if len(ids) <= 40:
        sample_ids = ids
    else:
        sample_ids = random.sample(ids, 60)
    got = []
    errs = 0
    for iid in sample_ids:
        try:
            r = get_item(s['token'], iid)
            if r: got.append(r)
        except Exception as e:
            errs += 1
    results[name] = {'sample_size': len(got), 'population_size': len(ids), 'errors': errs, 'items': got}
    print(name, 'sampled', len(got), 'of', len(ids), 'errors', errs, flush=True)

with open(os.path.join(OUT, 'sample_results.json'), 'w') as f:
    json.dump(results, f, indent=1)
print('SAMPLE_DONE', flush=True)
