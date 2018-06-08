from ipaddress import ip_address, ip_network

from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.tcp import TCP, TH_SYN, TH_PUSH, TH_FIN, TH_RST


class TCPManager:
    """
    Reads raw ethernet data, splits them by TCP stream and use a TCPReader per stream.

    The `callback` will be called on each reassembled stream chunk (when the PUSH flag is set).
    >>> def callback(host, port, data):
    >>>     print('Received data from', host, 'on Port', port + ':', str(data))

    The `host` and / or `client` can be set to a list of IP addresses in CIDR notation to filter packets:
    >>> host=['127.0.0.1/8', '1.2.3.4/32']
    >>> client=['127.0.0.1/8', '192.168.0.0/16']

    Example usage of TCPManager with win_pcap:
    >>> from tcp_reader import TCPManager
    >>> from winpcapy import WinPcapUtils
    >>>
    >>> def print_callback(host, port, data):
    >>>     print('Received data from', host, 'on Port', port + ':', str(data))
    >>>
    >>> tcp_manager = TCPManager(callback=print_callback, host=['93.184.216.34/32'], client=['192.168.0.0/16'])
    >>> WinPcapUtils.capture_on('*Ethernet*', tcp_manager.receive_raw_win_pcap)
    """

    def __init__(self, callback=None, host=None, client=None):
        """
        :param callback: Will be called on each reassembled stream chunk (when the PUSH flag is set).
        :param host: Can be set to a list of IP addresses in CIDR notation.
        :param client: Can be set to a list of IP addresses in CIDR notation.
        """
        # default to capture all IPs
        if host is None and client is None:
            host = ['0.0.0.0/0']
            client = ['0.0.0.0/0']
        elif client is None:
            client = host

        self.callback = callback
        self.host = host
        self.client = client
        self.tcp_readers = {}

    def receive_raw_win_pcap(self, win_pcap, param, header, pkt_data):
        """
        Can be used for `WinPcapUtils.capture_on` callback.
        :param win_pcap:
        :param param:
        :param header:
        :param pkt_data:
        """
        self.receive_raw_eth(pkt_data)

    def receive_raw_eth(self, raw):
        """
        Verify it contains an TCP packet and then call `receive`.
        :param raw: Raw data of the ethernet frame (payload).
        """
        eth = Ethernet(raw)

        if not isinstance(eth.data, IP):
            return
        ip = eth.data

        if not isinstance(ip.data, TCP):
            return
        tcp = ip.data

        self.receive(ip, tcp)

    def receive(self, ip, tcp):
        """
        Demeter correct `TCPReader` for packet and call `receive` with TCP packet.
        Packets not in `ip_filter` will be ignored.

        :param ip: Parsed `dpkt.IP` packet.
        :param tcp: Parsed `dpkt.TCP` packet.
        """
        src = ip_address(ip.src)
        sport = tcp.sport

        dst = ip_address(ip.dst)
        dport = tcp.dport

        capture = False
        for host_network in self.host:
            # check if src or dst is in host_network
            if src in ip_network(host_network):
                client = dst
            elif dst in ip_network(host_network):
                client = src
            else:
                continue

            # check if opposite side is in a client network
            for client_network in self.client:
                if client in ip_network(client_network):
                    capture = True
                    break

        if not capture:
            return

        session = (src, sport, dst, dport)

        if session not in self.tcp_readers.keys():
            self.tcp_readers[session] = TCPReader(dst, dport, callback=self.callback)

        reader = self.tcp_readers[session]
        reader.receive(tcp)


class TCPReader:
    """
    Receives `dpkt.TCP` packets, reorder them in sequence and then call callback.
    `TCPReader` can be used through `TCPManager`.
    """
    def __init__(self, host=None, port=None, callback=None):
        """
        :param host: TCP Host, will be passed to callback.
        :param port: TCP Port, will be passed to callback.
        :param callback: Will be called on reassembled data chunk (when the PUSH flag is set).
        """
        self.host = host
        self.port = port
        self.callback = callback
        self.packets = []
        self._seq = 0
        self._packet_buffer = []
        self._packet_buffer_active = False
        self._buffer = b''

    def receive(self, tcp):
        """
        :param tcp: `dpkt.TCP` packet.
        """
        if self._seq == 0:
            self._seq = tcp.seq

        # syn -> set sequence
        if tcp.flags & TH_SYN:
            self._seq = tcp.seq
            self._clear_buffer()
            self._clear_packet_buffer()
            return
        # out-of-order packet -> buffer
        if tcp.seq > self._seq:
            self._packet_buffer.append(tcp)
            self._process_packet_buffer()
            return
        # duplicate packet -> drop
        elif tcp.seq < self._seq:
            return

        self._buffer += tcp.data
        self._seq = tcp.seq + len(tcp.data)

        if tcp.flags & TH_PUSH:
            if callable(self.callback):
                self.callback(self._buffer)

            self.packets.append(self._buffer)
            self._clear_buffer()
        elif tcp.flags & TH_FIN | tcp.flags & TH_RST:
            # TODO end session
            return

        self._process_packet_buffer()

    def _process_packet_buffer(self):
        if self._packet_buffer_active:
            return
        else:
            self._packet_buffer_active = True

        packet_buffer = []

        # restart from lowest packet
        if len(self._packet_buffer) > 10:
            self._clear_buffer()
            self._seq = min([tcp.seq for tcp in self._packet_buffer])

        for tcp in self._packet_buffer:
            # duplicate packet -> drop
            if tcp.seq < self._seq:
                continue
            # correct packet -> receive
            elif tcp.seq == self._seq:
                self.receive(tcp)
                continue

            packet_buffer.append(tcp)

        self._packet_buffer = packet_buffer
        self._packet_buffer_active = False

    def _clear_buffer(self):
        self._buffer = b''

    def _clear_packet_buffer(self):
        self._packet_buffer = []
        self._packet_buffer_active = False
