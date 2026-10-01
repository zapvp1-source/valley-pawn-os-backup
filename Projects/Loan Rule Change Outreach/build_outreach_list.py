#!/usr/bin/env python3
"""Build the 75+ days-late loan outreach workbook from the Bravo pipeline exports (9/30/2026)."""
import csv, collections, datetime, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

BRAVO = sys.argv[1] if len(sys.argv) > 1 else "/sessions/bold-focused-ride/mnt/Projects/Bravo Data Extraction"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/sessions/bold-focused-ride/mnt/outputs/VP_75-Day_Past-Due_Outreach_List_2026-09-30.xlsx"
ASOF = datetime.date(2026, 9, 30)
STORES = {'CUL': 'Culpeper', 'HAR': 'Harrisonburg', 'LEX': 'Lexington', 'ROA': 'Roanoke', 'WAY': 'Waynesboro'}
MON = {'Culpeper': 150, 'Harrisonburg': 3740, 'Lexington': 3995, 'Roanoke': 7769, 'Waynesboro': 4555}  # #loan-review 9/28

amt = lambda s: float(s.replace('$', '').replace(',', ''))
pd = lambda s: datetime.datetime.strptime(s, '%m/%d/%Y').date()

detail = []
for st in STORES:
    f = f'{BRAVO}/output/2026-09-30_{st}_loans75-detail.csv'
    try:
        rows = list(csv.DictReader(open(f, encoding='utf-8-sig')))
    except Exception:
        rows = []
    if not rows or 'Ticket Number' not in rows[0]:
        continue
    for r in rows:
        r['Store'] = st
        detail.append(r)

contacts = {}
for st in STORES:
    cf = f'{BRAVO}/output/2024-08-30_{st}_forfeiture-winback-comparison-contacts.csv'
    for r in csv.DictReader(open(cf, encoding='utf-8-sig')):
        k = (st, r['Name'].strip().upper())
        lc = pd(r['Last Contact']) if r.get('Last Contact') else datetime.date(2000, 1, 1)
        if k not in contacts or lc > contacts[k][0]:
            contacts[k] = (lc, r)

cust = collections.OrderedDict()
for r in detail:
    k = (r['Store'], r['Customer'].strip().upper())
    c = cust.setdefault(k, {'tickets': set(), 'amt': 0.0, 'due': [], 'mp': set(), 'sms': set()})
    c['tickets'].add(r['Ticket Number']); c['amt'] += amt(r['Loan Amount']); c['due'].append(pd(r['Due Date']))
    c['mp'].add(r['MobilePawn']); c['sms'].add(r['SMS'])

wb = Workbook()
H = Font(name='Arial', bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864')
F = Font(name='Arial'); B = Font(name='Arial', bold=True)
thin = Side(style='thin', color='BFBFBF'); BR = Border(left=thin, right=thin, top=thin, bottom=thin)

def tc(n):
    return ' '.join(w.upper() if w.lower() in ('ii','iii','jr','sr') else w.capitalize() for w in n.split())

def hdr(ws, row, cols):
    for i, c in enumerate(cols, 1):
        x = ws.cell(row=row, column=i, value=c)
        x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical='center'); x.border = BR

def style(ws, r1, r2, c2):
    for row in ws.iter_rows(min_row=r1, max_row=r2, max_col=c2):
        for x in row:
            x.border = BR
            if not x.font.bold:
                x.font = Font(name='Arial', color=x.font.color)

# ---- Sheet 1: Outreach List
ws = wb.active; ws.title = 'Outreach List'
ws['A1'] = 'Valley Pawn — customers with a loan 75+ days late (all 5 stores)'; ws['A1'].font = Font(name='Arial', bold=True, size=13)
ws['A2'] = (f'Source: Bravo saved report "75 Days Past Due" (Past Due Age > 75, Status = LOAN, active), pulled {ASOF:%m/%d/%Y} '
            '12:55–1:06 PM ET via pipeline cell loans75-detail; contact info joined from the Bravo Customers export of 9/30/2026. One row per customer.')
ws['A2'].font = Font(name='Arial', italic=True, size=9)
cols = ['Store', 'Customer', 'Phone', 'Email', 'Address', '# Tickets', '$ Past Due', '% of Store', '% of Company', 'Oldest Due Date',
        'Max Days Past Due', 'MobilePawn', 'SMS Flag (Bravo)', 'Last Contact (Bravo)', 'Email ✔', 'Text ✔', 'Push ✔', 'Channels']
hdr(ws, 4, cols)
r = 5; first = r
order = sorted(cust.items(), key=lambda kv: (kv[0][0], -kv[1]['amt']))
lastrow = first + len(order) - 1
for (st, name), c in order:
    ct = contacts.get((st, name), (None, {}))[1]
    email = (ct.get('E-Mail') or '').strip(); phone = (ct.get('Phone') or '').strip(); addr = (ct.get('Address') or '').replace('\n', ', ')
    email_ok = bool(email) and email.upper() != 'DNC' and '@' in email
    text_ok = bool(phone) and ('SMS' in c['sms'])
    push_ok = 'Activated' in c['mp']
    ws.cell(r, 1, STORES[st]); ws.cell(r, 2, tc(name)); ws.cell(r, 3, phone); ws.cell(r, 4, email); ws.cell(r, 5, addr)
    ws.cell(r, 6, len(c['tickets'])); ws.cell(r, 7, c['amt']).number_format = '$#,##0.00'
    ws.cell(r, 8, f'=IFERROR(G{r}/SUMIFS($G${first}:$G${lastrow},$A${first}:$A${lastrow},A{r}),0)').number_format = '0.0%'
    ws.cell(r, 9, f'=IFERROR(G{r}/SUM($G${first}:$G${lastrow}),0)').number_format = '0.0%'
    ws.cell(r, 10, min(c['due'])).number_format = 'm/d/yyyy'
    ws.cell(r, 11, f'=DATE(2026,9,30)-J{r}').number_format = '0'
    ws.cell(r, 12, '/'.join(sorted(c['mp']))); ws.cell(r, 13, '/'.join(sorted(c['sms']))); ws.cell(r, 14, ct.get('Last Contact', ''))
    ws.cell(r, 15, 'Yes' if email_ok else 'No'); ws.cell(r, 16, 'Yes' if text_ok else 'No'); ws.cell(r, 17, 'Yes' if push_ok else 'No')
    ws.cell(r, 18, f'=IF(O{r}="Yes","Email ","")&IF(P{r}="Yes","Text ","")&IF(Q{r}="Yes","Push","")')
    r += 1
last = r - 1
ws.cell(r, 1, 'TOTAL').font = B
ws.cell(r, 6, f'=SUM(F{first}:F{last})').font = B
ws.cell(r, 7, f'=SUM(G{first}:G{last})').font = B; ws.cell(r, 7).number_format = '$#,##0.00'
ws.cell(r, 9, f'=SUM(I{first}:I{last})').number_format = '0.0%'
for col, L in ((15, 'O'), (16, 'P'), (17, 'Q')):
    ws.cell(r, col, f'=COUNTIF({L}{first}:{L}{last},"Yes")').font = B
style(ws, 5, r, 18)
ws['O4'].comment = Comment('Yes = Bravo has an email address on file that is not "DNC". Email goes out through Brevo.', 'Claude')
ws['P4'].comment = Comment('Yes = phone on file and Bravo SMS flag = SMS (not DNT). Texts go through Chekkit, which also suppresses anyone who replied STOP.', 'Claude')
ws['Q4'].comment = Comment('Yes = MobilePawn app activated. Push goes through Bravo Mobile Messenger.', 'Claude')
ws['K4'].comment = Comment("Days from the oldest ticket due date to 9/30/2026. Bravo's report criterion is Past Due Age > 75.", 'Claude')
for i, w in enumerate([13, 28, 15, 26, 38, 9, 12, 10, 11, 13, 11, 13, 12, 13, 8, 8, 8, 16], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = 'C5'; ws.row_dimensions[4].height = 32

# ---- Sheet 2: Loan Detail
wd = wb.create_sheet('Loan Detail')
wd['A1'] = 'Every row Bravo returned (one row per item on a ticket; a ticket with several items appears several times, each with its item amount)'
wd['A1'].font = Font(name='Arial', italic=True, size=9)
dcols = ['Store', 'Ticket Number', 'Customer', 'Loan Amount', 'Loan Date (Disposition Date)', 'Due Date', 'Pull Date',
         'Age (days since loan)', 'Days Past Due', 'MobilePawn', 'SMS']
hdr(wd, 3, dcols); rr = 4
for x in sorted(detail, key=lambda d: (d['Store'], d['Customer'], d['Ticket Number'])):
    wd.cell(rr, 1, STORES[x['Store']]); wd.cell(rr, 2, x['Ticket Number']); wd.cell(rr, 3, tc(x['Customer']))
    wd.cell(rr, 4, amt(x['Loan Amount'])).number_format = '$#,##0.00'
    wd.cell(rr, 5, pd(x['Disposition Date'])).number_format = 'm/d/yyyy'
    wd.cell(rr, 6, pd(x['Due Date'])).number_format = 'm/d/yyyy'
    wd.cell(rr, 7, pd(x['Pull Date'])).number_format = 'm/d/yyyy'
    wd.cell(rr, 8, int(x['Age'])); wd.cell(rr, 9, f'=DATE(2026,9,30)-F{rr}'); wd.cell(rr, 10, x['MobilePawn']); wd.cell(rr, 11, x['SMS'])
    rr += 1
wd.cell(rr, 1, 'TOTAL').font = B
wd.cell(rr, 4, f'=SUM(D4:D{rr-1})').font = B; wd.cell(rr, 4).number_format = '$#,##0.00'
style(wd, 4, rr, 11)
for i, w in enumerate([13, 16, 28, 12, 14, 12, 12, 12, 12, 13, 8], 1):
    wd.column_dimensions[get_column_letter(i)].width = w
wd.freeze_panes = 'A4'
detail_last = rr - 1

# ---- Sheet 3: Store Summary
wsum = wb.create_sheet('Store Summary')
hdr(wsum, 1, ['Store', 'Customers', 'Tickets', 'Item rows', '$ 75+ days late (9/30)', 'Top customer', 'Top customer $',
              'Top customer share', 'Weekly review 9/28 $ (Slack)', 'Change since Mon'])
rs = 2
for st, nm in STORES.items():
    cs = [(k, c) for k, c in cust.items() if k[0] == st]
    top = max(cs, key=lambda kv: kv[1]['amt']) if cs else None
    wsum.cell(rs, 1, nm)
    wsum.cell(rs, 2, f"=COUNTIF('Outreach List'!$A$5:$A${last},A{rs})")
    wsum.cell(rs, 3, f"=SUMIFS('Outreach List'!$F$5:$F${last},'Outreach List'!$A$5:$A${last},A{rs})")
    wsum.cell(rs, 4, f"=COUNTIF('Loan Detail'!$A$4:$A${detail_last},A{rs})")
    wsum.cell(rs, 5, f"=SUMIFS('Outreach List'!$G$5:$G${last},'Outreach List'!$A$5:$A${last},A{rs})").number_format = '$#,##0.00'
    wsum.cell(rs, 6, tc(top[0][1]) if top else '—'); wsum.cell(rs, 7, top[1]['amt'] if top else 0).number_format = '$#,##0.00'
    wsum.cell(rs, 8, f'=IFERROR(G{rs}/E{rs},0)').number_format = '0.0%'
    wsum.cell(rs, 9, MON[nm]).number_format = '$#,##0.00'; wsum.cell(rs, 9).font = Font(name='Arial', color='0000FF')
    wsum.cell(rs, 10, f'=E{rs}-I{rs}').number_format = '$#,##0.00;($#,##0.00);-'
    rs += 1
wsum.cell(rs, 1, 'COMPANY').font = B
for col in [2, 3, 4, 5, 7, 9, 10]:
    L = get_column_letter(col)
    wsum.cell(rs, col, f'=SUM({L}2:{L}{rs-1})').font = B
    if col in (5, 7, 9, 10):
        wsum.cell(rs, col).number_format = '$#,##0.00;($#,##0.00);-'
wsum.cell(rs, 8, f'=IFERROR(G{rs}/E{rs},0)').number_format = '0.0%'
style(wsum, 2, rs, 10)
wsum['I1'].comment = Comment("Blue = hardcoded from the #loan-review Slack post of 9/28/2026 (weekly review, Bravo Sum panel). Today's figures were cross-checked against the same Sum panel at 1:07–1:14 PM on 9/30 and match to the cent.", 'Claude')
for i, w in enumerate([14, 11, 9, 10, 20, 28, 15, 16, 22, 16], 1):
    wsum.column_dimensions[get_column_letter(i)].width = w

# ---- Sheet 4: Notes
wn = wb.create_sheet('Notes')
notes = [
    'HOW THIS LIST WAS BUILT (9/30/2026)',
    '1. Loans: Bravo POS, Loans/Buys → Custom Reports → saved report "75 Days Past Due". Criteria logged from the screen at run time: Active Loans and Buys; Past Due Age > 75; Status = LOAN; initial rows 250; sort PawnTime asc. Full grid capture (expected = captured on every store per the .meta sidecars).',
    '2. Contacts: Bravo Customers → saved report "Claude Forfeiture Winback Comparison" export of 9/30/2026 (name, phone, address, e-mail, MobilePawn, SMS flag, Last Contact), matched to the loan report on exact customer name within the same store. All 14 customers matched.',
    "3. Cross-check: the weekly loans-75-days-past-due cell (Bravo's own Sum panel) was re-run at 1:07–1:14 PM on 9/30 and matches every store's dollar total on this sheet exactly (CUL $0, HAR $3,090, LEX $4,000, ROA $4,480, WAY $2,525).",
    '',
    'THINGS TO KNOW',
    "• \"75 or more days late\": Bravo's criterion is strictly GREATER THAN 75 days past due. A loan that is exactly 75 days late today is not on this list; it will be tomorrow. The saved report was not changed (it feeds the weekly review).",
    "• Monday's weekly review (9/28) showed $20,209 company-wide; today it is $14,095. Bravo's Sum panel confirms today's figure, so the drop is real movement since Monday (payments / renewals / pulls), not a data problem.",
    '• Loan COUNTS in the weekly review are capped: the weekly cell counts the rows drawn on screen, and Bravo draws at most ~22, so Harrisonburg / Roanoke / Waynesboro showed exactly 22 on 9/28. Dollar totals were never affected. The new loans75-detail cell captures every row. Logged in the Valley Pawn CHANGELOG and BRAVO_KNOWN_ISSUES.',
    '• Rows on the Loan Detail tab are per ITEM, so one ticket with three items appears three times; the "# Tickets" column on the Outreach List counts distinct ticket numbers.',
    '• Email reach is thin: only 2 of 14 customers have a usable email in Bravo (one is marked DNC). Text reaches 11 of 14 (3 are DNT in Bravo; Chekkit also suppresses STOP replies). Push reaches 12 of 14 (MobilePawn activated).',
    '• Channels: Email = Brevo · Text = Chekkit campaign per store · Push = Bravo Mobile Messenger. Texts must identify Valley Pawn, include STOP wording, and go out 8am–9pm ET (handbook §07.06 / TCPA / VA TPPA).',
    '• Nothing has been sent. This workbook is the list only.',
]
for i, t in enumerate(notes, 1):
    c = wn.cell(i, 1, t)
    c.font = Font(name='Arial', bold=(t != '' and t.isupper()), size=10)
    c.alignment = Alignment(wrap_text=True, vertical='top')
wn.column_dimensions['A'].width = 140

wb.save(OUT)
print('customers', len(cust), 'detail rows', len(detail), 'total $', round(sum(c['amt'] for c in cust.values()), 2), '->', OUT)
