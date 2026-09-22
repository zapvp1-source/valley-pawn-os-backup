#!/usr/bin/env python3
"""fda_probe.py — can the NATIVE agent path read Apple Mail?

WHY (2026-09-21): this one question gates two separate things that have both been failing:
  * `daily-unopened-email-eval` — worst task in the fleet (1 of 7 days). It needs Mail read-state,
    which lives ONLY in Apple Mail's Envelope Index, not in the unified-search index (that has no
    read/unread column — checked, it does not).
  * the nightly unified-search mail rebuild, which has NEVER succeeded from launchd.
Both were blamed on Full Disk Access for ~/bin/vp-runner. That was stated as the leading cause but
never actually proven — the CHANGELOG says the proof is "one ls run through vp-runner from a
launchd context." This is that test. Run it through the host job queue, which executes under
vp-runner, and the answer is a fact instead of a theory.
"""
import glob, os, sqlite3, sys
HOME = os.path.expanduser("~")
print("running as uid=%s" % os.getuid())
mail = os.path.join(HOME, "Library/Mail")
print("\n1. list ~/Library/Mail")
try:
    print("   OK:", sorted(os.listdir(mail))[:6])
except Exception as e:
    print("   DENIED: %s: %s" % (type(e).__name__, e))
print("\n2. locate the Envelope Index (holds read/unread state)")
envs = glob.glob(os.path.join(mail, "V*/MailData/Envelope Index"))
print("   found:", envs or "none")
if envs:
    p = envs[0]
    print("\n3. open it read-only and count unread")
    try:
        c = sqlite3.connect("file:%s?mode=ro" % p.replace(" ", "%20"), uri=True)
        tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
        print("   tables:", tabs[:10])
        if "messages" in tabs:
            cols = [r[1] for r in c.execute("PRAGMA table_info(messages)")]
            print("   messages cols:", cols[:14])
            flag = "read" if "read" in cols else ("flags" if "flags" in cols else None)
            if flag == "read":
                n = c.execute("select count(*) from messages where read=0").fetchone()[0]
                print("   UNREAD COUNT: %d" % n)
            else:
                print("   no obvious read column; would need flag decoding")
        print("\n   VERDICT: NATIVE AGENTS CAN READ MAIL — no connector needed.")
    except Exception as e:
        print("   DENIED opening the index: %s: %s" % (type(e).__name__, e))
        print("\n   VERDICT: vp-runner lacks Full Disk Access. One GUI grant unblocks BOTH")
        print("   daily-unopened-email-eval AND the nightly unified-search mail rebuild.")
else:
    print("\n   VERDICT: cannot even see the Mail folder — Full Disk Access is missing.")

# Messages is a SEPARATE protected store with its own TCC treatment. The 04:50 unified-search-verify
# row blames "Apple Mail and Messages" together; proving Mail readable does NOT prove Messages is.
# Claiming a complete correction off a partial test is the error this whole effort keeps fixing.
print("\n4. Messages (~/Library/Messages/chat.db) — tested separately from Mail")
chat = os.path.join(HOME, "Library/Messages/chat.db")
try:
    cc = sqlite3.connect("file:%s?mode=ro" % chat, uri=True)
    n = cc.execute("select count(*) from message").fetchone()[0]
    print("   OK — message rows: %d" % n)
    print("   VERDICT: Messages is READABLE too. FDA is not the blocker for either source.")
except Exception as e:
    print("   DENIED: %s: %s" % (type(e).__name__, e))
    print("   VERDICT: Mail is readable but MESSAGES IS NOT — the FDA correction is PARTIAL.")
    print("   The nightly rebuild's Messages step genuinely needs a grant; its Mail step does not.")
