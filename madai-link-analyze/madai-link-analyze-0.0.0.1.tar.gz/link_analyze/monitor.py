#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/16 16:49
# @Author  : jialun.wjl
# @File    : monitor.py
# @Software: PyCharm
from scapy.all import sniff
from threading import Thread, Event
import urllib3
from logger import logger

class Monitor(Thread):

    def __init__(self, queue, event):
        logger("Initializing network monitor....")
        Thread.__init__(self)
        self.queue = queue
        self.event = event
        self._stop_event = Event()
        self.monitor_url = "unknown"
        self.interface_name = "default"
        self.test_video_url = "None"

    def set_monitor_url(self, url):
        self.monitor_url = url

    def set_report_info(self, url, interface_name, test_video_url):
        self.monitor_url = url
        self.interface_name = interface_name
        self.test_video_url = test_video_url

    def stop(self):
        self._stop_event.set()
        http = urllib3.PoolManager()
        http.request("GET", "http://youku.com")


    def filter_request(self, packet):
        tmp_str = "\n".join(packet.sprintf("{Raw:%Raw.load%}").split(r"\r\n"))
        request_lines = tmp_str.split("\n")
        if len(request_lines) > 1:
            request_uri = request_lines[0]
            origin_host = request_lines[1].split(' ')
            if "gm.mmstat.com" not in origin_host and (("ccode=" in request_uri and "psid=" in request_uri)
                                                       or ("ctype=" in request_uri and "sid=" in request_uri)):
                origin_uri = request_uri.split(' ')
                if len(origin_uri) > 1 and len(origin_host) > 1:
                    self.queue.put([self.monitor_url, "http://" + origin_host[1] + origin_uri[1], self.interface_name,
                                    self.test_video_url])
                    self.event.set()

    def run(self):
        logger("Network sniffer start to run...")
        sniff(prn=self.filter_request, lfilter=lambda p: "GET" in str(p), filter="tcp port 80",
              stop_filter=lambda p: self._stop_event.is_set())
        logger("Network sniffer stopped.")
