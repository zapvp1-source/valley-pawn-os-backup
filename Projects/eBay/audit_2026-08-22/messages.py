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


now = datetime.now(timezone.utc)
res = {}
for s in ns['STORES']:
    nm = s['name']
    rec = {'messages': [], 'feedback': {}, 'err': []}
    try:
        raw = call(s['token'], 'GetMyMessages',
                   '<StartTime>%s</StartTime><EndTime>%s</EndTime><DetailLevel>ReturnHeaders</DetailLevel>'
                   % ((now - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                      now.strftime('%Y-%m-%dT%H:%M:%S.000Z')))
        r = ET.fromstring(raw)
        for m in r.findall('.//{%s}Message' % NS):
            rec['messages'].append({
                'sender': T(m, 'Sender'), 'subject': T(m, 'Subject'),
                'read': T(m, 'Read'), 'replied': T(m, 'Replied'),
                'responseEnabled': T(m, 'ResponseEnabled'),
                'receive': T(m, 'ReceiveDate'), 'item': T(m, 'ItemID'),
                'flagged': T(m, 'Flagged'), 'folder': T(m.find('{%s}Folder' % NS), 'FolderID'),
            })
        rec['ack_msg'] = T(r, 'Ack')
        rec['err'] += [T(x, 'LongMessage') for x in r.findall('.//{%s}Errors' % NS)][:2]
    except Exception as e:
        rec['err'].append('msg:' + str(e)[:150])

    try:
        raw = call(s['token'], 'GetFeedback',
                   '<DetailLevel>ReturnAll</DetailLevel>'
                   '<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>1</PageNumber></Pagination>')
        r = ET.fromstring(raw)
        sm = r.find('.//{%s}FeedbackSummary' % NS)
        rec['feedback'] = {
            'score': T(r, 'FeedbackScore'),
            'positive_pct': T(r, 'FeedbackDetailItemTotal'),
            'neg30': T(sm, 'NegativeFeedbackPeriodicSummary') if sm is not None else None,
            'summary_xml': ET.tostring(sm, encoding='unicode')[:4000] if sm is not None else None,
        }
        det = []
        for f in r.findall('.//{%s}FeedbackDetail' % NS):
            if T(f, 'CommentType') in ('Negative', 'Neutral'):
                det.append({'type': T(f, 'CommentType'), 'text': T(f, 'CommentText'),
                            'date': T(f, 'CommentTime'), 'item': T(f, 'ItemID'),
                            'title': T(f, 'ItemTitle'), 'reply': T(f, 'Followup'),
                            'response': T(f, 'Response')})
        rec['neg_neutral'] = det
    except Exception as e:
        rec['err'].append('fb:' + str(e)[:150])
    res[nm] = rec
    print(nm, 'msgs', len(rec['messages']), 'negneu', len(rec.get('neg_neutral', [])), flush=True)

json.dump(res, open(os.path.join(OUT, 'messages.json'), 'w'), indent=1)
print('DONE')
