# !/usr/bin/python -u

"""
Copyright (C) 2018 LingoChamp Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests


def send_mail(html, config):
    mailFrom = config.mailFrom()
    mailTo = config.mailTo()
    mailCc = config.mailCc()
    mailSubject = config.mailSubject()
    print "==================\nsent from: %s\nto: %s\ncc: %s\nsubject: %s" % (mailFrom, mailTo, mailCc, mailSubject)
    return requests.post(
        "https://api.mailgun.net/v3/" + config.mailDomainName() + "/messages",
        auth=("api", config.mailApiKey()),
        data={"from": mailFrom,
              "to": mailTo,
              "cc": mailCc,
              "subject": mailSubject,
              "html": html})
