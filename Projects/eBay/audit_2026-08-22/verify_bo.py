import os, json, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
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
        return r.read().decode()


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text else d


Q = json.load(open(os.path.join(D, 'quality_pull2.json')))
tok = {s['name']: s['token'] for s in ns['STORES']}
out = []
# 12 Culpeper items GetSellerList reported as best_offer != true
cands = [i for i, v in Q['Culpeper'].items() if str(v.get('best_offer')).lower() != 'true'][:12]
for iid in cands:
    raw = call(tok['Culpeper'], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
    r = ET.fromstring(raw)
    it = r.find('.//{%s}Item' % NS)
    bo = it.find('{%s}BestOfferDetails' % NS)
    ld = it.find('{%s}ListingDetails' % NS)
    out.append({'id': iid, 'sellerlist_said': Q['Culpeper'][iid].get('best_offer'),
                'getitem_enabled': T(bo, 'BestOfferEnabled') if bo is not None else 'NO_NODE',
                'dispatch': T(it, 'DispatchTimeMax'),
                'ret_within': T(it.find('{%s}ReturnPolicy' % NS), 'ReturnsWithinOption') if it.find('{%s}ReturnPolicy' % NS) is not None else None,
                'ret_ship': T(it.find('{%s}ReturnPolicy' % NS), 'ShippingCostPaidByOption') if it.find('{%s}ReturnPolicy' % NS) is not None else None,
                'price': T(it.find('{%s}SellingStatus' % NS), 'CurrentPrice'),
                'title': (T(it, 'Title') or '')[:50]})
    time.sleep(0.2)
for o in out:
    print(o)
json.dump(out, open(os.path.join(D, 'verify_bo.json'), 'w'), indent=1)
