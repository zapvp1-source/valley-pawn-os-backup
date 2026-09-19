#!/usr/bin/env python3
"""vp_slack.py — the ONE Slack primitive for native (no-Claude) scripts. Uses the vp_ops_engine
bot token from Keychain (service vp-ops-slack-bot-token). stdlib only.

  vp_slack.py dm  "<text>"                    one plain DM to Joshua
  vp_slack.py post <channel_id> "<text>"      post text verbatim to a channel (bot must be a member)
  vp_slack.py post <channel_id> --file <p>    post the contents of file <p> verbatim (multi-line safe)
  vp_slack.py upload <channel_or_user_id> <path> "<title>"   upload a file (xlsx etc.)
  vp_slack.py has <channel_id> "<marker>" [hours]   exit 0 if a message containing marker exists in the last N hours (default 24)

Exit 0 = Slack accepted it. Non-zero = not delivered (reason on stderr). Never posts on error.
Rule 16 lives in the CALLER: this tool sends exactly what it is given.
"""
import getpass, json, os, subprocess, sys, time, urllib.request, urllib.parse

JOSHUA = "U03BB52MDSA"
SVC = "vp-ops-slack-bot-token"


def token():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", SVC, "-a", getpass.getuser(), "-w"],
                           capture_output=True, text=True, timeout=10)
        t = r.stdout.strip()
        if t.startswith("xox"):
            return t
    except Exception:
        pass
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if t.startswith("xox"):
        return t
    sys.exit("no slack bot token")


def call(method, payload=None, params=None, raw=False):
    tok = token()
    url = "https://slack.com/api/" + method
    if payload is not None:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    else:
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=30))


def dm_channel(user):
    r = call("conversations.open", {"users": user})
    if not r.get("ok"):
        sys.exit("conversations.open: " + r.get("error", "?"))
    return r["channel"]["id"]


def receipt(surface, target, ok, nbytes=0, note=""):
    """Record that this task published (see bin/vp_receipt.py). Keyed off $VP_TASK, which the
    launchd agents already export as their agent name. A DM is invisible to the audit bot, so
    without this line a delivered DM and a task that never ran are indistinguishable.
    Best-effort by design: a receipt failure must NEVER take down a real publication."""
    task = os.environ.get("VP_TASK", "").strip()
    if not task:
        return
    try:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "vp_receipt.py"), "write", task, "--surface", surface, "--target", target,
                        "--bytes", str(nbytes), "--ok", "true" if ok else "false", "--note", note],
                       capture_output=True, timeout=10)
    except Exception:
        pass


def dryrun_intercept(surface, target, text):
    """Fleet-wide publish guard (bin/vp_dryrun.py). Returns True if this send was DIVERTED.
    Fails OPEN on purpose: if the guard cannot be read, a real publication still goes out. A
    publication silently swallowed by a broken guard is a worse outcome than one extra Slack post."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import vp_dryrun
        task = os.environ.get("VP_TASK", "").strip()
        if not vp_dryrun.active_for(task):
            return False
        p = vp_dryrun.divert(task, surface, target, text)
        print("DRY RUN — not sent. Would have gone to %s. Written to %s" % (target, p))
        return True
    except Exception:
        return False


def post(channel, text):
    if not text.strip():
        sys.exit("refusing to post empty text")
    surface = "slack-dm" if channel.startswith("D") else "slack"
    if dryrun_intercept(surface, channel, text):
        return
    r = call("chat.postMessage", {"channel": channel, "text": text, "unfurl_links": False})
    if not r.get("ok"):
        receipt("slack", channel, False, len(text.encode()), "chat.postMessage: " + r.get("error", "?"))
        sys.exit("chat.postMessage: " + r.get("error", "?"))
    receipt("slack-dm" if channel.startswith("D") else "slack", channel, True, len(text.encode()),
            text.strip().splitlines()[0][:120])
    print(r.get("ts", ""))


def upload(target, path, title):
    size = os.path.getsize(path)
    if dryrun_intercept("file-upload", target, "(binary) %s — %d bytes, title: %s"
                        % (os.path.basename(path), size, title)):
        return
    r = call("files.getUploadURLExternal", params={"filename": os.path.basename(path), "length": size})
    if not r.get("ok"):
        sys.exit("getUploadURLExternal: " + r.get("error", "?"))
    with open(path, "rb") as f:
        req = urllib.request.Request(r["upload_url"], data=f.read(), method="POST")
        urllib.request.urlopen(req, timeout=60).read()
    ch = dm_channel(target) if target.startswith("U") else target
    r2 = call("files.completeUploadExternal",
              {"files": [{"id": r["file_id"], "title": title}], "channel_id": ch})
    if not r2.get("ok"):
        receipt("file-upload", ch, False, size, "completeUploadExternal: " + r2.get("error", "?"))
        sys.exit("completeUploadExternal: " + r2.get("error", "?"))
    receipt("file-upload", ch, True, size, os.path.basename(path))
    print(r["file_id"])


def has(channel, marker, hours):
    oldest = str(time.time() - hours * 3600)
    r = call("conversations.history", params={"channel": channel, "oldest": oldest, "limit": 200})
    if not r.get("ok"):
        sys.exit("conversations.history: " + r.get("error", "?"))
    return any(marker in (m.get("text") or "") for m in r.get("messages", []))


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "dm":
        post(dm_channel(JOSHUA), a[1])
    elif cmd == "post":
        ch = a[1]
        text = open(a[3], encoding="utf-8").read() if len(a) > 3 and a[2] == "--file" else a[2]
        post(ch, text)
    elif cmd == "upload":
        upload(a[1], a[2], a[3] if len(a) > 3 else os.path.basename(a[2]))
    elif cmd == "last":   # last <channel_id> [n]  — raw text of the last n messages (debug)
        r = call("conversations.history", params={"channel": a[1], "limit": int(a[2]) if len(a) > 2 else 3})
        for m in r.get("messages", []):
            print("---", m.get("ts"), m.get("user") or m.get("bot_id"), "subtype=", m.get("subtype"), "len=", len(m.get("text") or ""))
            print((m.get("text") or "")[:300])
    elif cmd == "has":
        sys.exit(0 if has(a[1], a[2], float(a[3]) if len(a) > 3 else 24) else 1)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
