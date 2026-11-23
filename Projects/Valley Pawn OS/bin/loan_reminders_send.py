#!/usr/bin/env python3
"""loan_reminders_send.py -- 9:15 AM sender for the loan / layaway reminder texts (built 2026-11-21, OFF by default).
A store sends ONLY when ALL of these hold; otherwise it sends nothing that day and says why in the agent log:
  1. LIVE file exists: fleet/state/loan_reminders_live/<STORE>   (created only on Joshua's go; delete = off)
  2. last night's plan exists: Loan Reminder Texts/trial/<today>/plan_<STORE>.csv
  3. send_window_ok(): the Bravo list was pulled after the stores closed last night AND it is before 9:45 AM
     (no store is open in between, so nothing on the list can have been paid at a counter or by phone)
  4. every text is 160 characters or less and the store's plan is not larger than MAX_PER_DAY (runaway guard)
Each phone gets at most one text per kind per day; results -> trial/<today>/sent_<STORE>.csv. No Slack.
--dry prints what would happen for every store, LIVE file or not, and sends nothing."""
import csv, datetime as dt, json, os, subprocess, sys, time, urllib.error, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
LR = os.path.join(PROJ, "Loan Reminder Texts")
sys.path.insert(0, LR)
import loan_reminders_plan as lp
LIVE = os.path.join(os.path.dirname(HERE), "fleet", "state", "loan_reminders_live")
MAX_PER_DAY = 250


def token(code):
    return subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"], capture_output=True, text=True).stdout.strip()


def text(tok, body):
    req = urllib.request.Request("https://api.chekkit.io/v1/messages", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json", "User-Agent": "ValleyPawnOps/1.0"})
    err = ""
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
    dry = "--dry" in sys.argv
    today = dt.date.today()
    pull = (today - dt.timedelta(days=1)).isoformat()
    day = os.path.join(LR, "trial", today.isoformat())
    for code, town in lp.STORES:
        live = os.path.exists(os.path.join(LIVE, code))
        plan = os.path.join(day, "plan_%s.csv" % code)
        if not os.path.exists(plan):
            print("%s: no plan for %s - nothing sent" % (code, today)); continue
        rows = list(csv.DictReader(open(plan, newline="")))
        ok, why = lp.send_window_ok(os.path.join(lp.BRAVO_OUT, "%s_%s_loan-reminders.csv" % (pull, code)), today)
        long_ = [r for r in rows if len(r["text"]) > 160]
        if not ok: print("%s: HELD (%s) - %d planned, nothing sent" % (code, why, len(rows))); continue
        if long_ or len(rows) > MAX_PER_DAY:
            print("%s: HELD (%d over 160 characters, %d planned vs cap %d) - nothing sent" % (code, len(long_), len(rows), MAX_PER_DAY)); continue
        if dry or not live:
            print("%s: %s - would send %d (%s)" % (code, "dry run" if dry else "not live", len(rows), why)); continue
        sent_path = os.path.join(day, "sent_%s.csv" % code)
        done = set()
        if os.path.exists(sent_path):
            done = {(r["phone"], r["kind"]) for r in csv.DictReader(open(sent_path, newline=""))}
        tok = token(code)
        if not tok:
            print("%s: no Chekkit key - nothing sent" % code); continue
        new = not os.path.exists(sent_path)
        n = bad = 0
        with open(sent_path, "a", newline="") as fh:
            w = csv.writer(fh)
            if new: w.writerow(["phone", "kind", "status", "error", "at"])
            for r in rows:
                if (r["phone"], r["kind"]) in done: continue
                if dt.datetime.now().time() > dt.time(9, 45): print("%s: 9:45 reached - stopping" % code); break
                st, err = text(tok, {"phone": r["phone"], "name": r.get("name") or "Valley Pawn customer", "message": r["text"]})
                w.writerow([r["phone"], r["kind"], st, err, dt.datetime.now().isoformat(timespec="seconds")]); fh.flush()
                done.add((r["phone"], r["kind"]))
                if 200 <= st < 300: n += 1
                else:
                    bad += 1
                    if "opted out" in (err or "").lower():   # Chekkit is the do-not-text source: remember it
                        op = os.path.join(os.path.dirname(HERE), "fleet", "state", "chekkit_optouts", code + ".tsv")
                        with open(op, "a") as of: of.write("%s\t%s\tChekkit refused: opted out\n" % (r["phone"], dt.datetime.now().isoformat(timespec="seconds")))
                time.sleep(1.1)
        print("%s: sent %d, rejected %d of %d planned" % (code, n, bad, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
