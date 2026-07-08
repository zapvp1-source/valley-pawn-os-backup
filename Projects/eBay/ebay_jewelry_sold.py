#!/usr/bin/env python3
"""Trailing-12-month eBay SOLD analysis, all 5 stores, jewelry vs everything else.
Pulls GetOrders in 90-day windows (API cap), classifies each sold line item, and
reports count + gross merchandise value (item price x qty, excludes shipping/tax).
Writes ~/ebay_jewelry_sold.json and prints a summary."""
import os,json,re,time,xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
from urllib.request import Request,urlopen
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
for p in PATHS:
    if os.path.exists(p):
        ns={};exec(compile(open(p).read(),p,"exec"),ns);STORES=ns["STORES"];break

# jewelry classifier (precious-metal / fine jewelry), watches split out
KARAT=re.compile(r'\b(\d{1,2}\s?K|10K|14K|18K|22K|24K|925|585|750|Sterling|dwt)\b',re.I)
NOUN =re.compile(r'\b(ring|chain|bracelet|earring|earrings|necklace|pendant|charm|bangle|brooch|anklet|cuban|rope|herringbone|hoop|wedding\s?band)\b',re.I)
METAL=re.compile(r'\b(gold|silver|platinum|diamond)\b',re.I)
WATCH=re.compile(r'\bwatch\b',re.I)
def is_jewelry(t):
    if WATCH.search(t): return "watch"
    if KARAT.search(t): return "jewelry"
    if NOUN.search(t) and METAL.search(t): return "jewelry"
    return "other"

def call(tok,cfrom,cto,page):
    inner=(f"<CreateTimeFrom>{cfrom}</CreateTimeFrom><CreateTimeTo>{cto}</CreateTimeTo>"
           f"<OrderStatus>Completed</OrderStatus><OrderRole>Seller</OrderRole>"
           f"<Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>{page}</PageNumber></Pagination>")
    body=(f'<?xml version="1.0" encoding="utf-8"?><GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>{inner}</GetOrdersRequest>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"GetOrders","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen(Request(URL,data=body,headers=h),timeout=90).read().decode())

now=datetime.now(timezone.utc)
wins=[]
end=now
start=end-timedelta(days=89)
wins.append((start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),end.strftime("%Y-%m-%dT%H:%M:%S.000Z")))
DAYS=89

report={}
ITEMS=[]
seen=set()  # dedupe transaction ids across windows
for s in STORES:
    cat={"jewelry":[0,0.0],"watch":[0,0.0],"other":[0,0.0]}
    for cfrom,cto in wins:
        page=1
        while True:
            try: r=call(s["token"],cfrom,cto,page)
            except Exception as e: print(s["name"],"win err",e,flush=True);break
            if r.findtext(f"{{{NS}}}Ack","")=="Failure":
                print(s["name"],"FAIL",r.findtext(f".//{{{NS}}}ShortMessage"),flush=True);break
            for tr in r.findall(f".//{{{NS}}}Transaction"):
                tid=(tr.findtext(f".//{{{NS}}}TransactionID") or "")+"-"+(tr.findtext(f".//{{{NS}}}OrderLineItemID") or "")
                if tid in seen: continue
                seen.add(tid)
                title=tr.findtext(f".//{{{NS}}}Item/{{{NS}}}Title") or ""
                qty=int(tr.findtext(f".//{{{NS}}}QuantityPurchased") or "1")
                price=float(tr.findtext(f".//{{{NS}}}TransactionPrice") or "0")
                k=is_jewelry(title)
                cat[k][0]+=qty; cat[k][1]+=price*qty
                if k in ("jewelry","watch"):
                    ITEMS.append({"store":s["name"],"cat":k,"title":title,"price":price*qty})
            tp=r.findtext(f".//{{{NS}}}PaginationResult/{{{NS}}}TotalNumberOfPages")
            try: tp=int(tp)
            except: tp=page
            if page>=tp: break
            page+=1
            time.sleep(0.3)
    report[s["name"]]=cat
    print(f"{s['name']}: jewelry {cat['jewelry'][0]} / ${cat['jewelry'][1]:,.2f} | watches {cat['watch'][0]} / ${cat['watch'][1]:,.2f} | other {cat['other'][0]} / ${cat['other'][1]:,.2f}",flush=True)

json.dump(report,open(os.path.expanduser("~/ebay_jewelry_sold.json"),"w"),indent=2)
# totals
tj=sum(report[s]['jewelry'][0] for s in report); tjv=sum(report[s]['jewelry'][1] for s in report)
tw=sum(report[s]['watch'][0] for s in report); twv=sum(report[s]['watch'][1] for s in report)
to=sum(report[s]['other'][0] for s in report); tov=sum(report[s]['other'][1] for s in report)
tot=tj+tw+to; totv=tjv+twv+tov
print("="*60)
print(f"TOTAL 12-MO: {tot} items sold, ${totv:,.2f} gross")
print(f"  JEWELRY: {tj} items ({tj/tot*100:.1f}%), ${tjv:,.2f} ({tjv/totv*100:.1f}% of sales), avg ${tjv/tj:,.2f}" if tj else "  JEWELRY: 0")
print(f"  WATCHES: {tw} items, ${twv:,.2f}, avg ${twv/tw:,.2f}" if tw else "  WATCHES: 0")
print(f"  OTHER:   {to} items, ${tov:,.2f}")
f=365.0/DAYS
print("="*60)
print(f"ANNUALIZED (x{f:.2f} from {DAYS}-day sample):")
print(f"  JEWELRY: ~{tj*f:.0f} items/yr, ~${tjv*f:,.0f}/yr")
print(f"  WATCHES: ~{tw*f:.0f} items/yr, ~${twv*f:,.0f}/yr")
print(f"  ALL eBay: ~{tot*f:.0f} items/yr, ~${totv*f:,.0f}/yr")
json.dump(ITEMS,open(os.path.expanduser("~/ebay_jewelry_items.json"),"w"),indent=2)
print("="*60)
print("JEWELRY & WATCH LINE ITEMS BY STORE:")
for st in sorted(set(i["store"] for i in ITEMS)):
    rows=[i for i in ITEMS if i["store"]==st]
    print(f"\n-- {st} ({len(rows)} items, ${sum(r['price'] for r in rows):,.2f}) --")
    for r in sorted(rows,key=lambda x:-x["price"]):
        print(f"   [{r['cat']:7}] ${r['price']:>8,.2f}  {r['title'][:60]}")
