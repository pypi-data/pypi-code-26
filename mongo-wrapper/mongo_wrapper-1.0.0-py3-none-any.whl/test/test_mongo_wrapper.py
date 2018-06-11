import unittest

import pymongo

from ..mongo_wrapper import MongoWrapper

class TestMongoWrapper(unittest.TestCase):
    def setUp(self):
        self.mongo = MongoWrapper()

    def test_using_database_fails(self):
        """test if calling MongoWrapper.database fails if db_name attribute not set"""
        try:
            self.mongo.database
            raise TypeError('you should not reach this')
        except Exception as e:
            self.assertEqual(type(e), AttributeError)

    def test_using_database_works_if_db_name_set(self):
        """passes if db_name is set"""
        self.mongo.db_name = 'test'
        self.assertIsInstance(self.mongo.database, pymongo.database.Database)

    def test_using_collection_fails(self):
        """test if calling MongoWrapper.collection fails if collection_name not set"""
        try:
            self.mongo.collection
            raise TypeError('this should not be reached')
        except Exception as e:
            self.assertEqual(type(e), AttributeError)

    def test_using_collection_works_if_collection_name_set(self):
        self.mongo.collection_name = 'test_collection'
        self.mongo.db_name = 'test'
        self.assertIsInstance(self.mongo.collection, pymongo.collection.Collection)

    def test_access_to_mongoclient_works(self):
        self.assertIsInstance(self.mongo.mongoclient, pymongo.mongo_client.MongoClient)

