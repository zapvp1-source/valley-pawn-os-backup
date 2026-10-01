#!/usr/bin/env python3
"""funds_verification.py [YYYY-MM-DD] [--render] [--no-pull] — native replacement for the Cowork task
`daily-funds-verification` (18:00 daily). Same four steps as its SKILL, no Claude session:

  1 Slack ledger: today's messages in the 5 store funds channels (ops bot token). Joshua's (U03BB52MDSA)
    "sent <amount>" replies are the sends. 6-digit transfer confirmation codes are NOT amounts.
  2 Bravo: one safe-register-journal pull for all 5 stores via bin/bravo_pull.sh (skipped with --no-pull
    when the CSVs are already on disk).
  3 CSV: rows with Txn Type = TENDER TRANSFER, Till Number = BANK, negative Amt Coll = funds received.
  4 Reconcile per store (within $1 = matched), save the markdown report, post to #daily-funds-reconcilation.

Deliberately conservative where the SKILL relied on judgment: if a store's channel mentions not needing
the money after a send ("don't need", "cancel", ...), the store is marked ⚠ Check with the quote — never
silently subtracted. A Joshua message that says "sent" with no parseable amount is also ⚠ Check.
"""
import csv
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "daily-funds-verification"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
REPORTS = os.path.expanduser("~/Documents/Claude/Projects/Daily Funds Verification")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
POST_CH = "C0B3R9B3S8H"   # #daily-funds-reconcilation
JOSHUA = "U03BB52MDSA"
STORES = [("CUL", "Culpeper", "C03BLHFJ3KN", "#pepper-funds"), ("HAR", "Harrisonburg", "C03BWRKEDUZ", "#harrisonburg-funds"),
          ("LEX", "Lexington", "C03B3K5DL6T", "#lex-funds"), ("ROA", "Roanoke", "C063K8E02TW", "#roanoke-funds"),
          ("WAY", "Waynesboro", "C03BLLRN64U", "#boro-funds")]
SENT_RX = re.compile(r"\bsent\b", re.I)
# amounts: "2k", "1.5k", "$2,000", "1500", "800" — but never a bare 6-digit code
AMT_RX = re.compile(r"\$?\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(k|K)?\b")
CANCEL_RX = re.compile(r"don'?t need|do not need|no longer need|not needed|cancel|never mind|nevermind|didn'?t need", re.I)


def api(tok, method, **params):
    req = urllib.request.Request("https://slack.com/api/%s?%s" % (method, urllib.parse.urlencode(params)),
                                 headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=30))


def parse_amount(text):
    """The funds amount in a 'sent ...' message, or None when there is none or more than one candidate
    (ambiguous -> the store is flagged for a look, never guessed). 6-digit codes are excluded."""
    vals = set()
    for num, k in AMT_RX.findall(text.replace("$ ", "$")):
        raw = num.replace(",", "")
        if not k and re.fullmatch(r"\d{6}", raw):
            continue                          # transfer confirmation code, not money
        v = float(raw) * (1000 if k else 1)
        if 20 <= v <= 50000:
            vals.add(v)
    return vals.pop() if len(vals) == 1 else None


def slack_ledger(tok, day):
    start = dt.datetime.combine(day, dt.time(0, 0), ET)
    end = start + dt.timedelta(days=1)
    out = {}
    for code, name, ch, chname in STORES:
        r = api(tok, "conversations.history", channel=ch, oldest=str(start.timestamp()), latest=str(end.timestamp()), limit="200")
        if not r.get("ok"):
            out[code] = {"error": r.get("error"), "sends": [], "cancels": [], "unparsed": []}
            continue
        sends, cancels, unparsed = [], [], []
        first_send_ts = None
        for m in sorted(r.get("messages", []), key=lambda m: float(m.get("ts", 0))):
            text = (m.get("text") or "").strip()
            t = dt.datetime.fromtimestamp(float(m["ts"]), ET).strftime("%-I:%M %p")
            if m.get("user") == JOSHUA and SENT_RX.search(text):
                a = parse_amount(text)
                if a is None:
                    unparsed.append((t, text[:80]))
                else:
                    sends.append((t, a, text[:60]))
                    first_send_ts = first_send_ts or float(m["ts"])
            elif m.get("user") != JOSHUA and first_send_ts and CANCEL_RX.search(text):
                cancels.append((t, text[:100]))
        out[code] = {"sends": sends, "cancels": cancels, "unparsed": unparsed}
    return out


def bravo_received(day):
    """Sum of BANK -> store TENDER TRANSFER negative legs per store. The export has 3 title lines and its
    data columns sit one to the right of the header (verified 9/28-9/29 against the known-good report), so
    cells are matched by VALUE, not by header position: a row counts when it contains 'TENDER TRANSFER'
    and 'BANK' and its last non-empty cell is a negative amount like ($2,000.00). Positive BANK legs
    (store deposits to the bank) are not funds received. De-duplicated on (Txn Num, amount)."""
    got = {}
    for code, *_ in STORES:
        p = os.path.join(BRAVO, "output", "%s_%s_safe-register-journal.csv" % (day.isoformat(), code))
        if not os.path.exists(p):
            got[code] = None
            continue
        total, seen = 0.0, set()
        with open(p, newline="", errors="replace") as fh:
            for row in csv.reader(fh):
                cells = [c.strip() for c in row]
                up = [c.upper() for c in cells]
                if "TENDER TRANSFER" not in up or "BANK" not in up:
                    continue
                vals = [c for c in cells if c]
                amt = vals[-1] if vals else ""
                if not (amt.startswith("(") or amt.startswith("-")):
                    continue
                v = float(re.sub(r"[^\d.]", "", amt) or 0)
                key = (cells[0], v)
                if cells[0] and key in seen:
                    continue
                seen.add(key)
                total += v
        got[code] = (round(total, 2), len(seen))
    return got


def usd(v):
    return "${:,.2f}".format(v)


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    day = dt.date.fromisoformat(args[0]) if args else dt.datetime.now(ET).date()
    # coexistence guard (2026-09-30): while the Cowork task is still enabled it writes the same report
    # file. If today's report already exists and is not marked INCOMPLETE, it has run — stay silent.
    rp = os.path.join(REPORTS, "%s Funds Verification.md" % day.isoformat())
    if not render and "--force" not in sys.argv and os.path.exists(rp) and "INCOMPLETE" not in open(rp, errors="replace").read()[:600]:
        print("report for %s already complete — nothing to do" % day)
        return 0
    tok = vp_slack.token()
    led = slack_ledger(tok, day)
    if not no_pull and not render:
        rc = subprocess.run(["/bin/bash", os.path.join(BIN, "bravo_pull.sh"), "safe-register-journal", day.isoformat(),
                             "CUL,HAR,LEX,ROA,WAY", "daily-funds-verification-%s" % day.strftime("%Y%m%d")],
                            capture_output=True, text=True, timeout=7500).returncode
        if rc != 0:
            print("bravo pull rc=%d — reconciling whatever landed" % rc)
    got = bravo_received(day)
    rows, n_ok, n_bad, n_chk, n_na = [], 0, 0, 0, 0
    total_exp = 0.0
    for code, name, ch, chname in STORES:
        L = led[code]
        exp = sum(a for _, a, _ in L["sends"])
        total_exp += exp
        b = got.get(code)
        notes = []
        if L.get("error"):
            status = "❓ Could not read Slack (%s)" % L["error"]; n_na += 1
        elif b is None:
            status = "❓ Could not verify (no Bravo data)"; n_na += 1
        elif L["cancels"] or L["unparsed"]:
            status = "⚠ Check"; n_chk += 1
            notes += ['store said "%s" at %s' % (q, t) for t, q in L["cancels"]]
            notes += ['"%s" at %s has no readable amount' % (q, t) for t, q in L["unparsed"]]
        elif abs(exp - b[0]) <= 1.0:
            status = "✓ Matched"; n_ok += 1
        else:
            status = "⚠ Discrepancy"; n_bad += 1
        act = usd(b[0]) if b else "—"
        sends = ", ".join("%s %s" % (t, usd(a)) for t, a, _ in L["sends"]) or "none"
        rows.append((code, name, sends, usd(exp), act, status, notes))
    if n_bad or n_chk:
        bottom = "%d store(s) need a look — %d matched, %d discrepancy, %d to check." % (n_bad + n_chk, n_ok, n_bad, n_chk)
    elif n_na:
        bottom = "%d of 5 stores verified; %d could not be verified." % (n_ok, n_na)
    elif total_exp == 0:
        bottom = "No funds activity today — all clear."
    else:
        bottom = "All %d stores matched — every dollar sent is in Bravo." % n_ok
    table = ["| Store | Sent (Slack) | Expected | In Bravo | Status |", "|---|---|---|---|---|"]
    for code, name, sends, exp, act, status, _ in rows:
        table.append("| %s | %s | %s | %s | %s |" % (name, sends, exp, act, status))
    table.append("| **Total** | | **%s** | | **%d/5 verified** |" % (usd(total_exp), n_ok))
    note_lines = ["- %s: %s" % (name, n) for code, name, *_rest in rows for n in _rest[-1]]
    md = "# Daily Funds Verification — %s\n\n**%s**\n\n%s\n%s\n\n_Native run (bin/funds_verification.py)._\n" % (
        day.isoformat(), bottom, "\n".join(table), ("\n" + "\n".join(note_lines)) if note_lines else "")
    post = "*Funds verification — %s*\n%s\n%s%s" % (
        day.strftime("%a %b %-d"), bottom,
        "\n".join("• %s: expected %s, Bravo %s — %s" % (name, exp, act, status) for code, name, sends, exp, act, status, _ in rows),
        ("\n" + "\n".join(note_lines)) if note_lines else "")
    if render:
        print("=== RENDER ONLY ===\n" + md + "\n--- slack ---\n" + post)
        return 0
    os.makedirs(REPORTS, exist_ok=True)
    open(os.path.join(REPORTS, "%s Funds Verification.md" % day.isoformat()), "w").write(md)
    if n_na == 5:
        ledger("Tonight's funds verification could not verify any store (no Bravo data); report saved, nothing posted.")
        return 1
    env = dict(os.environ, VP_TASK=AGENT)
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", POST_CH, post],
                       capture_output=True, text=True, timeout=60, env=env)
    if p.returncode != 0:
        ledger("Tonight's funds verification was built but the Slack post did not go through.")
        return 1
    print("posted:", bottom)
    return 0


if __name__ == "__main__":
    sys.exit(main())
