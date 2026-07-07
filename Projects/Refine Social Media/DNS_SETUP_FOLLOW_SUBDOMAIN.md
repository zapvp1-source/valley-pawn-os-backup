# DNS Setup — follow.thevalleypawn.com → Linkie

## What we're doing
Pointing `follow.thevalleypawn.com` at the Linkie page so the printed QR cards lead to a branded URL instead of `linkie.bio/...`.

## Where to do it
Your DNS lives at whoever hosts `thevalleypawn.com`. Most likely WordPress.com (since the site is hosted there) — they manage DNS through their dashboard at `wordpress.com/domains/manage/thevalleypawn.com/dns`.

If you registered the domain elsewhere (GoDaddy, Namecheap, Google Domains/Squarespace), DNS is at that registrar. Check `wordpress.com` → My Sites → Domains first.

## The CNAME record to add

| Type | Host/Name | Value/Target | TTL |
|---|---|---|---|
| `CNAME` | `follow` | `app.linkie.bio` | 3600 (1 hour) |

That's the **single record needed**.

## How path-based routing works (for the 5 stores)

Once `follow.thevalleypawn.com` points to `app.linkie.bio`, Linkie will accept these URLs **automatically** because each path is a distinct Linkie slug:

| Card destination URL | Resolves to |
|---|---|
| `follow.thevalleypawn.com` | `linkie.bio/valley_pawn` (BRAND master) |
| `follow.thevalleypawn.com/lexington` | `linkie.bio/valleypawn_lexington` |
| `follow.thevalleypawn.com/roanoke` | `linkie.bio/valleypawn_roanoke` |
| `follow.thevalleypawn.com/harrisonburg` | `linkie.bio/valleypawn_harrisonburg` |
| `follow.thevalleypawn.com/waynesboro` | `linkie.bio/valleypawn_waynesboro` |
| `follow.thevalleypawn.com/culpeper` | `linkie.bio/valleypawn_culpeper` |

**Wait — caveat:** Linkie may NOT automatically route subpaths to specific slugs without custom configuration on their side. Path routing varies by host.

**Two paths if Linkie doesn't auto-route:**

**Path 1 (preferred — Linkie supports custom domain natively):**
- In Linkie dashboard → Settings → Custom Domain → add `follow.thevalleypawn.com`
- Linkie's own router maps `/lexington` → `linkie.bio/valleypawn_lexington` automatically (this is how multi-page Linktree/Linkie products usually work)

**Path 2 (fallback — separate subdomains per store, only if Path 1 doesn't work):**
- Add 5 more CNAME records: `lexington.thevalleypawn.com`, `roanoke.thevalleypawn.com`, etc., each → `app.linkie.bio`
- Update each store's Linkie custom domain setting to its own subdomain
- Counter cards point to `lexington.thevalleypawn.com` instead of `follow.thevalleypawn.com/lexington`
- Less clean, more DNS records

**My recommendation:** start with Path 1 (single `follow` CNAME). Verify after the 6 Linkies are built. If routing doesn't work, fall back to Path 2.

## After the CNAME is added

DNS propagation: usually 5-30 min on WordPress.com. You can check by running:
```
dig follow.thevalleypawn.com CNAME
```
or visiting `follow.thevalleypawn.com` in a browser — should land on the brand Linkie.

## What I need from you for this step

**Reply "dns done"** once you've added the CNAME record. I'll verify propagation via `dig` and confirm the URL works.

If you tell me which DNS host (WordPress.com vs. registrar), I can give exact click-by-click steps. I can also drive Chrome through WordPress.com's DNS editor if you grant me access there — but for one CNAME record, the manual path is faster.
