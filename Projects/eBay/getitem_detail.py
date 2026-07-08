#!/usr/bin/env python3
import os,sys,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen
ns={}; exec(compile(open(os.path.expanduser('~/ebay_weekly_rankings.py')).read(),'x','exec'),ns)
store=sys.argv[2]; iid=sys.argv[1]
tok=[s['token'] for s in ns['STORES'] if s['name']==store][0]
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
NS="urn:ebay:apis:eBLBaseComponents"
b=f'<?xml version="1.0"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><DetailLevel>ReturnAll</DetailLevel></GetItemRequest>'
h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"GetItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
r=ET.fromstring(urlopen(Request("https://api.ebay.com/ws/api.dll",data=b.encode(),headers=h),timeout=60).read().decode())
g=lambda p: r.findtext(f".//{{{NS}}}"+p)
print("ListingStatus:",g("ListingStatus"))
print("Title:",g("Title"))
print("SKU/CustomLabel:",g("SKU"))
print("Price:",g("CurrentPrice"))
print("Qty:",g("Quantity"),"QtySold:",g("QuantitySold"))
print("Available:", (int(g("Quantity") or 0)-int(g("QuantitySold") or 0)))
print("EndTime:",g("EndTime"))
print("URL:",g("ViewItemURL"))
