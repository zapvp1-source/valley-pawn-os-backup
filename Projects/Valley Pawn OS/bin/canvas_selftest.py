#!/usr/bin/env python3
"""canvas_selftest.py create [--post-date D] | delete <canvas_id> ... — prove the native canvas write path on
SCRATCH canvases, never the live ones (2026-10-06).

create: for each weekly canvas (loan, layaway, employee, aged, store) render the markdown exactly as
weekly_canvases.py would, canvases.create a private scratch canvas titled "VP canvas self-test — <kind>"
holding a placeholder, then apply the SAME canvases.edit whole-document replace the live job sends, confirm it
with canvases.sections.lookup, and give Joshua read access so the result can be read back and compared.
Prints the scratch canvas ids. No receipts, no DMs, no channel posts.
delete: canvases.delete each scratch id (only ids whose title starts "VP canvas self-test").
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

os.environ["VP_TASK"] = "canvas-selftest"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "delete":
        for cid in sys.argv[2:]:
            info = vp_slack.call("files.info", params={"file": cid})
            title = (info.get("file") or {}).get("title", "")
            if not title.startswith("VP canvas self-test"):
                print(cid, "REFUSED — not a self-test canvas (%r)" % title)
                continue
            r = vp_slack.call("canvases.delete", {"canvas_id": cid})
            print(cid, "deleted" if r.get("ok") else "delete failed: %s" % r.get("error"))
        return 0
    import weekly_canvases as wc
    if sys.argv[1] == "titles":   # read-only: the live canvases' titles
        for cid in ("F0BH6BJ0PK7", "F0BJ48BMZGQ", "F0BH9UK284S", "F0BHDL6AULU", "F0BH6S9U5FX"):
            f = vp_slack.call("files.info", params={"file": cid}).get("file") or {}
            print(cid, repr(f.get("title")), f.get("filetype"), "channels=%s" % (f.get("channels") or f.get("groups")))
        return 0
    if sys.argv[1] == "probe2":   # date syntax variants on ONE scratch canvas
        c = vp_slack.call("canvases.create", {"title": "VP canvas self-test — dates",
                          "document_content": {"type": "markdown", "markdown": "start"}})
        cid = c.get("canvas_id")
        print("create", c.get("ok") or c.get("error"), cid)
        import calendar
        ts = calendar.timegm(dt.datetime(2026, 10, 5, 16, 0).timetuple())
        for label, txt in (("A slack_date", "A ![](slack_date:2026-10-05)"),
                           ("B mrkdwn date", "B <!date^%d^{date_short}|Oct 5, 2026>" % ts),
                           ("C plain", "C 2026-10-05"),
                           ("D table", "|a|b|\n|---|---|\n|1|2|"),
                           ("E heading emoji", "# :large_green_circle: Status — Week of x"),
                           ("F bold-italic", "*Company total (all store sales): **$1.00***")):
            r = vp_slack.call("canvases.edit", {"canvas_id": cid, "changes": [
                {"operation": "insert_at_end", "document_content": {"type": "markdown", "markdown": txt}}]})
            print(" ", label, r.get("ok") or r.get("error"), r.get("detail") or "")
        vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "read", "user_ids": [vp_slack.JOSHUA]})
        return 0
    if sys.argv[1] == "probe":   # which canvases.edit shapes does Slack accept? (scratch canvases only)
        md = wc.render_aged("2026-10-05", True)[0]
        def new(content):
            c = vp_slack.call("canvases.create", {"title": "VP canvas self-test — probe",
                              "document_content": {"type": "markdown", "markdown": content}})
            print("  create:", c.get("ok") or c.get("error"), c.get("canvas_id"))
            return c.get("canvas_id")
        def ed(cid, ch, label):
            r = vp_slack.call("canvases.edit", {"canvas_id": cid, "changes": [ch]})
            print("  %s: %s %s" % (label, r.get("ok") or r.get("error"), r.get("detail") or r.get("response_metadata") or ""))
            return r.get("ok")
        def look(cid, crit, label):
            r = vp_slack.call("canvases.sections.lookup", {"canvas_id": cid, "criteria": crit})
            print("  lookup %s: %s %s" % (label, r.get("ok") or r.get("error"), r.get("sections")))
            return r.get("sections") or []
        print("A create with the full rendered markdown")
        a = new(md)
        if a:
            look(a, {"contains_text": "Waynesboro"}, "text=Waynesboro (no type)")
            look(a, {"contains_text": "Policy"}, "text=Policy")
            look(a, {"section_types": ["any_header"]}, "any_header")
            look(a, {"contains_text": "Retail value by age"}, "caption")
            print("B whole-doc replace, plain text")
            ed(a, {"operation": "replace", "document_content": {"type": "markdown", "markdown": "hello"}}, "replace(no id) 'hello'")
        print("C placeholder canvas + insert_at_end full markdown")
        c = new("placeholder")
        if c:
            ed(c, {"operation": "insert_at_end", "document_content": {"type": "markdown", "markdown": md}}, "insert_at_end md")
            ed(c, {"operation": "replace", "document_content": {"type": "markdown", "markdown": md}}, "replace(no id) md")
            hs = look(c, {"section_types": ["any_header"]}, "headers")
            if hs:
                ed(c, {"operation": "replace", "section_id": hs[0]["id"], "document_content": {"type": "markdown",
                       "markdown": "# 📋 Aged Inventory Review — Current\n\nsecond line"}}, "replace(header id) two blocks")
        for cid in (a, c):
            if cid:
                vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "read", "user_ids": [vp_slack.JOSHUA]})
                print("probe canvas", cid)
        return 0
    pd =sys.argv[sys.argv.index("--post-date") + 1] if "--post-date" in sys.argv else dt.date.today().isoformat()
    fns = {"loan": wc.render_loan, "layaway": wc.render_layaway, "employee": wc.render_employee,
           "aged": wc.render_aged, "store": wc.render_store}
    for kind, fn in fns.items():
        os.environ["VP_TASK"] = "canvas-selftest"
        try:
            md = fn(pd, True)[0]
        except wc.Hold as e:
            print(kind, "HOLD —", e)
            continue
        c = vp_slack.call("canvases.create", {"title": "VP canvas self-test — %s" % kind,
                                               "document_content": {"type": "markdown", "markdown": "placeholder"}})
        if not c.get("ok"):
            print(kind, "create failed:", c.get("error"))
            continue
        cid = c["canvas_id"]
        e = vp_slack.call("canvases.edit", {"canvas_id": cid, "changes": [
            {"operation": "replace", "document_content": {"type": "markdown", "markdown": md}}]})
        first_h = [l for l in md.splitlines() if l.startswith("# ")][0]
        import re
        probe = re.sub(r":[a-z0-9_]+:|#", "", first_h).strip().split(" — ")[0]
        lk = vp_slack.call("canvases.sections.lookup", {"canvas_id": cid, "criteria": {"contains_text": probe}})
        a = vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "read", "user_ids": [vp_slack.JOSHUA]})
        print("%s %s edit=%s lookup(%r)=%s sections=%d access=%s" % (kind, cid, e.get("ok") or e.get("error"), probe,
              lk.get("ok") or lk.get("error"), len(lk.get("sections") or []), a.get("ok") or a.get("error")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
