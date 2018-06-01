from notmm.dbapi.orm import ZODBFileStorageProxy
from blogengine2.contrib.api_v1.model import CategoryManager
db = ZODBFileStorageProxy('127.0.0.1:4343')
objects = CategoryManager(connection=db).objects.all()
print objects
