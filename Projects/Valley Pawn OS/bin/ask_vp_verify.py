#!/usr/bin/env python3
"""
ask_vp_verify.py — the weekly ten-minute ask of Preston (agent ask-vp-verify, Mondays 09:00).

The only recurring ask on Preston's time in the whole Ask Valley Pawn system. Each Monday:
  1. Reads #preston-claude for the last batch this script posted and Preston's numbered replies:
        ok / yes / correct / 👍        -> VERIFIED
        no / wrong / not anymore        -> REJECTED (entry stops publishing)
        anything else                   -> VERIFIED with that text as the correction
     Writes them into Preston Knowledge Base/verified.json (merge, never overwrite) and rebuilds.
  2. Builds this week's batch: kb_build.py --queue (<= 10 pending entries, highest confidence first —
     those are what the responder is already answering from) plus any NOT-FOUND questions from
     Ask Valley Pawn/QUESTION_LOG.md in the last 7 days (a real store question beats a queued rule).
  3. Posts ONE message to #preston-claude — only if Ask Valley Pawn/config.json has "verify_enabled": true.
     Until Joshua flips that, the batch is written to Ask Valley Pawn/verify/<date>.md and nothing is posted.

Nothing else is ever sent. Never more than 10 items. Rule 16 on failure.
USAGE  ask_vp_verify.py [--dry-run]
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects")
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
KB = os.path.join(PROJ, "Preston Knowledge Base")
KB_BUILD = os.path.join(KB, "kb_build.py")
VERIFIED = os.path.join(KB, "verified.json")
BASE = os.path.join(PROJ, "Ask Valley Pawn")
CONFIG = os.path.join(BASE, "config.json")
QLOG = os.path.join(BASE, "QUESTION_LOG.md")
VDIR = os.path.join(BASE, "verify")
STATE = os.path.join(OS_DIR, "fleet", "state", "ask_vp", "verify_state.json")
LOG = os.path.join(HOME, "Library", "Logs", "valleypawn", "ask-vp-verify.log")
PRESTON_CH = "C0BGXSTT4TY"
PRESTON = "U03BWMEM9GR"
MARK = "Quick check — reply with the number and ok / no / the right answer"
PY = sys.executable or "/usr/bin/python3"

sys.path.insert(0, BIN)
import vp_slack  # noqa: E402


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def load_json(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default


def save_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w"), indent=1)
    os.replace(tmp, p)


# ----------------------------------------------------------------------------- 1. read replies
def parse_reply(text):
    t = text.strip()
    m = re.match(r"^\s*#?(\d{1,2})\s*[:\-.)]?\s*(.*)$", t, re.S)
    if not m:
        return None
    n, rest = int(m.group(1)), m.group(2).strip()
    low = rest.lower().strip(" .!")
    if low in ("ok", "okay", "yes", "correct", "right", "yep", "yup", "good", "👍", ":+1:", "still right", "true", "y"):
        return n, "VERIFIED", None
    if low in ("no", "wrong", "nope", "not anymore", "incorrect", "n", "👎", ":-1:", "no longer", "kill it", "delete"):
        return n, "REJECTED", None
    if rest:
        return n, "VERIFIED", rest
    return None


def read_replies(st):
    batch = st.get("last_batch")   # {"ts":..., "items":[{"n":1,"id":...}, ...]}
    if not batch:
        return 0
    ids = {it["n"]: it["id"] for it in batch["items"] if it.get("id")}
    try:
        r = vp_slack.call("conversations.replies", params={"channel": PRESTON_CH, "ts": batch["ts"], "limit": 100})
        msgs = r.get("messages", [])[1:]
        # he may also answer in the channel instead of the thread
        r2 = vp_slack.call("conversations.history", params={"channel": PRESTON_CH, "oldest": batch["ts"], "limit": 100})
        msgs += [m for m in r2.get("messages", []) if m.get("ts") != batch["ts"]]
    except Exception as e:
        log("reading replies failed: %s" % e)
        return 0
    ver = load_json(VERIFIED, {})
    n_done = 0
    for m in msgs:
        if m.get("user") != PRESTON:
            continue
        for line in (m.get("text") or "").splitlines():
            p = parse_reply(line)
            if not p or p[0] not in ids:
                continue
            n, status, corr = p
            eid = ids[n]
            ver[eid] = {"status": status, "verified_on": datetime.date.today().isoformat(),
                        "correction": corr, "supersedes": None}
            n_done += 1
    if n_done:
        save_json(VERIFIED, ver)
        r = subprocess.run([PY, KB_BUILD, "--force"], cwd=KB, capture_output=True, text=True, timeout=300)
        log("applied %d rulings; kb_build rc=%s" % (n_done, r.returncode))
    return n_done


# ----------------------------------------------------------------------------- 2. build batch
def not_found_rows(days=7):
    rows = []
    if not os.path.exists(QLOG):
        return rows
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    for ln in open(QLOG, encoding="utf-8"):
        if "NOT-FOUND" not in ln or not ln.startswith("| 20"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        try:
            when = datetime.datetime.strptime(cells[0][:16], "%Y-%m-%d %H:%M")
        except Exception:
            continue
        if when >= cutoff and len(cells) >= 4:
            rows.append(cells[3])
    return rows


def build_batch():
    r = subprocess.run([PY, KB_BUILD, "--queue"], cwd=KB, capture_output=True, text=True, timeout=300)
    q = []
    try:
        q = json.loads(r.stdout).get("batch", [])
    except Exception:
        log("queue unreadable: %s" % (r.stderr or r.stdout)[-300:])
    nf = not_found_rows()
    items, lines = [], []
    n = 0
    for e in q:
        if n >= 10 - min(len(nf), 3):
            break
        n += 1
        items.append({"n": n, "id": e["id"]})
        date = re.search(r"(20\d\d-\d\d-\d\d)", e.get("source", ""))
        lines.append("%d. %s\n   You said (%s): \"%s\"" % (n, e["claim"], date.group(1) if date else "date unknown", e["verbatim"][:280]))
    for qtext in nf[:3]:
        if n >= 10:
            break
        n += 1
        items.append({"n": n, "id": None, "question": qtext})
        lines.append("%d. A store asked this week and it isn't written down yet — what's the rule? \"%s\"" % (n, qtext))
    return items, lines


def main():
    dry = "--dry-run" in sys.argv
    st = load_json(STATE, {})
    cfg = load_json(CONFIG, {})
    applied = read_replies(st) if not dry else 0
    items, lines = build_batch()
    if not items:
        log("nothing to verify (applied %d)" % applied)
        return 0
    text = ("Preston — %s. Ten minutes max; skip anything you're not sure about and it comes back later.\n\n%s"
            % (MARK, "\n".join(lines)))
    os.makedirs(VDIR, exist_ok=True)
    outp = os.path.join(VDIR, "%s.md" % datetime.date.today().isoformat())
    open(outp, "w", encoding="utf-8").write(text + "\n\n<!-- items: %s -->\n" % json.dumps(items))
    if dry or not cfg.get("verify_enabled"):
        log("batch written to %s, NOT posted (verify_enabled=%s)" % (os.path.basename(outp), cfg.get("verify_enabled")))
        return 0
    r = vp_slack.call("chat.postMessage", {"channel": PRESTON_CH, "text": vp_slack.to_mrkdwn(text), "unfurl_links": False})
    if not r.get("ok"):
        log("post failed: %s" % r.get("error"))
        return 1
    vp_slack.receipt("slack", PRESTON_CH, True, len(text.encode()), "ask-vp verify batch")
    st["last_batch"] = {"ts": r.get("ts"), "items": items, "posted": datetime.date.today().isoformat()}
    save_json(STATE, st)
    log("posted batch of %d (applied %d rulings from last week)" % (len(items), applied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
