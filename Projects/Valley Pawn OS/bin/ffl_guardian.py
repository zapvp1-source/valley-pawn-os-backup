#!/usr/bin/env python3
"""FFL Guardian — Valley Pawn (native, additive, 2026-09-05).

Runs OUTSIDE Claude (pure stdlib Python via launchd) so it keeps working when
the Cowork fleet is saturated. Owns the deterministic half of the FFL
department. Nothing here needs a language model.

Jobs, every run:
  1. WEB-FORM RELAY — "Website FFL Transfer Request" mail from the
     thevalleypawn.com form -> one plain-language card in #gun-transfers,
     routed to the pickup store. Replaces the relay that died 2026-07-30 and
     left 4 August customers unannounced to their stores.
  2. INBOUND DIGEST — new GunBroker/MasterFFL "New Inbound FFL Transfer"
     notices -> one line per transfer in #gun-transfers, routed to the
     receiving store by the FFL number in the mail.
  3. VENDOR EXPIRY AUTO-REPLY — a retailer saying our FFL is expiring/expired
     gets an in-thread reply with the correct store's SIGNED license attached,
     and the roster records the send. This is the exact failure that got
     Culpeper cut off at GrabAGun on 2026-09-01.
  4. EXPIRATION LADDER — 120/90/60/30/14 days before each license expires, one
     plain DM to Joshua. ATF mails every renewal form to the FLORIDA address of
     record (Joshua's decision 2026-09-05) so this ladder is the only warning.
  5. STATUS — writes Compliance/ffl_status.json for the monthly rollups.

Rules honored: 12 (verify against output), 16 (no failure notices or technical
jargon on Slack — failures go to the log only), 18 (never post partial data).

State: Compliance/.ffl_guardian_state.json   (dedupe by message-id; nothing is
ever relayed, replied to, or DM'd twice)
Log:   ~/Library/Logs/valleypawn/ffl-guardian.log

Run manually:  python3 ffl_guardian.py [--dry-run] [--days N]
Installed as:  ~/Library/LaunchAgents/com.valleypawn.ffl-guardian.plist (7:15 AM)
"""

import datetime as dt
import email
import email.utils
import getpass
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import urllib.request
from email import policy

HOME = os.path.expanduser("~")
COMPLIANCE = os.path.join(HOME, "Documents/Claude/Projects/Compliance")
ROSTER = os.path.join(COMPLIANCE, "ffl_vendors.json")
STATE = os.path.join(COMPLIANCE, ".ffl_guardian_state.json")
STATUS = os.path.join(COMPLIANCE, "ffl_status.json")
FFL_FILES = os.path.join(COMPLIANCE, "ffl-files")
LOG = os.path.join(HOME, "Library/Logs/valleypawn/ffl-guardian.log")
MAIL_ROOT = os.path.join(HOME, "Library/Mail/V10")

GUN_TRANSFERS = "C0B08U7AC7P"      # #gun-transfers
JOSHUA_USER = "U03BB52MDSA"
KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"

LADDER_DAYS = [120, 90, 60, 30, 14]
DEFAULT_LOOKBACK_DAYS = 3          # mail scan window; state file prevents dupes
MAX_ACTION_AGE_DAYS = 5            # never act on mail older than this, whatever
                                   # the scan window is — stops a wide manual run
                                   # from replying to months-old vendor notices
VENDOR_COOLDOWN_DAYS = 14          # one license copy per vendor per store per
                                   # fortnight — a ticket system's auto-reply to
                                   # our reply must never start a loop
FROM_ADDRESS = "Joshua Davis <jdavis@fcfpawn.com>"

DRY = "--dry-run" in sys.argv
SEED = "--seed" in sys.argv        # mark everything in the window as handled and
                                   # send nothing (use once, at install)


def log(msg):
    line = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str(msg)
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def lookback_days():
    if "--days" in sys.argv:
        try:
            return int(sys.argv[sys.argv.index("--days") + 1])
        except Exception:
            pass
    return DEFAULT_LOOKBACK_DAYS


# ------------------------------------------------------------------ state
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    if DRY:
        return
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def new_state():
    return {"relayed": {}, "inbound": {}, "expiry_replies": {}, "ladder": {},
            "vendor_sends": {}, "last_run": None}


# ------------------------------------------------------------------ slack
def get_token():
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
             "-a", getpass.getuser(), "-w"],
            capture_output=True, text=True, timeout=10)
        tok = r.stdout.strip()
        if tok.startswith("xoxb-"):
            return tok
    except Exception:
        pass
    tok = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if tok.startswith("xoxb-"):
        return tok
    for p in (os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction/slack_config.json"),
              os.path.join(HOME, ".vp_slack_config.json")):
        try:
            d = json.load(open(p))
            t = (d.get("SLACK_BOT_TOKEN") or d.get("slack_bot_token") or "").strip()
            if t.startswith("xoxb-"):
                return t
        except Exception:
            continue
    return None


def _slack_call(token, method, payload):
    req = urllib.request.Request(
        "https://slack.com/api/" + method,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json; charset=utf-8"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def slack_post(channel, text):
    if DRY:
        log("[dry-run] would post to " + channel + ":\n" + text)
        return True
    token = get_token()
    if not token:
        log("ERROR no slack token; not posting")
        return False
    try:
        r = _slack_call(token, "chat.postMessage", {"channel": channel, "text": text})
        if not r.get("ok"):
            log("ERROR slack postMessage: " + str(r.get("error")))
            return False
        return True
    except Exception as e:
        log("ERROR slack network: " + str(e))
        return False


def slack_dm(text):
    if DRY:
        log("[dry-run] would DM Joshua:\n" + text)
        return True
    token = get_token()
    if not token:
        log("ERROR no slack token; not DMing")
        return False
    try:
        opened = _slack_call(token, "conversations.open", {"users": JOSHUA_USER})
        if not opened.get("ok"):
            log("ERROR conversations.open: " + str(opened.get("error")))
            return False
        return slack_post(opened["channel"]["id"], text)
    except Exception as e:
        log("ERROR slack dm: " + str(e))
        return False


# ------------------------------------------------------------------- mail
# Cheap C-level prefilter. The five store mailboxes take ~1,200 machine emails a
# DAY between them, so a 3-day window is ~6,000 files — far too many to parse in
# Python. grep the raw files for the handful of strings that could possibly
# matter, then parse only the handful that hit.
PREFILTER = [
    "Website FFL Transfer Request",
    "New Inbound FFL Transfer",
    "masterffl.com",
    "grabagun",
    "brownells",
    "sportsmans.com",
    "midwayusa",
    "FFL",
]


def recent_emlx(days):
    """Candidate .emlx files touched in the window. Drafts/Sent/Junk/Trash out."""
    try:
        r = subprocess.run(
            ["find", MAIL_ROOT, "-name", "*.emlx", "-newermt", "-%d days" % days],
            capture_output=True, text=True, timeout=300)
        paths = [p for p in r.stdout.splitlines() if p.strip()]
    except Exception as e:
        log("ERROR mail scan: " + str(e))
        return []
    keep = []
    for p in paths:
        low = p.lower()
        if "/drafts.mbox/" in low or "/sent messages.mbox/" in low or "/sent.mbox/" in low:
            continue
        if "/junk" in low or "/trash" in low or "/deleted messages" in low:
            continue
        keep.append(p)
    if not keep:
        return []
    log("mail window: %d messages, prefiltering" % len(keep))
    args = ["grep", "-l", "-i", "-Z"]
    for pat in PREFILTER:
        args += ["-e", pat]
    hits = []
    CHUNK = 400
    for i in range(0, len(keep), CHUNK):
        batch = keep[i:i + CHUNK]
        try:
            r = subprocess.run(args + batch, capture_output=True, text=True, timeout=300)
            hits += [p for p in r.stdout.split("\0") if p.strip()]
        except Exception as e:
            log("ERROR prefilter batch: " + str(e))
    return hits


def parse_emlx(path):
    try:
        with open(path, "rb") as f:
            head = f.readline()
            try:
                n = int(head.strip())
            except Exception:
                return None
            raw = f.read(n)
        m = email.message_from_bytes(raw, policy=policy.default)
        b = m.get_body(preferencelist=("plain", "html"))
        body = ""
        if b is not None:
            try:
                body = b.get_content()
            except Exception:
                body = ""
            if b.get_content_type() == "text/html":
                body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
                body = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
                body = re.sub(r"<[^>]+>", "\n", body)
                body = htmlmod.unescape(body)
        when = None
        try:
            when = email.utils.parsedate_to_datetime(m.get("Date"))
            if when is not None and when.tzinfo is not None:
                when = when.astimezone().replace(tzinfo=None)
        except Exception:
            when = None
        return {
            "path": path,
            "msgid": (m.get("Message-ID") or path).strip(),
            "from": (m.get("From") or "").strip(),
            "to": ((m.get("To") or "") + " " + (m.get("Delivered-To") or "")
                   + " " + (m.get("Cc") or "")).strip(),
            "subject": (m.get("Subject") or "").strip(),
            "date": (m.get("Date") or "").strip(),
            "when": when,
            "body": body,
        }
    except Exception:
        return None


def too_old(m, days=MAX_ACTION_AGE_DAYS):
    if m.get("when") is None:
        return False
    return (dt.datetime.now() - m["when"]).days > days


def send_reply(to_addr, subject, body, attachments, from_addr=FROM_ADDRESS, cc=None):
    """Send via Apple Mail (already authenticated for every account)."""
    if DRY:
        log("[dry-run] would email %s | %s | %d attachment(s)" % (to_addr, subject, len(attachments)))
        return True

    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')

    lines = ['set attList to {}']
    for i, a in enumerate(attachments):
        lines.append('set a%d to POSIX file "%s" as alias' % (i, esc(a)))
        lines.append('set end of attList to a%d' % i)
    lines.append('tell application "Mail"')
    lines.append('  set msg to make new outgoing message with properties '
                 '{subject:"%s", content:"%s", sender:"%s", visible:false}'
                 % (esc(subject), esc(body), esc(from_addr)))
    lines.append('  tell msg')
    lines.append('    make new to recipient at end of to recipients with properties {address:"%s"}'
                 % esc(to_addr))
    if cc:
        lines.append('    make new cc recipient at end of cc recipients with properties {address:"%s"}'
                     % esc(cc))
    lines.append('    repeat with f in attList')
    lines.append('      make new attachment with properties {file name:f} at after the last paragraph')
    lines.append('    end repeat')
    lines.append('  end tell')
    lines.append('  delay 3')
    lines.append('  send msg')
    lines.append('end tell')
    script = "\n".join(lines)
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            log("ERROR mail send to %s: %s" % (to_addr, r.stderr.strip()[:300]))
            return False
        return True
    except Exception as e:
        log("ERROR mail send: " + str(e))
        return False


# ------------------------------------------------------------------ roster
def load_roster():
    r = load_json(ROSTER, None)
    if not r or "stores" not in r:
        log("FATAL roster missing or unreadable: " + ROSTER)
        return None
    return r


def store_by_name(roster, text):
    t = (text or "").lower()
    for key, s in roster["stores"].items():
        if s["name"].lower() in t:
            return key
    return None


def store_by_ffl(roster, text):
    """HTML-to-text can wrap or pad an FFL number, so compare with all
    whitespace removed as well as verbatim."""
    t = text or ""
    flat = re.sub(r"\s+", "", t)
    for key, s in roster["stores"].items():
        if s["ffl"] in t or s["ffl"] in flat:
            return key
    return None


def store_by_recipient(roster, text):
    t = (text or "").lower()
    for key, s in roster["stores"].items():
        if s["email"].lower() in t:
            return key
    return None


def license_path(roster, key):
    p = os.path.join(FFL_FILES, roster["stores"][key]["file"])
    return p if os.path.exists(p) else None


# -------------------------------------------------------------- job 1: form
FORM_FIELDS = ("Your name", "Phone", "Email", "Pickup store")


def parse_web_form(body):
    """The Jetpack form mail is label-on-one-line, value-on-the-next."""
    lines = [l.strip() for l in (body or "").splitlines()]
    lines = [l for l in lines if l and l != "\xa0"]
    out = {}
    for i, l in enumerate(lines):
        for f in FORM_FIELDS:
            if l == f and i + 1 < len(lines):
                out[f] = lines[i + 1]
    key = "What is being transferred / who is shipping it (include any order or reference number)"
    for i, l in enumerate(lines):
        if l.startswith("What is being transferred"):
            rest = []
            for nxt in lines[i + 1:]:
                if nxt in ("Mark as spam", "View in dashboard", "Powered by Jetpack Forms"):
                    break
                rest.append(nxt)
            out[key] = " ".join(rest).strip()
            break
    out["_details"] = out.get(key, "")
    return out


def job_web_form_relay(roster, msgs, state):
    posted = 0
    for m in msgs:
        if "wordpress@thevalleypawn.com" not in m["from"].lower():
            continue
        if "ffl transfer request" not in m["subject"].lower():
            continue
        if m["msgid"] in state["relayed"]:
            continue
        if SEED or too_old(m):
            state["relayed"][m["msgid"]] = "seeded"
            continue
        f = parse_web_form(m["body"])
        name = f.get("Your name", "").strip()
        phone = f.get("Phone", "").strip()
        mail = f.get("Email", "").strip()
        store_txt = f.get("Pickup store", "").strip()
        details = f.get("_details", "").strip()
        if not name or not store_txt:
            log("SKIP unparseable web form: " + m["path"])
            continue
        key = store_by_name(roster, store_txt)
        store_name = roster["stores"][key]["name"] if key else store_txt
        parts = ["*New transfer coming to %s*" % store_name,
                 "%s%s%s" % (name,
                             (" · " + phone) if phone else "",
                             (" · " + mail) if mail else "")]
        if details:
            parts.append(details if len(details) <= 600 else details[:600] + "…")
        parts.append("Give them a call to confirm, and let them know it's $25 at pickup with a photo ID.")
        if slack_post(GUN_TRANSFERS, "\n".join(parts)):
            state["relayed"][m["msgid"]] = dt.datetime.now().isoformat(timespec="seconds")
            posted += 1
            log("relayed web form: %s -> %s" % (name, store_name))
    return posted


# ----------------------------------------------------------- job 2: inbound
def job_inbound_digest(roster, msgs, state):
    rows = []
    for m in msgs:
        if "masterffl.com" not in m["from"].lower():
            continue
        if "new inbound ffl transfer" not in m["subject"].lower():
            continue
        if m["msgid"] in state["inbound"]:
            continue
        if SEED or too_old(m):
            state["inbound"][m["msgid"]] = "seeded"
            continue
        key = (store_by_ffl(roster, m["body"] + "\n" + m["subject"])
               or store_by_recipient(roster, m["to"] + "\n" + m["body"])
               or store_by_name(roster, m["body"]))
        if not key:
            log("SKIP inbound, store not identified: " + m["subject"][:90])
            continue
        order = ""
        mo = re.search(r"Order\s+(\d+)", m["subject"])
        if mo:
            order = mo.group(1)
        buyer = ""
        mb = re.search(r"([A-Z][A-Za-z.\-']+(?:\s+[A-Z][A-Za-z.\-']+){1,2})\s+made a purchase", m["body"])
        if mb:
            buyer = mb.group(1).strip()
        rows.append((m["msgid"], roster["stores"][key]["name"], buyer, order))
    if not rows:
        return 0
    rows.sort(key=lambda r: r[1])
    body = ["*Online orders shipping to us*"]
    for _, store, buyer, order in rows:
        bits = [store]
        if buyer:
            bits.append(buyer)
        if order:
            bits.append("order " + order)
        body.append("• " + " · ".join(bits))
    body.append("Watch for these to arrive and call the customer when they land.")
    if slack_post(GUN_TRANSFERS, "\n".join(body)):
        now = dt.datetime.now().isoformat(timespec="seconds")
        for mid, _, _, _ in rows:
            state["inbound"][mid] = now
        log("posted inbound digest: %d transfer(s)" % len(rows))
        return len(rows)
    return 0


# ------------------------------------------------------- job 3: expiry reply
def looks_like_expiry_request(m, roster):
    pats = roster.get("expiry_warning_patterns", {})
    senders = [s.lower() for s in pats.get("known_senders", [])]
    frm = m["from"].lower()
    if not any(s in frm for s in senders):
        return False
    subj = m["subject"]
    rx = pats.get("subject_regex") or r"(?i)(ffl|license).*(expir|update|renew)"
    return bool(re.search(rx, subj))


def job_expiry_autoreply(roster, msgs, state):
    sent = 0
    for m in msgs:
        if m["msgid"] in state["expiry_replies"]:
            continue
        if not looks_like_expiry_request(m, roster):
            continue
        if SEED or too_old(m):
            state["expiry_replies"][m["msgid"]] = "seeded"
            continue
        blob = m["subject"] + "\n" + m["body"] + "\n" + m["to"]
        key = (store_by_ffl(roster, blob)
               or store_by_recipient(roster, m["to"])
               or store_by_name(roster, blob))
        if not key:
            log("SKIP expiry request, store not identified: " + m["subject"][:90])
            continue
        s = roster["stores"][key]
        path = license_path(roster, key)
        if not path:
            log("SKIP expiry request, no license file for " + key)
            continue
        # never send a license that really is expired
        try:
            exp = dt.date.fromisoformat(s["expires"])
        except Exception:
            exp = None
        if exp and exp <= dt.date.today():
            log("HOLD %s license is genuinely expired (%s) — not auto-replying" % (key, s["expires"]))
            slack_dm("Heads up - the %s license needs renewing before we can send it to anyone. "
                     "A dealer just asked for a current copy." % s["name"])
            state["expiry_replies"][m["msgid"]] = "held"
            continue
        addr = re.search(r"[\w.+-]+@[\w.-]+\.\w+", m["from"])
        if not addr:
            continue
        to_addr = addr.group(0)
        # cooldown — a helpdesk auto-acknowledging our reply must not start a loop
        domain = to_addr.split("@")[-1].lower()
        ck = domain + ":" + key
        prev = state["vendor_sends"].get(ck)
        if prev:
            try:
                if (dt.date.today() - dt.date.fromisoformat(prev[:10])).days < VENDOR_COOLDOWN_DAYS:
                    log("SKIP %s copy to %s — sent %s, inside cooldown" % (key, domain, prev[:10]))
                    state["expiry_replies"][m["msgid"]] = "cooldown"
                    continue
            except Exception:
                pass
        exp_str = exp.strftime("%-m/%-d/%Y") if exp else s["expires"]
        body = ("Current signed FFL for our %s store attached.\n\n"
                "%s, %s, expires %s. Type 02 Pawnbroker.\n"
                "%s\n%s   %s\nHours %s. Transfer fee $25.\n\n"
                "Joshua Davis\nFull Circle Finance Inc DBA Valley Pawn"
                % (s["name"], s["name"], s["ffl"], exp_str,
                   s["address"], s["phone"], s["email"], s["hours"]))
        subject = m["subject"]
        if not subject.lower().startswith("re:"):
            subject = "Re: " + subject
        if send_reply(to_addr, subject, body, [path], cc="jdavis@fcfpawn.com"):
            state["expiry_replies"][m["msgid"]] = dt.datetime.now().isoformat(timespec="seconds")
            state["vendor_sends"][ck] = dt.date.today().isoformat()
            sent += 1
            log("auto-replied license request: %s -> %s" % (s["name"], to_addr))
            # record on the roster
            for v in roster["vendors"]:
                if any(d in to_addr.lower() for d in v.get("domains", [])):
                    v["copy_version"] = roster.get("copy_version_current")
                    v["last_sent"] = dt.date.today().isoformat()
                    v.setdefault("listed", {})[key] = "copy-sent-" + dt.date.today().isoformat()
    if sent:
        save_json(ROSTER, roster)
    return sent


# ------------------------------------------------------- job 4: expiry ladder
def job_expiration_ladder(roster, state):
    today = dt.date.today()
    fired = []
    for key, s in roster["stores"].items():
        try:
            exp = dt.date.fromisoformat(s["expires"])
        except Exception:
            continue
        days = (exp - today).days
        for th in LADDER_DAYS:
            if days <= th:
                mark = "%s:%d" % (key, th)
                if mark in state["ladder"]:
                    continue
                if s.get("closed"):
                    msg = ("The %s firearms license is still active on ATF's system and expires %s "
                           "(%d days). That store is closed, so this is about whether it gets "
                           "formally wound down rather than just left to lapse."
                           % (s["name"].replace(" (CLOSED store)", ""),
                              exp.strftime("%b %-d, %Y"), days))
                elif days < 0:
                    msg = ("The %s firearms license shows an expiration date that has passed. "
                           "Worth confirming with ATF today." % s["name"])
                elif days <= 14:
                    msg = ("%s firearms license expires in %d days (%s). The renewal has to be "
                           "postmarked before then." % (s["name"], days, exp.strftime("%b %-d, %Y")))
                elif days <= 90:
                    msg = ("%s firearms license expires %s, about %d days out. ATF mails the "
                           "renewal form to the Florida address - watch for it there."
                           % (s["name"], exp.strftime("%b %-d, %Y"), days))
                else:
                    msg = ("%s firearms license expires %s, about four months out. ATF should mail "
                           "the renewal form to Florida around %s."
                           % (s["name"], exp.strftime("%b %-d, %Y"),
                              (exp - dt.timedelta(days=90)).strftime("%b %-d")))
                if slack_dm(msg):
                    state["ladder"][mark] = today.isoformat()
                    fired.append(mark)
                    # Mark every LOOSER threshold fired too. Without this, a
                    # license discovered late (Salem: found at 25 days, i.e.
                    # already past 120/90/60/30) would DM once per run for four
                    # consecutive runs about the same date.
                    for looser in LADDER_DAYS:
                        if looser > th:
                            state["ladder"].setdefault("%s:%d" % (key, looser), "skipped-past")
                break   # only the tightest unfired threshold per store per run
    return fired


# ------------------------------------------------------------------- status
def write_status(roster, counts):
    today = dt.date.today()
    soonest = None
    for key, s in roster["stores"].items():
        try:
            exp = dt.date.fromisoformat(s["expires"])
        except Exception:
            continue
        d = (exp - today).days
        if soonest is None or d < soonest[1]:
            soonest = (s["name"], d, s["expires"])
    total = current = 0
    for v in roster["vendors"]:
        total += 1
        if v.get("copy_version") == roster.get("copy_version_current"):
            current += 1
    save_json(STATUS, {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "next_expiration": {"store": soonest[0], "days": soonest[1], "date": soonest[2]} if soonest else None,
        "vendors_total": total,
        "vendors_holding_current_copy": current,
        "transfers_relayed_this_run": counts.get("relayed", 0),
        "inbound_transfers_this_run": counts.get("inbound", 0),
        "license_copies_sent_this_run": counts.get("expiry", 0),
    })


# --------------------------------------------------------------------- main
def main():
    log("=== ffl-guardian start%s" % (" (dry-run)" if DRY else ""))
    roster = load_roster()
    if roster is None:
        return 2
    state = load_json(STATE, new_state())
    for k in new_state():
        state.setdefault(k, {} if k != "last_run" else None)

    paths = recent_emlx(lookback_days())
    log("scanned %d recent messages" % len(paths))
    msgs = []
    for p in paths:
        m = parse_emlx(p)
        if m:
            msgs.append(m)

    counts = {}
    try:
        counts["relayed"] = job_web_form_relay(roster, msgs, state)
    except Exception as e:
        log("ERROR web-form relay: " + str(e))
        counts["relayed"] = 0
    try:
        counts["inbound"] = job_inbound_digest(roster, msgs, state)
    except Exception as e:
        log("ERROR inbound digest: " + str(e))
        counts["inbound"] = 0
    try:
        counts["expiry"] = job_expiry_autoreply(roster, msgs, state)
    except Exception as e:
        log("ERROR expiry autoreply: " + str(e))
        counts["expiry"] = 0
    try:
        fired = job_expiration_ladder(roster, state)
    except Exception as e:
        log("ERROR expiration ladder: " + str(e))
        fired = []

    state["last_run"] = dt.datetime.now().isoformat(timespec="seconds")
    save_json(STATE, state)
    try:
        write_status(roster, counts)
    except Exception as e:
        log("ERROR status write: " + str(e))

    log("done: relayed=%d inbound=%d copies_sent=%d ladder=%s"
        % (counts.get("relayed", 0), counts.get("inbound", 0),
           counts.get("expiry", 0), ",".join(fired) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
