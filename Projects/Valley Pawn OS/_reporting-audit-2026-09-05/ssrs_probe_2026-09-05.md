# SSRS headless probe — 2026-09-05 (read-only)
- `GET /ReportServer/logon.aspx` → 200, form fields TxtUser (prefilled service user), TxtPwd (empty), BtnLogon "Click to Continue", ASP.NET viewstate.
- `POST` same form (no password) → 302 `/ReportServer/default.aspx` = authenticated.
- Authenticated render of `BRAVO Company Performance` with `rs:Format=CSV` and no `r=` → rsReportParameterValueNotSet ("requires a value for parameter 'r'").
- With any historical `r=` GUID (43058c4d…, 6c6ae90a…) → rsErrorExecutingCommand (token expired/invalid).
- Unauthenticated render → 302 to logon (so auth is enforced; the `r` token is the tenant/request scoping gate, minted only by the Bravo client via WCF).
Conclusion: headless auth works; pure headless export blocked by `r`. Keep the hybrid CompanyKpis path; pursue Bravo scheduled emails / Reporting Pro instead.
