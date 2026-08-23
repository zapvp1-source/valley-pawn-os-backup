#!/usr/bin/env python3
"""
The one title from the incident that is factually risky.

Waynesboro 800321499390, $649.94. The accidental run retitled it
  "SONY ZV-E10 with extras"
   -> "Sony ZV-E10 Mirrorless Vlogging Camera Body with Extra Accessories - Used"

Its own item specifics carry MPN ILCZV-E10L/W. In Sony's part numbering the trailing "L" denotes
the LENS KIT (body + 16-50mm); the body-only SKU is ILCZV-E10. So the new title asserts
"Camera Body" on an item its own specifics say is a lens kit. Either way round that is a
not-as-described claim waiting to happen on a $650 item - the exact failure behind the existing
Harrisonburg neutral feedback ("lack of charger when the description claimed").

Fix: remove the body/kit assertion entirely and carry the MPN instead, which is verifiable.
Reversible - prior title stored below and in ~/ebay_incident_fix_state.json.
"""
import json, os
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'

STORE, ITEM = 'Waynesboro', '800321499390'
NEW = 'Sony ZV-E10 Mirrorless Vlogging Camera ILCZV-E10L/W White w/ Extras - Used'
STATE = os.path.join(HOME, 'ebay_incident_fix_state.json')


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


print('new title is %d chars' % len(NEW))
assert len(NEW) <= 80

r = call(TOK[STORE], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % ITEM)
it = r.find('.//{%s}Item' % NS)
before = T(it, 'Title')
status = T(it.find('{%s}SellingStatus' % NS), 'ListingStatus')
print('current :', before)
print('status  :', status)
if status != 'Active':
    print('not active - aborting')
    raise SystemExit(0)

st = json.load(open(STATE)) if os.path.exists(STATE) else {}
st[ITEM] = {'store': STORE, 'before': before, 'after': NEW,
            'reason': 'incident 2026-08-22: title asserted Camera Body but MPN ILCZV-E10L/W is the lens kit'}
json.dump(st, open(STATE, 'w'), indent=1)

r = call(TOK[STORE], 'ReviseFixedPriceItem',
         '<Item><ItemID>%s</ItemID><Title><![CDATA[%s]]></Title></Item>' % (ITEM, NEW))
ack = T(r, 'Ack')
errs = [T(e, 'LongMessage') for e in r.findall('.//{%s}Errors' % NS)]
print('ack     :', ack, errs[:2])

# verify live
r = call(TOK[STORE], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % ITEM)
live = T(r.find('.//{%s}Item' % NS), 'Title')
print('live now:', live)
print('VERIFIED :', live == NEW)
