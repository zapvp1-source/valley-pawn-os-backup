#!/usr/bin/env python3
"""winback_texts.py [--send] — native forfeiture-winback-texts-weekly (Thu 10:33, 2026-10-05).

Same program Joshua approved 2026-09-30, sent through Chekkit's API instead of its website:
  1 newest Email Refinement/forfeiture_winback/runs/<RUN>/chekkit_<Store>.csv (built Sundays by the native
    com.valleypawn.forfeiture-winback from verified Bravo data; last row = Joshua's confirmation copy)
  2 drop every phone already in ANY runs/*/chekkit_sent_<Store>.txt — nobody is ever texted twice
  3 POST https://api.chekkit.io/v1/messages {phone, name, message} with that store's token (Keychain
    vp-chekkit-token-<CODE>), the approved text verbatim with only the town changed; Joshua's copy is sent too.
    <= 1 request/second/token. A rejected number (opted out, landline, invalid) is skipped, never retried.
  4 append each successfully texted customer phone to runs/<RUN>/chekkit_sent_<Store>.txt immediately (crash-safe)
  5 one success post to #chekkit-updates in the SKILL's format
Default is a PREVIEW (counts + masked examples; nothing sent)."""
import csv, datetime as dt, glob, json, os, re, subprocess, sys, time, urllib.error, urllib.request
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "forfeiture-winback-texts-weekly"
ET = ZoneInfo("America/New_York")
RUNS = os.path.expanduser("~/Documents/Claude/Projects/Email Refinement/forfeiture_winback/runs")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
CH = "C0B0FQZ4FS8"
JOSH = "8049304221"
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]
MSG = ("Hi from Valley Pawn in {TOWN}! Pawn loans are different: your credit is always good with us, and you're always "
       "approved for another loan. Just bring in something of value. Gold & silver get the most! Stop by anytime or text us right here.")


def p10(s):
    d = re.sub(r"\D", "", s or "")
    d = d[1:] if len(d) == 11 and d.startswith("1") else d
    return d if len(d) == 10 else None


def token(code):
    return subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"], capture_output=True, text=True).stdout.strip()


def text(tok, body):
    req = urllib.request.Request("https://api.chekkit.io/v1/messages", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    for _ in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, ""
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 5)); continue
            return e.code, e.read().decode()[:160]
        except Exception as e:
            time.sleep(3); err = str(e)[:120]
    return 0, err


def main():
    send = "--send" in sys.argv
    runs = sorted(d for d in glob.glob(os.path.join(RUNS, "20??-??-??")) if os.path.isdir(d))
    if not runs:
        print("no runs"); return 1
    run = runs[-1]
    res, ex, notes = {}, {}, []
    for code, town in STORES:
        f = os.path.join(run, "chekkit_%s.csv" % town)
        if not os.path.exists(f):
            notes.append("%s: no list" % town); continue
        done = set()
        for s in glob.glob(os.path.join(RUNS, "*", "chekkit_sent_%s.txt" % town)):
            done |= {l.strip() for l in open(s) if l.strip()}
        todo, seen = [], set()
        for r in csv.DictReader(open(f, newline="", errors="replace")):
            p = p10(r.get("Phone"))
            if not p or p == JOSH or p in done or p in seen:
                continue
            seen.add(p)
            todo.append({"phone": p, "name": (r.get("First Name") or "").strip()})
        ex[town] = ["%s ...%s" % ((b["name"].split() or ["?"])[0], b["phone"][-4:]) for b in todo[:2]]
        c = {"to_text": len(todo), "texted": 0, "rejected": 0}
        if send and todo:
            tok = token(code)
            if not tok:
                notes.append("%s: no Chekkit key" % town); continue
            msg = MSG.replace("{TOWN}", town)
            sent_file = os.path.join(run, "chekkit_sent_%s.txt" % town)
            for b in todo:
                st, err = text(tok, {"phone": b["phone"], "name": b["name"] or "Valley Pawn customer", "message": msg})
                if 200 <= st < 300:
                    c["texted"] += 1
                    with open(sent_file, "a") as fh:
                        fh.write(b["phone"] + "\n")
                else:
                    c["rejected"] += 1
                time.sleep(1.1)
            text(tok, {"phone": JOSH, "name": "Joshua Davis", "message": msg})   # Joshua's confirmation copy
        res[town] = c
    print("run %s | %s" % (os.path.basename(run), "SEND" if send else "PREVIEW (nothing sent)"))
    for t, c in res.items():
        print("  %-13s %s  e.g. %s" % (t, json.dumps(c), ", ".join(ex.get(t, []))))
    for n in notes:
        print("  " + n)
    if not send:
        return 0
    total = sum(c["texted"] for c in res.values())
    if total:
        os.environ["VP_TASK"] = AGENT
        vp_slack.post(CH, "Win-back texts sent (customers who forfeited a loan and haven't been back)\n" +
                      "\n".join("• %s: %d" % (t, res[t]["texted"]) for _, t in STORES if t in res) + "\nTotal: %d" % total)
    rej = sum(c["rejected"] for c in res.values())
    if rej:
        with open(LEDGER, "a") as fh:
            fh.write("| %s (native) | %s | %d win-back numbers were not accepted by Chekkit (opted out, landline or invalid) and were skipped. | NEEDS_HUMAN: no | OPEN |\n"
                     % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, rej))
    return 0


if __name__ == "__main__":
    sys.exit(main())
