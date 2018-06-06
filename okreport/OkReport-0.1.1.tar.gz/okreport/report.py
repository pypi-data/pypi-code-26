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

import calendar
import time
from os import walk, listdir, makedirs, remove
from os.path import join, exists

from okreport import pmd_parser, findbugs_parser, lint_parser, helper, coverage_parser, apk_parser, qark_parser
from okreport.apk_parser import ApkInfo
from okreport.chart import get_chart_html, Chart, TYPE_DISK_SIZE, TYPE_PERCENT
from okreport.coverage_parser import Coverage
from okreport.findbugs_parser import FindBugs, PERFORMANCE_WARN, BAD_PRACTICE_WARN, MULTITHREADED_WARN, \
    VULNERABILITY_WARN
from okreport.lint_parser import Lint
from okreport.pmd_parser import Pmd
from okreport.qark_parser import Qark

CHART_FILE_FORMAT = "png"


def add_yesterday_empty_to_top(obj, x, y):
    top_date = x[0]
    yesterday_date = top_date - 24 * 60 * 60
    tmp_x = [yesterday_date] + x
    x[:] = []
    for value in tmp_x:
        x.append(value)
    y[yesterday_date] = obj


class Report:
    dateList = list()
    datePmdMap = {}
    dateFindbugsMap = {}
    dateLintMap = {}
    dateCoverageMap = {}
    dateApkinfoMap = {}
    dateQarkMap = {}

    def __init__(self):
        pass

    def save_last_report_to_cache(self, path):
        if not exists(path):
            makedirs(path)

        date = self.dateList[-1]
        config_path = join(path, get_config_name(date))
        if exists(config_path):
            remove(config_path)

        if self.dateList.__len__() > 1:
            # there are tow
            if helper.date_string(self.dateList[-1]) == helper.date_string(self.dateList[-2]):
                need_remove_path = join(path, get_config_name(self.dateList[-2]))
                print "remove duplicate file for the same day: %s" % need_remove_path
                if exists(need_remove_path):
                    remove(need_remove_path)

        config_file = open(config_path, "w")
        config_file.write("%s\n" % self.datePmdMap[date].to_cache())
        config_file.write("%s\n" % self.dateFindbugsMap[date].to_cache())
        config_file.write("%s\n" % self.dateLintMap[date].to_cache())
        config_file.write("%s\n" % self.dateCoverageMap[date].to_cache())
        config_file.write("%s\n" % self.dateApkinfoMap[date].to_cache())
        config_file.write("%s\n" % self.dateQarkMap[date].to_cache())
        config_file.close()

    def maintain_day(self):
        date_string_map = {}

        for date in self.dateList:
            date_string_map[date] = helper.date_string(date)

        remove_list = list()
        for leftDate in self.dateList:
            for rightDate in self.dateList:
                date_string = date_string_map[leftDate]
                another_string = date_string_map[rightDate]
                if date_string == another_string and leftDate != rightDate \
                        and not remove_list.__contains__(leftDate) and not remove_list.__contains__(rightDate):
                    remove_list.append(leftDate)

        print "remove duplicate on cache: %s" % remove_list

        for removed in remove_list:
            self.dateList.remove(removed)
            self.datePmdMap[removed] = None
            self.dateFindbugsMap[removed] = None
            self.dateLintMap[removed] = None
            self.dateCoverageMap[removed] = None
            self.dateApkinfoMap[removed] = None
            self.dateQarkMap[removed] = None

    def maintain_cache(self, path):
        date_list = get_dates_from_dir(path)
        for date in date_list:
            if date not in self.dateList:
                remove(join(path, get_config_name(date)))

        # 15 Day
        need_remove_count = date_list.__len__() - 15
        while need_remove_count > 0:
            remove(join(path, get_config_name(date_list[need_remove_count - 1])))
            need_remove_count -= 1

    def from_cache(self, path):
        self.dateList = get_dates_from_dir(path)

        if not exists(path) or self.dateList.__len__() <= 0:
            return

        for date in self.dateList:
            config_path = join(path, get_config_name(date))
            pmd = Pmd()
            pmd.from_cache(config_path)
            self.datePmdMap[date] = pmd

            findbugs = FindBugs()
            findbugs.from_cache(config_path)
            self.dateFindbugsMap[date] = findbugs

            lint = Lint()
            lint.from_cache(config_path)
            self.dateLintMap[date] = lint

            coverage = Coverage()
            coverage.from_cache(config_path)
            self.dateCoverageMap[date] = coverage

            apkinfo = ApkInfo()
            apkinfo.from_cache(config_path)
            self.dateApkinfoMap[date] = apkinfo

            qark = Qark()
            qark.from_cache(config_path)
            self.dateQarkMap[date] = qark

            print "load config and add date for data[%d]" % date

    def parse_and_add_report(self, report_path, apk_base_path=None, apk_path=None, qark_report_path=None):
        findbugs = FindBugs()
        pmd = Pmd()
        lint = Lint()
        coverage = Coverage()
        apkinfo = ApkInfo()
        qark = Qark()
        for path, dir_list, file_list in walk(report_path):
            for file_name in file_list:
                if file_name == "findbugs.html":
                    findbugs.parse(join(path, file_name))
                elif file_name == "pmd.html":
                    pmd.parse(join(path, file_name))
                elif file_name == "lint.html":
                    lint.parse(join(path, file_name))
                elif file_name == "index.html" and path.__contains__("/coverage/"):
                    coverage.parse(join(path, file_name))

        # 1527497994
        date = calendar.timegm(time.gmtime())
        self.dateList.append(date)
        self.datePmdMap[date] = pmd
        self.dateFindbugsMap[date] = findbugs
        self.dateLintMap[date] = lint
        self.dateCoverageMap[date] = coverage

        if apk_base_path and apk_path:
            apkinfo.parse(apk_base_path, apk_path)
        self.dateApkinfoMap[date] = apkinfo

        if qark_report_path:
            qark.parse(qark_report_path)
        self.dateQarkMap[date] = qark

        self.maintain_day()

    def get_pmd_chart_html(self, chart_path_list=list(), chart_dir=""):
        x = list(self.dateList)
        y = {}
        y.update(self.datePmdMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(Pmd(), x, y)

        y_date = list()
        for date in x:
            y_date.append(y[date].problemCount)

        chart_path = "%s/okpmd.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_path)
        return get_chart_html(x, y_date, title="OkPmd", chart_path=chart_path)

    def get_findbugs_chart_html(self, chart_path_list=list(), chart_dir=""):
        x = list(self.dateList)
        y = {}
        y.update(self.dateFindbugsMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(FindBugs(), x, y)

        performances = []
        bad_practices = []
        multi_threads = []
        vulnerabilities = []
        others = []
        for date in x:
            findbugs = y[date]
            performances.append(findbugs.performanceWarnCount)
            bad_practices.append(findbugs.badPracticeWarnCount)
            multi_threads.append(findbugs.multiThreadedWarnCount)
            vulnerabilities.append(findbugs.vulnerabilityWarnCount)
            others.append(findbugs.otherWarnCount)

        chart = Chart()
        chart.add_chart(x, performances, PERFORMANCE_WARN)
        chart.add_chart(x, bad_practices, BAD_PRACTICE_WARN)
        chart.add_chart(x, multi_threads, MULTITHREADED_WARN)
        chart.add_chart(x, vulnerabilities, VULNERABILITY_WARN)
        combine_chart_y = performances + bad_practices + multi_threads + vulnerabilities

        chart_main_path = "%s/okfindbugs-main.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_main_path)
        fragment = chart.done_with_html(chart_main_path, max(min(combine_chart_y) - 20, 0), combine_chart_y)

        chart_other_path = "%s/okfindbugs-other.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_other_path)
        fragment += get_chart_html(x, others, title="OkFindbugs Others", chart_path=chart_other_path)

        return fragment

    def get_lint_chart_html(self, chart_path_list=list(), chart_dir=""):
        x = list(self.dateList)
        y = {}
        y.update(self.dateLintMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(Lint(), x, y)

        correctness = []
        security = []
        performances = []
        others = []
        for date in x:
            lint = y[date]
            correctness.append(lint.correctnessCount)
            security.append(lint.securityCount)
            performances.append(lint.performanceCount)
            others.append(lint.otherCount)

        chart = Chart()
        chart.add_chart(x, correctness, title="Correctness")
        chart.add_chart(x, security, title="Security")
        chart.add_chart(x, performances, title="Performance")
        combine_chart_y = correctness + security + performances

        chart_main_path = "%s/oklint-main.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_main_path)
        chars_fragment = chart.done_with_html(chart_main_path, max(min(combine_chart_y) - 20, 0), combine_chart_y)

        chart_other_path = "%s/oklint-other.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_other_path)
        chars_fragment += get_chart_html(x, others, title="OkLint Others", chart_path=chart_other_path)

        return chars_fragment

    def get_coverage_html(self, chart_path_list=list(), chart_dir=""):
        x = list(self.dateList)
        y = {}
        y.update(self.dateCoverageMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(Coverage(), x, y)

        is_empty = True
        for date in x:
            coverage = y[date]
            is_empty = is_empty and coverage.is_empty()
            if not is_empty:
                break

        if is_empty:
            print "coverage is empty, so ignored!"
            return None

        y_map = {}
        name_list = list()
        for date in x:
            coverage = y[date]
            for name in coverage.percentMap:
                if name not in name_list:
                    name_list.append(name)

        for date in x:
            coverage = y[date]
            for name in name_list:
                if name not in y_map:
                    y_map[name] = list()

                if name in coverage.percentMap:
                    y_map[name].append(coverage.percentMap[name])
                else:
                    y_map[name].append(0)

        max_y_per_chart = 10
        split_y_map_list = list()
        split_y_map_list.append({})
        sub_map_count_cursor = 0
        for name in y_map:
            split_y_map_list[-1][name] = y_map[name]
            sub_map_count_cursor += 1
            if sub_map_count_cursor > max_y_per_chart:
                sub_map_count_cursor = 0
                split_y_map_list.append({})

        html = ""
        sub_map_index = 0
        for y_map in split_y_map_list:
            if y_map.__len__() <= 0:
                continue

            chart = Chart()
            combine_chart_y = []
            for name in y_map:
                combine_chart_y += y_map[name]
                chart.add_chart(x, y_map[name], name)

            chart_path = "%s/okcoverage%d.%s" % (chart_dir, sub_map_index, CHART_FILE_FORMAT)
            sub_map_index += 1
            chart_path_list.append(chart_path)
            html += chart.done_with_html(chart_path, 0, combine_chart_y, chart_type=TYPE_PERCENT)

        return html

    def get_qark_html(self, chart_path_list=list(), chart_dir=""):
        is_empty = True
        for date in self.dateList:
            qark = self.dateQarkMap[date]
            is_empty = is_empty and qark.is_empty()
            if not is_empty:
                break

        if is_empty:
            print "qark is empty, so ignored!"
            return None

        x = list(self.dateList)
        y = {}
        y.update(self.dateQarkMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(Qark(), x, y)

        y_map = {}
        name_list = list()
        for date in x:
            qark = y[date]
            for name in qark.risk_map:
                if name not in name_list:
                    name_list.append(name)

        for date in x:
            qark = y[date]
            for name in name_list:
                if name not in y_map:
                    y_map[name] = list()

                if name in qark.risk_map:
                    y_map[name].append(qark.risk_map[name])
                else:
                    y_map[name].append(0)

        chart = Chart()
        combine_chart_y = []
        for name in y_map:
            combine_chart_y += y_map[name]
            chart.add_chart(x, y_map[name], name)

        chart_path = "%s/okqark.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_path)
        return chart.done_with_html(chart_path, max(min(combine_chart_y) - 20, 0), combine_chart_y)

    def get_apkinfo_html(self, chart_path_list=list(), chart_dir=""):
        x = list(self.dateList)
        y = {}
        y.update(self.dateApkinfoMap)
        if x.__len__() == 1:
            add_yesterday_empty_to_top(ApkInfo(), x, y)

        is_empty = True
        for date in x:
            apkinfo = y[date]
            is_empty = is_empty and apkinfo.is_empty()
            if not is_empty:
                break

        if is_empty:
            print "apkinfo is empty, so ignored!"
            return None

        # non apk-size
        y_map = {}
        name_list = list()
        for date in x:
            apkinfo = y[date]
            non_apk_map = apkinfo.get_non_apk_map()
            for name in non_apk_map:
                if name not in name_list:
                    name_list.append(name)

        for date in x:
            apkinfo = y[date]
            for name in name_list:
                if name not in y_map:
                    y_map[name] = list()

                non_apk_map = apkinfo.get_non_apk_map()
                if name in non_apk_map:
                    y_map[name].append(non_apk_map[name])
                else:
                    y_map[name].append(0)

        chart = Chart()
        combine_chart_y = []
        for name in y_map:
            combine_chart_y += y_map[name]
            chart.add_chart(x, y_map[name], name)

        chart_path = "%s/okapkinfo.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_path)
        html = chart.done_with_html(chart_path, 0, combine_chart_y, chart_type=TYPE_DISK_SIZE)

        # apk-size
        apk_size_y = []
        for date in x:
            apkinfo = y[date]
            apk_size_y.append(apkinfo.get_apk_size())

        chart_path = "%s/okapkinfo-apksize.%s" % (chart_dir, CHART_FILE_FORMAT)
        chart_path_list.append(chart_path)

        return html + get_chart_html(x, apk_size_y, title="Apk Size", chart_path=chart_path, chart_type=TYPE_DISK_SIZE)

    def equals(self, left_index, right_index):
        left_key = self.dateList[left_index]
        right_key = self.dateList[right_index]
        pmd_equal = pmd_parser.equals(self.datePmdMap[left_key], self.datePmdMap[right_key])
        findbugs_equal = findbugs_parser.equals(self.dateFindbugsMap[left_key], self.dateFindbugsMap[right_key])
        lint_equal = lint_parser.equals(self.dateLintMap[left_index], self.dateLintMap[right_key])
        coverage_equal = coverage_parser.equals(self.dateCoverageMap[left_index], self.dateCoverageMap[right_key])
        apkinfo_equal = apk_parser.equals(self.dateApkinfoMap[left_index], self.dateApkinfoMap[right_key])
        qark_equal = qark_parser.equals(self.dateQarkMap[left_index], self.dateQarkMap[right_key])
        return pmd_equal and findbugs_equal and lint_equal and coverage_equal and apkinfo_equal and qark_equal

    def dump(self):
        for date in self.dateList:
            print "---------------------------------------\n%s %s:" % (helper.date_string(int(date)), date)
            print "\n[OkPmd]: "
            self.datePmdMap[date].dump()
            print "\n[OkFindbugs]: "
            self.dateFindbugsMap[date].dump()
            print "\n[OkLint]: "
            self.dateLintMap[date].dump()
            print "\n[OkCoverage]: "
            self.dateCoverageMap[date].dump()
            print "\n[OkApkAnalyzer]:"
            self.dateApkinfoMap[date].dump()
            print "\n[OkQark]:"
            self.dateQarkMap[date].dump()


def get_config_name(date):
    return "%d.report" % date


def get_dates_from_dir(path):
    if not exists(path):
        return list()

    file_list = listdir(path)

    order_date_list = list()

    for file_name in file_list:
        if not file_name.endswith(".report"):
            continue
        order_date_list.append(int(file_name.split(".")[0]))

    order_date_list.sort()
    return order_date_list
