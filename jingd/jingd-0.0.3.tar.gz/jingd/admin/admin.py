#! /usr/bin/env python
# coding: utf-8

import sys
import os
import requests

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

def write_error(msg, code=1):
    sys.stderr.write("%s\n" % msg)
    sys.exit(code)

def request_auth(method, url, data):
    auth_endpoint = os.environ.get("JINGD_AUTH_ENDPOINT")
    if auth_endpoint is None:
        write_error("Please Set ENV JINGD_AUTH_ENDPOINT", -1)
    headers = {"Content-Type": "application/json", "User-Agent": user_agent}
    url = "%s%s" % (auth_endpoint, url)
    resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code != 200:
        write_error(resp.status_code)
    r_data = resp.json()
    if r_data["status"] % 10000 < 100:
        print(r_data["message"])
    else:
        write_error(r_data["message"])