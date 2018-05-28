#! /usr/bin/env python
# coding: utf-8

import argparse
from admin.admin import request_auth, write_error


def reset_password(account, password):
    url = "/auth/password/reset/admin/"
    method = "PUT"
    data = {"account": account, "new_password": password}
    request_auth(method, url, data)


def block_user(account):
    url = "/auth/account/block/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def unlock_user(account):
    url = "/auth/account/unlock/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def main():
    usage = "Help you modify jingd user"
    description = "Please use follow arguments modify jingd user"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-a", "--action", dest="action", help="action", choices=["reset", "block", "unlock"])
    parser.add_argument("-u", "--user", dest="user", help="jingdu user")
    parser.add_argument("-p", "--password", dest="password", help="jingdu password", default="123456")
    args = parser.parse_args()
    if args.action == "reset":
        reset_password(args.user, args.password)
    elif args.action == "block":
        block_user(args.user)
    elif args.action == "unlock":
        unlock_user(args.user)
    else:
        write_error("Invalid action")

if __name__ == "__main__":
    main()
