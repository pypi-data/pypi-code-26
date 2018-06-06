#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/7 14:38
# @Author  : jialun.wjl
# @File    : module_chain.py
# @Software: PyCharm
from time import sleep
from selenium.webdriver.support.select import Select


class ModuleChain(object):

    def __init__(self, web_url, submit_btn_id, url_input_id, select_xpath, webdriver, monitor, sleep_time=15,
                 successor=None, video_urls=None):
        self.__web_url = web_url
        self.__submit_id = submit_btn_id
        self.__url_input_id = url_input_id
        self.__select_xpath = select_xpath
        self.__monitor = monitor
        self.__webdriver = webdriver
        self.__sleep_time = sleep_time
        self.__successor = successor
        self.__video_urls = video_urls

    def set_successor(self, successor):
        self.__successor = successor

    def get_driver(self):
        return self.__webdriver

    def get_video_urls(self):
        return self.__video_urls

    def get_monitor(self):
        return self.__monitor

    def handle(self):
        # todo
        print("Analyzing web site : ", self.__web_url)
        self.__webdriver.get(self.__web_url)
        url_input = self.__webdriver.find_element_by_id(self.__url_input_id)
        submit_btn = self.__webdriver.find_element_by_id(self.__submit_id)
        channel_select = Select(self.__webdriver.find_element_by_xpath(self.__select_xpath))
        select_num = len(channel_select.options)
        for i in range(select_num):
            channel_select.select_by_index(i)
            for url in self.__video_urls:
                try:
                    self.__monitor.set_report_info(self.__web_url, channel_select.first_selected_option.text, url)
                    url_input.clear()
                    url_input.send_keys(url)
                    submit_btn.click()
                    sleep(self.__sleep_time)
                except Exception as e:
                    print(e)
        if self.__successor is not None:
            self.__successor.handle()
