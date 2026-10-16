"""
THE ONLY writer to Publer for Valley Pawn social (2026-09-05).

Folds in every landmine the fleet has hit since June, so no lane can rediscover them:
  * Cloudflare 1010 without a browser User-Agent
  * job status comes back "complete", not "completed" (false JOB_timeouts all August)
  * bulk DELETE /posts wipes the whole queue -> hard-refused here
  * video media must be referenced by library id, and type must be "video" (never "reel")
  * blank / factually wrong / duplicate captions must never ship (qa gates)
  * a re-run must never double-post -> idempotent by (week, lane, item_key, account_key)

Input: a plan JSON produced by plan.py with captions filled in by the creative contract.
"""
from __future__ import annotations
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from publer_client import PublerClient, PublerError  # noqa: E402
from . import config, ledger, reader

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

_FORBIDDEN = [
    (re.compile(r"seven days a week|7 days a week", re.I), "no store is open 7 days/week"),
    # 2026-10-01: 5pm close is checked by _bad_5pm_close() below (valid only for Culpeper/Roanoke on Saturday).
    (re.compile(r"\bmon(?:day)?\s*(?:-|–|—|through|thru|to)\s*sat(?:urday)?\b[,:]?\s*(?:from\s*)?10(?::00)?\s*(?:am|a\.m\.)?\s*(?:-|–|—|to|until)\s*6", re.I),
     "stale hours: Culpeper, Roanoke & Waynesboro are Mon-Fri 10-6, Sat 10-5; Harrisonburg & Lexington close Wed"),
    (re.compile(r"dixie pawn", re.I), "never 'Dixie Pawn'"),
    (re.compile(r"full circle finance", re.I), "never the legal entity name customer-facing"),
    (re.compile(r"\b(gun|guns|firearm|firearms|rifle|pistol|handgun|shotgun|ammo|ammunition)\b", re.I), "no firearms on social"),
    (re.compile(r"\b(fast cash|instant cash|no credit check|quick cash)\b", re.I), "predatory phrasing"),
]
_PHONE = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
# 2026-10-01 (Joshua): ONLY the 6-day stores close at 5pm, and ONLY on Saturday (Culpeper & Roanoke; Waynesboro from 2026-10-14).
_FIVE_PM_CLOSE = re.compile(r"open (?:until|till|til) 5(?::00)?\s*p\.?m|clos(?:es?|ing) at 5(?::00)?\s*p\.?m|"
                            r"10(?::00)?\s*(?:am|a\.m\.)?\s*(?:-|–|—|to)\s*5(?::00)?\s*(?:pm|p\.m\.)", re.I)
_SIX_DAY = re.compile(r"culpeper|roanoke|waynesboro", re.I)

# 2026-10-14 (Joshua): Waynesboro is a 6-day store (Mon-Fri 10-6, Sat 10-5, closed Sun). Block its OLD hours:
# "closed Wed", the 5-day "Mon, Tue, Thu..." list, or "Sat 10-6" in a clause that names Waynesboro
# (clause = text since the last . ; | · or newline), plus the old "Harrisonburg, Waynesboro & Lexington" grouping.
# 2026-10-15: ALSO blocked when the post targets a Waynesboro account/page (GBP_Waynesboro, Waynesboro FB) and the
# clause names no other 5-day store (Harrisonburg/Lexington) -- the 10/15 GBP Alienware caption said
# "Open Mon, Tue, Thu, Fri and Sat from 10am to 6pm, closed Wed and Sun." with Waynesboro only in an earlier sentence.
# Also catches a Saturday 6pm close ("Saturday until 6", "Waynesboro ... close at 6" on a Saturday).
_WAY_STALE = re.compile(r"clos(?:ed|es)\s+(?:on\s+)?wed|\bmon(?:day)?s?,?\s*tue(?:s|sday)?s?,?\s*thu|"
                        r"\bsat(?:urday)?s?[:\s]*(?:from\s*)?10(?::00)?\s*(?:am|a\.m\.)?\s*(?:-|–|—|to|until)\s*6", re.I)
_WAY_SAT6 = re.compile(r"(?:clos(?:e|es|ing)\s+at|open\s+(?:until|till|til)|\buntil|\btill|\btil)\s*6(?![\d:])(?!\s*(?:am|a\.m))", re.I)
_DAY_WORD = re.compile(r"\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\b", re.I)
_WAY_OLD_GROUP = re.compile(r"harrisonburg,\s*waynesboro,?\s*(?:&|and)\s*lexington", re.I)
_FIVE_DAY_STORE = re.compile(r"harrisonburg|lexington", re.I)
_WAYNESBORO = re.compile(r"waynesboro", re.I)


def _targets_waynesboro(account_keys) -> bool:
    if isinstance(account_keys, str):
        account_keys = [account_keys]
    return any(_WAYNESBORO.search(k or "") for k in (account_keys or ()))


def _way_stale_hours(text: str, account_keys=()) -> bool:
    """True if the text states Waynesboro's pre-2026-10-14 hours.

    account_keys: the account key(s) the post goes to (str or list). When any is a Waynesboro account,
    an old-hours clause counts even if it doesn't name Waynesboro, unless it names Harrisonburg/Lexington."""
    if _WAY_OLD_GROUP.search(text):
        return True
    way_acct = _targets_waynesboro(account_keys)
    for m in _WAY_STALE.finditer(text):
        seg = re.split(r"[.;|·\n]", text[max(0, m.start() - 160): m.start()])[-1]
        if _WAYNESBORO.search(seg) or (way_acct and not _FIVE_DAY_STORE.search(seg)):
            return True
    for m in _WAY_SAT6.finditer(text):
        sent = re.split(r"[.;|·\n]", text[max(0, m.start() - 160): m.start()])[-1]
        days = _DAY_WORD.findall(sent)
        if not days or days[-1].lower() != "sat":
            continue  # a 6pm close is right Mon-Fri; only a Saturday 6pm close is stale
        clause = re.split(r"[,(]|\bclos\w*\s+at\s+\d", sent)[-1]
        if _WAYNESBORO.search(clause) or (way_acct and not _FIVE_DAY_STORE.search(clause)
                                         and not re.search(r"culpeper|roanoke", clause, re.I)):
            return True
    return False


def _bad_5pm_close(text: str, account_key: str = "") -> bool:
    """True if the text claims a 5pm close anywhere other than Culpeper/Roanoke/Waynesboro on Saturday."""
    for m in _FIVE_PM_CLOSE.finditer(text):
        win = text[max(0, m.start() - 80): m.end() + 40]
        sat = re.search(r"\bsat(?:urday)?s?\b", win, re.I)
        if not (sat and (_SIX_DAY.search(account_key or "") or _SIX_DAY.search(win))):
            return True
    return False


class Publisher(PublerClient):
    def _headers(self) -> dict:
        h = super()._headers()
        h["User-Agent"] = BROWSER_UA
        return h

    def _request(self, method: str, path: str, **kw):
        if method.upper() == "DELETE":
            raise PublerError("REFUSED: DELETE is disabled in vp_social (bulk DELETE /posts wiped 63 posts on 2026-08-22). "
                              "Remove posts in the Publer UI.")
        return super()._request(method, path, **kw)

    def wait_for_job(self, job_id: str, max_seconds: int = 180, poll_interval: float = 4.0) -> dict:
        deadline = time.time() + max_seconds
        while time.time() < deadline:
            st = self.job_status(job_id)
            state = st.get("status") if isinstance(st, dict) else None
            if state in ("complete", "completed", "failed", "error"):
                st = dict(st)
                st["status"] = "completed" if state in ("complete", "completed") else "failed"
                return st
            time.sleep(poll_interval)
        return {"status": "timeout", "job_id": job_id}

    def schedule_one(self, *, text: str, account_key: str, scheduled_at: str,
                     kind: str, media_id: str | None) -> dict:
        meta = self._account_meta(account_key)
        net: dict = {"type": "status" if not media_id else ("video" if kind == "video" else "photo"), "text": text}
        if media_id:
            net["media"] = [{"type": "video" if kind == "video" else "image", "id": media_id}]
        body = {"bulk": {"state": "scheduled",
                         "posts": [{"networks": {meta["network"]: net},
                                    "accounts": [{"id": meta["publer_id"], "scheduled_at": scheduled_at}]}]}}
        return self.post("/posts/schedule", json=body)


# --- QA gates ------------------------------------------------------------------

def qa_caption(text: str, account_key: str, kind: str, min_words: int) -> list[str]:
    problems = []
    t = (text or "").strip()
    if not t:
        return ["empty caption"]
    if len(t.split()) < min_words:
        problems.append(f"caption too short ({len(t.split())} words < {min_words})")
    for pat, why in _FORBIDDEN:
        if pat.search(t):
            problems.append(f"forbidden: {why}")
    if _bad_5pm_close(t, account_key):
        problems.append("forbidden: only Culpeper, Roanoke & Waynesboro close at 5pm, and only on Saturday")
    if _way_stale_hours(t, account_key):
        problems.append("forbidden: stale Waynesboro hours -- Waynesboro is Mon-Fri 10-6, Sat 10-5, closed Sun (open Wed from 10/14)")
    if account_key.startswith("GBP_"):
        if "#" in t:
            problems.append("GBP: hashtags")
        if _PHONE.search(t):
            problems.append("GBP: phone number in body")
        if len(t) > config.RULES["gbp_max_chars"]:
            problems.append("GBP: >1500 chars")
        if sum(1 for ch in t if ord(ch) > 0x2500) > 4:
            problems.append("GBP: too many emojis")
    if account_key == "BrandTwitter" and len(t) > config.RULES["x_max_chars"]:
        problems.append(f"X: {len(t)} chars > {config.RULES['x_max_chars']}")
    if account_key in config.STORES or account_key == "Brand":
        if "#" in t:
            problems.append("Facebook: no hashtags")
    return problems


def plan_level_checks(plan: dict) -> list[str]:
    """Cross-slot rules: identical captions, humor cap, per-page item cooldown, reveal present."""
    errs = []
    seen_hash: dict[str, str] = {}
    humor = 0
    week = plan["week"]
    for s in plan["slots"]:
        if s.get("lane") == "humor":
            humor += 1
        for acct, cap in (s.get("captions") or {}).items():
            if not cap:
                continue
            h = reader.caption_hash(cap)
            where = f"{s['slot_id']}/{acct}"
            if h in seen_hash:
                errs.append(f"identical caption: {where} == {seen_hash[h]}")
            seen_hash[h] = where
            for row in ledger.caption_exists(h, config.RULES["identical_caption_window_days"]):
                errs.append(f"identical caption already live: {where} == {row['account_key']} {row['scheduled_date']}")
        if s.get("item_key"):
            for acct in s.get("accounts", []):
                prior = [r for r in ledger.recent_item_posts(s["item_key"], acct, config.RULES["item_cooldown_days"])
                         if (r["plan_id"] or "") != plan["plan_id"]]
                same_kind = [r for r in prior if ((r["type"] or "").lower() in ("video", "reel")) == (s.get("kind") == "video")]
                if same_kind:
                    errs.append(f"{s['slot_id']}/{acct}: {s['item_key']} already had a {s.get('kind')} on {same_kind[0]['scheduled_date']}")
    if humor > config.RULES["humor_max_per_week"]:
        errs.append(f"humor slots {humor} > {config.RULES['humor_max_per_week']}/week")
    guess = [s for s in plan["slots"] if s.get("format_id", "").startswith("eng_guess") or "guess" in (s.get("format_id") or "")]
    reveals = [s for s in plan["slots"] if s.get("lane") == "reveal"]
    if guess and not reveals:
        errs.append("guess-the-price slot without a reveal slot (audience promise)")
    return errs


# --- publish ---------------------------------------------------------------------

def _media_for(p: Publisher, slot: dict, cache: dict) -> str | None:
    path = slot.get("media_path")
    if not path:
        return None
    if path in cache:
        return cache[path]
    if not Path(path).exists():
        raise PublerError(f"media missing: {path}")
    resp = p.upload_media(path)
    mid = resp.get("id") if isinstance(resp, dict) else None
    if not mid:
        raise PublerError(f"upload_media returned no id for {path}: {str(resp)[:200]}")
    cache[path] = mid
    return mid


def publish_plan(plan_path: Path, dry_run: bool | None = None, sleep_between: float = 8.0) -> dict:
    plan = json.loads(Path(plan_path).read_text())
    dry = config.dry_run_enabled() if dry_run is None else dry_run
    plan_id, week = plan["plan_id"], plan["week"]
    errs = plan_level_checks(plan)
    results = {"plan_id": plan_id, "dry_run": dry, "scheduled": 0, "skipped": 0, "failed": 0, "blocked": errs, "items": []}
    if errs:
        ledger.record_run("publish", False, {"plan_id": plan_id, "blocked": errs})
        return results
    p = Publisher()
    media_cache: dict = {}
    for s in plan["slots"]:
        kind = s.get("kind", "photo")
        for acct in s.get("accounts", []):
            r = {"slot": s["slot_id"], "account": acct}
            cap = (s.get("captions") or {}).get(acct) or ""
            min_words = config.RULES["min_words_brand"] if acct.startswith("Brand") and acct != "BrandTwitter" else \
                (12 if acct == "BrandTwitter" else config.RULES["min_words_store"])
            if s.get("lane") in ("community", "engagement"):   # engagement added 2026-10-05: a question post is short by design
                min_words = 20
            if acct == "BrandTikTok":       # 2026-10-05: TikTok captions are 1-2 lines by rule; 40 words made every one fail
                min_words = 6
            probs = qa_caption(cap, acct, kind, min_words)
            if probs:
                r.update(status="skipped", reason="; ".join(probs))
                ledger.upsert_planned(plan_id, s, acct, "skipped", reason=r["reason"])
                results["skipped"] += 1
                results["items"].append(r)
                continue
            if ledger.planned_status(week, s.get("lane"), s.get("item_key") or s["slot_id"], acct):
                r.update(status="skipped", reason="already live (idempotent)")
                results["skipped"] += 1
                results["items"].append(r)
                continue
            th = reader.caption_hash(cap)
            if dry:
                r.update(status="dry-run", scheduled_at=s["scheduled_at"])
                ledger.upsert_planned(plan_id, s, acct, "planned", text_hash=th, reason="dry-run")
                results["items"].append(r)
                continue
            try:
                mid = _media_for(p, s, media_cache)
                resp = p.schedule_one(text=cap, account_key=acct, scheduled_at=s["scheduled_at"], kind=kind, media_id=mid)
                job = resp.get("job_id") if isinstance(resp, dict) else None
                st = p.wait_for_job(job) if job else {"status": "no-job"}
                if st.get("status") == "completed":
                    r.update(status="scheduled", job_id=job)
                    ledger.upsert_planned(plan_id, s, acct, "scheduled", text_hash=th, job_id=job)
                    results["scheduled"] += 1
                elif st.get("status") == "timeout":
                    r.update(status="scheduled?", job_id=job, reason="job still working — postflight will confirm")
                    ledger.upsert_planned(plan_id, s, acct, "scheduled", text_hash=th, job_id=job, reason="job timeout; verify")
                    results["scheduled"] += 1
                else:
                    r.update(status="failed", job_id=job, reason=str(st)[:200])
                    ledger.upsert_planned(plan_id, s, acct, "failed", text_hash=th, job_id=job, reason=r["reason"])
                    results["failed"] += 1
            except PublerError as e:
                r.update(status="failed", reason=str(e)[:200])
                ledger.upsert_planned(plan_id, s, acct, "failed", text_hash=th, reason=r["reason"])
                results["failed"] += 1
            results["items"].append(r)
            time.sleep(sleep_between)
    out = Path(plan_path).with_name(Path(plan_path).stem + "_results.json")
    out.write_text(json.dumps(results, indent=1))
    ledger.record_run("publish", results["failed"] == 0, {k: v for k, v in results.items() if k != "items"})
    return results
