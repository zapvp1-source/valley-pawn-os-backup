#!/usr/bin/env python3
"""read-only: Brevo contact attribute names/types + list names (to find how 'monthly' tagging was stored)."""
import json, os, urllib.request
K = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
g = lambda p: json.load(urllib.request.urlopen(urllib.request.Request("https://api.brevo.com/v3" + p, headers={"api-key": K}), timeout=60))
print([(a["name"], a.get("type"), a.get("category")) for a in g("/contacts/attributes")["attributes"]])
print([(l["id"], l["name"], l.get("uniqueSubscribers") or l.get("totalSubscribers")) for l in g("/contacts/lists?limit=50")["lists"]])
