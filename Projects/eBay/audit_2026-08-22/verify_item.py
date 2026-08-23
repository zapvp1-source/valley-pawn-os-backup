import os,json,sys
import xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
SRC=os.path.expanduser('~/ebay_weekly_rankings.py'); ns={}
exec(compile(open(SRC).read(),SRC,'exec'),ns)
NS='urn:ebay:apis:eBLBaseComponents'
Q=json.load(open('quality_pull.json'))
def call(tok,name,inner):
    body=('<?xml version=\"1.0\" encoding=\"utf-8\"?><%sRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">'
          '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>')%(name,tok,inner,name)
    h={'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967','X-EBAY-API-CALL-NAME':name,
       'X-EBAY-API-APP-NAME':ns['APP_ID'],'X-EBAY-API-DEV-NAME':ns['DEV_ID'],'X-EBAY-API-CERT-NAME':ns['CERT_ID'],
       'X-EBAY-API-IAF-TOKEN':tok,'Content-Type':'text/xml'}
    with urlopen(Request('https://api.ebay.com/ws/api.dll',data=body.encode(),headers=h),timeout=90) as r:
        return r.read().decode()
for st in ['Culpeper','Roanoke','Waynesboro']:
    tok=[x for x in ns['STORES'] if x['name']==st][0]['token']
    iid=list(Q[st].keys())[0]
    raw=call(tok,'GetItem','<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel><IncludeItemSpecifics>true</IncludeItemSpecifics>'%iid)
    r=ET.fromstring(raw)
    it=r.find('.//{%s}Item'%NS)
    isp=it.find('{%s}ItemSpecifics'%NS)
    nvs=isp.findall('{%s}NameValueList'%NS) if isp is not None else []
    desc=it.find('{%s}Description'%NS)
    print('==',st,iid,'|',(it.find('{%s}Title'%NS).text or '')[:60])
    print('   ItemSpecifics count:',len(nvs))
    for nv in nvs[:8]:
        print('     -',nv.find('{%s}Name'%NS).text,'=',(nv.find('{%s}Value'%NS).text or '')[:40])
    print('   desc len:',len(desc.text) if desc is not None and desc.text else 0)
    print('   dispatch:',it.find('{%s}DispatchTimeMax'%NS).text if it.find('{%s}DispatchTimeMax'%NS) is not None else None)
    rp=it.find('{%s}ReturnPolicy'%NS)
    print('   returns:',ET.tostring(rp,encoding='unicode')[:220] if rp is not None else None)
