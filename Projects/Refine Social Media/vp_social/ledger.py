"""
The social ledger — one SQLite file that every lane writes to and every report reads from.

Tables
  posts      every Publer post we know about (synced nightly + written at publish time)
  planned    every slot the planner produced (plan_id, slot_id) and what became of it
  runs       one row per engine invocation (for STATUS / CHANGELOG, never for Slack)

Idempotency key for publishing = (week, lane, item_key, account_key). A slot with a
ledger row in state scheduled/published is never published twice.
"""
from __future__ import annotations
import json
import sqlite3
import datetime as dt
from contextlib import contextmanager
from pathlib import Path

from . import config
from . import reader

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
  publer_id      TEXT NOT NULL,
  account_id     TEXT NOT NULL,
  account_key    TEXT,
  provider       TEXT,
  state          TEXT,
  type           TEXT,
  source         TEXT,
  scheduled_at   TEXT,
  scheduled_date TEXT,
  text           TEXT,
  title          TEXT,
  text_hash      TEXT,
  media_ids      TEXT,
  post_link      TEXT,
  error          TEXT,
  updated_at     TEXT,
  lane           TEXT,
  item_key       TEXT,
  plan_id        TEXT,
  slot_id        TEXT,
  first_seen     TEXT,
  last_synced    TEXT,
  PRIMARY KEY (publer_id, account_id)
);
CREATE INDEX IF NOT EXISTS ix_posts_date ON posts(scheduled_date);
CREATE INDEX IF NOT EXISTS ix_posts_acct ON posts(account_key, scheduled_date);
CREATE INDEX IF NOT EXISTS ix_posts_item ON posts(item_key, account_key);

CREATE TABLE IF NOT EXISTS planned (
  plan_id      TEXT NOT NULL,
  slot_id      TEXT NOT NULL,
  week         TEXT,
  lane         TEXT,
  item_key     TEXT,
  account_key  TEXT,
  scheduled_at TEXT,
  kind         TEXT,               -- photo | video | status
  text_hash    TEXT,
  status       TEXT,               -- planned | scheduled | published | skipped | failed
  job_id       TEXT,
  publer_id    TEXT,
  reason       TEXT,
  created_at   TEXT,
  updated_at   TEXT,
  PRIMARY KEY (plan_id, slot_id, account_key)
);
CREATE INDEX IF NOT EXISTS ix_planned_key ON planned(week, lane, item_key, account_key);

CREATE TABLE IF NOT EXISTS runs (
  run_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT, finished_at TEXT, command TEXT, ok INTEGER, summary TEXT
);
"""


def _now() -> str:
    return dt.datetime.now(config.TZ).isoformat(timespec="seconds")


@contextmanager
def connect(path: Path = config.LEDGER_PATH):
    con = sqlite3.connect(path, timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()


# --- sync from Publer ----------------------------------------------------

def sync(days_back: int = 21, days_forward: int = 30) -> dict:
    """Pull every post in the window from Publer and upsert. Returns counts."""
    d_from, d_to = reader.date_range(days_back, days_forward)
    recs = reader.fetch_window(d_from, d_to)
    now = _now()
    ins = upd = 0
    with connect() as con:
        for r in recs:
            row = con.execute("SELECT publer_id FROM posts WHERE publer_id=? AND account_id=?",
                              (r["publer_id"], r["account_id"])).fetchone()
            if row:
                con.execute("""UPDATE posts SET state=?, type=?, source=?, scheduled_at=?, scheduled_date=?,
                               text=?, title=?, text_hash=?, media_ids=?, post_link=?, error=?, updated_at=?,
                               account_key=?, provider=?, last_synced=? WHERE publer_id=? AND account_id=?""",
                            (r["state"], r["type"], r["source"], r["scheduled_at"], r["scheduled_date"],
                             r["text"], r["title"], r["text_hash"], r["media_ids"], r["post_link"], r["error"],
                             r["updated_at"], r["account_key"], r["provider"], now, r["publer_id"], r["account_id"]))
                upd += 1
            else:
                con.execute("""INSERT INTO posts (publer_id, account_id, account_key, provider, state, type, source,
                               scheduled_at, scheduled_date, text, title, text_hash, media_ids, post_link, error,
                               updated_at, first_seen, last_synced)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (r["publer_id"], r["account_id"], r["account_key"], r["provider"], r["state"], r["type"],
                             r["source"], r["scheduled_at"], r["scheduled_date"], r["text"], r["title"],
                             r["text_hash"], r["media_ids"], r["post_link"], r["error"], r["updated_at"], now, now))
                ins += 1
        # attach lane/item/plan from planned rows by matching (account_key, text_hash) or publer_id
        con.execute("""UPDATE posts SET plan_id=(SELECT plan_id FROM planned pl WHERE pl.publer_id=posts.publer_id
                        AND pl.account_key=posts.account_key LIMIT 1)
                       WHERE plan_id IS NULL AND EXISTS (SELECT 1 FROM planned pl WHERE pl.publer_id=posts.publer_id
                        AND pl.account_key=posts.account_key)""")
        con.execute("""UPDATE posts SET lane=(SELECT lane FROM planned pl WHERE pl.account_key=posts.account_key
                        AND pl.text_hash=posts.text_hash AND pl.text_hash!='' LIMIT 1),
                       item_key=(SELECT item_key FROM planned pl WHERE pl.account_key=posts.account_key
                        AND pl.text_hash=posts.text_hash AND pl.text_hash!='' LIMIT 1),
                       plan_id=COALESCE(plan_id,(SELECT plan_id FROM planned pl WHERE pl.account_key=posts.account_key
                        AND pl.text_hash=posts.text_hash AND pl.text_hash!='' LIMIT 1)),
                       slot_id=COALESCE(slot_id,(SELECT slot_id FROM planned pl WHERE pl.account_key=posts.account_key
                        AND pl.text_hash=posts.text_hash AND pl.text_hash!='' LIMIT 1))
                       WHERE lane IS NULL AND EXISTS (SELECT 1 FROM planned pl WHERE pl.account_key=posts.account_key
                        AND pl.text_hash=posts.text_hash AND pl.text_hash!='')""")
        # resolve planned rows that now have a live post
        con.execute("""UPDATE planned SET publer_id=(SELECT publer_id FROM posts p WHERE p.account_key=planned.account_key
                        AND p.text_hash=planned.text_hash AND p.text_hash!='' LIMIT 1),
                       status=CASE WHEN (SELECT state FROM posts p WHERE p.account_key=planned.account_key
                        AND p.text_hash=planned.text_hash LIMIT 1)='published' THEN 'published'
                        WHEN (SELECT state FROM posts p WHERE p.account_key=planned.account_key
                        AND p.text_hash=planned.text_hash LIMIT 1)='failed' THEN 'failed' ELSE 'scheduled' END,
                       updated_at=?
                       WHERE status IN ('planned','scheduled') AND text_hash!='' AND EXISTS
                        (SELECT 1 FROM posts p WHERE p.account_key=planned.account_key AND p.text_hash=planned.text_hash)""",
                    (now,))
        con.execute("INSERT INTO runs (started_at, finished_at, command, ok, summary) VALUES (?,?,?,?,?)",
                    (now, _now(), "sync", 1, json.dumps({"from": d_from, "to": d_to, "fetched": len(recs),
                                                          "inserted": ins, "updated": upd})))
    return {"from": d_from, "to": d_to, "fetched": len(recs), "inserted": ins, "updated": upd}


# --- queries used by planner / publisher / reports ---------------------------

def posts_between(date_from: str, date_to: str, states=("scheduled", "published")) -> list[sqlite3.Row]:
    q = f"""SELECT * FROM posts WHERE scheduled_date BETWEEN ? AND ? AND state IN ({",".join("?"*len(states))})
            ORDER BY scheduled_at"""
    with connect() as con:
        return con.execute(q, (date_from, date_to, *states)).fetchall()


def recent_item_posts(item_key: str, account_key: str, days: int) -> list[sqlite3.Row]:
    d_from, d_to = reader.date_range(days, 30)
    with connect() as con:
        return con.execute("""SELECT * FROM posts WHERE item_key=? AND account_key=? AND scheduled_date BETWEEN ? AND ?
                              AND state IN ('scheduled','published')""", (item_key, account_key, d_from, d_to)).fetchall()


def caption_exists(text_hash: str, days: int = 7) -> list[sqlite3.Row]:
    d_from, d_to = reader.date_range(days, 30)
    with connect() as con:
        return con.execute("""SELECT account_key, scheduled_date FROM posts WHERE text_hash=? AND scheduled_date BETWEEN ? AND ?
                              AND state IN ('scheduled','published')""", (text_hash, d_from, d_to)).fetchall()


def planned_status(week: str, lane: str, item_key: str, account_key: str) -> sqlite3.Row | None:
    with connect() as con:
        return con.execute("""SELECT * FROM planned WHERE week=? AND lane=? AND item_key=? AND account_key=?
                              AND status IN ('scheduled','published') LIMIT 1""",
                           (week, lane, item_key, account_key)).fetchone()


def upsert_planned(plan_id: str, slot: dict, account_key: str, status: str, **kw) -> None:
    now = _now()
    with connect() as con:
        con.execute("""INSERT INTO planned (plan_id, slot_id, week, lane, item_key, account_key, scheduled_at, kind,
                       text_hash, status, job_id, publer_id, reason, created_at, updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(plan_id, slot_id, account_key) DO UPDATE SET status=excluded.status,
                       job_id=COALESCE(excluded.job_id, planned.job_id), publer_id=COALESCE(excluded.publer_id, planned.publer_id),
                       reason=excluded.reason, text_hash=excluded.text_hash, scheduled_at=excluded.scheduled_at, updated_at=excluded.updated_at""",
                    (plan_id, slot["slot_id"], slot.get("week"), slot.get("lane"), slot.get("item_key"), account_key,
                     slot.get("scheduled_at"), slot.get("kind"), kw.get("text_hash", ""), status, kw.get("job_id"),
                     kw.get("publer_id"), kw.get("reason"), now, now))


def record_run(command: str, ok: bool, summary: dict) -> None:
    with connect() as con:
        con.execute("INSERT INTO runs (started_at, finished_at, command, ok, summary) VALUES (?,?,?,?,?)",
                    (_now(), _now(), command, 1 if ok else 0, json.dumps(summary)))


def last_sync_at() -> str | None:
    with connect() as con:
        row = con.execute("SELECT finished_at FROM runs WHERE command='sync' AND ok=1 ORDER BY run_id DESC LIMIT 1").fetchone()
        return row[0] if row else None
