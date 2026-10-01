#!/usr/bin/env python3
"""bot_identity.py — who does the ops bot token post as? (auth.test + users.info). Read-only."""
import json, os, sys, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack
tok = vp_slack.token()
def api(m, **p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://slack.com/api/%s?%s" % (m, urllib.parse.urlencode(p)), headers={"Authorization": "Bearer " + tok}), timeout=20))
a = api("auth.test"); print("auth.test:", {k: a.get(k) for k in ("user", "user_id", "bot_id", "team")})
u = api("users.info", user=a.get("user_id")).get("user", {}); p = u.get("profile", {})
print("display:", p.get("display_name"), "| real:", p.get("real_name"), "| bot app name:", u.get("name"))
for uid in ("U0BLQTHLUTA",):
    x = api("users.info", user=uid).get("user", {}); print(uid, "->", x.get("profile", {}).get("real_name"), "/", x.get("name"))
