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

COUNT_REGEX = re.compile(r'<td align="center">(\d+)</td>')


def pmdCount(value=""):
    match_value = COUNT_REGEX.match(value)
    if match_value:
        return match_value.groups()[0]


class Pmd:
    problemCount = 0

    def __init__(self):
        pass

    def parse(self, path):
        for line in reversed(open(path, 'r').readlines()):
            total = pmdCount(line)
            if total:
                self.problemCount += int(total)
                break

    def dump(self):
        print "pmd count: %d" % self.problemCount

    def dumpHtmlBodyFragment(self):
        fragment = """<h2>OkPmd</h2>"""
        fragment += "<li>"
        fragment += "Count: %d" % self.problemCount
        fragment += "</li>\n"
        return fragment

    def toFileFragment(self):
        fragment = "OkPmd\n"
        fragment += "0:%d\n" % self.problemCount
        fragment += "end\n"
        return fragment

    def fromFile(self, conf_path):
        started = False
        for line in open(conf_path):
            line = line.strip()
            if line == "OkPmd":
                started = True
            if started:
                if "end" == line:
                    break
                values = line.split(":")
                if values[0] == "0":
                    self.problemCount = int(values[1])


def equals(left=Pmd(), right=Pmd()):
    return left.problemCount == right.problemCount
