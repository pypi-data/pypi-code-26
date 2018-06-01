from notmm.dbapi.orm import ZODBFileStorageProxy
# init the db
db = ZODBFileStorageProxy('/var/db/zodb/blogs.fs')
# retrieve tkadm30
user = db.Author.findone(username='tkadm30')
messages = user.m.messages()
for item in messages:
    print item.content
    print item.get_absolute_url()
