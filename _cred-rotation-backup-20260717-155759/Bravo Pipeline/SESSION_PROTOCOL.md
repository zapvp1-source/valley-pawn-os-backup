# Bravo Session Protocol

**MANDATORY first step for any Bravo-touching task. No exceptions.**

## Why this exists

Joshua has built a complete Bravo extraction pipeline that feeds CSVs to dozens of consumer tasks. The failure mode this protocol prevents is Claude re-discovering the pipeline on every session and proposing plans that ignore existing CSVs and handlers — which is what makes Joshua feel like he is fighting for Bravo interaction.

Joshua, 2026-05-26: *"I shouldn't have to hold you to the correct behavior. You're useless at that point. How do we make it rock solid?"*

This protocol IS the rock-solid answer. Skipping it is not an option — it is a contract violation visible in this file and reinforced by:

- Project root `CLAUDE.md` (auto-loads when this folder is mounted)
- The `bravo-pipeline-preflight-mandatory` feedback memory (loads via `MEMORY.md` every session)
- The `bravo-context` skill (instructs the same preflight)

If you find yourself answering a Bravo question without having run the preflight, **stop and run it now.**

---

## The protocol

### Step 1 — Preflight (always, first tool call)

```bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bin/bravo-preflight.sh"
```

Output: fresh CSVs (last 7d), stale CSVs (>30d), total CSV count, registry path, registry age.

### Step 2 — Read registry (always, second tool call)

```bash
cat "/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/bravo-pipeline-registry.md"
```

Find the cell that matches the request. Note its status (✅ / ⚠️ / ❌ / 🔨 / ❓).

### Step 3 — Decide the path

| Registry status | What to do |
|---|---|
| ✅ + fresh CSV covers window | Use the existing CSV. Do not re-pull. |
| ✅ + CSV stale or wrong window | Trigger a re-pull via the existing pipeline cell. |
| ⚠️ (consumer disabled) | Trigger a one-shot pull, or propose re-enabling the task. |
| ❓ | Confirm with Joshua or by reading the dispatch tables before acting. |
| 🔨 (gap) | Propose adding a new cell (additive-only — clone, never edit existing). |
| ❌ | Surface the breakage to Joshua first; do not paper over it. |

### Step 4 — Only THEN propose a plan

Lead with what already exists and what the gap is. Never lead with "I'll extract X from scratch" when the registry shows X exists.

---

## If the preflight cannot run

If the script path is not visible from the current Cowork session (parent `Projects/` not mounted), **stop**.

Do not guess. Do not improvise from memory. Tell Joshua exactly: *"I cannot run the Bravo preflight — the parent `Projects/` folder is not mounted in this session. Mount it, or paste the registry inline."*

Fallback reference: the `bravo-pipeline-registry-location` memory entry holds the canonical paths.

---

## When to update the registry

- After verifying any ❓ row → fill in the actual handler / CSV pattern / channel and bump "Last verified" to today's date.
- After a pipeline cell changes state (new consumer enabled, handler fixed, broken cell repaired) → update its status.
- After adding a new pipeline cell → add a new row in the appropriate OUT or IN table.
- After retiring a cell → mark it ❌ with a retirement date, do NOT delete the row (audit history).

Update the "Last full audit" line at the top whenever a comprehensive walk-through happens.
