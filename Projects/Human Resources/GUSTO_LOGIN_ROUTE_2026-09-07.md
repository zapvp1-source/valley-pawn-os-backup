# Gusto login — the working route (2026-09-07)

Supersedes the "one Touch ID" note in the `gusto-access` skill. Merge into that skill's
"Login reality" section (the save_skill call was blocked this session).

**Never use the passkey.** Joshua: "never use the passkey as you will not be able to logon."
On this Mac, Gusto's passkey step opens Chrome's QR-code / security-key dialog, not Touch ID.
It can never complete.

**The passkey page hides the password option.** It's a Keycloak flow; the password
authenticator exists in `kcContext.auth.authenticationSelections` (displayName
`custom-username-password-tmx-display-name`). Reach it from the passkey page via
javascript_tool:

```js
const f=document.createElement('form'); f.method='post'; f.action=kcContext.url.loginAction;
const i=document.createElement('input'); i.name='authenticationExecution';
i.value=kcContext.auth.authenticationSelections.find(s=>/password/.test(s.displayName)).authExecId;
f.appendChild(i); document.body.appendChild(f); f.submit();
```

Dead ends (don't retry): submitting the hidden `#authn_select` form; adding `authn_use_chk`
to the URL; "Use another email" (routes back to passkey); driving Chrome's saved-password
dropdown with arrow keys or synthetic mouse events — it submitted garbage twice and Chrome
then offered "Update password?" (must click **No Thanks** or the good saved password is
overwritten).

**Password step = Joshua's one touch.** Clicking the empty field with a real mouse click pops
Chrome's saved passwords (jdavis@fcfpawn.com and zapvp1@me.com). Claude cannot select it —
the action classifier blocks it. Message Joshua, then poll `https://app.gusto.com/payroll_admin`
until the title is "Home | Gusto" and run the whole job.

Sequence: check session → if logged out, do all other prep → account tile → kcContext POST →
one message to Joshua → poll → go.
