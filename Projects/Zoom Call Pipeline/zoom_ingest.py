#!/usr/bin/env python3
"""
zoom_ingest.py — pull Zoom Phone recordings, transcribe them LOCALLY, classify each
call as EMPLOYEE or CUSTOMER, and route. One ingest, two consumers.

    EMPLOYEE calls  -> out/employee/<id>.json   (transcript KEPT, feeds the Preston KB)
    CUSTOMER calls  -> out/customer/<date>.jsonl (structured record ONLY, transcript DESTROYED)

WHY THE ASYMMETRY (read before changing anything here)
    The knowledge base is durable and queryable by store staff, so it must never contain
    customer data. The call analysis is *about* customers, so it must never retain an
    individual customer's words. Those two requirements are opposite, which is why one
    pipeline routes to two stores rather than one system trying to serve both.

    Redaction on free-form speech is best-effort and leaks — a first name, a street, an
    unusual item, and a transcript is re-identifiable. So customer transcripts are never
    written to disk in readable form. They exist in memory, get reduced to a structured
    record with no identifiers, and are discarded in the same run.

FAIL-CLOSED CLASSIFICATION
    Unknown number, blocked number, unparseable number -> CUSTOMER. Misclassifying an
    employee call as a customer call costs one lost knowledge entry. The reverse puts a
    customer's conversation into a base staff can query. Not symmetric. Do not "improve"
    this into a fuzzy match.

LOCAL TRANSCRIPTION ONLY
    whisper-cpp on this Mac. If it is missing or fails, the run STOPS. It never falls back
    to a cloud transcription API — that would ship customer call audio to a third party and
    is the one thing this design exists to prevent.

READ-ONLY ACCESS
    Zoom Server-to-Server OAuth with phone_recording:read:admin + phone:read:admin. Nothing
    here can change a setting, delete a recording, or place a call.

USAGE
    python3 zoom_ingest.py --since 2026-08-21           # backfill from recording go-live
    python3 zoom_ingest.py                              # yesterday + today (normal daily run)
    python3 zoom_ingest.py --dry-run                    # list what WOULD be pulled, touch nothing
    python3 zoom_ingest.py --check                      # verify creds, whisper, roster; pull nothing
"""

import os
import re
import sys
import glob
import json
import time
import base64
import shutil
import argparse
import datetime
import subprocess
import urllib.parse
import urllib.request

BASE = os.path.expanduser("~/Documents/Claude/Projects/Zoom Call Pipeline")
SECRETS = os.path.expanduser("~/.vp_secrets/zoom_s2s.json")
ROSTER = os.path.join(BASE, "internal_roster.json")
STATE = os.path.join(BASE, "state.json")
OUT_EMP = os.path.join(BASE, "out", "employee")
OUT_CUS = os.path.join(BASE, "out", "customer")
TMP = "/tmp/vp_zoom_ingest"

API = "https://api.zoom.us/v2"
TOKEN_URL = "https://zoom.us/oauth/token"

# Extension -> store. BOTH the user extension and the Call Queue extension must be here:
# a recording's `owner` is the QUEUE (e.g. 806 "Waynesboro Store Queue"), while
# `accepted_by` is the USER (803). Mapping only the user extensions makes every call
# resolve to UNK — verified against a live 2026-09-01 record.
# Queue/user pairs from Valley Pawn OS/ZOOM_PHONE.md.
EXT_TO_STORE = {
    "802": "HAR", "805": "HAR",   # user, queue
    "803": "WAY", "806": "WAY",
    "807": "LEX", "804": "LEX",
    "808": "CUL", "810": "CUL",   # staged, still on Verizon — records nothing today
    "809": "ROA", "812": "ROA",   # staged, still on Verizon — records nothing today
}

# Zoom's recording metadata includes `caller_name` / `callee_name`, which for an inbound
# customer call is the caller's REAL NAME (carrier CNAM). It is never read, never stored
# and never logged anywhere in this pipeline. Do not "enrich" a record with it.
_NEVER_READ = ("caller_name", "callee_name")


# ---------------------------------------------------------------- auth

def _load_json(path, what):
    if not os.path.exists(path):
        sys.stderr.write("FATAL: %s not found at %s\n" % (what, path))
        sys.exit(2)
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception as e:
        sys.stderr.write("FATAL: %s is not valid JSON (%s)\n" % (what, e))
        sys.exit(2)


_token_cache = {"tok": None, "exp": 0}


def token():
    """Server-to-Server OAuth. Cached with a 60s safety margin."""
    if _token_cache["tok"] and time.time() < _token_cache["exp"] - 60:
        return _token_cache["tok"]
    c = _load_json(SECRETS, "Zoom credentials")
    for k in ("account_id", "client_id", "client_secret"):
        if not c.get(k):
            sys.stderr.write("FATAL: %s missing '%s'\n" % (SECRETS, k))
            sys.exit(2)
    basic = base64.b64encode(
        ("%s:%s" % (c["client_id"], c["client_secret"])).encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "account_credentials",
        "account_id": c["account_id"],
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    req.add_header("Authorization", "Basic " + basic)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        sys.stderr.write("FATAL: Zoom token exchange failed: %s\n" % e)
        sys.stderr.write("  Check the app is ACTIVATED and has phone_recording:read:admin.\n")
        sys.exit(2)
    _token_cache["tok"] = d["access_token"]
    _token_cache["exp"] = time.time() + int(d.get("expires_in", 3600))
    return _token_cache["tok"]


def api_get(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + token())
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


# ---------------------------------------------------------------- roster / classification

def norm(num):
    """US number -> last 10 digits. Returns None if it isn't a usable number."""
    if not num:
        return None
    d = re.sub(r"\D", "", str(num))
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 else None


def load_roster():
    r = _load_json(ROSTER, "internal roster")
    known = {}
    for person in r.get("people", []):
        for n in person.get("numbers", []):
            k = norm(n)
            if k:
                known[k] = person.get("name", "unknown")
    return known


def classify(other_party, roster):
    """EMPLOYEE only on an exact roster match. Everything else is CUSTOMER. Fail closed."""
    k = norm(other_party)
    if k and k in roster:
        return "EMPLOYEE", roster[k]
    return "CUSTOMER", None


# ---------------------------------------------------------------- transcription

def whisper_bin():
    for name in ("whisper-cli", "whisper-cpp", "main"):
        p = shutil.which(name)
        if p:
            return p
    return None


def model_path():
    """small.en first: phone audio is 8 kHz, compressed and noisy, and base.en drops
    numbers and proper nouns on it — exactly the tokens that matter here."""
    for p in (os.path.join(BASE, "models", "ggml-small.en.bin"),
              os.path.join(BASE, "models", "ggml-base.en.bin"),
              "/opt/homebrew/share/whisper-cpp/ggml-base.en.bin",
              os.path.expanduser("~/.cache/whisper/ggml-base.en.bin")):
        if os.path.exists(p):
            return p
    return None


def transcribe(audio_path):
    """Local Whisper. Returns text. NEVER falls back to a cloud API — see module docstring."""
    wb, mp = whisper_bin(), model_path()
    if not wb or not mp:
        raise RuntimeError(
            "local whisper unavailable (bin=%s model=%s) — refusing to transcribe. "
            "This pipeline never sends call audio off this machine." % (wb, mp))
    wav = os.path.join(TMP, "cur.wav")
    subprocess.run(["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", wav],
                   check=True, capture_output=True)
    # -mc 0 is NOT optional. Without it, whisper carries decoded text forward as context and
    # gets stuck repeating it. Every one of our calls opens with the same recorded-line
    # announcement, which is the perfect trigger: the model locks onto that sentence, emits it
    # 2-8 times, and drops the ENTIRE conversation that follows. That silently blanked 35% of
    # the week's calls (112 of 321) and produced two confident, wrong business conclusions
    # before Joshua listened to the audio and said the calls were plainly answered and talking.
    # Verified 2026-09-08: identical file, same model — without -mc 0 the transcript is four
    # copies of the announcement; with it, the full conversation (a gold/coin lead) comes back.
    out = subprocess.run([wb, "-m", mp, "-f", wav, "-nt", "-np", "-mc", "0"],
                         check=True, capture_output=True, text=True)
    try:
        os.remove(wav)
    except OSError:
        pass
    return out.stdout.strip()


# ---------------------------------------------------------------- customer reduction

SPAM_HINTS = ("this is a courtesy call", "your car's extended warranty", "press one to",
              "final notice", "we've been trying to reach you")

CATEGORIES = {
    # NOTE 2026-09-07: expanded after the first real weekly read showed 68% of real calls
    # landing in "other" category — verified those calls were NOT short/junk (avg 78s, 90%
    # inbound), i.e. real conversations the original narrow keyword lists just missed. More
    # specific categories are listed before more generic ones on purpose (e.g. diamond before
    # gold_jewelry) since `next()` takes the first match and "engagement ring" should not
    # resolve to the generic "ring" keyword in gold_jewelry.
    "gaming_console": ("ps5", "ps4", "playstation", "xbox", "nintendo", "switch",
                        "video game", "controller", "series x"),
    "diamond": ("diamond", "carat", "engagement ring", "engagement"),
    "gold_jewelry": ("gold", "chain", "ring", "necklace", "bracelet", "karat", "14k", "10k",
                      "jewelry", "earrings", "wedding band", "class ring", "pendant",
                      "cash for gold", "scrap gold"),
    "silver_coins": ("silver", "coin", "bullion", "morgan", "peace dollar", "junk silver",
                      "quarter", "half dollar", "silver dollar", "proof set", "coin collection"),
    "firearm": ("gun", "rifle", "pistol", "shotgun", "firearm", "ffl", "transfer", "ammo",
                "handgun", "revolver", "ar-15", "ar15", "magazine", "background check"),
    "tools": ("drill", "dewalt", "milwaukee", "saw", "tool", "generator", "compressor",
              "impact driver", "chainsaw", "pressure washer", "welder", "table saw",
              "power tool", "makita", "ryobi"),
    "electronics": ("laptop", "tv", "iphone", "phone", "tablet", "macbook", "computer",
                     "monitor", "camera", "gopro", "headphones", "airpods", "samsung"),
    "instrument": ("guitar", "amp", "drum", "violin", "keyboard", "bass guitar", "saxophone",
                    "trumpet", "piano"),
    "jewelry_watch": ("watch", "rolex", "seiko", "citizen", "movado", "apple watch", "fossil"),
    "general_merchandise": ("furniture", "recliner", "mattress", "appliance", "refrigerator",
                              "washer", "dryer", "lawn mower", "atv", "bicycle", "bike",
                              "stroller"),
}

INTENTS = {
    # Expanded 2026-09-07 alongside CATEGORIES — same finding, same reason.
    "item_availability": ("do you have", "still available", "in stock", "got any", "looking for",
                           "you carry", "you got", "in the store", "on the floor", "available",
                           "do y'all have", "does your store have"),
    "sell_or_pawn": ("sell", "pawn", "loan on", "how much would you give", "what would you give",
                      "bring in", "trade in", "get a loan", "need a loan", "want to pawn",
                      "looking to sell", "wanting to sell", "get rid of", "cash out"),
    "price_quote": ("how much", "what do you pay", "what's it worth", "price on", "worth",
                     "value", "appraisal", "estimate", "quote me", "ballpark", "spot price",
                     "gold price", "silver price"),
    "payment_or_redeem": ("payment", "pay on my", "redeem", "pick up my", "extend", "interest",
                           "my ticket", "loan number", "balance", "due date", "extend my loan",
                           "get my stuff back", "reclaim", "renew", "past due", "overdue",
                           "over due"),
    "hours_or_location": ("what time", "open", "closed", "where are you", "address", "directions",
                           "today", "what days", "y'all open"),
    "employment": ("hiring", "application", "job", "position", "apply", "job opening", "resume",
                    "interview"),
}

# Preston's qualifying script (#general 2026-02-02): "Have you done business here before?
# / Are you trying to loan or sell? / How much are you needing?" — asked BEFORE looking
# anything up. Detected in aggregate only; never attributed to a named employee in a channel.
# Expanded 2026-09-07 with the same phrasing variants as INTENTS/CATEGORIES.
QUALIFIERS = ("done business", "loan or sell", "pawn or sell", "how much are you needing",
              "how much do you need", "how much are you looking to get",
              "what are you looking to do", "sell it or pawn it", "loan it or sell it",
              "how much you need", "how much you're needing")


def reduce_customer(text, meta):
    """Transcript -> structured record with NO identifiers. The transcript dies with this call."""
    t = (text or "").lower()

    cat = next((c for c, kws in CATEGORIES.items() if any(k in t for k in kws)), "other")
    intent = next((i for i, kws in INTENTS.items() if any(k in t for k in kws)), "other")

    return {
        "date": meta["date"],
        "store": meta["store"],
        "direction": meta["direction"],
        "duration_s": meta["duration_s"],
        "intent": intent,
        "category": cat,
        "outcome": ("not_in_stock" if any(p in t for p in
                    ("don't have", "do not have", "sold", "out of", "we don't carry"))
                    else "we_dont_take" if any(p in t for p in
                    ("we don't take", "we do not take", "not interested", "can't help you with"))
                    else "engaged"),
        "qualifying_questions_asked": any(q in t for q in QUALIFIERS),
        "spam": (meta["duration_s"] <= 15 and meta["direction"] == "inbound")
                or any(s in t for s in SPAM_HINTS),
    }
    # NOTE: `text` is a local. It is never written, never returned, never logged.


# ---------------------------------------------------------------- main

def save_state(done):
    """Atomic checkpoint. Called after every processed call — see the note at the call site."""
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"done": sorted(done)}, f)
    os.replace(tmp, STATE)


def daterange(since, until):
    d, out = since, []
    while d <= until:
        out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N calls (testing, and for chunking a long backfill)")
    a = ap.parse_args()

    if a.check:
        print("credentials:", "OK" if os.path.exists(SECRETS) else "MISSING " + SECRETS)
        print("roster:     ", "OK" if os.path.exists(ROSTER) else "MISSING " + ROSTER)
        print("whisper bin:", whisper_bin() or "MISSING (brew install whisper-cpp)")
        print("whisper mdl:", model_path() or "MISSING (download ggml-base.en.bin)")
        print("ffmpeg:     ", shutil.which("ffmpeg") or "MISSING")
        if os.path.exists(SECRETS):
            try:
                token()
                print("zoom auth:   OK")
            except SystemExit:
                print("zoom auth:   FAILED")
        return 0

    for d in (OUT_EMP, OUT_CUS, TMP):
        os.makedirs(d, exist_ok=True)

    # Sweep any audio a previously-killed run left behind. Call audio must never linger
    # on disk outside the run that is actively transcribing it.
    for stale in glob.glob(os.path.join(TMP, "*")):
        try:
            os.remove(stale)
        except OSError:
            pass

    roster = load_roster()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"done": []}
    done = set(state.get("done", []))

    today = datetime.date.today()
    since = datetime.date.fromisoformat(a.since) if a.since else today - datetime.timedelta(days=1)
    until = datetime.date.fromisoformat(a.until) if a.until else today

    n_emp = n_cus = n_skip = 0
    for day in daterange(since, until):
        page = None
        while True:
            params = {"from": day, "to": day, "page_size": 300}
            if page:
                params["next_page_token"] = page
            try:
                res = api_get("/phone/recordings", params)
            except Exception as e:
                sys.stderr.write("WARN: recordings pull failed for %s: %s\n" % (day, e))
                break

            for rec in res.get("recordings", []):
                if a.limit and (n_emp + n_cus) >= a.limit:
                    break
                rid = rec.get("id")
                if not rid or rid in done:
                    n_skip += 1
                    continue

                # Resolve the store from whichever extension is present. `accepted_by` is
                # the user who actually took the call (most precise); `owner` is usually the
                # Call Queue. Try both — an unanswered call has no accepted_by at all.
                accepted_ext = str((rec.get("accepted_by") or {}).get("extension_number", ""))
                owner_ext = str((rec.get("owner") or {}).get("extension_number", ""))
                store = (EXT_TO_STORE.get(accepted_ext)
                         or EXT_TO_STORE.get(owner_ext) or "UNK")

                direction = (rec.get("direction") or "").lower()
                other = rec.get("callee_number") if direction == "outbound" else rec.get("caller_number")

                kind, who = classify(other, roster)
                meta = {"date": day, "store": store, "direction": direction or "unknown",
                        "duration_s": int(rec.get("duration") or 0)}

                if a.dry_run:
                    print("%s  %s  %-8s %-9s %4ss  %s" % (day, store, kind, direction,
                                                          meta["duration_s"], who or ""))
                    continue

                url = rec.get("download_url")
                if not url:
                    n_skip += 1
                    continue
                audio = os.path.join(TMP, rid + ".mp3")
                try:
                    req = urllib.request.Request(url)
                    req.add_header("Authorization", "Bearer " + token())
                    with urllib.request.urlopen(req, timeout=180) as r, open(audio, "wb") as f:
                        shutil.copyfileobj(r, f)
                    text = transcribe(audio)
                except RuntimeError:
                    raise  # local-whisper failure is fatal, never degrade to a cloud call
                except Exception as e:
                    sys.stderr.write("WARN: %s failed (%s)\n" % (rid, e))
                    continue
                finally:
                    if os.path.exists(audio):
                        os.remove(audio)   # audio never persists here; it lives in Zoom

                if kind == "EMPLOYEE":
                    # Transcript KEPT — this is the knowledge source.
                    with open(os.path.join(OUT_EMP, rid + ".json"), "w", encoding="utf-8") as f:
                        json.dump({**meta, "call_id": rid, "participant": who,
                                   "transcript": text}, f, indent=2)
                    n_emp += 1
                else:
                    # Transcript DESTROYED — only the structured record survives this line.
                    rec_out = reduce_customer(text, meta)
                    with open(os.path.join(OUT_CUS, day + ".jsonl"), "a", encoding="utf-8") as f:
                        f.write(json.dumps(rec_out) + "\n")
                    del text
                    n_cus += 1

                # Persist state after EVERY call, not at the end of the run. A backfill is
                # hundreds of calls and can be killed part-way; checkpointing at the end
                # meant a dead run lost all progress AND re-appended every record it had
                # already written on the next attempt. Found on the 2026-09-01 test run.
                done.add(rid)
                save_state(done)

            page = res.get("next_page_token")
            if not page or (a.limit and (n_emp + n_cus) >= a.limit):
                break
        if a.limit and (n_emp + n_cus) >= a.limit:
            break

    if not a.dry_run:
        save_state(done)

    print("employee=%d customer=%d skipped=%d" % (n_emp, n_cus, n_skip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
