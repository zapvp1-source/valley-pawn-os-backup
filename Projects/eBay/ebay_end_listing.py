#!/usr/bin/env python3
"""End a single eBay fixed-price listing. Usage: ebay_end_listing.py <ItemID> <Store> [--apply]"""
import os,sys,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
iid=sys.argv[1]; store=sys.argv[2]; apply="--apply" in sys.argv
tok=[s['token'] for s in ns['STORES'] if s['name']==store][0]
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
NS="urn:ebay:apis:eBLBaseComponents"
if not apply:
    print("DRY RUN — would end",iid,store); sys.exit(0)
b=f'<?xml version="1.0"?><EndFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><EndingReason>NotAvailable</EndingReason></EndFixedPriceItemRequest>'
h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"EndFixedPriceItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
r=ET.fromstring(urlopen(Request("https://api.ebay.com/ws/api.dll",data=b.encode(),headers=h),timeout=60).read().decode())
ack=r.findtext(f"{{{NS}}}Ack")
print("Ack:",ack)
print("EndTime:",r.findtext(f".//{{{NS}}}EndTime"))
msg=r.findtext(f".//{{{NS}}}LongMessage") or r.findtext(f".//{{{NS}}}ShortMessage")
if msg: print("Msg:",msg)
