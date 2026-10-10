#!/usr/bin/env python3
"""
ask_vp_responder.py — Ask Valley Pawn: the real-time, corpus-only answer agent for the staff question channel.

Runs every 15 s from launchd (com.valleypawn.ask-vp via bin/ask_vp_responder.sh). Each run:
  1. rebuilds the corpus if any source changed (bin/ask_vp_corpus.py — cheap no-op otherwise; a failed
     build means NO answers this run, never answers from a stale file),
  2. reads new top-level messages in the question channel (as the Goldilocks / VP OPS ENGINE bot),
  3. for each real question: retrieves the best-matching corpus passages (BM25, stdlib), asks Claude for an
     answer that may ONLY use those passages and must cite them by id, then validates the answer in code:
        - status "answer" needs >= 1 cited passage of answerable trust (POLICY / VERIFIED / HIGH / ACADEMY /
          FACT / LIVE); MEDIUM / LOW passages can only be surfaced as context; SUPERSEDED never
        - every cite must be one of the passages that were actually retrieved (no invented sources)
        - no machinery words, file paths or ids in the reply (Field Communication Standard v3)
        - no approved-offer language on a live deal
     Any failed check downgrades the reply to the plain "not written down — ask your manager / Preston" line
     (Rule 18: withhold, don't caveat). The source line under every answer is written by THIS code from the
     cited ids, never by the model.
  4. delivers: MODE=SHADOW -> one DM to Joshua showing the question and the reply it would have posted;
               MODE=LIVE   -> threaded reply under the question in the channel.
  5. appends a row to Ask Valley Pawn/QUESTION_LOG.md (NOT-FOUND rows are the interview list) and
     advances fleet/state/ask_vp/state.json.

Hard lines (do not "simplify" away):
  * Corpus only. The model never sees anything but retrieved passages. No web, no memory, no general knowledge.
  * Never a specific dollar offer presented as approved. Melt MATH may be shown (live spot from
    Valley Pawn OS/spot_prices.json) with Preston's band; the approval is a human's.
  * Out of scope -> route, don't answer: pay, schedule, PTO balance, discipline, disputes, financials, books,
    real estate, personal. The channel cannot approve exceptions.
  * Rule 16: failures are silent in Slack. Technical detail goes to the log; nothing to any team channel.
  * Customer data never enters here: the corpus has none, and the question text is never written anywhere but
    the question log (which store staff do not read).

USAGE
  ask_vp_responder.py                 one poll (what launchd runs)
  ask_vp_responder.py --ask "q" [--store Culpeper]   answer one question to stdout, no Slack
  ask_vp_responder.py --selftest      run selftest/questions.json -> selftest/<stamp>.md, no Slack
  ask_vp_responder.py --status        print config, state, corpus status
"""
import datetime
import json
import math
import os
import re
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, "Documents/Claude/Projects")
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BASE = os.path.join(PROJ, "Ask Valley Pawn")
CORPUS = os.path.join(BASE, "corpus", "ASK_VP_CORPUS.jsonl")
CONFIG = os.path.join(BASE, "config.json")
QLOG = os.path.join(BASE, "QUESTION_LOG.md")
SELFTEST_DIR = os.path.join(BASE, "selftest")
STATE_DIR = os.path.join(OS_DIR, "fleet", "state", "ask_vp")
STATE = os.path.join(STATE_DIR, "state.json")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
SPOT = os.path.join(OS_DIR, "spot_prices.json")
LOG = os.path.join(HOME, "Library", "Logs", "valleypawn", "ask-vp.log")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")

JOSHUA = "U03BB52MDSA"
PRESTON = "U03BWMEM9GR"
PY = sys.executable or "/usr/bin/python3"

sys.path.insert(0, BIN)
try:
    import vp_ai        # Claude via Keychain key (vp-agent-anthropic-key)
    import vp_slack     # Slack via Keychain bot token (vp-ops-slack-bot-token)
except Exception as e:  # pragma: no cover
    vp_ai = vp_slack = None
    _IMPORT_ERR = str(e)

DEFAULT_CONFIG = {
    "mode": "SHADOW",                 # SHADOW = DM Joshua only; LIVE = reply in the channel thread
    "channel": "C0BS11KTYKU",         # #ask-handbook (to be renamed #ask-valley-pawn at launch)
    "model": None,                    # None = vp_ai default
    "poll_limit": 20,
    "max_chunks": 10,
    "min_score_ratio": 0.30,          # keep passages scoring >= ratio * best
    "answerable_trust": ["POLICY", "VERIFIED", "HIGH", "ACADEMY", "FACT", "LIVE", "INDUSTRY"],
    "ignore_users": [],               # slack ids never answered (bots are skipped automatically)
}

ANSWERABLE = set(DEFAULT_CONFIG["answerable_trust"])
MACHINERY = re.compile(
    r"(cowork|claude|anthropic|knowledge[- ]base|corpus|entry id|scheduled task|launchd|pipeline|"
    r"\bkb:|\bpp:|\bhb:|\bac:|\bfact:|/users/|\.md\b|\.json\b|\.py\b|retriev|passage|chunk)", re.I)
HEDGE = re.compile(r"\b(likely|probably|presumably|i think|i believe|may have changed|might have changed|not on record|isn't on record|is not on record|unclear whether)\b", re.I)
OFFER_LANG = re.compile(r"(offer (them|him|her|the customer)?\s*\$\d|we can (pay|offer) (them|him|her)?\s*\$\d|"
                        r"approved (offer|amount|price)|go ahead and (pay|offer) \$)", re.I)

STOP = set("""a an the and or of to in on for with at by from is are was were be been it this that these those
as if then than so do does did can could would should will may might i you we they he she our your their my me
us them what when where which who how why not no yes ok okay please thanks about into out up down over under just
also any some all get got have has had let lets its it's im i'm there here hey hi""".split())

SYN = {
    "pto": ["paid", "time", "off", "vacation", "leave"],
    "vacation": ["pto", "paid", "time", "off"],
    "gun": ["firearm", "firearms"], "guns": ["firearm", "firearms"], "pistol": ["handgun", "firearm"],
    "rifle": ["firearm", "long", "gun"], "glock": ["handgun", "firearm"],
    "4473": ["form", "atf", "background", "check"], "nics": ["background", "check", "delay", "deny"],
    "melt": ["scrap", "spot", "karat", "dwt", "value"], "spot": ["melt", "price", "ounce"],
    "dwt": ["pennyweight", "weight"], "gram": ["weight"], "grams": ["weight"], "karat": ["gold", "purity", "14k", "10k"],
    "payoff": ["balance", "redeem", "redemption", "loan"], "payout": ["balance", "redeem", "loan"],
    "pawn": ["loan", "ticket"], "loan": ["pawn", "ticket"], "layaway": ["layaways"],
    "wifi": ["wi-fi", "password", "internet"], "wi-fi": ["wifi", "password", "internet"],
    "goldilocks": ["reports", "bot", "morning", "report"], "report": ["reports", "goldilocks"],
    "hours": ["open", "close", "closing", "opening", "saturday", "wednesday"],
    "closed": ["hours", "open", "closing"], "open": ["hours", "closed"],
    "drawer": ["cash", "count", "balance"], "safe": ["funds", "cash"],
    "scrap": ["bucket", "buckets", "melt", "refiner"], "bucket": ["buckets", "scrap"],
    "diamond": ["diamonds", "stone", "stones"], "stones": ["diamonds", "stone"],
    "ebay": ["listing", "online", "sales"], "listing": ["ebay", "online"],
    "phone": ["call", "caller", "telephone", "disclose", "verify"], "caller": ["phone", "call", "verify"],
    "manager": ["store", "escalate", "preston"], "preston": ["escalate", "manager"],
    "check": ["paycheck", "pay"], "paycheck": ["pay", "payroll"], "paid": ["pay", "payroll"],
    "harassment": ["conduct", "eeo"], "dress": ["attire", "appearance"],
    "sell": ["sale", "sales", "buy"], "price": ["pricing", "sticker"],
    "text": ["texting", "chekkit", "message"], "texting": ["text", "chekkit"],
    "rolex": ["watch", "luxury", "watches"], "omega": ["watch", "luxury"], "watches": ["watch", "rolex", "luxury"],
    "pokemon": ["trading", "card", "cards"], "pokeman": ["pokemon", "trading", "card"], "card": ["trading", "cards"],
    "cards": ["trading", "card"], "psa": ["graded", "card"], "autograph": ["memorabilia", "signed"],
    "guitar": ["musical", "instrument"], "laptop": ["electronics", "computer"], "console": ["electronics", "game"],
    "evaluate": ["check", "authenticate", "comp", "value"], "authentic": ["genuine", "fake", "authenticate"],
}

CANNED = {
    "not_covered": "That one's not written down yet — check with {mgr}. I've flagged it.",
    "out_of_scope": "That's one for {mgr_short} — I don't handle pay, schedules, time off, discipline or company numbers.",
    "unclear": "That number isn't settled right now — check with Preston before you quote it.",
    "error": None,   # on an internal error we say nothing at all (Rule 16)
}

SYSTEM = """You are Goldilocks, Valley Pawn's know-it-all coworker in Slack (Full Circle Finance Inc, five Virginia pawn stores). Staff and Preston Peters, the Operations Manager, talk to you like they'd text the most experienced person in the company. You answer like the most experienced person in the company answering a clerk at the counter: direct, plain, friendly, SHORT — and ONLY from what is actually on record.

THIS IS A CONVERSATION. You get the conversation so far plus the newest message. Read the history: a follow-up like "what about silver?", "and if it's 10k?", "what do I say to him?" or "ok what's step 2" refers back to what was just discussed — resolve it from the history and answer the follow-up directly. Don't repeat what you already said; build on it. Talk like a person: "Yep —", "No, don't do that.", "Good question —", "Here's how:" are fine. Use their first name now and then, not every message.

THE ONLY SOURCE OF TRUTH for facts is the PASSAGES block. Each passage has an id, a trust level and a citation. You know nothing else about Valley Pawn, pawn rules, prices or law: no general knowledge, no internet. If the passages don't cover it, say so plainly and point them to the right person.

TRUST LEVELS
- POLICY, FACT, ACADEMY, VERIFIED, LIVE: answer from them.
- HIGH: an established Valley Pawn rule. Answer from it as the rule itself — state it plainly. Do NOT quote anyone, do NOT name Preston as the source, do NOT give the date it was said.
- INDUSTRY: general pawn-shop know-how (how to evaluate, authenticate or comp an item; what pawn shops typically take). Use it to answer "how do I check/evaluate X" and "do we take X" when Valley Pawn's own material is silent. Valley Pawn's own passages ALWAYS win: if one says we don't take something, or sets a different rule, follow ours. INDUSTRY never sets a pay percentage, loan amount or approval.
- MEDIUM / LOW: a one-off judgment, not a rule. Never the answer. If it's all there is: say there's no set rule and to check with their manager.
- If two passages disagree, say in one line that the number isn't settled and to check before quoting it (status conflict). Don't list the history. Never pick one, never average. EXCEPTION: FACT passages are the current record for store hours, phone numbers, addresses, store emails and who manages what; where a FACT passage and older manual text disagree on those, answer from FACT and add one short line that the manual is being updated.

WHAT YOU CAN SAY WITHOUT A PASSAGE (status chat or clarify) — and only this:
- chat: greetings, thanks, "you there?", "what can you do?" — one or two friendly lines, no facts. ("Hey Sandi — what do you need?" / "Anytime." / "I can answer anything about how we do things here — policy, gold and jewelry, firearms steps, the phone, store hours, what the morning reports mean. Just ask like you'd ask Preston.")
- clarify: if the question is genuinely ambiguous and the answer depends on it, ask ONE short question back ("Is this a buy or a pawn?" / "What karat is it stamped?"). Only when you truly can't answer without it; otherwise answer.

NEVER
- compute or state a specific dollar offer for a live deal as approved. You may show melt math (LIVE passage) and the percentage band Preston set; the approval is a human's — say so.
- answer anything about someone's own pay, schedule, time-off balance, discipline, a dispute, company financials or books, real estate or personal matters -> status out_of_scope.
- name internal systems, files, ids, "the knowledge base", "passages", "sources" or how you work. Don't say who a rule came from or when — just give the rule. Mentioning the P&P manual or handbook section is fine when it helps.
- hedge. No "likely", "probably", or guessing what a setting is now. If the latest value on record may have changed, that's status conflict.
- invent anything in a chat or clarify reply — no numbers, rules or names there.

Bracketed editorial notes inside manual text ("[NOTE: paraphrased … recommend confirming]") are drafting notes, not a reason to refuse: answer the rule as written, and only if the note says the wording is unconfirmed add one line to confirm the exact form with Preston.

STYLE — SHORT. This is a text to someone at the counter. Lead with the answer in the first few words ("Yes.", "No —", "Gold only, not the stones."). 1–3 short sentences. A procedure gets at most 4 numbered steps, one line each. Give the exact words to say to a customer only when that's what they asked for. No background, no "here's why", no extra tips they didn't ask for, no follow-up offers, no sign-off. If they want more they'll ask. Don't add a source line.

OUTPUT: always call the respond tool exactly once with status, reply, cites and topic.
"cites" must copy passage ids EXACTLY as given (e.g. "kb:pay-percentage-estimator-set-46a31d72", "pp:04.02/multiple-handgun-sales-protocol"). chat and clarify have empty cites. Use "escalate" only when they explicitly want Preston pulled in ("can Preston look at this") — reply is then a one-line summary for him."""


# ----------------------------------------------------------------------------- utilities
def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(LOG, "a") as f:
        f.write(line + "\n")


def ledger(sentence, needs_human="no"):
    try:
        with open(LEDGER, "a") as f:
            f.write("| %s (native) | ask-vp | %s | NEEDS_HUMAN: %s | OPEN |\n"
                    % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET"), sentence, needs_human))
    except Exception:
        pass


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG):
        try:
            cfg.update(json.load(open(CONFIG)))
        except Exception as e:
            log("config unreadable (%s) — using defaults, mode forced SHADOW" % e)
            cfg["mode"] = "SHADOW"
    if cfg.get("mode") not in ("SHADOW", "LIVE"):
        cfg["mode"] = "SHADOW"
    return cfg


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"last_ts": None, "answered": {}}


def save_state(st):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, STATE)


def roster():
    try:
        d = json.load(open(ROSTER))
    except Exception:
        return {}, {}
    by_slack, managers = {}, {}
    for e in d.get("employees", []):
        if e.get("slack_id"):
            by_slack[e["slack_id"]] = e
        if (e.get("title") or "").strip().lower() == "manager":
            managers[e.get("department")] = e.get("preferred") or e.get("name")
    return by_slack, managers


# ----------------------------------------------------------------------------- corpus + retrieval
def ensure_corpus():
    r = subprocess.run([PY, os.path.join(BIN, "ask_vp_corpus.py")], capture_output=True, text=True, timeout=400)
    if r.returncode != 0:
        log("CORPUS BUILD FAILED rc=%s %s" % (r.returncode, (r.stderr or "")[-600:]))
        return False
    return os.path.exists(CORPUS)


def load_corpus():
    chunks = []
    with open(CORPUS, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                chunks.append(json.loads(ln))
    return chunks


def tokens(text):
    out = []
    for w in re.findall(r"[a-z0-9][a-z0-9'\-\.]*", text.lower()):
        w = w.strip(".'")
        if not w or w in STOP:
            continue
        if len(w) > 4 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 4 and w.endswith("ing"):
            w = w[:-3]
        elif len(w) > 3 and w.endswith("es"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


class BM25(object):
    def __init__(self, chunks, k1=1.4, b=0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.docs = []
        self.df = {}
        for c in chunks:
            t = tokens(c.get("title", "") + " " + c.get("title", "") + " " + c["text"])
            self.docs.append(t)
            for w in set(t):
                self.df[w] = self.df.get(w, 0) + 1
        self.N = len(chunks)
        self.avg = sum(len(d) for d in self.docs) / max(1, self.N)

    def fix_typos(self, qt):
        """Store staff type fast: 'wqcthes' -> 'watch'. Unknown words are mapped to the closest corpus word."""
        import difflib
        if not hasattr(self, "_vocab"):
            self._vocab = [w for w, n in self.df.items() if n >= 2 and len(w) >= 3]
        out = []
        for w in qt:
            if w in self.df or len(w) < 4 or w.isdigit():
                out.append(w)
                continue
            m = difflib.get_close_matches(w, self._vocab, n=1, cutoff=0.72)
            out.append(m[0] if m else w)
        return out

    def search(self, q, k=10):
        qt = tokens(q)
        expanded = list(qt)
        for w in qt:
            for s in SYN.get(w, []):
                expanded.extend(tokens(s))
        weights = {}
        for w in qt:
            weights[w] = weights.get(w, 0) + 1.0
        for w in expanded:
            weights.setdefault(w, 0.0)
            weights[w] += 0.35
        scores = []
        for i, d in enumerate(self.docs):
            if not d:
                scores.append(0.0)
                continue
            tf = {}
            for w in d:
                tf[w] = tf.get(w, 0) + 1
            s = 0.0
            L = len(d)
            for w, wt in weights.items():
                f = tf.get(w)
                if not f:
                    continue
                idf = math.log(1 + (self.N - self.df.get(w, 0) + 0.5) / (self.df.get(w, 0) + 0.5))
                s += wt * idf * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * L / self.avg))
            scores.append(s)
        order = sorted(range(self.N), key=lambda i: -scores[i])[:k]
        return [(self.chunks[i], scores[i]) for i in order if scores[i] > 0]


# ----------------------------------------------------------------------------- live melt math
KARAT = {"24": 0.999, "22": 0.9167, "18": 0.75, "14": 0.5833, "10": 0.4167, "9": 0.375}


def melt_chunk(q):
    """If the question names a karat and a weight, build a LIVE passage with today's spot and the math."""
    ql = q.lower()
    k = re.search(r"\b(24|22|18|14|10|9)\s*k(arat|t)?\b", ql)
    silver = bool(re.search(r"\b(sterling|\.925|925|silver)\b", ql))
    w = re.search(r"(\d+(?:\.\d+)?)\s*(dwt|pennyweight|pennyweights|g|gram|grams|gr|oz|ounce|ounces|ozt)\b", ql)
    if not w or (not k and not silver):
        return None
    try:
        sp = json.load(open(SPOT))
    except Exception:
        return None
    amt, unit = float(w.group(1)), w.group(2)
    if unit in ("dwt", "pennyweight", "pennyweights"):
        ozt = amt / 20.0
        shown = "%g dwt ÷ 20 = %.4f troy oz" % (amt, ozt)
    elif unit in ("g", "gram", "grams", "gr"):
        ozt = amt / 31.1035
        shown = "%g g ÷ 31.1035 = %.4f troy oz" % (amt, ozt)
    else:
        ozt = amt
        shown = "%g troy oz" % amt
    if k:
        purity = KARAT[k.group(1)]
        spot = float(sp.get("gold_usd_per_ozt") or 0)
        metal = "%sK gold" % k.group(1)
    else:
        purity = 0.925
        spot = float(sp.get("silver_usd_per_ozt") or 0)
        metal = "sterling silver (.925)"
    if spot <= 0:
        return None
    melt = ozt * purity * spot
    updated = (sp.get("updated_at") or "")[:16].replace("T", " ")
    text = ("Melt math for %s, %s: %s; × purity %.4f = %.4f fine oz; × spot $%s/oz (as of %s) = melt value $%s. "
            "Melt is the floor, not an offer: the amount we pay is the percentage of melt Preston has set for that item type, and any approval is a human decision. "
            "Pure gold is 24K; weights are troy (20 dwt = 1 troy oz)."
            % (metal, w.group(0), shown, purity, ozt * purity, "{:,.2f}".format(spot), updated, "{:,.2f}".format(melt)))
    return {"id": "live:melt", "layer": "live", "trust": "LIVE", "cite": "today's spot price (%s)" % updated,
            "title": "live melt math", "text": text}


# ----------------------------------------------------------------------------- answering
def retrieve(bm, cfg, q):
    hits = bm.search(q, k=cfg["max_chunks"] * 2)
    hits = [(c, s) for c, s in hits if c.get("trust") != "SUPERSEDED"]
    if not hits:
        return []
    best = hits[0][1]
    keep = [(c, s) for c, s in hits if s >= cfg["min_score_ratio"] * best][:cfg["max_chunks"]]
    ind = [(c, s) for c, s in hits if c.get("trust") == "INDUSTRY" and (c, s) not in keep][:2]
    keep += ind
    m = melt_chunk(q)
    if m:
        keep.insert(0, (m, best + 1))
    return keep


def build_prompt(q, asker, store, passages, history=None):
    parts = []
    if history:
        parts.append("CONVERSATION SO FAR (oldest first):")
        for who, text in history[-10:]:
            parts.append("%s: %s" % (who, text.strip()[:1500]))
        parts.append("")
    parts.append("NEWEST MESSAGE from %s (%s store): %s" % (asker or "a team member", store or "unknown", q.strip()))
    parts += ["", "PASSAGES (the only facts you may use):"]
    for c, s in passages:
        parts.append("")
        parts.append("[id=%s] [trust=%s] [cite=%s]" % (c["id"], c["trust"], c["cite"]))
        parts.append(c["text"][:6000])
    if not passages:
        parts.append("(none matched — so only chat, clarify, out_of_scope or not_covered are possible)")
    parts.append("")
    parts.append("Reply by calling the respond tool.")
    return "\n".join(parts)


RESPOND_TOOL = {
    "name": "respond",
    "description": "Send Goldilocks' reply to the newest message.",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["answer", "conflict", "chat", "clarify", "not_covered", "out_of_scope", "escalate"]},
            "reply": {"type": "string", "description": "The Slack message text."},
            "cites": {"type": "array", "items": {"type": "string"}, "description": "Passage ids used, copied exactly."},
            "topic": {"type": "string"},
        },
        "required": ["status", "reply", "cites"],
    },
}


def _post(body):
    import urllib.request, urllib.error
    req = urllib.request.Request(vp_ai.API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": vp_ai.key(), "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode()[:300]
        except Exception:
            pass
        raise ValueError("HTTP %s %s" % (e.code, detail))


TAGGED_HINT = ("\n\nFORMAT (plain text, exactly these four labelled lines, REPLY last):\n"
               "STATUS: <answer|conflict|chat|clarify|not_covered|out_of_scope|escalate>\n"
               "CITES: <passage ids separated by commas, or none>\n"
               "TOPIC: <3-6 word slug>\n"
               "REPLY: <the Slack message — may run over several lines>")


def parse_tagged(raw):
    m = re.search(r"STATUS:\s*([a-z_]+)", raw, re.I)
    c = re.search(r"CITES:\s*(.*)", raw, re.I)
    t = re.search(r"TOPIC:\s*(.*)", raw, re.I)
    r = re.search(r"REPLY:\s*(.*)\Z", raw, re.I | re.S)
    if not m or not r:
        raise ValueError("untagged answer")
    cites = [x.strip() for x in (c.group(1) if c else "").split(",") if x.strip() and x.strip().lower() != "none"]
    return {"status": m.group(1).lower(), "cites": cites, "topic": (t.group(1).strip() if t else ""),
            "reply": r.group(1).strip()}


def ask_structured(prompt, model=None, max_tokens=1500):
    """Structured reply. 1) forced tool call; 2) if the API refuses that for this model, a tagged
    plain-text format parsed in code. Either way the caller gets a dict or an exception."""
    mdl = model or vp_ai.MODEL
    if not getattr(ask_structured, "_tools_off", False):
        body = {"model": mdl, "max_tokens": max_tokens, "system": SYSTEM, "tools": [RESPOND_TOOL],
                "tool_choice": {"type": "tool", "name": "respond"}, "messages": [{"role": "user", "content": prompt}]}
        try:
            resp = _post(body)
            for blk in resp.get("content", []):
                if blk.get("type") == "tool_use" and blk.get("name") == "respond":
                    return blk.get("input") or {}, resp.get("stop_reason")
        except ValueError as e:
            if "HTTP 400" in str(e):
                ask_structured._tools_off = True
                log("tool call refused for %s, using tagged format: %s" % (mdl, e))
            else:
                raise
    body = {"model": mdl, "max_tokens": max_tokens, "system": SYSTEM.replace(
                "OUTPUT: always call the respond tool exactly once with status, reply, cites and topic.",
                "OUTPUT: use the labelled FORMAT given at the end of the message."),
            "messages": [{"role": "user", "content": prompt + TAGGED_HINT}]}
    resp = _post(body)
    raw = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    return parse_tagged(raw), resp.get("stop_reason")


def parse_json(raw):
    """First JSON object in the model's text (tolerates text or a second object after it)."""
    i = raw.find("{")
    if i < 0:
        raise ValueError("no JSON in answer")
    obj, _ = json.JSONDecoder(strict=False).raw_decode(raw[i:])
    return obj if isinstance(obj, dict) else {}


def answer(q, asker="", store="", cfg=None, bm=None, by_id=None, history=None):
    """Returns dict(status, reply, cites, topic, checks, latency, source_line).
    history = [(speaker, text), ...] oldest first — the thread or DM so far, excluding q."""
    cfg = cfg or load_config()
    t0 = time.time()
    # retrieval sees the recent user turns too, so "what about silver?" still finds the gold/melt passages
    # typos: staff type fast on phones ("role wqcthes"). If any word is unknown to the corpus, have the model
    # fix the spelling first (search only — the reply still sees the original message too).
    q_search = q
    if bm is not None and any(len(w) >= 4 and not w.isdigit() and w not in bm.df for w in tokens(q)):
        try:
            fixed = vp_ai.ask("Fix the spelling and typos in this message from a pawn-shop employee. Keep the meaning and "
                              "wording otherwise. Output only the corrected message.\n\n" + q, max_tokens=120).strip()
            if fixed and len(fixed) < 400:
                q_search = fixed
                if fixed.lower() != q.lower():
                    out_note = "typo-fixed: %s" % fixed[:120]
        except Exception:
            pass
    ctx = " ".join(t for w, t in (history or [])[-4:] if w != "Goldilocks")
    passages = retrieve(bm, cfg, (q_search + " " + ctx).strip()) if ctx else retrieve(bm, cfg, q_search)
    if ctx:
        m0 = melt_chunk(q) or melt_chunk(ctx + " " + q)
        if m0 and not any(c["id"] == "live:melt" for c, _ in passages):
            passages.insert(0, (m0, 99))
    retrieved = {c["id"]: c for c, s in passages}
    _, managers = roster()
    mgr = managers.get(store) or "your Store Manager"
    fills = {"mgr": mgr if mgr != "your Store Manager" else mgr,
             "mgr_short": mgr if mgr != "your Store Manager" else "your Store Manager",
             "preston": " — and if it's a deal or pricing question, Preston"}
    out = {"status": "not_covered", "reply": CANNED["not_covered"].format(**fills), "cites": [], "topic": "",
           "checks": [], "latency": 0.0, "source_line": "", "retrieved": list(retrieved.keys())}
    prompt = build_prompt(q if q_search == q else "%s  (they mean: %s)" % (q, q_search), asker, store, passages, history)
    has_answerable = any(c.get("trust") in ANSWERABLE for c, _ in passages)
    j = {}
    for attempt in (1, 2):
        raw = ""
        try:
            j, stop = ask_structured(prompt, model=cfg.get("model"))
            raw = json.dumps(j)[:400]
            if stop == "max_tokens":
                out["checks"].append("hit max_tokens")
        except Exception as e:
            out["checks"].append("model error (try %d): %s" % (attempt, str(e)[:160]))
            j = {}
        st0 = (j.get("status") or "").strip().lower()
        out.setdefault("raw", []).append(raw)
        # one retry when the model refuses or garbles while answerable passages ARE on the table
        if attempt == 1 and has_answerable and (not j or st0 in ("not_covered", "")):
            out["checks"].append("retry: first pass said %s" % (st0 or "nothing"))
            prompt = prompt + ("\n\nCHECK AGAIN: read every passage above carefully. If any POLICY, FACT, ACADEMY, "
                               "VERIFIED, HIGH or LIVE passage answers the newest message (or the follow-up in context), "
                               "answer from it and cite it. Only say not_covered if none of them do.")
            continue
        break
    if not j:
        out["status"] = "error"
        out["checks"].append("raw: %s" % (out.get("raw") or [""])[-1][:300])
        out["reply"] = ""
        out["latency"] = time.time() - t0
        return out
    status = (j.get("status") or "").strip().lower()
    reply = (j.get("reply") or "").strip()
    cites = [c for c in (j.get("cites") or []) if isinstance(c, str)]
    out["topic"] = (j.get("topic") or "")[:60]

    # ---- validation in code (the model is not trusted to police itself)
    # normalise cites: the model sometimes drops the prefix ("kb:") or quotes the title — match by suffix once
    norm = []
    for c in cites:
        if c in retrieved:
            norm.append(c)
            continue
        cand = [rid for rid in retrieved if rid.endswith(":" + c) or rid.endswith("/" + c) or rid.split(":", 1)[-1] == c]
        norm.append(cand[0] if len(cand) == 1 else c)
    cites = norm
    bad_cites = [c for c in cites if c not in retrieved]
    if bad_cites:
        out["checks"].append("invented cites dropped: %s" % ",".join(bad_cites[:4]))
    cites = [c for c in cites if c in retrieved]
    answerable_cites = [c for c in cites if retrieved[c]["trust"] in ANSWERABLE]

    if status in ("answer", "conflict"):
        if not answerable_cites and status == "answer":
            out["checks"].append("answer without an answerable cite -> not_covered")
            status = "not_covered"
        elif not reply:
            out["checks"].append("empty reply -> not_covered")
            status = "not_covered"
        elif MACHINERY.search(reply):
            out["checks"].append("machinery words in reply -> not_covered: %s" % MACHINERY.search(reply).group(0))
            status = "not_covered"
        elif OFFER_LANG.search(reply):
            out["checks"].append("approved-offer language -> not_covered")
            status = "not_covered"
        elif status == "answer" and HEDGE.search(reply):
            out["checks"].append("hedged answer (%s) -> unclear" % HEDGE.search(reply).group(0))
            status = "unclear"
    elif status in ("chat", "clarify"):
        cites = []
        if not reply:
            status = "not_covered"
        elif MACHINERY.search(reply):
            out["checks"].append("machinery words in %s -> not_covered" % status)
            status = "not_covered"
        elif len(reply) > 450 or re.search(r"[$%]|\b\d{2,}\b", reply):
            out["checks"].append("%s reply carried facts/numbers -> not_covered" % status)
            status = "not_covered"
    elif status == "escalate":
        if not reply:
            reply = "Preston, can you take a look at this one? (%s)" % q[:140]
    elif status == "out_of_scope":
        reply = CANNED["out_of_scope"].format(**fills)
    else:
        if status != "not_covered":
            out["checks"].append("unknown status %r -> not_covered" % status)
        status = "not_covered"

    if status == "unclear":
        reply = CANNED["unclear"].format(**fills)
        cites = []
    if status == "not_covered":
        if has_answerable and not out["checks"]:
            out["checks"].append("model said not_covered; raw: %s" % (out.get("raw") or [""])[-1][:300].replace("\n", " "))
        reply = CANNED["not_covered"].format(**fills)
        cites = []
    if status in ("answer", "conflict"):
        srcs = []
        for c in cites:
            cite = retrieved[c]["cite"]
            if c.startswith("kb:"):
                cite = "Valley Pawn practice"
            elif c.startswith("ac:"):
                cite = re.sub(r"^Academy lesson (\S+) — ", r"Academy \1: ", cite)
            elif c.startswith("live:"):
                cite = "today's spot price"
            elif c.startswith("ind:"):
                cite = "general pawn know-how"
            if cite not in srcs:
                srcs.append(cite)
        out["source_line"] = "_From: " + " · ".join(srcs[:3]) + "_" if srcs else ""
        reply = reply.rstrip() + ("\n\n" + out["source_line"] if out["source_line"] else "")
    out.update({"status": status, "reply": reply, "cites": cites, "latency": time.time() - t0})
    return out


# ----------------------------------------------------------------------------- slack loop (conversational)
THREAD_TTL_H = 24          # follow a thread for this long after the last turn
PASSES = 3                 # passes per launchd run (every 15 s) -> a new message is seen within ~5 s
PASS_GAP_S = 4.5


def human_msg(m, bot_user, cfg):
    if m.get("subtype") not in (None, "file_share", "thread_broadcast"):
        return False
    if m.get("bot_id") or not m.get("user") or m["user"] == bot_user:
        return False
    if m["user"] in cfg.get("ignore_users", []):
        return False
    return len((m.get("text") or "").strip()) >= 2


def clean(text, bot_user):
    if bot_user:
        text = text.replace("<@%s>" % bot_user, "")
    return text.strip()


def user_name(uid, by_slack):
    e = by_slack.get(uid)
    if e:
        return (e.get("preferred") or e.get("name") or uid), (e.get("department") or "")
    try:
        r = vp_slack.call("users.info", params={"user": uid})
        p = (r.get("user") or {}).get("profile") or {}
        return (p.get("first_name") or p.get("display_name") or p.get("real_name") or uid), ""
    except Exception:
        return uid, ""


def is_staff_lead(uid, by_slack):
    if uid == PRESTON:
        return True
    e = by_slack.get(uid) or {}
    return (e.get("title") or "").strip().lower() == "manager"


def thread_history(channel, thread_ts, upto_ts, bot_user, by_slack):
    """[(speaker, text)] of the thread before upto_ts, oldest first."""
    try:
        r = vp_slack.call("conversations.replies", params={"channel": channel, "ts": thread_ts, "limit": 50})
    except Exception:
        return []
    hist = []
    for m in r.get("messages", []):
        if float(m.get("ts", 0)) >= float(upto_ts):
            break
        if m.get("bot_id") or m.get("user") == bot_user:
            hist.append(("Goldilocks", (m.get("text") or "")))
        elif m.get("user"):
            hist.append((user_name(m["user"], by_slack)[0], clean(m.get("text") or "", bot_user)))
    return hist


def qlog(asker, store, q, outcome):
    os.makedirs(BASE, exist_ok=True)
    new = not os.path.exists(QLOG)
    with open(QLOG, "a", encoding="utf-8") as f:
        if new:
            f.write("# Ask Valley Pawn — Question Log\n\nEvery question asked and how it was handled. "
                    "NOT-FOUND rows are the interview list: what Preston knows that is not written down yet.\n\n"
                    "| When | Asker | Store | Question | Outcome |\n|---|---|---|---|---|\n")
        f.write("| %s | %s | %s | %s | %s |\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), asker, store or "—",
                                                 q.replace("|", "/").replace("\n", " ")[:200], outcome))


def outcome_code(res):
    s = res["status"]
    if s == "answer":
        return "ANSWERED " + ",".join(res["cites"][:3])
    if s == "conflict":
        return "CONFLICT SURFACED " + ",".join(res["cites"][:3])
    if s == "escalate":
        return "ESCALATED to Preston"
    if s == "chat":
        return "CHAT"
    if s == "clarify":
        return "CLARIFY (asked a question back)"
    if s == "out_of_scope":
        return "OUT-OF-SCOPE (routed)"
    if s == "unclear":
        return "NOT-FOUND (unclear which value is current; routed to Preston)"
    if s == "error":
        return "ERROR (nothing posted)"
    return "NOT-FOUND (routed)"


def live_for(cfg, uid):
    return cfg["mode"] == "LIVE" or uid in (cfg.get("live_users") or [])


def post_reply(cfg, channel, thread_ts, uid, asker, store, q, res):
    """LIVE (or a live_users member): reply where they asked. Otherwise: shadow DM to Joshua."""
    if res["status"] == "error" or not res["reply"]:
        return False
    text = res["reply"]
    if res["status"] == "escalate":
        text = "<@%s> — %s (from %s%s)" % (PRESTON, text, asker, (", " + store) if store else "")
    if live_for(cfg, uid):
        payload = {"channel": channel, "text": vp_slack.to_mrkdwn(text), "unfurl_links": False}
        if thread_ts:
            payload["thread_ts"] = thread_ts
        r = vp_slack.call("chat.postMessage", payload)
        ok = bool(r.get("ok"))
        vp_slack.receipt("slack", channel, ok, len(text.encode()), "ask-vp reply " + res["status"])
        if not ok:
            log("chat.postMessage failed: %s" % r.get("error"))
        return ok
    shadow = ("*Goldilocks — shadow* (nothing posted where they asked)\n*%s (%s):* %s\n\n*Would reply:*\n%s\n\n_%s · %.1fs%s_"
              % (asker, store or "store unknown", q, text, outcome_code(res), res["latency"],
                 (" · " + "; ".join(res["checks"])) if res["checks"] else ""))
    try:
        vp_slack.post(vp_slack.dm_channel(JOSHUA), shadow)
        return True
    except SystemExit as e:
        log("shadow DM failed: %s" % e)
        return False


class Ctx(object):
    def __init__(self, cfg, st):
        self.cfg, self.st = cfg, st
        self.bm = None
        self.by_slack, _ = roster()
        try:
            self.bot_user = (vp_slack.call("auth.test", {}) or {}).get("user_id")
        except Exception:
            self.bot_user = None

    def corpus(self):
        if self.bm is None:
            if not ensure_corpus():
                ledger("ask-vp: corpus build failed — questions left unanswered until the build passes", "no")
                return None
            self.bm = BM25(load_corpus())
        return self.bm


import threading
_LOCK = threading.Lock()


def handle(ctx, channel, msg, thread_ts, history):
    """Answer one human message and record it. Safe to run several at once (busy morning, 12 people asking)."""
    with _LOCK:
        bm = ctx.corpus()
    if bm is None:
        return False
    q = clean(msg.get("text") or "", ctx.bot_user)
    asker, store = user_name(msg["user"], ctx.by_slack)
    res = answer(q, asker, store, ctx.cfg, bm, history=history)
    ok = post_reply(ctx.cfg, channel, thread_ts, msg["user"], asker, store, q, res)
    code = outcome_code(res) + ("" if ok else " [delivery failed]")
    with _LOCK:
        ctx.st.setdefault("answered", {})[msg["ts"]] = code
        qlog(asker, store, q, code + (" (follow-up)" if history else ""))
    log("%s | %s | %s | %.1fs | %s" % ("LIVE" if live_for(ctx.cfg, msg["user"]) else "SHADOW", asker, code,
                                       res["latency"], "; ".join(res["checks"])))
    return ok


def pass_channel(ctx):
    cfg, st = ctx.cfg, ctx.st
    ch = cfg["channel"]
    # 1. new top-level messages -> answer in a thread under them, then follow that thread
    try:
        r = vp_slack.call("conversations.history", params={"channel": ch, "oldest": st["last_ts"],
                                                           "limit": cfg["poll_limit"], "inclusive": "false"})
    except Exception as e:
        log("history error: %s" % e)
        return
    if not r.get("ok"):
        log("history not ok: %s" % r.get("error"))
        return
    newest = st["last_ts"]
    jobs = []
    for m in sorted(r.get("messages", []), key=lambda x: float(x.get("ts", 0))):
        newest = max(newest, m.get("ts", newest), key=float)
        if m.get("thread_ts") and m["thread_ts"] != m.get("ts"):
            continue
        if not human_msg(m, ctx.bot_user, cfg) or m["ts"] in st.get("answered", {}):
            continue
        jobs.append(m)
    st["last_ts"] = newest
    if jobs:
        ctx.corpus()
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=6) as ex:
            results = list(ex.map(lambda mm: (mm, handle(ctx, ch, mm, mm["ts"], [])), jobs))
        for mm, ok in results:
            if ok:
                st.setdefault("threads", {})[mm["ts"]] = {"last": mm["ts"], "asker": mm["user"], "touched": time.time()}

    # 2. follow-ups inside threads we're part of -> keep the conversation going
    now = time.time()
    for tts, t in list(st.get("threads", {}).items()):
        if now - t.get("touched", now) > THREAD_TTL_H * 3600 or t.get("closed"):
            st["threads"].pop(tts, None)
            continue
        try:
            rr = vp_slack.call("conversations.replies", params={"channel": ch, "ts": tts, "oldest": t["last"], "limit": 50})
        except Exception:
            continue
        for m in rr.get("messages", []):
            if float(m.get("ts", 0)) <= float(t["last"]) or m.get("ts") == tts:
                continue
            t["last"] = max(t["last"], m["ts"], key=float)
            if not human_msg(m, ctx.bot_user, cfg) or m["ts"] in st.get("answered", {}):
                continue
            if m["user"] != t.get("asker") and is_staff_lead(m["user"], ctx.by_slack):
                # Preston or a manager stepped in — Goldilocks steps back; their answer gets captured tonight
                t["closed"] = True
                log("thread %s: %s stepped in, Goldilocks stepping back" % (tts, user_name(m["user"], ctx.by_slack)[0]))
                break
            hist = thread_history(ch, tts, m["ts"], ctx.bot_user, ctx.by_slack)
            if handle(ctx, ch, m, tts, hist):
                t["touched"] = time.time()


def pass_dms(ctx):
    """Direct messages to Goldilocks: a private conversation, answered in the DM."""
    st = ctx.st
    if st.get("dm_disabled"):
        return
    try:
        r = vp_slack.call("conversations.list", params={"types": "im", "limit": 200})
    except Exception as e:
        log("dm list error: %s" % e)
        return
    if not r.get("ok"):
        st["dm_disabled"] = r.get("error", "?")
        log("DMs off: %s (needs im:read + im:history on the bot)" % st["dm_disabled"])
        return
    dms = st.setdefault("dms", {})
    for c in r.get("channels", []):
        cid, uid = c.get("id"), c.get("user")
        if not cid or not uid or uid in ("USLACKBOT", ctx.bot_user):
            continue
        if cid not in dms:
            dms[cid] = "%.6f" % time.time()        # never answer DM history
            continue
        try:
            h = vp_slack.call("conversations.history", params={"channel": cid, "oldest": dms[cid], "limit": 20})
        except Exception:
            continue
        if not h.get("ok"):
            if h.get("error") == "missing_scope":
                st["dm_disabled"] = "missing_scope"
                log("DMs off: missing im:history")
                return
            continue
        msgs = sorted(h.get("messages", []), key=lambda x: float(x.get("ts", 0)))
        for m in msgs:
            dms[cid] = max(dms[cid], m.get("ts", dms[cid]), key=float)
        new = [m for m in msgs if human_msg(m, ctx.bot_user, ctx.cfg) and m["ts"] not in st.get("answered", {})]
        if not new:
            continue
        try:
            full = vp_slack.call("conversations.history", params={"channel": cid, "limit": 14})
            prior = sorted(full.get("messages", []), key=lambda x: float(x.get("ts", 0)))
        except Exception:
            prior = []
        for m in new:
            hist = []
            for pm in prior:
                if float(pm.get("ts", 0)) >= float(m["ts"]):
                    break
                if time.time() - float(pm.get("ts", 0)) > THREAD_TTL_H * 3600:
                    continue
                who = "Goldilocks" if (pm.get("bot_id") or pm.get("user") == ctx.bot_user) else user_name(pm.get("user", ""), ctx.by_slack)[0]
                hist.append((who, pm.get("text") or ""))
            handle(ctx, cid, m, None, hist)


def poll():
    if vp_ai is None or vp_slack is None:
        log("import failure: %s" % _IMPORT_ERR)
        return 2
    cfg = load_config()
    st = load_state()
    if not st.get("last_ts"):
        st["last_ts"] = "%.6f" % time.time()
        save_state(st)
        log("initialised last_ts=%s mode=%s" % (st["last_ts"], cfg["mode"]))
        return 0
    if st.get("channel") != cfg["channel"]:
        # channel changed: start the new one from "now minus 10 min" so a test typed just before the switch is caught
        st["channel"] = cfg["channel"]
        st["last_ts"] = max(st["last_ts"], "%.6f" % (time.time() - 600), key=float)
    replay = os.path.join(STATE_DIR, "replay.txt")
    if os.path.exists(replay):
        tss = [x.strip() for x in open(replay).read().split() if x.strip()]
        os.remove(replay)
        for t in tss:
            st.get("answered", {}).pop(t, None)
        if tss:
            st["last_ts"] = min([st["last_ts"]] + ["%.6f" % (float(t) - 0.000001) for t in tss], key=float)
            log("replay requested for %s" % ", ".join(tss))
    ctx = Ctx(cfg, st)
    for i in range(PASSES):
        pass_channel(ctx)
        if cfg.get("dms_enabled", True):
            pass_dms(ctx)
        save_state(st)
        if i < PASSES - 1:
            time.sleep(PASS_GAP_S)
    if len(st.get("answered", {})) > 500:
        keys = sorted(st["answered"], key=float)[-300:]
        st["answered"] = {k: st["answered"][k] for k in keys}
        save_state(st)
    return 0


# ----------------------------------------------------------------------------- selftest / cli
def selftest():
    cfg = load_config()
    if not ensure_corpus():
        print("corpus build failed")
        return 2
    bm = BM25(load_corpus())
    qpath = os.path.join(SELFTEST_DIR, "questions.json")
    qs = json.load(open(qpath))
    os.makedirs(SELFTEST_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    outp = os.path.join(SELFTEST_DIR, "%s.md" % stamp)
    lines = ["# Ask Valley Pawn selftest %s (mode %s, nothing posted)" % (stamp, cfg["mode"]), ""]
    passed = 0
    for i, item in enumerate(qs, 1):
        hist = [tuple(h) for h in item.get("history", [])]
        res = answer(item["q"], item.get("asker", "Test"), item.get("store", "Culpeper"), cfg, bm, history=hist)
        want = item.get("expect")
        ok = (want is None) or (res["status"] == want)
        passed += 1 if ok else 0
        lines += ["## %d. %s%s" % (i, item["q"], ("  _(follow-up after: %s)_" % " / ".join(h[1][:60] for h in hist)) if hist else ""),
                  "expected: %s · got: **%s** · %s · %.1fs · %d chars" % (want, res["status"], "PASS" if ok else "FAIL", res["latency"], len(res["reply"].split("\n\n_From:")[0])),
                  "retrieved: %s" % ", ".join(res.get("retrieved", [])[:8]),
                  "checks: %s" % ("; ".join(res["checks"]) or "none"), "", res["reply"], ""]
    lines.insert(2, "**%d / %d passed**" % (passed, len(qs)))
    open(outp, "w", encoding="utf-8").write("\n".join(lines))
    print(outp)
    print("%d/%d passed" % (passed, len(qs)))
    return 0 if passed == len(qs) else 1


def main():
    a = sys.argv[1:]
    if "--status" in a:
        print(json.dumps({"config": load_config(), "state": load_state(),
                          "corpus_exists": os.path.exists(CORPUS)}, indent=1))
        return 0
    if "--selftest" in a:
        return selftest()
    if "--ask" in a:
        q = a[a.index("--ask") + 1]
        store = a[a.index("--store") + 1] if "--store" in a else ""
        if not ensure_corpus():
            print("corpus build failed")
            return 2
        res = answer(q, "Test", store, load_config(), BM25(load_corpus()))
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return 0
    return poll()


if __name__ == "__main__":
    sys.exit(main())
