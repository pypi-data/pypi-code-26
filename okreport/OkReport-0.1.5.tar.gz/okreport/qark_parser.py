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

NAME_REGEX = re.compile(r'.*id="([^_]+)_count">')
VALUE_REGEX = re.compile(r'^(\d+)$')


class Qark:
    risk_map = {}

    def __init__(self):
        self.risk_map = {}

    def parse(self, qark_report_path=""):
        name_cursor = None
        for line in open(qark_report_path + "/report.html", "r"):
            line = line.strip()
            if name_cursor:
                match_values = VALUE_REGEX.match(line)
                if match_values:
                    self.risk_map[name_cursor] = int(match_values.groups()[0])
                    name_cursor = None
            else:
                match_values = NAME_REGEX.match(line)
                if match_values:
                    name_cursor = match_values.groups()[0]

    def to_cache(self):
        fragment = "okQark\n"
        for name in self.risk_map:
            fragment += "%s:%d\n" % (name, self.risk_map[name])
        fragment += "end\n"
        return fragment

    def from_cache(self, cache_path):
        started = False
        for line in open(cache_path, "r"):
            line = line.strip()
            if line == "okQark":
                started = True
            elif started:
                if "end" == line:
                    break
                values = line.split(":")
                if values.__len__() < 2:
                    print "unknown date from cache %s" % line
                    exit(-1)
                self.risk_map[values[0]] = int(values[1])

    def dump(self):
        for name in self.risk_map:
            print "%s: %d" % (name, self.risk_map[name])

    def is_empty(self):
        return self.risk_map.__len__() <= 0


def equals(left=Qark(), right=Qark()):
    if left == right:
        return True

    if left.risk_map.__len__() != right.risk_map.__len__():
        return False

    for left_name in left.risk_map:
        if left_name not in right.risk_map:
            return False
        if left.risk_map[left_name] != right.risk_map[left_name]:
            return False

# qark = Qark()
# qark.parse("/Users/jacks/Downloads/tmp/qark-report/report.html")
# qark.dump()
