#!/usr/bin/env python3
"""Enhance eBay listing photos (gentle auto-levels/brightness/sharpen) and replace them live.
Pipeline per listing: download each pic -> enhance -> UploadSiteHostedPictures (EPS) -> collect new URLs
-> ReviseFixedPriceItem with new PictureDetails (same order). Reversible via original URLs.
State: ~/ebay_photo_enhance_state.json { ItemID: {store, original:[urls]} }
Usage:
  python3 ebay_photo_enhance.py <store> <photos.json> [--only ITEMID] [--apply] [--primary-only]
  python3 ebay_photo_enhance.py --revert [--only ITEMID] [--apply]

Quota-safety flags (all optional, apply only when writing with --apply):
  --primary-only     upload/replace ONLY the primary photo (~7x fewer upload calls). Recommended.
  --min-budget N     pre-flight gate: refuse to start if remaining daily budget for
                     UploadSiteHostedPictures or ReviseFixedPriceItem is below N (default 300).
  --max-calls N      hard safety cap: stop the run after N eBay write calls, save state, exit.
  --no-preflight     skip the pre-flight GetAPIAccessRules quota check.
  --skip-upscaled    with --force, still skip items already marked upscaled in state (clean resume
                     across days without redoing finished items; preserves original URLs for revert).
The run auto-STOPS (saving state) the moment eBay returns a usage-limit / 503 error instead of
hammering the endpoint. Already-processed items are skipped on rerun, so it resumes cleanly the
next day. eBay per-call daily limits reset at ~midnight US/Pacific.
"""
import os,sys,json,io,uuid,time,xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageEnhance,ImageStat
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.expanduser("~/.vp_secrets"))
from ebay_credentials import APP_ID as APP, DEV_ID as DEV, CERT_ID as CERT  # never hardcode these -- see ~/.vp_secrets/ebay_credentials.py
PATHS=[os.path.expanduser("~/ebay_weekly_rankings.py"),"/sessions/fervent-admiring-noether/mnt/Desktop/Claude/Claude Back Up/Claude 4 back up/ebay_weekly_rankings.py"]
NS="urn:ebay:apis:eBLBaseComponents";URL="https://api.ebay.com/ws/api.dll"
STATE=os.path.expanduser("~/ebay_photo_enhance_state.json")
def toks():
    for p in PATHS:
        if os.path.exists(p):
            ns={};exec(compile(open(p).read(),p,"exec"),ns)
            if "STORES" in ns: return {s["name"]:s["token"] for s in ns["STORES"]}
    raise SystemExit("no tokens")
def enhance(im):
    im=im.convert("RGB")
    im2=ImageOps.autocontrast(im,cutoff=0.5)
    lum=ImageStat.Stat(im2.convert("L")).mean[0]
    if lum<95: im2=ImageEnhance.Brightness(im2).enhance(1.18)
    elif lum<120: im2=ImageEnhance.Brightness(im2).enhance(1.08)
    im2=ImageEnhance.Color(im2).enhance(1.06)
    im2=ImageEnhance.Sharpness(im2).enhance(1.35)
    return im2
def hdr(tok,call,ctype):
    return {"X-EBAY-API-SITEID":"0","X-EBAY-API-COMPATIBILITY-LEVEL":"967","X-EBAY-API-CALL-NAME":call,
            "X-EBAY-API-APP-NAME":APP,"X-EBAY-API-DEV-NAME":DEV,"X-EBAY-API-CERT-NAME":CERT,
            "X-EBAY-API-IAF-TOKEN":tok,"Content-Type":ctype}
def _http(body,headers,timeout=90,retries=4):
    """POST to eBay with exponential backoff on transient 500/502/503 (does NOT retry limit errors)."""
    import urllib.error
    for i in range(retries):
        try:
            return urlopen(Request(URL,data=body,headers=headers),timeout=timeout).read().decode()
        except urllib.error.HTTPError as e:
            if e.code in (500,502,503) and i<retries-1:
                time.sleep(3*(2**i)); continue
            raise
def is_limit(m):
    """True if an eBay message/exception indicates a usage-limit or service-unavailable condition."""
    m=str(m).lower()
    return ("exceeded usage limit" in m) or ("service unavailable" in m) or ("call limit" in m) or (" 503" in m)
def access_rules(tok):
    """Return {CallName:(daily_used,daily_cap)} from GetAPIAccessRules for pre-flight budgeting."""
    body=("<?xml version='1.0' encoding='utf-8'?><GetAPIAccessRulesRequest xmlns='urn:ebay:apis:eBLBaseComponents'>"
          "<RequesterCredentials><eBayAuthToken>"+tok+"</eBayAuthToken></RequesterCredentials></GetAPIAccessRulesRequest>").encode()
    r=ET.fromstring(_http(body,hdr(tok,"GetAPIAccessRules","text/xml")))
    out={}
    for rule in r.iter(f"{{{NS}}}APIAccessRule"):
        call=rule.findtext(f"{{{NS}}}CallName") or "ApplicationAggregate"
        try: used=int(rule.findtext(f"{{{NS}}}DailyUsage") or 0)
        except Exception: used=0
        try: cap=int(rule.findtext(f"{{{NS}}}DailyHardLimit") or 0)
        except Exception: cap=0
        out[call]=(used,cap)
    return out
def upload_eps(tok,jpg_bytes,name):
    b="----ebayboundary"+uuid.uuid4().hex
    xml=(f'<?xml version="1.0" encoding="utf-8"?><UploadSiteHostedPicturesRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
         f'<RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials>'
         f'<PictureName>{escape(name)}</PictureName><PictureSet>Supersize</PictureSet></UploadSiteHostedPicturesRequest>')
    parts=[]
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="XML Payload"\r\nContent-Type: text/xml;charset=utf-8\r\n\r\n{xml}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="dummy"; filename="image.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode())
    parts.append(jpg_bytes); parts.append(f'\r\n--{b}--\r\n'.encode())
    body=b"".join(parts)
    r=ET.fromstring(_http(body,hdr(tok,"UploadSiteHostedPictures",f"multipart/form-data; boundary={b}"),timeout=120))
    ack=r.findtext(f"{{{NS}}}Ack","")
    if ack not in ("Success","Warning"):
        return None,(r.findtext(f".//{{{NS}}}LongMessage") or ack)
    full=r.findtext(f".//{{{NS}}}SiteHostedPictureDetails/{{{NS}}}FullURL")
    return full,ack
def revise(tok,iid,urls):
    pics="".join(f"<PictureURL>{escape(u)}</PictureURL>" for u in urls)
    body=(f'<?xml version="1.0" encoding="utf-8"?><ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents"><RequesterCredentials><eBayAuthToken>{tok}</eBayAuthToken></RequesterCredentials><Item><ItemID>{iid}</ItemID><PictureDetails><GalleryType>Gallery</GalleryType>{pics}</PictureDetails></Item></ReviseFixedPriceItemRequest>').encode()
    r=ET.fromstring(_http(body,hdr(tok,"ReviseFixedPriceItem","text/xml"),timeout=90))
    ack=r.findtext(f"{{{NS}}}Ack","")
    return ack in ("Success","Warning"),(r.findtext(f".//{{{NS}}}ShortMessage") or ack)
import re
def hires(u):
    # request eBay's large master variant
    u=re.sub(r's-l\d+\.jpg', 's-l1600.jpg', u)
    u=re.sub(r'/\$_\d+\.JPG', '/$_57.JPG', u)
    return u
def dl(u):
    try: return urlopen(Request(hires(u),headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
    except Exception: return urlopen(Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
def ensure_min(im,mn=1600):
    w,h=im.size
    if max(w,h)>=mn: return im
    s=mn/max(w,h)
    return im.resize((int(round(w*s)),int(round(h*s))),Image.LANCZOS)
def main():
    TK=toks(); apply="--apply" in sys.argv; only=None
    if "--only" in sys.argv: only=sys.argv[sys.argv.index("--only")+1]
    state=json.load(open(STATE)) if os.path.exists(STATE) else {}
    if "--revert" in sys.argv:
        for iid,rec in list(state.items()):
            if only and iid!=only: continue
            if apply:
                ok,msg=revise(TK[rec["store"]],iid,rec["original"]); print(("OK " if ok else "FAIL ")+iid,msg)
        return
    store=sys.argv[1]; data=json.load(open(sys.argv[2])); tok=TK[store]
    primary_only="--primary-only" in sys.argv
    # --- pre-flight quota gate (only when actually writing) ---
    if apply and "--no-preflight" not in sys.argv:
        budget=int(sys.argv[sys.argv.index("--min-budget")+1]) if "--min-budget" in sys.argv else 300
        try:
            ru=access_rules(tok)
        except Exception as e:
            print("STOP preflight: cannot read eBay access rules (app may be throttled):",str(e)[:100]); return
        blocked=False
        for cn in ("UploadSiteHostedPictures","ReviseFixedPriceItem"):
            used,cap=ru.get(cn,(0,0)); rem=(cap-used) if cap else None
            print(f"quota {cn}: used={used} cap={cap} rem={rem}")
            if cap and rem is not None and rem<budget:
                print(f"STOP preflight: {cn} remaining {rem} < buffer {budget}. Resume after ~midnight US/Pacific."); blocked=True
        if blocked: return
    max_calls=int(sys.argv[sys.argv.index("--max-calls")+1]) if "--max-calls" in sys.argv else None
    calls=0
    done=fail=0
    for it in data:
        iid=it["id"]
        if only and iid!=only: continue
        if iid in state and "--force" not in sys.argv: continue
        if "--skip-upscaled" in sys.argv and state.get(iid,{}).get("upscaled"): continue
        orig=it["pics"]
        if not orig: continue
        if max_calls is not None and calls>=max_calls:
            print(f"STOP: reached --max-calls {max_calls} safety cap after done={done}. Rerun to continue."); break
        srcs=orig[:1] if primary_only else orig
        newurls=[]
        try:
            for k,u in enumerate(srcs):
                img=ensure_min(Image.open(io.BytesIO(dl(u))))
                buf2=io.BytesIO(); enhance(img).save(buf2,"JPEG",quality=90); buf2.seek(0)
                eps,msg=upload_eps(tok,buf2.read(),f"{iid}_{k}"); calls+=1
                if not eps:
                    if is_limit(msg):
                        print(f"STOP: eBay usage limit hit on UploadSiteHostedPictures at {iid} (done={done}). Resume after reset.")
                        json.dump(state,open(STATE,"w"),indent=2); return
                    raise RuntimeError("upload failed: "+str(msg))
                newurls.append(eps)
            final=newurls+ (orig[1:] if primary_only else [])
            if not apply:
                print(f"DRY {iid}: would replace {len(srcs)} pic(s)"); continue
            ok,msg=revise(tok,iid,final); calls+=1
            if ok:
                rec=state.get(iid,{}); rec.update({"store":store,"original":rec.get("original",orig),"upscaled":True})
                state[iid]=rec; done+=1; print("OK  ",iid,it["title"][:40])
            else:
                fail+=1; print("FAIL revise",iid,msg)
                if is_limit(msg):
                    print(f"STOP: eBay usage limit hit on ReviseFixedPriceItem at {iid} (done={done}). Resume after reset.")
                    json.dump(state,open(STATE,"w"),indent=2); return
        except Exception as e:
            fail+=1; print("FAIL",iid,e)
            if is_limit(e):
                print(f"STOP: eBay usage limit / service-unavailable at {iid} (done={done}). Resume after reset.")
                json.dump(state,open(STATE,"w"),indent=2); return
        if apply: json.dump(state,open(STATE,"w"),indent=2); time.sleep(0.4)
        if (done+fail)%20==0: print(f"...progress done={done} fail={fail} calls={calls}",flush=True)
    print(f"{'APPLIED' if apply else 'DRY'} done={done} fail={fail} calls={calls}")
if __name__=="__main__": main()
