#!/usr/bin/env python
# -*- coding: utf-8 -*-


from util import Util
import openpyxl
import os
from logger import logger

class Reporter(object):

    def __init__(self):
        logger("Initializing reporter....")
        self.excel = openpyxl.Workbook()

    def write_to_excel(self, data_array=[]):
        logger("write_to_excel")
        sheet = self.excel.active
        sheet.title = 'link_analyze_report'
        for i in range(0, len(data_array)):
            for j in range(0, len(data_array[i])):
                sheet.cell(row=i + 1, column=j + 1, value=str(data_array[i][j]))
        now = Util.time_now()
        file_name = "链接分析报告" + "_" + now + ".xlsx"
        report_dir = "report/"
        if not os.path.exists(report_dir):
            os.mkdir(report_dir)
        self.excel.save(report_dir + file_name)
        self.excel.close()