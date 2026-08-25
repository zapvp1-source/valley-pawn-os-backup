#!/usr/bin/env python3
"""Giveaway follow-up discount ladder — Joshua's decision, 2026-08-24:
10% off in-store this month -> 20% next month -> 30% the month after -> stop.

Same mechanic as the existing "15% Off In-Store" holiday campaigns already run
by this account (e.g. Memorial Day 2026) — no new redemption system needed,
just "show this email in-store" honored at the register like the holiday sends
already are.

Campaign 71 (already queued for tomorrow 8/25 9am) gets the 10% copy.
Two new campaigns are created and scheduled for 20% (+1 month) and 30%
(+2 months), all to list 6 (82 giveaway entrants). After the 30% send, the
ladder stops — no further discount campaigns to this list.
"""
import json, urllib.request, os, time, sys, datetime

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"
LIST = 6


def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                   headers={"api-key": KEY,
                                            "Content-Type": "application/json",
                                            "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + a * 4); continue
            return e.code, e.read().decode()
    return 429, "rate limited"


def shell(eyebrow, headline, subline, body_html, cta_label, cta_url, utm):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{headline}</title>
<style>
body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}}
table,td{{mso-table-lspace:0pt;mso-table-rspace:0pt}}
img{{-ms-interpolation-mode:bicubic;border:0;height:auto;line-height:100%;outline:none;text-decoration:none}}
body{{margin:0!important;padding:0!important;width:100%!important;background-color:#F7F9FC}}
a{{color:#0099DD;text-decoration:none}}
@media screen and (max-width:600px){{.container{{width:100%!important}}.px-mobile{{padding-left:20px!important;padding-right:20px!important}}.h1{{font-size:26px!important;line-height:1.2!important}}}}
</style></head>
<body style="margin:0;padding:0;background-color:#F7F9FC;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<div style="display:none;font-size:1px;color:#F7F9FC;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">{subline}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#F7F9FC;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;background-color:#FFFFFF;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(45,26,94,0.06);">
<tr><td align="center" style="padding:28px 24px 16px 24px;background-color:#FFFFFF;">
<a href="https://thevalleypawn.com?utm_source=brevo&utm_medium=email&utm_campaign={utm}&utm_content=logo">
<img src="https://i0.wp.com/thevalleypawn.com/wp-content/uploads/2026/03/vp_logo_name-no-tag.png?fit=600%2C67&ssl=1" width="280" alt="Valley Pawn" style="display:block;width:280px;max-width:280px;height:auto;">
</a></td></tr>
<tr><td style="background-color:#2D1A5E;padding:32px 28px 28px 28px;" class="px-mobile">
<p style="margin:0 0 8px 0;color:#3DB8E8;font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">{eyebrow}</p>
<h1 class="h1" style="margin:0 0 12px 0;color:#FFFFFF;font-size:30px;line-height:1.18;font-weight:800;letter-spacing:-0.5px;">{headline}</h1>
<p style="margin:0;color:#E6DEF7;font-size:15px;line-height:1.5;">{subline}</p>
</td></tr>
<tr><td style="padding:28px 32px 8px 32px;" class="px-mobile">{body_html}</td></tr>
<tr><td style="padding:8px 32px 28px 32px;" class="px-mobile">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#F0F7FC;border-left:4px solid #0099DD;border-radius:6px;">
<tr><td style="padding:16px 18px;"><p style="margin:0;color:#2D1A5E;font-size:14px;line-height:1.55;">
Everything we sell carries our standard <strong>30-day warranty</strong>. We buy outright too &mdash; gold, silver, electronics, tools, the works. That&rsquo;s our promise: what&rsquo;s right is right.
</p></td></tr></table></td></tr>
<tr><td align="center" style="padding:8px 32px 36px 32px;" class="px-mobile">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td align="center" bgcolor="#F58C8A" style="border-radius:999px;">
<a href="{cta_url}&utm_source=brevo&utm_medium=email&utm_campaign={utm}&utm_content=primary_cta" style="display:inline-block;padding:16px 32px;font-size:16px;font-weight:700;color:#2D1A5E;text-decoration:none;border-radius:999px;letter-spacing:0.2px;">{cta_label} &rarr;</a>
</td></tr></table></td></tr>
<tr><td style="padding:0 32px;" class="px-mobile"><div style="height:1px;background-color:#E6E9F0;line-height:1px;font-size:1px;">&nbsp;</div></td></tr>
<tr><td style="padding:24px 32px 6px 32px;" class="px-mobile">
<p style="margin:0 0 2px 0;color:#0099DD;font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">Find your store</p>
<h2 style="margin:0;color:#2D1A5E;font-size:20px;line-height:1.25;font-weight:700;">Five Valley Pawn locations</h2></td></tr>
<tr><td style="padding:12px 32px 24px 32px;" class="px-mobile">
<p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;"><strong style="color:#2D1A5E;">Culpeper</strong> &nbsp;<a href="https://thevalleypawn.com/c/culpeper?utm_content=store_culpeper_call">Call</a> &middot; <a href="https://thevalleypawn.com/t/culpeper?utm_content=store_culpeper_text">Text</a></p>
<p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;"><strong style="color:#2D1A5E;">Waynesboro</strong> &nbsp;<a href="https://thevalleypawn.com/c/waynesboro?utm_content=store_waynesboro_call">Call</a> &middot; <a href="https://thevalleypawn.com/t/waynesboro?utm_content=store_waynesboro_text">Text</a></p>
<p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;"><strong style="color:#2D1A5E;">Harrisonburg</strong> &nbsp;<a href="https://thevalleypawn.com/c/harrisonburg?utm_content=store_harrisonburg_call">Call</a> &middot; <a href="https://thevalleypawn.com/t/harrisonburg?utm_content=store_harrisonburg_text">Text</a></p>
<p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;"><strong style="color:#2D1A5E;">Lexington</strong> &nbsp;<a href="https://thevalleypawn.com/c/lexington?utm_content=store_lexington_call">Call</a> &middot; <a href="https://thevalleypawn.com/t/lexington?utm_content=store_lexington_text">Text</a></p>
<p style="margin:0;font-size:14px;line-height:1.7;"><strong style="color:#2D1A5E;">Roanoke</strong> &nbsp;<a href="https://thevalleypawn.com/c/roanoke?utm_content=store_roanoke_call">Call</a> &middot; <a href="https://thevalleypawn.com/t/roanoke?utm_content=store_roanoke_text">Text</a></p>
</td></tr>
<tr><td align="center" style="background-color:#2D1A5E;padding:28px 28px 22px 28px;" class="px-mobile">
<p style="margin:0 0 12px 0;color:#FFFFFF;font-size:18px;font-weight:800;letter-spacing:0.5px;">What&rsquo;s Right Is Right.</p>
<p style="margin:0 0 16px 0;color:#E6DEF7;font-size:13px;line-height:1.55;">Family-owned in the Shenandoah Valley since 2014.</p>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="padding:0 6px;"><a href="https://instagram.com/valley_pawn?utm_source=brevo&utm_medium=email&utm_campaign={utm}&utm_content=footer_instagram" style="display:inline-block;padding:10px 16px;font-size:13px;font-weight:700;color:#2D1A5E;background-color:#FFFFFF;border-radius:6px;text-decoration:none;">Follow @valley_pawn</a></td>
<td style="padding:0 6px;"><a href="https://thevalleypawn.com?utm_source=brevo&utm_medium=email&utm_campaign={utm}&utm_content=footer_website" style="display:inline-block;padding:10px 16px;font-size:13px;font-weight:700;color:#2D1A5E;background-color:#F58C8A;border-radius:6px;text-decoration:none;">thevalleypawn.com</a></td>
</tr></table>
<p style="margin:20px 0 0 0;color:#B9AED9;font-size:12px;line-height:1.6;">
Valley Pawn<br>571 James Madison Highway, Culpeper, VA 22701<br>
You&rsquo;re receiving this because you&rsquo;re a Valley Pawn customer.<br>
<a href="{{{{ unsubscribe }}}}" style="color:#B9AED9;text-decoration:underline;">Unsubscribe</a> &middot;
<a href="{{{{ mirror }}}}" style="color:#B9AED9;text-decoration:underline;">View in browser</a>
</p></td></tr>
</table></td></tr></table>
</body></html>"""


def body(pct, urgency):
    return f"""
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Thanks again for entering our giveaway &mdash; we really appreciate you taking a minute to sign up.</p>
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">{urgency} Show this email in any of our five stores and we'll take <strong>{pct}% off</strong> anything you buy &mdash; no minimum, no catch.</p>
"""


TEN = ("10% off in-store this month", "MONTH 1 OF 3", body(10,
    "This month only:"))
TWENTY = ("20% off in-store this month", "MONTH 2 OF 3", body(20,
    "This offer is going up, not down — this month:"))
THIRTY = ("Last call — 30% off in-store", "FINAL MONTH", body(30,
    "Final month of this offer, and it's the best one:"))

today = datetime.date.today()


def add_months(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return datetime.date(y, m, day)


PLAN = [
    (71, None, TEN, today),                # already-created campaign, update in place
    (None, "Giveaway Ladder — 20% (month 2)", TWENTY, add_months(today, 1)),
    (None, "Giveaway Ladder — 30% final (month 3)", THIRTY, add_months(today, 2)),
]

for cid, name, (subject_bit, eyebrow, body_html), send_date in PLAN:
    utm = f"giveaway_ladder_{send_date.isoformat()}"
    html = shell(eyebrow, "Thanks for entering", "A little something for stopping by.",
                 body_html, "Find your nearest store", "https://thevalleypawn.com", utm)
    scheduled_at = f"{send_date.isoformat()}T09:00:00-04:00"
    if cid:
        payload = {"subject": f"Thanks for entering — {subject_bit}", "htmlContent": html}
        if DRY:
            print(f"[dry] update campaign {cid}: {payload['subject']} (already scheduled)")
            continue
        st, res = req("PUT", f"/emailCampaigns/{cid}", payload)
        print(f"campaign {cid} update: {st}")
    else:
        payload = {
            "name": name, "subject": f"Thanks for entering — {subject_bit}",
            "sender": SENDER, "replyTo": REPLY_TO, "htmlContent": html,
            "recipients": {"listIds": [LIST]}, "inlineImageActivation": False,
            "mirrorActive": True,
        }
        if DRY:
            print(f"[dry] create + schedule: {name} for {scheduled_at}")
            continue
        st, res = req("POST", "/emailCampaigns", payload)
        print(f"create '{name}': {st} {res}")
        if st < 300:
            newid = res["id"]
            st2, res2 = req("PUT", f"/emailCampaigns/{newid}", {"scheduledAt": scheduled_at})
            print(f"  schedule {newid} for {scheduled_at}: {st2}")

print("\nDRY RUN — pass --apply" if DRY else "\nDONE")
