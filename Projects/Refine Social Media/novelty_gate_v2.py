#!/usr/bin/env python3
"""
novelty_gate_v2.py — supplementary, strictly-tightening novelty check.

ADDITIVE by design (Rule #4): creative_drift.py is untouched. This module is an
EXTRA hurdle a candidate must clear on top of DriftEngine.is_novel(), never a
replacement and never a relaxation. A candidate that this module blocks would
have been allowed through by the base gate.

Why it exists — defect found during the 2026-08-22 Q4 refresh:
    DriftEngine.is_novel() compares the FIRST FIVE WORDS of two titles and
    rejects at an overlap of >= 3. Existing formats with SHORT titles can
    therefore never be matched. "Caption this photo please" scores an overlap of
    2 against the live format "Caption this" and passes cleanly. Roughly a third
    of the seed registry has titles under four words, so a third of the registry
    is currently unprotected against re-skins - which is precisely the failure
    the quarterly gate exists to prevent.

Three added checks:
    1. SUBSET       - one title's words fully contain the other's (any length).
    2. JACCARD      - full-title word similarity >= 0.55, ignoring stopwords.
    3. HOOK VERB    - same pillar + same leading verb + same head noun.
"""
from __future__ import annotations

STOP = {"a", "an", "the", "this", "that", "these", "those", "is", "are", "was",
        "it", "its", "of", "to", "for", "and", "or", "in", "on", "at", "by",
        "we", "you", "your", "our", "us", "here", "what", "how", "why", "with"}


def _words(s: str) -> list[str]:
    return [w.strip(".,!?:;\"'()") for w in s.lower().split() if w.strip(".,!?:;\"'()")]


def _content(s: str) -> set[str]:
    return {w for w in _words(s) if w not in STOP}


def check(title: str, template: str, pillar: str, existing: list) -> tuple[bool, str]:
    """existing: iterable of objects with .id/.title/.template/.pillar/.status."""
    t_all, t_con = set(_words(title)), _content(title)
    for f in existing:
        if getattr(f, "status", "") == "retired":
            continue
        f_all, f_con = set(_words(f.title)), _content(f.title)

        # 1. subset — catches "Caption this" vs "Caption this photo please"
        if t_all and f_all and (t_all <= f_all or f_all <= t_all):
            return False, f"title is a word-subset of '{f.id}' ({f.title!r})"

        # 2. jaccard on content words
        if t_con and f_con:
            j = len(t_con & f_con) / len(t_con | f_con)
            if j >= 0.55:
                return False, f"title {j:.0%} similar to '{f.id}' ({f.title!r})"

        # 3. same pillar + same opening verb + same head noun
        if f.pillar == pillar and t_con and f_con:
            tw, fw = _words(title), _words(f.title)
            if tw and fw and tw[0] == fw[0] and (t_con & f_con):
                return False, f"same pillar, same opening word as '{f.id}'"
    return True, ""
