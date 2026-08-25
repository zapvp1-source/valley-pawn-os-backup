import json, os
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
TOK = {s['name']: s['token'] for s in ns['STORES']}
NS = 'urn:ebay:apis:eBLBaseComponents'


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


for store in ('Harrisonburg', 'Lexington', 'Roanoke'):
    r = call(TOK[store], 'GetFeedback',
             '<DetailLevel>ReturnAll</DetailLevel>'
             '<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>1</PageNumber></Pagination>')
    print('==', store, 'ack', T(r, 'Ack'))
    for f in r.findall('.//{%s}FeedbackDetail' % NS):
        ct = T(f, 'CommentType')
        if ct in ('Negative', 'Neutral'):
            print('  FeedbackID:', T(f, 'FeedbackID'), '| CommentingUser:', T(f, 'CommentingUser'),
                  '| ItemID:', T(f, 'ItemID'), '| Type:', ct, '| Date:', T(f, 'CommentTime'),
                  '| Responded:', T(f, 'Response') is not None,
                  '| Text:', (T(f, 'CommentText') or '')[:60])
