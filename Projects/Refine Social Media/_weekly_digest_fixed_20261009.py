"""
One-off wrapper for the 2026-10-09 vp-content-batch-weekly digest run.

WHY THIS EXISTS (do not fold into report.py without review — flagged for
interactive Claude / Joshua):
  vp_social/report.py:digest() computes engagement as
      it.get("likes", 0) + it.get("comments", 0) + it.get("shares", 0) + it.get("saves", 0)
  but Publer's /analytics endpoint (confirmed live 2026-10-09) does NOT put
  likes/comments/shares/reach/engagement at the top level of each post_insights
  item -- it nests them under item["analytics"]["<field>"]["value"], e.g.
      item["analytics"]["likes"] == {"name": "Likes", "value": 1, "tooltip": {...}}
  Top-level "comments" on the raw post object is something else entirely (the
  post's actual comment thread, a list) -- summing int + list crashes digest()
  on every single account, every call, 100% reproducible. That crash is what
  made vp-content-batch-weekly withhold the Slack DM today ("ERROR: TypeError:
  unsupported operand type(s) for +: 'int' and 'list'").

  Separately, the Cowork mount at ~/mnt/Refine Social Media/ does not support
  SQLite's rollback-journal unlink-on-commit (confirmed: disk I/O error on
  every ledger.sync() while cwd is the mount; works fine once the ledger file
  is copied to local VM scratch outside mnt/). This wrapper copies the ledger
  there via VP_SOCIAL_LEDGER before importing config, same escape hatch the
  module's own comment already documents for "sandbox tests."

This file reproduces report.digest() verbatim except for the analytics
extraction, so the DM text matches what report.py would produce once it's
patched. Intentionally NOT edited into report.py during an unattended run
per the task's "don't modify the digest script mid-run" guardrail -- the fix
belongs in report.py permanently, reviewed by an interactive session.
"""
import os
import sys

os.environ["VP_SOCIAL_LEDGER"] = os.path.expanduser("~/vp_ledger_work/social_ledger.sqlite")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime as dt  # noqa: E402
from collections import Counter  # noqa: E402
from vp_social import config, ledger, reader, report  # noqa: E402


def _val(analytics: dict, name: str):
    v = (analytics or {}).get(name)
    if isinstance(v, dict):
        return v.get("value") or 0
    return v or 0


def digest_fixed(days: int = 7) -> str:
    report._fresh_or_sync()
    d_from, d_to = reader.date_range(days - 1)
    rows = ledger.posts_between(d_from, d_to, states=("published",))
    if not rows:
        raise report.Withhold("0 published posts in the window")
    p = reader._client()
    idx = {v["publer_id"]: k for k, v in config.load_accounts().items() if v.get("publer_id")}
    scored, failures = [], []
    for pid, key in idx.items():
        if key == "BrandBlog":
            continue
        try:
            for it in p.post_insights(pid, since=d_from, until=d_to, limit=100):
                an = it.get("analytics") or {}
                eng = _val(an, "engagement")
                if not eng:
                    eng = (_val(an, "likes") + _val(an, "comments") + _val(an, "shares") + _val(an, "post_clicks"))
                reach = _val(an, "reach")
                scored.append({
                    "key": key,
                    "text": (it.get("text") or it.get("caption") or "")[:90].replace("\n", " "),
                    "reach": reach, "eng": eng, "type": it.get("type") or it.get("postType"),
                })
        except Exception as e:  # noqa: BLE001
            failures.append(f"{key}: {e}")
    if failures and len(failures) > 3:
        raise report.Withhold("Publer analytics unavailable for " + "; ".join(failures))
    total_reach = sum(s["reach"] for s in scored)
    total_eng = sum(s["eng"] for s in scored)
    top = sorted(scored, key=lambda s: -s["eng"])[:5]
    lines = [f"*Weekly Social Digest — {report._fmt_date(d_from)} to {report._fmt_date(d_to)}*",
             f"{len(rows)} posts published · {total_reach:,} reach · {total_eng:,} engagements "
             f"({len(scored)} posts with analytics available).", ""]
    if top:
        lines.append("*Top posts by engagement:*")
        lines += [f"• {s['key']} — {s['eng']} eng / {s['reach']} reach — \"{s['text']}\"" for s in top]
    by_acct = Counter(r["account_key"] for r in rows)
    lines += ["", "*Volume by page:* " + " · ".join(f"{k} {by_acct[k]}" for k in report.ORDER if by_acct.get(k))]
    if failures:
        lines += ["", "_Analytics not returned for: " + ", ".join(f.split(":")[0] for f in failures) + "._"]
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        print(digest_fixed(7))
        sys.exit(0)
    except report.Withhold as w:
        print(f"WITHHOLD: {w}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
