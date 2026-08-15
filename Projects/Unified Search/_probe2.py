import osxphotos
db = osxphotos.PhotosDB()
photos = [p for p in db.photos() if p.screenshot]
local = sum(1 for p in photos if not p.ismissing)
missing = sum(1 for p in photos if p.ismissing)
print('local', local, 'missing', missing, 'total', len(photos))
allp = db.photos()
local_all = sum(1 for p in allp if not p.ismissing)
print('all photos local:', local_all, 'of', len(allp))
