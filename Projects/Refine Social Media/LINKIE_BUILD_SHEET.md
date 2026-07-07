# Linkie Build Sheet — Copy-Paste Setup (10 min total)

## You're already in `linkie.bio/valley_pawn` (the BRAND master). Fill this in, then duplicate 5x for stores.

### 1️⃣ Brand Master Linkie (`linkie.bio/valley_pawn`)

| Field | Value |
|---|---|
| **Name** | Valley Pawn *(already set)* |
| **Title** | Family-Owned Pawn Since 2014 |
| **Bio** | 5 Virginia locations · Gold buying · Fair loans · 30-day warranty on everything we sell |
| **Accent Color** | `#C7301F` (Valley Pawn red, change from default `#0071D0`) |
| **Appearance** | Light |
| **Columns** | 2 |
| **Social Icons** | Hide *(we're listing platforms as buttons instead)* |

**Click "Collect Emails" — set the form to:**
- Title: **Win $100 every month**
- Subtitle: *Drop your email — that's your entry. New winner every month, no purchase necessary. [Rules](follow.thevalleypawn.com/rules)*
- Button text: **Enter to Win**

**Add Buttons (in this order — click "Add Button" or "+" to add each):**

| Order | Label | URL |
|---|---|---|
| 1 | 📘 Follow on Facebook | `https://www.facebook.com/profile.php?id=1603970336542485` |
| 2 | 🎥 Watch on YouTube (Coming Soon) | `https://www.youtube.com/@valleypawnva` *(placeholder — update when channel exists)* |
| 3 | 𝕏 Follow on X | `https://x.com/valleypawnva` |
| 4 | 📸 Follow on Instagram | `https://www.instagram.com/valley_pawn` |
| 5 | 🎵 Follow on TikTok | `https://www.tiktok.com/@thevalleypawn` |
| 6 | 🛍️ Visit Our Store | `https://thevalleypawn.com` |
| 7 | 📖 Read Our Blog | `https://thevalleypawn.com/blog` |

**Click Save (top right).**

---

### 2️⃣ Five Store Linkies (duplicate the master)

In Linkie's top-left dropdown (the `linkie.bio/valley_pawn ▼` selector), click **"+ New Profile"** or **"Duplicate"** five times.

For each duplicate, set the **slug** (URL part) and **only swap button #1 (Facebook)**:

| Linkie slug | Button #1 Label | Button #1 URL |
|---|---|---|
| `valleypawn_lexington` | 📘 Lexington on Facebook | `https://www.facebook.com/profile.php?id=379605279045904` |
| `valleypawn_roanoke` | 📘 Roanoke on Facebook | `https://www.facebook.com/profile.php?id=188243497698836` |
| `valleypawn_harrisonburg` | 📘 Harrisonburg on Facebook | `https://www.facebook.com/profile.php?id=474248069342834` |
| `valleypawn_waynesboro` | 📘 Waynesboro on Facebook | `https://www.facebook.com/profile.php?id=303444680270846` |
| `valleypawn_culpeper` | 📘 Culpeper on Facebook | `https://www.facebook.com/profile.php?id=100478091680300` |

**Everything else (buttons 2-7, accent color, bio, email collection) stays identical across all 6 Linkies.**

Save each.

---

### 3️⃣ Reply "linkies done" when finished

Then I will:
- Generate 6 store-specific counter card PDFs (master + 5 stores) using these final URLs
- Set up DNS routing for `follow.thevalleypawn.com/{store}`
- Verify Sunday 8 PM `vp-content-batch` cron fires hands-off
- Build the monthly giveaway draw automation skeleton

**Total your time: ~10 minutes of copy-paste.** Mine: everything else.

---

## Why we're doing it this way

Linkie's visual editor doesn't expose a public API for profile setup. Driving it via Chrome MCP pixel-clicks is unreliable and slower than you doing the copy-paste manually. The board's call is "hands-off where automatable, pragmatic where not" — this UI form-fill is the "pragmatic" half. Once the 6 Linkies are built and saved, everything downstream (QR codes, DNS, scheduled tasks) is fully automated.
