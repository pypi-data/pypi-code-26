"""A simple adapter for pymongo's MongoClient class"""
from pymongo import MongoClient

from .error_handlers import is_attribute_set

class MongoWrapper(object):
    """MongoWrapper is a thin adapter around pymongo's MongoClient class. Used this so that 
    some basic attributes ,e.g. mongo url, database and collection names, can be stored 
    within the class.

    To access the MongoClient class directly, use MongoWrapper.mongoclient

    Keyword Arguments:
    mongo_uri - connecting url for the MongoClient. Default is 'mongodb://localhost:27017/'

    db_name - name of the database.

    collection_name - name of the collection for the database 'db_name'
    """
    def __init__(self, mongo_uri='mongodb://localhost:27017/', db_name=None, collection_name=None):
        self._mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.mongoclient = MongoClient(self.mongo_uri)

    @property
    def mongo_uri(self):
        """mongo url address"""
        return self._mongo_uri

    @mongo_uri.setter
    def mongo_uri(self, mongo_uri):
        self._mongo_uri = mongo_uri
        self.mongoclient = MongoClient(self._mongo_uri)

    @property
    @is_attribute_set('db_name')
    def database(self):
        """database adapter for pymongo.MongoClient.Database. Exposes all methods attached to MongoClient's
        database """
        return self.mongoclient[self.db_name]
    
    @property
    @is_attribute_set('db_name')
    @is_attribute_set('collection_name')
    def collection(self):
        """Adapter for pymongo.MongoClient.Database.Collection"""
        return self.mongoclient[self.db_name][self.collection_name]
