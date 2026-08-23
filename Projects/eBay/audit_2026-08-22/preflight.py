import os, json
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
WATCH = ('ReviseFixedPriceItem', 'ReviseItem', 'GetItem', 'RespondToFeedback', 'EndFixedPriceItem')
out = {}
for s in ns['STORES']:
    nm = s['name']
    rec = {'limits': {}, 'profiles': {}, 'optin': None}
    try:
        raw = call(s['token'], 'GetAPIAccessRules', '')
        r = ET.fromstring(raw)
        for ar in r.findall('.//{%s}APIAccessRule' % NS):
            cn = T(ar, 'CallName')
            if cn in WATCH:
                rec['limits'][cn] = {'dailyLimit': T(ar, 'DailyHardLimit'),
                                     'dailyUsage': T(ar, 'DailyUsage'),
                                     'dailySoft': T(ar, 'DailySoftLimit')}
        rec['limits']['_ack'] = T(r, 'Ack')
    except Exception as e:
        rec['limits']['err'] = str(e)[:150]

    # Business policies opt-in?
    try:
        raw = call(s['token'], 'GetUserPreferences',
                   '<ShowSellerProfilePreferences>true</ShowSellerProfilePreferences>')
        r = ET.fromstring(raw)
        sp = r.find('.//{%s}SellerProfilePreferences' % NS)
        rec['optin'] = T(sp, 'SupportedSellerProfiles') if sp is not None else None
        rec['optin_flag'] = T(sp, 'SellerProfileOptedIn') if sp is not None else None
        rec['prefs_xml'] = ET.tostring(sp, encoding='unicode')[:900] if sp is not None else None
    except Exception as e:
        rec['optin'] = 'err:' + str(e)[:120]

    # Does a live item carry SellerProfiles?
    iid = list(Q[nm].keys())[0]
    try:
        raw = call(s['token'], 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
        r = ET.fromstring(raw)
        it = r.find('.//{%s}Item' % NS)
        prof = it.find('{%s}SellerProfiles' % NS)
        rec['item_profiles'] = ET.tostring(prof, encoding='unicode')[:700] if prof is not None else 'NONE (inline policies)'
        rec['sample_item'] = iid
    except Exception as e:
        rec['item_profiles'] = 'err:' + str(e)[:120]
    out[nm] = rec
    print('==', nm)
    print('   limits:', json.dumps(rec['limits']))
    print('   optedIn:', rec.get('optin_flag'), '|', str(rec.get('optin'))[:80])
    print('   item SellerProfiles:', str(rec['item_profiles'])[:400])

json.dump(out, open(os.path.join(D, 'preflight.json'), 'w'), indent=1)
print('DONE')
