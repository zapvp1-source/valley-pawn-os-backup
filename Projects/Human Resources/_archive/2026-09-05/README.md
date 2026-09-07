# Archived 2026-09-05 — HR Phase 0 folder hygiene

Superseded working files moved out of the Human Resources root so the current
governing documents are unambiguous. Nothing deleted; everything here is intact.

| File | Why archived | Superseded by |
|---|---|---|
| Employee_Handbook_v2026.1_DRAFT.docx | superseded draft | Employee_Handbook_v2026.2_FINAL.docx |
| Valley_Pawn_PP_Manual_v2026.1_DRAFT.docx | superseded draft | Valley_Pawn_PP_Manual_v2026.3_FINAL.docx |
| Valley_Pawn_PP_Manual_v2026.2_FINAL.docx | superseded version (its title page also still read "Version 2026.1 — DRAFT") | Valley_Pawn_PP_Manual_v2026.3_FINAL.docx |
| Valley_Pawn_Sales_Loan_Associate_Postings_HAR_WAY.docx | pre-pay-transparency posting with no wage range — NOT compliant with Va. pay-transparency requirements; kept only as a record | ..._v2_PAYTRANSPARENCY.docx |
| _build_scrap_naming_policy.py | stale generator; produced a 7-section formal policy that no longer matches the shipped one-page standard | Gold_Scrap_Bucket_Naming_Standard_2026-08.docx |
| hiring_campaign_create.log / hiring_preflight.log / hiring_v2.log | one-shot 2026-07-23 Brevo campaign logs | — |
| _upload_tmp/ | byte-identical duplicates (md5 verified 2026-09-05) of Jewelry_Display_OneInOneOut_Policy.pdf and ROC_Martin_Dowden_Waynesboro_2026-07-25.pdf, left over from a Gusto upload staging step | the copies in the HR root |

`Ask_Handbook/build_sources.py` globs the HR root only (non-recursive), so archiving these
does not change what #ask-handbook serves — it removes the risk of a superseded FINAL being
picked up if version parsing ever changes.
