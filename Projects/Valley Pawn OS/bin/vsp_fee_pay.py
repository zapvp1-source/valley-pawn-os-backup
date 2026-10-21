#!/usr/bin/env python3
"""vsp_fee_pay.py — native monthly VSP gun-check (NICS) fee payment for all 5 Valley Pawn stores (2026-10-20).

Flow mapped live 2026-10-20 (Compliance/vsp/PORTAL_MAP.md):
  ebilling.vsp.virginia.gov (Oracle iReceivables, user X009686, password = Chrome-saved on the pw-vp profile)
    Customer Search → Go (#Icxgocontrol) → rows N25:Aricustdetail:{0,2,4,6,8} = ROA, WAY, HAR, CUL, LEX
    → Account (#ARIMENUACCTDETAILS) → Status Open/pending → FIRE-##### rows
    → tick row → MAKE PAYMENT (#Pay) → page embeds  open('https://vsppayments.virginiainteractive.org/Checkout?token=…')
  vsppayments.virginiainteractive.org/Checkout  (amount screen, #PaymentBtn Next)
  securecheckout.cdc.nicusa.com/Checkout/Payment (NIC): Payment Type select (CC | ACH) → Next
    → Customer Information (prefilled from VSP) → Payment Information: Name on Account, business checkbox,
      Routing, Account, Re-enter, Checking/Savings → Next → review → Submit Payment → receipt (also emailed).

MODES
  --read            log in, read every store's balance + open invoices, write Compliance/vsp/<YYYY-MM>.json. No payment pages.
  (default) stage   --read, then for each store with a balance open the NIC checkout, choose Electronic Check,
                    fill name/business, STOP before bank numbers. DM Joshua the list. (Tabs stay open in the
                    automation Chrome only while the script runs — staging is for a human to finish in his Chrome;
                    the Cowork task does that. Native default is therefore --read + DM unless --pay.)
  --pay             full unattended payment by Electronic Check. Bank details come ONLY from the macOS Keychain
                    (services vp-vsp-ach-routing / vp-vsp-ach-account / vp-vsp-ach-name), which Joshua stores himself:
                      security add-generic-password -U -s vp-vsp-ach-routing -a "$USER" -w '<routing>'
                      security add-generic-password -U -s vp-vsp-ach-account -a "$USER" -w '<account>'
                      security add-generic-password -U -s vp-vsp-ach-name    -a "$USER" -w 'Full Circle Finance Inc'
                    Nothing here ever logs or prints those values.
  --dry-run         with --pay: do everything except the final Submit Payment click (proves the fill).
  --no-dm           no Slack.

GUARD RAILS (controller rules, 2026-10-20 expert board) — any breach => that store is NOT paid, it is reported:
  * only transaction type Invoice, number FIRE-*, invoice date in the current month, status Open
  * per-store amount <= MAX_STORE (300) and run total <= MAX_TOTAL (900)
  * no Overdue balance, no second open invoice, no penalty/interest line
  * a Payment row dated this month already on the account => already paid, skip
  * "Change Password" page or any login failure => stop, ONE DM to Joshua, ledger row. Never retries the login
    (the account locks after 5 failures), never touches Login Assistance.
Receipts: Compliance/vsp/<YYYY-MM>/<STORE>-receipt.html + .png; month file updated with confirmation numbers.
"""
import datetime as dt
import getpass
import json
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
sys.path.insert(0, BIN)
COMP = os.path.expanduser("~/Documents/Claude/Projects/Compliance")
OUT = os.path.join(COMP, "vsp")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
ET = ZoneInfo("America/New_York")
AGENT = "vsp-fee-pay"
PORTAL = "https://ebilling.vsp.virginia.gov"
# Bill Management > Customer Search function (the page the eyeglasses links live on); reached directly because the
# portal Home page (where a saved session lands) has no Customer Search link.
CS_URL = PORTAL + "/OA_HTML/RF.jsp?function_id=10928&resp_id=51394&resp_appl_id=222&security_group_id=0&lang_code=US"
STORES = [("ROA", 0, "15848"), ("WAY", 2, "16284"), ("HAR", 4, "16627"), ("CUL", 6, "280758"), ("LEX", 8, "283759")]
MAX_STORE, MAX_TOTAL = 300.0, 900.0
RECEIPT_EMAIL = "fullcirclepawn@gmail.com"


def log(*a):
    print(dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def ledger(sentence, human="no"):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, human))
    except OSError:
        pass


def dm(text):
    if "--no-dm" in sys.argv:
        log("DM (suppressed):", text)
        return
    subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "dm", text], timeout=60)


def keychain(svc):
    r = subprocess.run(["security", "find-generic-password", "-s", svc, "-a", getpass.getuser(), "-w"],
                       capture_output=True, text=True, timeout=10)
    v = r.stdout.strip()
    return v or None


def money(s):
    return float(re.sub(r"[^\d.\-]", "", s or "") or 0)


# ---------------------------------------------------------------- portal
def login(page):
    page.goto(PORTAL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    title = page.title()
    if "Logged In As" in page.inner_text("body"):
        return True  # saved session still valid (lands on Home or Customer Search)
    # login form: username prefilled or empty; password autofilled by Chrome. ONE attempt.
    btn = page.locator("button:has-text('Login'), button:has-text('Log In'), input[type=submit]").first
    if btn.count() == 0:
        raise RuntimeError("no login button on %s" % title)
    pw = page.locator("input[type=password]").first
    if pw.count() and not pw.input_value():
        time.sleep(3)  # give Chrome autofill a moment
    if pw.count() and not pw.input_value():
        raise RuntimeError("password not autofilled")
    btn.click()
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    time.sleep(3)
    t = page.title()
    if "Change Password" in t:
        raise RuntimeError("CHANGE_PASSWORD")
    if "Login failed" in page.inner_text("body"):
        raise RuntimeError("LOGIN_FAILED")
    if "Logged In As" not in page.inner_text("body"):
        raise RuntimeError("unexpected page after login: %s" % t)
    return True


def goto_search(page):
    page.goto(CS_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    if "Change Password" in page.title():
        raise RuntimeError("CHANGE_PASSWORD")
    if page.locator("#Icxgocontrol").count() == 0:
        raise RuntimeError("Customer Search page did not load (title %s)" % page.title())
    page.locator("#Icxgocontrol").click()
    time.sleep(3)


def open_store(page, row):
    goto_search(page)
    page.locator("#N25\\:Aricustdetail\\:%d" % row).click()
    page.wait_for_load_state("domcontentloaded")
    time.sleep(3)
    body = page.inner_text("body")
    hdr = re.search(r"Department of State Police-([^\n]+)", body)
    bal = re.search(r"Your Account Balance:\s*USD\s*([\d.,]+)", body)
    over = re.search(r"Overdue Receivables\s*([\d.,]+)", body)
    page.locator("#ARIMENUACCTDETAILS").click()
    page.wait_for_load_state("domcontentloaded")
    time.sleep(3)
    return (hdr.group(1).strip() if hdr else "?"), money(bal.group(1) if bal else "0"), money(over.group(1) if over else "0")


def account_rows(page, status):
    page.select_option("#Iraccountstatus", label=status)
    page.locator("#Iracctdtlgocontrol").click()
    time.sleep(4)
    rows = page.evaluate("""() => [...document.querySelectorAll('table tr')]
        .map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean))
        .filter(c => c.length >= 7 && /\\d{2}\\/\\d{2}\\/\\d{4}/.test(c[3]))""")
    out = []
    for c in rows:
        out.append({"number": c[0], "type": c[1], "status": c[2], "date": c[3], "due": c[4],
                    "amount": money(c[5]), "remaining": money(c[6])})
    return out


def checkout_url(page):
    html = page.content()
    m = re.search(r"open\('(https://vsppayments[^']+)'", html)
    return m.group(1) if m else None


# ---------------------------------------------------------------- NIC checkout
def nic_fill(ctx, url, store, amount, pay, dry):
    """Open the vendor checkout in a new page. Returns dict(status, confirmation, note)."""
    pg = ctx.new_page()
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    txt = pg.inner_text("body")
    m = re.search(r"(FIRE-\d+)\s+(\d+)\s+\$([\d.,]+)", txt)
    if not m or abs(money(m.group(3)) - amount) > 0.005:
        pg.close()
        return {"status": "mismatch", "note": "checkout amount did not match invoice"}
    pg.locator("#PaymentBtn").click()
    pg.wait_for_load_state("domcontentloaded")
    time.sleep(3)
    pg.select_option("select", value="ACH")
    time.sleep(1)
    pg.locator("button:has-text('Next'):visible").first.click()
    time.sleep(3)
    name_box = pg.get_by_label(re.compile("Name on Account"))
    for attempt in range(3):  # the bank form can be slow to appear (WAY 10/20); re-click Next once or twice
        try:
            name_box.wait_for(state="visible", timeout=45000)
            break
        except Exception:
            if attempt == 2:
                diag = os.path.join(OUT, dt.datetime.now(ET).strftime("%Y-%m"), "%s-stuck.png" % store)
                os.makedirs(os.path.dirname(diag), exist_ok=True)
                pg.screenshot(path=diag, full_page=True)
                raise
            nb = pg.locator("button:has-text('Next'):visible")
            if nb.count():
                nb.first.click()
            time.sleep(5)
    if not pay:
        pg.close()
        return {"status": "staged", "note": "Electronic Check selected; bank details not entered"}
    name, routing, acct = keychain("vp-vsp-ach-name"), keychain("vp-vsp-ach-routing"), keychain("vp-vsp-ach-account")
    if not (name and routing and acct):
        pg.close()
        return {"status": "no-bank-details", "note": "Keychain items vp-vsp-ach-* missing"}
    pg.get_by_label(re.compile("Name on Account")).fill(name)
    pg.get_by_label(re.compile("business account")).check()
    pg.get_by_label(re.compile("^Routing Number")).fill(routing)
    pg.get_by_label(re.compile("^Account Number")).fill(acct)
    pg.get_by_label(re.compile("Re-enter Account Number")).fill(acct)
    pg.get_by_label("Checking").check()
    time.sleep(1)
    pg.locator("button:has-text('Next'):visible").last.click()
    time.sleep(4)
    review = pg.inner_text("body")
    if "%.2f" % amount not in review:
        pg.close()
        return {"status": "review-mismatch", "note": "amount missing on review screen"}
    os.makedirs(os.path.join(OUT, dt.datetime.now(ET).strftime("%Y-%m")), exist_ok=True)
    shot = os.path.join(OUT, dt.datetime.now(ET).strftime("%Y-%m"), "%s-review.png" % store)
    pg.screenshot(path=shot, full_page=True)
    if dry:
        pg.close()
        return {"status": "dry-run", "note": "stopped before Submit Payment", "review_png": shot}
    if "authorize this transaction" not in review:
        pg.close()
        return {"status": "review-mismatch", "note": "authorization text missing on review screen"}
    auth = pg.locator("input[type=checkbox]:visible")
    if auth.count() != 1:
        pg.close()
        return {"status": "review-mismatch", "note": "expected one visible checkbox on review, found %d" % auth.count()}
    # "Yes, I authorize this transaction." is a styled checkbox: Playwright's check() on the input does not toggle it
    # (10/20 live run). Click the label text, then fall back to setting it in the page, and verify before Submit.
    try:
        pg.get_by_text(re.compile("I authorize this transaction")).first.click()
        time.sleep(1)
    except Exception:
        pass
    if not auth.first.is_checked():
        auth.first.evaluate("e => { e.checked = true; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }")
        time.sleep(1)
    if not auth.first.is_checked():
        pg.close()
        return {"status": "review-mismatch", "note": "could not tick the authorization box"}
    time.sleep(1)
    pg.locator("button:has-text('Submit Payment'):visible, input[value*='Submit']:visible").first.click()
    time.sleep(8)
    rtxt = pg.inner_text("body")
    conf = re.search(r"Transaction ID:\s*([0-9]{6,})", rtxt) or re.search(r"(?:Confirmation|Reference)\s*(?:Number|#|No\.?)?:?\s*([A-Z0-9-]{6,})", rtxt, re.I)
    paid_ok = "Thank you for your payment" in rtxt and ("%.2f" % amount) in rtxt
    rp = os.path.join(OUT, dt.datetime.now(ET).strftime("%Y-%m"), "%s-receipt" % store)
    open(rp + ".html", "w").write(pg.content())
    pg.screenshot(path=rp + ".png", full_page=True)
    pg.close()
    return {"status": "paid" if (conf and paid_ok) else "submitted-unconfirmed", "confirmation": conf.group(1) if conf else None,
            "receipt": rp + ".png"}


# ---------------------------------------------------------------- main
def main():
    read_only = "--read" in sys.argv
    pay = "--pay" in sys.argv
    dry = "--dry-run" in sys.argv
    now = dt.datetime.now(ET)
    ym = now.strftime("%Y-%m")
    os.makedirs(OUT, exist_ok=True)
    month_file = os.path.join(OUT, ym + ".json")
    result = {"run_at": now.isoformat(), "mode": "pay" if pay else ("read" if read_only else "stage"),
              "dry_run": dry, "stores": {}, "total_open": 0.0}
    import vp_browser
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx = vp_browser.launch(p)
        try:
            page = vp_browser.first_page(ctx)
            try:
                login(page)
            except RuntimeError as e:
                msg = str(e)
                if msg == "CHANGE_PASSWORD":
                    dm("The State Police billing site is asking for a new password before it will let anyone in. "
                       "Please open ebilling.vsp.virginia.gov in the automation Chrome (vp_signin_front.sh), set the new "
                       "password and let Chrome save it. I'll pick the gun-check fees up on the next run.")
                    ledger("VSP portal forced a password change; waiting on Joshua", "yes, set new VSP password")
                else:
                    dm("I couldn't get into the State Police billing site this month (one try only, so the account "
                       "doesn't lock). Please sign in once on the automation Chrome so the saved password is current.")
                    ledger("VSP login failed: %s" % msg, "yes, re-save VSP password")
                result["error"] = msg
                json.dump(result, open(month_file, "w"), indent=1)
                return 1
            for code, row, cust in STORES:
                name, bal, over = open_store(page, row)
                rows = account_rows(page, "Any Status")
                this_month = [r for r in rows if r["date"].endswith("/%d" % now.year) and r["date"].startswith("%02d/" % now.month)]
                inv = [r for r in this_month if r["type"] == "Invoice" and r["number"].startswith("FIRE") and r["status"] == "Open"]
                paid = [r for r in this_month if r["type"] == "Payment"]
                st = {"name": name, "customer": cust, "balance": bal, "overdue": over,
                      "open_invoices": inv, "payments_this_month": paid, "action": None}
                result["stores"][code] = st
                result["total_open"] += bal
                log(code, name, "balance", bal, "overdue", over, "open", [(i["number"], i["amount"]) for i in inv])
                st["action"] = "nothing-due" if bal == 0 else None
            # guard rails
            flags = []
            if result["total_open"] > MAX_TOTAL:
                flags.append("total %.2f over cap" % result["total_open"])
            for code, st in result["stores"].items():
                st["hold"] = None
                if st["balance"] == 0:
                    continue
                if st["overdue"] > 0:
                    st["hold"] = "overdue %.2f" % st["overdue"]
                elif len(st["open_invoices"]) != 1:
                    st["hold"] = "%d open invoices" % len(st["open_invoices"])
                elif abs(st["open_invoices"][0]["remaining"] - st["balance"]) > 0.005 or st["balance"] > MAX_STORE:
                    st["hold"] = "balance %.2f does not match its one invoice / over cap" % st["balance"]
                elif st["payments_this_month"]:
                    st["hold"] = "already shows a payment this month (posting lag?)"
                if st["hold"]:
                    flags.append("%s: %s" % (code, st["hold"]))
            result["flags"] = flags
            payable = [c for c, st in result["stores"].items() if st["balance"] and not st["hold"]]
            if read_only or result["total_open"] > MAX_TOTAL or not payable:
                json.dump(result, open(month_file, "w"), indent=1)
                if flags and not read_only:
                    dm("VSP gun-check fees for %s need a look before paying: %s. Nothing was paid." % (now.strftime("%B"), "; ".join(flags)))
                    ledger("VSP run held: " + "; ".join(flags), "yes, review VSP invoices")
                if read_only:
                    due = [(c, s["balance"]) for c, s in result["stores"].items() if s["balance"]]
                    dm("VSP gun-check fees for %s: %s — total $%.2f." % (now.strftime("%B"),
                       ", ".join("%s $%.2f" % d for d in due) or "nothing owed", result["total_open"]))
                return 0
            # pay / stage, one store at a time
            for code, row, cust in STORES:
                st = result["stores"][code]
                if st["balance"] == 0 or st["hold"]:
                    continue
                open_store(page, row)
                account_rows(page, "Open/pending")
                url = None
                for attempt in range(2):  # the reload that carries the checkout link can be slow (WAY/HAR/CUL 10/20)
                    page.locator("input[name='Iracctdetailstables:selected:0']").check()
                    page.locator("#Pay").click()
                    for _ in range(12):
                        time.sleep(2.5)
                        url = checkout_url(page)
                        if url:
                            break
                    if url:
                        break
                    time.sleep(3)
                if not url:
                    st["action"] = "no-checkout-url"
                    continue
                try:
                    st["action"] = nic_fill(ctx, url, code, st["balance"], pay, dry)
                except Exception as e:  # one store's checkout problem must not stop the others
                    st["action"] = {"status": "error", "note": "%s: %s" % (type(e).__name__, str(e)[:200])}
                    for extra in ctx.pages[1:]:
                        try:
                            extra.close()
                        except Exception:
                            pass
                log(code, st["action"])
                json.dump(result, open(month_file, "w"), indent=1)
            paid = [(c, s["balance"]) for c, s in result["stores"].items() if isinstance(s["action"], dict) and s["action"]["status"] == "paid"]
            other = [(c, s["action"]["status"] if isinstance(s["action"], dict) else (s["action"] or s.get("hold") or "held")) for c, s in result["stores"].items() if s["balance"] and not (isinstance(s["action"], dict) and s["action"]["status"] == "paid")]
            if pay and not dry:
                if paid:
                    msg = "VSP gun-check fees for %s paid by e-check: %s — total $%.2f." % (now.strftime("%B"),
                          ", ".join("%s $%.2f" % x for x in paid), sum(a for _, a in paid))
                    if other:
                        msg += " Still open (couldn't finish on the site): %s — I'll retry on the next run." % ", ".join(c for c, _ in other)
                else:
                    msg = "VSP gun-check fees for %s: nothing was paid this run — the payment site didn't cooperate for %s. I'll retry on the next run." % (now.strftime("%B"), ", ".join(c for c, _ in other))
                    ledger("VSP pay run paid nothing: " + "; ".join("%s=%s" % o for o in other))
                dm(msg)
            else:
                dm("VSP gun-check fees for %s: %s — total $%.2f. %s" % (now.strftime("%B"),
                   ", ".join("%s $%.2f" % (c, s["balance"]) for c, s in result["stores"].items() if s["balance"]),
                   result["total_open"], "Dry run completed to the review screen." if dry else "Staged, not paid."))
        finally:
            json.dump(result, open(month_file, "w"), indent=1)
            vp_browser.close(ctx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
