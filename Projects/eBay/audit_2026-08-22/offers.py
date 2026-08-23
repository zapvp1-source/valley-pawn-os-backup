import os, json, time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
NS = 'urn:ebay:apis:eBLBaseComponents'
OUT = os.path.dirname(os.path.abspath(__file__))


def call(tok, name, inner):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            ) % (name, tok, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': ns['APP_ID'],
         'X-EBAY-API-DEV-NAME': ns['DEV_ID'], 'X-EBAY-API-CERT-NAME': ns['CERT_ID'],
         'X-EBAY-API-IAF-TOKEN': tok, 'Content-Type': 'text/xml'}
    with urlopen(Request('https://api.ebay.com/ws/api.dll', data=body.encode(), headers=h), timeout=120) as r:
        return r.read().decode()


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text else d


res = {}
for s in ns['STORES']:
    nm = s['name']
    out = {'offers': [], 'err': []}
    try:
        raw = call(s['token'], 'GetBestOffers', '<BestOfferStatus>Active</BestOfferStatus><DetailLevel>ReturnAll</DetailLevel>')
        r = ET.fromstring(raw)
        out['ack'] = T(r, 'Ack')
        out['err'] += [T(x, 'LongMessage') for x in r.findall('.//{%s}Errors' % NS)][:3]
        for arr in r.findall('.//{%s}BestOfferArray' % NS):
            for bo in arr.findall('{%s}BestOffer' % NS):
                out['offers'].append({
                    'id': T(bo, 'BestOfferID'),
                    'price': T(bo.find('{%s}Price' % NS), 'Price') or T(bo, 'Price'),
                    'qty': T(bo, 'Quantity'),
                    'status': T(bo, 'Status'),
                    'expire': T(bo, 'ExpirationTime'),
                    'buyer': T(bo.find('{%s}Buyer' % NS), 'UserID') if bo.find('{%s}Buyer' % NS) is not None else None,
                    'msg': (T(bo, 'BuyerMessage') or '')[:120],
                    'item': T(bo, 'ItemID'),
                })
        # also grab raw for structure debugging
        out['raw_head'] = raw[:1500]
    except Exception as e:
        out['err'].append(str(e)[:200])
    res[nm] = out
    print(nm, 'active offers:', len(out['offers']), 'ack', out.get('ack'), out['err'][:1], flush=True)

json.dump(res, open(os.path.join(OUT, 'offers.json'), 'w'), indent=1)
print('DONE')
