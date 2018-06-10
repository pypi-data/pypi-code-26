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

TOTAL_PERCENT_REGEX = re.compile(
    r'.*<td>Total</td><td class="bar">[\d|,]+ of [\d|,]+</td><td class="ctr2">(\d+)%</td>.*')
PATH_MODULE_NAME_REGEX = re.compile(r'.*/reports/(\S*)/coverage.*')


def parse_path(path=""):
    match_value = PATH_MODULE_NAME_REGEX.match(path)
    if match_value:
        return match_value.groups()[0]
    else:
        return None


def find_percent(line=""):
    match_value = TOTAL_PERCENT_REGEX.match(line)
    if match_value:
        return match_value.groups()[0]

    return None


class Coverage:
    percentMap = {}

    def __init__(self):
        self.percentMap = {}

    def parse(self, path=""):
        name = parse_path(path)
        if not name:
            print "can't parse %s, so ignored" % path
            return

        percent = None
        for line in open(path):
            line = line.strip()
            if line.__len__() > 0:
                percent = find_percent(line)
                if percent:
                    break
        if percent is None:
            print "parse %s failed with its percent is None: %s" % (name, path)
            exit(-1)

        self.percentMap[name] = int(percent)

    def is_empty(self):
        return self.percentMap.__len__() == 0

    def to_cache(self):
        fragment = "OkCoverage\n"
        for name in self.percentMap:
            fragment += "%s:%d\n" % (name, self.percentMap[name])
        fragment += "end\n"
        return fragment

    def from_cache(self, conf_path):
        started = False
        for line in open(conf_path):
            line = line.strip()
            if line == "OkCoverage":
                started = True
            elif started:
                if "end" == line:
                    break
                values = line.split(":")
                if values.__len__() != 2:
                    print "parse config file failed for OkCoverage for %s" % line
                    exit(-1)
                self.percentMap[values[0]] = int(values[1])

    def dump(self):
        for name in self.percentMap:
            print "%s: %d%%" % (name, self.percentMap[name])


def equals(left=Coverage(), right=Coverage()):
    if left == right:
        return True

    if left.percentMap.__len__() != right.percentMap.__len__():
        return False

    for left_name in left.percentMap:
        if left_name not in right.percentMap:
            return False
        if left.percentMap[left_name] != right.percentMap[left_name]:
            return False
