#!/usr/bin/env python3
"""
Age-aware discount allowance (Valley Pawn). Built 2026-09-28.

  from discount_policy import judge
  judge(discount_pct=0.35, discount_dollars=21.0, age=<item_age.estimate(...)>)
  -> {'age_days': 20, 'band': '0-30', 'allowed_pct': 0.10, 'over_by_pct': 0.25,
      'age_flag': True, 'basis': 'age'}

A sale is an AGE FLAG when discount_pct > allowed_pct for its age band and the
dollars off are at least min_dollars_to_flag. If age is unknown, age_flag is None
and the caller keeps its own flat rule. Numbers live in discount_policy.json.
"""
from __future__ import annotations
import json, os

_HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_FILE = os.path.join(_HERE, "discount_policy.json")
_policy = None


def policy() -> dict:
    global _policy
    if _policy is None:
        with open(POLICY_FILE) as f:
            _policy = json.load(f)
    return _policy


def allowance(age_days: int | None):
    if age_days is None:
        return None
    for b in policy()["bands"]:
        if age_days <= b["max_days"]:
            return b
    return policy()["bands"][-1]


def judge(discount_pct: float | None, discount_dollars: float | None, age: dict | None) -> dict:
    out = {"age_days": None, "band": None, "allowed_pct": None, "over_by_pct": None,
           "age_flag": None, "basis": "unknown-age", "age_confidence": "unknown",
           "age_lower_bound": False}
    if not age or age.get("age_days") is None:
        return out
    b = allowance(age["age_days"])
    out.update(age_days=age["age_days"], band=b["label"], allowed_pct=b["allowed_pct"],
               basis="age", age_confidence=age.get("confidence", "unknown"),
               age_lower_bound=bool(age.get("lower_bound")))
    if discount_pct is None:
        out["age_flag"] = False
        return out
    over = discount_pct - b["allowed_pct"]
    out["over_by_pct"] = round(over, 4)
    out["age_flag"] = bool(over > 0.0001 and (discount_dollars or 0) >= policy()["min_dollars_to_flag"])
    return out
