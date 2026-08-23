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
    for i in range(3):
        try:
            with urlopen(Request('https://api.ebay.com/ws/api.dll', data=body.encode(), headers=h), timeout=120) as r:
                return r.read().decode()
        except Exception:
            if i == 2:
                raise
            time.sleep(3)


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text else d


now = datetime.now(timezone.utc)
res = {}
for s in ns['STORES']:
    nm = s['name']
    ents = []
    errs = []
    # chunk 90 days into 30-day slices
    for c in range(0, 90, 30):
        e = now - timedelta(days=c)
        b = now - timedelta(days=min(c + 30, 90))
        page = 1
        while True:
            inner = ('<AccountHistorySelection>BetweenSpecifiedDates</AccountHistorySelection>'
                     '<BeginDate>%s</BeginDate><EndDate>%s</EndDate>'
                     '<DetailLevel>ReturnAll</DetailLevel>'
                     '<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>'
                     ) % (b.strftime('%Y-%m-%dT%H:%M:%S.000Z'), e.strftime('%Y-%m-%dT%H:%M:%S.000Z'), page)
            raw = call(s['token'], 'GetAccount', inner)
            r = ET.fromstring(raw)
            if T(r, 'Ack') == 'Failure':
                errs.append([T(x, 'LongMessage') for x in r.findall('.//{%s}Errors' % NS)][:2])
                break
            for en in r.findall('.//{%s}AccountEntry' % NS):
                ents.append({'type': T(en, 'AccountDetailsEntryType'), 'desc': T(en, 'Description'),
                             'amt': T(en, 'GrossDetailAmount'), 'date': T(en, 'Date'), 'item': T(en, 'ItemID')})
            pr = r.find('.//{%s}PaginationResult' % NS)
            tot = int(T(pr, 'TotalNumberOfPages', '1') or 1)
            if page >= tot:
                break
            page += 1
            time.sleep(0.2)
    res[nm] = {'entries': ents, 'errs': errs}
    print(nm, len(ents), 'entries', flush=True)

json.dump(res, open(os.path.join(OUT, 'fees_90d.json'), 'w'), indent=1)
print('DONE')
