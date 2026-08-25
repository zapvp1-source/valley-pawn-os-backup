import shutil
p='/Users/joshuadavis/Documents/Claude/Scheduled/vp-ai-search-health-check/SKILL.md'
shutil.copy(p, p+'.bak-20260823-nap')
s=open(p).read()
old='  • Harrisonburg — 1790 East Market Street, Ste 22, Harrisonburg, VA 22801'
new='  • Harrisonburg — 1790 East Market Street, Harrisonburg, VA 22801'
n=s.count(old); s=s.replace(old,new)
anchor='  • Roanoke — 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 — (540) 562-0776 — closed Wed & Sun'
note = anchor + """

> \U0001F4CC **CANONICAL NAP CORRECTIONS (2026-08-23, confirmed by Joshua — do not revert):**
> 1. **Harrisonburg has NO suite number.** It is "1790 East Market Street" — full stop. The old
>    "Ste 22" that used to be in this file was WRONG, and was removed from our own website schema
>    and footer template on 2026-08-23. If "Ste 22" appears on ANY listing, that is a DEFECT to
>    correct — never treat it as canonical.
> 2. **Roanoke occupies BOTH Suite C and Suite D.** Customer-facing canonical stays "Suite C".
>    The ATF FFL record reads "2362-D" — that is **CORRECT, not drift.** Never "fix" 2362-D and
>    never flag it as an error. Where the full footprint is stated, "Suite C & D" is correct."""
m=s.count(anchor); s=s.replace(anchor,note,1)
open(p,'w').write(s)
print('ste22_replaced',n,'anchor_found',m)
