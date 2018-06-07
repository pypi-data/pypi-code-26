#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/4 15:54
# @Author  : jialun.wjl
# @File    : site_suite.py
# @Software: PyCharm
from link_analyze.site_module.module_chain import ModuleChain

class SiteSuite(object):

    def __init__(self, webdriver, monitor, video_urls=None):
        site1 = Action5ifxwSite(webdriver, monitor, None, video_urls)
        site2 = SourceSurgeSite(webdriver, monitor, site1, video_urls)
        site3 = Jxwuou0Site(webdriver, monitor, site2, video_urls)
        site4 = FuliWuSite(webdriver, monitor, site3, video_urls)
        self.__chain = site4

    def run(self):
        self.__chain.handle()

class Action5ifxwSite(ModuleChain):

    def __init__(self, webdriver, monitor, successor=None, video_urls=None):
        ModuleChain.__init__(self, "http://www.5ifxw.com/vip/", "doplayers", "url", "/html/body/div[1]/div[" \
                                                                                    "2]/select", webdriver,
                             monitor, 15, successor, video_urls)

    def handle(self):
        ModuleChain.handle()

class SourceSurgeSite(ModuleChain):

    def __init__(self, webdriver, monitor, successor=None, video_urls=None):
        ModuleChain.__init__(self, "http://source.surge.sh/video.html", "bf", "url", '//*[@id="jk"]',
                             webdriver,
                             monitor, 15, successor, video_urls)

    def handle(self):
        ModuleChain.handle()

    def test(self):
        print("test2")

class Jxwuou0Site(ModuleChain):

    def __init__(self, webdriver, monitor, successor=None, video_urls=None):
        ModuleChain.__init__(self, "http://jxw.uou0.com/", "bf", "url", '//*[@id="jk"]', webdriver,
                             monitor, 15, successor, video_urls)

    def handle(self):
        ModuleChain.handle()

class FuliWuSite(ModuleChain):

    def __init__(self, webdriver, monitor, successor=None, video_urls=None):
        ModuleChain.__init__(self, "http://www.fuliw.top/vip/", "doplayers", "url",
                             '/html/body/div[2]/div[2]/select', webdriver,
                             monitor, 15, successor, video_urls)

    def handle(self):
        ModuleChain.handle(self)
