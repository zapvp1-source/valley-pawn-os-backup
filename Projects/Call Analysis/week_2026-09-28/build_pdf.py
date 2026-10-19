import docx
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
NAVY=RGBColor(0x2D,0x1A,0x5E); BLUE=RGBColor(0x00,0x99,0xDD); GREY=RGBColor(0x59,0x59,0x59); RED=RGBColor(0xB0,0x1E,0x2D)
OUT='/sessions/festive-trusting-clarke/mnt/Projects/Call Analysis/week_2026-09-28/'
d=docx.Document(); s=d.sections[0]; s.page_width=Inches(8.5); s.page_height=Inches(11)
s.left_margin=s.right_margin=Inches(0.7); s.top_margin=s.bottom_margin=Inches(0.55)
st=d.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(10); st.element.rPr.rFonts.set(qn('w:eastAsia'),'Calibri')
def P(t,size=10,bold=False,color=None,after=2,before=0):
    p=d.add_paragraph(); p.paragraph_format.space_after=Pt(after); p.paragraph_format.space_before=Pt(before)
    r=p.add_run(t); r.font.size=Pt(size); r.bold=bold
    if color: r.font.color.rgb=color
    return p
def B(head,body=''):
    p=d.add_paragraph(style='List Bullet'); p.paragraph_format.space_after=Pt(2)
    r=p.add_run(head+(' ' if body else '')); r.bold=True; r.font.color.rgb=NAVY; r.font.size=Pt(10)
    if body: r2=p.add_run(body); r2.font.size=Pt(10)
def shade(c,fill):
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:color'),'auto'); sh.set(qn('w:fill'),fill); tcPr.append(sh)
def table(rows,widths):
    t=d.add_table(rows=len(rows),cols=len(rows[0])); t.style='Table Grid'
    t.autofit=False
    for j,w in enumerate(widths): t.columns[j].width=Inches(w)
    for i,row in enumerate(rows):
        for j,v in enumerate(row):
            c=t.rows[i].cells[j]; c.width=Inches(widths[j]); p=c.paragraphs[0]; r=p.add_run(str(v)); r.font.size=Pt(9)
            if i==0: r.bold=True; r.font.color.rgb=RGBColor(255,255,255); shade(c,'2D1A5E')
    d.add_paragraph().paragraph_format.space_after=Pt(2)

P('VALLEY PAWN',9,True,BLUE,0)
P('Phone & Text Review — by Store',18,True,NAVY,0)
P('Sep 28 – Oct 18, 2026 (3 weeks)   ·   1,790 recorded calls read, all 5 stores   ·   For Joshua only',9.5,False,GREY,6)

P('THE NUMBERS',11,True,BLUE,2,2)
table([
 ['','Culpeper','Harrisonburg','Waynesboro','Lexington','Roanoke'],
 ['Calls in while open','374','384','323','162','458'],
 ['Missed while open','28 (7%)','82 (21%)','52 (16%)','32 (20%)','66 (14%)'],
 ['Missed calls never reached by phone','4','44','30','12','4'],
 ['Missed-call texts sent / replied*','19 / 3','61 / 19','43 / 5','45 / 4','40 / 4'],
 ['Text conversations (3 wks)','53','76','77','27','46'],
 ['Calls promising a hold past due','23','13','11','15','50'],
 ['Calls giving account info w/o a real ID check','17','12','7','8','19'],
 ['Sell/pawn calls w/ qualifying questions','27 of 49','32 of 56','30 of 64','12 of 22','34 of 65'],
],[2.15,0.95,1.0,1.0,0.95,0.95])
P('*Missed-call text results are logged through Oct 11. Roanoke is on Zoom now and is fully covered. Qualifying questions improved a lot (about 10% in September → about half now).',8,False,GREY,4)

P('FIVE THINGS THAT CUT ACROSS EVERY STORE',11,True,BLUE,2,4)
B('The Oct 1 “no more holds” change is not being followed.','About 110 calls promised a hold or extension on a loan already past due. Stores are making up their own rules: Roanoke says “two months,” Lexington still quotes “75 days” (and “Oct 3”), Waynesboro says “15 days,” and Culpeper, Harrisonburg and Lexington all quote a “5-day grace period.” Roanoke (Benji, Joey) is the heaviest by far. Needs one clear message from Preston on what the rule is.')
B('Account details still go to whoever calls.','About 63 calls: wives, sons, mothers, girlfriends and “calling for” someone got balances, items and due dates. Several phone numbers were changed on a name only. The scripts drafted Sept 28 fix this and are still waiting on your OK.')
B('Police / ATF callers are not verified.','Roanoke read a buyer’s full name, address, birth date, height, weight and license number to an “ATF tracing center” on a callback number the caller supplied (Oct 5). Roanoke also gave a seller’s ID address to a caller saying he was Rocky Mount PD (Oct 8), and Harrisonburg described recent jewelry buys to a caller saying he was Harrisonburg PD. None of the three was confirmed.')
B('Stores running out of cash.','Lexington had no cash all Saturday afternoon (Oct 17) and sent sellers away or to other stores (“I’m low on cash today. I don’t have anything”). Harrisonburg (Oct 3, “we’re out of cash today”), Culpeper and Waynesboro also turned away or delayed deals for cash.')
B('Card readers and app.','A Preston call on Oct 13 says card readers fail on 1–2 of every 5 transactions, and an Oct 14 call says deposits weren’t batching. A firearm that should have been shipped back has sat a month past its return label (Oct 15; the store isn’t named). Many customers can’t pay or see loans in the mobile app.')

def store(name, items):
    P(name,12,True,BLUE,2,6)
    for h,b in items: B(h,b)

store('CULPEPER',[
 ('Phones are the best of the five:','7% missed, steady all three weeks. The most callbacks promised (46), so follow-through is the risk.'),
 ('Holds on past-due loans (23).','Sandy: “Yeah honey, I’ll put that note in” on a loan two months past due. Rob pulled Milwaukee tools back off the floor after they expired and took a payment.'),
 ('Customer lost his collateral.','Joshua (staff) first told Ronnie nothing had gone out for sale, then after a hold: “It’s been melted… I apologize.” (Oct 14)'),
 ('Third parties.','Kathy got her husband Randy’s full account history, balances and due dates (Oct 17). Ashley got Kyle’s layaway status, gun loans, and a hold to the 23rd (Oct 9).'),
 ('Gun shipment signed for by “Scott” — “we do not have a Scott.”','The customer’s firearm package is in the store, but nobody on staff signed for it (Oct 17). Check the receiving log.'),
 ('Other:','A light fixture over the gun case reportedly “caught on fire, started smoking” (Oct 1). Saturday hours were misquoted as 10–6 several times (it’s 10–5). Customers say they walk out when Sandy is off.'),
 ('Praise:','Joshua (staff) is the standout. He verifies callers properly, makes his callbacks, and called the State Police to fix a buyer’s paperwork.'),
])
store('HARRISONBURG',[
 ('Worst missed-call rate: 21%.','44 missed callers were never reached. It is improving week to week (26% → 20% → 17%).'),
 ('Personal calls on the store line.','On Oct 5 the store phone made about 20 short personal calls in 20 minutes. One is a family argument (“where the hell are you guys? We had to go to Kroger because Katie… play[ed] with poop”).'),
 ('Holds and third parties.','Walker: “Yeah, man. It’ll be fine” on pushing a payment to next month. A mother got her daughter’s defaulted laptop details and a layaway to get it back. Preston gave a son his mother’s expired-loan details.'),
 ('Unverified “police” call.','Walker described a Hamilton pocket watch and a 1905 gold-coin necklace to a caller saying he was a Harrisonburg officer (Oct 8).'),
 ('Training gap.','Cam quoted $375–400 on a crossbow worth about $100. Preston caught it and stopped Cam from phone quotes (Oct 15).'),
 ('Praise:','Walker’s buying calls and follow-ups (“Just didn’t want to miss out on your business”). Preston handled two stolen-property callers well.'),
])
store('WAYNESBORO',[
 ('First open Wednesday (Oct 14): every call missed.','All 9 calls from 12:24 to 4:03 PM went unanswered.'),
 ('Missed 16% overall; 30 callers never reached.','Week 3 jumped back to 20%.'),
 ('Holds past due:','“Today would be the last day to pay… before they come out for sale” after 15 days. A Milwaukee loan due Sept 2 was still not pulled on Oct 6.'),
 ('Bought counterfeit trading cards.','Martin paid $120 for cards that failed the rip test. The seller is returning $100 and the amounts don’t reconcile (Oct 13).'),
 ('Police matter waiting on us.','Raleigh PD needs Waynesboro to receive a seized firearm for release to its owner. Their messages went unreturned (Oct 5).'),
 ('Wording to fix:','“No sales tax” and break-even talk on a counter-offer. On the first open Wednesday, 8 texts still told customers the store was closed Wednesdays.'),
 ('Praise:','Chad called a customer back to apologize and offered a discount when “sold” items turned out to be misplaced. Stephanie asks for photos before customers make the drive.'),
])
store('LEXINGTON',[
 ('Missed 20%,','the highest rate for its volume. Staff often say they work alone and close about 30 minutes for lunch.'),
 ('Still running the old 75-day rule.','“At the 75 day mark, I would have to expire it” (Uriah, Oct 9). Staff called first-payment defaults to invite payment instead of expiring them.'),
 ('Out of cash Saturday Oct 17.','Five calls were turned away or told to wait until Monday (“it’s pretty much based off of if I sell anything in the store today”).'),
 ('Possible stolen tablet.','An iPad about to go on the floor came up “blocked” on T-Mobile’s IMEI check (Oct 17). Hold it, don’t sell it. Good catch by staff.'),
 ('Unwinding our own buys.','Staff missed a crack at intake and asked the seller to bring the $120 back (Oct 13 and Oct 16).'),
 ('Praise:','Uriah called back a customer who felt brushed off, after Preston coached him (Oct 17). Strong pricing explanations on silver and PS5s.'),
])
store('ROANOKE',[
 ('Now on Zoom; best callback rate.','45 of 66 missed calls got a call back, and only 4 callers were never reached. Missed calls dropped from 19% to 9%.'),
 ('Biggest hold problem: about 50 calls.','Benji and Joey run a “two-month” rule that isn’t policy: “we’re only supposed to hold them for two months, and you’re already behind more than two months.” Holds are noted to “Monday” or “Friday” on loans due in August and September, firearm loans included.'),
 ('ATF trace personal data read out (Oct 5).','Full buyer identity read to a number the caller supplied. Confirm it was really the ATF tracing center.'),
 ('Seller’s ID address given to an unverified “officer” (Oct 8).','“What’s his address off of his ID? 47 Muse Court Lane.” The blower was also put on hold for him.'),
 ('Possible under-21 gun sale (Oct 7).','Benji to a buyer whose check just cleared: “You were the one that were underage… since you turned 21 Friday.” Pull the 4473 and confirm whether it was a handgun.'),
 ('Other firearm items:','“Could my wife do it? … you should be good” (Joey, pawning a husband’s gun without his ID). A background-check result was given by phone with no ID check.'),
 ('Long holds and complaints:','A hospitalized caller sat on hold about 23 minutes. Several customers say their payments weren’t recorded. A customer selling a pressure washer waited over a week for promised callbacks. For two days after Roanoke started opening Wednesdays, 11 missed-call texts still implied it was closed.'),
 ('Praise:','Fastest text replies (5 min). Kind, effective collections calls. A first-time gun buyer was walked carefully through a private-sale FFL transfer.'),
])
store('TEXTS (Chekkit)',[
 ('Harrisonburg review requests still say “Dixie Pawn Inc.”','36 went out on Oct 9 and Oct 16. That is a setting in Chekkit and can be fixed in minutes.'),
 ('Unanswered customers:','Harrisonburg (an app problem, an extension request and about 8 leads), Waynesboro (about 10 leads, including a .45 ACP), Culpeper (layaway app login, pendant), Roanoke (a late-payment plea), Lexington (refrigerator).'),
 ('By text:','Payoffs and gun prices were given after the AI said they couldn’t be (Lexington). Waynesboro and Lexington told customers “we don’t have enough cash.” Culpeper texts are being sent under one staff login but signed by different people.'),
 ('Opt-outs:','60 STOPs, mostly from the Oct 1 loans blast and Roanoke’s Oct 6 “open Wednesdays” blast to about 1,030 people.'),
])
P('Quotes come from machine transcripts. Play the audio in Zoom (Phone → Recordings) before acting. Call numbers, Zoom IDs and every call’s summary are in review_*.json in this folder.',8,False,GREY,0,8)
d.save(OUT+'Phone_Text_Review_By_Store_Sep28-Oct18.docx')
print('ok')
