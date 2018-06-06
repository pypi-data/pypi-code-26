#!/usr/bin/env python
# --*--coding: utf-8 --*--

import time
from scapy.all import TCP, IP, sniff, Raw
from logger import logger

class HttpRequestSniffer(object):
    def __init__(self, port=80, iface='en0', filter='tcp', keywords = []):
        self.port = port
        self.iface = iface
        self.filter = filter

        self.http_load = ''
        self.http_fragged = False
        self.http_pack = None
        self.keywords = keywords

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
            logger(time.strftime('%a, %d %b %Y %H:%M:%S %z: '), http_req_url, True)

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

        url = ''.join([host, uri])
        if len(self.keywords) == 0:
            return url

        for keyword in self.keywords:
            if keyword in url:
                return url

        return

    def start(self):
        sniff(
            prn=self.parser,
            filter=self.filter,
            iface=self.iface
        )




