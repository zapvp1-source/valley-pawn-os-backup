# adjustments_log.jsonl — VOID ENTRIES NOTICE

**Written 2026-08-22. Read this before treating any row in `adjustments_log.jsonl` as signal.**

## Six of the eight rows are artifacts, not content decisions

`publer_weekly_digest.py` classified a post as theme `warranty` on the regex
`warranty|what'?s right is right`.

**"What's Right Is Right" is the Valley Pawn brand tagline** and sits in the footer of
nearly every post. "30-day warranty" is likewise a stock adjunct line on product posts.
So the classifier labelled **103 of 246 text-carrying posts** `warranty` when only
about **8** are actually *about* the warranty.

The following rows are therefore VOID — they record the regex matching boilerplate, not
any real performance signal:

| week_ending | row | status |
|---|---|---|
| 2026-07-12 | `+5% warranty next batch` | **VOID — artifact** |
| 2026-07-27 | `+5% warranty next batch` | **VOID — artifact** |
| 2026-07-31 | `+5% warranty next batch` | **VOID — artifact** |
| 2026-08-07 | `+5% warranty next batch` | **VOID — artifact** |
| 2026-08-14 | `+5% warranty next batch` | **VOID — artifact** |
| 2026-08-21 | `+5% warranty next batch` | **VOID — artifact** |

The 2026-08-07, 08-14 and 08-21 rows are self-refuting on their face — they record
`top: warranty` **and** `bottom: warranty` simultaneously, then still emit
`+5% warranty`. A theme cannot be both the best and worst performer and still warrant
more of it. That is the signature of a category that is really just "every post."

Only two rows survive: `2026-07-12 hold current mix` and `2026-07-17 +5% community`.
Note that the `community` row is *also* suspect — see below.

## Do not act on these rows

The Friday adjust loop has been steering the content mix toward a category that does not
meaningfully exist for **eight consecutive weeks**. No batch should carry forward a
`+5% warranty` bias. Reset to the registry's baseline mix.

## What was fixed (2026-08-22)

`publer_weekly_digest.py` — backup at `publer_weekly_digest.py.bak-pre-fix-20260822`:

1. **Boilerplate is now stripped before classification** (`strip_boilerplate()`), so the
   tagline, the 30-day-warranty adjunct, "family-owned", "since 20xx", "five stores",
   "Shenandoah Valley", store addresses and the brand name itself can never vote.
2. **`warranty` now requires the post to be *about* the warranty** — the word must
   survive boilerplate-stripping, or appear alongside explicit subject phrasing
   ("if it doesn't work, bring it back", "we stand behind what we sell", "no fine print").
3. **Other collisions found and fixed in the same pass:**
   - `heritage` matched the footer's "since 2014" / "five stores" / "Shenandoah" —
     **every single old `heritage` hit was an artifact** (5 → 1).
   - `community` matched `walker street` and `davis street`, which are **Valley Pawn's
     own store addresses** — so every Lexington post carrying its address was labelled
     `community` (24 → 10). *This is why the 2026-07-17 `+5% community` row is also
     unreliable.* This collision was not in the original bug report; it was found by
     re-running the classifier against the corpus.
   - `value` matched `\$\d{2,}`, i.e. any price, i.e. every product post (12 → 19 after
     switching to explicit price-comparison phrasing).
   - `team` matched bare `meet ` and `our team` in product copy (0 → 4).
   - `mobile-app` matched any use of the word "app".
4. **`MIN_POSTS_FOR_SIGNAL` is now per-account, not corpus-wide.** The 8/21 digest steered
   on n=8. An account must publish at least 10 posts in the window before it may influence
   the mix, and a winning theme needs at least 3 posts behind it. Thin accounts are still
   reported — they just don't get a vote. When no account clears the bar the digest emits
   `hold current mix — insufficient signal` instead of inventing a steer.
5. Rows written from now on carry `classifier_version: "2026-08-22-boilerplate-fix"`,
   plus `signal_posts` and `signal_accounts`. **Any row without a `classifier_version`
   field predates this fix and should be treated as suspect.**

## Standing rule

`MIN_POSTS_FOR_SIGNAL` does not protect against a mislabelled category — a bad regex
clears any volume threshold easily. **Re-read the classifier patterns before trusting
digest output**, and check them against sitewide boilerplate specifically. This is now a
required step in the quarterly creative refresh.
