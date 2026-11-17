import json,sys
from wp import wp
out={}
for typ in ('pages','posts'):
    p=1
    while True:
        b=wp('/%s?context=edit&per_page=100&page=%d&status=publish&_fields=id,slug,link,title,content,meta'%(typ,p))
        for it in b: out['%s/%d'%(typ,it['id'])]=it
        if len(b)<100: break
        p+=1
json.dump(out,open('backups_pre/pages_posts_edit_20261116.json','w'))
print(len(out))
