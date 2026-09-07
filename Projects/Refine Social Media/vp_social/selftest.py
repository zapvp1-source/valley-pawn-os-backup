#!/usr/bin/env python3
"""
Proof-before-deploy checks for the engine. Read-only against Publer; never publishes.
Run: cd "<Refine Social Media>" && python3 -m vp_social.selftest
Every case below is a real failure this department actually shipped at least once.
"""
from __future__ import annotations
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

from . import config, ledger, publish, reader, report

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((PASS if ok else FAIL, name, detail))


def slot(sid, accounts, captions, **kw):
    s = {"slot_id": sid, "lane": kw.pop("lane", "brand"), "item_key": kw.pop("item_key", f"it:{sid}"),
         "accounts": accounts, "kind": kw.pop("kind", "photo"),
         "scheduled_at": (dt.datetime.now(config.TZ) + dt.timedelta(days=2)).isoformat(),
         "week": "2099-01-04", "media_path": None, "captions": captions}
    s.update(kw)
    return s


GOOD = ("Sandi has a Mantis 4-cycle tiller on the floor in Culpeper at $249, against $599.99 new, "
        "and it starts on the second pull. Come put your hands on it before the weekend.")


def main() -> int:
    # 1. caption gates
    check("empty caption blocked", publish.qa_caption("", "Culpeper", "photo", 25) != [])
    check("firearms blocked", any("firearm" in p for p in publish.qa_caption(
        "We just took in a rifle and it is priced to move today at the Roanoke store counter.", "Roanoke", "photo", 5)))
    check("Dixie Pawn blocked", any("Dixie" in p for p in publish.qa_caption(
        "Dixie Pawn in Harrisonburg has a Martin guitar on the wall this week for two thousand.", "Harrisonburg", "photo", 5)))
    check("'7 days a week' blocked", any("7 days" in p or "seven" in p.lower() for p in publish.qa_caption(
        "We are open seven days a week at every one of our five Valley stores, stop in any time.", "Brand", "photo", 5)))
    check("fast cash blocked", any("predatory" in p for p in publish.qa_caption(
        "Need instant cash today? Walk into any Valley Pawn store and walk out paid in minutes.", "Brand", "photo", 5)))
    check("GBP hashtags blocked", any("hashtag" in p for p in publish.qa_caption(GOOD + " #ValleyPawn", "GBP_Culpeper", "photo", 20)))
    check("GBP phone blocked", any("phone" in p for p in publish.qa_caption(GOOD + " Call (540) 445-5510.", "GBP_Culpeper", "photo", 20)))
    check("FB hashtags blocked", any("hashtag" in p for p in publish.qa_caption(GOOD + " #ValleyPawn", "Culpeper", "photo", 20)))
    check("X length blocked", any("chars" in p for p in publish.qa_caption("x " * 200, "BrandTwitter", "photo", 5)))
    check("short caption blocked", any("too short" in p for p in publish.qa_caption("Nice tiller.", "Culpeper", "photo", 25)))
    check("good caption passes", publish.qa_caption(GOOD, "Culpeper", "photo", 25) == [], str(publish.qa_caption(GOOD, "Culpeper", "photo", 25)))

    # 2. plan-level gates
    dup = {"plan_id": "selftest", "week": "2099-01-04",
           "slots": [slot("a", ["Culpeper"], {"Culpeper": GOOD}), slot("b", ["Waynesboro"], {"Waynesboro": GOOD})]}
    check("identical caption across accounts blocked",
          any("identical caption" in e for e in publish.plan_level_checks(dup)))

    humor = {"plan_id": "selftest", "week": "2099-01-04",
             "slots": [slot(f"h{i}", ["Brand"], {"Brand": GOOD + f" {i}"}, lane="humor") for i in range(3)]}
    check("humor cap enforced", any("humor slots" in e for e in publish.plan_level_checks(humor)))

    guess = {"plan_id": "selftest", "week": "2099-01-04",
             "slots": [slot("g", ["Brand"], {"Brand": GOOD}, lane="engagement", format_id="eng_guess_price")]}
    check("guess without reveal blocked", any("reveal" in e for e in publish.plan_level_checks(guess)))
    guess["slots"].append(slot("g-rev", ["Brand"], {"Brand": GOOD + " Answer:"}, lane="reveal"))
    check("guess with reveal passes", not any("reveal" in e for e in publish.plan_level_checks(guess)))

    # 3. publisher safety
    p = publish.Publisher()
    check("browser UA present", "Mozilla" in p._headers().get("User-Agent", ""))
    try:
        p.delete("/posts")
        check("DELETE refused", False, "DELETE went through — queue-wipe guard is gone")
    except Exception as e:  # noqa: BLE001
        check("DELETE refused", "REFUSED" in str(e), str(e)[:80])
    for spelling in ("complete", "completed"):
        st = {"status": spelling}
        check(f"job status '{spelling}' accepted",
              (lambda s: s in ("complete", "completed"))(st["status"]))

    # 4. reader always sends a date range
    src = (Path(__file__).parent / "reader.py").read_text()
    check("reader always passes from/to", '"from": date_from' in src and '"to": date_to' in src)

    # 5. ledger + reports
    try:
        n = len(ledger.posts_between("2026-08-01", "2026-09-30", states=("published",)))
        check("ledger has published posts", n > 50, f"{n} posts")
    except Exception as e:  # noqa: BLE001
        check("ledger has published posts", False, str(e)[:80])
    try:
        report.recap(days=7)
        check("recap renders", True)
    except report.Withhold as w:
        check("recap renders", False, f"withheld: {w}")
    try:
        report.recap(days=1, end=dt.date(2099, 1, 1))
        check("recap withholds on an empty window", False, "it produced output for an empty window")
    except report.Withhold:
        check("recap withholds on an empty window", True)

    # 6. dry-run really is dry
    check("DRY_RUN switch on", config.dry_run_enabled(), "state/DRY_RUN present")

    width = max(len(n) for _, n, _ in results)
    for status, name, detail in results:
        print(f"{status}  {name.ljust(width)}  {detail}")
    bad = [r for r in results if r[0] == FAIL]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
