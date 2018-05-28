#! /usr/bin/env python
# coding: utf-8

import argparse
from admin.admin import request_auth


def reset_password(account, password):
    url = "/auth/password/reset/admin/"
    method = "PUT"
    data = {"account": account, "new_password": password}
    request_auth(method, url, data)


def reset_func():
    usage = "Help you modify jingd user"
    description = "Please use follow arguments modify jingd user"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-u", "--user", dest="user", help="jingdu user")
    parser.add_argument("-p", "--password", dest="password", help="jingdu password", default="123456")
    args = parser.parse_args()
    reset_password(args.user, args.password)

if __name__ == "__main__":
    reset_func()
