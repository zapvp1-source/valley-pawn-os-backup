## 2026-08-22 (eBay secrets migrated + INCIDENT: accidental live title changes, contained)

- **DONE — eBay secrets moved out of plaintext.** `~/ebay_weekly_rankings.py` (mode 701,
  world-executable) hardcoded the Slack webhook, `APP_ID`/`DEV_ID`/`CERT_ID` and all 5 store OAuth
  tokens, and ~30 other scripts `exec()` it to get `STORES`. Values moved to
  `~/.vp_secrets/ebay_store_tokens.py` (mode 600); the source now imports them and still defines
  `SLACK_WEBHOOK / APP_ID / DEV_ID / CERT_ID / STORES` at module level, so **every consumer and all
  4 launchd agents keep working unchanged**. Verified: interface intact, 5 stores resolve, 0
  residual secret literals, source re-permed to 700. Backup at
  `~/ebay_weekly_rankings.py.bak-2026-08-22`. Done by `audit_2026-08-22/secure_creds.py`.
- **INCIDENT (my fault, contained — full writeup in `eBay/audit_2026-08-22/INCIDENT_2026-08-22.md`).**
  A follow-on sweep to clear the same literals from the other ~18 `~/ebay_*.py` scripts verified
  each rewrite by `exec()`ing the file. Those scripts are operational, not importable — they do
  their work at module level with no `__main__` guard. The verification therefore ran a live
  quality-fix pass: **17 eBay titles were changed for real** (11 on already-Completed listings, 6
  on Active), 2 category changes and 2 photo/title fixes failed harmlessly ("Auction ended").
  - Killed on detection. All 18 rewritten scripts restored from `.bak-2026-08-22` and
    **compile-checked, not exec'd** (`incident_restore.py`). The 4 launchd-critical scripts verified
    compiling with credentials resolving.
  - All 17 changed titles re-read live via `GetItem` and checked for factual accuracy. **One real
    defect found and corrected:** Waynesboro `800321499390` ($649.94) had been retitled "Camera
    **Body**" while its own specifics carry MPN `ILCZV-E10L/W` — Sony's **lens-kit** SKU. Retitled to
    `Sony ZV-E10 Mirrorless Vlogging Camera ILCZV-E10L/W White w/ Extras - Used`, applied and
    verified live, reversible via `~/ebay_incident_fix_state.json`.
  - The other 16 were left in place: same class of enrichment `ebay-weekly-quality-fix` applies
    every Monday, no further factual conflicts found on spot-check, and all remain revertible from
    `~/ebay_weekly_qualityfix_state.json` (`title_before` preserved).
- **NEW HARD RULE:** never `exec()` or import a `~/ebay_*.py` (or any operational) script to verify
  a syntax-only edit — use `py_compile`/AST. Running one of those files *is* a production change.
- **Also observed:** a detached process `/tmp/vp_ebay_fix.py --apply` (PPID 1, started 23:48:54)
  was already applying this audit's A/B/C remediation — Roanoke 14→30-day returns, no-returns→30-day,
  Best Offer ON for Culpeper (auto-accept 90% / auto-decline 75%) — state at
  `~/vp_ebay_fix_state.json`, 248 entries and climbing (A=13 B=42 C=193). Not started by this
  session. This session's duplicate (`eBay/ebay_policy_fix.py`) was killed rather than run
  concurrently against the same listings. **That process's output still needs verifying.**
