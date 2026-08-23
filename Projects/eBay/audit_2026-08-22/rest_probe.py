import json, os, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns={}; exec(compile(open(SRC).read(),SRC,'exec'), ns)
STORES=ns['STORES']
ENDPOINTS = [
 ('marketing_campaigns','https://api.ebay.com/sell/marketing/v1/ad_campaign?limit=10'),
 ('analytics_traffic','https://api.ebay.com/sell/analytics/v1/traffic_report?dimension=DAY&filter=marketplace_ids:%7BEBAY_US%7D&metric=LISTING_IMPRESSION_TOTAL,LISTING_VIEWS_TOTAL,SALES_CONVERSION_RATE'),
 ('seller_standards','https://api.ebay.com/sell/analytics/v1/seller_standards_profile'),
 ('finances_summary','https://api.ebay.com/sell/finances/v1/transaction_summary'),
]
out={}
for s in STORES:
    r={}
    for name,url in ENDPOINTS:
        try:
            req=Request(url, headers={'Authorization':'Bearer '+s['token'],'Content-Type':'application/json','X-EBAY-C-MARKETPLACE-ID':'EBAY_US'})
            with urlopen(req, timeout=45) as resp:
                r[name]=json.loads(resp.read().decode())
        except HTTPError as e:
            r[name]={'HTTP':e.code,'body':e.read().decode()[:400]}
        except Exception as e:
            r[name]={'err':str(e)[:200]}
    out[s['name']]=r
json.dump(out, open('rest_probe.json','w'), indent=1)
print(json.dumps({k:{kk:(vv if isinstance(vv,dict) and ('HTTP' in vv or 'err' in vv) else 'OK') for kk,vv in v.items()} for k,v in out.items()}, indent=1))
