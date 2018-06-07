#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logger import logger
from httprequestsniffer import HttpRequestSniffer
from reporter import Reporter
import re

class Monitor(object):

    def __init__(self, keywords=[], nokeywords=[],extractkeys = []):
        logger("Initializing network monitor....")
        self.monitor_url = "unknown"
        self.interface_name = "default"
        self.test_video_url = "None"
        self.keywords = keywords
        self.nokeywords = nokeywords
        self.data_array = []
        self.uniq_list = []
        self.reporter = Reporter()
        self.extractkeys = extractkeys

    def set_monitor_url(self, url):
        self.monitor_url = url

    def set_report_info(self, url, interface_name, test_video_url):
        self.monitor_url = url
        self.interface_name = interface_name
        self.test_video_url = test_video_url

    def find_target_url(self, url, host, uri):
        try:
            logger("find_target_url")
            self.parse_one_data([self.monitor_url, url, host])
            self.finish_find_url()
        except Exception as e:
            logger(e)

    def parse_key_value(self, str, data):
        strarray = re.findall(r"" + str + "=(.+?)&", data)
        if strarray and len(strarray) >= 1:
            return strarray[0]
        else:
            return ''

    def parse_one_data(self, data):
        uk = data[0]
        if uk in self.uniq_list:
            return
        else:
            self.uniq_list.append(uk)

        url = data[1]
        for extractkey in self.extractkeys:
            value = self.parse_key_value(extractkey, url)
            if value:
                data.append(value)
            else:
                data.append('')
        self.data_array.append(data)

    def start(self, finish_find_url = None):
        logger("Network sniffer start to run...")
        self.finish_find_url = finish_find_url

        default_title = ['盗链播放页', '盗链地址', '盗链Host']
        for extractkey in self.extractkeys:
            default_title.append(extractkey)

        self.data_array.insert(0, default_title)
        httpRequestSniffer = HttpRequestSniffer(self.keywords, self.nokeywords,
                                                self.find_target_url,
                                                finish_find_url)
        httpRequestSniffer.start()

        if len(self.data_array) >= 1:
            self.reporter.write_to_excel(self.data_array)

        logger("data_array " + str(self.data_array))
        logger("Network sniffer stopped.")
