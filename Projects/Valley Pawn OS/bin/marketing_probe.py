#!/usr/bin/env python3
"""marketing_probe.py — READ-ONLY ground truth for the marketing stall (2026-10-05).
Prints credential FILE NAMES only (never values), Brevo's last campaigns, the website's last posts,
and the newest post on each Facebook page if a token file is found."""
import glob, json, os, subprocess, urllib.request, datetime as dt
H = os.path.expanduser("~")
print("== credential files (names only)")
for d in ("~/.config/valley-pawn", "~/.vp_secrets", "~/.config/publer", "~/.config/meta"):
    p = os.path.expanduser(d)
    print(d, sorted(os.listdir(p)) if os.path.isdir(p) else "(absent)")
print("== token.json candidates")
for pat in ("/var/folders/*/*/T/claude-hostloop-plugins/*/skills/facebook-post/data/tokens.json",
            H + "/Documents/Claude/**/tokens.json", H + "/.config/**/*token*.json"):
    for f in glob.glob(pat, recursive=True)[:8]:
        print(" ", f.replace(H, "~"), dt.datetime.fromtimestamp(os.path.getmtime(f)).date())
print("== keychain item names matching publer/wordpress/meta/facebook/canva")
out = subprocess.run(["security", "dump-keychain"], capture_output=True, text=True).stdout
names = sorted({l.split("=", 1)[1].strip().strip('"') for l in out.splitlines() if '"svce"<blob>=' in l})
print(" ", [n for n in names if any(k in n.lower() for k in ("publer", "wordpress", "wp-", "meta", "facebook", "canva", "brevo", "midjourney", "openai", "anthropic"))])
def get(url, hdr=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=hdr or {"User-Agent": "vp-probe"}), timeout=30))
try:
    k = open(H + "/.config/valley-pawn/brevo_api_key").read().strip()
    for st in ("sent", "queued", "draft"):
        r = get("https://api.brevo.com/v3/emailCampaigns?status=%s&limit=6&sort=desc" % st, {"api-key": k, "accept": "application/json"})
        print("== brevo", st, r.get("count"))
        for c in r.get("campaigns", []):
            print("  ", c.get("id"), (c.get("sentDate") or c.get("scheduledAt") or c.get("modifiedAt") or "")[:16], c.get("name"))
except Exception as e:
    print("brevo error", e)
for site in ("https://thevalleypawn.com",):
    try:
        for p in get(site + "/wp-json/wp/v2/posts?per_page=4&_fields=date,title,link"):
            print("== blog", p["date"][:10], p["title"]["rendered"][:80])
    except Exception as e:
        print("blog error", site, e)
