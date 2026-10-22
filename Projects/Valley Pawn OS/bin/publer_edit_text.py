#!/usr/bin/env python3
"""publer_edit_text.py <publer_id> <account_key> <new_text_file> [--apply] — change ONLY the caption of one SCHEDULED
Publer post (2026-10-21, daily social fact-check). Refuses published posts. Runs the vp_social caption QA for that
account first (firearms, hours, GBP rules, giveaway pause ...). Backs up the original to fleet/_backups/publer_edits/.
Never changes time, account, media or state; never deletes. Without --apply: dry run."""
import json, os, sys, datetime as dt
RSM = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects")) + "/Refine Social Media"
OS_DIR = os.environ.get("VP_PROJECTS", os.path.expanduser("~/Documents/Claude/Projects")) + "/Valley Pawn OS"
sys.path.insert(0, RSM); os.chdir(RSM)
from publer_client import PublerClient  # noqa: E402
from vp_social.publish import qa_caption  # noqa: E402
pid, acct, path = sys.argv[1], sys.argv[2], sys.argv[3]
apply = "--apply" in sys.argv
new = open(path, encoding="utf-8").read().strip()
p = PublerClient()
cur = p.get(f"/posts/{pid}")
post = cur.get("post", cur) if isinstance(cur, dict) else {}
if post.get("state") != "scheduled":
    print("REFUSED: post is not scheduled (state=%s)" % post.get("state")); sys.exit(2)
min_words = 20 if not acct.startswith("Brand") else 12
probs = qa_caption(new, acct, "status", min_words)
if probs:
    print("REFUSED by caption QA:", "; ".join(probs)); sys.exit(3)
bk = os.path.join(OS_DIR, "fleet/_backups/publer_edits"); os.makedirs(bk, exist_ok=True)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
json.dump(post, open(os.path.join(bk, f"{pid}_{stamp}.json"), "w"), indent=1, default=str)
if not apply:
    print("DRY RUN OK — would set text (%d chars) on %s %s" % (len(new), acct, pid)); sys.exit(0)
p.put(f"/posts/{pid}", json={"post": {"text": new}})
after = p.get(f"/posts/{pid}"); after = after.get("post", after)
ok = (after.get("text") or "").strip() == new and after.get("scheduled_at") == post.get("scheduled_at") and after.get("state") == "scheduled"
print("APPLIED" if ok else "APPLIED-BUT-VERIFY-FAILED", pid, acct, after.get("scheduled_at"))
sys.exit(0 if ok else 4)
