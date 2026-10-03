#!/usr/bin/env python3
"""bravo_request.py <YYYY-MM> — email Bravo's marketing team this month's PUSH request (MobilePawn app users).
Text goes through Chekkit (scheduled task ebay-campaign-chekkit-monthly); Joshua 2026-10-02: no Parallels,
so Bravo sends the push for us instead of us driving Bravo's screen.
Sent through Brevo transactional email from hello@thevalleypawn.com, reply-to Joshua, Joshua cc'd.
Gated by config.json bravo_request_enabled. Idempotent: writes packs/<m>/bravo_request_sent.json."""
import json, os, sys, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
m = sys.argv[1]
cfg = json.load(open(os.path.join(HERE, "config.json")))
pack = os.path.join(HERE, "packs", m)
marker = os.path.join(pack, "bravo_request_sent.json")
if not cfg.get("bravo_request_enabled"):
    print("bravo request: disabled in config.json"); sys.exit(0)
if os.path.exists(marker):
    print("bravo request: already sent"); sys.exit(0)
push = open(os.path.join(pack, "push.txt")).read().strip()
body = f"""Hi Tahoe,

Could you schedule this month's MobilePawn push notification for all five Valley Pawn stores, to all of our app users? Details below.

{push}

Push only, please (we handle texts separately). Please reply to confirm once it's scheduled. Thank you!

Joshua Davis
Valley Pawn"""
key = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
payload = {"sender": {"name": "Joshua Davis — Valley Pawn", "email": "hello@thevalleypawn.com"},
           "replyTo": {"email": "jdavis@fcfpawn.com", "name": "Joshua Davis"},
           "to": cfg["bravo_to"], "cc": cfg["bravo_cc"],
           "subject": f"Valley Pawn — MobilePawn push request for {m}", "textContent": body}
r = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=json.dumps(payload).encode(),
                           method="POST", headers={"api-key": key, "Content-Type": "application/json",
                                                   "Accept": "application/json"})
try:
    with urllib.request.urlopen(r, timeout=60) as resp:
        res = json.loads(resp.read() or b"{}")
except urllib.error.HTTPError as e:
    print("bravo request FAILED:", e.code, e.read().decode()); sys.exit(1)
json.dump({"messageId": res.get("messageId"), "to": cfg["bravo_to"]}, open(marker, "w"), indent=1)
print("bravo request sent:", res.get("messageId"))
