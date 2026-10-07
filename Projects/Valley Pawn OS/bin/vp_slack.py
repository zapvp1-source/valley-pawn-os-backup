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


def to_mrkdwn(text):
    """Standard markdown -> Slack mrkdwn, the same conversion Claude's Slack connector applies to what a
    Cowork task sends. Without it a bot post shows **bold** and [text](url) literally, so a report moved
    to a native agent would stop looking like the one it replaced (Joshua 2026-09-30: formatting must
    be the same). Code blocks (``` ... ```) are left untouched — the table formatters rely on them."""
    import re
    parts = re.split(r"(```.*?```)", text, flags=re.S)
    for i, seg in enumerate(parts):
        if seg.startswith("```"):
            continue
        seg = re.sub(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)", r"<\2|\1>", seg)          # [t](u) -> <u|t>
        seg = re.sub(r"\*\*(?=\S)([^*\n]+?)(?<=\S)\*\*", r"*\1*", seg)                   # **b** -> *b*
        seg = re.sub(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", r"*\1*", seg)                     # ## h -> *h*
        seg = re.sub(r"~~(?=\S)([^~\n]+?)(?<=\S)~~", r"~\1~", seg)                      # ~~s~~ -> ~s~
        parts[i] = seg
    return "".join(parts)


def _cell(txt):
    """One table cell as rich_text; **bold** / *bold* markers become a bold style (as the connector does)."""
    import re
    t = txt.strip()
    m = re.fullmatch(r"\*\*(.+)\*\*|\*(.+)\*", t)
    mi = None if m else re.fullmatch(r"_(\S(?:.*\S)?)_", t)   # _x_ = italic, as the connector renders it (2026-10-06)
    el = {"type": "text", "text": (m.group(1) or m.group(2)) if m else (mi.group(1) if mi else t)}
    if m:
        el["style"] = {"bold": True}
    elif mi:
        el["style"] = {"italic": True}
    if not el["text"]:
        el["text"] = " "
    return {"type": "rich_text", "elements": [{"type": "rich_text_section", "elements": [el]}]}


def to_blocks(text):
    """If the message (outside code fences) contains a markdown table, return Block Kit blocks that render it
    as a native Slack table — exactly what Claude's Slack connector produces (verified on the 2026-09-01 FFL
    post: section + 'table' block of rich_text cells). Returns None when there is no table. Slack allows one
    table per message; a second table stays as text."""
    import re
    lines = text.split("\n")
    in_code, start = False, None
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if (l.strip().startswith("|") and i + 1 < len(lines)
                and re.fullmatch(r"\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*", lines[i + 1])):
            start = i
            break
    if start is None:
        return None
    end = start + 2
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    def cells(l):
        return [c for c in l.strip().strip("|").split("|")]
    rows = [cells(lines[start])] + [cells(l) for l in lines[start + 2:end]]
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    if len(rows) > 100 or width > 20:
        return None
    blocks = []
    before, after = "\n".join(lines[:start]).strip("\n"), "\n".join(lines[end:]).strip("\n")
    for chunk in (before,):
        if chunk.strip():
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": to_mrkdwn(chunk)[:3000]}})
    blocks.append({"type": "table", "rows": [[_cell(c) for c in r] for r in rows]})
    if after.strip():
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": to_mrkdwn(after)[:3000]}})
    return blocks


def post(channel, text):
    if not text.strip():
        sys.exit("refusing to post empty text")
    if os.environ.get("VP_SLACK_RAW") != "1":
        text = to_mrkdwn(text)
    surface = "slack-dm" if channel.startswith("D") else "slack"
    if dryrun_intercept(surface, channel, text):
        return
    payload = {"channel": channel, "text": text, "unfurl_links": False}
    blocks = None if os.environ.get("VP_SLACK_RAW") == "1" else to_blocks(text)
    if blocks:
        payload["blocks"] = blocks          # native Slack table, like the connector; text stays the fallback
    r = call("chat.postMessage", payload)
    if not r.get("ok") and blocks:          # a table Slack rejects must never cost the post itself
        payload.pop("blocks", None)
        r = call("chat.postMessage", payload)
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
    # No "oldest" param: on 2026-10-05 the same oldest-bounded call returned the messages once and an
    # empty list the next second, and the guard missed a duplicate. Read the newest 100 and filter by ts.
    cutoff = time.time() - hours * 3600
    r = call("conversations.history", params={"channel": channel, "limit": 100})
    if not r.get("ok"):
        sys.exit("conversations.history: " + r.get("error", "?"))
    return any(marker in (m.get("text") or "") for m in r.get("messages", []) if float(m.get("ts", 0)) >= cutoff)


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
