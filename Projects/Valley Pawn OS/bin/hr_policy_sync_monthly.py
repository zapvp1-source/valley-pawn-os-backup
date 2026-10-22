#!/usr/bin/env python3
"""hr_policy_sync_monthly.py [--render] [--since YYYY-MM-DD] [--until YYYY-MM-DD] — native `vp-hr-policy-monthly-sync`
(1st of month 08:35 ET; Mac-first wave 3 second pass, 2026-10-20). Internal document hygiene; ONE DM to Joshua only.
  1  #policy-announcements (C03BHQ9RLR0), read as the ops bot, since the last native run
     (fleet/state/hr_policy_sync.json; first run: since 2026-08-01 — the 10/1 cloud run checked "back through early August")
  2  the governing text = Human Resources/Ask_Handbook/SOURCES_CURRENT.md (the auto-built full text of the CURRENT
     P&P Manual + Employee Handbook — the 10/1 cloud run re-pointed this check at the real manual, which superseded the
     old running Google Doc list on 9/23)
  3  bin/vp_ai.py (claude-sonnet-5-5): which announcements are new/changed policies, and is each already captured
  4  operational gaps -> a ready-to-insert numbered entry (title, effective date, policy text, source, legacy P&P
     section from the 11-section taxonomy) written to Human Resources/POLICY_SYNC_PENDING_<YYYY-MM>.md for review.
     NOTE (deliberate deviation): the SKILL's "append to the Google Doc" step has no Mac path (the token has no Docs/
     Drive scope, and the live manual is a .docx) — drafted entries stay reviewable in that file, nothing is edited.
     HR/employment-law items (pay, leave, benefits, discrimination, accommodation, discipline) are flagged only.
  5  DM in the 10/1 shape: "Monthly policy-sync check for <Month> — nothing new to add this month." + the plain
     explanation, or what was found / drafted / needs Handbook + legal follow-up. Never "attorney-approved".
--render: same reads + model call, the DM and the pending file go to fleet/test_output/ only; state not advanced.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "vp-hr-policy-monthly-sync"
CH = "C03BHQ9RLR0"
HR = os.path.join(L.PROJ, "Human Resources")
SOURCES = os.path.join(HR, "Ask_Handbook", "SOURCES_CURRENT.md")
STATE = os.path.join(L.OS_DIR, "fleet", "state", "hr_policy_sync.json")
SYSTEM = ("You keep Valley Pawn's written policies in step with what is announced in Slack. You compare carefully and "
          "never claim a policy is missing if the manual covers the same rule in different words. You never present "
          "drafted language as attorney-approved.")
PROMPT = """GOVERNING DOCUMENTS (current P&P Manual + Employee Handbook, full text):
{sources}

#policy-announcements messages since {since} (oldest first; date, author, text):
{msgs}

For every message that announces a NEW or CHANGED policy, procedure, protocol or requirement, decide whether the governing
documents already capture it. Return ONLY JSON:
{{"policies": [{{"title": "...", "announced": "YYYY-MM-DD", "author": "...", "captured": true/false,
  "where": "<section of the manual that covers it, if captured>", "kind": "operational" | "hr_legal",
  "draft": {{"number_hint": "<next P&P number if you can tell>", "effective": "YYYY-MM-DD", "text": "<2-6 sentence policy text>",
             "legacy_section": "<one of: Employee Administration, Funds Control, Administrative Office Duties, Screening & Qualifying, Customer Transactions, Merchandising, Marketing, Collections, Legal Information, Safety & Security>"}} or null}}],
 "manual_version": "<the version string of the P&P Manual above>", "manual_updated": "<its last-updated date>"}}"""
DM = """Write Joshua's monthly policy-sync DM for {month}. Plain language, short, no file paths, no system names.
Reference — last month's real DM (match its tone and length):
---
Monthly policy-sync check for October — nothing new to add this month.

Checked policy announcements back through early August. The three policies from that stretch (gold scrap bucket naming, jewelry category standard, store email password policy) are all already captured in the current Policies & Procedures Manual (v2026.8). Nothing has been announced as a new policy since the manual was consolidated on 9/23.
---
Facts for this run (use only these):
checked since: {since}; manual: {ver} (updated {upd})
policies found: {found}
If something is not captured: say what was drafted for review (operational) and what needs Handbook integration + legal review (HR/employment-law). If nothing new: the one-line headline + one or two sentences of what was checked.
Return ONLY the DM text."""


def main():
    render = "--render" in sys.argv
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else st.get("last_run", "2026-08-01")
    month = L.now().strftime("%B")
    until = sys.argv[sys.argv.index("--until") + 1] if "--until" in sys.argv else None   # parity renders only
    if until:
        month = dt.date.fromisoformat(until).strftime("%B")
    msgs = L.history(CH, L.ts_of(dt.date.fromisoformat(since)), L.ts_of(dt.date.fromisoformat(until), end=True) if until else "%.6f" % L.now().timestamp())
    names = L.users()
    blob = "\n\n".join("[%s] %s: %s" % (dt.datetime.fromtimestamp(float(m["ts"]), L.ET).date(), names.get(m.get("user"), m.get("user") or "bot"),
                                        L.text_of(m)[:3000]) for m in msgs if L.text_of(m).strip())
    found = []
    ver = upd = ""
    if blob:
        out = L.ask_json(PROMPT.format(sources=open(SOURCES).read(), since=since, msgs=blob[:60000]), system=SYSTEM, max_tokens=9000)
        found = out.get("policies") or []
        ver, upd = out.get("manual_version", ""), out.get("manual_updated", "")
    gaps = [p for p in found if not p.get("captured")]
    if gaps:
        lines = ["# Policy sync — drafted entries for review (%s)" % L.now().strftime("%Y-%m-%d"), "",
                 "Drafted by the native vp-hr-policy-monthly-sync check from #policy-announcements. NOT attorney-reviewed. "
                 "Nothing has been inserted into the manual or the handbook.", ""]
        for p in gaps:
            d = p.get("draft") or {}
            lines += ["## %s (%s, announced %s by %s)" % (p["title"], "HR / employment law — Handbook + legal review" if p.get("kind") == "hr_legal" else "operational",
                                                          p.get("announced"), p.get("author")),
                      "- Effective: %s" % d.get("effective", "?"), "- Legacy P&P section: %s" % d.get("legacy_section", "?"),
                      "- Number hint: %s" % d.get("number_hint", "?"), "", d.get("text", ""), ""]
        pend = os.path.join(L.TEST_OUT if render else HR, "POLICY_SYNC_PENDING_%s.md" % L.now().strftime("%Y-%m"))
        os.makedirs(os.path.dirname(pend), exist_ok=True)
        open(pend, "w").write("\n".join(lines))
        print("pending file:", pend)
    facts = json.dumps([{k: p.get(k) for k in ("title", "announced", "captured", "where", "kind")} for p in found])
    text = L.ask(DM.format(month=month, since=since, ver=ver or "current", upd=upd or "?", found=facts or "none"), max_tokens=3000).strip()
    ok = L.post(TASK, L.JOSHUA, text, render, label="joshua")
    if ok is True and not render:   # 'DRYRUN' (publish guard) never advances the since-date
        json.dump({"last_run": L.now().date().isoformat()}, open(STATE, "w"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
