#!/usr/bin/env python3
"""vp_audit.py — measure every Tier-1 publication's ACTUAL delivery record, from the channels.

WHY (2026-09-18, Joshua): "take each task, evaluate the performance of it since inception, decide
if it's good to go or not based off accuracy and consistency." Until now that judgement was made
by eyeballing a channel — which is exactly how three working checks got reported as broken. This
replaces opinion with a count.

METHOD — the only honest one available:
  * expand each entry's cadence into every instance it SHOULD have fired in the window;
  * pull the real Slack history for its channel ONCE (paginated) and index the timestamps whose
    text contains the entry's marker;
  * an instance is HIT if a marked message lands in [instance, instance + grace + SLACK_SLOP];
  * report per task: expected / hit / rate, longest dark run, last good, and the dark dates.
Nothing is inferred from lastRunAt. Nothing is published. Read-only.

LIMITS, stated so nobody over-reads the output:
  * Only covers entries whose output is a Slack CHANNEL the bot can read. DM-surface and canvas
    entries are listed as NOT MEASURABLE, not as failures.
  * Channel history is what the bot can see; if the bot joined a channel recently (several joined
    2026-09-16/17), instances before that are UNKNOWN, not misses — they are excluded and counted.
  * A HIT means "a message with the right marker landed in the window." It does NOT prove the
    numbers inside were correct. Accuracy incidents are tracked separately from the manifest's
    own `_corrected` notes (which is where a wrong post gets recorded).

USAGE:  vp_audit.py [--days 60] [--json out.json]   ->  markdown table on stdout
"""
import datetime as dt
import getpass
import json
import os
import subprocess
import sys
import time
import glob
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
TIER1_PATH = os.path.join(OS_DIR, "fleet/tier1_tasks.json")
OUTPUTS_PATH = os.path.join(OS_DIR, "fleet/expected_outputs.json")
SVC = "vp-ops-slack-bot-token"
SLACK_SLOP_H = 2.0      # a post that lands a little after grace still counts as delivered
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DAYS = 60
if "--days" in sys.argv:
    DAYS = int(sys.argv[sys.argv.index("--days") + 1])
JSON_OUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None


# ---------------------------------------------------------------- slack
def token():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", SVC, "-a", getpass.getuser(), "-w"],
                           capture_output=True, text=True, timeout=10)
        if r.stdout.strip().startswith("xox"):
            return r.stdout.strip()
    except Exception:
        pass
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if t.startswith("xox"):
        return t
    sys.exit("no slack bot token")


TOK = token()
_hist_cache = {}


def history(channel, oldest):
    """All messages in a channel since `oldest` (epoch float). Cached per channel."""
    key = (channel, int(oldest))
    if key in _hist_cache:
        return _hist_cache[key]
    msgs, cursor = [], None
    for _ in range(40):                       # hard page cap
        p = {"channel": channel, "oldest": str(oldest), "limit": 200}
        if cursor:
            p["cursor"] = cursor
        url = "https://slack.com/api/conversations.history?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOK})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            _hist_cache[key] = ("ERROR", str(e))
            return _hist_cache[key]
        if not r.get("ok"):
            _hist_cache[key] = ("ERROR", r.get("error", "?"))
            return _hist_cache[key]
        msgs.extend(r.get("messages", []))
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(1.2)                       # be kind to the rate limit
    _hist_cache[key] = ("OK", msgs)
    return _hist_cache[key]


def bot_joined_at(msgs):
    """Epoch of the bot's channel_join, if present — instances before it are UNKNOWN, not misses."""
    for m in msgs:
        if m.get("subtype") == "channel_join" and "VP OPS ENGINE" in (m.get("text") or ""):
            return float(m["ts"])
    return None


# ---------------------------------------------------------------- cadence -> every instance in the window
def hhmm(tok):
    tok = tok.replace("et", "")
    return int(tok[:2]), int(tok[2:4])


def instances(cadence, start, end):
    """Every datetime this cadence should have fired in [start, end]."""
    if not cadence or cadence.startswith("retired"):
        return None
    p = cadence.split("-")
    kind = p[0]
    out = []
    try:
        if kind in ("daily", "weekdays", "monsat"):
            h, m = hhmm(p[1])
            limit = {"daily": 7, "weekdays": 5, "monsat": 6}[kind]
            d = start.date()
            while d <= end.date():
                if d.weekday() < limit:
                    out.append(dt.datetime.combine(d, dt.time(h, m)))
                d += dt.timedelta(days=1)
        elif kind == "weekly":
            if p[1] not in WEEKDAYS:
                return None
            h, m = hhmm(p[2])
            target = WEEKDAYS.index(p[1])
            d = start.date()
            while d <= end.date():
                if d.weekday() == target:
                    out.append(dt.datetime.combine(d, dt.time(h, m)))
                d += dt.timedelta(days=1)
        elif kind in ("monthly", "quarterly"):
            n = int("".join(c for c in p[1] if c.isdigit()) or 1)
            h, m = hhmm(p[2])
            y, mo = start.year, start.month
            while dt.datetime(y, mo, 1) <= end:
                if kind == "quarterly" and mo not in (1, 4, 7, 10):
                    pass
                else:
                    try:
                        c = dt.datetime(y, mo, n, h, m)
                        if start <= c <= end:
                            out.append(c)
                    except ValueError:
                        pass
                mo += 1
                if mo == 13:
                    mo, y = 1, y + 1
        else:
            return None
    except Exception:
        return None
    return [c for c in out if start <= c <= end]


# ---------------------------------------------------------------- receipts
def _receipts(task):
    """Successful-send timestamps for a task, from fleet/receipts/<task>.jsonl. See vp_receipt.py."""
    p = os.path.join(os.path.dirname(OUTPUTS_PATH), "receipts", task + ".jsonl")
    out = []
    try:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if not r.get("ok", True):
                    continue
                try:
                    out.append(dt.datetime.fromisoformat(r["ts"]).replace(tzinfo=None))
                except (ValueError, KeyError):
                    pass
    except OSError:
        return []
    return sorted(out)


# ---------------------------------------------------------------- file artifacts
def _expand(path, c):
    """Expand instance-date placeholders. {PREV-YYYY-MM} is the month BEFORE the instance —
    close-cycle artifacts (bonus, EOM) run on day N and write the month they just closed."""
    prev = c.replace(day=1) - dt.timedelta(days=1)
    return (path.replace("{YYYY-MM-DD}", c.strftime("%Y-%m-%d"))
                .replace("{PREV-YYYY-MM}", prev.strftime("%Y-%m"))
                .replace("{YYYY-MM}", c.strftime("%Y-%m")))


def _found(pat, c, grace_h):
    """(exists, on_time). on_time means the artifact was WRITTEN inside [instance, instance+grace].
    A file that exists but was written outside its window is a backfill, not a run — scoring it as a
    hit is exactly how a task that never fires on its day looks healthy forever (Rule 12)."""
    hits = glob.glob(pat) if "*" in pat else ([pat] if os.path.exists(pat) else [])
    if not hits:
        return False, False
    lo, hi = c.timestamp(), (c + dt.timedelta(hours=max(grace_h, 1))).timestamp()
    ok = False
    for h in hits:
        try:
            if lo <= os.path.getmtime(h) <= hi:
                ok = True
                break
        except OSError:
            pass
    return True, ok


# ---------------------------------------------------------------- audit
def main():
    tier1_doc = json.load(open(TIER1_PATH))
    tier1 = {t for g in tier1_doc.get("tier1", {}).values() for t in g}
    infra = set(tier1_doc.get("tier1", {}).get("infrastructure", []))
    entries = [e for e in json.load(open(OUTPUTS_PATH))["entries"] if e.get("task") in tier1]

    end = dt.datetime.now()
    start = end - dt.timedelta(days=DAYS)
    rows = []

    for e in entries:
        task, out = e["task"], e.get("output", "")
        rec = {"task": task, "cadence": e.get("cadence", ""), "output": out,
               "accuracy_notes": sum(1 for k in e if k.startswith("_corrected"))}
        # ---- RECEIPTS: the only evidence for surfaces this bot cannot read (DM, canvas) ----
        if out == "receipt":
            rl = _receipts(task)
            inst = instances(e.get("cadence", ""), start, end)
            if not rl:
                rec.update(status="AWAITING RECEIPTS",
                           note="no receipt has been written yet — this task becomes measurable on its "
                                "next run. Absence here is missing evidence, NOT a missed publication.")
                rows.append(rec)
                continue
            if not inst:
                rec.update(status="NOT MEASURABLE", note="cadence not parseable: %s" % e.get("cadence"))
                rows.append(rec)
                continue
            grace = e.get("grace_hours", 12)
            born = min(rl)                       # receipts cannot speak about runs before they existed
            hit = miss = 0
            dark = []
            run = best = 0
            for c in inst:
                if c > end - dt.timedelta(minutes=5) or c < born:
                    continue
                lo, hi = c, c + dt.timedelta(hours=max(grace, 1))
                if any(lo <= r <= hi for r in rl):
                    hit += 1
                    run = 0
                else:
                    miss += 1
                    run += 1
                    best = max(best, run)
                    dark.append(c.strftime("%m/%d"))
            scored = hit + miss
            rec.update(status="MEASURED", expected=scored, hit=hit, miss=miss, unknown=0,
                       rate=(round(100.0 * hit / scored, 1) if scored else None), longest_dark=best,
                       since=born.strftime("%m/%d"), last_good=max(rl).strftime("%m/%d %H:%M"),
                       dark_dates=dark[-60:],
                       note="scored from publication receipts; history before %s is not recoverable"
                            % born.strftime("%m/%d"))
            rows.append(rec)
            continue
        # ---- FILE artifacts: measurable on disk when the path carries the instance date ----
        if out == "file":
            path = e.get("path", "")
            inst = instances(e.get("cadence", ""), start, end)
            if not any(k in path for k in ("{YYYY-MM-DD}", "{YYYY-MM}", "{PREV-YYYY-MM}")):
                # undated artifact (e.g. a state.json rewritten in place): only its mtime is knowable,
                # so history cannot be reconstructed. Say that plainly instead of scoring it.
                try:
                    mt = dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%m/%d %H:%M")
                except OSError:
                    mt = "missing"
                rec.update(status="MTIME ONLY", note="undated artifact %s — last written %s; per-run history not recoverable"
                           % (os.path.basename(path), mt))
                rows.append(rec)
                continue
            if not inst:
                rec.update(status="NOT MEASURABLE", note="cadence not parseable: %s" % e.get("cadence"))
                rows.append(rec)
                continue
            grace = e.get("grace_hours", 12)
            hit = miss = late = 0
            dark, late_dates = [], []
            first = None
            run = best = 0
            for c in inst:
                if c > end - dt.timedelta(minutes=5):
                    continue
                exists, on_time = _found(_expand(path, c), c, grace)
                if exists and first is None:
                    first = c                      # inception = first artifact that ever appeared
                if first is None:
                    continue                       # before this artifact ever appeared
                if on_time:
                    hit += 1
                    run = 0
                else:
                    miss += 1
                    run += 1
                    best = max(best, run)
                    if exists:
                        late += 1
                        late_dates.append(c.strftime("%m/%d"))
                    else:
                        dark.append(c.strftime("%m/%d"))
            scored = hit + miss
            note = None
            if late:
                note = ("%d instance(s) have an artifact on disk written OUTSIDE the run window "
                        "(backfilled, not run on the day): %s" % (late, ", ".join(late_dates[-6:])))
            rec.update(status="MEASURED", expected=scored, hit=hit, miss=miss, unknown=0, late=late,
                       rate=(round(100.0 * hit / scored, 1) if scored else None), longest_dark=best,
                       since=(first.strftime("%m/%d") if first else "never"),
                       last_good="(on disk)", dark_dates=dark[-60:], note=note)
            rows.append(rec)
            continue
        if not out.startswith("slack:#"):
            rec.update(status="NOT MEASURABLE", note="DM / canvas surface — not readable by this bot")
            rows.append(rec)
            continue
        inst = instances(e.get("cadence", ""), start, end)
        if not inst:
            rec.update(status="NOT MEASURABLE", note="cadence not parseable or retired: %s" % e.get("cadence"))
            rows.append(rec)
            continue
        st, payload = history(e["channel_id"], start.timestamp())
        if st == "ERROR":
            rec.update(status="NO ACCESS", note="slack: %s" % payload)
            rows.append(rec)
            continue
        joined = bot_joined_at(payload)
        # INCEPTION: a rate is only honest if the denominator starts when the publication actually
        # began. #discount-review has no messages before 08/13 and #emails-missed none before 08/07 —
        # counting 60 days of "expected" against a channel that is 36 days old invents misses.
        # Inception = the first time this marker ever appeared (the publication's real birth);
        # fall back to the channel's oldest visible message.
        all_ts = [float(m["ts"]) for m in payload if m.get("ts")]
        channel_oldest = min(all_ts) if all_ts else start.timestamp()
        marker = e.get("marker", "")
        ci = bool(e.get("marker_ci"))
        hits = sorted(float(m["ts"]) for m in payload
                      if marker and (marker.lower() in (m.get("text") or "").lower() if ci
                                     else marker in (m.get("text") or "")))
        inception = min(hits) if hits else channel_oldest
        if joined:
            inception = max(inception, joined)
        inception_dt = dt.datetime.fromtimestamp(inception)
        grace = dt.timedelta(hours=e.get("grace_hours", 4) + SLACK_SLOP_H)
        hit, miss, unknown, dark = 0, 0, 0, []
        for c in inst:
            if c.timestamp() < inception:
                unknown += 1                              # before this publication existed
                continue
            if c > end - dt.timedelta(minutes=5):
                continue                                  # not due yet
            lo, hi = c.timestamp(), (c + grace).timestamp()
            if any(lo <= h <= hi for h in hits):
                hit += 1
            else:
                miss += 1
                dark.append(c.strftime("%m/%d"))
        if not hits:
            # The marker never appeared ANYWHERE in the window. That is almost always a bad marker
            # string, not a publication that never ran — proven 2026-09-18 when review-obtained-last-week
            # read 0/8 "never" purely because the manifest said "ranked" and the post says "Ranked".
            # Never present this as a delivery rate.
            rec.update(status="MARKER SUSPECT",
                       note="marker %r never matched any message in %d days — verify the marker against a real post before treating this as a miss" % (marker, DAYS))
            rows.append(rec)
            continue
        scored = hit + miss
        # longest consecutive dark run
        run = best = 0
        for c in inst:
            if c.timestamp() < inception or c > end - dt.timedelta(minutes=5):
                continue
            lo, hi = c.timestamp(), (c + grace).timestamp()
            if any(lo <= h <= hi for h in hits):
                run = 0
            else:
                run += 1
                best = max(best, run)
        rec.update(status="MEASURED", expected=scored, hit=hit, miss=miss, unknown=unknown,
                   rate=(round(100.0 * hit / scored, 1) if scored else None),
                   longest_dark=best, since=inception_dt.strftime("%m/%d"),
                   last_good=(dt.datetime.fromtimestamp(max(hits)).strftime("%m/%d %H:%M") if hits else "never"),
                   dark_dates=dark[-60:])
        rows.append(rec)

    measured = [r for r in rows if r["status"] == "MEASURED"]
    measured.sort(key=lambda r: (r["rate"] if r["rate"] is not None else 999, r["task"]))

    print("# Tier-1 delivery audit — last %d days (to %s)\n" % (DAYS, end.strftime("%Y-%m-%d %H:%M")))
    try:                                      # a forgotten dry run would silently flatten every rate
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import vp_dryrun
        on, doc = vp_dryrun.state()
        if on:
            print("> **DRY RUN IS ACTIVE until %s (scope: %s).** Native publications are being diverted\n"
                  "> to fleet/test_output/ and are NOT reaching Slack. Misses below are the guard, not\n"
                  "> the fleet. Clear it with `vp_dryrun.py off`.\n" % (doc.get("until"), doc.get("scope")))
    except Exception:
        pass
    print("Counted from the real channel history. A HIT = a message carrying the entry's marker landed")
    print("within its scheduled time + grace. This measures DELIVERY, not whether the numbers inside")
    print("were right — accuracy incidents are the `_corrected` column (manifest notes).\n")
    print("| Task | Cadence | Since | Expected | Delivered | Rate | Longest dark | Last good | Accuracy |")
    print("|---|---|---|---:|---:|---:|---:|---|---|".replace("|---|---|---|---:|---:|---:|---:|---|---|",
          "|---|---|---:|---:|---:|---:|---|---:|"))
    for r in measured:
        print("| %s | %s | %s | %d | %d | %s%% | %d | %s | %d |" % (
            r["task"], r["cadence"], r["since"], r["expected"], r["hit"],
            r["rate"] if r["rate"] is not None else "—", r["longest_dark"], r["last_good"], r["accuracy_notes"]))
    nm = [r for r in rows if r["status"] != "MEASURED"]
    if nm:
        print("\n## Not measurable from Slack (%d) — needs a different probe, NOT a failure\n" % len(nm))
        for r in nm:
            print("- **%s** (%s) — %s" % (r["task"], r["status"], r.get("note", "")))
    if JSON_OUT:
        json.dump(rows, open(JSON_OUT, "w"), indent=2)
        print("\n(json -> %s)" % JSON_OUT)


if __name__ == "__main__":
    main()
