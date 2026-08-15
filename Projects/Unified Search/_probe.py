import osxphotos
db = osxphotos.PhotosDB()
photos = [p for p in db.photos() if p.screenshot]
p = photos[0]
print('uuid', p.uuid)
print('path', p.path)
print('path_edited', p.path_edited)
print('ismissing', p.ismissing)
print('incloud', p.incloud)
print('iscloudasset', p.iscloudasset)
print('original_filename', p.original_filename)
