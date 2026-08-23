#!/usr/bin/env python3
"""Check the 6 still-ACTIVE listings whose titles were changed by the incident, for factual
accuracy against their own description text. The risk being tested: a title that now asserts
something the listing does not support (e.g. 'Body' on a camera that shipped with a lens) is an
INAD magnet."""
import json, os, re, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'
D = os.path.dirname(os.path.abspath(__file__))

ACTIVE = [
    ('Culpeper', '398155091025'), ('Culpeper', '398165119962'),
    ('Waynesboro', '800303619445'), ('Waynesboro', '800303620695'),
    ('Waynesboro', '800321499390'), ('Harrisonburg', '800321800443'),
    ('Culpeper', '398147106908'), ('Lexington', '158076113078'),
]


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


out = []
for store, iid in ACTIVE:
    r = call(TOK[store], 'GetItem',
             '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel><IncludeItemSpecifics>true</IncludeItemSpecifics>' % iid)
    it = r.find('.//{%s}Item' % NS)
    if it is None:
        out.append({'item': iid, 'store': store, 'err': 'no item'})
        continue
    desc = T(it, 'Description', '') or ''
    txt = re.sub(r'<[^>]+>', ' ', desc)
    txt = re.sub(r'\s+', ' ', txt).strip()
    # the human-written part is usually before the boilerplate template
    isp = it.find('{%s}ItemSpecifics' % NS)
    specs = {}
    if isp is not None:
        for nv in isp.findall('{%s}NameValueList' % NS):
            specs[T(nv, 'Name')] = T(nv, 'Value')
    out.append({'store': store, 'item': iid, 'title': T(it, 'Title'),
                'status': T(it.find('{%s}SellingStatus' % NS), 'ListingStatus'),
                'price': T(it.find('{%s}SellingStatus' % NS), 'CurrentPrice'),
                'cond': T(it, 'ConditionDisplayName'),
                'specs': specs, 'desc_snip': txt[:900]})
    time.sleep(0.25)

json.dump(out, open(os.path.join(D, 'incident_verify_active.json'), 'w'), indent=1)
for o in out:
    print('\n==== %s %s [%s] $%s cond=%s' % (o.get('store'), o.get('item'), o.get('status'), o.get('price'), o.get('cond')))
    print('  TITLE: %s' % o.get('title'))
    print('  SPECS: %s' % json.dumps(o.get('specs', {}))[:300])
    print('  DESC : %s' % (o.get('desc_snip', '')[:600]))
