# SKILL DELTA — 2026-06-29

**For Joshua to apply in Settings → Capabilities.** Skill files are a read-only cache inside a
Cowork session, so I cannot edit them from here. These are the additive edits that keep the two
"first-read" skills pointing at the now-current capability picture. Everything is additive — nothing
below removes existing content.

Source of truth for all of this is now **BUSINESS_OS.md → Section 13** (added this session). These
skill edits just make sessions *find* it.

---

## 1. `enterprise-map` skill — 2 small additive edits

**a) Point the connector list at BUSINESS_OS Section 13 + add MCP-first.**
In the "### MCP connectors" block, append:

> **MCP-first (Rule 0):** prefer a native MCP connector over Chrome/computer-use/osascript. Full
> authorized inventory + installed plugin marketplaces + live-truth queries now live in
> **BUSINESS_OS.md → Section 13 (Tooling, Connectors & Capability Inventory)**. Read that for the
> current "what do I already have access to" answer instead of trusting this snapshot.

**b) Add a load-protocol step.**
In "## The Load Protocol", add a half-step after step 1:

> **1b. Read BUSINESS_OS.md → Section 13** to load the current tool/connector/plugin inventory and
> the MCP-first order before choosing how to reach a system.

---

## 2. `valley-pawn-context` skill — 1 additive edit

Add to the rules/reference area:

> **MCP-first (Rule 0):** Always use a native MCP connector before Chrome or computer-use. The
> authorized connector + plugin inventory lives in BUSINESS_OS.md → Section 13. Installed plugin
> marketplaces that extend what Claude can do for Valley Pawn include: small-business, finance,
> marketing, legal, operations, productivity, customer-support (plus the core anthropic-skills VP
> bundle). When a task could use one, reach for it rather than building from scratch.

*(Note: the still-pending `VALLEY_PAWN_CONTEXT_DELTA_2026-06-22.md` — Harrisonburg "Ste 22" NAP fix —
is separate and also waiting to be applied in Settings. Apply both in one pass.)*

---

## 3. Optional but recommended

Add **BUSINESS_OS.md → Section 13** as a referenced read inside `valley-pawn-context` so the
capability inventory is effectively auto-loaded every session (this is the "Future" note already in
BUSINESS_OS Section 12).

---

**How to apply:** Settings → Capabilities → edit each skill → paste the additive blocks above →
save. Then delete this file (or leave it; it's harmless).
