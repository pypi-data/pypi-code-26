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
from os.path import exists


def send_mail(html, attachPathList, config):
    mailFrom = config.mailFrom()
    mailTo = config.mailTo()
    mailCc = config.mailCc()
    mailSubject = config.mailSubject()

    attachList = []

    print "\n---------------------------------------"
    for attachPath in attachPathList:
        attachList.append(("inline", open(attachPath)))
        if not exists(attachPath):
            print "%s not exists" % attachPath
            exit(-1)
        print "add inline attach %s" % attachPath

    print "====================\nsent from: %s\nto: %s\ncc: %s\nsubject: %s" % (mailFrom, mailTo, mailCc, mailSubject)
    return requests.post(
        "https://api.mailgun.net/v3/" + config.mailDomainName() + "/messages",
        auth=("api", config.mailApiKey()),
        files=attachList,
        data={"from": mailFrom,
              "to": mailTo,
              "cc": mailCc,
              "subject": mailSubject,
              "html": html})
