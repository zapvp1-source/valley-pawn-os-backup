#!/usr/bin/env python3
"""
creative_drift.py — Valley Pawn creative drift engine.

Implements CREATIVE_DRIFT.md. Owns which content formats run in a given week,
enforces cooldowns and the exploration budget, gates performance claims behind a
statistical confidence threshold, and applies the seasonal skin.

The two failure modes this exists to prevent, both observed in the 2026-08-22
90-day audit:

  FREEZE      — the same caption ran 21 times across 5 accounts, and one ran four
                times on the SAME page. Nothing owned novelty.
  NOISE-CHASE — the Friday loop moved the content mix on n=8 posts with
                single-digit engagement ("top: warranty 36 reach, bottom: warranty
                0 reach, +5% warranty"). Nothing owned statistical honesty.

Exploration budget fixes the first. MIN_POSTS_FOR_SIGNAL fixes the second.

CLI
---
    python3 creative_drift.py init                 # seed the registry
    python3 creative_drift.py select --lane community --slots 4
    python3 creative_drift.py record --format-id X --account Brand --engagement 3 --reach 120
    python3 creative_drift.py refresh               # quarterly: retire / rest / report gaps
    python3 creative_drift.py status
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "creative_state.json"
LEDGER_PATH = ROOT / "CREATIVE_LEDGER.md"

# --- Tunables, all justified in CREATIVE_DRIFT.md ---------------------------
MIN_POSTS_FOR_SIGNAL = 30      # below this, measured performance is IGNORED
EXPLORE_FLOOR = 0.15           # never fall below this share of slots
COOLDOWN_FORMAT_DAYS = 21      # same format, same page
COOLDOWN_HOOK_DAYS = 45        # same hook/angle, same page
COOLDOWN_HUMOR_DAYS = 60       # same humor bit, anywhere
DECLINE_REST_THRESHOLD = 0.40  # >40% off its own peak -> rest a quarter

SEASONS = [
    ("late_summer", (8, 22), (9, 15), "Warm gold, high sun",
     "Back-to-school, last warm evenings", "laptops, tablets, dorm gear, mowers"),
    ("early_fall", (9, 15), (10, 15), "Amber, oxblood accents",
     "First cool morning, harvest", "tools, generators, hunting prep, layaway opens"),
    ("peak_fall", (10, 15), (11, 10), "Deep amber, navy",
     "Foliage, Friday night lights", "storm prep, gold selling, Halloween"),
    ("early_winter", (11, 10), (12, 5), "Navy, gold, ivory",
     "Gratitude, Veterans, gathering", "Black Friday, layaway payoff"),
    ("holiday", (12, 5), (12, 26), "Gold on navy, warm light",
     "Gifts, tradition, made it home", "jewelry, watches, layaway pickup"),
    ("new_year", (12, 26), (1, 31), "Cool navy, clean ivory",
     "Reset, cash flow, fresh start", "gold buying, pawn loans - peak pawn season"),
]

STORES = ["Culpeper", "Harrisonburg", "Lexington", "Roanoke", "Waynesboro"]


# ---------------------------------------------------------------------------
def season_for(d: date) -> dict:
    for name, (m0, d0), (m1, d1), palette, hooks, subjects in SEASONS:
        start = date(d.year, m0, d0)
        end = date(d.year if m1 >= m0 else d.year + 1, m1, d1)
        if m1 < m0:  # wraps the year (new_year)
            if d >= start or d <= date(d.year, m1, d1):
                return {"season": name, "palette": palette, "hooks": hooks, "subjects": subjects}
        elif start <= d < end:
            return {"season": name, "palette": palette, "hooks": hooks, "subjects": subjects}
    return {"season": "new_year", "palette": SEASONS[-1][3],
            "hooks": SEASONS[-1][4], "subjects": SEASONS[-1][5]}


@dataclass
class Format:
    id: str
    lane: str                 # community | engagement | video | product | humor
    pillar: str
    title: str
    template: str
    status: str = "candidate"       # candidate | active | resting | retired
    seasons: list[str] = field(default_factory=list)   # empty = all seasons
    hook_key: str = ""              # cooldown key for the angle
    created: str = ""
    posts: int = 0
    engagement_total: float = 0.0
    reach_total: float = 0.0
    peak_index: float = 0.0
    last_used: dict[str, str] = field(default_factory=dict)   # account -> ISO date
    notes: str = ""

    # -- derived ------------------------------------------------------------
    @property
    def index(self) -> float:
        """Engagement per post. Meaningless below the signal threshold."""
        return self.engagement_total / self.posts if self.posts else 0.0

    @property
    def confident(self) -> bool:
        return self.posts >= MIN_POSTS_FOR_SIGNAL

    def days_since(self, account: str, today: date) -> int:
        iso = self.last_used.get(account)
        if not iso:
            return 10_000
        return (today - date.fromisoformat(iso)).days

    def on_cooldown(self, account: str, today: date) -> bool:
        window = COOLDOWN_HUMOR_DAYS if self.lane == "humor" else COOLDOWN_FORMAT_DAYS
        return self.days_since(account, today) < window


# ---------------------------------------------------------------------------
class DriftEngine:
    def __init__(self, path: Path = STATE_PATH):
        self.path = path
        self.state = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            raw["formats"] = [Format(**f) for f in raw.get("formats", [])]
            return raw
        return {"version": 1, "created": date.today().isoformat(),
                "formats": [], "untried_territory": [], "history": []}

    def save(self) -> None:
        out = dict(self.state)
        out["formats"] = [asdict(f) for f in self.state["formats"]]
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(out, indent=2))
        tmp.replace(self.path)   # atomic — a killed run never truncates the registry

    # -- exploration budget -------------------------------------------------
    def measured_posts(self) -> int:
        return sum(f.posts for f in self.state["formats"])

    def explore_share(self) -> float:
        """
        Cold start deliberately runs HOT on exploration.

        Valley Pawn has volume without signal: 485 measured posts in the audited
        90 days, but a median engagement of 0.0 on 8 of 9 accounts. Near-zero
        variance is not information, so total-post count alone must not be
        allowed to graduate us out of exploration. We also require that at least
        a few formats have cleared the signal threshold.
        """
        n = self.measured_posts()
        confident = sum(1 for f in self.state["formats"] if f.confident)
        if n < 200 or confident < 3:
            return 0.40
        if n < 800 or confident < 8:
            return 0.25
        return EXPLORE_FLOOR

    # -- selection ----------------------------------------------------------
    def select(self, lane: str, slots: int, account: str = "Brand",
               today: date | None = None, seed: int | None = None) -> list[Format]:
        today = today or date.today()
        rng = random.Random(seed)
        season = season_for(today)["season"]

        pool = [
            f for f in self.state["formats"]
            if f.lane == lane
            and f.status in ("candidate", "active")
            and (not f.seasons or season in f.seasons)
            and not f.on_cooldown(account, today)
        ]
        if not pool:
            return []

        untried = [f for f in pool if f.posts == 0]
        proven = [f for f in pool if f.posts > 0]

        n_explore = max(1, round(slots * self.explore_share())) if untried else 0
        n_explore = min(n_explore, len(untried), slots)

        chosen = rng.sample(untried, n_explore) if n_explore else []

        def score(f: Format) -> float:
            # Unproven formats contribute NO performance term — unknown, not bad.
            perf = f.index if f.confident else 0.0
            novelty = 1.0 / (1.0 + f.posts) * 2.0
            fatigue = max(0.0, 1.0 - f.days_since(account, today) / 90.0)
            return perf + novelty - fatigue

        rest = sorted(
            [f for f in proven + untried if f not in chosen], key=score, reverse=True
        )
        chosen += rest[: max(0, slots - len(chosen))]
        return chosen[:slots]

    # -- recording ----------------------------------------------------------
    def record(self, format_id: str, account: str, engagement: float,
               reach: float = 0.0, when: date | None = None) -> None:
        when = when or date.today()
        for f in self.state["formats"]:
            if f.id == format_id:
                f.posts += 1
                f.engagement_total += engagement
                f.reach_total += reach
                f.last_used[account] = when.isoformat()
                if f.status == "candidate" and f.posts >= 3:
                    f.status = "active"
                f.peak_index = max(f.peak_index, f.index)
                return
        raise KeyError(f"unknown format id: {format_id}")

    # -- quarterly refresh --------------------------------------------------
    def refresh(self, today: date | None = None) -> dict:
        """Retire the proven-bad, rest the fatigued, report how many new ideas are owed."""
        today = today or date.today()
        confident = [f for f in self.state["formats"]
                     if f.confident and f.status == "active"]
        report = {"retired": [], "rested": [], "candidates_needed": 0,
                  "season": season_for(today)["season"]}

        if len(confident) >= 5:
            ranked = sorted(confident, key=lambda f: f.index)
            cutoff = max(1, len(ranked) // 5)
            for f in ranked[:cutoff]:
                # Two strikes, not one — a single weak quarter is variance.
                strikes = int(f.notes.count("[weak]")) + 1
                f.notes = (f.notes + f" [weak]{today.isoformat()}").strip()
                if strikes >= 2:
                    f.status = "retired"
                    report["retired"].append(f.id)

        for f in self.state["formats"]:
            if (f.status == "active" and f.confident and f.peak_index > 0
                    and f.index < f.peak_index * (1 - DECLINE_REST_THRESHOLD)):
                f.status = "resting"
                report["rested"].append(f.id)

        active = sum(1 for f in self.state["formats"] if f.status in ("active", "candidate"))
        report["candidates_needed"] = max(8, 24 - active)
        return report

    # -- novelty gate -------------------------------------------------------
    def is_novel(self, title: str, template: str, pillar: str) -> tuple[bool, str]:
        """
        Reject a proposed format that is a re-skin of something already live.
        Deterministic and cheap by design — this runs before anything is queued,
        and it is what stops the quarterly 'invent new formats' step from
        regenerating the same handful of ideas with new adjectives.
        """
        t_words = set(title.lower().split()[:5])
        for f in self.state["formats"]:
            if f.status == "retired":
                continue
            if f.pillar == pillar and len(t_words & set(f.title.lower().split()[:5])) >= 3:
                return False, f"opening overlaps existing format '{f.id}'"
            if f.template.strip().lower() == template.strip().lower():
                return False, f"identical template to '{f.id}'"
        return True, ""

    def add_candidate(self, fmt: Format) -> tuple[bool, str]:
        ok, why = self.is_novel(fmt.title, fmt.template, fmt.pillar)
        if not ok:
            return False, why
        fmt.status = "candidate"
        fmt.created = date.today().isoformat()
        self.state["formats"].append(fmt)
        return True, ""


# ---------------------------------------------------------------------------
SEED_FORMATS = [
    # lane, pillar, id, title, template, seasons
    ("community", "Community", "com_landmark_morning", "Morning at a local landmark",
     "One landmark, one specific true detail, one sentence of weather/light. No CTA.", []),
    ("community", "Community", "com_local_calendar", "This weekend in town",
     "A confirmed [C26] local event, described as a neighbor would. No CTA, no product.", []),
    ("community", "Community", "com_friday_lights", "Friday night football",
     "Name the local high school and mascot, wish them well. Nothing else.", ["early_fall", "peak_fall"]),
    ("community", "Community", "com_first_cold", "First cold morning",
     "The first genuinely cold morning of the year in this specific town.", ["early_fall", "peak_fall"]),
    ("community", "Community", "com_then_now", "Then and now",
     "A historic detail about a building or street locals walk past every day.", []),
    ("community", "Community", "com_foliage_timing", "Foliage, town by town",
     "When THIS town's color actually turns - differs by elevation across our five.", ["peak_fall"]),
    ("community", "Community", "com_local_word", "How locals say it",
     "A nickname only people from this town use, and where it came from.", []),
    ("community", "Community", "com_small_detail", "The detail you walk past",
     "One overlooked physical detail downtown - brickwork, a date stone, a mural corner.", []),
    ("community", "Community", "com_market_day", "Market morning",
     "The local farmers market as a scene, not an ad. Season and closing dates matter.", []),
    ("community", "Community", "com_college_town", "Campus is back",
     "The week the students return and the town changes character. JMU, VMI, W&L, Roanoke College.", []),
    ("engagement", "Engagement", "eng_stock_poll", "What should we stock more of?",
     "Straight poll. Then actually act on the answer and say so later.", []),
    ("engagement", "Engagement", "eng_caption_this", "Caption this",
     "One genuinely odd photo from the counter. Best caption wins nothing but glory.", []),
    ("engagement", "Engagement", "eng_guess_price", "Guess the price",
     "Real item, price hidden, answer revealed in comments the next day.", []),
    ("engagement", "Engagement", "eng_what_is_it", "What is this thing?",
     "An odd item that genuinely walked in. Ask, then answer in the comments.", []),
    ("engagement", "Engagement", "eng_this_or_that", "This or that",
     "Two real items side by side. Which one are you taking home?", []),
    ("engagement", "Engagement", "eng_best_find", "Best find you ever made",
     "Open question. No product, no CTA - just ask and then actually reply to everyone.", []),
    ("engagement", "Engagement", "eng_makers_mark", "Who made this?",
     "Macro shot of a maker's mark or hallmark. Ask people to identify it.", []),
    ("video", "Deal", "vid_deal_reel", "Deal Reel",
     "Machine-rendered vertical reel from the Monday deal photo. Zero human input.", []),
    ("video", "Story", "vid_walked_in", "What walked in this week",
     "Short round-up reel of the odd/interesting things that came across the counter.", []),
    ("video", "Story", "vid_one_object", "The story of one object",
     "A single item, its maker, its era, why it matters. Slow, quiet, no hard sell.", []),
    ("humor", "Humor", "hum_object_pov", "POV: the item",
     "Dry Shenandoah humor from the object's point of view. Never at a customer's expense.", []),
    ("humor", "Humor", "hum_overheard", "Overheard at the counter",
     "A gentle, anonymized, affectionate counter moment. Punch at objects, never people.", []),
]

UNTRIED_TERRITORY = [
    "behind-the-counter appraisal explainers",
    "restoration before/afters",
    "counter POV time-lapses",
    "employee picks with the employee's actual reasoning",
    "storm-prep checklists",
    "then-and-now local photos",
    "the story of one object",
    "who made this? maker-mark close-ups",
]


def cmd_init(engine: DriftEngine) -> int:
    if engine.state["formats"]:
        print(f"Registry already has {len(engine.state['formats'])} formats — not reseeding.")
        return 0
    for lane, pillar, fid, title, template, seasons in SEED_FORMATS:
        engine.state["formats"].append(Format(
            id=fid, lane=lane, pillar=pillar, title=title, template=template,
            seasons=seasons, hook_key=fid, created=date.today().isoformat()))
    engine.state["untried_territory"] = UNTRIED_TERRITORY
    engine.save()
    print(f"Seeded {len(engine.state['formats'])} formats, "
          f"{len(UNTRIED_TERRITORY)} untried territories.")
    return 0


def cmd_status(engine: DriftEngine) -> int:
    s = season_for(date.today())
    print(f"Season: {s['season']}  |  palette: {s['palette']}")
    print(f"Hooks:  {s['hooks']}")
    print(f"Measured posts: {engine.measured_posts()}   "
          f"Exploration budget: {engine.explore_share():.0%}   "
          f"(signal threshold {MIN_POSTS_FOR_SIGNAL} posts/format)")
    by = {}
    for f in engine.state["formats"]:
        by.setdefault(f.status, []).append(f)
    for status in ("active", "candidate", "resting", "retired"):
        fs = by.get(status, [])
        if fs:
            print(f"\n{status.upper()} ({len(fs)})")
            for f in fs:
                sig = f"idx {f.index:.2f}" if f.confident else f"n={f.posts} (below signal)"
                print(f"  {f.id:<24} {f.lane:<11} {sig}")
    return 0


def cmd_select(engine: DriftEngine, lane: str, slots: int, account: str) -> int:
    picks = engine.select(lane, slots, account)
    s = season_for(date.today())
    print(f"[{s['season']}] lane={lane} account={account} "
          f"explore={engine.explore_share():.0%}")
    if not picks:
        print("  no eligible formats (all on cooldown or out of season)")
        return 1
    if len(picks) < slots:
        # Under-fill is a real signal, not a silent shortfall: the registry has
        # run dry for this lane/season. Surfacing it is what triggers the
        # quarterly invention step to top the registry back up.
        print(f"  ⚠ UNDER-FILL: {len(picks)}/{slots} — registry is thin for "
              f"lane={lane} in season={s['season']}. Run `refresh` to queue new candidates.")
    for f in picks:
        tag = "NEW" if f.posts == 0 else f"n={f.posts}"
        print(f"  {tag:<6} {f.id:<24} {f.title}")
        print(f"         {f.template}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Valley Pawn creative drift engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("refresh")
    sel = sub.add_parser("select")
    sel.add_argument("--lane", required=True)
    sel.add_argument("--slots", type=int, default=4)
    sel.add_argument("--account", default="Brand")
    rec = sub.add_parser("record")
    rec.add_argument("--format-id", required=True)
    rec.add_argument("--account", required=True)
    rec.add_argument("--engagement", type=float, required=True)
    rec.add_argument("--reach", type=float, default=0.0)

    a = ap.parse_args()
    engine = DriftEngine()

    if a.cmd == "init":
        return cmd_init(engine)
    if a.cmd == "status":
        return cmd_status(engine)
    if a.cmd == "select":
        return cmd_select(engine, a.lane, a.slots, a.account)
    if a.cmd == "record":
        engine.record(a.format_id, a.account, a.engagement, a.reach)
        engine.save()
        print(f"recorded {a.format_id} / {a.account}: eng={a.engagement} reach={a.reach}")
        return 0
    if a.cmd == "refresh":
        rep = engine.refresh()
        engine.save()
        print(json.dumps(rep, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
