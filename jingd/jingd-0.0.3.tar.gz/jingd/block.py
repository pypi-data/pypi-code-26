#! /usr/bin/env python
# coding: utf-8

import argparse
from admin.admin import request_auth


def block_user(account):
    url = "/auth/account/block/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def block_func():
    usage = "Help you modify jingd user"
    description = "Please use follow arguments modify jingd user"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-u", "--user", dest="user", help="jingdu user")
    args = parser.parse_args()
    block_user(args.user)

if __name__ == "__main__":
    block_func()

