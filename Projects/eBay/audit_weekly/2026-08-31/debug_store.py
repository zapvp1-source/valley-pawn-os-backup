#!/usr/bin/env python3
import os, xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
STORES = ns['STORES']; APP_ID = ns['APP_ID']; DEV_ID = ns['DEV_ID']; CERT_ID = ns['CERT_ID']
URL = 'https://api.ebay.com/ws/api.dll'

s = STORES[0]
body = ('<?xml version="1.0" encoding="utf-8"?>'
        '<GetStoreRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
        '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>'
        '</GetStoreRequest>') % s['token']
h = {'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967',
     'X-EBAY-API-CALL-NAME':'GetStore','X-EBAY-API-APP-NAME':APP_ID,
     'X-EBAY-API-DEV-NAME':DEV_ID,'X-EBAY-API-CERT-NAME':CERT_ID,
     'X-EBAY-API-IAF-TOKEN':s['token'],'Content-Type':'text/xml'}
with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=60) as r:
    raw = r.read().decode('utf-8')
print(raw[:3000])
