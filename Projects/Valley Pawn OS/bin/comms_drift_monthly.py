#!/usr/bin/env python3
"""comms_drift_monthly.py [--render] [--asof YYYY-MM-DD] — native `vp-comms-drift-monthly-check`
(3rd of month 08:00 ET; Mac-first wave 3 second pass, 2026-10-20). Read-only audit; ONE DM to Joshua, never a channel.
  1  last 30 days of the 17 team channels, read as the ops bot
  2  only AUTOMATION posts (the ops bot / any bot, or Joshua's account — the Cowork connector posts as Joshua): human
     chat is never judged. Each post is screened IN CODE first (tool/system words, file paths and IDs, "Sent using"
     footers, failure/error wording, > ~150 words) so the model only sees real candidates
  3  bin/vp_ai.py (claude-sonnet-5-5) judges the candidates against FIELD_COMMUNICATION_STANDARD.md, quotes the
     offending line, and names the likely task from fleet/expected_outputs.json (channel id -> task) — read-only
  4  DM, the 10/3 shape: "Comms standard check — <Month Year> (last 30 days, 17 team channels): drift found." + up to 5
     numbered lines "#channel — <issue> (likely: <task>)" + 'Say "fix these" and I'll rewrite the affected task files.'
     or "✅ Comms standard check — <Month Year>: no drift found across the 17 team channels checked."
--render: same reads and model call; the DM goes to fleet/test_output/ only.
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402

TASK = "vp-comms-drift-monthly-check"
STANDARD = os.path.join(L.OS_DIR, "FIELD_COMMUNICATION_STANDARD.md")
EXPECTED = os.path.join(L.OS_DIR, "fleet", "expected_outputs.json")
CHANNELS = {"general": "C03BETSS669", "store-performance": "C03CGTN3KN1", "employee-performance": "C0ATTLPQHR8",
            "loan-review": "C0B08RS2BMK", "layaway-review": "C04N24STDP1", "aged-inventory-review": "C04NGH4FF35",
            "items-to-price": "C0BA5U0GENL", "pawn-walks": "C0B8WR95N31", "jewlery-counts": "C0BM9NHGTT4",
            "bonus-goals": "C04TXF0KGNL", "google-reviews": "C04NDE52U2G", "weekly-returns-summary": "C0B1K4WK2HZ",
            "monthly-gun-audit": "C07CPN020G0", "deal-of-the-week": "C0AVCANK7E3", "company-performance": "C0B26GD8D2R",
            "policy-announcements": "C03BHQ9RLR0", "new-customers": "C0BHF9NM0BH"}
SCREEN = re.compile(r"\b(bravo|cowork|chekkit|gusto|brevo|qbo|quickbooks|publer|pipeline|handler|watchdog|sync|csv|export|"
                    r"claude|bot|automation|script|trigger|deploy|codesign|gatekeeper|error|failed|failure|delayed|retry|"
                    r"verified against|supersedes|pulled automatically|sent using)\b|/Users/|docs\.google|drive\.google|"
                    r"\btrig_|\.json\b|\.py\b|\.md\b", re.I)
SYSTEM = ("You audit Valley Pawn's team-facing Slack posts against its Field Communication Standard. Be specific and "
          "fair: quote the exact offending words. A post that a store clerk can read and act on, in plain language, "
          "is fine even if long-ish. Group repeats of the same issue into one finding.")
PROMPT = """THE STANDARD:
{standard}

CHANNEL -> TASKS THAT POST THERE (for the 'likely' attribution; read-only):
{tasks}

CANDIDATE AUTOMATION POSTS from the last 30 days (each: channel, date, why it was screened, text):
{posts}

Return ONLY JSON: {{"findings": [{{"channel": "<name without #>", "issue": "<one line, quoting the offending words>",
"likely": "<task id(s) separated by ' / ', or 'shared template issue, not one task'>", "severity": <1-10>}}]}}
Each "issue" is ONE line of at most ~170 characters with a short quote (a few words) of the offending text. "likely" must be a task id from the map, "shared template issue, not one task", or "unknown".
At most 8 findings, worst first. An empty list is correct when nothing breaks the standard."""


def is_automation(m):
    """The ops bot / any bot, or a post Claude made through Joshua's account (it carries the connector's "Sent using"
    footer or an app id). Joshua typing in a channel himself is human chat and is never judged."""
    if m.get("bot_id") or m.get("subtype") == "bot_message":
        return True
    return m.get("user") == L.JOSHUA and (bool(m.get("app_id")) or "Sent using" in L.text_of(m))


def main():
    render = "--render" in sys.argv
    asof = dt.date.fromisoformat(sys.argv[sys.argv.index("--asof") + 1]) if "--asof" in sys.argv else L.now().date()
    label = asof.strftime("%B %Y")
    oldest, latest = L.ts_of(asof - dt.timedelta(days=30)), L.ts_of(asof, end=True)
    tasks = {}
    for e in json.load(open(EXPECTED)).get("entries", []):
        if e.get("channel_id"):
            tasks.setdefault(e["channel_id"], set()).add(e["task"])
    cands, read = [], 0
    for name, ch in CHANNELS.items():
        try:
            msgs = L.history(ch, oldest, latest)
        except RuntimeError as e:
            print("unreadable", name, e)
            continue
        read += 1
        for m in msgs:
            if not is_automation(m):
                continue
            t = L.text_of(m)
            words = len(t.split())
            hits = sorted({h.group(0).lower() for h in SCREEN.finditer(t)})
            if hits or words > 150:
                why = ", ".join(hits[:6]) + (" ; %d words" % words if words > 150 else "")
                cands.append("#%s | %s | %s\n%s" % (name, dt.datetime.fromtimestamp(float(m["ts"]), L.ET).date(), why, t[:1200]))
    tmap = "\n".join("#%s: %s" % (n, ", ".join(sorted(tasks.get(c, [])) or ["(none listed)"])) for n, c in CHANNELS.items())
    findings = []
    if cands:
        out = L.ask_json(PROMPT.format(standard=open(STANDARD).read()[:30000], tasks=tmap, posts="\n\n".join(cands)[:120000]),
                         system=SYSTEM, max_tokens=8000)
        findings = sorted(out.get("findings") or [], key=lambda f: -int(f.get("severity") or 0))[:5]
    if findings:
        lines = ["Comms standard check — %s (last 30 days, %d team channels): drift found." % (label, read), ""]
        for i, f in enumerate(findings, 1):
            lines.append("%d. #%s — %s (likely: %s)" % (i, f["channel"].lstrip("#"), f["issue"].rstrip("."), f.get("likely") or "unknown"))
        lines += ["", 'Say "fix these" and I\'ll rewrite the affected task files.']
        text = "\n".join(lines)
    else:
        text = "✅ Comms standard check — %s: no drift found across the %d team channels checked." % (label, read)
    print("screened candidates:", len(cands))
    ok = L.post(TASK, L.JOSHUA, text, render, label="joshua")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
