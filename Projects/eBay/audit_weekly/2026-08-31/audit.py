#!/usr/bin/env python3
# Weekly eBay channel audit - READ ONLY. 2026-08-31
# Modeled on audit_weekly/2026-08-24/pull.py, extended per ebay-weekly-channel-audit SKILL.md spec.
# Only read calls used: GetMyeBaySelling, GetSellerTransactions, GetAccount, GetItem,
# GetMyMessages, GetFeedback, GetBestOffers. No revise/end/write calls anywhere in this file.
import json, os, sys, time, re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)  # loads STORES/APP_ID/DEV_ID/CERT_ID only; __name__ != '__main__' in this ns, main() never runs
STORES = ns['STORES']; APP_ID = ns['APP_ID']; DEV_ID = ns['DEV_ID']; CERT_ID = ns['CERT_ID']
NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
OUT = os.path.dirname(os.path.abspath(__file__))
now = datetime.now(timezone.utc)

MARKDOWN_STATE_PATH = os.path.expanduser('~/ebay_markdown_state.json')

def log(*a):
    print(*a, flush=True)

def call(token, name, inner, tries=3):
    body = ('<?xml version="1.0" encoding="utf-8"?>'
            '<%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>'
            '%s</%sRequest>') % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967',
         'X-EBAY-API-CALL-NAME':name,'X-EBAY-API-APP-NAME':APP_ID,
         'X-EBAY-API-DEV-NAME':DEV_ID,'X-EBAY-API-CERT-NAME':CERT_ID,
         'X-EBAY-API-IAF-TOKEN':token,'Content-Type':'text/xml'}
    last_err = None
    for i in range(tries):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=120) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception as e:
            last_err = e
            if i == tries-1: raise
            time.sleep(3)
    raise last_err

def T(el, tag, d=None):
    if el is None: return d
    x = el.find('{%s}%s' % (NS, tag))
    return x.text if x is not None and x.text is not None else d

def q(name): return '{%s}%s' % (NS, name)

def active_listings(store):
    items = []
    page = 1
    while True:
        inner = ('<ActiveList><Include>true</Include><Pagination>'
                 '<EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber>'
                 '</Pagination></ActiveList><DetailLevel>ReturnAll</DetailLevel>') % page
        r = call(store['token'], 'GetMyeBaySelling', inner)
        al = r.find(q('ActiveList'))
        if al is None: break
        got = al.findall(q('ItemArray') + '/' + q('Item')) or al.findall('.//' + q('Item'))
        items.extend(got)
        pr = al.find(q('PaginationResult'))
        tot = int(T(pr, 'TotalNumberOfPages', '1') or 1)
        if page >= tot: break
        page += 1
    return items

def aging_bucket(days):
    if days is None: return 'unknown'
    if days <= 30: return '0-30'
    if days <= 60: return '31-60'
    if days <= 90: return '61-90'
    if days <= 180: return '91-180'
    if days <= 365: return '181-365'
    return '365+'

def parse_item(it):
    def g(p, d=None):
        x = it.find(p)
        return x.text if x is not None and x.text is not None else d
    ld = it.find(q('ListingDetails')); sp = it.find(q('SellingStatus')); pd = it.find(q('PictureDetails'))
    start = T(ld, 'StartTime')
    days = None
    if start:
        try:
            st = datetime.strptime(start[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
            days = (now - st).days
        except Exception: pass
    price = None
    for p in [q('CurrentPrice'), q('ConvertedCurrentPrice')]:
        x = sp.find(p) if sp is not None else None
        if x is not None:
            try: price = float(x.text); break
            except Exception: pass
    if price is None:
        x = it.find(q('BuyItNowPrice'))
        try: price = float(x.text) if x is not None else None
        except Exception: price = None
    title = g(q('Title'), '') or ''
    pics = len(pd.findall(q('PictureURL'))) if pd is not None else 0
    bo = it.find(q('BestOfferDetails'))
    bo_en = (T(bo, 'BestOfferEnabled') or g(q('BestOfferEnabled')) or 'false')
    rp = it.find(q('ReturnPolicy'))
    return {
        'id': g(q('ItemID')), 'title': title, 'title_len': len(title), 'price': price,
        'qty': int(g(q('Quantity'), '1') or 1), 'days_live': days, 'start': start, 'pics': pics,
        'best_offer': bo_en.lower() == 'true', 'condition': g(q('ConditionDisplayName')),
        'dispatch_max': g(q('DispatchTimeMax')),
        'returns_accepted': T(rp, 'ReturnsAcceptedOption'), 'returns_within': T(rp, 'ReturnsWithinOption'),
        'shipping_cost_paid_by': T(rp, 'ShippingCostPaidByOption'),
        'specifics_count': len(it.findall('.//' + q('NameValueList'))), 'sku': g(q('SKU')),
        'aging_bucket': aging_bucket(days),
    }

def sold(store, days_back=90):
    out = []; end = now
    for chunk in range(0, days_back, 30):
        e = end - timedelta(days=chunk); s = end - timedelta(days=min(chunk+30, days_back))
        page = 1
        while True:
            inner = ('<ModTimeFrom>%s</ModTimeFrom><ModTimeTo>%s</ModTimeTo>'
                     '<IncludeContainingOrder>true</IncludeContainingOrder>'
                     '<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>'
                     '<DetailLevel>ReturnAll</DetailLevel>') % (
                     s.strftime('%Y-%m-%dT%H:%M:%S.000Z'), e.strftime('%Y-%m-%dT%H:%M:%S.000Z'), page)
            r = call(store['token'], 'GetSellerTransactions', inner)
            if T(r, 'Ack') == 'Failure': break
            for tx in r.findall('.//' + q('Transaction')):
                it = tx.find(q('Item')); amt = T(tx, 'TransactionPrice'); created = T(tx, 'CreatedDate')
                ld = it.find(q('ListingDetails')) if it is not None else None
                start = T(ld, 'StartTime') if ld is not None else None
                days_to_sell = None
                if start and created:
                    try:
                        st = datetime.strptime(start[:19], '%Y-%m-%dT%H:%M:%S')
                        ct = datetime.strptime(created[:19], '%Y-%m-%dT%H:%M:%S')
                        days_to_sell = (ct - st).days
                    except Exception: pass
                out.append({'item_id': T(it,'ItemID') if it is not None else None,
                    'price': float(amt) if amt else None, 'created': created,
                    'qty': int(T(tx,'QuantityPurchased','1') or 1), 'days_to_sell': days_to_sell})
            pr = r.find('.//' + q('PaginationResult'))
            tot = int(T(pr, 'TotalNumberOfPages', '1') or 1)
            if page >= tot: break
            page += 1
    seen=set(); ded=[]
    for o in out:
        k=(o['item_id'], o['created'])
        if k in seen: continue
        seen.add(k); ded.append(o)
    return ded

FEE_KEYWORDS = [
    ('promoted', 'promoted_listings'),
    ('ad fee', 'promoted_listings'),
    ('final value', 'final_value_fee'),
    ('fvf', 'final_value_fee'),
    ('insertion', 'insertion'),
    ('international', 'international'),
    ('return', 'return_shipping'),
    ('subscription', 'subscription'),
    ('store', 'subscription'),
]

def categorize_fee(type_str):
    t = (type_str or '').lower()
    for kw, cat in FEE_KEYWORDS:
        if kw in t:
            return cat
    return 'other'

def fees(store, days_back=90):
    ents=[]
    for c in range(0, days_back, 30):
        e = now - timedelta(days=c); b = now - timedelta(days=min(c+30, days_back))
        page=1
        while True:
            inner = ('<AccountHistorySelection>BetweenSpecifiedDates</AccountHistorySelection>'
                     '<BeginDate>%s</BeginDate><EndDate>%s</EndDate><DetailLevel>ReturnAll</DetailLevel>'
                     '<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>'
                     ) % (b.strftime('%Y-%m-%dT%H:%M:%S.000Z'), e.strftime('%Y-%m-%dT%H:%M:%S.000Z'), page)
            r = call(store['token'], 'GetAccount', inner)
            if T(r,'Ack') == 'Failure': break
            for en in r.findall('.//' + q('AccountEntry')):
                typ = T(en,'AccountDetailsEntryType')
                amt = T(en,'GrossDetailAmount')
                try: amt_f = abs(float(amt)) if amt else 0.0
                except Exception: amt_f = 0.0
                ents.append({'type': typ, 'amt': amt_f, 'category': categorize_fee(typ)})
            pr = r.find('.//' + q('PaginationResult'))
            tot = int(T(pr,'TotalNumberOfPages','1') or 1)
            if page >= tot: break
            page += 1
    return ents

def store_info(store):
    try:
        r = call(store['token'], 'GetStore', '')
        st = r.find(q('Store'))
        return {'subscription': T(st, 'Subscription') if st is not None else None}
    except Exception as e:
        return {'error': str(e)[:200]}

def classify_message(subject, folder):
    s = (subject or '').lower()
    if any(k in s for k in ['return', 'refund']):
        return 'return_refund'
    if any(k in s for k in ['case', 'dispute', 'inr', 'inad', 'item not']):
        return 'case_dispute'
    return 'other'

def messages_feedback(store):
    rec = {'messages': [], 'feedback': {}, 'err': []}
    try:
        r = call(store['token'], 'GetMyMessages',
                 '<StartTime>%s</StartTime><EndTime>%s</EndTime><DetailLevel>ReturnHeaders</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>1</PageNumber></Pagination>'
                 % ((now - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S.000Z'), now.strftime('%Y-%m-%dT%H:%M:%S.000Z')))
        for m in r.findall('.//' + q('Message')):
            subj = T(m,'Subject')
            read = T(m,'Read')
            rec['messages'].append({'read': read, 'subject': subj, 'category': classify_message(subj, None)})
        pr = r.find('.//' + q('PaginationResult'))
        tot = int(T(pr, 'TotalNumberOfPages', '1') or 1)
        # cap at 3 pages (600 messages) to bound runtime; note if truncated
        page = 2
        while page <= min(tot, 3):
            r2 = call(store['token'], 'GetMyMessages',
                 '<StartTime>%s</StartTime><EndTime>%s</EndTime><DetailLevel>ReturnHeaders</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>'
                 % ((now - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S.000Z'), now.strftime('%Y-%m-%dT%H:%M:%S.000Z'), page))
            for m in r2.findall('.//' + q('Message')):
                subj = T(m,'Subject'); read = T(m,'Read')
                rec['messages'].append({'read': read, 'subject': subj, 'category': classify_message(subj, None)})
            page += 1
        rec['messages_truncated'] = tot > 3
    except Exception as e:
        rec['err'].append('msg:'+str(e)[:200])
    try:
        r = call(store['token'], 'GetFeedback', '<DetailLevel>ReturnAll</DetailLevel><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>1</PageNumber></Pagination>')
        rec['feedback'] = {'score': T(r,'FeedbackScore'), 'positive_pct': T(r,'PositiveFeedbackPercent')}
        det=[]; all_recent=[]
        for f in r.findall('.//' + q('FeedbackDetail')):
            ctype = T(f,'CommentType'); ctime = T(f,'CommentTime')
            all_recent.append({'type': ctype, 'date': ctime})
            if ctype in ('Negative','Neutral'):
                det.append({'type':ctype,'text':T(f,'CommentText'),'date':ctime,'item':T(f,'ItemID'),'response':T(f,'Response')})
        rec['neg_neutral']=det
        # compute rolling pos% for 1/6/12 months from the pulled page (best-effort, capped sample)
        def pos_pct(days):
            cutoff = now - timedelta(days=days)
            window = []
            for c in all_recent:
                if not c['date']: continue
                try:
                    dt = datetime.strptime(c['date'][:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                if dt >= cutoff:
                    window.append(c['type'])
            if not window: return None
            pos = sum(1 for t in window if t == 'Positive')
            return round(100.0 * pos / len(window), 1)
        rec['feedback']['pos_pct_1mo'] = pos_pct(30)
        rec['feedback']['pos_pct_6mo'] = pos_pct(182)
        rec['feedback']['pos_pct_12mo'] = pos_pct(365)
    except Exception as e:
        rec['err'].append('fb:'+str(e)[:200])
    return rec

def offers(store):
    out={'offers':[],'err':[]}
    try:
        r = call(store['token'], 'GetBestOffers', '<BestOfferStatus>Active</BestOfferStatus><DetailLevel>ReturnAll</DetailLevel>')
        for arr in r.findall('.//' + q('BestOfferArray')):
            for bo in arr.findall(q('BestOffer')):
                exp = T(bo,'ExpirationTime')
                soon = False
                if exp:
                    try:
                        et = datetime.strptime(exp[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                        soon = (et - now) < timedelta(hours=48)
                    except Exception: pass
                out['offers'].append({'id':T(bo,'BestOfferID'),'status':T(bo,'Status'),'expire':exp,'item':T(bo,'ItemID'),'expiring_soon':soon})
    except Exception as e:
        out['err'].append(str(e)[:200])
    return out

def load_markdown_state():
    try:
        with open(MARKDOWN_STATE_PATH) as f:
            return json.load(f)
    except Exception as e:
        return {'error': str(e)[:200]}

result = {}
store_errors = {}
for s in STORES:
    name = s['name']
    log('== '+name)
    rec = {}
    try:
        items = active_listings(s)
        rec['active'] = [parse_item(i) for i in items]
    except Exception as e:
        rec['active']=[]; rec['active_error']=str(e)[:300]
        store_errors.setdefault(name, []).append('active_listings: '+str(e)[:200])
    log('  active', len(rec.get('active',[])))
    try:
        rec['sold90'] = sold(s, 90)
    except Exception as e:
        rec['sold90']=[]; rec['sold_error']=str(e)[:300]
        store_errors.setdefault(name, []).append('sold_transactions: '+str(e)[:200])
    log('  sold90', len(rec.get('sold90',[])))
    try:
        rec['fees90'] = fees(s, 90)
    except Exception as e:
        rec['fees90']=[]; rec['fees_error']=str(e)[:300]
        store_errors.setdefault(name, []).append('fees: '+str(e)[:200])
    log('  fees90', len(rec.get('fees90',[])))
    try:
        rec['store_info'] = store_info(s)
    except Exception as e:
        rec['store_info']={'error':str(e)[:200]}
    try:
        rec['msgfb'] = messages_feedback(s)
    except Exception as e:
        rec['msgfb']={'error':str(e)[:200]}
    try:
        rec['offers'] = offers(s)
    except Exception as e:
        rec['offers']={'error':str(e)[:200]}
    result[name] = rec
    log('  done', name)

result['_markdown_state'] = load_markdown_state()
result['_store_errors'] = store_errors
result['_pull_time_utc'] = now.isoformat()

with open(os.path.join(OUT,'raw_pull.json'),'w') as f:
    json.dump(result, f, indent=1)
log('DONE')
