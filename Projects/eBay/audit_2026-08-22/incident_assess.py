#!/usr/bin/env python3
"""
INCIDENT ASSESSMENT 2026-08-22 - what did the accidental exec() actually change on eBay?
Ground truth only: reads each item's LIVE title via GetItem and compares to the state file's
title_before / title_after. No metadata inference (Rule 12).
"""
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


rows = []
for path in ['ebay_weekly_qualityfix_state.json']:
    p = os.path.join(HOME, path)
    if not os.path.exists(p):
        continue
    st = json.load(open(p))
    for iid, rec in st.items():
        store = rec.get('store')
        if store not in TOK:
            continue
        try:
            r = call(TOK[store], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
            it = r.find('.//{%s}Item' % NS)
            live_title = T(it, 'Title')
            status = T(it.find('{%s}SellingStatus' % NS), 'ListingStatus') if it.find('{%s}SellingStatus' % NS) is not None else None
            live_cat = T(it.find('{%s}PrimaryCategory' % NS), 'CategoryID') if it.find('{%s}PrimaryCategory' % NS) is not None else None
        except Exception as e:
            rows.append({'item': iid, 'store': store, 'err': str(e)[:100]})
            continue
        before = rec.get('title_before')
        after = rec.get('title_after')
        if live_title == after and before != after:
            verdict = 'CHANGED-BY-INCIDENT'
        elif live_title == before:
            verdict = 'unchanged'
        else:
            verdict = 'other'
        rows.append({'item': iid, 'store': store, 'status': status, 'verdict': verdict,
                     'before': before, 'after': after, 'live': live_title,
                     'cat_before': rec.get('cat_before'), 'cat_after': rec.get('cat_after'),
                     'live_cat': live_cat})
        time.sleep(0.25)

json.dump(rows, open(os.path.join(D, 'incident_assess.json'), 'w'), indent=1)
ch = [r for r in rows if r.get('verdict') == 'CHANGED-BY-INCIDENT']
print('checked %d items' % len(rows))
print('ACTUALLY CHANGED ON EBAY: %d' % len(ch))
for r in ch:
    print('\n  %s  %s  [%s]' % (r['store'], r['item'], r['status']))
    print('    was : %s' % r['before'])
    print('    now : %s' % r['live'])
    if r.get('cat_before') and r.get('cat_before') != r.get('live_cat'):
        print('    cat : %s -> %s' % (r['cat_before'], r['live_cat']))
print('\nunchanged: %d  other: %d  errors: %d' % (
    sum(1 for r in rows if r.get('verdict') == 'unchanged'),
    sum(1 for r in rows if r.get('verdict') == 'other'),
    sum(1 for r in rows if 'err' in r)))
for r in rows:
    if r.get('verdict') == 'other':
        print('  OTHER %s %s\n     before: %s\n     live  : %s' % (r['store'], r['item'], r['before'], r['live']))
