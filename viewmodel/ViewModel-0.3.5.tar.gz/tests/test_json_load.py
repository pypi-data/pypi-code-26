# -*- coding: utf-8 -*-
# Copyright 2017 Salt Technologies Pty Ltd
# Licensed under the ???? License, see LICENSE file for details.

"""Tests for :mod:`viewmodel.?` module (JSON load to DB)."""
import shutil
from typing import List
import os
import pytest
from bson import ObjectId
from viewmodel.json_load import JSONLoad, DEFAULT_DUMP_DATA_FOLDER_NAME

TEST_DB_NAME = 'test_json_load_temp_db'


def get_test_data_path(is_test=False):
    path = os.getcwd()
    if not path.endswith('tests'):
        path = os.path.join(path, 'tests')
    if is_test:
        return path
    else:
        return os.path.join(path, 'test_data')


@pytest.fixture
def test_db():
    conn = JSONLoad(db_name=TEST_DB_NAME)
    yield conn
    conn.drop_db(TEST_DB_NAME)


class TestLoadJSONFile:
    def test_load_json_file_manual(self, db):
        data = db.data

        test_data = {"name": "Julie"}
        # insert test_data to create the collection
        data_id = data.insert_one(test_data).inserted_id
        assert isinstance(data_id, ObjectId)

        # did the data get inserted?
        search = db.data.find_one()
        assert isinstance(search, dict)
        assert search['name'] == 'Julie'

    def test_load_json_init_ok(self):
        db_connect = JSONLoad(db_name='my_collection')
        assert db_connect.host_name == 'localhost'
        assert db_connect.port_number == 27017
        assert db_connect.db_name == 'my_collection'
        assert db_connect.client
        assert db_connect.db

    def test_load_json_db_name_missing(self):
        with pytest.raises(ValueError) as error_message:
            JSONLoad()
        assert 'DB name (db_name) required!' in str(error_message)

    def test_insert_once(self, test_db):
        conn = test_db
        test_data = {"address": "1 Redwood Place"}
        data_id = conn.insert_one(collection_name='my_collection', data=test_data)
        assert isinstance(data_id, ObjectId)

    def test_insert_once_missing_parameters(self, test_db):
        conn = test_db
        data_id = conn.insert_one()
        assert data_id == "Missing parameters (collection_name + data)!"
        data_id = conn.insert_one(collection_name='test_this_coll')
        assert data_id == "Missing parameter (data)!"
        data_id = conn.insert_one(data={1: 'string'})
        assert data_id == "Missing parameter (collection_name)!"

    def test_insert_many(self, test_db):
        conn = test_db
        test_data = [
            {"address": "1 Redwood Place", "state": 'NSW'},
            {"address": "2 Green Street", "state": 'Qld'}
        ]
        data_ids = conn.insert_many(collection_name='my_many_collection', data=test_data)
        assert isinstance(data_ids, List)
        assert isinstance(data_ids[0], ObjectId)

    def test_insert_many_missing_parameters(self, test_db):
        conn = test_db
        data_ids = conn.insert_many()
        assert data_ids == "Missing parameters (collection_name + data)!"
        data_ids = conn.insert_many(collection_name='test_coll')
        assert data_ids == "Missing parameter (data)!"
        data_ids = conn.insert_many(data=[{'a': 1}])
        assert data_ids == "Missing parameter (collection_name)!"

    def test_drop_db(self):
        conn = JSONLoad(db_name='drop_test')
        test_data = {"address": "1 Redwood Place"}
        data_id = conn.insert_one(collection_name='my_drop_collection', data=test_data)
        assert isinstance(data_id, ObjectId)
        message = conn.drop_db(db_name='drop_test')
        assert message == "DB drop_test dropped!"

    def test_drop_db_does_not_exist(self):
        conn = JSONLoad(db_name='drop_test')
        message = conn.drop_db(db_name='db_missing')
        assert message == "DB db_missing does not exist! No action taken!"

    def test_drop_collection(self, test_db):
        conn = test_db
        test_data = {"junk": 10}
        conn.insert_one(collection_name='junk_coll', data=test_data)
        test_data = {"junket": 10}
        data_id = conn.insert_one(collection_name='junk_coll_2', data=test_data)
        assert isinstance(data_id, ObjectId)
        message = conn.drop_collection(collection_name='junk_coll')
        assert message == "Collection junk_coll dropped!"
        collections = conn.db.collection_names(include_system_collections=False)
        assert len(collections) > 0

    def test_method_read_json_data_file(self, test_db):
        path = get_test_data_path()
        fn = "devices.pdf"

        conn = test_db
        res = conn.read_json_data_file(path_to_file=path, file_name=fn)
        assert res == "File name 'devices.pdf' is not a JSON file!"

        fn = "devices_not_list.json"
        res = conn.read_json_data_file(path_to_file=path, file_name=fn)
        assert res == """Input data file 'devices_not_list.json' must be of type JSON Array!
                       Export using the '--jsonArray' switch!"""

        fn = "devices.json"
        conn.read_json_data_file(path_to_file=path, file_name=fn)
        assert conn.json_data

    def test_method_load_data(self, test_db):
        cn = "test_devices"
        path = get_test_data_path()
        fn = "devices.json"

        conn = test_db
        conn.load_data(collection_name=cn, path_to_file=path, file_name=fn)

    def test_load_all_methods_raises_exception_when_give_non_existing_folder(self, test_db):
        path = get_test_data_path()
        folder_name = 'i_am_not_there'
        folder_path = os.path.join(path, folder_name)

        conn = test_db
        with pytest.raises(ValueError) as e_info:
            conn.load_all(folder_path)
        assert str(e_info.value) == f'path not exist: {folder_path}'

    def test_load_all_methods_raises_exception_when_folder_is_empty(self, test_db):
        folder_name = 'for_test'
        path = os.path.join(
            get_test_data_path(is_test=True),
            folder_name
        )

        if not os.path.exists(path):
            os.makedirs(path)

        conn = test_db
        with pytest.raises(ValueError) as e_info:
            conn.load_all(path)
        assert str(e_info.value) == f'Expect a non-empty folder: {path}'

        shutil.rmtree(path)

    def test_load_all_methods_should_load_all_data_in_database(self, test_db):
        path = os.path.join(get_test_data_path(), 'for_testing_load_all')

        # Make sure we start from an empty collection
        conn = test_db
        db = conn.db
        conn.drop_db('test_load_all')
        assert len(db.collection_names()) == 0

        conn.load_all(path)
        new_names = db.collection_names()
        assert len(new_names) == 3
        assert 'cities' in new_names
        assert 'emails' in new_names
        assert 'devices' in new_names

        assert db['emails'].count() == 2
        assert db['devices'].count() == 10
        assert db['cities'].count() == 10

    def test_get_default_dumped_data_path(self, test_db):
        conn = test_db
        expect_path = os.path.join(
            get_test_data_path(is_test=True),
            DEFAULT_DUMP_DATA_FOLDER_NAME
        )
        assert conn.get_default_dumped_data_path() == expect_path
