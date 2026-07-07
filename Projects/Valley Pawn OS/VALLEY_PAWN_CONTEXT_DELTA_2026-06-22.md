# valley-pawn-context — Delta Patch 2026-06-22

This is a small additive patch to apply to the canonical `valley-pawn-context` skill via **Settings → Capabilities → Skills → valley-pawn-context → Edit**.

The audit done 2026-06-22 surfaced that Harrisonburg actually occupies **Suite 22** at 1790 East Market Street. Both Google Business Profile and the WordPress JSON-LD already reflect this; the canonical NAP in this skill did not. Joshua confirmed in chat 2026-06-22: Harrisonburg = Ste 22.

## Change required — Harrisonburg address line

**FIND** (Locations section, store #3):

```
### 3. Harrisonburg
- **Address:** 1790 East Market Street, Harrisonburg, VA 22801
- **Phone:** (540) 574-4500
```

**REPLACE WITH**:

```
### 3. Harrisonburg
- **Address:** 1790 East Market Street, Ste 22, Harrisonburg, VA 22801
- **Phone:** (540) 574-4500
```

## Also update the "Stale variants seen in the wild" section

**APPEND** under Harrisonburg's known-good address note (or add it to the existing "Stale variants" list near the Roanoke Suite C bullet):

```
- Harrisonburg: address WITHOUT "Ste 22" is **stale** — canonical includes Ste 22.
  Verified 2026-06-22 via Google Knowledge Panel + WordPress JSON-LD; Joshua confirmed.
```

That's it — two small additive edits. No deletions, no rule changes, no behavioral changes. Just the suite number correction.

---

## Why we're not editing the skill file directly

Skill files live in a read-only cache at `/var/folders/.../skills/valley-pawn-context/SKILL.md`. Edits there don't change the user's installed skill. Joshua needs to apply this in Settings → Capabilities.

After Joshua applies the change, the next session that reads valley-pawn-context will have the correct Harrisonburg address. Until then, this delta document is the authoritative reference.
