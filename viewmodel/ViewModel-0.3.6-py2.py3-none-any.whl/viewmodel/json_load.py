from typing import List, Dict

import os
from bson import json_util
from pymongo import MongoClient

DEFAULT_DUMP_DATA_FOLDER_NAME = 'dumped_data'


class JSONLoad:
    def __init__(self, host_name: str = 'localhost', port_number: int = 27017, db_name: str = None):
        self.host_name = host_name
        self.port_number = port_number

        if not db_name:
            raise ValueError('DB name (db_name) required!')
        else:
            self.db_name = db_name

        self.client = MongoClient(self.host_name, self.port_number)
        self.db = self.client[self.db_name]

        self.json_data = None

        # current working directory
        self.cwd = os.getcwd()

    def insert_one(self, collection_name: str = None, data: Dict = None):
        data = data if data else {}
        if collection_name and data:
            collection = self.db[collection_name]
            data_id = collection.insert_one(data).inserted_id
            return data_id
        elif not collection_name and data:
            return "Missing parameter (collection_name)!"
        elif not data and collection_name:
            return "Missing parameter (data)!"
        else:
            return "Missing parameters (collection_name + data)!"

    def insert_many(self, collection_name: str = None, data: List = None):
        data = data if data else []
        if collection_name and data:
            collection = self.db[collection_name]
            collection.drop()
            data_ids = collection.insert_many(data).inserted_ids
            return data_ids
        elif not collection_name and data:
            return "Missing parameter (collection_name)!"
        elif not data and collection_name:
            return "Missing parameter (data)!"
        else:
            return "Missing parameters (collection_name + data)!"

    def drop_db(self, db_name):
        if db_name not in self.client.database_names():
            return f"DB {db_name} does not exist! No action taken!"

        self.client.drop_database(db_name)
        return f"DB {db_name} dropped!"

    def drop_collection(self, collection_name):
        if collection_name not in self.db.collection_names(include_system_collections=False):
            return f"Collection {collection_name} does not exist! No action taken!"

        self.db.drop_collection(collection_name)
        return f"Collection {collection_name} dropped!"

    def read_json_data_file(self, path_to_file, file_name):
        # change the path so we can read the input file
        extension = file_name.split('.')[1]
        if 'json' not in extension:
            return f"File name '{file_name}' is not a JSON file!"

        full_path = os.path.join(path_to_file, file_name)

        with open(full_path, "r") as f:
            data = json_util.loads(f.read())
            if not isinstance(data, List):
                return f"""Input data file '{file_name}' must be of type JSON Array!
                       Export using the '--jsonArray' switch!"""
            else:
                self.json_data = data

        return data

    def load_data(self, collection_name, path_to_file, file_name):
        data = self.read_json_data_file(path_to_file, file_name)
        self.insert_many(collection_name=collection_name, data=data)

    @staticmethod
    def get_default_dumped_data_path():
        path = os.getcwd()
        if not path.endswith('tests'):
            path = os.path.join(path, 'tests')
        return os.path.join(path, DEFAULT_DUMP_DATA_FOLDER_NAME)

    def load_all(self, json_data_path=None):
        if not json_data_path:
            json_data_path = JSONLoad.get_default_dumped_data_path()

        if not os.path.isdir(json_data_path):
            raise ValueError(f'path not exist: {json_data_path}')
        if not os.listdir(json_data_path):
            raise ValueError(f'Expect a non-empty folder: {json_data_path}')

        for file in os.listdir(json_data_path):
            if not file.endswith('.json'):
                continue
            file_path = os.path.join(json_data_path, file)
            if os.path.isfile(file_path):
                collection_name = file.split('.')[0]
                self.load_data(collection_name, json_data_path, file)

    def restore_db_from_json(self):
        self.drop_db(self.db_name)
        self.load_all()
