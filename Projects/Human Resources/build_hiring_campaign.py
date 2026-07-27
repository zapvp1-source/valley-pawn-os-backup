#!/usr/bin/env python3
"""Build the 2026-07-23 'We're hiring' Brevo campaign from VP Master Template (id 11).
Creates a DRAFT campaign to lists 3 (Valley Pawn Customers) + 10 (Internal Seeds).
Then run brevo_preflight.py <id> before scheduling. One-shot, additive — does not touch template 11."""
import json, os, urllib.request

API = "https://api.brevo.com/v3"
k = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()

def req(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(API + path, data=data, method=method,
        headers={"api-key": k, "accept": "application/json", "content-type": "application/json"})
    resp = urllib.request.urlopen(r, timeout=30)
    body = resp.read().decode()
    return json.loads(body) if body else {}

# 1. Pull master template html (v2 COMPACT — current standard per preflight)
t = req("GET", "/smtp/templates/48")
html = t["htmlContent"]

SLUG = "hiring_2026-07-23"
BODY = """
<h2 style="color:#2D1A5E; font-size:22px; margin:0 0 14px;">You already know us &mdash; come work with us</h2>
<p style="color:#333; font-size:16px; line-height:1.6; margin:0 0 16px;">Valley Pawn is hiring <strong>Retail Sales Associates</strong> at all five stores &mdash; Culpeper, Waynesboro, Harrisonburg, Lexington and Roanoke. We're family-owned since 2014, and some of the best people on our team started out on the other side of the counter.</p>
<p style="color:#333; font-size:16px; line-height:1.6; margin:0 0 16px;"><strong>The honest pitch:</strong> every Sunday off (all five stores are closed), most locations closed Wednesdays too, and our doors close at 6 PM &mdash; no late retail nights, ever. Competitive hourly pay plus a monthly bonus program tied to how your store performs. And the work is never boring: jewelry one hour, guitars and electronics the next.</p>
<p style="color:#333; font-size:16px; line-height:1.6; margin:0 0 16px;"><strong>No pawn experience needed.</strong> Attitude beats r&eacute;sum&eacute; here &mdash; we'll train you on everything. You'll need to be 18 or older, available Saturdays, and able to pass the background screening required to work in a licensed pawn business. Full-time and part-time available.</p>
<p style="color:#333; font-size:16px; line-height:1.6; margin:0 0 16px;"><strong>Know somebody great?</strong> Forward them this email. The details and how to apply are at <a href="https://thevalleypawn.com/careers?utm_source=brevo&amp;utm_medium=email&amp;utm_campaign=hiring_2026-07-23&amp;utm_content=body_careers_link" style="color:#0099DD;">thevalleypawn.com/careers</a> &mdash; or just walk into any store and ask for an application.</p>
""".strip()

repl = {
    "[[CAMPAIGN_SLUG]]": SLUG,
    "[[HERO_EYEBROW]]": "WE&rsquo;RE HIRING",
    "[[HERO_HEADLINE]]": "Come work where What&rsquo;s Right Is Right",
    "[[HERO_SUBLINE]]": "We&rsquo;re hiring at all five Valley Pawn stores &mdash; and we&rsquo;d love for it to be someone we already know.",
    "[[BODY_HTML]]": BODY,
    "[[PRIMARY_CTA_LABEL]]": "See open positions",
    "[[PRIMARY_CTA_URL]]": "https://thevalleypawn.com/careers",
    "[[PRIMARY_CTA_SEP]]": "?",
    "[[PRIMARY_CTA_SUB]]": "Or stop by any store and ask for an application",
    "[[SUBJECT_FALLBACK]]": "We're hiring — come work at Valley Pawn",
}
for a, b in repl.items():
    html = html.replace(a, b)

leftover = [m for m in ("[[CAMPAIGN_SLUG]]","[[HERO_","[[BODY_HTML]]","[[PRIMARY_CTA") if m in html]
if leftover:
    raise SystemExit("Unfilled markers remain: %s" % leftover)

payload = {
    "name": "Hiring — Retail Sales Associates v2 (2026-07-23)",
    "subject": "We're hiring — come work at Valley Pawn",
    "previewText": "All five stores. Sundays off, home by 6, monthly bonus — and we'll train you.",
    "sender": {"name": "Valley Pawn", "email": "jdavis@fcfpawn.com"},
    "htmlContent": html,
    "recipients": {"listIds": [3, 10]},
}
out = req("POST", "/emailCampaigns", payload)
print("CAMPAIGN_ID:", out.get("id"))
