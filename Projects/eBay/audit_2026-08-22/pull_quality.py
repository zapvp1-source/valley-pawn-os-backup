import json, os, time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
SRC=os.path.expanduser('~/ebay_weekly_rankings.py'); ns={}
exec(compile(open(SRC).read(),SRC,'exec'), ns)
STORES=ns['STORES']; APP_ID=ns['APP_ID']; DEV_ID=ns['DEV_ID']; CERT_ID=ns['CERT_ID']
NS='urn:ebay:apis:eBLBaseComponents'; URL='https://api.ebay.com/ws/api.dll'
def q(n): return '{%s}%s'%(NS,n)
def call(tok,name,inner):
    body=('<?xml version=\"1.0\" encoding=\"utf-8\"?><%sRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">'
          '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>')%(name,tok,inner,name)
    h={'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967','X-EBAY-API-CALL-NAME':name,
       'X-EBAY-API-APP-NAME':APP_ID,'X-EBAY-API-DEV-NAME':DEV_ID,'X-EBAY-API-CERT-NAME':CERT_ID,
       'X-EBAY-API-IAF-TOKEN':tok,'Content-Type':'text/xml'}
    for i in range(3):
        try:
            with urlopen(Request(URL,data=body.encode(),headers=h),timeout=180) as r:
                return ET.fromstring(r.read().decode())
        except Exception as e:
            if i==2: raise
            time.sleep(4)
def txt(el,tag,d=None):
    if el is None: return d
    x=el.find(q(tag)); return x.text if x is not None and x.text else d
now=datetime.now(timezone.utc)
out={}
for s in STORES:
    items={}; page=1
    while True:
        inner=('<EndTimeFrom>%s</EndTimeFrom><EndTimeTo>%s</EndTimeTo>'
               '<GranularityLevel>Fine</GranularityLevel><IncludeItemSpecifics>true</IncludeItemSpecifics><IncludeItemSpecifics>true</IncludeItemSpecifics>'
               '<Pagination><EntriesPerPage>50</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>')%(
               now.strftime('%Y-%m-%dT%H:%M:%S.000Z'),(now+timedelta(days=120)).strftime('%Y-%m-%dT%H:%M:%S.000Z'),page)
        r=call(s['token'],'GetSellerList',inner)
        ack=txt(r,'Ack')
        if ack=='Failure':
            print(s['name'],'FAIL',ET.tostring(r,encoding='unicode')[:500]); break
        got=r.findall('.//'+q('Item'))
        for it in got:
            iid=txt(it,'ItemID')
            if not iid: continue
            pd=it.find(q('PictureDetails')); rp=it.find(q('ReturnPolicy'))
            ss=it.find(q('SellingStatus')); ld=it.find(q('ListingDetails'))
            sd=it.find(q('ShippingDetails'))
            svc=[]
            if sd is not None:
                for so in sd.findall(q('ShippingServiceOptions')):
                    svc.append({'svc':txt(so,'ShippingService'),'cost':txt(so,'ShippingServiceCost')})
            items[iid]={
              'title':txt(it,'Title',''),'price':txt(ss,'CurrentPrice') or txt(it,'StartPrice'),
              'pics':len(pd.findall(q('PictureURL'))) if pd is not None else 0,
              'specifics':len(it.findall('.//'+q('NameValueList'))),
              'spec_names':[txt(nv,'Name') for nv in it.findall('.//'+q('NameValueList'))][:40],
              'best_offer':txt(it.find(q('BestOfferDetails')),'BestOfferEnabled') if it.find(q('BestOfferDetails')) is not None else txt(it,'BestOfferEnabled'),
              'returns':txt(rp,'ReturnsAcceptedOption'),'returns_within':txt(rp,'ReturnsWithinOption'),
              'ret_ship_by':txt(rp,'ShippingCostPaidByOption'),
              'dispatch':txt(it,'DispatchTimeMax'),
              'cat':txt(it.find(q('PrimaryCategory')),'CategoryName') if it.find(q('PrimaryCategory')) is not None else None,
              'cat_id':txt(it.find(q('PrimaryCategory')),'CategoryID') if it.find(q('PrimaryCategory')) is not None else None,
              'cond':txt(it,'ConditionDisplayName'),
              'start':txt(ld,'StartTime'),'hits':txt(it,'HitCount'),'watch':txt(it,'WatchCount'),
              'qty':txt(it,'Quantity'),'qty_sold':txt(ss,'QuantitySold'),
              'ship':svc,'desc_len':len(txt(it,'Description','') or ''),
              'sku':txt(it,'SKU'),'site':txt(it,'Site'),
              'store_cat':txt(it.find(q('Storefront')),'StoreCategoryID') if it.find(q('Storefront')) is not None else None,
            }
        pr=r.find('.//'+q('PaginationResult')); tot=int(txt(pr,'TotalNumberOfPages','1') or 1)
        print(s['name'],'page',page,'of',tot,'items',len(items),flush=True)
        if page>=tot: break
        page+=1
    out[s['name']]=items
json.dump(out,open('quality_pull2.json','w'),indent=1)
print('DONE')
