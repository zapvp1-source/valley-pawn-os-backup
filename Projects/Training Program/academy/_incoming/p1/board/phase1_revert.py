import sys, json, copy; sys.path.insert(0,'board')
from edit_lib import *
import edit_lib
ORIG='/tmp/orig/'
import glob,os
def orig(lid):
    p=path_of(lid); rel=os.path.relpath(p,'/home/claude/academy_review') if False else p.split('academy_review/')[-1]
    rel=os.path.normpath(rel).split('board/../')[-1]
    return json.load(open(ORIG+rel))
def revert_say(lid, idx):  # 1-based slide index in current file, take original slide by heading match
    cur=slide(lid,idx); o=orig(lid)
    m=[s for s in o['slides'] if s['heading']==cur['heading']]
    assert m, (lid, cur['heading']); cur['say']=m[0]['say']; edit_lib._touched.add(lid)
def revert_kp(lid):
    load(lid)['key_points']=orig(lid)['key_points']; edit_lib._touched.add(lid)
def revert_field(lid,k):
    load(lid)[k]=orig(lid)[k]; edit_lib._touched.add(lid)
def revert_lesson_narr(lid):
    o=orig(lid); d=load(lid)
    for k in ('title','objectives','minutes','key_points'): d[k]=o[k]
    om={s['heading']:s for s in o['slides']}
    for s in d['slides']:
        if s['heading'] in om: s['say']=om[s['heading']]['say']
    edit_lib._touched.add(lid)

# L1-05: all narrated changes deferred (bullets to match old narration)
revert_lesson_narr('L1-05')
bullet_sub('L1-05',1,'never explain how we run the store','never explain the store')
bullet_sub('L1-05',3,"'Yes sir, the pistol, it's still here'","'Yes sir, the Glock 30, it's still here'")
# L1-03 closed-day: defer (old D71 default stands until re-voiced)
revert_say('L1-03',1); bullet('L1-03',1,"Third day lands on a day the store is closed? Plan to finish on day 1 or 2","Third day lands on a day the store is closed? It's due the day before")
# L2-03 kp, L3-04 slide 4, L7-02 kp, L2-04 slide 2
revert_kp('L2-03'); revert_say('L3-04',4); revert_kp('L7-02'); revert_say('L2-04',2)
# L7-06 eBay: narration + bullet back
revert_say('L7-06',1); bullet('L7-06',1,"More than 3% late and the store loses Top Rated. Pile up defects and cases and the store goes Below Standard — buried in search","More than 3% late and the store loses Top Rated status: no fee discount, pushed down in search")
# key points not wrong in old form
for lid in ('L4-04','M-01','L1-01','L3-03'): revert_kp(lid)
# L8-00 annual window deferred
revert_lesson_narr('L8-00'); bullet('L8-00',3,"Everyone repeats the three annual lessons every January, due by January 31 — same window as your gun-safety recert","Everyone repeats the three annual lessons every year")
# L5-01 slide 3 consent line deferred (bullet keeps consent)
revert_say('L5-01',3)
# L7-15: original slides back, plus the untaught day-7 bullet on the scorecard slide (free)
d=load('L7-15'); d['slides']=copy.deepcopy(orig('L7-15')['slides'])
s6=d['slides'][5]; s6['bullets'][-1]=s6['bullets'][-1]+'. Not done by day 7? Tell your manager the same day'
s6['bullets']=[b.replace("8. Finished it: the four things (warranty, clearance, free layaway, the app) and the email on the account","8. Finished it: the four things before they leave (warranty, free layaway, the app, plus clearance) and the email on the account") for b in s6['bullets']]
edit_lib._touched.add('L7-15')
print(save_all())
