#!/usr/bin/env python3
"""
mkt_lib — shared primitives for the marketing data layer. Stdlib only, no deps.

Created 2026-09-05 (AI Marketing umbrella plan §5). Three things every marketing
task needs and each was re-implementing on its own:

  1. data_path()      — where a day's cached pull for a source lives, so ONE task
                        pulls and every consumer reads the cache.
  2. write_json()/read_json() — atomic, idempotent, resumable day-files.
  3. chrome_lock()    — mutual exclusion for the two jobs that legitimately need a
                        browser (AI-engine prompt tests, Facebook comment sweep) so
                        they never collide with each other or with the Bravo pipeline.

Formatter contract (see format_aged_inventory.py, the proven pattern):
  a formatter prints the EXACT Slack body on stdout and exits 0, or prints NOTHING
  and exits 2. Callers post stdout verbatim on 0 and post nothing on 2. Use
  withhold() to bail out of a formatter correctly.
"""
from __future__ import annotations
import errno, json, os, sys, tempfile, time
from contextlib import contextmanager
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Ai Optimized Marketing/
DATA = os.path.join(ROOT, "data")
LOCK_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/_run_locks")
SOURCES = ("social", "email", "reputation", "presence", "deals", "blog", "ebay", "website")


# ---------- day-file cache ----------

def data_path(source: str, day: str | date | None = None, ext: str = "json") -> str:
    """Path to one day's cached pull for a source. Creates the directory."""
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}; expected one of {SOURCES}")
    day = day or date.today()
    day = day.isoformat() if isinstance(day, date) else str(day)
    d = os.path.join(DATA, source)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{day}.{ext}")


def write_json(path: str, obj) -> str:
    """Atomic write: temp file in the same dir + rename. Never leaves a half file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise
    return path


def read_json(path: str, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def cached(source: str, day=None, max_age_hours: float | None = None):
    """Return today's cached pull if it exists (and is fresh enough), else None.
    Lets a consumer read what the collector already pulled instead of re-pulling."""
    p = data_path(source, day)
    if not os.path.exists(p):
        return None
    if max_age_hours is not None:
        if (time.time() - os.path.getmtime(p)) > max_age_hours * 3600:
            return None
    return read_json(p)


# ---------- formatter contract ----------

def withhold(reason: str) -> "NoReturn":
    """Rule 18: incomplete or unvalidated data is WITHHELD, never caveated.
    Prints nothing to stdout; reason goes to stderr for the run log; exit 2."""
    print(f"WITHHOLD: {reason}", file=sys.stderr)
    sys.exit(2)


def emit(body: str) -> "NoReturn":
    """Print the exact Slack body and exit 0. Callers post stdout verbatim."""
    sys.stdout.write(body if body.endswith("\n") else body + "\n")
    sys.exit(0)


# ---------- chrome mutual exclusion ----------

@contextmanager
def chrome_lock(owner: str, timeout_s: int = 900, poll_s: int = 15, stale_s: int = 3600):
    """Exclusive lock for anything driving Chrome, shared with the Bravo pipeline's
    lock directory. Usage:

        with chrome_lock("vp-ai-visibility-metrics") as got:
            if not got:
                withhold("chrome busy")   # or defer to the retry queue
            ...drive the browser...

    Never blocks forever: gives up after `timeout_s` and yields False.
    A lock file older than `stale_s` is treated as abandoned and taken over
    (a crashed run must not wedge the fleet).
    """
    os.makedirs(LOCK_DIR, exist_ok=True)
    path = os.path.join(LOCK_DIR, "chrome.lock")
    deadline = time.time() + timeout_s
    fd = None
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({
                "owner": owner, "pid": os.getpid(),
                "acquired": datetime.now().isoformat(timespec="seconds"),
            }).encode())
            os.close(fd); fd = None
            break
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            try:
                age = time.time() - os.path.getmtime(path)
                holder = read_json(path, {}) or {}
            except OSError:
                age, holder = 0, {}
            if age > stale_s:
                print(f"chrome_lock: taking over stale lock held by "
                      f"{holder.get('owner','?')} for {int(age)}s", file=sys.stderr)
                try: os.unlink(path)
                except OSError: pass
                continue
            if time.time() >= deadline:
                print(f"chrome_lock: gave up after {timeout_s}s; held by "
                      f"{holder.get('owner','?')}", file=sys.stderr)
                yield False
                return
            time.sleep(poll_s)
    try:
        yield True
    finally:
        try: os.unlink(path)
        except OSError: pass


if __name__ == "__main__":
    # self-test: no side effects beyond a temp day-file under data/_selftest
    p = data_path("social", "1970-01-01")
    write_json(p, {"ok": True})
    assert read_json(p)["ok"] is True
    os.unlink(p)
    with chrome_lock("selftest", timeout_s=5) as got:
        assert got is True
        with chrome_lock("selftest-2", timeout_s=1, poll_s=1) as got2:
            assert got2 is False, "second acquire should fail while first is held"
    assert not os.path.exists(os.path.join(LOCK_DIR, "chrome.lock")), "lock not released"
    print("mkt_lib self-test PASS")
