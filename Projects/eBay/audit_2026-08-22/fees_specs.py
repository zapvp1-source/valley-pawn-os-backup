import os, json, random, time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
NS = 'urn:ebay:apis:eBLBaseComponents'


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


Q = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quality_pull2.json')))
OUT = os.path.dirname(os.path.abspath(__file__))
res = {'fees': {}, 'specs': {}, 'store': {}}

for s in ns['STORES']:
    nm = s['name']
    tok = s['token']
    try:
        raw = call(tok, 'GetAccount',
                   '<AccountHistorySelection>LastInvoice</AccountHistorySelection>'
                   '<DetailLevel>ReturnAll</DetailLevel>'
                   '<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>1</PageNumber></Pagination>')
        r = ET.fromstring(raw)
        ents = []
        for e in r.findall('.//{%s}AccountEntry' % NS):
            ents.append({'type': T(e, 'AccountDetailsEntryType'), 'desc': T(e, 'Description'),
                         'amt': T(e, 'GrossDetailAmount'), 'date': T(e, 'Date'), 'item': T(e, 'ItemID')})
        res['fees'][nm] = {'ack': T(r, 'Ack'), 'n': len(ents), 'entries': ents[:400],
                           'err': [T(x, 'LongMessage') for x in r.findall('.//{%s}Errors' % NS)][:3],
                           'balance': T(r, 'CurrentBalance')}
    except Exception as e:
        res['fees'][nm] = {'err': str(e)[:200]}

    try:
        raw = call(tok, 'GetStore', '<DetailLevel>ReturnAll</DetailLevel>')
        r = ET.fromstring(raw)
        stn = r.find('.//{%s}Store' % NS)
        res['store'][nm] = {'ack': T(r, 'Ack'), 'name': T(stn, 'Name'),
                            'level': T(stn, 'SubscriptionLevel'),
                            'err': [T(x, 'LongMessage') for x in r.findall('.//{%s}Errors' % NS)][:2]}
    except Exception as e:
        res['store'][nm] = {'err': str(e)[:200]}

    ids = list(Q[nm].keys())
    random.seed(7)
    random.shuffle(ids)
    ids = ids[:20]
    sam = []
    for iid in ids:
        try:
            raw = call(tok, 'GetItem',
                       '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>'
                       '<IncludeItemSpecifics>true</IncludeItemSpecifics>' % iid)
            r = ET.fromstring(raw)
            it = r.find('.//{%s}Item' % NS)
            isp = it.find('{%s}ItemSpecifics' % NS)
            nvs = isp.findall('{%s}NameValueList' % NS) if isp is not None else []
            sam.append({'id': iid, 'title': T(it, 'Title'), 'n': len(nvs),
                        'names': [T(nv, 'Name') for nv in nvs],
                        'cat': T(it.find('{%s}PrimaryCategory' % NS), 'CategoryName'),
                        'dispatch': T(it, 'DispatchTimeMax'),
                        'hits': T(it, 'HitCount'), 'watch': T(it, 'WatchCount'),
                        'price': T(it.find('{%s}SellingStatus' % NS), 'CurrentPrice')})
        except Exception as e:
            sam.append({'id': iid, 'err': str(e)[:120]})
        time.sleep(0.15)
    res['specs'][nm] = sam
    print(nm, 'done', flush=True)

json.dump(res, open(os.path.join(OUT, 'fees_specs.json'), 'w'), indent=1)
print('DONE')
