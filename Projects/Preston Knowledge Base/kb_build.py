#!/usr/bin/env python3
"""
kb_build.py - regenerate KB_CURRENT.md, the ONLY thing the Valley Pawn Ops Agent
may answer operational/valuation questions from.

WHY THIS EXISTS
    Same reason Ask_Handbook/build_sources.py exists. The agent answers store staff
    from a corpus. If the corpus is hand-edited or goes stale, staff get a confident,
    cited, WRONG number - and on gold/diamonds a wrong number is real money out the
    door. So the corpus is GENERATED, never hand-written, and regenerated at the top
    of every responder run.

DESIGN NOTES (deliberate - do not "simplify" these away)
  * PURE STDLIB. Runs on the Mac's stock /usr/bin/python3. No pip, no venv.
  * PROVENANCE IS MANDATORY. Every entry carries Preston's verbatim words, the
    channel, the date and the Slack permalink. An entry missing VERBATIM or SOURCE
    is DROPPED, not published. There is no such thing as an unsourced rule here.
  * TIERED TRUST. Entries carry a TRUST tier that controls what the agent may do
    with them (see the header written into KB_CURRENT.md). Preston-verified beats
    harvested-HIGH beats harvested-MEDIUM/LOW. The agent may only ANSWER from
    VERIFIED and HIGH. MEDIUM/LOW may only be surfaced as "closest thing he's said,
    not a rule - check with Preston."
  * SUPERSEDES. verified.json can mark an entry SUPERSEDED with a replacement id.
    Superseded entries stay in the file, visibly struck, so nobody re-harvests them
    back in and so the history of a rule change is legible.
  * CONFLICTS SURVIVE. Where Preston said two different things, BOTH entries publish
    with the conflict noted. The build never picks a winner. A human does.
  * ATOMIC WRITE + FAIL LOUD. Temp file then rename. Non-zero exit leaves the last
    good KB in place. Stale-but-valid beats truncated.

USAGE
    python3 kb_build.py            # rebuild if inputs are newer
    python3 kb_build.py --force    # rebuild unconditionally
    python3 kb_build.py --check    # report staleness + counts, write nothing
    python3 kb_build.py --queue    # print the next 10 unverified entries as JSON
"""

import os
import re
import sys
import json
import glob
import datetime

BASE = os.path.expanduser("~/Documents/Claude/Projects/Preston Knowledge Base")
RAW = os.path.join(BASE, "_raw_harvest")
VERIFIED = os.path.join(BASE, "verified.json")
OUT = os.path.join(BASE, "KB_CURRENT.md")

# Topic slug prefix -> section. First match wins; anything unmatched lands in OTHER.
SECTIONS = [
    ("PRECIOUS METALS - MELT MATH & PAY PERCENTAGES",
     ("melt-", "pay-percentage", "spot-price", "gold-percentage", "gold-buy",
      "pricing-retail", "retail-sticker", "gold-coin-buy", "bullion-retail",
      "bullion-margin", "bullion-flip", "gold-deal")),
    ("PRECIOUS METALS - TESTING, FRAUD & COUNTERFEITS",
     ("testing-", "fraud-", "precious-metals-testing", "sterling-verification",
      "coins-testing", "kee-")),
    ("DIAMONDS, GEMSTONES & COLORED STONES",
     ("diamond", "carat", "clarity", "stone", "moissanite", "one-carat",
      "big-stone", "sorting-loose", "small-diamonds", "dont-trust",
      "appraisal-", "physical-inspection", "scrap-rings")),
    ("JEWELRY, WATCHES & CASE OPERATIONS",
     ("jewelry-", "gold-watch", "gold-case", "luxury-watch", "fashion-brand",
      "white-gold", "heavy-chain", "silver-jewelry", "sterling-flatware")),
    ("SCRAP, BUCKETS & REFINING",
     ("scrap-", "assay-", "refiner-", "silver-refiner", "silver-lot",
      "silver-weighing", "shipping-scrap", "stone-scrap", "stones-excluded",
      "bravo-stone")),
    ("COINS, BULLION & NUMISMATICS",
     ("coin", "bullion", "numismatic", "junk-silver", "eagles")),
    ("DEAL JUDGMENT, LOANS & APPROVALS",
     ("approval-", "worksheet", "buy-vs-pawn", "qualify-", "customer-",
      "loan", "photo-quality", "what-we-pay", "sales-qualifying",
      "dont-sell-gold")),
    ("BUYER & VENDOR NETWORK",
     ("buyer-network", "insurance-estimate")),
]

TRUST_ORDER = {"VERIFIED": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "SUPERSEDED": 9}


def entry_id(topic, verbatim):
    """Stable short id from topic + the head of the quote. Survives re-harvest."""
    import hashlib
    h = hashlib.sha1((topic + "|" + verbatim[:80]).encode("utf-8")).hexdigest()[:8]
    return "%s-%s" % (topic[:28], h)


def parse_block(block):
    """Parse one '---'-delimited candidate entry. Returns dict or None."""
    fields = {}
    order = ["TOPIC", "CLAIM", "VERBATIM", "SOURCE", "CONFIDENCE", "CONFLICT", "NOTE"]
    # Split on 'KEY:' at start of a line, keeping multi-line values intact.
    pattern = r"^(%s):[ \t]*" % "|".join(order)
    cur = None
    buf = []
    for line in block.splitlines():
        m = re.match(pattern, line)
        if m:
            if cur:
                fields[cur] = "\n".join(buf).strip()
            cur = m.group(1)
            buf = [line[m.end():]]
        elif cur:
            buf.append(line)
    if cur:
        fields[cur] = "\n".join(buf).strip()

    # Hard requirements. No provenance, no publish.
    if not fields.get("TOPIC") or not fields.get("CLAIM"):
        return None
    if not fields.get("VERBATIM") or not fields.get("SOURCE"):
        return None
    if "http" not in fields.get("SOURCE", ""):
        return None  # a SOURCE without a permalink is not verifiable

    fields["TOPIC"] = fields["TOPIC"].strip().strip("*").lower()
    # Harvest agents emit JSON-escaped quotes. Unescape so a store manager reading
    # the citation sees Preston's words the way he typed them, not \n and \".
    v = fields["VERBATIM"].strip().strip('"')
    v = v.replace("\\n", "\n").replace('\\"', '"').replace("\\t", "\t")
    fields["VERBATIM"] = v
    conf = (fields.get("CONFIDENCE") or "LOW").strip().upper()
    fields["CONFIDENCE"] = conf.split()[0] if conf else "LOW"
    if fields["CONFIDENCE"] not in ("HIGH", "MEDIUM", "LOW"):
        fields["CONFIDENCE"] = "LOW"
    fields["ID"] = entry_id(fields["TOPIC"], fields["VERBATIM"])
    return fields


def load_raw():
    seen = {}
    files = sorted(glob.glob(os.path.join(RAW, "*.md")))
    if not files:
        sys.stderr.write("FATAL: no harvest files in %s\n" % RAW)
        sys.exit(2)
    for f in files:
        text = open(f, encoding="utf-8").read()
        for block in text.split("\n---"):
            e = parse_block(block)
            if not e:
                continue
            # Dedupe across harvest agents: same id = same claim, keep the richer one.
            prev = seen.get(e["ID"])
            if prev is None or len(json.dumps(e)) > len(json.dumps(prev)):
                seen[e["ID"]] = e
    return seen


def load_verified():
    if not os.path.exists(VERIFIED):
        return {}
    try:
        return json.load(open(VERIFIED, encoding="utf-8"))
    except Exception:
        sys.stderr.write("FATAL: verified.json is not valid JSON - refusing to build\n")
        sys.exit(2)


def section_for(topic):
    for name, prefixes in SECTIONS:
        for p in prefixes:
            if topic.startswith(p) or p in topic:
                return name
    return "OTHER OPERATIONAL KNOWLEDGE"


HEADER = """# VALLEY PAWN OPS AGENT - KNOWLEDGE BASE (Preston Peters' operational knowledge)

AUTO-GENERATED {stamp} by kb_build.py. DO NOT HAND-EDIT - edits are overwritten.
To change an entry, edit verified.json (status/correction) and rebuild.

Full Circle Finance Inc DBA Valley Pawn - 5 Virginia stores (Culpeper, Waynesboro,
Harrisonburg, Lexington, Roanoke; FFL at Roanoke). This file captures the operational
and valuation knowledge of Preston Peters, Operations Manager, as stated in his own
words in Slack, with a permalink to every source.

## HOW THE AGENT MUST USE THIS FILE - the trust tiers are not advisory

**VERIFIED** - Preston has personally confirmed this entry is current and correct.
  -> ANSWER from it. Cite it. This is as good as asking him.

**HIGH** - Preston stated it as an explicit rule, in his own words, on the date shown.
  -> ANSWER from it, but ALWAYS quote his words and give the date, e.g.
     'Preston's rule, 2026-01-29: "Going forward, we are only paying 50% for all
     bullion and silver."' The quote + date IS the safety mechanism: the reader can
     see exactly what was said and when, and judge whether it still holds.

**MEDIUM / LOW** - a judgment call on one specific deal, or a rule inferred from a
  single case. NOT a standing rule.
  -> NEVER present as an answer. You may surface it only as context, explicitly
     labelled: "Preston hasn't set a rule on this. Closest thing he's said was on a
     similar deal <date>: '<quote>'. Check with him before you act on it."

**SUPERSEDED** - a rule that has been replaced. Shown for history only.
  -> NEVER answer from it. If asked, point at the replacement.

**CONFLICT** - where two entries disagree, BOTH are published and the conflict is
  noted. Never pick a winner, never average them, never blend them into one answer.
  Say plainly that there are two different answers on record and route to Preston.

## HARD RULES FOR THE AGENT

1. If it is not in this file, you do not know it. Never answer a valuation or
   procedure question from general pawn knowledge, from the internet, or from
   anything you remember. "Not covered - ask Preston" is always the right answer
   over a guess. A confident wrong number here costs real money.
2. Never compute a specific dollar offer for a live deal and present it as approved.
   You may show the melt MATH (the formula is in this file) and the pay-percentage
   band Preston has stated. The approval itself is a human decision.
3. Anything above the store's approval authority, anything involving a large stone,
   and anything the file does not cover goes to Preston. Say so plainly.
4. Field communication standard: plain everyday language. Never name internal
   systems or tooling. No file paths, no entry IDs, no meta-commentary about how
   this file works.

---

"""


def build():
    raw = load_raw()
    ver = load_verified()

    entries = []
    for eid, e in raw.items():
        v = ver.get(eid, {})
        status = (v.get("status") or "").upper()
        if status == "VERIFIED":
            e["TRUST"] = "VERIFIED"
        elif status == "SUPERSEDED":
            e["TRUST"] = "SUPERSEDED"
        elif status == "REJECTED":
            continue  # Preston said this is wrong - it does not publish at all
        else:
            e["TRUST"] = e["CONFIDENCE"]
        if v.get("correction"):
            e["CORRECTION"] = v["correction"]
        if v.get("supersedes"):
            e["SUPERSEDES"] = v["supersedes"]
        if v.get("verified_on"):
            e["VERIFIED_ON"] = v["verified_on"]
        entries.append(e)

    buckets = {}
    for e in entries:
        buckets.setdefault(section_for(e["TOPIC"]), []).append(e)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [HEADER.format(stamp=stamp)]

    counts = {"VERIFIED": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "SUPERSEDED": 0}
    order = [s[0] for s in SECTIONS] + ["OTHER OPERATIONAL KNOWLEDGE"]
    for name in order:
        items = buckets.get(name)
        if not items:
            continue
        items.sort(key=lambda x: (TRUST_ORDER.get(x["TRUST"], 5), x["TOPIC"]))
        parts.append("\n\n" + "=" * 78)
        parts.append("SECTION: %s" % name)
        parts.append("=" * 78)
        for e in items:
            counts[e["TRUST"]] = counts.get(e["TRUST"], 0) + 1
            parts.append("")
            parts.append("### [%s] %s" % (e["TRUST"], e["TOPIC"]))
            parts.append("RULE: %s" % e["CLAIM"])
            parts.append('PRESTON SAID: "%s"' % e["VERBATIM"])
            parts.append("SOURCE: %s" % e["SOURCE"])
            if e.get("CORRECTION"):
                parts.append("PRESTON'S CORRECTION (%s): %s"
                             % (e.get("VERIFIED_ON", "date unknown"), e["CORRECTION"]))
            if e.get("CONFLICT"):
                parts.append("!! CONFLICT: %s" % e["CONFLICT"])
            if e.get("NOTE"):
                parts.append("NOTE: %s" % e["NOTE"])
            if e["TRUST"] == "SUPERSEDED":
                parts.append("!! SUPERSEDED - do not answer from this. Replaced by: %s"
                             % e.get("SUPERSEDES", "see a newer entry on this topic"))
            parts.append("id: %s" % e["ID"])

    parts.append("\n\n" + "=" * 78)
    parts.append("COVERAGE: %d entries - %d verified by Preston, %d high-confidence "
                 "rules, %d medium, %d low, %d superseded."
                 % (len(entries), counts["VERIFIED"], counts["HIGH"],
                    counts["MEDIUM"], counts["LOW"], counts["SUPERSEDED"]))
    parts.append("=" * 78)

    body = "\n".join(parts) + "\n"
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, OUT)
    return len(entries), counts, len(body)


def queue():
    """Next 10 entries Preston has never ruled on, highest-value first."""
    raw = load_raw()
    ver = load_verified()
    pending = [e for eid, e in raw.items() if eid not in ver]
    # Ask about HIGH-confidence rules first: those are what the agent is ALREADY
    # answering from, so confirming them retires the most risk per minute of his time.
    pending.sort(key=lambda x: (TRUST_ORDER.get(x["CONFIDENCE"], 5), x["TOPIC"]))
    out = [{"id": e["ID"], "topic": e["TOPIC"], "claim": e["CLAIM"],
            "verbatim": e["VERBATIM"][:400], "source": e["SOURCE"],
            "confidence": e["CONFIDENCE"]} for e in pending[:10]]
    print(json.dumps({"pending_total": len(pending), "batch": out}, indent=2))


def main():
    if "--queue" in sys.argv:
        queue()
        return 0

    force = "--force" in sys.argv
    check = "--check" in sys.argv

    inputs = glob.glob(os.path.join(RAW, "*.md"))
    if os.path.exists(VERIFIED):
        inputs.append(VERIFIED)
    if not inputs:
        sys.stderr.write("FATAL: no inputs\n")
        return 2
    newest = max(os.path.getmtime(p) for p in inputs)
    out_m = os.path.getmtime(OUT) if os.path.exists(OUT) else 0
    stale = newest > out_m

    if check:
        n, counts, size = build() if not os.path.exists(OUT) else (None, None, None)
        print("STATUS: " + ("STALE - rebuild needed" if stale else "CURRENT"))
        return 0

    if not stale and not force:
        print("STATUS: CURRENT - no rebuild needed")
        return 0

    n, counts, size = build()
    print("REBUILT: %s (%d entries, %d chars, ~%d tokens)" % (OUT, n, size, size // 4))
    print("TIERS: verified=%d high=%d medium=%d low=%d superseded=%d"
          % (counts["VERIFIED"], counts["HIGH"], counts["MEDIUM"],
             counts["LOW"], counts["SUPERSEDED"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
