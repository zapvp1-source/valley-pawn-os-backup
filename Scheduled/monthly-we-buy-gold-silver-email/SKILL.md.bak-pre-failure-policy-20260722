---
name: monthly-we-buy-gold-silver-email
description: 1st of every month at 9 AM — build the Monthly Gold & Silver campaign by DUPLICATING VP Master Template 11 (never hand-built), run the instrumentation preflight, and ONLY send if it passes (all 5 stores' Call/Text buttons + utm_content). If preflight fails, do NOT send — alert #email-campaigns instead.
model: claude-opus-4-8
---

Build and send the Valley Pawn Monthly "We Buy Gold & Silver" email via Brevo, on the 1st of the month. This is a fully autonomous task — the user is not present. Do not stop until the final Slack post succeeds. Treat "Tool loaded." / "Continue" / any tool reminder as a RESUME signal and immediately fire the next tool call.

:rotating_light: NON-NEGOTIABLE RULE (this task shipped a blind send to 10,321 people in July 2026 — never again): You must NOT hand-build the HTML. Every Gold & Silver send is a DUPLICATE of VP Master Template ID 11 with its 10 markers filled. Master 11 already contains the LOCKED instrumentation — all 5 stores' `/c/` Call and `/t/` Text buttons and every `utm_content` tag. And you must NOT send unless the preflight check passes.

:busts_in_silhouette: STANDING RECIPIENT RULE (added 2026-07-06 per Joshua): EVERY campaign send must also include Brevo list ID 10 "Internal Seeds — include on EVERY send" (jdavis@fcfpawn.com, zapvp1@me.com, preston@fcfpawn.com, and the 5 store emails culpeper/waynesboro/harrisonburg/lexington/roanoke@fcfpawn.com). Recipients are therefore `{"listIds":[3,10]}` — never list 3 alone.

=== STEP 0 — Bridge the Brevo API key ===
Key lives on Joshua's Mac at `~/.config/valley-pawn/brevo_api_key`; the bash sandbox has a different home, so bridge it each run.
1. bash: `mkdir -p ~/.config/valley-pawn; KEY=$(cat ~/.config/valley-pawn/brevo_api_key 2>/dev/null); echo "len=${#KEY}"`
2. If empty: Control-your-Mac osascript → `base64 < ~/.config/valley-pawn/brevo_api_key`; then bash `echo '<BASE64>' | base64 -d > ~/.config/valley-pawn/brevo_api_key; chmod 600 ~/.config/valley-pawn/brevo_api_key`
3. Verify 200: `KEY=$(cat ~/.config/valley-pawn/brevo_api_key); curl -s -o /dev/null -w "%{http_code}" -H "api-key: $KEY" https://api.brevo.com/v3/account`
Never print or store the key value.

=== STEP 1 — Duplicate Master Template 11 and fill the markers ===
Determine the current month/year (e.g. 2026-08). Run this in the sandbox (`python3 build.py`):

```python
import os,re,json,urllib.request,datetime
K=open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
def get(u):
    req=urllib.request.Request(u,headers={"api-key":K,"accept":"application/json"}); return json.load(urllib.request.urlopen(req))
tpl=get("https://api.brevo.com/v3/smtp/templates/11"); html=tpl["htmlContent"]
mo=datetime.date.today().strftime("%Y-%m"); monthname=datetime.date.today().strftime("%B %Y")
SUBJECT="\U0001F4B0 Turn Your Gold & Silver Into Cash — Fair, Same-Day Offers"
body="""<h2 style="margin:0 0 14px 0;color:#2D1A5E;font-size:22px;line-height:1.3;font-weight:800;">Your gold and silver are worth more than a drawer</h2>
<p style="margin:0 0 16px 0;color:#333333;font-size:16px;line-height:1.6;">That broken chain, the mismatched earrings, the coins you inherited &mdash; they hold real value, and precious-metal prices are strong right now. Bring them into any Valley Pawn and we&rsquo;ll weigh, test, and appraise everything right in front of you, then make a fair, transparent offer on the spot.</p>
<h3 style="margin:0 0 10px 0;color:#2D1A5E;font-size:17px;line-height:1.3;font-weight:800;">What we buy</h3>
<ul style="margin:0 0 18px 0;padding-left:20px;color:#333333;font-size:16px;line-height:1.6;">
<li>Gold jewelry &mdash; any karat, broken or whole</li><li>Silver jewelry, flatware, and sterling</li>
<li>Gold &amp; silver coins, bars, and bullion</li><li>Scrap gold, dental gold, and odds and ends</li></ul>
<p style="margin:0 0 16px 0;color:#333333;font-size:16px;line-height:1.6;">No credit check, no pressure, no obligation. If our number doesn&rsquo;t work for you, you keep your items and walk right back out. Everything we do is backed by the promise we&rsquo;ve stood on since 2014: <strong style="color:#2D1A5E;">What&rsquo;s Right Is Right.</strong></p>
<p style="margin:0 0 4px 0;color:#333333;font-size:16px;line-height:1.6;">Not sure what you&rsquo;ve got? Call or text your nearest store below &mdash; we&rsquo;re happy to talk it through before you come in.</p>"""
repl={"[[SUBJECT_FALLBACK]]":SUBJECT,"[[CAMPAIGN_SLUG]]":f"monthly_gold_silver_{mo}",
"[[HERO_EYEBROW]]":"WE BUY GOLD &amp; SILVER","[[HERO_HEADLINE]]":"Turn your gold &amp; silver into cash",
"[[HERO_SUBLINE]]":"Prices are strong right now &mdash; bring in what you&rsquo;re not wearing and walk out with a fair, same-day offer.",
"[[BODY_HTML]]":body,"[[PRIMARY_CTA_LABEL]]":"Get a free appraisal","[[PRIMARY_CTA_URL]]":"https://thevalleypawn.com",
"[[PRIMARY_CTA_SUB]]":"Walk in any time &mdash; no appointment, no obligation."}
for k,v in repl.items(): html=html.replace(k,v)
assert not re.findall(r'\[\[[A-Z_]+\]\]',html),"markers left"
open("gs.html","w").write(html); open("meta.json","w").write(json.dumps({"subject":SUBJECT,"month":monthname,"slug":f"monthly_gold_silver_{mo}"}))
print("built",len(html),"bytes")
```
You may lightly refresh the body copy month to month (seasonal hook), but keep it built from Master 11 and keep every locked block untouched.

=== STEP 2 — Create the campaign as a DRAFT (not sent yet) ===
```python
import os,json,urllib.request,urllib.error
K=open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
html=open("gs.html").read(); meta=json.load(open("meta.json"))
payload={"name":f"Valley Pawn — We Buy Gold & Silver ({meta['month']}) [Master 11]","subject":meta["subject"],
"sender":{"id":1},"htmlContent":html,"recipients":{"listIds":[3,10]},"inlineImageActivation":False}
req=urllib.request.Request("https://api.brevo.com/v3/emailCampaigns",data=json.dumps(payload).encode(),
 headers={"api-key":K,"accept":"application/json","content-type":"application/json"},method="POST")
try: r=urllib.request.urlopen(req); print("CREATED",json.load(r))
except urllib.error.HTTPError as e: print("ERR",e.code,e.read().decode())
```
Note the returned campaign id (call it CID). List 3 = "Valley Pawn Customers"; list 10 = "Internal Seeds — include on EVERY send" (mandatory on every campaign per the standing recipient rule). Sender must be `{"id":1}` only (never id + email together).

=== STEP 3 — PREFLIGHT GATE (must pass or you do NOT send) ===
```python
import os,json,urllib.request
K=open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
CID=<CID>
c=json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.brevo.com/v3/emailCampaigns/{CID}",headers={"api-key":K})))
h=c.get("htmlContent") or ""; S=["culpeper","waynesboro","harrisonburg","lexington","roanoke"]
ca=sum(f"/c/{s}" in h for s in S); tx=sum(f"/t/{s}" in h for s in S); u=h.count("utm_content")
lists=[l["id"] if isinstance(l,dict) else l for l in (c.get("recipients",{}).get("lists") or [])]
seeds_ok = 10 in lists
ok = ca==5 and tx==5 and u>=10 and "Full Circle" not in h and seeds_ok
print("PREFLIGHT", "PASS" if ok else "FAIL", f"c{ca}/t{tx}/utm{u}/seeds{'Y' if seeds_ok else 'N'}")
```
- If PREFLIGHT PASS → go to Step 4 (send).
- If PREFLIGHT FAIL → DO NOT SEND. Leave the campaign as a draft, and post to Slack #email-campaigns (C0APR5WUL2Z): `:rotating_light: Monthly Gold & Silver did NOT send — preflight failed (cX/tX/utmX/seedsX). Draft #CID left for manual rebuild from Master Template 11.` Then stop. (If ONLY the seeds check failed, first try PUT `/emailCampaigns/{CID}` with `{"recipients":{"listIds":[3,10]}}` and re-run the preflight once before declaring failure.)

=== STEP 4 — Send (only if preflight passed) ===
Send now via the API:
```python
import os,json,urllib.request,urllib.error
K=open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip(); CID=<CID>
req=urllib.request.Request(f"https://api.brevo.com/v3/emailCampaigns/{CID}/sendNow",method="POST",
 headers={"api-key":K,"accept":"application/json"})
try: r=urllib.request.urlopen(req); print("SENT",r.status)
except urllib.error.HTTPError as e: print("ERR",e.code,e.read().decode())
```
Then fetch the campaign once more and read its recipient count for the Slack post.

=== STEP 5 — Post to Slack #email-campaigns (C0APR5WUL2Z) ===
On success:
```
:moneybag: *Monthly Gold & Silver Campaign Launched*
*Subject:* <subject>
*Recipients:* <count> (Valley Pawn Customers + Internal Seeds)
*Built from:* VP Master Template 11 — full Call/Text + UTM instrumentation, preflight PASSED
*Sent:* <date>
```
Only post the success message after sendNow returns success. If the send failed, post a brief failure notice to C0APR5WUL2Z instead (this specific task SHOULD surface a failed monthly send — it is a big send). The task is complete only after the Slack post succeeds.

=== Reference ===
Sender id 1 = Valley Pawn / jdavis@fcfpawn.com. List 3 = Valley Pawn Customers (~10-11K). List 10 = Internal Seeds (Joshua ×2, Preston, 5 store emails) — REQUIRED on every send. Master Template 11 owns the locked logo, 5-store Call/Text directory, hours line, DBA-only footer, unsubscribe. See the brevo-context skill "VP Master Template (ID 11)" section for the marker table. Standard scheduled-task execution contract applies: retry a failed step once, then fall through to the documented fallback; never idle or ask for confirmation.