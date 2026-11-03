#!/usr/bin/env python3
"""asof.py — one rule for every weekly "month-to-date" report (2026-11-02).

Monday 11/2/2026 every MTD report held: the reporting Sunday was 11/1, so "November to date" was one closed
Sunday — no business, $0 everywhere, and the sanity gates correctly withheld. Rule: when the reporting day is a
Sunday that is the 1st of the month, the latest real month-to-date is the month that just closed, as of
Saturday (the last day of that month). Every MTD reader and the Monday pull use this, so they agree.

  python3 asof.py [YYYY-MM-DD]   -> prints the as-of date for that reporting day (default: yesterday)
"""
import datetime as dt
import sys


def asof(d):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d[:10])
    if d.weekday() == 6 and d.day == 1:
        return d - dt.timedelta(days=1)
    return d


def reporting_day(run_day):
    """The Monday chain reports on Sunday; any other day reports on itself."""
    if isinstance(run_day, str):
        run_day = dt.date.fromisoformat(run_day[:10])
    return run_day - dt.timedelta(days=1) if run_day.weekday() == 0 else run_day


if __name__ == "__main__":
    d = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today() - dt.timedelta(days=1)
    print(asof(d).isoformat())
