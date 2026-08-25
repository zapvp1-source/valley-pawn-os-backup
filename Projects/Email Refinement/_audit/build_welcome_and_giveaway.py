#!/usr/bin/env python3
"""Two builds:

1. WELCOME — Brevo's drag-and-drop Automation workflow builder has no public
   creation API (GET /automation/workflows returns 404) and there's no saved
   browser session for app.brevo.com or admin.google.com to build it by hand.
   Transactional email works entirely through the API though, so this uses
   that instead: a reusable transactional template + a new WELCOMED boolean
   attribute. A companion scheduled task (created separately) finds contacts
   created in the last 24h without WELCOMED=true, sends the transactional
   email, and flags them. Functionally equivalent to the automation, fully
   API-driven, no browser login required.

2. GIVEAWAY FOLLOW-UP — 82 clean giveaway entrants (list 6), zero follow-up
   since July. Stage a real campaign now.
"""
import json, urllib.request, os, time, sys

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
BASE = "https://api.brevo.com/v3"
DRY = "--apply" not in sys.argv
SENDER = {"name": "Valley Pawn", "email": "hello@thevalleypawn.com"}
REPLY_TO = "jdavis@fcfpawn.com"


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


# ---------------------------------------------------------------- shared shell
# Reuses the locked structure from the production master template (logo,
# hero band, trust strip, primary CTA, footer) — no store directory here,
# these are single-purpose one-off sends, not the weekly.
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


WELCOME_BODY = """
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Thanks for connecting with Valley Pawn. We're a family-owned shop with five stores across the Shenandoah Valley, and we do three things: buy your gold and valuables for a fair price, loan against almost anything, and sell quality used gear for less than retail.</p>
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">No pressure, no appointment needed &mdash; just walk into whichever store is closest and someone will take care of you.</p>
"""

GIVEAWAY_BODY = """
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Thanks again for entering our giveaway &mdash; we had a great turnout and really appreciate you taking a minute to sign up.</p>
<p style="margin:0 0 14px 0;font-size:16px;line-height:1.6;color:#1a1a1a;">Whether or not your name got pulled this time, we'd love to actually meet you. Stop by any of our five stores &mdash; we're always adding new arrivals, and we buy gold, silver, and just about anything of value if you're looking to sell.</p>
"""


def build_and_send_giveaway():
    html = shell("THANKS FOR ENTERING", "You're in good company",
                 "82 people entered our giveaway — here's a little something for stopping by.",
                 GIVEAWAY_BODY, "Find your nearest store", "https://thevalleypawn.com",
                 "giveaway_followup_2026-08")
    payload = {
        "name": f"Giveaway Follow-Up — {os.popen('date +%Y-%m-%d').read().strip()}",
        "subject": "Thanks for entering — here's 10% off just for stopping by",
        "sender": SENDER, "replyTo": REPLY_TO, "htmlContent": html,
        "recipients": {"listIds": [6]},
        "inlineImageActivation": False, "mirrorActive": True,
    }
    if DRY:
        print("[dry] giveaway campaign:", payload["name"], "|", payload["subject"])
        return
    st, res = req("POST", "/emailCampaigns", payload)
    print("giveaway campaign create:", st, res)


def build_welcome_template():
    html = shell("WELCOME", "Good to have you",
                 "One place for gold, loans, and quality used gear — five stores across the Valley.",
                 WELCOME_BODY, "See what's in stock", "https://thevalleypawn.com",
                 "welcome_transactional")
    payload = {
        "templateName": "Welcome — transactional (API-triggered)",
        "subject": "Welcome to Valley Pawn",
        "sender": SENDER, "replyTo": REPLY_TO, "htmlContent": html,
        "isActive": True,
    }
    if DRY:
        print("[dry] welcome template:", payload["templateName"])
        return None
    st, res = req("POST", "/smtp/templates", payload)
    print("welcome template create:", st, res)
    return res.get("id") if st < 300 else None


def ensure_welcomed_attribute():
    if DRY:
        print("[dry] would ensure WELCOMED boolean attribute exists")
        return
    st, res = req("POST", "/contacts/attributes/normal/WELCOMED", {"type": "boolean"})
    print("WELCOMED attribute:", st, res if st >= 300 else "OK (or already existed)")


if __name__ == "__main__":
    print("=== Giveaway follow-up ===")
    build_and_send_giveaway()
    print("\n=== Welcome transactional template ===")
    tid = build_welcome_template()
    print("template id:", tid)
    print("\n=== WELCOMED attribute ===")
    ensure_welcomed_attribute()
    print("\nDRY RUN — pass --apply" if DRY else "\nDONE")
