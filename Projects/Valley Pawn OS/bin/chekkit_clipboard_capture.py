#!/usr/bin/env python3
"""chekkit_clipboard_capture.py [minutes] — ONE-TIME setup helper (2026-10-05). For up to N minutes (default 45),
watch the Mac clipboard ONLY for Chekkit API tokens (exact shape chk_ + 60-70 letters/digits/_; anything else is never
read further or sent anywhere). Each new token is checked against GET /v1/leaderboard to learn which store it belongs
to, saved in the Keychain as vp-chekkit-token-<CODE>, the clipboard is cleared, and a Mac notification says which
store was saved. Stops when all five stores have a working token. Never prints or logs a token."""
import datetime as dt, hashlib, json, re, subprocess, sys, time, urllib.request
PAT = re.compile(r"^chk_[A-Za-z0-9_]{60,70}$")
CODES = {"Culpeper": "CUL", "Waynesboro": "WAY", "Harrisonburg": "HAR", "Lexington": "LEX", "Roanoke": "ROA"}
def have(code):
    return bool(subprocess.run(["security", "find-generic-password", "-s", "vp-chekkit-token-" + code, "-w"], capture_output=True, text=True).stdout.strip())
def notify(msg):
    subprocess.run(["osascript", "-e", 'display notification "%s" with title "Valley Pawn — Chekkit" sound name "Glass"' % msg])
def whose(tok):
    t = dt.date.today()
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://api.chekkit.io/v1/leaderboard?from=%s&to=%s" % (t - dt.timedelta(days=7), t),
                                   headers={"Authorization": "Bearer " + tok, "User-Agent": "ValleyPawnOps/1.0"}), timeout=20)
        return json.load(r)["location"]["name"]
    except Exception:
        return None
mins = float(sys.argv[1]) if len(sys.argv) > 1 else 45
end = time.time() + mins * 60
seen = set()
notify("Ready — create a token in Chekkit and click its copy button. I'll save it automatically.")
while time.time() < end:
    missing = [c for c in CODES.values() if not have(c)]
    if not missing:
        notify("All 5 stores connected. You're done!"); print("all 5 saved"); break
    clip = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout.strip()
    if PAT.match(clip):
        fp = hashlib.sha256(clip.encode()).hexdigest()[:8]
        if fp not in seen:
            seen.add(fp)
            name = whose(clip)
            code = next((c for n, c in CODES.items() if name and n in name), None)
            if not code:
                notify("That token didn't work — create a new one and copy it again."); print("invalid token", fp)
            else:
                subprocess.run(["security", "delete-generic-password", "-s", "vp-chekkit-token-" + code], capture_output=True)
                subprocess.run(["security", "add-generic-password", "-s", "vp-chekkit-token-" + code, "-a", "valleypawn", "-w", clip, "-U"], capture_output=True)
                subprocess.run(["pbcopy"], input="", text=True)
                left = [n for n, c in CODES.items() if not have(c)]
                notify("%s saved ✓  Still needed: %s" % (name.replace("Valley Pawn - ", "").replace("Valley Pawn-", ""), ", ".join(left) or "none"))
                print("saved", code, fp)
    time.sleep(1)
print("stopped; saved:", [c for c in CODES.values() if have(c)])
