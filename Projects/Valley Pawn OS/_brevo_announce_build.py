#!/usr/bin/env python3
"""Build the Waynesboro 6-days announcement campaign from VP Master Template 11 (patched copy)."""
import json, urllib.request
from pathlib import Path

KEY = (Path.home() / ".config" / "valley-pawn" / "brevo_api_key").read_text().strip()
BASE = "https://api.brevo.com/v3"

def call(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"accept": "application/json", "api-key": KEY, "content-type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = r.read().decode()
            return json.loads(d) if d.strip() else {}
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:400]); raise

tpl = Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/brevo_backups_2026-07-23/template_11_new.html").read_text()

BODY_HTML = (
    '<p style="margin:0 0 16px 0;color:#333333;font-size:15px;line-height:1.65;">Big news from our Waynesboro store: starting <strong>Wednesday, July 29</strong>, we&rsquo;re open <strong>six days a week</strong> &mdash; Monday through Saturday, 10am to 6pm.</p>'
    '<p style="margin:0 0 16px 0;color:#333333;font-size:15px;line-height:1.65;">That&rsquo;s one more day every week to make a loan payment, get a free appraisal, sell your gold and silver, put something on layaway, or just come browse the showroom. Same fair, no-judgment service &mdash; now with Wednesdays.</p>'
    '<p style="margin:0 0 16px 0;color:#333333;font-size:15px;line-height:1.65;">And as always, everything we sell is backed by our 30-day warranty. What&rsquo;s Right Is Right.</p>'
)

tokens = {
    "[[CAMPAIGN_SLUG]]": "waynesboro_6days_2026-07-24",
    "[[HERO_EYEBROW]]": "STORE HOURS UPDATE",
    "[[HERO_HEADLINE]]": "Waynesboro is now open 6 days a week",
    "[[HERO_SUBLINE]]": "Starting Wednesday, July 29, our Waynesboro store is open Monday through Saturday, 10am&ndash;6pm &mdash; one more day to shop, sell, or make a payment.",
    "[[BODY_HTML]]": BODY_HTML,
    "[[PRIMARY_CTA_LABEL]]": "Get directions to Waynesboro",
    "[[PRIMARY_CTA_URL]]": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Waynesboro+VA",
    "[[PRIMARY_CTA_SEP]]": "&",
    "[[PRIMARY_CTA_SUB]]": "1321 West Broad Street, Waynesboro &middot; Now open Wednesdays",
    "[[SUBJECT_FALLBACK]]": "Waynesboro is now open 6 days a week",
}
html = tpl
for k, v in tokens.items():
    n = html.count(k)
    print(f"token {k}: {n}")
    html = html.replace(k, v)

leftover = html.count("[[")
print("leftover [[ tokens:", leftover)
if leftover:
    i = html.index("[[")
    print("context:", html[i-60:i+80])
    raise SystemExit("unfilled tokens — aborting")

body = {
    "name": "Waynesboro 6 Days — Hours Announcement — 2026-07-24",
    "subject": "Waynesboro is now open 6 days a week 🎉",
    "previewText": "Starting July 29: Monday–Saturday, 10am–6pm. One more day to shop, sell, or make a payment.",
    "sender": {"name": "Valley Pawn", "email": "jdavis@fcfpawn.com"},
    "htmlContent": html,
    "recipients": {"listIds": [3, 10]},
}
res = call("/emailCampaigns", "POST", body)
print("CREATED campaign id:", res.get("id"))
Path("/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/brevo_backups_2026-07-23/announce_campaign_id.txt").write_text(str(res.get("id")))
