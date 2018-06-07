#!/usr/bin/env python
# -*- coding: utf-8 -*-

from monitor import Monitor
import json
from logger import logger
from browserthread import BrowserThread

class Analyzer(object):

    def __init__(self, keywords=[], nokeywords=[], extractkeys=[]):
        self.monitor = Monitor(keywords, nokeywords, extractkeys)

    def url_under_analyze(self, url):
        self.monitor.set_monitor_url(url)

    def start(self, file_path):
        auto_mode_str = json.loads(open(file_path, "r").read())
        logger("auto_mode_str" + str(auto_mode_str))

        browserThread = BrowserThread(auto_mode_str["firefoxConfig"], auto_mode_str["urls"],
                                      self.url_under_analyze)
        browserThread.start()
        self.monitor.start(browserThread.finish_find_url)

        # wait key stop
        browserThread.stop()

        # additional_sites = site_suite.SiteSuite(self.driver, self.monitor,
        #                                         ["http://v.youku.com/v_show/id_XMzQ1MjM5ODY0NA==.html"])
        #
