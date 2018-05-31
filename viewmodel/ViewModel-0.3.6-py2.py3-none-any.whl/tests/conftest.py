import pytest
from objdict import ObjDict
from pymongo import MongoClient
from viewmodel import viewMongoDB as viewModelDB
from viewmodel.json_load import JSONLoad

TEST_DB_NAME = 'test_MV'


@pytest.fixture(scope='session', autouse=True)
def restore_db_from_json():
    JSONLoad(db_name=TEST_DB_NAME).restore_db_from_json()


res = ObjDict(dbname=TEST_DB_NAME, dbserver=None)
viewModelDB.baseDB.connect(res)


TEST_JSON_LOAD_DB_NAME = 'test_json_load_temp_db'


@pytest.fixture(scope='session', autouse=True)
def db():
    client = MongoClient('localhost', 27017)
    database = client[TEST_JSON_LOAD_DB_NAME]
    yield database
    client.drop_database(TEST_JSON_LOAD_DB_NAME)
