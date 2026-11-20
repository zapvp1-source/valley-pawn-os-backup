#!/usr/bin/env python3
"""
ask_vp_capture.py — nightly knowledge capture for Ask Valley Pawn (agent ask-vp-capture, 22:00 daily).

Turns what Preston and the store managers ALREADY said today into sourced knowledge entries, with zero
effort from them. Three sources, one output:

  1. Slack: every message by Preston or a store manager in the deal/ops channels in the last 26 h
     (overlap on purpose; the build dedupes). Replies are read with their parent question.
  2. Recorded employee-to-employee calls: runs the Zoom pipeline (Zoom Call Pipeline/zoom_ingest.py —
     local whisper only, customer calls reduced + destroyed there) and reads only out/employee/*.json
     that this script has not processed before. Store<->Preston calls on his Zoom line (ext 813) land here.
  3. (one-time) Preston Time Review/transcripts — the five store<->Preston calls transcribed 10/1.

Each candidate entry is written in the Preston Knowledge Base harvest format and appended to
  Preston Knowledge Base/_raw_harvest/capture_<date>.md
then kb_build.py rebuilds KB_CURRENT.md. The responder's corpus picks it up on its next run (<= 15 s).

RULES (the extraction prompt enforces these; the build drops anything missing a quote or a source)
  * Only operational rules, numbers, thresholds, procedures, testing methods, valuation judgments, named
    counterparties. Chatter, scheduling, cash requests, acknowledgements -> nothing.
  * VERBATIM = the speaker's exact words. Never merged, smoothed or invented.
  * CONFIDENCE: HIGH only when stated as a general rule. When in doubt, LOWER.
  * From calls: never a customer's name, number, item tied to a person, or a customer's words.
  * Contradictions are captured WITH a CONFLICT line, never resolved here.
  * Silent: posts nothing anywhere. Failures -> log + one ledger row.

USAGE  ask_vp_capture.py [--no-zoom] [--dry-run] [--since-hours N]
"""
import datetime
import glob
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
RAW = os.path.join(KB, "_raw_harvest")
KB_BUILD = os.path.join(KB, "kb_build.py")
ZOOM = os.path.join(PROJ, "Zoom Call Pipeline")
ZOOM_INGEST = os.path.join(ZOOM, "zoom_ingest.py")
ZOOM_EMP = os.path.join(ZOOM, "out", "employee")
PTR = os.path.join(PROJ, "Preston Time Review", "transcripts")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
STATE_DIR = os.path.join(OS_DIR, "fleet", "state", "ask_vp")
STATE = os.path.join(STATE_DIR, "capture_state.json")
LOG = os.path.join(HOME, "Library", "Logs", "valleypawn", "ask-vp-capture.log")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
PY = sys.executable or "/usr/bin/python3"

PRESTON = "U03BWMEM9GR"
CHANNELS = {   # from the staged preston-knowledge-capture task (2026-09-07) + #ask-handbook
    "C03BWGT5F5X": "#deal-questions", "C03BETSS669": "#general",   # #loans-and-buys (C03GBDKSLRE) archived — Joshua 10/8
    "C0BGXSTT4TY": "#preston-claude", "C03BHQ9RLR0": "#policy-announcements", "C05EHBH4G67": "#scrap-rankings",
    "C04NGH4FF35": "#aged-inventory-review", "C063K8E02TW": "#roanoke-funds", "C03BLLRN64U": "#boro-funds",
    "C03B3K5DL6T": "#lex-funds", "C03BWRKEDUZ": "#harrisonburg-funds", "C0BS11KTYKU": "#ask-handbook",
}

sys.path.insert(0, BIN)
import vp_ai      # noqa: E402
import vp_slack   # noqa: E402

EXTRACT_SYSTEM = """You extract operational knowledge for Valley Pawn (a five-store Virginia pawn business) from what Preston Peters (Operations Manager) or a store manager wrote or said. Output ONLY candidate entries in exactly this format, separated by a line containing only ---, or the single word NONE.

---
TOPIC: <short-kebab-slug, e.g. pay-percentage-bullion>
CLAIM: <1-2 sentences, the rule in plain actionable language>
VERBATIM: "<the speaker's exact words, unedited, copied from the source>"
SOURCE: <copy the SOURCE line given for that message exactly>
CONFIDENCE: HIGH | MEDIUM | LOW
CONFLICT: <only if it contradicts something stated elsewhere in this batch; otherwise omit the line>
---

Keep ONLY: a rule, a number, a threshold, a procedure, a testing method, a valuation judgment, a named vendor/buyer, a policy. Drop chatter, scheduling, cash requests, acknowledgements, questions with no answer, anything about a specific employee's pay or conduct.
CONFIDENCE: HIGH only when stated as a general rule ("going forward we…", "always…", "never…"). MEDIUM when a rule is clearly implied by one case. LOW for a judgment on one deal. When in doubt, go LOWER.
NEVER invent, extrapolate, merge two messages into one cleaner claim, or paraphrase inside VERBATIM. If a message states nothing usable, skip it.
From a phone transcript: quote only the RULE being stated by the employee/manager/Preston. Never a customer's name, phone number, address, item tied to a person, or a customer's words."""


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def ledger(sentence, needs_human="no"):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | ask-vp-capture | %s | NEEDS_HUMAN: %s | OPEN |\n"
                    % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET"), sentence, needs_human))
    except Exception:
        pass


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"calls_done": [], "ptr_done": [], "last_slack_ts": {}}


def save_state(st):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE)


def speakers():
    """slack id -> (display, role) for Preston + store managers."""
    out = {PRESTON: ("Preston Peters", "Operations Manager")}
    try:
        d = json.load(open(ROSTER))
        for e in d.get("employees", []):
            if (e.get("title") or "").strip().lower() == "manager" and e.get("slack_id"):
                out[e["slack_id"]] = (e.get("name") or e.get("preferred"), "%s manager" % e.get("department"))
    except Exception as e:
        log("roster unreadable: %s" % e)
    return out


# ----------------------------------------------------------------------------- slack
def permalink(ch, ts):
    try:
        r = vp_slack.call("chat.getPermalink", params={"channel": ch, "message_ts": ts})
        return r.get("permalink") or ""
    except Exception:
        return ""


def slack_items(hours, st):
    sp = speakers()
    cutoff = time.time() - hours * 3600
    items = []
    for ch, name in CHANNELS.items():
        try:
            r = vp_slack.call("conversations.history", params={"channel": ch, "oldest": "%.6f" % cutoff, "limit": 200})
        except Exception as e:
            log("history %s failed: %s" % (name, e))
            continue
        if not r.get("ok") and r.get("error") == "not_in_channel":
            # public channel the bot was never invited to: join once (needs channels:join), then retry
            try:
                j = vp_slack.call("conversations.join", {"channel": ch})
                if j.get("ok"):
                    r = vp_slack.call("conversations.history", params={"channel": ch, "oldest": "%.6f" % cutoff, "limit": 200})
                else:
                    log("join %s failed: %s — needs an invite for the bot" % (name, j.get("error")))
            except Exception as e:
                log("join %s error: %s" % (name, e))
        if not r.get("ok"):
            log("history %s not ok: %s" % (name, r.get("error")))
            continue
        for m in r.get("messages", []):
            if m.get("user") not in sp or m.get("subtype") or len((m.get("text") or "").strip()) < 25:
                continue
            # also walk threads: replies by Preston/managers under any recent top-level message
            items.append((ch, name, m, None))
            if m.get("reply_count"):
                try:
                    rr = vp_slack.call("conversations.replies", params={"channel": ch, "ts": m["ts"], "limit": 50})
                    for rep in rr.get("messages", [])[1:]:
                        if rep.get("user") in sp and len((rep.get("text") or "").strip()) >= 25:
                            items.append((ch, name, rep, m))
                except Exception:
                    pass
        # threads under OTHER people's questions (the common case in #deal-questions)
        for m in r.get("messages", []):
            if m.get("user") in sp or not m.get("reply_count"):
                continue
            try:
                rr = vp_slack.call("conversations.replies", params={"channel": ch, "ts": m["ts"], "limit": 50})
            except Exception:
                continue
            for rep in rr.get("messages", [])[1:]:
                if rep.get("user") in sp and len((rep.get("text") or "").strip()) >= 25 and float(rep.get("ts", 0)) >= cutoff:
                    items.append((ch, name, rep, m))
    # dedupe by ts
    seen, out = set(), []
    for it in items:
        key = (it[0], it[2].get("ts"))
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out, sp


def slack_batch_text(items, sp):
    parts = []
    for ch, name, m, parent in items:
        who, role = sp[m["user"]]
        day = datetime.datetime.fromtimestamp(float(m["ts"])).strftime("%Y-%m-%d")
        link = permalink(ch, m["ts"])
        if not link:
            continue
        src = "%s (%s, %s) | %s | %s" % (name, who, role, day, link)
        q = ("QUESTION BEING ANSWERED: " + (parent.get("text") or "")[:600] + "\n") if parent else ""
        parts.append("=== MESSAGE\nSOURCE: %s\n%sSPEAKER: %s (%s)\nTEXT: %s\n" % (src, q, who, role, (m.get("text") or "")[:3000]))
    return "\n".join(parts)


# ----------------------------------------------------------------------------- calls
def run_zoom(hours):
    if not os.path.exists(ZOOM_INGEST):
        log("zoom_ingest.py missing — skipping calls")
        return
    since = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    env = dict(os.environ)
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + env.get("PATH", "")
    try:
        r = subprocess.run([PY, ZOOM_INGEST, "--since", since, "--limit", "150"], cwd=ZOOM, env=env,
                           capture_output=True, text=True, timeout=3300)
        log("zoom_ingest rc=%s %s" % (r.returncode, (r.stdout or r.stderr).strip().splitlines()[-1:] ))
    except subprocess.TimeoutExpired:
        log("zoom_ingest timed out (55 min) — partial progress is checkpointed; next night continues")
    except Exception as e:
        log("zoom_ingest error: %s" % e)


def call_items(st):
    items = []
    for p in sorted(glob.glob(os.path.join(ZOOM_EMP, "*.json"))):
        cid = os.path.basename(p)[:-5]
        if cid in st["calls_done"]:
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        t = (d.get("transcript") or "").strip()
        if len(t) < 200:
            st["calls_done"].append(cid)
            continue
        src = "zoom-call:%s | %s | %s %s" % (cid, d.get("date", ""), d.get("store", "UNK"), d.get("participant", ""))
        items.append((cid, src, t))
    # one-time: the Preston Time Review transcripts
    for p in sorted(glob.glob(os.path.join(PTR, "*"))):
        base = os.path.basename(p)
        if base in st["ptr_done"] or not base.lower().endswith((".txt", ".md", ".json")):
            continue
        try:
            raw = open(p, encoding="utf-8", errors="ignore").read()
            if base.endswith(".json"):
                try:
                    raw = json.loads(raw).get("transcript") or json.loads(raw).get("text") or raw
                except Exception:
                    pass
        except Exception:
            continue
        m = re.search(r"(20\d\d-\d\d-\d\d)", base)
        src = "zoom-call:%s | %s | store<->Preston (transcribed 2026-10-01)" % (base, m.group(1) if m else "")
        if len(raw.strip()) >= 200:
            items.append(("ptr:" + base, src, raw.strip()))
        else:
            st["ptr_done"].append(base)
    return items


# ----------------------------------------------------------------------------- extraction
ENTRY_OK = re.compile(r"^TOPIC:.*\nCLAIM:.*\nVERBATIM:.*\nSOURCE:.*\nCONFIDENCE:", re.M | re.S)


def extract(text, dry):
    if dry:
        return ""
    out = vp_ai.ask(text, system=EXTRACT_SYSTEM, max_tokens=4000)
    out = out.strip()
    if out.upper().startswith("NONE") or "TOPIC:" not in out:
        return ""
    return out


def main():
    a = sys.argv[1:]
    dry = "--dry-run" in a
    hours = int(a[a.index("--since-hours") + 1]) if "--since-hours" in a else 26
    st = load_state()
    os.makedirs(RAW, exist_ok=True)
    captured = []

    # 1. Slack
    try:
        items, sp = slack_items(hours, st)
        log("slack: %d Preston/manager messages in window" % len(items))
        for i in range(0, len(items), 12):
            batch = slack_batch_text(items[i:i + 12], sp)
            if batch.strip():
                e = extract(batch, dry)
                if e:
                    captured.append(e)
    except Exception as e:
        log("slack capture failed: %s" % e)

    # 2. calls
    if "--no-zoom" not in a and not dry:
        run_zoom(hours)
    try:
        calls = call_items(st)
        log("calls: %d new employee transcripts" % len(calls))
        for cid, src, t in calls:
            text = "=== CALL TRANSCRIPT\nSOURCE: %s\nNOTE: employee-to-employee call. Quote only rules stated by Preston or a manager. Never a customer's name, number, address or words.\nTRANSCRIPT:\n%s\n" % (src, t[:16000])
            e = extract(text, dry)
            if e:
                captured.append(e)
            if not dry:
                (st["ptr_done"] if cid.startswith("ptr:") else st["calls_done"]).append(cid.replace("ptr:", ""))
    except Exception as e:
        log("call capture failed: %s" % e)

    if dry:
        print("dry run: %d slack items" % len(items))
        return 0
    if not captured:
        save_state(st)
        log("nothing new")
        return 0

    body = "\n".join(c.strip() + "\n---\n" for c in captured)
    n = len(ENTRY_OK.findall(body))
    day = datetime.date.today().isoformat()
    path = os.path.join(RAW, "capture_%s.md" % day)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n# captured %s by ask_vp_capture.py\n---\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), body))
    r = subprocess.run([PY, KB_BUILD, "--force"], cwd=KB, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        broken = path + ".broken-%s" % datetime.datetime.now().strftime("%H%M%S")
        os.replace(path, broken)
        subprocess.run([PY, KB_BUILD, "--force"], cwd=KB, capture_output=True, text=True, timeout=300)
        log("kb_build failed after append; file set aside as %s" % os.path.basename(broken))
        ledger("ask-vp-capture: a captured file broke the knowledge build and was set aside (%s)" % os.path.basename(broken), "no")
        return 1
    save_state(st)
    log("captured %d candidate entries -> %s; KB rebuilt" % (n, os.path.basename(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
