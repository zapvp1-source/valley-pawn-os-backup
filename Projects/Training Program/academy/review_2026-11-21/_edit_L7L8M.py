import json,glob,sys
LOG=[]
SRC="CEO rulings 2026-11-21 (ACADEMY_FINAL_RULINGS)"
def find(pat):
    m=[f for f in glob.glob(pat) if not f.endswith('.bak')]; assert len(m)==1,(pat,m); return m[0]
class L:
    def __init__(s,pat):
        s.f=find(pat); s.d=json.load(open(s.f)); s.id=s.d['id']; s.n=0
    def _get(s,path):
        o=s.d
        for k in path[:-1]: o=o[k]
        return o,path[-1]
    def rep(s,path,old,new,rule):
        o,k=s._get(path); cur=o[k]; assert isinstance(cur,str) and cur.count(old)==1,(s.id,path,old,cur)
        o[k]=cur.replace(old,new); LOG.append((s.id,ps(path),old,new,rule)); s.n+=1
    def setv(s,path,new,rule):
        o,k=s._get(path); old=o[k]; assert old!=new,(s.id,path)
        o[k]=new; LOG.append((s.id,ps(path),old,new,rule)); s.n+=1
    def opt(s,qi,oi,text=None,why=None,rule=''):
        if text is not None: s.setv(['quiz','questions',qi,'options',oi,'text'],text,rule)
        if why is not None: s.setv(['quiz','questions',qi,'options',oi,'why'],why,rule)
    def save(s):
        if SRC not in s.d['sources']: s.d['sources'].append(SRC)
        json.dump(s.d,open(s.f,'w'),indent=2,ensure_ascii=False); open(s.f,'a').write('\n') if RAWNL.get(s.f) else None
def ps(path):
    out=''
    for k in path: out+= '[%d]'%k if isinstance(k,int) else '.'+k
    return out
RAWNL={}
for f in glob.glob('lessons/L7/*.json')+glob.glob('lessons/L8/*.json')+glob.glob('lessons/M/*.json'):
    RAWNL[f]=open(f).read().endswith('\n')
S=lambda i,k,*r:['slides',i,k,*r]
Q=lambda i,*r:['quiz','questions',i,*r]

# ---------------- L7-02
x=L('lessons/L7/02_*.json')
x.setv(S(1,'bullets',3),"No agreement to sign. The customer gets a receipt showing the balance and the payment schedule",21)
x.rep(S(1,'say'),"Every layaway has a signed agreement, and two receipts that both get signed. The original goes to the customer, the copy goes in the daily folder.","There's no layaway agreement to sign. The customer gets a receipt that shows the balance and the payment schedule.",21)
x.setv(S(8,'bullets',2),"Past 30 days: no return",'9/30')
x.setv(S(8,'bullets',3),"Receipt, original condition, all accessories. No returns on ammo or consumables",9)
x.setv(S(8,'bullets',4),"Firearms return like any other item: 7 days money back, store credit through day 30",9)
x.rep(S(8,'say'),"After thirty days there's no automatic refund, and a manager reviews it.","After thirty days there's no return.",'9/30')
x.rep(S(8,'say'),"No returns on firearms, ammunition or consumables.","No returns on ammunition or consumables. Firearms return like any other item.",9)
x.setv(S(9,'bullets',2),"Past 30 days: there is no warranty",30)
x.rep(S(9,'say'),"Past thirty days, a manager reviews it case by case.","Past thirty days, there is no warranty.",30)
x.rep(['key_points',6],"days 8–30 store credit, past 30 a manager. Warranty: stops working inside 30 days, we make it right","days 8–30 store credit, firearms included. Warranty: stops working inside 30 days, we make it right; no warranty after 30 days",'9/30')
x.opt(6,1,"Politely explain that we can't take returns on ammunition or consumables","No returns on ammunition or consumables. Say it kindly and plainly. Firearms return like any other item, but ammunition doesn't.",9)
x.save()

# ---------------- L7-03
x=L('lessons/L7/03_*.json')
x.rep(['floor_check'],"never confirm a firearm","no firearm detail to an unverified caller",13)
x.setv(S(0,'bullets',1),"Three rules: verify before you disclose, quote or capture, firearm loans only after full verification",13)
x.rep(S(0,'say'),"quote or capture, and never confirm a firearm.","quote or capture, and a firearm on a loan is only discussed once the account is fully verified.",13)
x.setv(S(2,'bullets',4),"Photos help with a quote. Gold and jewelry are quoted in the store only, after appraisal",'13/27')
x.rep(S(2,'say'),"Remember from Level 1: gold, silver and diamonds get no number unless the spot sheet is open and you know what the item is.","Photos help, so ask for them. The exception is gold and jewelry. Those are quoted in the store only, after we appraise them.",'13/27')
x.setv(S(5,'bullets',3),"A firearm on a loan: once the account is fully verified, discuss it like any other loan item",13)
x.rep(S(5,'say'),"And firearms are never confirmed on the phone, to anyone.","And once the account is fully verified, a firearm on a loan is discussed like any other loan item.",13)
x.rep(['key_points',4],"Never confirm a firearm","Once verified, a firearm on a loan is discussed like any other loan item",13)
x.save()

# ---------------- L7-05
x=L('lessons/L7/05_*.json')
x.setv(S(3,'bullets',3),"Price off SOLD listings, not active ones, in the same used condition and with at least one bid. Price at the higher average sold price: you can always come down, you can't go up",23)
x.rep(S(3,'say'),"Asking prices are just what people hope to get.","Asking prices are just what people hope to get. Price at the higher average sold price. You can always come down, but you can't go up.",23)
x.setv(['key_points',4],"Price from sold comps with a bid, used condition, at the higher average sold price",23)
x.opt(4,1,"Around $300, a little under the middle of the sold comps, so it moves quickly","Right comps, wrong spot in them. Our rule is the higher average sold price. You can always come down; you can't go up.",23)
x.opt(4,2,"At the higher average sold price, toward the $340 end of the sold comps","Sold listings with a bid, in used condition, priced at the higher average sold price. You can always come down, but you can't go up.",23)
x.setv(Q(4,'options',1,'correct'),False,23); x.setv(Q(4,'options',2,'correct'),True,23)
x.save()

# ---------------- L7-07
x=L('lessons/L7/07_*.json')
x.setv(['call_clip'],None,28)
x.rep(['objectives'],"say no with a real referral","say no well and offer what we can do instead",24)
x.setv(S(4,'bullets',1),"Never send a customer to a competitor. Say what we can do instead",24)
x.setv(S(4,'say'),"Sometimes the answer is no, and that's fine. Say it clearly and early, with the real reason. Then tell them what we can do. Picture a drummer trying to sell his own brand of drumsticks. You say no right away, you explain why, and you tell him what we do buy. He can still leave saying thank you. Our rule is we never send a customer to a competitor. And leave the door open. Tell them what we pay the most for, so next time they bring us that.",24)
x.setv(['key_points',5],"Say no early, with the real reason, then what we can do. Never send a customer to a competitor",24)
x.opt(0,1,why="Let them vent, apologize, then protect them. Handled that way, a customer like this ends up thanking us just for letting him come back.",rule=28)
x.opt(1,1,"Hear him out, apologize, and tell him honestly the warranty ended at 30 days","There is no warranty after 30 days, and no manager review. Let him vent, apologize, and say no clearly with the real reason. If a coworker told him otherwise, own that too.",30)
x.opt(1,2,why="There is no warranty after 30 days. Don't promise an exchange we don't give.",rule=30)
x.opt(3,1,why="Call before she even misses it. It takes under a minute, and going out of your way is the standard.",rule=28)
x.opt(4,1,"Say no early with the real reason, then tell him what we do buy and what we pay the most for","Real reason, what we can do, door left open. A firm no can still end in a thank you.",24)
x.opt(4,2,"Say no clearly with the real reason, and point him to a music store that might want them","Never send a customer to a competitor. Say what we can do instead: what we buy and what we pay the most for.",24)
x.save()

# ---------------- L7-11
x=L('lessons/L7/11_*.json')
x.setv(['call_clip'],None,28)
x.setv(S(3,'bullets',1),"Bundle instead of cut: two optics together at $160 rather than slicing the price of one",28)
x.rep(S(3,'say'),"One of our associates sold two optics together at a hundred sixty instead of slicing the price of one.","Say a customer wants two optics. Sell the pair together at a hundred sixty instead of slicing the price of one.",28)
x.opt(4,1,why="Get the customer's number first, then bundle instead of cutting. The pair at one price keeps most of the margin (KB negotiation-first-to-speak).",rule=28)
x.save()

# ---------------- L7-12
x=L('lessons/L7/12_*.json')
x.setv(['call_clip'],None,28)
x.rep(S(1,'bullets',2),"Firearms: case, ammo (the lock comes with it, free)","Firearms: case, ammo (a lock is offered with handguns only)",15)
x.rep(S(1,'say'),"Firearms get a case, a lock, and ammunition.","Firearms get a case and ammunition, and a lock is offered with a handgun.",15)
x.setv(S(2,'bullets',0),"Ask 'what number do you need to be at?', then build the deal up with add-ons to fill it",28)
x.rep(S(2,'say'),"Here's a trick from one of our best calls. The associate asked the customer what number he needed to be at, then built the deal up with games to fill it.","Here's a trick that works. Ask the customer what number he needs to be at, then build the deal up with games to fill it.",28)
x.opt(2,0,why="A budget is a basket, not a ceiling. He has forty dollars left that an add-on can fill.",rule=28)
x.opt(2,1,why="Build the deal up to the number with the add-on that makes it better (§05.03).",rule=28)
x.opt(2,2,why="He told you his number. Fill it; don't blow past it.",rule=28)
x.save()

# ---------------- L7-14
x=L('lessons/L7/14_*.json')
x.setv(S(3,'bullets',0),"Needs-it-to-work: ammunition in the right caliber. Makes-it-better: a case, a cleaning kit, optics. A lock is offered with handguns only",15)
x.rep(S(3,'say'),"The makes-it-better add-ons are a case, a lock, a cleaning kit, optics.","The makes-it-better add-ons are a case, a cleaning kit, optics. A lock is offered with handguns only.",15)
x.setv(S(3,'bullets',2),"Account with an email, so the record is on file. Firearms return like any other item: 7 days money back, store credit through day 30. Say the four things",9)
x.setv(S(3,'bullets',3),"A transfer is a service fee, not a retail sale, so it isn't counted in your sales total. How it rings is Level 6",32)
x.rep(S(3,'say'),"A transfer is not a sale and doesn't count toward your number.","A transfer is a service fee, not a retail sale, so it isn't counted in your sales total.",32)
x.setv(S(4,'bullets',2),"Buyer under 21: no handgun. Wants a rifle with a detachable magazine or a pistol grip? Call the Market Manager BEFORE you start any paperwork",12)
x.rep(S(4,'say'),"If you think you're looking at an assault firearm, or the buyer is under twenty-one, pause and get the current rule from the Market Manager before you go any further.","If a buyer under twenty-one wants a rifle with a detachable magazine or a pistol grip, call the Market Manager before you start any paperwork, to verify it's legal today.",12)
x.setv(['key_points',3],"Add-ons: ammo in the right caliber, then case, cleaning kit, optics. A lock is offered with handguns only",15)
x.setv(['key_points',4],"A transfer is a service fee, not a retail sale. It isn't counted in your sales total",32)
x.setv(['key_points',5],"Delay or denial: Level 6. Under-21 buyer and a rifle with a detachable magazine or pistol grip: call the Market Manager before any paperwork",12)
x.opt(2,1,"Ammo in the right gauge, then case and cleaning kit; an account with an email; the four things; then the paperwork per Level 6",rule=15)
x.opt(5,0,why="A transfer is a service fee, not a retail sale, so it isn't counted in your sales total. The optic he's looking at would be (KB transfer-firearm-accounting).",rule=32)
x.opt(5,1,why="A transfer is a service fee, not a retail sale. The man at the optics shelf is a sales customer, and that sale is yours (KB transfer-firearm-accounting; §05.03).",rule=32)
x.setv(Q(6,'prompt'),"A buyer who is 20 wants a rifle with a detachable magazine and a pistol grip. What do you do?",12)
x.opt(6,0,why="The 4473 and the background check don't settle this. An under-21 buyer and this kind of rifle means a call to the Market Manager before any paperwork starts.",rule=12)
x.opt(6,1,why="That's a judgment call at the counter. The Market Manager verifies what's legal today, before any paperwork.",rule=12)
x.opt(6,2,"Call the Market Manager before you start any paperwork","Under-21 buyer and a rifle with a detachable magazine or pistol grip: call the Market Manager before paperwork starts, to verify current legality.",12)
x.save()

# ---------------- L8-04
x=L('lessons/L8/04_*.json')
x.rep(S(0,'bullets',0),"photos, fingerprints, signatures","photos of IDs, signatures",18)
x.rep(S(0,'say'),"photos of I Ds, fingerprints, signatures","photos of I Ds, signatures",18)
x.opt(3,0,"Ring it under his login, then tell him when he's back so he knows","There is never a reason to conduct a transaction under another employee's login; telling him later doesn't fix accountability or the audit trail (§02.04).",5)
x.save()

# ---------------- M-01
x=L('lessons/M/01_*.json')
x.setv(S(3,'bullets',1),"Days 1–5: grace period, no late fee",10)
x.setv(S(3,'bullets',2),"Day 6: a late fee of 5% of the loan principal starts. It is not printed on the ticket",10)
x.setv(S(3,'bullets',3),"Then 10 more days, and the loan expires. Nothing is pulled before that",10)
x.setv(S(3,'bullets',4),"Never made a first payment? Mark it expired in Bravo as soon as it's past due, any amount — but nothing is pulled, priced or sold before those 15 days are up",10)
x.setv(S(3,'bullets',5),"A renewal must show the correct loan date in Bravo; count from the latest due date in Bravo",19)
x.setv(S(3,'say'),"Loans run on one timeline, and every count here is days past due. Day one is the day after the due date. Days one through five are the grace period. On day six, a late fee starts. It's five percent of the loan principal, and it is not printed on the ticket. Then there are ten more days before the loan expires. Nothing gets pulled before that. A loan that never got a first payment is marked expired as soon as it's past due, whatever the amount, but it still isn't pulled before those fifteen days are up. And a renewal has to show the correct loan date in Bravo, because every count runs from the latest due date there.",'10/19')
x.setv(['key_points',2],"Loans: every count is days past due; 5-day grace, a 5% late fee on the principal from day 6 (not printed on the ticket), then 10 more days and the loan expires",10)
x.setv(['key_points',3],"First-payment defaults are marked expired at day 1 past due and pulled only after the 15 days are up; a renewal must show the correct loan date in Bravo",'10/19')
x.opt(3,0,"Pull and price it — at 40 days past due the loan expired weeks ago","An expired loan still doesn't move into sellable inventory without a statement of ownership, whatever the day count (§06.01; Va. Code § 54.1-4005).",10)
x.setv(Q(4,'prompt'),"A customer comes in on day 8 past due to pay. He says, 'My ticket doesn't say anything about a late fee.' What's right?",10)
x.opt(4,0,"Waive it — if the fee isn't printed on the ticket, we can't charge it","The late fee is not printed on the ticket, but it's the rule: 5% of the loan principal, starting on day 6 past due.",10)
x.opt(4,1,"Explain that a 5% late fee on the principal started on day 6","Five-day grace period, then a late fee of 5% of the loan principal from day 6. It isn't printed on the ticket, so explain it plainly.",10)
x.opt(4,2,"Charge 5% of the full payoff, interest included, since he's past the grace period","The late fee is 5% of the loan principal, not of the payoff.",10)
x.setv(Q(5,'prompt'),"A new associate pulls a loan on day 8 past due because 'the grace period is over.' What do you tell her?",10)
x.opt(5,0,"Good catch — the 5-day grace period is over, so day 8 is fine to pull","The end of the grace period starts the late fee, not the pull. The loan has 10 more days before it expires.",10)
x.opt(5,1,"Put it back. Day 6 starts the late fee; the loan expires 10 days later","Five days of grace, the late fee from day 6, then 10 more days before the loan expires. Nothing is pulled before that.",10)
x.opt(5,2,"Leave it pulled, but don't price it until the loan expires","Pulling it is the problem. It stays in loan status until the loan expires.",10)
x.opt(6,0,why="First-payment defaults are marked expired as soon as they're past due, but the 15-day statutory hold still applies before anything is pulled or sold (§06.01; §05.01).",rule=10)
x.opt(6,1,"Treat it like any other loan and wait out the grace period before you mark it expired","First-payment defaults don't wait. They're marked expired as soon as they're past due, and pulled once the 15 days are up.",10)
x.opt(7,0,"Pull it — day 35 is long expired, and a renewal doesn't change the original date","A renewal moves the due date. Counting from the old one pulls a loan that isn't past due (§06.01).",'10/19')
x.opt(7,1,why="A renewal must show the correct loan date in Bravo, and every count runs from the latest due date there.",rule=19)
x.opt(7,2,"Charge the 5% late fee now, since it's past day 6 from the original due date","This loan isn't past due; its due date moved with the renewal. Check that the renewal shows the correct loan date in Bravo.",'10/19')
x.save()

# ---------------- M-04
x=L('lessons/M/04_*.json')
x.rep(Q(4,'prompt'),"gave a gold price without the spot sheet","quoted a gold price over the phone",'27/13')
x.save()

# ---------------- M-05
x=L('lessons/M/05_*.json')
x.setv(S(0,'bullets',3),"They're added to Gusto for you — managers don't onboard new hires in Gusto — so their documents are waiting",32)
x.rep(S(0,'say'),"And they're added to Gusto, so their paperwork is waiting for them.","You don't onboard them in Gusto. That's done for you, so their paperwork is waiting for them.",32)
x.setv(S(2,'bullets',0),"Gun safety class + certificate, on the clock. They pay for the class and are reimbursed as a paid-out from the till. The certificate goes to the Market Manager, who gets it filed in Gusto",7)
x.rep(S(2,'say'),"The gun safety class and certificate are done on the clock, the company pays for the certificate, and it's verified at the provider's site.","The gun safety class and certificate are done on the clock. The employee pays for the class and is reimbursed as a paid-out from the till. The certificate goes to the Market Manager, who gets it filed in Gusto.",7)
x.setv(S(4,'bullets',1),"Do one when the training prompts for it, and at your discretion. Watch them do it, then mark it off in the New Hire Training Tracker the same day",8)
x.rep(S(4,'say'),"Watch them do the real thing, then mark it off in the training tracker the same day.","You do one when the training prompts for it, and at your discretion. Watch them do the real thing, then mark it off in the training tracker the same day.",8)
x.opt(2,0,"Give her until Friday and note it on the checklist, since the store's computer caused the delay",rule=32)
x.save()

# ---------------- M-06
x=L('lessons/M/06_*.json')
x.rep(S(0,'bullets',0),"counting a drawer","counting the till",5)
x.setv(S(0,'bullets',1),"When the training prompts for one, or at your discretion, you watch them do it, for real, and tap ✅",8)
x.rep(S(0,'say'),"counting a drawer, opening and closing the store. You watch them do it for real, and then you tap the check.","counting the till, opening and closing the store. You do one when the training prompts for it, and at your discretion. You watch them do it for real, and then you tap the check.",'5/8')
x.rep(S(1,'bullets',0),"real drawer","real till",5)
x.rep(S(1,'bullets',3),"drawer counts only","till counts only",5)
x.rep(S(1,'say'),"a real drawer","a real till",5)
x.rep(['key_points',0],"Screen test + Floor Check = mastered;","Screen test + Floor Check = mastered; do one when the training prompts for it, and at your discretion;",8)
x.setv(Q(0,'prompt'),"Watching a till-count Floor Check, you see your trainee about to skip printing the Bravo count report. You say, 'Don't forget the report.' She prints it and finishes perfectly. Pass or redo?",'4/5')
x.opt(0,0,"Pass — the till balanced, and every step, the report included, got done",rule='4/5')
x.opt(0,1,"Redo. Coach the report step now and watch a full count another day",rule='4/5')
x.opt(0,2,"Pass, and note in the Academy that you gave her one reminder on the report",rule='4/5')
x.rep(Q(5,'prompt'),"A trainee's drawer count came out $10 short.","A trainee's till count came out $10 short.",5)
x.opt(5,0,"Redo — the till didn't balance, and a pass means the numbers have to match","The Floor Check line for balancing the till includes handling a mismatch: recount, research, call the Market Manager before EOD, document. She did every step (L2-03 floor_check).",5)
x.save()

json.dump(LOG,open('review_2026-11-21/_L7L8M_log.json','w'),indent=1,ensure_ascii=False)
print(len(LOG),'edits')
