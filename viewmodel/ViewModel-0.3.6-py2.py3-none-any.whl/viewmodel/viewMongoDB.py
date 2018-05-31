#!/usr/bin/env python3
"""
this is the mongo DB version of viewModelDB.
import as ViewModelDB

provides a 'baseDB' object as a connection to mongo.
baseDB.db is the access to the database
This could be upgraded to provide fault tolerance in future.
"""
import pymongo
def key(fld):
    """if sqlA return fld.key"""
    return fld.split('.', 1)[1] #for MongoDB
def pclass(fld):
    """if sqlA return fld.key"""
    return fld.split('.', 1)[0] #for MongoDB

class CollectEmulator:
    """ emulates a mongo collection, by getting collection if needed"""
    def __init__(self,name):
        self.baseDB = baseDB
        self.name=name

    def find(self,*args,**kwargs):
        return self.baseDB.db.get_collection(self.name).find(*args,**kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'CollectEmulator:'+self.name


class DBConnector:
    def __init__(self, theDBObj):
        self._theDBObj = theDBObj

    def __getattr__(self, attr):
        return CollectEmulator(attr)

    def get_collection(self, collect_name):
        return self._theDBObj._db_con.get_collection(collect_name)


class ViewModelDB:
    """ this class manages the mongo connections"""
    def __init__(self, site):
        """ site expecting an ObjDict (but object will quack right now)
            None is the setting to use localhost
        """
        self.dbserver = getattr(site, 'dbserver', None)
        self.dbname = getattr(site, 'dbname', None)
        # no more autoconnect
        # if site. 'dbserver'):
        #    self._make_con(self.dbserver, self.dbname)
        self._db = DBConnector(self)
        self.con = None
        self._db_con = None

    def _make_con(self, dbserver, dbname):
        print('make con', dbname)
        self.con = pymongo.MongoClient(dbserver)
        if dbname:
            self._db_con = self.con.get_database(dbname)
    
    @property
    def db(self):
        return self._db

    def connect(self, site):
        self.dbserver = getattr(site, 'dbserver', self.dbserver)
        self.dbname = getattr(site, 'dbname', self.dbname)
        self._make_con(self.dbserver, self.dbname)

try:
    import siteSettings.site as site
except ImportError:
    site = object() #ObjDict(dbserver=False,dbname=None)
#else:
#    engstr= site.dbserver
#    dbstr=site.dbname

baseDB = ViewModelDB(site)
print("loaded modeldb")
def default(collect):
    """retireve collection from baseDB"""
    if isinstance(collect,CollectEmulator):
        collect = collect.name
    return baseDB.db.get_collection(collect)
