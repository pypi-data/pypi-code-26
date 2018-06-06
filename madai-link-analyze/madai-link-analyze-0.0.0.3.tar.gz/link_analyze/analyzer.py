#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/16 17:30
# @Author  : jialun.wjl
# @File    : analyzer.py
# @Software: PyCharm
from selenium import webdriver
from monitor import Monitor
from reporter import Reporter
from threading import Event
from Queue import Queue
import json
import time
from logger import logger
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class Analyzer(object):

    def __init__(self):
        self.queue = Queue()
        self.event = Event()
        self.monitor = Monitor(self.queue, self.event)
        self.reporter = Reporter(self.queue, self.event)

    def analyze(self, file_path):
        auto_mode_str = json.loads(open(file_path, "r").read())

        logger("auto_mode_str" + str(auto_mode_str))
        self.profile = webdriver.FirefoxProfile(auto_mode_str["firefoxConfig"])


        self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'true')
        self.profile.set_preference("plugin.state.flash", 2)
        self.driver = webdriver.Firefox(self.profile,executable_path='./browser/mac/geckodriver')
        self.driver.implicitly_wait(30)

        self.monitor.start()
        self.reporter.start()

        for url in auto_mode_str["urls"]:
            logger("Analyzing url : ", url)
            try:
                self.driver.get(url)
                self.monitor.set_monitor_url(url)
                time.sleep(20)
            except Exception as e:
                logger(e)
        # additional_sites = site_suite.SiteSuite(self.driver, self.monitor,
        #                                         ["http://v.youku.com/v_show/id_XMzQ1MjM5ODY0NA==.html"])
        #
        # additional_sites.run()
        self.monitor.stop()
        self.reporter.stop()
        self.driver.quit()
