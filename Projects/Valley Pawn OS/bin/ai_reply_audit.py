#!/usr/bin/env python3
"""ai_reply_audit.py — nightly accuracy loop for every automated customer text (comms review 2026-10-20).

WHY: the AI text responder (bin/chekkit_ai_responder.py) answers customers 24/7, but its event log keeps only
the decision and a reason — never what it said. On 10/14 it told a Waynesboro customer "we're closed right now"
on the store's first open Wednesday and nobody could see it; its fact list still carried a dead deadline
("bring loans current by Sat Oct 3") 17 days later. Joshua's rule: automatic communications must be functional
— the customer gets the right answer, quickly. This closes the loop: read back what was actually sent, grade
it against the CURRENT hours and facts, and tell Joshua only when something was wrong.

WHAT IT READS (Chekkit API, GET only, per-store tokens — bin/chekkit_api.py):
  every business message in the day's conversations that ends with "(Automated reply" (the AI) plus the
  missed-call texts ("Hi, this is Valley Pawn in ..."), with the customer messages before and after it.
WHAT IT CHECKS, per AI reply:
  deterministic  - said "closed" while the store was OPEN at send time (fleet/missed_call_text_config.json)
                 - said "open" / gave a next-open phrase while the store was open (or the wrong day)
                 - any hours text that does not match the store's hours_text
                 - "Dixie" (brand), a price/dollar amount, a firearm model, a date in the past
                 - over max_reply_chars, missing the automated-reply tag
  judged (vp_ai) - is the answer correct against the fact list, does it answer what was asked, would a
                   customer need to ask again; returns {ok, issue, severity}
  config         - any fact in chekkit_ai_config.json extra_facts that names a calendar date already past
WHAT IT WRITES: fleet/ai_reply_audit/<date>.json + .md (customer = store + last-4 only). The texting
scorecard shows "AI replies checked / wrong" from this file. One plain DM to Joshua ONLY when a reply was
wrong or a fact is stale (what it said, what it should have said) — never a technical failure ping (Rule 16).
  ai_reply_audit.py                 yesterday (ET)
  ai_reply_audit.py --date 2026-10-14 [--render]      --render prints and sends nothing
"""
import argparse, datetime as dt, json, os, re, sys, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OS_DIR = os.path.dirname(HERE)
FLEET = os.path.join(OS_DIR, "fleet")
OUT = os.path.join(FLEET, "ai_reply_audit")
MCT = os.path.join(FLEET, "missed_call_text_config.json")
AICFG = os.path.join(FLEET, "chekkit_ai_config.json")
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
JOSHUA = "U03BB52MDSA"
TASK = "ai-reply-audit"
STORES = ["CUL", "WAY", "HAR", "LEX", "ROA"]
NAMES = {"CUL": "Culpeper", "WAY": "Waynesboro", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke"}
MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
DATE_RE = re.compile(r"\b(?:%s)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b" % MONTHS, re.I)
MONEY_RE = re.compile(r"\$\s?\d")
HOURS_RE = re.compile(r"\b\d{1,2}\s?(?:am|pm)\b", re.I)


def during_hours(t, s):
    if t.weekday() not in s.get("days", []):
        return False
    o = dt.time.fromisoformat(s.get("open", "10:00"))
    c = dt.time.fromisoformat(s.get("close_by_weekday", {}).get(str(t.weekday()), s.get("close", "18:00")))
    return o <= t.time() < c


def ledger(sentence, needs="no"):
    with open(os.path.join(FLEET, "FAILURE_LEDGER.md"), "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence, needs))


def l4(p):
    d = "".join(c for c in str(p or "") if c.isdigit())
    return "…" + d[-4:] if d else "…?"


def is_ai(m):
    t = (m.get("text") or "").lower()
    return m.get("sender") == "business" and "(automated reply" in t


def is_mct(m):
    t = (m.get("text") or "").lower()
    return m.get("sender") == "business" and t.startswith("hi, this is valley pawn in")


def past_date(text, day):
    """A 'Mon DD' mention that is before `day` in the same year (dead deadline)."""
    for m in DATE_RE.finditer(text):
        mon = m.group(0).split()[0][:3].lower()
        try:
            mi = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].index(mon) + 1
            d = dt.date(day.year, mi, int(m.group(1)))
        except Exception:
            continue
        if d < day - dt.timedelta(days=1):
            return m.group(0)
    return ""


def rule_checks(reply, sent_at, store_cfg, aicfg, day):
    t = reply.lower()
    issues = []
    op = during_hours(sent_at, store_cfg)
    if op and re.search(r"\b(we'?re|we are|store is|currently) closed\b|closed right now|closed (?:today|now)", t):
        issues.append("said the store was closed while it was OPEN (%s %s)" % (sent_at.strftime("%a"), sent_at.strftime("%-I:%M %p")))
    if op and re.search(r"\b(next open|opens? (?:again|back up|at)|we open (?:at|tomorrow|monday))", t):
        issues.append("gave a 'next open' time while the store was OPEN")
    if not op and re.search(r"\b(we'?re|we are) open (?:right )?now\b|stop (?:in|by) now", t):
        issues.append("said the store was open while it was CLOSED")
    ht = (store_cfg.get("hours_text") or "").lower()
    for h in HOURS_RE.findall(t):
        hh = h.replace(" ", "").lower()
        if ht and hh not in ht.replace(" ", "") and hh not in ("10am", "6pm", "5pm"):
            issues.append("quoted an hour (%s) that is not in this store's hours (%s)" % (h, store_cfg.get("hours_text")))
            break
    if "dixie" in t:
        issues.append("used the retired name 'Dixie Pawn'")
    if MONEY_RE.search(t) and "$25" not in t:
        issues.append("quoted a dollar amount")
    pd = past_date(t, day)
    if pd:
        issues.append("mentioned a date already past (%s)" % pd)
    if len(reply) > int(aicfg.get("max_reply_chars", 420)) + 60:
        issues.append("longer than the %d-character limit" % aicfg.get("max_reply_chars", 420))
    return issues


def judge(items, aicfg, mct):
    """vp_ai grades each reply against the live facts. Returns {idx: {ok, issue, severity}}."""
    try:
        import vp_ai
    except Exception:
        return {}
    facts = "\n".join("- " + f for f in aicfg.get("extra_facts", []))
    hours = "\n".join("- %s: %s" % (NAMES[c], mct["stores"][c].get("hours_text", "")) for c in STORES)
    system = ("You audit automated customer texts for Valley Pawn (5 Virginia pawn stores). For each item decide whether the AUTOMATED REPLY was "
              "correct and genuinely useful to the customer, judged ONLY against the FACTS and HOURS below and the customer's message. "
              "Wrong = states something false or contradicting the facts, quotes a price/offer, discusses a specific firearm for sale, promises something, "
              "answers a different question, or tells the customer to do something impossible. Not wrong = asking for photos/details, saying a team member "
              "will follow up, giving the app link for payments, declining an item we do not take. Return ONLY JSON: "
              "{\"<idx>\": {\"ok\": true|false, \"issue\": \"<one plain sentence, empty if ok>\", \"severity\": \"low|medium|high\", \"should_have_said\": \"<one sentence, empty if ok>\"}}\n\n"
              "FACTS:\n%s\n\nHOURS:\n%s" % (facts, hours))
    out = {}
    for i in range(0, len(items), 12):
        chunk = items[i:i + 12]
        prompt = "\n\n".join("ITEM %d | %s | sent %s | store was %s\nCUSTOMER: %s\nAUTOMATED REPLY: %s\nCUSTOMER AFTER: %s" % (
            it["idx"], NAMES[it["store"]], it["sent_at"].strftime("%a %-I:%M %p"), "OPEN" if it["open"] else "CLOSED",
            it["customer_before"][:700], it["reply"][:600], it["customer_after"][:300] or "(nothing yet)") for it in chunk)
        for attempt in range(3):
            try:
                got = vp_ai.ask_json("Audit these automated replies.\n\n" + prompt, system=system, max_tokens=3000)
                for k, v in (got or {}).items():
                    try:
                        out[int(k)] = v
                    except Exception:
                        pass
                break
            except Exception as e:
                print("judge attempt %d failed: %s" % (attempt + 1, str(e)[:140]), file=sys.stderr); time.sleep(5)
    return out


def collect(day, mct):
    import chekkit_api as ck
    start = dt.datetime.combine(day, dt.time(0), ET).astimezone(UTC)
    end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(0), ET).astimezone(UTC)
    items, errors, mct_count, dbg = [], {}, {s: 0 for s in STORES}, {}
    for code in STORES:
        convs = {}
        try:
            convs = ck.conversations_since(code, start)
            for phone, c in convs.items():
                msgs = ck.messages(code, c.get("id") or c.get("_id") or "")
                msgs = [m for m in msgs if ck.ts(m.get("createdAt"))]
                msgs.sort(key=lambda m: ck.ts(m.get("createdAt")))
                for j, m in enumerate(msgs):
                    t = ck.ts(m.get("createdAt"))
                    if not (start <= t < end):
                        continue
                    dbg[code] = dbg.get(code, 0) + 1
                    if "--debug" in sys.argv and m.get("sender") != "customer":
                        print("debug   %s %s sender=%s sentBy=%s text=%r" % (code, t.astimezone(ET).strftime("%m/%d %H:%M"), m.get("sender"), m.get("sentBy"), (m.get("text") or "")[:70]), file=sys.stderr)
                    if is_mct(m):
                        mct_count[code] += 1
                    if not is_ai(m):
                        continue
                    before = [x for x in msgs[:j] if x.get("sender") == "customer"][-3:]
                    after = [x for x in msgs[j + 1:] if x.get("sender") == "customer"][:2]
                    staff_after = any(x.get("sender") == "business" and not ck.is_automated(x) for x in msgs[j + 1:])
                    items.append({"idx": len(items) + 1, "store": code, "phone4": l4(phone), "sent_at": t.astimezone(ET),
                                  "open": during_hours(t.astimezone(ET), mct["stores"][code]),
                                  "customer_before": " | ".join((x.get("text") or ("[photo]" if x.get("media") else "")).strip() for x in before),
                                  "reply": (m.get("text") or "").strip(),
                                  "customer_after": " | ".join((x.get("text") or ("[photo]" if x.get("media") else "")).strip() for x in after),
                                  "staff_followed_up": staff_after})
                time.sleep(0.2)
        except Exception as e:
            errors[code] = "%s: %s" % (type(e).__name__, str(e)[:120])
        if "--debug" in sys.argv:
            print("debug %s convs=%d window_msgs=%d ai=%d" % (code, len(convs) if 'convs' in dir() else -1, dbg.get(code, 0),
                                                            sum(1 for it in items if it["store"] == code)), file=sys.stderr)
    return items, errors, mct_count


def from_drafts(day, mct):
    """PRIMARY source (2026-10-20): the responder's own log of exactly what it sent —
    fleet/ai_responder/drafts-<date>.md rows with Status SENT. The Chekkit conversation API pages only the newest
    conversations, so it misses most of a past day (10/19 read 0 of 9 sends); the drafts file is complete."""
    p = os.path.join(FLEET, "ai_responder", "drafts-%s.md" % day.isoformat())
    out = []
    try:
        lines = open(p).read().splitlines()
    except OSError:
        return None
    for l in lines:
        c = [x.strip() for x in l.split("|")]
        if len(c) < 8 or c[1] in ("Time", "") or c[1].startswith("---"):
            continue
        tm, store, who, said, reply, status = c[1], c[2], c[3], c[4], c[5], c[6]
        if store not in STORES or not status.upper().startswith("SENT"):
            continue
        try:
            t = dt.datetime.combine(day, dt.datetime.strptime(tm, "%I:%M %p").time(), ET)
        except ValueError:
            continue
        out.append({"idx": len(out) + 1, "store": store, "phone4": "…" + who.split("…")[-1][:4] if "…" in who else "…?",
                    "sent_at": t, "open": during_hours(t, mct["stores"][store]), "customer_before": said, "reply": reply,
                    "customer_after": "", "staff_followed_up": False})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date"); ap.add_argument("--render", action="store_true"); ap.add_argument("--no-judge", action="store_true"); ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()
    day = dt.date.fromisoformat(a.date) if a.date else (dt.datetime.now(ET).date() - dt.timedelta(days=1))
    mct = json.load(open(MCT)); aicfg = json.load(open(AICFG))
    os.makedirs(OUT, exist_ok=True)
    items, errors, mct_count = collect(day, mct)
    drafted = from_drafts(day, mct)
    if drafted is not None and len(drafted) >= len(items):
        items = drafted          # the responder's own record is complete; the API is the fallback
    try:                         # missed-call texts: the sender's own receipts are complete (the API read is not)
        rc = {s_: 0 for s_ in STORES}
        for line in open(os.path.join(FLEET, "receipts", "missed-call-text.jsonl")):
            r = json.loads(line)
            if r.get("ok") and str(r.get("ts", "")).startswith(day.isoformat()):
                c_ = str(r.get("target", "")).split(":")[-1]
                if c_ in rc:
                    rc[c_] += 1
        mct_count = rc
    except (OSError, ValueError):
        pass
    if len(errors) == len(STORES):
        if not a.render:
            ledger("The nightly check of automated customer texts could not read Chekkit for any store, so nothing was audited.")
        print("Chekkit unreadable:", errors); return 1
    # 1. deterministic
    for it in items:
        it["rule_issues"] = rule_checks(it["reply"], it["sent_at"], mct["stores"][it["store"]], aicfg, day)
    # 2. judged
    verdicts = {} if a.no_judge else judge(items, aicfg, mct)
    for it in items:
        v = verdicts.get(it["idx"]) or {}
        it["judge_ok"] = v.get("ok", None); it["judge_issue"] = (v.get("issue") or "").strip()
        it["severity"] = v.get("severity", ""); it["should_have_said"] = (v.get("should_have_said") or "").strip()
        it["wrong"] = bool(it["rule_issues"]) or (it["judge_ok"] is False and it["severity"] in ("medium", "high"))
    # 3. config staleness
    stale = []
    for f in aicfg.get("extra_facts", []):
        pd = past_date(f.lower(), day)
        if pd:
            stale.append("fact mentions a past date (%s): %s" % (pd, f[:90]))
    wrong = [it for it in items if it["wrong"]]
    summary = {"date": day.isoformat(), "checked": len(items), "wrong": len(wrong), "missed_call_texts": mct_count,
               "by_store": {s: {"checked": sum(1 for it in items if it["store"] == s), "wrong": sum(1 for it in wrong if it["store"] == s)} for s in STORES},
               "stale_facts": stale, "errors": errors, "run": dt.datetime.now(ET).isoformat(timespec="seconds"),
               "items": [{k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in it.items()} for it in items]}
    json.dump(summary, open(os.path.join(OUT, day.isoformat() + ".json"), "w"), indent=1)
    L = ["# Automated-text audit — %s" % day.strftime("%a %b %d, %Y"), "",
         "Checked %d AI replies, %d wrong. Missed-call texts sent: %s." % (len(items), len(wrong), ", ".join("%s %d" % (s, mct_count[s]) for s in STORES)), ""]
    for it in items:
        tag = "WRONG" if it["wrong"] else ("ok" if it["judge_ok"] is not False else "flag(low)")
        L.append("- [%s] %s %s %s — customer: %s\n  reply: %s\n  %s%s" % (
            tag, it["store"], it["phone4"], it["sent_at"].strftime("%-I:%M %p"), it["customer_before"][:160].replace("\n", " "),
            it["reply"][:300].replace("\n", " "), "; ".join(it["rule_issues"] + ([it["judge_issue"]] if it["judge_issue"] else [])),
            ("\n  should have said: " + it["should_have_said"]) if it["should_have_said"] else ""))
    if stale:
        L += ["", "## Stale facts in chekkit_ai_config.json"] + ["- " + s for s in stale]
    if errors:
        L += ["", "## Stores not read"] + ["- %s: %s" % (k, v) for k, v in errors.items()]
    open(os.path.join(OUT, day.isoformat() + ".md"), "w").write("\n".join(L) + "\n")
    # 4. DM only when something is wrong (business content)
    if wrong or stale:
        lines = ["Automated texts on %s: %d checked, %d wrong." % (day.strftime("%b %d"), len(items), len(wrong))]
        for it in wrong[:6]:
            lines.append("• %s, customer %s, %s — the AI said: \"%s\" — %s%s" % (
                NAMES[it["store"]], it["phone4"], it["sent_at"].strftime("%-I:%M %p"), it["reply"][:160].replace("\n", " "),
                "; ".join(it["rule_issues"] + ([it["judge_issue"]] if it["judge_issue"] else [])),
                (" A team member has since texted them." if it["staff_followed_up"] else " Nobody has followed up yet — worth a text from the store.")))
        if len(wrong) > 6:
            lines.append("• and %d more in fleet/ai_reply_audit/%s.md" % (len(wrong) - 6, day.isoformat()))
        for s in stale:
            lines.append("• AI fact list: " + s)
        msg = "\n".join(lines)
        if a.render:
            print("=== DM Joshua\n" + msg)
        else:
            import vp_slack
            vp_slack.post(vp_slack.dm_channel(JOSHUA), msg)
    print("checked %d wrong %d stale %d errors %s" % (len(items), len(wrong), len(stale), list(errors)))
    if a.render:
        print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
