#!/usr/bin/env python3
"""vp_canvas_section.py — department "landing page" canvases for the Slack Restructure (2026-11-09).

One bot-owned canvas per department, tabbed in its channel. Every publication routed with action
"headline" writes its FULL body into its own section of that canvas (replacing last time's), and the
channel only gets a 5-line headline + "Full table -> canvas". The canvas never scrolls away; Drive
keeps history (the publishers already write their files there).

State: fleet/canvas_state/dept_canvases.json   {dept: {id, channel, title, url}}
       fleet/canvas_state/dept_sections/<dept>.json  {section_key: {"md": ..., "updated": ISO}}
Whole-document replace on every write (same approach as weekly_canvases.py — the only edit mode that
has proven reliable with the bot token).

CLI:  vp_canvas_section.py ensure            create any missing department canvas (idempotent)
      vp_canvas_section.py status            print the mapping
      vp_canvas_section.py write <dept> <section_key> <file>   (manual / test)
"""
import datetime as dt, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack

OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(OS_DIR, "fleet", "canvas_state")
IDS = os.path.join(STATE_DIR, "dept_canvases.json")
SECTIONS_DIR = os.path.join(STATE_DIR, "dept_sections")

# dept key -> (channel id, title). Channel ids survive renames, so Phase 2 renames need no change here.
DEPTS = {
    "scoreboard": ("C03CGTN3KN1", ":bar_chart: Scoreboard — store & employee performance (live)"),
    "loans":      ("C04N24STDP1", ":clipboard: Loans & Layaways (live)"),
    "aged":       ("C04NGH4FF35", ":package: Aged Inventory & Markdowns (live)"),
    "marketing":  ("C0BMRC2LN3D", ":mega: Marketing — web, social, email, eBay, reviews (live)"),
    "leadership": ("C0B26GD8D2R", ":briefcase: Leadership Reports (live)"),
    "daily":      ("C0B3R9B3S8H", ":white_check_mark: Daily Checks — funds, jewelry, texts, calls (live)"),
    "selftest":   ("C0BLQSABGGY", ":test_tube: Route self-test canvas (ignore)"),   # private #vp-ops-shadow only
}


def _load(p, default):
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def ensure(dept):
    """Return {id, channel, title, url} for dept, creating the canvas if needed."""
    ids = _load(IDS, {})
    if dept in ids and ids[dept].get("id"):
        return ids[dept]
    ch, title = DEPTS[dept]
    md = "# %s\n\n_Updated automatically. Each report below is replaced in place when it runs; history is in Google Drive._\n" % title
    r = vp_slack.call("canvases.create", {"title": title, "channel_id": ch,
                                          "document_content": {"type": "markdown", "markdown": md}})
    if not r.get("ok"):
        raise RuntimeError("canvases.create %s: %s %s" % (dept, r.get("error"), r.get("detail") or ""))
    cid = r["canvas_id"]
    vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "read", "channel_ids": [ch]})
    vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "write", "user_ids": [vp_slack.JOSHUA]})
    info = vp_slack.call("files.info", params={"file": cid})
    url = ((info.get("file") or {}).get("permalink")) or ""
    ids[dept] = {"id": cid, "channel": ch, "title": title, "url": url, "created": dt.datetime.now().isoformat(timespec="seconds")}
    _save(IDS, ids)
    return ids[dept]


def url_for(dept):
    ids = _load(IDS, {})
    return (ids.get(dept) or {}).get("url", "")


def mrkdwn_to_canvas(text):
    """Slack mrkdwn body -> canvas markdown. *b* -> **b**, <url|t> -> [t](url), code fences kept."""
    parts = re.split(r"(```.*?```)", text, flags=re.S)
    out = []
    for seg in parts:
        if seg.startswith("```"):
            out.append(seg); continue
        seg = re.sub(r"<(https?://[^|>]+)\|([^>]+)>", r"[\2](\1)", seg)
        seg = re.sub(r"<(https?://[^>]+)>", r"\1", seg)
        seg = re.sub(r"(?<![*\w])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![*\w])", r"**\1**", seg)
        seg = re.sub(r"(?m)^• ", "- ", seg)
        # canvas markdown folds single newlines into one paragraph; keep each report line on its own
        # line by separating plain-text lines with a blank line (tables and list items stay contiguous).
        lines = seg.split("\n"); fixed = []
        for i, l in enumerate(lines):
            fixed.append(l)
            st = l.strip(); nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            kind = lambda t: "t" if t.startswith("|") else ("l" if (t.startswith("- ") or t.startswith("* ") or re.match(r"^\d+\. ", t)) else "p")
            if st and nxt and (kind(st) != kind(nxt) or kind(st) == "p"):
                fixed.append("")
        out.append("\n".join(fixed))
    return "".join(out)


def render(dept, sections):
    ch, title = DEPTS[dept]
    now = dt.datetime.now().strftime("%a %b %-d, %-I:%M %p")
    md = ["_Updated %s. Each report is replaced in place when it runs; the channel carries only the headline. History: Google Drive._" % now, ""]
    for key, sec in sorted(sections.items(), key=lambda kv: kv[1].get("updated", ""), reverse=True):
        md.append("## %s" % key)
        md.append("_as of %s_" % sec.get("updated_h", sec.get("updated", "")))
        md.append("")
        md.append(sec["md"].strip())
        md.append("")
        md.append("---")
        md.append("")
    return "\n".join(md)


def write(rule, full_text):
    """Called by vp_slack for action=headline. rule['canvas'] = dept key; rule['section_key'] or marker."""
    dept = rule["canvas"]
    key = rule.get("section_key") or rule.get("marker") or rule.get("id")
    meta = ensure(dept)
    p = os.path.join(SECTIONS_DIR, dept + ".json")
    secs = _load(p, {})
    now = dt.datetime.now()
    secs[key] = {"md": mrkdwn_to_canvas(full_text), "updated": now.isoformat(timespec="seconds"),
                 "updated_h": now.strftime("%a %b %-d, %-I:%M %p")}
    md = render(dept, secs)
    if vp_slack.dryrun_intercept("canvas", meta["id"], md):
        return "dry"
    r = vp_slack.call("canvases.edit", {"canvas_id": meta["id"], "changes": [
        {"operation": "replace", "document_content": {"type": "markdown", "markdown": md}}]})
    if not r.get("ok"):
        vp_slack.receipt("canvas", meta["id"], False, len(md.encode()), "canvases.edit: %s" % r.get("error"))
        raise RuntimeError("canvases.edit %s: %s" % (dept, r.get("error")))
    _save(p, secs)
    vp_slack.receipt("canvas", meta["id"], True, len(md.encode()), "%s / %s" % (dept, key))
    return True


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["ensure"]:
        for d in DEPTS:
            if d == "selftest":
                continue
            m = ensure(d); print(d, m["id"], m["url"])
    elif a[:1] == ["status"]:
        print(json.dumps(_load(IDS, {}), indent=1))
    elif a[:1] == ["write"] and len(a) == 4:
        print(write({"canvas": a[1], "section_key": a[2]}, open(a[3], encoding="utf-8").read()))
    else:
        print(__doc__)
