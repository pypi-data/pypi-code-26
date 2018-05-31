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

from okreport import pmd_parser, findbugs_parser, lint_parser, helper
from okreport.chart import getSingleChartHtmlFragment, addChart, endChartAndGetHtmlFragment
from okreport.findbugs_parser import FindBugs, PERFORMANCE_WARN, BAD_PRACTICE_WARN, MULTITHREADED_WARN, \
    VULNERABILITY_WARN, OTHER_WARN
from okreport.lint_parser import Lint
from okreport.pmd_parser import Pmd


def addYesterdayEmptyToTop(obj, x, y):
    topDate = x[0]
    yesterDayDate = topDate - 24 * 60 * 60
    tmpX = [yesterDayDate] + x
    x[:] = []
    for value in tmpX:
        x.append(value)
    y[yesterDayDate] = obj


class Report:
    dateList = list()
    datePmdMap = {}
    dateFindbugsMap = {}
    dateLintMap = {}

    def __init__(self):
        pass

    def addLastConfig(self, path):
        if not exists(path):
            makedirs(path)

        date = self.dateList[-1]
        config_path = join(path, getConfigName(date))
        if exists(config_path):
            remove(config_path)

        if self.dateList.__len__() > 1:
            # there are tow
            if self.equals(-1, -2):
                need_remove_path = join(path, getConfigName(self.dateList[-2]))
                if exists(need_remove_path):
                    remove(need_remove_path)

        config_file = open(config_path, "w")
        config_file.write("%s\n" % self.datePmdMap[date].toFileFragment())
        config_file.write("%s\n" % self.dateFindbugsMap[date].toFileFragment())
        config_file.write("%s\n" % self.dateLintMap[date].toFileFragment())
        config_file.close()

    def maintainDay(self):
        dateStringMap = {}

        for date in self.dateList:
            dateStringMap[date] = helper.dateString(date)

        remove_list = list()
        for leftDate in self.dateList:
            for rightDate in self.dateList:
                dateString = dateStringMap[leftDate]
                anotherString = dateStringMap[rightDate]
                if dateString == anotherString and leftDate != rightDate \
                        and not remove_list.__contains__(leftDate) and not remove_list.__contains__(rightDate):
                    remove_list.append(leftDate)

        print "remove duplicate on cache: %s" % remove_list

        for removed in remove_list:
            self.dateList.remove(removed)
            self.datePmdMap[removed] = None
            self.dateFindbugsMap[removed] = None
            self.dateLintMap[removed] = None

    def maintainConfigs(self, path):
        dateList = getDateList(path)
        for date in dateList:
            if date not in self.dateList:
                remove(join(path, getConfigName(date)))

        # 15 Day
        needRemoveCount = dateList.__len__() - 15
        while needRemoveCount > 0:
            remove(join(path, getConfigName(dateList[needRemoveCount - 1])))
            needRemoveCount -= 1

    def fromConfig(self, path):
        self.dateList = getDateList(path)

        if not exists(path) or self.dateList.__len__() <= 0:
            return

        for date in self.dateList:
            config_path = join(path, getConfigName(date))
            pmd = Pmd()
            pmd.fromFile(config_path)
            self.datePmdMap[date] = pmd

            findbugs = FindBugs()
            findbugs.fromFile(config_path)
            self.dateFindbugsMap[date] = findbugs

            lint = Lint()
            lint.fromFile(config_path)
            self.dateLintMap[date] = lint

    def addParse(self, reportPath):
        findbugs = FindBugs()
        pmd = Pmd()
        lint = Lint()
        for path, dir_list, file_list in walk(reportPath):
            for file_name in file_list:
                if file_name == "findbugs.html":
                    findbugs.parse(join(path, file_name))
                elif file_name == "pmd.html":
                    pmd.parse(join(path, file_name))
                elif file_name == "lint.html":
                    lint.parse(join(path, file_name))

        # 1527497994
        date = calendar.timegm(time.gmtime())

        self.dateList.append(date)
        self.datePmdMap[date] = pmd
        self.dateFindbugsMap[date] = findbugs
        self.dateLintMap[date] = lint

        self.maintainDay()

    def getPmdChartHtmlFragment(self):
        x = list(self.dateList)
        y = {}
        y.update(self.datePmdMap)
        if x.__len__() == 1:
            addYesterdayEmptyToTop(Pmd(), x, y)

        yDate = list()
        for date in x:
            yDate.append(y[date].problemCount)

        return getSingleChartHtmlFragment(x, yDate, title="OkPmd")

    def getFindbugsChartHtmlFragment(self):
        x = list(self.dateList)
        y = {}
        y.update(self.dateFindbugsMap)
        if x.__len__() == 1:
            addYesterdayEmptyToTop(FindBugs(), x, y)

        performances = []
        badPractices = []
        multiThreadeds = []
        vulneerabilitys = []
        others = []
        for date in x:
            findbugs = y[date]
            performances.append(findbugs.performanceWarnCount)
            badPractices.append(findbugs.badPracticeWarnCount)
            multiThreadeds.append(findbugs.multiThreadedWarnCount)
            vulneerabilitys.append(findbugs.vulnerabilityWarnCount)
            others.append(findbugs.otherWarnCount)

        # startChartHtml("OkFindbugs")
        addChart(x, performances, PERFORMANCE_WARN)
        addChart(x, badPractices, BAD_PRACTICE_WARN)
        addChart(x, multiThreadeds, MULTITHREADED_WARN)
        addChart(x, vulneerabilitys, VULNERABILITY_WARN)
        combineChartY = performances + badPractices + multiThreadeds + vulneerabilitys
        fragment = endChartAndGetHtmlFragment(max(min(combineChartY) - 20, 0), combineChartY)
        fragment += getSingleChartHtmlFragment(x, others, title=OTHER_WARN)

        return fragment

    def getLintChartHtmlFragment(self):
        x = list(self.dateList)
        y = {}
        y.update(self.dateLintMap)
        if x.__len__() == 1:
            addYesterdayEmptyToTop(Lint(), x, y)

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

        addChart(x, correctness, title="Correctness")
        addChart(x, security, title="Security")
        addChart(x, performances, title="Performance")
        combineChartY = correctness + security + performances
        charsFragment = endChartAndGetHtmlFragment(max(min(combineChartY) - 20, 0), combineChartY)
        charsFragment += getSingleChartHtmlFragment(x, others, title="Others")

        return charsFragment

    def equals(self, leftIndex, rightIndex):
        leftKey = self.dateList[leftIndex]
        rightKey = self.dateList[rightIndex]
        pmd_equal = pmd_parser.equals(self.datePmdMap[leftKey], self.datePmdMap[rightKey])
        findbugs_equal = findbugs_parser.equals(self.dateFindbugsMap[leftKey], self.dateFindbugsMap[rightKey])
        lint_equal = lint_parser.equals(self.dateLintMap[rightKey], self.dateLintMap[rightKey])
        return pmd_equal and findbugs_equal and lint_equal

    def dump(self):
        for date in self.dateList:
            print "---------------------------------------\n%s %s:" % (helper.dateString(int(date)), date)
            print "\n[OkPmd]: "
            self.datePmdMap[date].dump()
            print "\n[OkFindbugs]: "
            self.dateFindbugsMap[date].dump()
            print "\n[OkLint]: "
            self.dateLintMap[date].dump()


def getConfigName(date):
    return "%d.report" % date


def getDateList(path):
    if not exists(path):
        return list()

    file_list = listdir(path)

    orderDateList = list()

    for file_name in file_list:
        if not file_name.endswith(".report"):
            continue
        orderDateList.append(int(file_name.split(".")[0]))

    orderDateList.sort()
    return orderDateList
