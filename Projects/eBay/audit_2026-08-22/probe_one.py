import os,time,sys
import xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
SRC=os.path.expanduser('~/ebay_weekly_rankings.py'); ns={}
exec(compile(open(SRC).read(),SRC,'exec'),ns)
S=[x for x in ns['STORES'] if x['name']=='Lexington'][0]
NS='urn:ebay:apis:eBLBaseComponents'
def call(name,inner,gran):
    body=('<?xml version=\"1.0\" encoding=\"utf-8\"?><%sRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">'
          '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>')%(name,S['token'],inner,name)
    h={'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967','X-EBAY-API-CALL-NAME':name,
       'X-EBAY-API-APP-NAME':ns['APP_ID'],'X-EBAY-API-DEV-NAME':ns['DEV_ID'],'X-EBAY-API-CERT-NAME':ns['CERT_ID'],
       'X-EBAY-API-IAF-TOKEN':S['token'],'Content-Type':'text/xml'}
    t=time.time()
    with urlopen(Request('https://api.ebay.com/ws/api.dll',data=body.encode(),headers=h),timeout=120) as r:
        raw=r.read().decode()
    print('elapsed',round(time.time()-t,1),'bytes',len(raw))
    return ET.fromstring(raw)
now=datetime.now(timezone.utc)
inner=('<EndTimeFrom>%s</EndTimeFrom><EndTimeTo>%s</EndTimeTo><GranularityLevel>Fine</GranularityLevel>'
       '<Pagination><EntriesPerPage>10</EntriesPerPage><PageNumber>1</PageNumber></Pagination>')%(
       now.strftime('%Y-%m-%dT%H:%M:%S.000Z'),(now+timedelta(days=120)).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
r=call('GetSellerList',inner,'Fine')
print('Ack',r.find('{%s}Ack'%NS).text if r.find('{%s}Ack'%NS) is not None else '?')
items=r.findall('.//{%s}Item'%NS)
print('items',len(items))
if items:
    it=items[0]
    print('title',it.find('{%s}Title'%NS).text)
    pd=it.find('{%s}PictureDetails'%NS)
    print('pics',len(pd.findall('{%s}PictureURL'%NS)) if pd is not None else 'NONE')
    print('specs',len(it.findall('.//{%s}NameValueList'%NS)))
    rp=it.find('{%s}ReturnPolicy'%NS)
    print('returnpolicy',ET.tostring(rp,encoding='unicode')[:300] if rp is not None else 'NONE')
    print('dispatch',it.find('{%s}DispatchTimeMax'%NS).text if it.find('{%s}DispatchTimeMax'%NS) is not None else 'NONE')
    bo=it.find('{%s}BestOfferDetails'%NS)
    print('bo',ET.tostring(bo,encoding='unicode')[:200] if bo is not None else 'NONE')
else:
    print(ET.tostring(r,encoding='unicode')[:1200])
