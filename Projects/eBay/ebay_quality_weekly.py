import os
#!/usr/bin/env python3
"""Valley Pawn — weekly NEW-listing quality check (all 5 stores).
For listings created in the last 7 days, flags: title issues (short / intake code / ALL-CAPS),
eBay category mismatch (Taxonomy API), and too-few-photos (<3). Posts to Slack #ebay-performance.
Runs Monday 10:30 AM via LaunchAgent. Read-only (no changes)."""
import base64,json,os,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from datetime import datetime,timedelta,timezone
from urllib.error import HTTPError
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, CERT_ID as CERT, DEV_ID as DEV  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
HOOK = open(os.path.expanduser("~/.vp_secrets/slack_webhook_ebay_markdown")).read().strip()  # never hardcode -- see ~/.vp_secrets/slack_webhook_ebay_markdown
CODE=re.compile(r"\((?:[A-Za-z]{1,4})?\d{3,}[A-Za-z]?\)")
def stores():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return ns["STORES"]
    raise SystemExit("no tokens")
def app_token():
    auth=base64.b64encode(f"{APP}:{CERT}".encode()).decode()
    d=urllib.parse.urlencode({"grant_type":"client_credentials","scope":"https://api.ebay.com/oauth/api_scope"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.ebay.com/identity/v1/oauth2/token",data=d,headers={"Authorization":f"Basic {auth}","Content-Type":"application/x-www-form-urlencoded"}),timeout=30))["access_token"]
def call(tok,name,inner):
    body=(f'<?xml version="1.0" encoding="utf-8"?><{name}Request xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>{inner}</{name}Request>').encode()
    h={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":name,"X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"}
    return ET.fromstring(urlopen_(Request_(URL,data=body,headers=h)))
from urllib.request import Request as Request_, urlopen as _uo
def urlopen_(req): return _uo(req,timeout=60).read().decode()
def pdt(s):
    for f in ("%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(s,f).replace(tzinfo=timezone.utc)
        except: pass
    return None
def suggest(app_tok,q):
    url="https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions?"+urllib.parse.urlencode({"q":q[:300]})
    try:
        j=json.load(_uo(Request_(url,headers={"Authorization":f"Bearer {app_tok}"}),timeout=20))
        return j["categorySuggestions"][0]["category"]["categoryId"], j["categorySuggestions"][0]["category"]["categoryName"]
    except: return None,None
def photo_count(tok,iid):
    try:
        r=ET.fromstring(urlopen_(Request_(URL,data=(f'<?xml version="1.0" encoding="utf-8"?><GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><ItemID>{iid}</ItemID><DetailLevel>ItemReturnAttributes</DetailLevel></GetItemRequest>').encode(),
            headers={"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":"GetItem","X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,"X-EBAY-API-IAF-TOKEN":tok,"Content-Type":"text/xml"})))
        return len(r.findall(f".//{{{NS}}}PictureDetails/{{{NS}}}PictureURL"))
    except: return None
def title_flags(t):
    f=[]
    if len(t)<45: f.append("short")
    if CODE.search(t): f.append("intake-code")
    letters=[c for c in t if c.isalpha()]
    if letters and all(c.isupper() for c in letters): f.append("ALL-CAPS")
    return f
def main():
    app_tok=app_token(); now=datetime.now(timezone.utc); cut=now-timedelta(days=7)
    lines=[]; tot_new=tot_flag=0
    for s in stores():
        tok=s["token"]; new=[]
        r=call(tok,"GetMyeBaySelling","<ActiveList><Include>true</Include><Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>1</PageNumber></Pagination></ActiveList>")
        for it in r.findall(f".//{{{NS}}}ActiveList/{{{NS}}}ItemArray/{{{NS}}}Item"):
            st=pdt(it.findtext(f".//{{{NS}}}ListingDetails/{{{NS}}}StartTime") or "")
            if not st or st<cut: continue
            new.append({"id":it.findtext(f"{{{NS}}}ItemID"),"title":it.findtext(f"{{{NS}}}Title") or "",
                        "cat":it.findtext(f".//{{{NS}}}PrimaryCategory/{{{NS}}}CategoryID")})
        flagged=[]
        for it in new:
            issues=title_flags(it["title"])
            sid,sname=suggest(app_tok,it["title"])
            if sid and it["cat"] and sid!=it["cat"]: issues.append(f"category?→{sname}")
            pc=photo_count(tok,it["id"])
            if pc is not None and pc<3: issues.append(f"{pc}-photo")
            if issues: flagged.append((it["title"][:44],issues))
        tot_new+=len(new); tot_flag+=len(flagged)
        head=f"*{s['name']}* — {len(new)} new, {len(flagged)} flagged"
        lines.append(head)
        for t,iss in flagged[:6]: lines.append(f"   • {t} — {', '.join(iss)}")
    msg=(f"🔎 *eBay New-Listing Quality Check* — last 7 days\n"
         f"{tot_new} new listings, *{tot_flag}* with issues (title / category / photos)\n\n"+"\n".join(lines)+
         "\n\n_Fix flagged items: full 80-char keyword titles, no intake codes, proper case, right category, 3+ clear photos (whole-item primary)._")
    _uo(Request_(HOOK,data=json.dumps({"text":msg}).encode(),headers={"Content-Type":"application/json"}),timeout=15)
    print("posted;",tot_new,"new",tot_flag,"flagged")
if __name__=="__main__": main()
