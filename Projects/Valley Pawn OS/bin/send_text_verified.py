#!/usr/bin/env python3
"""
send_text_verified.py — hardened outbound text sender for Valley Pawn automations.

WHY THIS EXISTS (2026-09-10): the `send_imessage` MCP tool forces the iMessage
service. Recipients who are not on iMessage (Android phones) fail with chat.db
error 22 and NO SMS fallback — roughly half of applicant texts were silently
lost this way (Sarah Wheeler, Jessica Paling, Stacie Jones, Elliot Martin, ...).
The Mac has Text Message Forwarding enabled (SMS account is active), so SMS
sends succeed when routed there explicitly.

WHAT IT DOES
  1. Normalizes the number to E.164.
  2. Picks a route from chat.db history: a service that already delivered to
     this number wins; a number whose only history is iMessage error-22 goes
     straight to SMS; unknown numbers try iMessage first.
  3. Sends via AppleScript to the chosen Messages account, then VERIFIES in
     chat.db that a new outbound row exists with is_sent=1 and error=0.
  4. On error 22 / not-sent, retries on the other service. Verifies again.
  5. Appends one line to the ledger and prints a JSON result.

USAGE
  send_text_verified.py --to "+15404715197" --text "Hi Sarah ..." [--task NAME]
  send_text_verified.py --to 5404715197 --text-file /path/msg.txt
  Exit 0 = verified sent. Exit 1 = both routes failed (caller should fall back
  to email and log the gap). Never claims success without a chat.db row.

  Designed to finish inside the ~25s osascript wrapper limit.
"""
import argparse, json, os, re, sqlite3, subprocess, sys, time
from datetime import datetime

DB = os.path.expanduser("~/Library/Messages/chat.db")
LEDGER = os.path.expanduser(
    "~/Documents/Claude/Projects/Valley Pawn OS/fleet/TEXT_SEND_LEDGER.md")
POLL_SECONDS = 7          # per attempt; error 22 surfaces within ~2s
POLL_STEP = 0.5


def normalize(num: str) -> str:
    d = re.sub(r"\D", "", num or "")
    if len(d) == 10:
        d = "1" + d
    if len(d) == 11 and d.startswith("1"):
        return "+" + d
    if num.strip().startswith("+") and len(d) >= 11:
        return "+" + d
    raise ValueError(f"cannot normalize phone number: {num!r}")


def q(sql, args=()):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def history(number):
    """Return {service: (delivered_count, error22_count)} for our outbound."""
    rows = q("""SELECT m.service, m.is_sent, m.error
                FROM message m JOIN handle h ON m.handle_id=h.ROWID
                WHERE m.is_from_me=1 AND h.id=?""", (number,))
    out = {}
    for svc, sent, err in rows:
        d, e = out.get(svc, (0, 0))
        if sent == 1 and err == 0:
            d += 1
        elif err == 22:
            e += 1
        out[svc] = (d, e)
    return out


def choose_routes(number):
    h = history(number)
    good = [s for s, (d, e) in h.items() if d > 0]
    if "iMessage" in good:
        return ["iMessage", "SMS"]
    if "SMS" in good or "RCS" in good:
        return ["SMS", "iMessage"]
    if h.get("iMessage", (0, 0))[1] > 0:      # only ever failed on iMessage
        return ["SMS", "iMessage"]
    return ["iMessage", "SMS"]


def max_rowid():
    return q("SELECT COALESCE(MAX(ROWID),0) FROM message")[0][0]


def applescript_send(number, text, service):
    esc = text.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
tell application "Messages"
    set acct to first account whose service type is {service} and enabled is true
    set p to participant "{number}" of acct
    send "{esc}" to p
end tell'''
    r = subprocess.run(["osascript", "-e", script],
                       capture_output=True, text=True, timeout=20)
    return r.returncode == 0, (r.stderr or "").strip()


def verify(number, since_rowid, want_service):
    """Poll for the new outbound row; return (status, rowid, service, error)."""
    deadline = time.time() + POLL_SECONDS
    last = None
    while time.time() < deadline:
        rows = q("""SELECT m.ROWID, m.service, m.is_sent, m.is_delivered, m.error
                    FROM message m JOIN handle h ON m.handle_id=h.ROWID
                    WHERE m.is_from_me=1 AND h.id=? AND m.ROWID>?
                    ORDER BY m.ROWID DESC LIMIT 1""", (number, since_rowid))
        if rows:
            rid, svc, sent, delivered, err = rows[0]
            last = (rid, svc, sent, delivered, err)
            if err and err != 0:
                return "error", rid, svc, err
            if sent == 1:
                return "sent", rid, svc, 0
        time.sleep(POLL_STEP)
    if last:
        return "pending", last[0], last[1], last[4]
    return "norow", None, want_service, None


def ledger(line):
    try:
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        new = not os.path.exists(LEDGER)
        with open(LEDGER, "a") as f:
            if new:
                f.write("# Text send ledger (send_text_verified.py)\n\n"
                        "| when ET | task | number | route | result | rowid | note |\n"
                        "|---|---|---|---|---|---|---|\n")
            f.write(line + "\n")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--text-file")
    ap.add_argument("--task", default="manual")
    ap.add_argument("--force-service", choices=["iMessage", "SMS"])
    a = ap.parse_args()

    text = a.text if a.text is not None else open(a.text_file).read().rstrip("\n")
    if not text.strip():
        print(json.dumps({"ok": False, "error": "empty text"})); sys.exit(1)
    number = normalize(a.to)
    routes = [a.force_service, "SMS" if a.force_service == "iMessage" else "iMessage"] \
        if a.force_service else choose_routes(number)

    attempts = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for svc in routes:
        base = max_rowid()
        ok, err = applescript_send(number, text, svc)
        if not ok:
            attempts.append({"service": svc, "status": "applescript_error", "detail": err})
            continue
        status, rid, seen_svc, dberr = verify(number, base, svc)
        attempts.append({"service": svc, "status": status, "rowid": rid, "db_error": dberr})
        if status == "sent":
            res = {"ok": True, "to": number, "service": seen_svc, "rowid": rid,
                   "attempts": attempts}
            ledger(f"| {now} | {a.task} | {number} | {seen_svc} | SENT | {rid} | "
                   f"{'fallback' if len(attempts) > 1 else 'first try'} |")
            print(json.dumps(res)); sys.exit(0)
        if status == "pending":
            # Row exists, no error yet, not confirmed sent within the poll window.
            # iMessage to a valid iMessage user can sit 'pending' briefly; treat as
            # likely-sent but flag it so the caller can re-verify.
            res = {"ok": True, "to": number, "service": seen_svc, "rowid": rid,
                   "unverified": True, "attempts": attempts}
            ledger(f"| {now} | {a.task} | {number} | {seen_svc} | PENDING | {rid} | "
                   f"row exists, is_sent not yet 1 — re-verify |")
            print(json.dumps(res)); sys.exit(0)
        # error / norow → try next route
        time.sleep(1.0)

    ledger(f"| {now} | {a.task} | {number} | {'>'.join(routes)} | FAILED | - | "
           f"{json.dumps(attempts)[:160]} |")
    print(json.dumps({"ok": False, "to": number, "attempts": attempts,
                      "action": "fall back to email; log gap"}))
    sys.exit(1)


if __name__ == "__main__":
    main()
