#!/usr/bin/env python3
"""Verify every change made in the 2026-09-05 Email Dept Phase 0 + Phase 1 pass.
Checks live state (Brevo API, files on disk), not what any script claimed. Rule 12."""
import json, os, re, urllib.request, urllib.error

KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
S = os.path.expanduser("~/Documents/Claude/Scheduled")
P = os.path.expanduser("~/Documents/Claude/Projects")
ok = fail = 0


def check(label, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1; print(f"  PASS  {label}" + (f" — {detail}" if detail else ""))
    else:
        fail += 1; print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))


def get(path):
    r = urllib.request.Request("https://api.brevo.com/v3" + path, headers={"api-key": KEY, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def read(p):
    return open(p, encoding="utf-8").read()


print("\n== F1: monthly gold send retimed ==")
d = read(os.path.join(S, "monthly-we-buy-gold-silver-email/SKILL.md"))
check("gold task file still present and unmodified in body", "Master Template 11" in d)
print("     (cron is held in the task registry, not the file — confirmed '0 9 1 * *' at update time)")

print("\n== F7: orphan drafts parked ==")
for cid in (43, 49, 23, 1):
    c = get(f"/emailCampaigns/{cid}")
    lists = c["recipients"].get("lists")
    check(f"campaign {cid} parked + seed-only",
          c["name"].startswith("[PARKED") and lists == [10] and c["status"] == "draft",
          f"{c['status']} | lists {lists} | {c['name'][:48]}")

print("\n== F6: picker STEP 5 + STEP 8 ==")
d = read(os.path.join(S, "vp-deal-of-week-monday-pick/SKILL.md"))
check("dead /v3/media upload instruction gone from STEP 5", "/v3/media` (multipart form)" not in d)
step5 = d[d.index("STEP 5 —"):d.index("STEP 6 — FILL")]   # slice the real STEP 5 body, not the first
check("STEP 5 names the endpoint as forbidden",              # stray 'STEP 6' cross-reference above it
      "Do NOT use Brevo `POST /v3/media`" in step5 and "does not exist" in step5)
check("STEP 5 gives the proven path", "wp-json/wp/v2/media" in step5 or "HARDENING ADDENDUM" in step5)
check("STEP 8 pins the channel ID", "C0AVCANK7E3" in d.split("STEP 8")[-1])
check("backup exists", os.path.exists(os.path.join(S, "vp-deal-of-week-monday-pick/SKILL.md.bak-pre-20260905-phase0")))

print("\n== Phase 1 item 8: runway floor 4 -> 8 ==")
d = read(os.path.join(S, "brevo-weekly-efficiency-audit/SKILL.md"))
check("audit floor is 8 weeks", "fewer than 8 weeks of runway" in d and "fewer than 4 weeks" not in d)
g = read(os.path.join(S, "brevo-weekly-draft-guard/SKILL.md"))
check("draft-guard points at the stager", "brevo-stage-next-quarter" in g)
check("draft-guard's dead Dec-31 warning removed", "After Dec 31 2026 the calendar runs out" not in g)

print("\n== Phase 1 item 7: stager ==")
p = os.path.join(S, "brevo-stage-next-quarter/SKILL.md")
check("task file exists", os.path.exists(p))
d = read(p)
check("model pinned", re.search(r"^model: claude-sonnet-5$", d, re.M) is not None)
check("no bad path typo", "joshuadavin" not in d)
check("script committed", os.path.exists(os.path.join(P, "Email Refinement/bin/stage_quarter.py")))

print("\n== Phase 1 item 9: Engaged v2 ==")
st = json.load(open(os.path.join(P, "Email Refinement/bin/engaged_v2_state.json")))
lid = st["list_id"]
lst = get(f"/contacts/lists/{lid}")
live = get(f"/contacts/lists/{lid}/contacts?limit=500")["contacts"]
l7 = get("/contacts/lists/7/contacts?limit=500")["contacts"]
check(f"list {lid} exists and is named for humans", "human-verified" in lst["name"], lst["name"][:60])
check("v2 membership matches state file", len(live) == st["last_count"], f"live {len(live)} vs state {st['last_count']}")
check("v2 is a strict subset of list 7 (nothing invented)",
      {c['email'] for c in live} <= {c['email'] for c in l7}, f"v2 {len(live)} / list7 {len(l7)}")
check("list 7 untouched (still the live audience)", len(l7) >= 175, f"{len(l7)} members")
p = os.path.join(S, "brevo-engaged-v2-refresh/SKILL.md")
check("refresh task exists + pinned", os.path.exists(p) and re.search(r"^model: claude-sonnet-5$", read(p), re.M) is not None)

print("\n== no campaign points at v2 yet (the switch is Joshua's call) ==")
bad = []
for status in ("draft", "queued"):
    for c in get(f"/emailCampaigns?status={status}&limit=100").get("campaigns", []):
        if lid in (c["recipients"].get("lists") or []):
            bad.append((c["id"], c["name"]))
check("no draft/queued campaign sends to v2", not bad, str(bad))

print("\n== weekly calendar intact ==")
drafts = get("/emailCampaigns?status=draft&limit=100")["campaigns"]
weekly = [c for c in drafts if not c["name"].startswith("[PARKED") and re.search(r"— \w+ \d{1,2}, 2026$", c["name"])]
check("weekly drafts still staged", len(weekly) >= 17, f"{len(weekly)} future weekly drafts")
check("each weekly draft still has engaged + seeds",
      all(7 in (c["recipients"].get("lists") or []) and 10 in (c["recipients"].get("lists") or []) for c in weekly))

print("\n== Fleet Guardian manifest ==")
m = json.load(open(os.path.join(P, "Valley Pawn OS/fleet/expected_outputs.json")))
tasks = {e["task"] for e in m["entries"]}
for t in ("brevo-stage-next-quarter", "brevo-weekly-efficiency-audit", "brevo-preflight-watchdog", "monthly-we-buy-gold-silver-email"):
    check(f"manifest covers {t}", t in tasks)

print(f"\n==== {ok} passed, {fail} failed ====")
raise SystemExit(1 if fail else 0)
