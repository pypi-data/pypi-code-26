#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/24 21:15
# @Author  : jialun.wjl
# @File    : reporter.py
# @Software: PyCharm
from threading import Thread, Event
from util import Util
import openpyxl
import os
import re
from logger import logger

class Reporter(Thread):

    def __init__(self, queue, event):
        print("Initializing reporter....")
        Thread.__init__(self)
        self.queue = queue
        self.event = event
        self.excel = openpyxl.Workbook()
        self._stop_event = Event()
        self._start_time = Util.time_now()
        self._data_array = []
        self._report_dir = "report/"
        self._uniq_list = []

    def stop(self):
        self._stop_event.set()
        self.event.set()

    def run(self):
        while not self._stop_event.is_set():
            while not self.queue.empty():
                data = self.queue.get()
                try:
                    self._parse_one_data(data)
                except Exception as e:
                    print(e)
            self.event.clear()
            self.event.wait()
        if len(self._data_array) != 0:
            self._data_array.insert(0, ['分析源', '请求内容', '线路', '测试视频url', 'ccode', 'psid'])
            self._write_to_excel()

    def _parse_one_data(self, data):
        uk = data[0] + "_" + data[2] + "_" + data[3]
        if uk in self._uniq_list:
            return
        else:
            self._uniq_list.append(uk)
        ccode = ''
        psid = ''
        if "psid=" in data[1]:
            psid = re.findall(r"psid=(.+?)&", data[1])[0]
            ccode = re.findall(r"ccode=(.+?)&", data[1])[0]
        else:
            psid = re.findall(r"sid=(.+?)&", data[1])[0]
            ccode = re.findall(r"ctype=(.+?)&", data[1])[0]
        data.append(ccode)
        data.append(psid)
        self._data_array.append(data)

    def _write_to_excel(self):
        sheet = self.excel.active
        sheet.title = 'madai_link_analyze_report'
        for i in range(0, len(self._data_array)):
            for j in range(0, len(self._data_array[i])):
                sheet.cell(row=i + 1, column=j + 1, value=str(self._data_array[i][j]))
        now = Util.time_now()
        file_name = "分析报告_" + self._start_time + "_" + now + ".xlsx"
        if not os.path.exists(self._report_dir):
            os.mkdir(self._report_dir)
        self.excel.save(self._report_dir + file_name)


