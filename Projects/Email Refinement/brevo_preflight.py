#!/usr/bin/env python3
"""
Brevo send preflight v3 — instrumentation + content guardrail with AUTO-FIX.
Run against a campaign ID BEFORE scheduling/sending.

Usage:  python3 brevo_preflight.py <campaign_id>
Exit 0 = PASS (safe to send; may have been auto-fixed first).
Exit 1 = FAIL (unfixable problem — do not send).

Behavior (v3, 2026-07-23):
 - Mechanically-fixable defects are AUTO-REPAIRED on modifiable campaigns
   (draft/queued/scheduled/suspended), then the full check suite re-runs.
   Only a fully-clean result is written back (PUT) and passed.
   Fixable: double-"?" URLs, unfilled [[PRIMARY_CTA_SEP]], legal-entity-name
   footer leak, misplaced content inside a LOCKED store card.
 - Judgment defects still hard-fail: missing Call/Text buttons, low utm
   coverage, firearms language, unbalanced personalization conditionals,
   other unfilled [[MARKERS]].
 - SENT campaigns are report-only — never modified.
 - PAY TRANSPARENCY (added 2026-08-03): any campaign containing hiring language must
   state a wage/salary or range (Va. Code 40.1-28.7:12). Hard-fail, never auto-fixed —
   where a range belongs in prose is a judgment call, and guessing a number is worse
   than blocking the send.

Key: ~/.config/valley-pawn/brevo_api_key (bridge from Mac if empty).
"""
import os, sys, json, re, time, urllib.request, urllib.error

STORES = ["culpeper","waynesboro","harrisonburg","lexington","roanoke"]
API = "https://api.brevo.com/v3"

# --- VA pay-transparency (Va. Code 40.1-28.7:12, eff. 2026-07-01) -------------
# ANY posting for a job, promotion or transfer -- including a marketing email that
# advertises an opening -- must state a good-faith wage/salary or range. No employer
# size threshold. Penalty: $1k first / $5k subsequent civil, plus a private action
# for $1k-$10k statutory damages or actual damages, plus attorney fees.
# Campaign #51 (2026-07-23 hiring blast) went out without one. This check exists so
# that cannot recur silently.
# STRONG: unambiguous "this email advertises a job". Any ONE triggers.
HIRING_SIGNALS_STRONG = [
    r"\bwe(?:'|’)?re hiring\b", r"\bwe are hiring\b", r"\bnow hiring\b",
    r"\bhiring\s+(?:retail\s+)?(?:sales|loan|store|full[- ]time|part[- ]time)\b",
    r"\bjoin (?:our|the) team\b", r"\bcome work (?:with|at|for)\b",
    r"\bopen positions?\b", r"\bjob openings?\b", r"\bnow accepting applications\b",
]
# WEAK: consistent with a job ad but also normal in an ordinary newsletter footer.
# A careers link ALONE is not a job posting -- requiring two weak signals stops
# preflight failing every campaign the day someone adds /careers to the footer.
HIRING_SIGNALS_WEAK = [
    r"thevalleypawn\.com/careers", r"/careers\b",
    r"\bapply (?:at|now|today|online)\b", r"\bsend (?:your )?resum(?:e|é)\b",
]
# Accept either an explicit range or a single stated wage; hourly or salaried.
PAY_DISCLOSURE_RES = [
    # $16.50-$21.50 /hour  (en dash, em dash, hyphen, or "to")
    r"\$\s?\d{1,3}(?:[.,]\d{2})?\s*(?:\u2013|\u2014|-|to)\s*\$?\s?\d{1,3}(?:[.,]\d{2})?\s*(?:/|\s*per\s*|\s*an\s*)?\s*(?:hr|hour)\b",
    # $45,000-$55,000 a year / per year / annually
    r"\$\s?\d{2,3}(?:,\d{3})\s*(?:\u2013|\u2014|-|to)\s*\$?\s?\d{2,3}(?:,\d{3})\s*(?:/|\s*per\s*|\s*a\s*)?\s*(?:yr|year|annually)\b",
    # single stated wage: $17.00 per hour / an hour / /hour
    r"\$\s?\d{1,3}(?:[.,]\d{2})?\s*(?:/|\s*per\s*|\s*an\s*)\s*(?:hr|hour)\b",
    # single stated salary
    r"\$\s?\d{2,3}(?:,\d{3})\s*(?:/|\s*per\s*|\s*a\s*)\s*(?:yr|year|annually)\b",
]

def _looks_like_job_posting(text):
    """Matched signals if this email advertises an opening, else [].
    Trigger = any ONE strong signal, or TWO+ weak signals together."""
    strong=[p for p in HIRING_SIGNALS_STRONG if re.search(p, text, re.I)]
    weak=[p for p in HIRING_SIGNALS_WEAK if re.search(p, text, re.I)]
    if strong: return strong+weak
    return weak if len(weak)>=2 else []

def _has_pay_disclosure(text):
    return any(re.search(p, text, re.I) for p in PAY_DISCLOSURE_RES)

def key():
    p=os.path.expanduser("~/.config/valley-pawn/brevo_api_key")
    k=open(p).read().strip() if os.path.exists(p) else ""
    if not k: sys.exit("FAIL: Brevo API key missing — bridge it from the Mac first.")
    return k

def _open_with_retry(req, tries=5):
    """Brevo rate-limits bursts (HTTP 429). Back off and retry so a multi-campaign
    watchdog sweep doesn't crash mid-run."""
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries-1:
                time.sleep(2 ** attempt * 3)  # 3s, 6s, 12s, 24s
                continue
            raise

def get(url,k):
    req=urllib.request.Request(url,headers={"api-key":k,"accept":"application/json"})
    return json.load(_open_with_retry(req))

def put_html(cid,k,html):
    body=json.dumps({"htmlContent":html}).encode()
    req=urllib.request.Request(f"{API}/emailCampaigns/{cid}",data=body,method="PUT",
        headers={"api-key":k,"accept":"application/json","content-type":"application/json"})
    return _open_with_retry(req).status

# ---------------- checks ----------------

def run_checks(h):
    """Returns (problems, fixable_flags). Each problem is (code, message)."""
    problems=[]
    no_c = re.sub(r"<!--.*?-->", "", h, flags=re.S)

    calls=[s for s in STORES if f"/c/{s}" in h]
    texts=[s for s in STORES if f"/t/{s}" in h]
    utm=h.count("utm_content")
    if len(calls)<5: problems.append(("buttons",f"missing Call buttons for: {set(STORES)-set(calls) or 'none'} ({len(calls)}/5)"))
    if len(texts)<5: problems.append(("buttons",f"missing Text buttons for: {set(STORES)-set(texts) or 'none'} ({len(texts)}/5)"))
    if utm<10:       problems.append(("utm",f"only {utm} utm_content tags (need >=10 — north-star tracking)"))
    if "Full Circle" in no_c: problems.append(("legalname","legal entity name 'Full Circle Finance Inc' in customer-visible content — DBA only"))

    for m in re.finditer(r'href="([^"]+)"', no_c):
        u=m.group(1)
        if u.startswith("http") and u.count("?")>1:
            problems.append(("doubleq",f"malformed URL (two '?'): {u[:110]}"))

    leftovers=sorted(set(re.findall(r"\[\[[A-Z_]+\]\]", no_c)))
    for l in leftovers:
        problems.append(("sep" if l=="[[PRIMARY_CTA_SEP]]" else "marker", f"unfilled template marker: {l}"))

    for m in re.finditer(r'<!-- =+ LOCKED: STORE — ([A-Z]+) =+ -->', h):
        card=m.group(1).title()
        nxt=re.search(r'<!-- =+ LOCKED', h[m.end():])
        seg=h[m.end(): m.end()+(nxt.start() if nxt else 3000)]
        if re.search(r'<h3\b', seg) or "NOTPAWN" in seg:
            label=(re.findall(r'NOTPAWN[^<]*', seg) or ["<h3> content block"])[0].strip()
            problems.append(("cardcontent",f"foreign content inside the {card} directory card: '{label}'"))

    n_if=len(re.findall(r'\{%\s*if\b',h)); n_end=len(re.findall(r'\{%\s*endif\s*%\}',h))
    if n_if!=n_end: problems.append(("jinja",f"unbalanced personalization conditionals: {n_if} if vs {n_end} endif"))

    sig=_looks_like_job_posting(no_c)
    if sig and not _has_pay_disclosure(no_c):
        problems.append(("paytransparency",
            "this email advertises a job opening but states NO wage/salary range — "
            "Va. Code 40.1-28.7:12 (eff. 2026-07-01) requires a good-faith pay range in "
            "EVERY posting for a job, promotion or transfer, with no employer-size threshold. "
            f"Hiring language detected: {sig[:3]}. "
            "Add the approved range (Sales & Loan Associate/Rep: $16.50-$21.50 per hour) to the body copy."))

    fw=sorted(set(w.lower() for w in re.findall(r'\b(firearms?|guns?|pistols?|rifles?|shotguns?|ammo|ammunition)\b',no_c,re.I)))
    if fw: problems.append(("firearms",f"firearms language in rendered content: {fw} — VP policy is zero firearms mentions in marketing email"))
    return problems

FIXABLE = {"doubleq","sep","legalname","cardcontent"}

# ---------------- fixers ----------------

def fix_doubleq(h):
    def repl(m):
        u=m.group(1)
        if u.startswith("http") and u.count("?")>1:
            first=u.find("?")
            u=u[:first+1]+u[first+1:].replace("?","&")
        return f'href="{u}"'
    return re.sub(r'href="([^"]+)"', repl, h)

def fix_sep(h):
    # decide '?' vs '&' from the URL immediately preceding the token inside the same href
    def repl(m):
        url=m.group(1)
        sep="&" if "?" in url else "?"
        return f'href="{url}{sep}'
    return re.sub(r'href="([^"\[]*)\[\[PRIMARY_CTA_SEP\]\]', repl, h)

def fix_legalname(h):
    # normalize footer brand line to DBA only (leave HTML comments untouched)
    parts = re.split(r'(<!--.*?-->)', h, flags=re.S)
    out=[]
    for p in parts:
        if p.startswith("<!--"):
            out.append(p); continue
        p=re.sub(r'(?:<strong[^>]*>)?Full Circle Finance,? Inc\.?(?:</strong>)?'
                 r'(?:\s*(?:&middot;|·|—|–|-)?\s*(?:DBA)?\s*Valley Pawn)?', 'Valley Pawn', p)
        out.append(p)
    return "".join(out)

def fix_cardcontent(h):
    """Move NOTPAWN/h3 content divs out of LOCKED store cards into the body slot (before TRUST STRIP)."""
    m=re.search(r'<div style="background:#f4f1ec;[^"]*">.*?NOTPAWN.*?</div>\s*', h, re.S)
    if not m: return h
    div=m.group(0).strip()
    h=h[:m.start()]+h[m.end():]
    anchor=h.find("<!-- ============ LOCKED: TRUST STRIP")
    if anchor==-1: return h  # nowhere safe to put it; content removed from card is still better
    close_td=h.rfind("</td>",0,anchor)
    if close_td==-1: return h
    return h[:close_td]+"\n"+div+"\n          "+h[close_td:]

FIXERS={"doubleq":fix_doubleq,"sep":fix_sep,"legalname":fix_legalname,"cardcontent":fix_cardcontent}

# ---------------- main ----------------

def check(cid):
    k=key()
    c=get(f"{API}/emailCampaigns/{cid}",k)
    h=c.get("htmlContent") or ""
    name=c.get("name",""); status=c.get("status","")
    modifiable = status in ("draft","queued","scheduled","suspended")

    problems=run_checks(h)
    calls=[s for s in STORES if f"/c/{s}" in h]; texts=[s for s in STORES if f"/t/{s}" in h]
    print(f"Campaign #{cid} [{status}] {name}")
    print(f"  Call buttons: {len(calls)}/5   Text buttons: {len(texts)}/5   utm_content: {h.count('utm_content')}")

    fixed_log=[]
    if problems and modifiable:
        codes={p[0] for p in problems}
        for code in codes & FIXABLE:
            h2=FIXERS[code](h)
            if h2!=h:
                h=h2; fixed_log.append(code)
        # cardcontent can occur multiple times
        while "cardcontent" in {p[0] for p in run_checks(h)}:
            h2=fix_cardcontent(h)
            if h2==h: break
            h=h2
        remaining=run_checks(h)
        if fixed_log:
            if not remaining:
                st=put_html(cid,k,h)
                print(f"  AUTO-FIXED ({', '.join(sorted(set(fixed_log)))}) and saved (HTTP {st}) — re-verified clean.")
                print("  RESULT: ✅ PASS (after auto-fix) — safe to schedule.")
                return 0
            else:
                print(f"  Auto-fix repaired: {', '.join(sorted(set(fixed_log)))} — but unfixable problems remain (campaign NOT modified):")
                for p in remaining: print("   - "+p[1])
                print("  RESULT: ❌ FAIL — DO NOT SEND")
                return 1
        # nothing fixable
    if problems:
        tag = "" if modifiable else " (sent/report-only — cannot modify)"
        print(f"  RESULT: ❌ FAIL — DO NOT SEND{tag}")
        for p in problems: print("   - "+p[1])
        print("  Fix: rebuild from VP Master Template v2 COMPACT (ID 48) — see brevo-context skill.")
        return 1
    print("  RESULT: ✅ PASS — instrumentation + content checks intact, safe to schedule.")
    return 0

if __name__=="__main__":
    if len(sys.argv)!=2: sys.exit("Usage: python3 brevo_preflight.py <campaign_id>")
    sys.exit(check(sys.argv[1]))
