#!/usr/bin/env python
# --*--coding: utf-8 --*--

import time
from scapy.all import TCP, IP, sniff, Raw
from logger import logger
import threading
from timetable import TimerReset

class HttpRequestSniffer(object):

    def __init__(self, keywords=[], nokeywords=[],
                 find_target_url=None, finish_find_url=None, timeout_s=20, port=80, iface='en0',
                 filter='tcp'):
        self.port = port
        self.iface = iface
        self.filter = filter

        self.http_load = ''
        self.http_fragged = False
        self.http_pack = None
        self.keywords = keywords
        self.nokeywords = nokeywords
        self.find_target_url = find_target_url
        self.finish_find_url = finish_find_url
        self.is_find_target_url = False
        self.timeout_s = timeout_s
        self.timer = None

    def finish_find_one_sniffer(self):
        if self.finish_find_url is not None:
            self.finish_find_url()

    def parser(self, pkt):
        if not pkt.haslayer(Raw):
            return
        elif self.port not in [pkt[TCP].sport, pkt[TCP].dport]:
            return

        self.parse_http(pkt[Raw].load, pkt[IP].ack)

    def parse_http(self, load, ack):
        if ack == self.http_pack:
            self.http_load = self.http_load + load
            load = self.http_load
            self.http_fragged = True
        else:
            self.http_load = load
            self.http_pack = ack
            self.http_fragged = False

        try:
            header_lines = load.split('\r\n\r\n')[0].split('\r\n')
        except ValueError:
            header_lines = load.split('\r\n')

        http_req_url = self.get_http_req_url(header_lines)

        if http_req_url:
            logger("http_req_url = " + http_req_url)

    def get_http_req_url(self, header_lines):
        host = ''
        uri = ''
        http_method = header_lines[0][0:header_lines[0].find('/')].strip()

        if http_method != 'GET':
            return

        for line in header_lines:
            # find host
            if 'Host:' in line:
                host = line.split('Host: ')[1].strip()

            # find uri
            if 'GET /' in line:
                uri = line.split('GET ')[1].split(' HTTP/')[0].strip()

        url = "http://" + ''.join([host, uri])

        target_url = url
        for keyword in self.keywords:
            target_url = None
            if keyword in url:
                target_url = url
                break

        for nokeyword in self.nokeywords:
            if nokeyword in url:
                target_url = None
                break

        if target_url and self.find_target_url:
            self.find_target_url(target_url, host, uri)
            self.timer.reset()

        return target_url

    def start(self):
        self.timer = TimerReset(self.timeout_s, self.finish_find_one_sniffer)
        self.timer.start()
        sniff(
            prn=self.parser,
            filter=self.filter,
            iface=self.iface
        )
