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
import subprocess

from humanfriendly import format_size


def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    return out.split('\n')


def is_last_success():
    result = run_command('echo $?')[0].rstrip()
    return result == '0'


ROOT_PATH_REGEX = re.compile('^/([^/]+)/*$')
APK_ANALYZER_LINE_REGEX = re.compile('^(\d+)[^\d]+(\d+)[^\d]+(\d+)[^/]+(.*)')

ASSET_SIZE = "assetSize"
RES_SIZE = "resSize"
LIB_SIZE = "libSize"
METHOD_COUNT = "methodCount"
DEX_SIZE = "dexSize"
APK_SIZE = "apkSize"
OTHER_SIZE = "otherSize"


def get_pathname_if_root(path=""):
    split_path = path.split("/")
    if split_path.__len__() <= 1:
        print "unknown %s" % path
        exit(-1)
    elif split_path.__len__() <= 2:
        return split_path[1]
    elif split_path.__len__() <= 3:
        if split_path[2] == '':
            return split_path[1]
        else:
            return None
    else:
        return None


class ApkInfo:
    apkinfo_map = {}

    def __init__(self):
        self.apkinfo_map = {}

    def parse(self, old_apk_path, new_apk_path):
        lines = run_command("apkanalyzer apk compare %s %s" % (old_apk_path, new_apk_path))

        dex_size = 0
        res_size = 0
        other_size = 0

        for line in lines:
            line = line.strip()
            if line.__len__() <= 0:
                continue
            match_values = APK_ANALYZER_LINE_REGEX.match(line)
            if not match_values:
                print "can't parse line for %s" % line
                continue

            old_size, new_size, diff_size, path = match_values.groups()
            new_size = int(new_size)
            if path == "/" and APK_SIZE not in self.apkinfo_map:
                # apk size
                self.apkinfo_map[APK_SIZE] = new_size
            elif path == "/assets/":
                self.apkinfo_map[ASSET_SIZE] = new_size
            elif path == "/lib/":
                self.apkinfo_map[LIB_SIZE] = new_size
            elif path == "/res/" or path == "/resources.arsc":
                res_size += new_size
            elif path.endswith(".dex"):
                dex_size += new_size
            else:
                if path == '':
                    print line
                    print match_values.groups()
                root_path_name = get_pathname_if_root(path)
                if root_path_name and new_size > 0:
                    other_category = root_path_name
                    print "add %s to other size with %s" % (other_category, format_size(new_size))
                    other_size += new_size

        self.apkinfo_map[DEX_SIZE] = dex_size
        self.apkinfo_map[RES_SIZE] = res_size
        self.apkinfo_map[OTHER_SIZE] = other_size

    def get_apk_size(self):
        if APK_SIZE not in self.apkinfo_map:
            return 0

        return self.apkinfo_map[APK_SIZE]

    def get_non_apk_map(self):
        non_apk_map = {}
        for name in self.apkinfo_map:
            if name == APK_SIZE:
                continue
            non_apk_map[name] = self.apkinfo_map[name]
        return non_apk_map

    def to_cache(self):
        fragment = "OkApkAnalyzer\n"
        for name in self.apkinfo_map:
            fragment += "%s:%d\n" % (name, self.apkinfo_map[name])
        fragment += "end\n"
        return fragment

    def from_cache(self, conf_path):
        started = False
        for line in open(conf_path):
            line = line.strip()
            if line == "OkApkAnalyzer":
                started = True
            elif started:
                if "end" == line:
                    break
                values = line.split(":")
                if values.__len__() != 2:
                    print "parse config file failed for OkApkAnalyzer for %s" % line
                    exit(-1)
                self.apkinfo_map[values[0]] = int(values[1])

    def dump(self):
        for name in self.apkinfo_map:
            print "%s: %s" % (name, format_size(self.apkinfo_map[name]))

    def is_empty(self):
        return self.apkinfo_map.__len__() <= 0


def equals(left=ApkInfo(), right=ApkInfo()):
    if left == right:
        return True

    if left.apkinfo_map.__len__() != right.apkinfo_map.__len__():
        return False

    for left_name in left.apkinfo_map:
        if left_name not in right.apkinfo_map:
            return False
        if left.apkinfo_map[left_name] != right.apkinfo_map[left_name]:
            return False

# parser = ApkInfo()
#
# parser.parse("/Users/jacks/Downloads/base.apk",
#              "/Users/jacks/Downloads/new.apk")
#
# print "================================"
# parser.dump()
# print "================================"
