#!/usr/bin/env python3
"""entity_compliance_monthly.py [--render] [--asof YYYY-MM-DD] — native `entity-compliance-check`
(1st of month 09:00 ET; Mac-first wave 3 second pass, 2026-10-20). DM to Joshua ONLY when something needs action.
  1  Life OS/ENTITY_COMPLIANCE_CALENDAR.md is the authority for deadlines
  2  evidence that something already happened (Rule 12 — verify against output): Unified Search (local index of Apple
     Mail + iMessage + iCloud) for confirmations from scc.virginia.gov, tnsos.gov, fisgov.com, northwestregisteredagent.com
     and the county treasurers / tax offices, last 150 days; plus the Life OS/OPEN_ITEMS_REGISTER.md lines that mention
     an entity, property tax, registered agent or annual report
  3  bin/vp_ai.py (claude-sonnet-5-5) builds the 90-day lookahead from those two inputs ONLY (unverified dates stay a
     verification task, never a date), drops anything the evidence shows done, and lists newly-confirmed filings
  4  newly-confirmed filings are APPENDED to the calendar under "## Native check log" (backup first; never overwrites)
  5  nothing due and nothing to verify = silence. Otherwise ONE plain DM in the 10/1 shape:
     "Monthly entity check — coming up in the next 90 days:" + "• _<item>_ — due _<date>_. <one action>" lines
     (+ an "Already done:" line when the evidence closed something)
--render: same reads + model call, the DM to fleet/test_output/, the calendar untouched.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "entity-compliance-check"
CAL = os.path.join(L.PROJ, "Life OS", "ENTITY_COMPLIANCE_CALENDAR.md")
OIR = os.path.join(L.PROJ, "Life OS", "OPEN_ITEMS_REGISTER.md")
USEARCH = os.path.join(L.PROJ, "Unified Search", "usearch.py")
SEARCHES = [("annual report", "scc.virginia.gov"), ("registration fee", "scc.virginia.gov"), ("annual report", "tnsos"),
            ("registered agent", "northwestregisteredagent.com"), ("renewal", "northwestregisteredagent.com"),
            ("property tax", None), ("real estate tax", None), ("Chesterfield", None), ("Augusta County", None),
            ("Staunton", None), ("Roane County", None), ("St. Johns County tax", None), ("tax return", "silverline")]
OIR_RX = re.compile(r"(entity|property tax|real estate tax|registered agent|annual report|SCC|tnsos|Farming Infinity|Northwest)", re.I)
SYSTEM = ("You run Joshua Davis's monthly entity-compliance check. The calendar file is the authority for deadlines. "
          "Evidence (emails/texts/open items) can only CLOSE an item, never invent a date. Be concise and concrete.")
PROMPT = """TODAY: {today}. Lookahead window: {today} through {end} (90 days).

ENTITY COMPLIANCE CALENDAR (authority):
{cal}

EVIDENCE — local mail/message search hits (newest first; title | from | date | snippet):
{ev}

OPEN ITEMS REGISTER lines that mention entities / property tax / registered agents:
{oir}

Return ONLY JSON:
{{"due": [{{"item": "<entity or property + what>", "due": "<Mon D, or 'by <date>'>", "action": "<the one action that closes it>",
           "already_done_evidence": "<quote if the evidence shows it done, else empty>"}}],
 "verify": [{{"item": "...", "action": "..."}}],
 "already_done": ["<one short line per item the evidence shows filed/paid, with date>"],
 "newly_confirmed": [{{"entity": "...", "what": "...", "date": "YYYY-MM-DD", "confirmation": "...", "amount": "..."}}]}}
Only include in "due" what falls inside the window and is NOT shown done. "newly_confirmed" = filings proven by the evidence
that the calendar file does not already record."""
DM = """Write Joshua's monthly entity-check Slack DM from these facts. Use exactly this shape (Slack mrkdwn, plain words, no file paths):
Monthly entity check — coming up in the next 90 days:

• _<item>_ — due _<date>_. <action>
...
Already done: <one sentence, only if any>
Reference (last month's real DM):
Monthly entity check — coming up in the next 90 days:

• _Woods Walk (Chesterfield County) property tax_ — 2nd half due _Mon Dec 7_. Chesterfield cancelled all old autopays on 7/31, so set up a new Scheduled Payment in their payment portal.
• _Farming Infinity Tennessee LLC_ — confirm who its Tennessee registered agent is.
Already done: Full Circle Finance's Virginia annual report was filed and the fee paid in July. Next one is due June 30, 2027.

Rules: one bullet per item, at most two short sentences each (what is due + the one action). Verification items are their own
short bullets ("confirm ..."). Never mention searches, evidence, data, or what could not be checked. Leave out anything that is
only "probably fine" or speculative. At most 8 bullets.
FACTS: {facts}
Return ONLY the DM text."""


def evidence(today):
    since = (today - dt.timedelta(days=150)).isoformat()
    hits = []
    for q, frm in SEARCHES:
        cmd = ["/usr/bin/python3", USEARCH, "query", q, "--since", since, "--until", today.isoformat(), "-n", "6", "--json"]
        if frm:
            cmd += ["--from", frm]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            for h in json.loads(r.stdout or "[]"):
                hits.append("%s | %s | %s | %s" % (h.get("title"), h.get("who"), dt.datetime.fromtimestamp(h.get("ts") or 0).date(),
                                                   (h.get("snippet") or "").replace("\n", " ")[:300]))
        except Exception as e:
            hits.append("(search %r failed: %s)" % (q, type(e).__name__))
    return list(dict.fromkeys(hits))


def main():
    render = "--render" in sys.argv
    today = dt.date.fromisoformat(sys.argv[sys.argv.index("--asof") + 1]) if "--asof" in sys.argv else L.now().date()
    cal = open(CAL).read()
    oir = [l.strip()[:400] for l in open(OIR, errors="ignore") if OIR_RX.search(l)][-80:]
    ev = evidence(today)
    out = L.ask_json(PROMPT.format(today=today, end=today + dt.timedelta(days=90), cal=cal, ev="\n".join(ev)[:40000],
                                   oir="\n".join(oir)[:20000]), system=SYSTEM, max_tokens=7000)
    due = [d for d in out.get("due") or [] if not d.get("already_done_evidence")]
    ver = out.get("verify") or []
    conf = out.get("newly_confirmed") or []
    if conf and not render:
        shutil.copy2(CAL, CAL + ".bak-native-%s" % today.strftime("%Y%m%d"))
        with open(CAL, "a") as f:
            if "## Native check log" not in cal:
                f.write("\n\n## Native check log\n")
            for c in conf:
                f.write("- %s (found by the native monthly check %s): %s — %s, %s, confirmation %s\n"
                        % (c.get("date"), today, c.get("entity"), c.get("what"), c.get("amount") or "amount n/a", c.get("confirmation") or "n/a"))
    print("due:", json.dumps(due, indent=1), "\nverify:", json.dumps(ver), "\nconfirmed:", json.dumps(conf))
    if not due and not ver:
        print("nothing due in 90 days and nothing to verify — silent (correct output)")
        return 0
    text = L.ask(DM.format(facts=json.dumps({"due": due, "verify": ver, "already_done": out.get("already_done") or []})),
                 max_tokens=3000).strip()
    return 0 if L.post(TASK, L.JOSHUA, text, render, label="joshua") else 1


if __name__ == "__main__":
    sys.exit(main())
