# -*- coding: utf-8 -*-
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

import re

from okreport.html import addTd

COLUMN_COUNT_REGEX = re.compile(r'<td class="countColumn">(\d+)</td>.*')
CATEGORY_REGEX = re.compile(r'.*<td class="categoryColumn"><a href=".*">(.*)</a>')


class Lint:
    correctnessCount = 0
    securityCount = 0
    performanceCount = 0
    otherCount = 0

    correctnessScope = False
    securityScope = False
    performanceScope = False
    otherScope = False

    def parse_line(self, line=""):
        match_value = COLUMN_COUNT_REGEX.match(line)
        if match_value:
            value = int(match_value.groups()[0])
            if self.correctnessScope:
                self.correctnessCount += value
            elif self.securityScope:
                self.securityCount += value
            elif self.performanceScope:
                self.performanceCount += value
            else:
                self.otherCount += value
            return

        match_value = CATEGORY_REGEX.match(line)
        if match_value:
            self.reset()
            category = match_value.groups()[0]
            if category == "Correctness":
                self.correctnessScope = True
            elif category == "Security":
                self.securityScope = True
            elif category == "Performance":
                self.performanceScope = True
            else:
                self.otherScope = True

    def parse(self, path=""):
        started = False
        for line in open(path):
            if '<table class="overview">' in line:
                started = True
            if started:
                if "</table>" in line:
                    break
                self.parse_line(line)

    def dumpHtmlBodyFragment(self):
        fragment = u"""<h2>OkLint</h2>
    <table width="500" cellpadding="5" cellspacing="2">
    <tr class="tableheader">
    <th align="left">警告类型</th>
    <th align="right">数量</th>
    </tr>"""
        fragment += """<tr class="tablerow0">"""
        fragment += addTd(u"使用警告")
        fragment += addTd(self.correctnessCount.__str__(), True)
        fragment += "</tr>"

        fragment += """<tr class="tablerow1">"""
        fragment += addTd(u"安全警告")
        fragment += addTd(self.securityCount.__str__(), True)
        fragment += "</tr>"

        fragment += """<tr class="tablerow0">"""
        fragment += addTd(u"性能警告")
        fragment += addTd(self.performanceCount.__str__(), True)
        fragment += "</tr>"

        fragment += """<tr class="tablerow1">"""
        fragment += addTd(u"其他警告")
        fragment += addTd(self.otherCount.__str__(), True)
        fragment += "</tr>"

        fragment += "</table>\n"
        return fragment

    def dump(self):
        print u"""使用警告: %d
安全警告: %d
性能警告: %d
其他警告: %d""" % (self.correctnessCount, self.securityCount, self.performanceCount, self.otherCount)

    def reset(self):
        self.correctnessScope = False
        self.securityScope = False
        self.performanceScope = False
        self.otherScope = False

    def __init__(self):
        pass

    def toFileFragment(self):
        fragment = "OkLint\n"
        fragment += "0:%d\n" % self.correctnessCount
        fragment += "1:%d\n" % self.securityCount
        fragment += "2:%d\n" % self.performanceCount
        fragment += "3:%d\n" % self.otherCount
        fragment += "end\n"
        return fragment

    def fromFile(self, conf_path):
        started = False
        for line in open(conf_path):
            line = line.strip()
            if line == "OkLint":
                started = True
            if started:
                if "end" == line:
                    break
                values = line.split(":")
                if values[0] == "0":
                    self.correctnessCount = int(values[1])
                elif values[0] == "1":
                    self.securityCount = int(values[1])
                elif values[0] == "2":
                    self.performanceCount = int(values[1])
                elif values[0] == "3":
                    self.otherCount = int(values[1])


def equals(left=Lint(), right=Lint()):
    if left == right:
        return True
    if left.correctnessCount != right.correctnessCount:
        return False
    if left.securityCount != right.securityCount:
        return False
    if left.performanceCount != right.performanceCount:
        return False
    if left.otherCount != right.otherCount:
        return False

    return True
