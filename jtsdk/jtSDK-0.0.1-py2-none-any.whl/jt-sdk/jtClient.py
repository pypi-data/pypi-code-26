#!/usr/bin/env python
# -- coding: utf-8 --
import requests
import os
import sys
import jtConstant
import jtException

reload(sys)
sys.setdefaultencoding('utf8')

class jtClient(object):

    def __init__(self):
        self.url = os.environ['JT_HOST'] + "/" + os.environ["JT_PORT"]

    def jt_status(self):
        response = requests.get(url + jtConstant.ROOT)
        if (response.status_code == 200):
            return True
        return False

    def create_index(self, index, json_data):
        response = requests.post(url + jtConstant.INDEX_FORMAT.format(index),
                                headers = jtConstant.HEADER,
                                data = json_data)
        if (response.status_code == 201):
            return True
        else:
            raise jtException(response.status_code, response.text)

    def update_index(self, index, json_data):
        response = requests.put(url + jtConstant.INDEX_FORMAT.format(index),
                                headers = jtConstant.HEADER,
                                data = json_data)
        if (response.status_code == 200):
            return True
        else:
            raise jtException(response.status_code, response.text)

    def check_if_index_exist(self, index):
        response = requests.head(url + jtConstant.INDEX_FORMAT.format(index),
                                headers = jtConstant.HEADER,
                                data = json_data)
        if (response.status_code == 200):
            return True
        return False

    def get_index(self, index):
        response = requests.get(url + jtConstant.INDEX_FORMAT.format(index),
                                headers = jtConstant.HEADER,
                                data = json_data)
        if (response.status_code == 200):
            json_acceptable_string = response.text.replace("'", "\"")
            return json.loads(json_acceptable_string)
        else:
            raise jtException(response.status_code, response.text)

    def get_all_indices(self):
        response = requests.get(url + jtConstant.INDEX)
        if (response.status_code == 200):
            json_acceptable_string = response.text.replace("'", "\"")
            return json.loads(json_acceptable_string)
        else:
            raise jtException(response.status_code, response.text)

    def get_size(self):
        response = requests.get(url + jtConstant.INDEX)
        if (response.status_code == 200):
            return int(response.text)
        else:
            raise jtException(response.status_code, response.text)

    def manual_back_up(self):
        response = requests.post(url + jtConstant.BACKUP)
        if (response.status_code == 200):
            return True
        else:
            raise jtException(response.status_code, response.text)
